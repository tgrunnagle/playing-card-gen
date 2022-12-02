#!/usr/bin/python
import json
from abc import ABC
from dataclasses import dataclass

from decklist_provider import DecklistProviderFactory


@dataclass
class InputParameters:
    config: dict
    decklist_id: str
    decklist: list[dict[str, str]]

class InputParameterBuilder(ABC):

    @staticmethod
    def build(config_path: str, decklist_id: str):
        with open(config_path, 'r') as config_file:
            config = json.load(config_file)

        decklist = DecklistProviderFactory.build(config).get_list(decklist_id)

        return InputParameters(
            config,
            decklist_id,
            decklist,
        )

