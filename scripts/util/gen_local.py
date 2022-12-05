#!/usr/bin/python
import argparse
import os
import sys
from abc import ABC

sys.path.append(os.path.dirname(os.path.dirname(os.path.realpath(__file__))))

from generator import Generator  # noqa
from input_parameters import InputParameterBuilder  # noqa


class GenLocal(ABC):
    def run(config_path: str, decklist_id: str, output_folder: str) -> str:
        params = InputParameterBuilder.build(config_path, decklist_id)

        # output name is the same as the decklist
        output_name = os.path.split(decklist_id)[1].split('.')[0] + '.png'
        output_file = Generator.run(params, os.path.join(output_folder, output_name))
        return output_file


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument('--config', type=str, required=True,
                        help='Path to json-formatted generator config')
    parser.add_argument('--decklist', type=str, required=True,
                        help='Id/path for cards list csv')
    parser.add_argument('--out_folder', type=str, required=False, default='.')
    args = parser.parse_args()
    out_file = GenLocal.run(args.config, args.decklist, args.out_folder)
    print('Saved result to ' + out_file)
