#!/usr/bin/python
import json
from abc import ABC
from dataclasses import dataclass
import os

from provider.decklist_provider import DecklistProviderFactory


@dataclass
class InputParameters:
    config: dict
    decklist: list[dict[str, str]]
    deck_name: str

class InputParameterBuilder(ABC):

    @staticmethod
    def build(config_path: str, decklist_id: str):
        with open(config_path, 'r') as config_file:
            config = json.load(config_file)

        decklist = DecklistProviderFactory.build(config).get_list(decklist_id)
        decklist_name = os.path.split(decklist_id)[1].split('.')[0]

        return InputParameters(
            config,
            decklist,
            decklist_name,
        )

