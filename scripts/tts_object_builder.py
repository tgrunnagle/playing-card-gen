#!/usr/bin/python
import json
import os
from abc import ABC
from math import ceil

from deck import MAX_WIDTH


class TTSObjectBuilder(ABC):

    _TEMPLATE_FILE = os.path.join(os.path.dirname(
        os.path.realpath(__file__)), 'tts_deck_object_template.json')
    _DECK_KEY = 41  # TODO understand what the keys in "CustomDeck are"
    _URL_FORMAT = 'https://drive.google.com/uc?export=download&id={}'

    def build_deck(deck_size: int, front_id: str, back_id: str) -> dict:
        with open(TTSObjectBuilder._TEMPLATE_FILE) as template:
            deck_object = json.load(template)

        deck_object['ObjectStates'][0]['DeckIDs'] = [TTSObjectBuilder._DECK_KEY *
                                                     100 + i for i in range(deck_size)]

        num_wide = min(MAX_WIDTH, deck_size)
        deck_object['ObjectStates'][0]['CustomDeck'] = {
            str(TTSObjectBuilder._DECK_KEY): {
                "FaceURL": TTSObjectBuilder._URL_FORMAT.format(front_id),
                "BackURL": TTSObjectBuilder._URL_FORMAT.format(back_id),
                "NumWidth": num_wide,
                "NumHeight": ceil(deck_size / num_wide),
                "BackIsHidden": True,
                "UniqueBack": False,
                "Type": 0
            }
        }

        return deck_object