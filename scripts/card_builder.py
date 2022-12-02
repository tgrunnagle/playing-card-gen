#!/usr/bin/python
from abc import ABC, abstractmethod

from card import Card
from placement import *
from image_provider import ImageProviderFactory
from card_layer_factory import CardLayerFactory
from config_enums import CardBuilderType


class CardBuilder(ABC):

    @abstractmethod
    def build(self, card_info: dict[str, str]) -> Card:
        pass


class CardBuilderFactory(ABC):

    _DEFAULT_TYPE = CardBuilderType.BASIC

    @staticmethod
    def build(config: dict) -> CardBuilder:
        card_type: CardBuilderType = config.get(
            'card_type') or CardBuilderFactory._DEFAULT_TYPE
        if card_type == CardBuilderType.BASIC:
            return BasicCardBuilder(config)
        else:
            raise Exception('Unsupported card type "' + card_type + '"')


class BasicCardBuilder(CardBuilder):

    def __init__(
        self,
        config: dict
    ):
        self._image_provider = ImageProviderFactory.build(config)
        self._config = config

    def build(self, card_info: dict[str, str]) -> Card:
        card = Card(self._config.get('w'), self._config.get('h'))
        card.add_layers(
            CardLayerFactory.build(
                self._config, card_info, self._image_provider)
        )
        return card
