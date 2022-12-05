#!/usr/bin/python

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
        deck_builder = DeckBuilder(card_builder)
        deck = deck_builder.build(params.deck_name, params.decklist)
        return deck

    # return [result file, deck size]
    def gen_deck_image(
        out_folder: str,
        params: Optional[InputParameters] = None,
        deck: Optional[Deck] = None
    ) -> Tuple[str, int]:

        if (params is None) == (deck is None):
            Exception('One of either params or deck must be set')

        if deck is None:
            deck = Generator.gen_deck(params)

        if not os.path.exists(out_folder):
            os.makedirs(out_folder)

        out_file = os.path.join(out_folder, deck.get_name() + '.png')

        with deck.render() as deck_image:
            deck_image.save(out_file, bitmap_format='png')
        return (out_file, deck.get_size())
