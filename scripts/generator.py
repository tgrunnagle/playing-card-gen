#!/usr/bin/python

import os
from abc import ABC

from card_builder import CardBuilderFactory
from deck_builder import DeckBuilder
from input_parameters import InputParameters


class Generator(ABC):
    @staticmethod
    def run(params: InputParameters):

        card_builder = CardBuilderFactory.build(params.config)
        deck_builder = DeckBuilder(card_builder)
        deck = deck_builder.build(params.decklist)

        if params.decklist_id.endswith('.csv'):
            out_name = params.decklist_id.split('/')[-1].split('.')[0]
        else:
            out_name = params.decklist_id

        out_folder = params.config.get('output_folder')
        if not os.path.exists(out_folder):
            os.makedirs(out_folder)
        out_file = os.path.join(
            out_folder,
            out_name + '.png')

        with deck.render() as deck_image:
            deck_image.save(out_file, bitmap_format='png')
            print('Saved result to ' + out_file)