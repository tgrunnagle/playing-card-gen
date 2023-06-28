#!/usr/bin/python
import json
import os
from abc import ABC

from deck.deck import Deck
from tts.tts_object_builder import TTSObjectBuilder


class TTSHelper(ABC):
    _TTS_SAVED_OBJECTS_FOLDER = (
        os.path.expanduser("~")
        + "/Documents/My Games/Tabletop Simulator/Saves/Saved Objects"
    )

    @staticmethod
    def build_and_save(
        deck_name: str,
        deck_size: int,
        deck_image_width: int,
        front_id: str,
        back_id: str,
        out_folder: str | None,
    ) -> str:
        out_folder = out_folder or TTSHelper._TTS_SAVED_OBJECTS_FOLDER
        deck_object = TTSObjectBuilder.build_deck(
            deck_size, deck_image_width, front_id, back_id
        )

        if not os.path.exists(out_folder):
            raise Exception("Could not save TTS object, output folder does not exist")

        out_file = os.path.join(out_folder, deck_name + ".json")
        with open(out_file, "w") as f:
            json.dump(deck_object, f, indent=4)

        return out_file
