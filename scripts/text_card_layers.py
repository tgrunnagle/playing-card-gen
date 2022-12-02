#!/usr/bin/python
from dataclasses import dataclass
from typing import Optional
import sys
import os
import pathlib
from image_provider import ImageProvider
from PIL import ImageFont, Image, ImageDraw
from placement import Placement, to_box, move_placement
from card_layer import CardLayer
from image_card_layers import BasicImageLayer
from config_enums import VerticalTextAlignment


_DEFAULT_FONT_WINDOWS = 'constan.ttf'
_DEFAULT_FONT_MACOS = 'Gill Sans.ttf'  # TODO verify this exists
_STARTING_FONT_SIZE = 32


class BasicTextLayer(CardLayer):

    def __init__(
        self,
        text: str,
        placement: Placement,
        max_font_size: Optional[int] = None,
        font_file: Optional[str] = None,
        spacing_ratio: Optional[float] = None,
        v_alignment: Optional[VerticalTextAlignment] = None,
    ):
        self._text = text
        self._placement = placement
        self._starting_font_size = max_font_size or _STARTING_FONT_SIZE
        self._font_file = font_file or _get_default_font_file()
        self._spacing_ratio = spacing_ratio or 0.0
        self._v_alignment = v_alignment or VerticalTextAlignment.TOP

    def render(self, onto: Image.Image):
        outer_box = CardLayer._move_box((0, 0), to_box(self._placement))
        font_size = self._starting_font_size

        draw = ImageDraw.Draw(onto, 'RGBA')
        while True:
            font = ImageFont.truetype(self._font_file, font_size)
            spacing = int(font.getbbox(' ')[3] * self._spacing_ratio)
            multiline_text = '\n'.join(self._split_lines_to_width(font))
            text_box = draw.multiline_textbbox(
                (0, 0), multiline_text, font, spacing=spacing)
            if CardLayer._within_box(outer_box, text_box):
                break
            font_size = font_size - 1
            if font_size < 8:
                print('Warning: failed to fit text in a box')
                break

        v_offset = _get_v_offset(self._v_alignment, text_box, self._placement)
        draw.multiline_text(
            (self._placement.x, self._placement.y + v_offset),
            multiline_text,
            font=font,
            fill=(0, 0, 0, 255),
            spacing=spacing,
        )

    def _split_lines_to_width(self, font: ImageFont.FreeTypeFont) -> list[str]:
        lines = list()
        index = 0
        while index < len(self._text):
            length = _find_next_fit_length(
                self._text, index, font, self._placement.w)
            if length == 0:
                print('Warning: unable to fit text a row')
                return self._text

            lines.append(self._text[index:index + length])
            index = index + length

        return lines


