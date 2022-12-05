#!/usr/bin/python

from card_builder import CardBuilder
from deck import Deck


class DeckBuilder:

    def __init__(
        self,
        card_builder: CardBuilder,
    ):
        self._cb = card_builder

    def build(self, name: str, cards_config: list[dict]) -> Deck:
        deck = Deck(name)
        for card_config in cards_config:
            if not bool(card_config.get('skip')):
                deck.add_card(self._cb.build(card_config))
        return deck
