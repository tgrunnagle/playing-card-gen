#!/usr/bin/python

import contextlib
import os
from abc import ABC
from typing import Optional, Tuple

from card_builder import CardBuilderFactory
from deck import Deck
from deck_builder import DeckBuilder
from input_parameters import InputParameters


class Generator(ABC):
    def gen_deck(params: InputParameters) -> Deck:

        card_builder = CardBuilderFactory.build(params.config)
        deck_builder = DeckBuilder(card_builder, params.config)
        deck = deck_builder.build(params.deck_name, params.decklist)
        return deck

    def gen_deck_images(
        out_folder: str,
        params: Optional[InputParameters] = None,
        deck: Optional[Deck] = None
    ) -> list[str]:

        if (params is None) == (deck is None):
            Exception('One of either params or deck must be set')

        if deck is None:
            deck = Generator.gen_deck(params)

        if not os.path.exists(out_folder):
            os.makedirs(out_folder)

        result_files = []
        image_index = 0
        deck_images = deck.render()
        for deck_image in deck_images:
            with contextlib.closing(deck_image):
                file_name = deck.get_name() + '.png' \
                    if len(deck_images)== 1 \
                    else deck.get_name() + '_' + str(image_index) + '.png'

                out_file = os.path.join(
                    out_folder, file_name)
                deck_image.save(out_file, bitmap_format='png')

            image_index = image_index + 1
            result_files.append(out_file)

        return result_files
