#!/usr/bin/python
import argparse
import json
import os
import sys
from abc import ABC
import shutil

from gen_local import GenLocal

sys.path.append(os.path.dirname(os.path.dirname(os.path.realpath(__file__))))

from decklist_provider import DecklistProviderFactory  # noqa
from google_drive_client import GoogleDriveClient  # noqa
from tts_object_builder import TTSObjectBuilder  # noqa


class GenAndTTS(ABC):
    def run(
        tts_config_path: str,
        deck_config_path: str,
        decklist_path: str,
        output_folder: str,
        copy_to_tts: bool,
    ) -> list[str]:

        deck_image_file = GenLocal.run(
            deck_config_path, decklist_path, output_folder)

        asset_name = os.path.split(deck_image_file)[1].split('.')[0] + '_tts_deck'

        with open(deck_config_path, 'r') as stream:
            deck_config = json.load(stream)
        with open(tts_config_path, 'r') as stream:
            tts_config = json.load(stream)

        google_client = GoogleDriveClient(
            tts_config.get('google_secrets_path'))

        target_file_name = asset_name + '.png'
        target_folder = tts_config.get('google_tts_folder_id')
        target_ids = google_client.get_ids(target_file_name, target_folder)
        if len(target_ids) == 0:
            target_id = google_client.create_png(
                deck_image_file, target_file_name, target_folder)
        else:
            target_id = target_ids[0]
            google_client.update_png(deck_image_file, target_id)

        assets_folder = tts_config.get('google_assets_folder_id')
        back_name = tts_config.get('back_image')
        back_ids = google_client.get_ids(back_name, assets_folder)
        if len(back_ids) == 0:
            raise Exception('No id found for ' + back_name)
        back_id = back_ids[0]

        # TODO avoid rereading the entire decklist to get the # cards
        decklist = DecklistProviderFactory.build(
            deck_config).get_list(decklist_path)
        num = 0
        for _ in decklist:
            num = num + 1
        tts_deck = TTSObjectBuilder.build_deck(
            num, target_id, back_id)

        if not os.path.exists(output_folder):
            os.makedirs(output_folder)
        tts_file = os.path.join(
            output_folder,
            asset_name + '.json',
        )
        with open(tts_file, 'w+') as stream:
            json.dump(tts_deck, stream, indent=4)

        if copy_to_tts:
            copy = shutil.copy(tts_file, _TTS_SAVED_OBJECTS_FOLDER)

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
    parser.add_argument('--copy_to_tts', type=bool, required=False, default=False)
    args = parser.parse_args()

    created_files = GenAndTTS.run(
        args.tts_config, args.deck_config, args.decklist, args.out_folder, args.copy_to_tts)
    for file in created_files:
        if file:
            print('Saved result in ' + file)

