from enum import Enum
from io import BufferedWriter
import io
import os
import random
import tempfile
import re

from PIL import Image
from typing import Any, Dict, List, Tuple

from rectpack import float2dec, newPacker, PackingMode
from reportlab.platypus import SimpleDocTemplate, Spacer
from reportlab.lib.units import inch
from reportlab.lib.pagesizes import A4
from reportlab.pdfgen import canvas
from reportlab.pdfbase.ttfonts import TTFont
from reportlab.pdfbase import pdfmetrics

import wordwrap

DEC_PRECISION = 6
SCRIPT_SIZE_FONT = 0.7  # super/subscript font size
Y_SCRIPT = 1 - SCRIPT_SIZE_FONT

# Register fonts
pdfmetrics.registerFont(TTFont('Bullet-Font', 'fonts/NotoSans-Regular.ttf'))
pdfmetrics.registerFont(TTFont('Topic-Font', 'fonts/NotoSans-Bold.ttf'))


class StyleType(Enum):
    """Text styling types"""
    NORMAL = "normal"
    SUPERSCRIPT = "superscript"
    SUBSCRIPT = "subscript"


class MediaType(Enum):
    """Supported topic media types"""
    TEXT = "text"
    IMAGE = "image"


Topic = Dict[str, Any]
StyledString = List[Tuple[str, StyleType]]

PATTERN = re.compile(r"([^\^_]+)|(\^)\{([^\}]+)\}|(_)\{([^\}]+)\}")


