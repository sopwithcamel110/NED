from enum import Enum
from io import BufferedWriter
import io
import os
import random
import tempfile
import unicodedata
import re
import fitz
import copy

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
SCRIPT_FONT_SIZE = 0.7  # super/subscript font size
Y_SCRIPT = 1 - SCRIPT_FONT_SIZE

DEFAULT_MAX_PAGE = 2

DEFAULT_FONT_SIZE = 11
MIN_FONT_SIZE = 5 # can change? 
REDUCE_MULT = 0.15 # multiplier to reduce font size
ROUND_VAL = 1 # rounding to nth place

# Register fonts
pdfmetrics.registerFont(TTFont('Bullet-Font', 'fonts/NotoSans-Regular.ttf'))
pdfmetrics.registerFont(TTFont('Topic-Font', 'fonts/NotoSans-Bold.ttf'))


class StyleType(Enum):
    """Text styling types"""
    NORMAL = "normal"
    SUPERSCRIPT = "superscript"
    SUBSCRIPT = "subscript"
    COMBINED = "combined"


class MediaType(Enum):
    """Supported topic media types"""
    TEXT = "text"
    IMAGE = "image"


Topic = Dict[str, Any]
StyledString = List[Tuple[str, StyleType]]

PATTERN = re.compile(
    r"([^\^_]+)"  # Normal text
    r"|(\^)\{([^\}]+)\}"  # Superscripts
    r"|(_)\{([^\}]+)\}"  # Subscripts
    r"|([^\^_]+)_\{([^\}]+)\}\^\{([^\}]+)\}"  # Combined subscript and superscript
)


