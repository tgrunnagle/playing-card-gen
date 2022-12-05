#!/usr/bin/python
import argparse
import os
from abc import ABC
from typing import Optional, Tuple

from requests import request


class GenRemote(ABC):

    # returns [result file, deck size]
    def run(
        config_path: str, decklist_path: str, output_folder: str, port: Optional[int]
    ) -> Tuple[str, int]:

        if not os.path.exists(output_folder):
            os.makedirs(output_folder)

        out_name = decklist_path.split('/')[-1].split('.')[0]
        out_file = os.path.join(
            output_folder,
            out_name + '.png')

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
            deck_size = int(response.headers.get('deck_size'))
        return (out_file, deck_size)


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
    (out_file, _) = GenRemote.run(args.config, args.decklist,
                             args.out_folder, args.port)
    print('Saved result to ' + out_file)