class CheatsheetGenerator:
    """
    Tool for creating fully whitespace optimized cheatsheets using notes.
    """

    def __init__(
        self,
        topics: List[Topic],
        dimensions: Tuple[float, float] = A4,
        font_size: int = 5,
    ):
        self.topics = topics
        self.width, self.height = dimensions
        self.font_size = font_size

        self._pdf_buffer = io.BytesIO()
        self._canvas = canvas.Canvas(self._pdf_buffer, pagesize=A4)

    def _parse_style(input_list: List[str]) -> List[List[Tuple[str, str]]]:
        """
        Parse a string for superscripts (^{}) and subscripts (_{}).
        Returns a list of lists of tuples (text, style), where style can be 'normal', 'superscript', or 'subscript'.
        """
        results = []

        for s in input_list:
            parts = []
            matches = PATTERN.finditer(s)

            for match in matches:
                if match.group(1):  # Normal text
                    parts.append((match.group(1), "normal"))
                elif match.group(2):  # Superscript
                    parts.append((match.group(3), "superscript"))
                elif match.group(4):  # Subscript
                    parts.append((match.group(5), "subscript"))

            results.append(parts)

        return results

    def _render_parsed_text(self, x, y, parsed_text):
        """
        Render parsed text with LaTeX-style superscripts and subscripts on a ReportLab canvas.
        """
        for text, style in parsed_text:
            if style == "normal":
                c.setFont(font, font_size)
                c.drawString(x, y, text)
                x += self._styleStringWidth(c, text, font, font_size)
            elif style == "superscript":
                c.setFont(font, font_size *
                          SCRIPT_SIZE_FONT)  # Smaller font for superscript
                c.drawString(x, y + font_size * Y_SCRIPT,
                             text)  # Raise superscript
                x += self._styleStringWidth(text)
            elif style == "subscript":
                self._canvas.setFont(
                    self.font, self.font_size *
                    SCRIPT_SIZE_FONT)  # Smaller font for subscript
                self._canvas.drawString(x, y - self.font_size * Y_SCRIPT,
                                        text)  # Lower subscript
                x += self._styleStringWidth(text)

    def _styleStringWidth(self, parsed_text: List[str]) -> int:
        """
        wrapper for stringWidth function taking into account superscripts and subscript dimension changes.
        """
        width = 0
        for text, style in parsed_text:
            if style == "normal":
                font_size = self.font_size
            elif style in ["superscript", "subscript"]:
                font_size = self.font_size * SCRIPT_SIZE_FONT  # Adjusted font size for superscripts and subscripts
            else:
                continue  # Skip unsupported styles (shouldn't occur with proper input)

            # Add the width of the current segment
            width += self._canvas.stringWidth(text, 'Bullet-Font', font_size)

        return width

    def _wrap_string_list(self, content: Topic) -> None:
        """Word-wrap topic to maximize space efficiency."""
        min_size = float('inf')

        raw_topic = content['topic']
        content['topic'] = [raw_topic]
        raw_content = content['content']

        max_str_len = max(
                self._canvas.stringWidth(raw_topic, 'Topic-Font', self.font_size),
                max(
                    (self._canvas.stringWidth(s, 'Bullet-Font', self.font_size)
                    for s in raw_content), default=float('-inf')))
        
        max_str_len = int(min(max_str_len, self.width))
        content['width'] = max_str_len

        for width in range(max_str_len // 2, max_str_len + 1):
            topic = wordwrap.wrap(raw_topic, self._canvas, 'Topic-Font',
                                  self.font_size, width)
            bullets = []
            for s in raw_content:
                bullets.extend(wordwrap.wrap(s, self._canvas, 'Bullet-Font', self.font_size,
                              width))

            max_width = max([
                self._canvas.stringWidth(s, 'Bullet-Font', self.font_size)
                for s in bullets
            ] + [
                self._canvas.stringWidth(s, 'Topic-Font', self.font_size)
                for s in topic
            ])
            size = max_width * (len(bullets) + len(topic))
            if size < min_size:
                min_size = size
                content['topic'] = topic
                content['content'] = bullets
                content['width'] = max_width

    def _get_dimensions(self, content: Topic) -> Tuple[float, float]:
        """
        Calculate the width and height of the given content, considering text wrapping.
        Parameters:
        - c: The ReportLab canvas object.
        - content: The content dictionary containing topic, content, and media type.
        - font_size: Font size for text.
        - max_width: Maximum width of the text content before wrapping.
        Returns:
        - A tuple containing:
            - The maximum width of the content.
            - The total height of the content.
        """
        match MediaType(content['media']):
            case MediaType.TEXT:
                self._wrap_string_list(content)
                topic_height = self.font_size * (len(content['topic']) +
                                                 len(content['content']))

                return content['width'], topic_height
            case MediaType.IMAGE:
                #content width, content height
                img = Image.open(content['content'][0])

                # get width and height
                image_width = img.width
                image_height = img.height
                scale_factor = max(image_height, image_height) / (2 * inch)
                image_height /= scale_factor
                image_width /= scale_factor

                content['content'][1] = image_width
                content['content'][2] = image_height
                return image_width, image_height

    def _place_content(
        self,
        content: Topic,
        x: float,
        y: float,
    ) -> None:
        """
        Place content directly at x and y on the given canvas.
        Parameters:
        - c: The ReportLab canvas object.
        - content: The content dictionary containing topic, content, and media type.
        - x: X-coordinate to start drawing.
        - y: Y-coordinate to start drawing.
        - font_size: Font size for text.
        """
        match MediaType(content['media']):
            case MediaType.TEXT:
                y -= self.font_size

                i = 0

                self._canvas.setFont("Topic-Font", self.font_size)
                for s in content['topic']:
                    self._canvas.drawString(x, y - ((i + 1) * self.font_size),
                                            s)
                    i += 1

                self._canvas.setFont("Bullet-Font", self.font_size)
                for s in content['content']:
                    self._canvas.drawString(x, y - ((i + 1) * self.font_size),
                                            s)
                    i += 1

            case MediaType.IMAGE:
                image_path = content['content'][0]
                image_width = content['content'][1]
                image_height = content['content'][2]
                self._canvas.drawImage(image_path,
                                       x,
                                       y - image_height,
                                       width=image_width,
                                       height=image_height)

    def create_pdf(self) -> io.BytesIO:
        """
        Create a fully optimized cheatsheet from a list of topics. Utilizes formatting and
        positioning to make efficient use of white space.
        """
        print("Creating cheatsheet...")

        packer = newPacker(mode=PackingMode.Online, rotation=False)

        # Add infinite A4 bins
        packer.add_bin(float2dec(self.width, DEC_PRECISION),
                       float2dec(self.height, DEC_PRECISION),
                       count=float('inf'))

        # Pack topics
        for i, content in enumerate(self.topics):
            w, h = self._get_dimensions(content)
            packer.add_rect(float2dec(w, DEC_PRECISION),
                            float2dec(h, DEC_PRECISION), i)

        # Display rectpacked topics on PDF
        for abin in packer:
            for rect in abin:
                x = float(rect.x)
                y = self.height - float(
                    rect.y
                )  # rectpack uses bottom-left origin, adjust for reportlab
                w = float(rect.width)
                h = float(rect.height)
                rid = rect.rid

                content = data_dict[rid]
                self._place_content(content, x, y)

            # Create new blank page
            self._canvas.showPage()

        # Save the PDF
        self._canvas.save()

        self._pdf_buffer.seek(0)
        return self._pdf_buffer


if __name__ == "__main__":
    data_dict = []
    images = [
        {
            "topic": "Images",
            "content": ["example/dag.png", 4, 2],
            "media": "image"
        },
        {
            "topic": "Images",
            "content": ["example/graph.png", 4, 2],
            "media": "image"
        },
        {
            "topic": "Images",
            "content": ["example/proof.png", 4, 2],
            "media": "image"
        },
        {
            "topic": "Images",
            "content": ["example/rules.png", 4, 2],
            "media": "image"
        },
    ]
    with open('example/neil_cheatsheet.txt', 'r', encoding='utf-8') as f:
        data = {'media': 'text', 'content': []}
        for line in f.readlines():
            if not line.strip():
                data_dict.append(data)
                data = {'media': 'text', 'content': []}
            elif 'topic' not in data:
                data['topic'] = line
            else:
                data['content'].append(line)

    for i, v in enumerate(images):
        data_dict.insert(3 + 2 * i, v)

    gen = CheatsheetGenerator(data_dict)
    with open("cheatsheet.pdf", "wb") as f:
        f.write(gen.create_pdf().read())
