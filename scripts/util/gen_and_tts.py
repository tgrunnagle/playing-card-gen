#!/usr/bin/python
import argparse
import json
import os
import sys
from abc import ABC
import shutil
from typing import Optional

from gen_local import GenLocal
from gen_remote import GenRemote

sys.path.append(os.path.dirname(os.path.dirname(os.path.realpath(__file__))))

from google_drive_client import GoogleDriveClient  # noqa
from tts_object_builder import TTSObjectBuilder  # noqa


class GenAndTTS(ABC):
    def run(
        tts_config_path: str,
        deck_config_path: str,
        decklist_path: str,
        output_folder: str,
        gen_remote: bool,
        remote_port: Optional[int],
        copy_to_tts: bool,
    ) -> list[str]:

        # generate the deck
        (deck_image_file, deck_size) = \
            GenRemote.run(deck_config_path, decklist_path, output_folder, remote_port) \
            if gen_remote \
            else GenLocal.run(deck_config_path, decklist_path, output_folder)

        asset_name = os.path.split(deck_image_file)[
            1].split('.')[0] + '_tts_deck'

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

        # download the back image
        assets_folder = tts_config.get('google_assets_folder_id')
        back_name = tts_config.get('back_image')
        back_ids = google_client.get_ids(back_name, assets_folder)
        if len(back_ids) == 0:
            raise Exception('No id found for ' + back_name)
        back_id = back_ids[0]

        # build and save the TTS object
        tts_deck = TTSObjectBuilder.build_deck(
            deck_size, front_id, back_id)

        if not os.path.exists(output_folder):
            os.makedirs(output_folder)
        tts_file = os.path.join(
            output_folder,
            asset_name + '.json',
        )
        with open(tts_file, 'w+') as stream:
            json.dump(tts_deck, stream, indent=4)

        # optionally copy to the TTS folder for easy access in game
        if copy_to_tts:
            if (os.path.exists(_TTS_SAVED_OBJECTS_FOLDER)):
                copy = shutil.copy(tts_file, _TTS_SAVED_OBJECTS_FOLDER)
            else:
                print('Warning: could not copy to TTS - folder does not exist')

        return [deck_image_file, tts_file, copy]


_TTS_SAVED_OBJECTS_FOLDER = os.path.expanduser('~') + \
    '/Documents/My Games/Tabletop Simulator/Saves/Saved Objects'

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument('--tts_config', type=str, required=True,
                        help='Path to json-formatted tts config')
    parser.add_argument('--deck_config', type=str, required=True,
                        help='Path to json-formatted deck generator config')
    parser.add_argument('--decklist', type=str, required=True,
                        help='Id/path for cards list csv')
    parser.add_argument('--out_folder', type=str, required=False, default='.')
    parser.add_argument('--copy_to_tts', type=bool,
                        required=False, default=False)
    parser.add_argument('--remote', type=bool,
                        required=False, default=False)
    parser.add_argument('--port', type=int,
                        required=False)
    args = parser.parse_args()

    created_files = GenAndTTS.run(
        args.tts_config,
        args.deck_config,
        args.decklist,
        args.out_folder,
        args.remote,
        args.port,
        args.copy_to_tts
    )
    for file in created_files:
        if file:
            print('Saved result in ' + file)
