#!/usr/bin/python

from card_builder import CardBuilder
from deck import Deck
from typing import Optional
from config_enums import ImageLayout

class DeckBuilder:

    def __init__(
        self,
        card_builder: CardBuilder,
        config: dict
    ):
        self._cb = card_builder
        self._config = config

    def build(self, name: str, cards_config: list[dict]) -> Deck:
        deck = Deck(name, self._config)
        for card_config in cards_config:
            if not bool(card_config.get('skip')):
                for _ in range(int(card_config.get('count') or 1)):
                    deck.add_card(self._cb.build(card_config))
        return deck