class CheatsheetGenerator:
    """
    Tool for creating fully whitespace optimized cheatsheets using notes.
    """

    def __init__(
        self,
        topics: List[Topic],
        dimensions: Tuple[float, float] = A4,
        max_page: int = DEFAULT_MAX_PAGE #
    ):
        self.topics = topics
        self.original_topics = copy.deepcopy(topics) # saved information in case of reseting
        self.width, self.height = dimensions
        self.font_size = DEFAULT_FONT_SIZE
        self.max_page = max_page
        self.min_font_size = MIN_FONT_SIZE
        self._pdf_buffer = io.BytesIO()
        self._canvas = canvas.Canvas(self._pdf_buffer, pagesize=A4)

    def _render_parsed_text(self, x, y, parsed_text, font):
        """
        Render parsed text with LaTeX-style superscripts, subscripts, and combinations
        on a ReportLab canvas.
        """
        for item in parsed_text:
            if isinstance(item, tuple) and len(item) == 2:
                text, style = item
                if style == StyleType.NORMAL:
                    self._canvas.setFont(font, self.font_size)
                    self._canvas.drawString(x, y, text)
                    x += self._canvas.stringWidth(text, font, self.font_size)
                elif style == StyleType.SUPERSCRIPT:
                    self._canvas.setFont(font,
                                         self.font_size * SCRIPT_FONT_SIZE)
                    self._canvas.drawString(x, y + self.font_size * Y_SCRIPT,
                                            text)
                    x += self._canvas.stringWidth(
                        text, font, self.font_size * SCRIPT_FONT_SIZE)
                elif style == StyleType.SUBSCRIPT:
                    self._canvas.setFont(font,
                                         self.font_size * SCRIPT_FONT_SIZE)
                    self._canvas.drawString(x, y - self.font_size * Y_SCRIPT,
                                            text)
                    x += self._canvas.stringWidth(
                        text, font, self.font_size * SCRIPT_FONT_SIZE)

            elif isinstance(item, tuple) and len(item) == 4:  #combined
                base, _, subscript, superscript = item
                # Render base character
                self._canvas.setFont(font, self.font_size)
                self._canvas.drawString(x, y, base)
                base_width = self._canvas.stringWidth(base, font,
                                                      self.font_size)
                x += base_width

                # Render subscript
                self._canvas.setFont(font, self.font_size * SCRIPT_FONT_SIZE)
                subscript_width = self._canvas.stringWidth(
                    subscript, font, self.font_size * SCRIPT_FONT_SIZE)
                self._canvas.drawString(x, y - self.font_size * Y_SCRIPT,
                                        subscript)

                # Render superscript
                self._canvas.setFont(font, self.font_size * SCRIPT_FONT_SIZE)
                self._canvas.drawString(x + subscript_width,
                                        y + self.font_size * Y_SCRIPT,
                                        superscript)
                x += subscript_width + self._canvas.stringWidth(
                    superscript, font, self.font_size * SCRIPT_FONT_SIZE)

        return x

    def _reset_canvas_and_buffer(self):
        """Resets the canvas and buffer for PDF regeneration."""
        self._pdf_buffer = io.BytesIO()
        self._canvas = canvas.Canvas(self._pdf_buffer, pagesize=A4)

    def _lower_font(self, packer) -> float:
        """Lowers font size depending on how many topics are over page limit"""
        _topics = 0
        for i in range(self.max_page, len(packer)):
            _topics += len(packer[i])
        
        self.font_size = round(self.font_size - 
                                round(_topics * REDUCE_MULT, ROUND_VAL), 
                                ROUND_VAL)

    @staticmethod
    def _parse_style(content: Topic) -> None:
        """
        Parse a string for superscripts (^{}) and subscripts (_{}).
        Edits content['content'] to a list of lists of tuples (text, style), where style can be 'normal', 'superscript', or 'subscript'.
        This function MUST be called before any string width-reading, or else the width will be inaccurate.
        """

        def _parse_str_style(text: str) -> StyledString:
            results = []
            matches = PATTERN.finditer(text)

            for match in matches:
                if match.group(1):  # Normal text
                    results.append((match.group(1), StyleType.NORMAL))
                elif match.group(2):  # Superscript
                    results.append((match.group(3), StyleType.SUPERSCRIPT))
                elif match.group(4):  # Subscript
                    results.append((match.group(5), StyleType.SUBSCRIPT))
                elif match.group(6):  # Combined subscript and superscript
                    results.append((match.group(6), StyleType.COMBINED,
                                    match.group(7), match.group(8)))
            return results

        content['topic'] = [_parse_str_style(content['topic'])]
        content['content'] = [_parse_str_style(s) for s in content['content']]

    def _styleStringWidth(self, text: StyledString, font: str) -> int:
        """
        Wrapper for stringWidth function that accounts for superscripts and subscript dimension changes.
        """
        width = 0

        for content, style in text:  # Iterate through tuples in the sublist
            if style == StyleType.NORMAL:
                current_font_size = self.font_size
            else:
                current_font_size = self.font_size * SCRIPT_FONT_SIZE

            # Add the width of the current text with the current font size
            width += self._canvas.stringWidth(content, font, current_font_size)

        return width

    def _wrap_string_list(self, content: Topic) -> None:
        """Word-wrap topic to maximize space efficiency."""

        def fake_wrap(text: StyledString, font: str, width: int):
            """
            Wrap the stringified version of the styled string `text`. Then, reconstruct the 
            styled string using the lengths of the wrapped result. The "fake" aspect
            of this function comes from not taking into account the width differences of
            "xy" and "x^y" when choosing where to wrap. This does not cause functional issues, 
            since we are overcompensating.
            """
            wrapped = wordwrap.wrap(''.join(p[0] for p in text), self._canvas,
                                    font, self.font_size, width, break_long_words=False)

            res = []
            i = 0
            c = 0
            curSeg, curStyle = text[i]
            for w in wrapped:
                styled_str = []
                curStr = ''
                for wc in w:
                    curStr += wc
                    c += 1
                    if c >= len(curSeg):
                        styled_str.append((curStr, curStyle))
                        curStr = ''
                        i += 1
                        c = 0
                        if i < len(text):
                            curSeg, curStyle = text[i]
                if curStr:
                    styled_str.append((curStr, curStyle))
                res.append(styled_str)

            return res

        min_size = float('inf')

        raw_topic = content['topic'][0]
        raw_content = content['content']
        

        max_str_len = max(
            self._styleStringWidth(raw_topic, 'Topic-Font'),
            max((self._styleStringWidth(s, 'Bullet-Font')
                 for s in raw_content),
                default=float('-inf')))

        max_str_len = int(min(max_str_len, self.width))
        content['width'] = max_str_len

        for width in range(max_str_len // 2, max_str_len + 1):
            topic = fake_wrap(raw_topic, 'Topic-Font', width)
            bullets = []
            for s in raw_content:
                bullets.extend(fake_wrap(s, 'Bullet-Font', width))

            max_width = max(
                [self._styleStringWidth(s, 'Bullet-Font') for s in bullets] +
                [self._styleStringWidth(s, 'Topic-Font') for s in topic])
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
        media = MediaType(content['media'])
        if media == MediaType.TEXT:
            topic_height = self.font_size * (len(content['topic']) +
                                             len(content['content']))

            return content['width'], topic_height
        elif media == MediaType.IMAGE:
            return content['content'][1], content['content'][2]

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
                i = 0
                for s in content['topic']:
                    self._render_parsed_text(x, y - ((i + 1) * self.font_size),
                                             s, 'Topic-Font')
                    i += 1

                for s in content['content']:
                    self._render_parsed_text(x, y - ((i + 1) * self.font_size),
                                             s, 'Bullet-Font')
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

    def _preprocess_data(self) -> None:
        """Perform necessary preprocessing on the inputted data"""
        for content in self.topics:
            media = MediaType(content['media'])
            if media == MediaType.TEXT:
                # Normalize unicode
                content['topic'] = unicodedata.normalize(
                    'NFKD', content['topic'])
                normalized = []
                for bullet in content['content']:
                    normalized.append(
                        unicodedata.normalize('NFKC', bullet).strip())
                content['content'] = normalized

                # Convert strs to StyledStrs
                self._parse_style(content)

                # Wrap lines
                self._wrap_string_list(content)
            elif media == MediaType.IMAGE:
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

    def create_pdf(self) -> io.BytesIO:
        """
        Create a fully optimized cheatsheet from a list of topics. If the PDF exceeds the maximum
        allowed pages, it will regenerate the PDF using smaller fonts until it fits.

        :return: io.BytesIO buffer containing the generated PDF.
        """

        while self.font_size >= self.min_font_size:
            try:
                print(f"Creating cheatsheet with font size {self.font_size}...")
                self.topics = copy.deepcopy(self.original_topics)
                
                # Reset the canvas and buffer
                self._reset_canvas_and_buffer()

                # Preprocess topics for packing
                self._preprocess_data()

                # Initialize the packer
                packer = newPacker(mode=PackingMode.Online, rotation=False)

                # Add infinite A4 bins
                packer.add_bin(float2dec(self.width, DEC_PRECISION),
                            float2dec(self.height, DEC_PRECISION),
                            count=float('inf'))

                # Pack topics into the bins
                for i, content in enumerate(self.topics):
                    w, h = self._get_dimensions(content)
                    packer.add_rect(float2dec(w, DEC_PRECISION),
                                    float2dec(h, DEC_PRECISION), i)

                # Generate the PDF
                for abin in packer:
                    for rect in abin:
                        x = float(rect.x)
                        y = self.height - float(rect.y)  # Adjust for bottom-left origin
                        w = float(rect.width)
                        h = float(rect.height)
                        rid = rect.rid

                        content = self.topics[rid]
                        self._place_content(content, x, y)

                    # Add a new blank page for the next bin
                    self._canvas.showPage()

                # Ensure all topics are packed
                assert len(packer.rect_list()) == len(self.topics)

                # Save the PDF to the buffer
                self._canvas.save()
                self._pdf_buffer.seek(0)

                # Check the page count
                if self.max_page >= len(packer):
                    print("PDF created successfully within page limit.")
                    return self._pdf_buffer

                # Reduce the font size if the page count exceeds the limit
                print("PDF exceeds the page limit. Reducing font size...")
                self._lower_font(packer)

            except Exception as e:
                print(f"Error during PDF creation: {e}")
                raise

        raise ValueError("Unable to create a PDF within the page limit using the available font sizes.")
        return self._pdf_buffer # return whatever works with some error message for user


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
