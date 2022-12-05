#!/usr/bin/python
import json
import os
from abc import ABC
from math import ceil

# try to keep imports to a minimum to make running this
# locally as easy as possible


class TTSObjectBuilder(ABC):

    _MAX_WIDTH = 10  # this should match Deck._MAX_WIDTH
    _TEMPLATE_FILE = os.path.join(os.path.dirname(
        os.path.realpath(__file__)), 'tts_deck_object_template.json')
    _DECK_KEY = 41  # TODO understand what the keys in "CustomDeck are"
    _URL_FORMAT = 'https://drive.google.com/uc?export=download&id={}'

    # returns the dict representation of the TTS saved object file
    # use json.dump to write it to a file
    def build_deck(deck_size: int, front_id: str, back_id: str) -> dict:
        with open(TTSObjectBuilder._TEMPLATE_FILE) as template:
            deck_object = json.load(template)

        deck_object['ObjectStates'][0]['DeckIDs'] = [TTSObjectBuilder._DECK_KEY *
                                                     100 + i for i in range(deck_size)]

        num_wide = min(TTSObjectBuilder._MAX_WIDTH, deck_size)
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
