#!/usr/bin/python
import argparse
import csv
import io
import json
from abc import ABC

from card_builder import CardBuilderFactory
from config_enums import ImageProviderType
from deck_builder import DeckBuilder
from flask import Flask, request, send_file
from input_parameters import InputParameters
from werkzeug.exceptions import BadRequest


class Server(ABC):

    server = Flask(__name__)

    @staticmethod
    def run(assets_folder: str, host: str, port: int):
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

        # override the image to the server folder
        config['local_assets_folder'] = Server.assets_folder

        decklist = request.files.get('decklist')
        if decklist is None:
            return BadRequest('Decklist file required')

        with io.TextIOWrapper(decklist.stream, encoding='utf-8') as dls:
            cards = csv.DictReader(dls.readlines())

        params = InputParameters(config, '', cards)

        card_builder = CardBuilderFactory.build(params.config)
        deck_builder = DeckBuilder(card_builder)
        deck = deck_builder.build(params.decklist)

        with deck.render() as deck_image:
            stream = io.BytesIO()
            deck_image.save(stream, format='png')
            stream.seek(0)
            return send_file(stream,  mimetype='image/png')


if __name__ == "__main__":

    parser = argparse.ArgumentParser()
    parser.add_argument('--assets_folder', type=str, required=True,
                        help='Path to assets')
    parser.add_argument('--host', type=str, required=False)
    parser.add_argument('--port', type=int, required=False, default=8084)
    args = parser.parse_args()

    Server.run(args.assets_folder, args.host, args.port)
