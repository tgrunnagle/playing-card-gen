#!/usr/bin/python
import argparse

from gen.generator import Generator
from google.google_drive_client import GoogleDriveClient
from param.config_enums import ImageProviderType
from param.input_parameters import InputParameterBuilder
from tts.tts_helper import TTSHelper
from util.helpers import Helpers as h

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--gen_config",
        type=str,
        required=True,
        help="Path to json-formatted generation configuration.",
    )
    parser.add_argument(
        "--deck_config",
        type=str,
        required=True,
        help="Path to json-formatted deck configuration.",
    )
    parser.add_argument(
        "--decklist",
        type=str,
        required=True,
        help="Path/name of the decklist to generate.",
    )
    parser.add_argument(
        "--tts", action="store_true", help="Flag to build and save a TTS deck object."
    )
    args = parser.parse_args()

    params = InputParameterBuilder.build(
        args.gen_config, args.deck_config, args.decklist
    )
    deck = Generator.gen_deck(args.decklist, params)
    image_files = Generator.gen_images(deck, params)
    back_image_file = Generator.gen_back_image(deck, params)

    if args.tts:
        if (
            len(image_files) != 1
            or not back_image_file
            or h.require(params.config, "image_provider") != ImageProviderType.GOOGLE
        ):
            raise Exception(
                "Expected a single output image (sheet), a back, and google image provider for TTS"
            )
        google_client = GoogleDriveClient(
            h.require(params.config, "google_secrets_path")
        )
        front_id = image_files[0]
        back_id = back_image_file
        tts_file = TTSHelper.build_and_save(
            deck.get_name(),
            deck.get_size(),
            deck.get_dimensions()[0],
            front_id,
            back_id,
            h.dont_require("tts/local_output_folder"),
        )
        print("Saved TTS object to " + tts_file)
        google_client.create_or_update_json(tts_file, h.require("output/folder"))
        print("Uploaded TTS object to google drive")
