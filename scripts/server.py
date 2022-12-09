#!/usr/bin/python
import argparse
import contextlib
import csv
import io
import json
from abc import ABC
from typing import Optional

from card_builder import CardBuilderFactory
from config_enums import ImageProviderType, ImageLayout
from deck_builder import DeckBuilder
from flask import Flask, request, send_file
from input_parameters import InputParameters
from werkzeug.exceptions import BadRequest


class Server(ABC):

    server = Flask(__name__)

    @staticmethod
    def run(assets_folder: str, host: Optional[str], port: Optional[int]):
        Server.assets_folder = assets_folder
        Server.server.run(host=host, port=port)

    @server.route("/gen", methods=['POST'])
    def gen():
        config_file = request.files.get('config')
        if config_file is None:
            return BadRequest('config file required')
        config: dict = json.load(config_file)

        if config.get('image_provider') != ImageProviderType.LOCAL:
            return BadRequest('Only local images supported')

        if config.get('output_image_layout') == ImageLayout.SINGLETON:
            return BadRequest('Only the sheet layout is supported')

        # override the image to the server folder
        config['local_assets_folder'] = Server.assets_folder

        decklist = request.files.get('decklist')
        if decklist is None:
            return BadRequest('Decklist file required')

        with io.TextIOWrapper(decklist.stream, encoding='utf-8') as stream:
            cards = list(csv.DictReader(stream.readlines()))

        params = InputParameters(config, cards, '')

        if len(params.decklist) == 0:
            return BadRequest('Empty decklist')

        card_builder = CardBuilderFactory.build(params.config)
        deck_builder = DeckBuilder(card_builder, params.config)
        deck = deck_builder.build(params.deck_name, params.decklist)

        deck_images = deck.render()
        if len(deck_images) != 1:
            print('Warning: unexpected number of images: ' + str(len(deck_images)))
            list(map(lambda i: i.close(), deck_images))
            return BadRequest('No result images')

        with contextlib.closing(deck_images[0]):
            stream = io.BytesIO()
            deck_images[0].save(stream, format='png')
            stream.seek(0)
            response = send_file(stream,  mimetype='image/png')

        return response


if __name__ == "__main__":

    parser = argparse.ArgumentParser()
    parser.add_argument('--assets_folder', type=str, required=True,
                        help='Path to assets')
    parser.add_argument('--host', type=str, required=False)
    parser.add_argument('--port', type=int, required=False, default=8084)
    args = parser.parse_args()

    Server.run(args.assets_folder, args.host, args.port)
