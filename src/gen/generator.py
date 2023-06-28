#!/usr/bin/python

import contextlib
from abc import ABC

from PIL.Image import Image

from card.card_builder import CardBuilder
from deck.deck import Deck
from deck.deck_builder import DeckBuilder
from param.input_parameters import InputParameters
from provider.decklist_provider import DecklistProviderFactory
from provider.image_provider import ImageProviderFactory


class Generator(ABC):
    @staticmethod
    def gen_deck(deck_name: str, params: InputParameters) -> Deck:
        card_builder = CardBuilder(params.config)
        deck_builder = DeckBuilder(card_builder, params.config)
        decklist = DecklistProviderFactory.build(params.config).get_list(deck_name)
        deck = deck_builder.build(params.deck_name, decklist)
        return deck

    @staticmethod
    def gen_images(
        deck: Deck,
        params: InputParameters,
    ) -> list[str]:
        image_provider = ImageProviderFactory.build(params.config)

        def _save_and_close(name: str, img: Image) -> str:
            with contextlib.closing(img):
                return image_provider.save_image(name, img)

        images = deck.render()
        deck_name = deck.get_name()
        result_files = list(
            map(
                _save_and_close,
                [
                    Generator._get_image_name(deck_name, i)
                    for i in range(len(images))
                ],
                images,
            )
        )
        return result_files

    @staticmethod
    def gen_back_image(
        deck: Deck,
        params: InputParameters,
    ) -> str | None:
        if not deck.has_back():
            return None
        image_provider = ImageProviderFactory.build(params.config)
        image = deck.render_back()
        with contextlib.closing(image):
            return image_provider.save_image(deck.get_name() + "_back.png", image)

    @staticmethod
    def _get_image_name(deck_name: str, index: int) -> str:
        return deck_name + "_" + str(index) + ".png"
