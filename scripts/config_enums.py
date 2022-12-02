#!/usr/bin/python
from enum import StrEnum


class CardBuilderType(StrEnum):
    BASIC = 'basic'


class CardLayerType(StrEnum):
    STATIC_TEXT = 'static_text'
    TEXT = 'text'
    EMBEDDED_TEXT = 'embedded_text'
    STATIC_IMAGE = 'static_image'
    IMAGE = 'image'
    SYMBOL_ROW = 'symbol_row'


class DecklistProviderType(StrEnum):
    LOCAL = 'local'
    GOOGLE = 'google'


class ImageProviderType(StrEnum):
    LOCAL = 'local'
    GOOGLE = 'google'


class SymbolDirection(StrEnum):
    RIGHT = 'right'
    LEFT = 'left'
    DOWN = 'down'
    UP = 'up'


class VerticalTextAlignment(StrEnum):
    TOP = 'top'
    MIDDLE = 'middle'
    BOTTOM = 'bottom'
