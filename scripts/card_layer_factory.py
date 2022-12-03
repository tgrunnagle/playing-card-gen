#!/usr/bin/python
from abc import ABC

from card_layer import CardLayer
from config_enums import CardLayerType
from image_card_layers import BasicImageLayer, SymbolRowImageLayer
from image_provider import ImageProvider
from placement import *
from text_card_layers import BasicTextLayer, EmbeddedImageTextCardLayer
import os
from typing import Optional

class CardLayerFactory(ABC):

    @staticmethod
    def build(
        config: dict,
        card: dict[str, str],
        image_provider: ImageProvider
    ) -> list[CardLayer]:

        layers: list[CardLayer] = []
        layer_configs: list[dict] = config.get('card_layers') or []
        
        for layer_config in layer_configs:
            layer_type: CardLayerType = layer_config.get('type')
            font_file = CardLayerFactory._get_font_file(
                config,
                layer_config,
            )

            if layer_type == CardLayerType.STATIC_TEXT:
                layers.append(BasicTextLayer(
                    layer_config.get('text'),
                    parse_placement(layer_config.get('place')),
                    layer_config.get('max_font_size') or config.get(
                        'text_max_font_size'),
                    CardLayerFactory._get_font_file(config, layer_config),
                    layer_config.get('spacing_ratio') or config.get(
                        'text_spacing_ratio'),
                    layer_config.get('v_alignment'),
                ))

            elif layer_type == CardLayerType.TEXT:
                layers.append(BasicTextLayer(
                    card.get(layer_config.get('prop')),
                    parse_placement(layer_config.get('place')),
                    layer_config.get('max_font_size') or config.get(
                        'text_max_font_size'),
                    CardLayerFactory._get_font_file(config, layer_config),
                    layer_config.get('spacing_ratio') or config.get(
                        'text_spacing_ratio'),
                    layer_config.get('v_alignment'),
                ))

            elif layer_type == CardLayerType.EMBEDDED_TEXT:
                layers.append(EmbeddedImageTextCardLayer(
                    card.get(layer_config.get('prop')),
                    parse_placement(layer_config.get('place')),
                    image_provider,
                    config.get('text_embed_symbol_id_map'),
                    layer_config.get('max_font_size') or config.get(
                        'text_max_font_size'),
                    CardLayerFactory._get_font_file(config, layer_config),
                    layer_config.get('spacing_ratio') or config.get(
                        'text_spacing_ratio'),
                    layer_config.get('v_alignment'),
                    layer_config.get('embed_v_offset_ratio') or config.get(
                        'text_embed_v_offset_ratio'),
                    layer_config.get('embed_size_ratio') or config.get(
                        'text_embed_size_ratio'),
                ))

            elif layer_type == CardLayerType.STATIC_IMAGE:
                layers.append(BasicImageLayer(
                    image_provider,
                    layer_config.get('image'),
                    parse_placement(layer_config.get('place')),
                ))

            elif layer_type == CardLayerType.IMAGE:
                layers.append(BasicImageLayer(
                    image_provider,
                    card.get(layer_config.get('prop')),
                    parse_placement(layer_config.get('place')),
                ))

            elif layer_type == CardLayerType.SYMBOL_ROW:
                layers.append(SymbolRowImageLayer(
                    image_provider,
                    card.get(layer_config.get('prop')),
                    config.get('symbol_id_map'),
                    parse_placement(layer_config.get('place')),
                    layer_config.get('spacing'),
                    layer_config.get('direction'),
                ))

            else:
                raise Exception('Unsupported layer type "' + layer_type + '"')

        return layers

    @staticmethod
    def _get_font_file(
        config: dict,
        layer_config: dict,
    ) -> Optional[str]:
        font_file = layer_config.get('font_file') or config.get('text_font_file')
        if font_file is None:
            return None
        assets_folder = config.get('local_assets_folder')
        if assets_folder is not None:
            return os.path.join(assets_folder, font_file)
        return font_file

