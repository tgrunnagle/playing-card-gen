#!/usr/bin/python
import argparse
import csv
import io
import json
import os
import random
import string
import threading
from abc import ABC
from typing import Optional

from card_builder import CardBuilderFactory
from config_enums import ImageProviderType
from deck_builder import DeckBuilder
from flask import Flask, g, request, send_file
from input_parameters import InputParameters
from werkzeug.exceptions import BadRequest


class CleanupDaemon(ABC):

    _CLEANUP_INTERVAL = 10

    def __init__(self):
        self._lock = threading.Lock()
        self._running = False
        self._files = []

    def start(self):
        if self._running:
            return
        self._lock.acquire()
        try:
            if self._running:
                return

            self._schedule_deletes()
            self._running = True
        finally:
            self._lock.release()

    def add_file(self, file: str):
        if not self._running:
            raise Exception('cleanup daemon not running')

        self._lock.acquire()
        try:
            self._files.append(file)
        finally:
            self._lock.release()

    def _pop_file(self) -> Optional[str]:
        self._lock.acquire()
        try:
            if len(self._files) == 0:
                return None
            return self._files.pop()
        finally:
            self._lock.release()

    def _schedule_deletes(self):
        threading.Timer(
            CleanupDaemon._CLEANUP_INTERVAL, self._delete_files, args=()).start()

    def _delete_files(self):
        try:
            file = self._pop_file()
            while file is not None:
                if os.path.exists(file):
                    os.remove(file)
                file = self._pop_file()
        finally:
            self._schedule_deletes()


class Server(ABC):

    server = Flask(__name__)

    @staticmethod
    def run(assets_folder: str, host: str, port: int):

        Server.assets_folder = assets_folder
        Server.temp_folder = os.path.join(os.path.abspath('.'), 'temp/server/')
        if not os.path.exists(Server.temp_folder):
            os.makedirs(Server.temp_folder)

        Server.cleanup = CleanupDaemon()
        Server.cleanup.start()

        Server.server.teardown_appcontext(Server._on_context_teardown)
        Server.server.run(host=host, port=port)

    @staticmethod
    def _on_context_teardown(_):
        try:
            temp_file = g.get('temp_file')
            if temp_file is not None:
                Server.cleanup.add_file(temp_file)
        except Exception as e:
            print(e)

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

        g.temp_file = temp_file

        return send_file(temp_file,  mimetype='image/png')


if __name__ == "__main__":

    parser = argparse.ArgumentParser()
    parser.add_argument('--assets_folder', type=str, required=True,
                        help='Path to assets')
    parser.add_argument('--host', type=str, required=False)
    parser.add_argument('--port', type=int, required=False, default=8084)
    args = parser.parse_args()

    Server.run(args.assets_folder, args.host, args.port)
