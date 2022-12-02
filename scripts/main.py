#!/usr/bin/python
import argparse
from abc import ABC

from generator import Generator
from input_parameters import InputParameterBuilder


class Main(ABC):
    @staticmethod
    def run(config_path: str, decklist_id: str):
        params = InputParameterBuilder.build(config_path, decklist_id)
        Generator.run(params)


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument('--config', type=str, required=True,
                        help='Path to json-formatted generator config')
    parser.add_argument('--decklist', type=str, required=True,
                        help='Id/path for cards list csv')
    args = parser.parse_args()
    Main.run(args.config, args.decklist)
