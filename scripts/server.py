#!/usr/bin/python
import argparse
import csv
import io
import json
import os
import threading
from abc import ABC
from typing import Optional

from card_builder import CardBuilderFactory
from config_enums import ImageProviderType
from deck_builder import DeckBuilder
from flask import Flask, g, request, send_file
from input_parameters import InputParameters
from werkzeug.exceptions import BadRequest


class CleanupDaemon():

    _CLEANUP_INTERVAL = 10

    def __init__(self):
        self._lock = threading.Lock()
        self._cleanup_lock = threading.Lock()
        self._running = False
        self._files = []
        self._streams = []

    def start(self):
        if self._running:
            return
        self._lock.acquire()
        try:
            if self._running:
                return

            self._schedule_cleanup()
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

    def add_stream(self, stream: io.IOBase):
        if not self._running:
            raise Exception('cleanup daemon not running')

        self._lock.acquire()
        try:
            self._streams.append(stream)
        finally:
            self._lock.release()

    def _file_count(self) -> int:
        return len(self._files)

    def _stream_count(self) -> int:
        return len(self._streams)

    def _pop_file(self) -> Optional[str]:
        self._lock.acquire()
        try:
            if len(self._files) == 0:
                return None
            return self._files.pop(0)
        finally:
            self._lock.release()

    def _pop_stream(self) -> Optional[io.IOBase]:
        self._lock.acquire()
        try:
            if len(self._streams) == 0:
                return None
            return self._streams.pop(0)
        finally:
            self._lock.release()

    def _schedule_cleanup(self):
        timer = threading.Timer(
            CleanupDaemon._CLEANUP_INTERVAL, self._cleanup, args=())
        timer.daemon = True
        timer.start()

    def _cleanup(self):
        self._cleanup_lock.acquire()
        try:
            # only process as many files/streams as there are to start
            # in case this method re-adds them.
            # no other thread should be removing items while the
            # _cleanup_lock is held.
            file_count = self._file_count()
            for _ in range(file_count):
                file = self._pop_file()
                if file is not None and os.path.exists(file):
                    os.remove(file)

            stream_count = self._stream_count()
            for _ in range(stream_count):
                stream = self._pop_stream()
                if stream is not None and not stream.closed:
                    if stream.tell() == 0:
                        # stream not read yet
                        self.add_stream(stream)
                    else:
                        stream.close()
        except Exception as e:
            print('Exception during cleanup: ' + str(e))
        finally:
            self._cleanup_lock.release()
            self._schedule_cleanup()


class Server(ABC):

    server = Flask(__name__)
    cleanup = CleanupDaemon()

    @staticmethod
    def run(assets_folder: str, host: str, port: int):

        Server.assets_folder = assets_folder

        Server.cleanup.start()

        Server.server.teardown_appcontext(Server._on_context_teardown)
        Server.server.run(host=host, port=port)

    @staticmethod
    def _on_context_teardown(_):
        try:
            # can't close the stream here because the response isn't
            # dont with it yet
            # there's still a race condition with cleanup
            stream: io.BytesIO = g.get('file_stream')
            if stream is not None:
                Server.cleanup.add_stream(stream)

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

        with deck.render() as deck_image:
            stream = io.BytesIO()
            deck_image.save(stream, format='png')
            stream.seek(0)
            g.file_stream = stream
            return send_file(stream,  mimetype='image/png')


if __name__ == "__main__":

    parser = argparse.ArgumentParser()
    parser.add_argument('--assets_folder', type=str, required=True,
                        help='Path to assets')
    parser.add_argument('--host', type=str, required=False)
    parser.add_argument('--port', type=int, required=False, default=8084)
    args = parser.parse_args()

    Server.run(args.assets_folder, args.host, args.port)
