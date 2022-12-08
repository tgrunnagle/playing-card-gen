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


class GenAndTTS(ABC):

    _TTS_SAVED_OBJECTS_FOLDER = os.path.expanduser('~') + \
        '/Documents/My Games/Tabletop Simulator/Saves/Saved Objects'

    def run(
        tts_config_path: str,
        deck_config_path: str,
        decklist_path: str,
        output_folder: str,
        copy_to_tts: bool,
    ) -> list[str]:



        # generate the deck, save it locally
        params = InputParameterBuilder.build(deck_config_path, decklist_path)
        if params.config['output_image_layout'] != ImageLayout.SHEET:
            raise Exception('Only sheet output is supported')

        deck = Generator.gen_deck(params)

        deck_image_files = Generator.gen_deck_images(output_folder, deck=deck)
        if len(deck_image_files) != 1:
            raise Exception('Error: expected a single deck image')

        deck_image_file = deck_image_files[0]
        created_files = [deck_image_file]

        # generate and upload TTS assets
        asset_name = os.path.split(deck_image_file)[
            1].split('.')[0] + '_tts'
        with open(tts_config_path, 'r') as stream:
            tts_config = json.load(stream)

        google_client = GoogleDriveClient(
            tts_config.get('google_secrets_path'))

        # create/update the front image on Google drive
        front_file_name = asset_name + '.png'
        target_folder = tts_config.get('google_tts_folder_id')
        front_ids = google_client.get_ids(front_file_name, target_folder)
        if len(front_ids) == 0:
            front_id = google_client.create_png(
                deck_image_file, front_file_name, target_folder)
        else:
            front_id = front_ids[0]
            google_client.update_png(deck_image_file, front_id)

        # get the id of the back image, copy it to the target folder
        assets_folder = tts_config.get('google_assets_folder_id')
        back_name = tts_config.get('back_image')
        back_ids = google_client.get_ids(back_name, assets_folder)
        if len(back_ids) != 1:
            raise Exception('Expected one id found for ' + back_name)
        back_id = back_ids[0]
        if target_folder != assets_folder:
            google_client.copy_file(back_id, None, target_folder)

        # build and save the TTS object locally and on Google drive
        tts_deck = TTSObjectBuilder.build_deck(
            deck.get_size(), deck.get_dimensions()[0], front_id, back_id)

        if not os.path.exists(output_folder):
            os.makedirs(output_folder)

        tts_file_name = asset_name + '.json'
        tts_file_path = os.path.join(
            output_folder,
            tts_file_name,
        )
        with open(tts_file_path, 'w+') as stream:
            json.dump(tts_deck, stream, indent=4)
        created_files.append(tts_file_path)

        tts_ids = google_client.get_ids(tts_file_name, target_folder)
        if len(tts_ids) == 0:
            google_client.create_json(
                tts_file_path, tts_file_name, target_folder)
        else:
            google_client.update_json(tts_file_path, tts_ids[0])

        # optionally copy to the TTS folder for easy access in game
        if copy_to_tts:
            if (os.path.exists(GenAndTTS._TTS_SAVED_OBJECTS_FOLDER)):
                tts_copy = shutil.copy(
                    tts_file_path, GenAndTTS._TTS_SAVED_OBJECTS_FOLDER)
                created_files.append(tts_copy)
            else:
                print('Warning: could not copy to TTS - folder does not exist')

        return created_files

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

    created_files = GenAndTTS.run(
        args.tts_config,
        args.deck_config,
        args.decklist,
        args.out_folder,
        args.copy_to_tts
    )
    for file in created_files:
        if file:
            print('Saved result in ' + file)
