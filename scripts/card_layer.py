#!/usr/bin/python
from abc import ABC, abstractmethod

from PIL import Image


class CardLayer(ABC):

    @abstractmethod
    def render(self, onto: Image.Image) -> Image.Image:
        pass

    @staticmethod
    def _within_box(
            outer: tuple[int, int, int, int],
            inner: tuple[int, int, int, int]
    ) -> bool:
        return outer[0] <= inner[0] \
            and outer[1] <= inner[1] \
            and outer[2] >= inner[2] \
            and outer[3] >= inner[3]

    @staticmethod
    def _move_box(
        target: tuple[int, int],
        box: tuple[int, int, int, int]
    ) -> tuple[int, int, int, int]:
        return (
            target[0],
            target[1],
            box[2] - (box[0] - target[0]),
            box[3] - (box[1] - target[1])
        )