class EmbeddedImageTextCardLayer(CardLayer):

    @dataclass
    class EmbeddedImage:
        place: Placement
        image_id: str

    def __init__(
        self,
        text: str,
        placement: Placement,
        image_provider: ImageProvider,
        embedding_map: dict[str, str],
        max_font_size: Optional[int] = None,
        font_file: Optional[str] = None,
        spacing_ratio: Optional[float] = None,
        v_alignment: Optional[VerticalTextAlignment] = None,
        embed_v_offset_ratio: Optional[float] = None,
        embed_size_ratio: Optional[float] = None
    ):
        self._text = text
        self._placement = placement
        self._image_provider = image_provider
        self._embedding_map = embedding_map
        self._starting_font_size = max_font_size or _STARTING_FONT_SIZE
        self._font_file = font_file or _get_default_font_file()
        self._spacing_ratio = spacing_ratio or 0
        self._v_alignment = v_alignment or VerticalTextAlignment.TOP
        self._embed_v_offset_ratio = embed_v_offset_ratio or 0
        self._embed_size_ratio = embed_size_ratio or 1

    def render(self, onto: Image.Image):
        outer_box = CardLayer._move_box((0, 0), to_box(self._placement))
        font_size = self._starting_font_size
        draw = ImageDraw.Draw(onto, 'RGBA')

        while True:
            font = ImageFont.truetype(self._font_file, font_size)
            spacing = int(self._spacing_ratio * font.getbbox(' ')[3])

            (text_lines, embeds) = self._split_lines_and_place_embeds(
                draw, font, spacing)
            multiline_text = '\n'.join(text_lines)

            text_box = draw.multiline_textbbox(
                (0, 0),
                multiline_text,
                font,
                spacing=spacing)

            if CardLayer._within_box(outer_box, text_box):
                break

            font_size = font_size - 1
            if font_size < 8:
                print('Warning: failed to fit text in a box')
                break

        v_offset = _get_v_offset(self._v_alignment, text_box, self._placement)
        draw.multiline_text(
            (self._placement.x, self._placement.y + v_offset),
            multiline_text,
            font=font,
            fill=(0, 0, 0, 255),
            spacing=spacing)

        embed_v_offset = int(self._embed_v_offset_ratio * font.getbbox(' ')[3])
        self._render_embeds(embeds, v_offset + embed_v_offset, onto)

    def _split_lines_and_place_embeds(
        self,
        draw: ImageDraw.ImageDraw,
        font: ImageFont.FreeTypeFont,
        spacing: int,
    ) -> tuple[list[str], list[EmbeddedImage]]:
        lines = []
        embeds = []
        padding = self._get_padding(draw, font)
        padding_width = draw.textsize(padding, font)[0]
        line_height = draw.textsize(' ', font)[1] + spacing

        (padded_text, embedding_indexes) = self._pad_embeddings(padding)

        index = 0
        while index < len(padded_text):
            length = _find_next_fit_length(
                padded_text, index, font, self._placement.w)
            if length == 0:
                print('Warning: unable to fit text a row')
                return (self._text, [])

            for embed in embedding_indexes:
                if (embed[0] < index + length) and embed[0] >= index:
                    x = self._placement.x + \
                        draw.textsize(padded_text[index:embed[0]], font)[0]
                    y = self._placement.y + (len(lines) * line_height)
                    embeds.append(
                        self.EmbeddedImage(
                            Placement(x, y, padding_width, padding_width),
                            embed[1],
                        ),
                    )

            lines.append(padded_text[index:index + length])
            index = index + length

        return (lines, embeds)

    # returns (padded_string, embedding_indexes)
    def _pad_embeddings(self, padding: str) -> tuple[str, list[tuple[int, str]]]:
        index = 0
        total_padding = 0
        last_index = 0
        embeds = list()

        new_text = ''
        while index < len(self._text):
            next = self._next_word_index(self._text, index)
            word = self._text[index:next]

            embedding = self._embedding_map.get(word.strip())
            if embedding is not None:
                embeds.append((index + total_padding, embedding))
                replacement_text = word.replace(word.strip(), padding)
                new_text = new_text + \
                    self._text[last_index:index] + replacement_text
                last_index = next
                total_padding = total_padding + \
                    len(replacement_text) - len(word)

            index = next

        if last_index != index:
            new_text = new_text + self._text[last_index:index]

        return (new_text, embeds)

    def _next_word_index(self, text: str, start: int) -> int:
        while start < len(text) and not text[start].isspace():
            start = start + 1
        while start < len(text) and text[start].isspace():
            start = start + 1
        return start

    def _render_embeds(self, embeds: list[EmbeddedImage], v_offset: int, onto: Image.Image):
        for embed in embeds:
            BasicImageLayer(
                self._image_provider,
                embed.image_id,
                move_placement(0, v_offset, embed.place)
            ).render(onto)

    def _get_padding(self, draw: ImageDraw.ImageDraw, font: ImageFont.ImageFont) -> str:
        height_px = draw.textsize(self._text, font)[1]
        padding = ' '
        while draw.textsize(padding, font)[0] < self._embed_size_ratio * height_px:
            padding = padding + ' '
        return padding


# returns length of string starting from start that fits in
# the width of the box
def _find_next_fit_length(
    text: str,
    start: int,
    font: ImageFont.FreeTypeFont,
    width_px: int
) -> int:
    newline = text[start:].find('\n')
    end = start + newline if newline != -1 else len(text) - 1

    # no newlines at this point
    while end > start \
            and font.getlength(text[start:end + 1]) > width_px:

        # scan from right for the next word
        # first skip any whitespaces
        char_seen = False
        while end > start:
            if text[end].isspace():
                if char_seen:
                    break
            else:
                char_seen = True

            end = end - 1

    return end - start + 1


def _get_v_offset(
    v_alignment: Optional[VerticalTextAlignment],
    text_bbox: tuple[int, int, int, int],
    text_placement: Placement,
) -> int:
    if v_alignment == VerticalTextAlignment.MIDDLE:
        v_offset = int((text_placement.h - text_bbox[3]) / 2)
    elif v_alignment == VerticalTextAlignment.BOTTOM:
        v_offset = int(text_placement.h - text_bbox[3])
    else:
        v_offset = 0
    return v_offset


def _get_default_font_file() -> str:
    if sys.platform.startswith('win32'):
        drive = pathlib.Path.home().drive + '\\\\'
        return os.path.join(drive, 'Windows\\Fonts\\', _DEFAULT_FONT_WINDOWS)
    elif sys.platform.startswith('darwin'):
        drive = pathlib.Path.home().drive + '//'
        return os.path.join(drive, 'System/Library/Fonts/', _DEFAULT_FONT_MACOS)
