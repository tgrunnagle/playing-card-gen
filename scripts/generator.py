#!/usr/bin/python

import contextlib
import os
from abc import ABC
from typing import Optional, Tuple
from PIL.Image import Image

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
        result_files.extend(
            list(
                map(
                    Generator._save_deck_image,
                    zip(
                        deck.render(),
                        [
                            Generator._get_output_path(
                                out_folder, deck.get_name(), i)
                            for i in range(deck.get_size())
                        ]
                    )
                )
            )
        )

        return result_files

    def _save_deck_image(image_and_path: Tuple[Image, str]) -> str:
        with contextlib.closing(image_and_path[0]):
            image_and_path[0].save(image_and_path[1], bitmap_format='png')
        return image_and_path[1]

    def _get_output_path(out_folder: str, deck_name: str, image_index: int) -> str:
        return os.path.join(
            out_folder,
            deck_name + '_' + str(image_index) + '.png'
        )
