#!/usr/bin/python
import argparse
import json
import os
import sys
from abc import ABC
import shutil

from gen import Gen

sys.path.append(os.path.dirname(os.path.dirname(os.path.realpath(__file__))))

from google_drive_client import GoogleDriveClient  # noqa
from tts_object_builder import TTSObjectBuilder  # noqa
from input_parameters import InputParameterBuilder  # noqa
from config_enums import *  # noqa
from generator import Generator  # noqa


class GenAndTTS():

    _TTS_SAVED_OBJECTS_FOLDER = os.path.expanduser('~') + \
        '/Documents/My Games/Tabletop Simulator/Saves/Saved Objects'

    def __init__(
        self,
        tts_config_path: str,
        deck_config_path: str,
        decklist_path: str,
        output_folder: str,
        copy_to_tts: bool,
    ):
        with open(tts_config_path, 'r') as stream:
            self._tts_config = json.load(stream)
        self._deck_config_path = deck_config_path
        self._decklist_path = decklist_path
        self._output_folder = output_folder
        self._copy_to_tts = copy_to_tts

        self._google_client = GoogleDriveClient(
            self._tts_config.get('google_secrets_path'))

    def run(self) -> list[str]:
        gen_params = InputParameterBuilder.build(
            self._deck_config_path, self._decklist_path)
        if gen_params.config['output_image_layout'] != ImageLayout.SHEET:
            raise Exception('Only sheet output is supported')

        # generate the deck, save it locally
        deck = Generator.gen_deck(gen_params)
        deck_image_files = Generator.gen_deck_images(
            self._output_folder, deck=deck)
        if len(deck_image_files) != 1:
            raise Exception('Error: expected a single deck image')

        deck_image_file = deck_image_files[0]
        created_files = [deck_image_file]

        asset_name = os.path.split(deck_image_file)[
            1].split('.')[0] + '_tts'

        front_id = self._upload_front_file(deck_image_file, asset_name + '.png')
        back_id = self._copy_back_file()

        # build the TTS objects, then upload them
        tts_deck = TTSObjectBuilder.build_deck(
            deck.get_size(), deck.get_dimensions()[0], front_id, back_id)

        if not os.path.exists(self._output_folder):
            os.makedirs(self._output_folder)

        tts_file_name = asset_name + '.json'
        tts_file_path = os.path.join(
            self._output_folder,
            tts_file_name,
        )
        with open(tts_file_path, 'w+') as stream:
            json.dump(tts_deck, stream, indent=4)
        created_files.append(tts_file_path)

        self._upload_tts_file(tts_file_path, tts_file_name)

        # optionally copy to the TTS folder for easy access in game
        if self._copy_to_tts:
            if (os.path.exists(GenAndTTS._TTS_SAVED_OBJECTS_FOLDER)):
                tts_copy = shutil.copy(
                    tts_file_path, GenAndTTS._TTS_SAVED_OBJECTS_FOLDER)
                created_files.append(tts_copy)
            else:
                print('Warning: could not copy to TTS - folder does not exist')

        return created_files

    def _upload_front_file(self, file_path: str, name: str) -> str:
        target_folder = self._tts_config.get('google_tts_folder_id')
        return self._google_client.create_or_update_png(file_path, target_folder, name)

    def _copy_back_file(self) -> str:
        assets_folder = self._tts_config.get('google_assets_folder_id')
        target_folder = self._tts_config.get('google_tts_folder_id')
        back_name = self._tts_config.get('back_image')

        back_id = self._google_client.copy_file(
            back_name, assets_folder, target_folder)

        return back_id

    def _upload_tts_file(self, file_path: str, name: str) -> str:
        target_folder = self._tts_config.get('google_tts_folder_id')
        return self._google_client.create_or_update_json(file_path, target_folder, name)


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument('--tts_config', type=str, required=True,
                        help='Path to json-formatted tts config')
    parser.add_argument('--deck_config', type=str, required=True,
                        help='Path to json-formatted deck generator config')
    parser.add_argument('--decklist', type=str, required=True,
                        help='Id/path for cards list csv')
    parser.add_argument('--out_folder', type=str, required=False, default='.')
    parser.add_argument('--copy_to_tts', action='store_true')
    args = parser.parse_args()

    created_files = GenAndTTS(
        args.tts_config,
        args.deck_config,
        args.decklist,
        args.out_folder,
        args.copy_to_tts
    ).run()
    for file in created_files:
        if file:
            print('Saved result in ' + file)
