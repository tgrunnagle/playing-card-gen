#!/usr/bin/python
from image_provider import ImageProvider
from PIL import Image
from placement import Placement, to_box, copy_placement
from config_enums import SymbolDirection
from card_layer import CardLayer


class BasicImageLayer(CardLayer):
    def __init__(
        self,
        image_provider: ImageProvider,
        art_id: str,
        art_placement: Placement
    ):
        self._image_provider = image_provider
        self._art_id = art_id
        self._art_placement = art_placement

    def render(self, onto: Image.Image):
        with self._image_provider.get_image(self._art_id) as image:
            w_ratio = image.width / self._art_placement.w
            h_ratio = image.height / self._art_placement.h
            if w_ratio <= h_ratio:
                w_resized = self._art_placement.w
                h_resized = int(image.height / w_ratio)
            else:
                w_resized = int(image.width / h_ratio)
                h_resized = self._art_placement.h

            with image.resize((w_resized, h_resized)) as resized:
                with resized.crop((0, 0, self._art_placement.w, self._art_placement.h)) as cropped:
                    onto.paste(
                        im=cropped,
                        box=to_box(self._art_placement),
                        mask=cropped
                    )


class SymbolRowImageLayer(CardLayer):

    def __init__(
        self,
        image_provider: ImageProvider,
        symbols: str,
        symbol_id_map: dict[str, str],
        initial_placement: Placement,
        spacing: int,
        direction: SymbolDirection
    ):
        self._inner_layers: list[CardLayer] = []

        placement = copy_placement(initial_placement)

        # go backwards through the string if going right (LTR) or UP (BTT)
        for symbol in (
                symbols
            if direction in [SymbolDirection.RIGHT, SymbolDirection.DOWN]
            else symbols[::-1]
        ):
            if symbol.isspace():
                continue

            self._inner_layers.append(
                BasicImageLayer(
                    image_provider,
                    symbol_id_map.get(symbol),
                    placement
                )
            )

            placement = copy_placement(placement)

            if direction == SymbolDirection.RIGHT:
                placement.x = placement.x + (spacing + placement.w)
            elif direction == SymbolDirection.LEFT:
                placement.x = placement.x - (spacing + placement.w)
            elif direction == SymbolDirection.DOWN:
                placement.y = placement.y + (spacing + placement.h)
            else:
                placement.y = placement.y - (spacing + placement.h)

    def render(self, onto: Image.Image):
        for layer in self._inner_layers:
            layer.render(onto)
