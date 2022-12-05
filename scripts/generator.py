#!/usr/bin/python

import os
from abc import ABC

from card_builder import CardBuilderFactory
from deck_builder import DeckBuilder
from input_parameters import InputParameters

class Generator(ABC):
    @staticmethod
    def run(params: InputParameters, output_file: str) -> str:

        card_builder = CardBuilderFactory.build(params.config)
        deck_builder = DeckBuilder(card_builder)
        deck = deck_builder.build(params.decklist)

        out_folder = os.path.dirname(output_file)
        if not os.path.exists(out_folder):
            os.makedirs(out_folder)

        if not output_file.endswith('.png'):
            output_file = output_file + '.png'

        with deck.render() as deck_image:
            deck_image.save(output_file, bitmap_format='png')
        return output_file