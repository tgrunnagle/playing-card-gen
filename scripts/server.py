#!/usr/bin/python
import argparse
import csv
import json
from abc import ABC
import io

from card_builder import CardBuilderFactory
from config_enums import ImageProviderType
from deck_builder import DeckBuilder
from flask import Flask, request, send_file
from input_parameters import InputParameters
from werkzeug.exceptions import BadRequest
import os
import random
import string


class Server(ABC):

    server = Flask(__name__)

    @staticmethod
    def run(assets_folder: str):
        Server.assets_folder = assets_folder
        Server.temp_folder = os.path.join(os.path.abspath('.'), 'temp')

        if not os.path.exists(Server.temp_folder):
            os.makedirs(Server.temp_folder)

        Server.server.run(port=8084)


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

        temp_file = os.path.join(Server.temp_folder, ''.join(random.choice(
            string.ascii_letters) for _ in range(10)) + '.png')
        with deck.render() as deck_image:
            deck_image.save(temp_file, bitmap_format='png')
        return send_file(temp_file,  mimetype='image/png')


if __name__ == "__main__":

    parser=argparse.ArgumentParser()
    parser.add_argument('--assets_folder', type=str, required=True,
                        help='Path to assets')

    args=parser.parse_args()

    Server.run(args.assets_folder)
