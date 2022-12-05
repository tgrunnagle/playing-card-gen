#!/usr/bin/python
from math import ceil

import PIL.Image
from card import Card

class Deck:

    _MAX_WIDTH = 10

    def __init__(self, name: str):
        self._name = name
        self._cards: list[Card] = list()

    def get_size(self):
        return len(self._cards)

    def get_name(self):
        return self._name

    def add_card(self, card: Card):
        self._cards.append(card)

    def render(self) -> PIL.Image.Image:
        num_cards = len(self._cards)
        if num_cards == 0:
            return PIL.Image.new('RGBA', (0, 0))

        num_w = min(Deck._MAX_WIDTH, num_cards)
        num_h = ceil(num_cards / num_w)
        card_place = self._cards[0].get_placement()
        deck_pix_w = card_place.w * num_w
        deck_pix_h = card_place.h * num_h
        deck_image = PIL.Image.new('RGBA', (int(deck_pix_w), int(deck_pix_h)))

        card_index = 0
        for y in range(num_h):
            for x in range(num_w):
                card = self._cards[card_index]
                card_index = card_index + 1

                card_image = card.render()

                x_start = x * card_place.w
                x_end = (x + 1) * card_place.w
                y_start = y * card_place.h
                y_end = (y + 1) * card_place.h
                deck_image.paste(im=card_image, box=(
                    x_start, y_start, x_end, y_end))

                card_image.close()

        return deck_image
