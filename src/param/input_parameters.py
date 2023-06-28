#!/usr/bin/python
import json
import os
from abc import ABC
from dataclasses import dataclass


@dataclass
class InputParameters:
    config: dict
    deck_name: str


class InputParameterBuilder(ABC):
    @staticmethod
    def build(gen_config_path: str, deck_config_path: str, decklist_file: str):
        with open(gen_config_path, "r") as f:
            gen_config = json.load(f)
        with open(deck_config_path, "r") as f:
            deck_config = json.load(f)

        config = gen_config | deck_config

        decklist_name = os.path.basename(decklist_file).split(".")[0]

        return InputParameters(
            config,
            decklist_name,
        )
