#!/usr/bin/python
import argparse
import os

from requests import request


class GenRemote():

    @staticmethod
    def run(
        config_path: str, decklist_path: str, output_folder: str, port: int | None
    ) -> str:

        if not os.path.exists(output_folder):
            os.makedirs(output_folder)

        out_file = os.path.join(
            output_folder,
            os.path.split(decklist_path)[1].split('.')[0] + '.png')

        with \
                open(config_path) as config, \
                open(decklist_path) as decklist, \
                request(
                    url='http://localhost:' + str(port or 8084) + '/gen',
                    files={'config': config, 'decklist': decklist},
                    method='POST',
                    stream=True,
                ) as response, \
                open(out_file, 'wb+') as result:

            result.write(response.content)
        return out_file


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument('--config', type=str, required=True,
                        help='Path to json-formatted generator config')
    parser.add_argument('--decklist', type=str, required=True,
                        help='Path to the cards list csv')
    parser.add_argument('--port', type=int, required=False,
                        help='Remote port')
    parser.add_argument('--out_folder', type=str, required=False, default='.')

    args = parser.parse_args()
    out_file = GenRemote.run(args.config, args.decklist,
                             args.out_folder, args.port)
    print('Saved result to ' + out_file)
