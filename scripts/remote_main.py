#!/usr/bin/python
from abc import ABC
from requests import request
import os
import argparse


class RemoteMain(ABC):

    @staticmethod
    def run(config_path: str, decklist_path: str):

        out_name = decklist_path.split('/')[-1].split('.')[0]
        out_file = os.path.join(
            './',
            out_name + '.png')

        with \
            open(config_path) as config, \
            open(decklist_path) as decklist, \
            request(
                url='http://localhost:8084/gen',
                files={'config': config, 'decklist': decklist},
                method='POST',
                stream=True,
            ) as response, \
            open(out_file, 'wb+') as result:

            result.write(response.content)

        print('Saved result to ' + out_file)


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument('--config', type=str, required=True,
                        help='Path to json-formatted generator config')
    parser.add_argument('--decklist', type=str, required=True,
                        help='Id/path for cards list csv')
    args = parser.parse_args()
    RemoteMain.run(args.config, args.decklist)
