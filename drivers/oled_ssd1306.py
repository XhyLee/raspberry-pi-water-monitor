from __future__ import annotations

from pathlib import Path
from typing import Iterable

from PIL import Image, ImageDraw, ImageFont
from smbus2 import SMBus


class SSD1306OLED:
    def __init__(
        self,
        bus_id: int,
        address: int = 0x3C,
        width: int = 128,
        height: int = 64,
        font_candidates: list[str] | None = None,
        font_size: int = 12,
        line_height: int = 16,
    ) -> None:
        self.address = address
        self.width = width
        self.height = height
        self.pages = height // 8
        self.line_height = line_height
        self._bus = SMBus(bus_id)
        self._font = self._load_font(font_candidates or [], font_size)

    def init(self) -> None:
        for command in (
            0xAE,
            0xD5,
            0x80,
            0xA8,
            0x3F,
            0xD3,
            0x00,
            0x40,
            0xA1,
            0xC8,
            0xDA,
            0x12,
            0x81,
            0xCF,
            0xD9,
            0xF1,
            0xDB,
            0x30,
            0xA4,
            0xA6,
            0x8D,
            0x14,
            0xAF,
        ):
            self.write_command(command)
        self.clear()

    def clear(self) -> None:
        self.display_image(Image.new("1", (self.width, self.height), 0))

    def show_lines(self, lines: Iterable[str]) -> None:
        image = Image.new("1", (self.width, self.height), 0)
        draw = ImageDraw.Draw(image)

        for index, line in enumerate(lines):
            draw.text((0, index * self.line_height), line, font=self._font, fill=255)

        self.display_image(image)

    def display_image(self, image: Image.Image) -> None:
        if image.size != (self.width, self.height):
            image = image.resize((self.width, self.height))

        pixels = image.load()
        for page in range(self.pages):
            self.write_command(0xB0 | page)
            self.write_command(0x10)
            self.write_command(0x00)

            row_bytes = []
            for x in range(self.width):
                value = 0
                for bit in range(8):
                    if pixels[x, page * 8 + bit]:
                        value |= 1 << bit
                row_bytes.append(value)

            for start in range(0, len(row_bytes), 16):
                self.write_data(row_bytes[start : start + 16])

    def write_command(self, command: int) -> None:
        self._bus.write_byte_data(self.address, 0x00, command)

    def write_data(self, payload: list[int]) -> None:
        self._bus.write_i2c_block_data(self.address, 0x40, payload)

    def power_off(self) -> None:
        self.write_command(0xAE)

    def close(self) -> None:
        self._bus.close()

    def _load_font(self, font_candidates: list[str], font_size: int) -> ImageFont.ImageFont:
        for font_path in font_candidates:
            candidate = Path(font_path)
            if candidate.exists():
                try:
                    return ImageFont.truetype(str(candidate), font_size)
                except OSError:
                    continue
        return ImageFont.load_default()
