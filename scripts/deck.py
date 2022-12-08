#!/usr/bin/python
from math import ceil

import PIL.Image
from card import Card
from config_enums import ImageLayout
from typing import Tuple

class Deck:

    DEFAULT_MAX_WIDTH = 10

    def __init__(self, name: str, config: dict):
        self._name = name
        self._cards: list[Card] = list()
        self._layout = config.get('output_image_layout') or ImageLayout.SHEET
        self._padding = (
            config.get('output_x_padding') or 0,
            config.get('output_y_padding') or 0
        )
        self._padding_color = config.get('output_padding_colorstring') or '#000000'
        self._sheet_max_width = config.get('output_sheet_max_width') or Deck.DEFAULT_MAX_WIDTH

    def get_size(self):
        return len(self._cards)

    def get_name(self):
        return self._name

    def get_dimensions(self) -> Tuple[int, int]:
        width = min(self._sheet_max_width, self.get_size())
        height = ceil(self.get_size() / width)
        return (width, height)

    def add_card(self, card: Card):
        self._cards.append(card)

    def render(self) -> list[PIL.Image.Image]:
        return \
            self._render_singletons() \
            if self._layout == ImageLayout.SINGLETON \
            else self._render_sheets()

    def _render_sheets(self) -> list[PIL.Image.Image]:
        num_cards = len(self._cards)
        if num_cards == 0:
            return []

        (num_w, num_h) = self.get_dimensions()

        card_place = self._cards[0].get_placement()
        card_place.w = card_place.w + 2 * self._padding[0]
        card_place.h = card_place.h + 2 * self._padding[1]

        deck_pix_w = card_place.w * num_w
        deck_pix_h = card_place.h * num_h

        deck_image = PIL.Image.new('RGBA', (int(deck_pix_w), int(deck_pix_h)))

        card_index = 0
        for y in range(num_h):
            for x in range(num_w):
                card = self._cards[card_index]
                card_index = card_index + 1

                with self._render_with_padding(card) as card_image:
                    x_start = x * card_place.w
                    x_end = (x + 1) * card_place.w
                    y_start = y * card_place.h
                    y_end = (y + 1) * card_place.h
                    deck_image.paste(im=card_image, box=(
                        x_start, y_start, x_end, y_end))

        return [deck_image]

    def _render_singletons(self) -> list[PIL.Image.Image]:
        num_cards = len(self._cards)
        if num_cards == 0:
            return []
        result = []
        for card_index in range(num_cards):
            card = self._cards[card_index]
            result.append(self._render_with_padding(card))
        return result

    def _render_with_padding(self, card: Card) -> PIL.Image.Image:
        if self._padding == (0, 0):
            return card.render()
        with card.render() as card_image:
            padded_image = PIL.Image.new(
                'RGBA',
                (
                    card_image.width + 2 * self._padding[0],
                    card_image.height + 2 * self._padding[1],
                ),
                color=self._padding_color
            )
            padded_image.paste(
                card_image, (self._padding[0], self._padding[1]))
            return padded_image
