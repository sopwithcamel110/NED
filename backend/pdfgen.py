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
SCRIPT_SIZE_FONT = 0.7 # super/subscript font size
Y_SCRIPT = 1 - SCRIPT_SIZE_FONT


pdfmetrics.registerFont(TTFont('Bullet-Font', 'fonts/NotoSans-Regular.ttf'))
pdfmetrics.registerFont(TTFont('Topic-Font', 'fonts/NotoSans-Bold.ttf'))

ContentType = Dict[str, Any]

class MediaType(Enum):
    TEXT = "text"
    IMAGE = "image"

PATTERN = re.compile(r"([^\^_]+)|(\^)\{([^\}]+)\}|(_)\{([^\}]+)\}")

def parse_style(input_list: List[str]) -> List[List[Tuple[str, str]]]:
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

def render_parsed_text(c, x, y, parsed_text, font, font_size):
    """
    Render parsed text with LaTeX-style superscripts and subscripts on a ReportLab canvas.
    """
    for text, style in parsed_text:
        if style == "normal":
            c.setFont(font, font_size)
            c.drawString(x, y, text)
            x += styleStringWidth(c, text, font, font_size)
        elif style == "superscript":
            c.setFont(font, font_size * SCRIPT_SIZE_FONT)  # Smaller font for superscript
            c.drawString(x, y + font_size * Y_SCRIPT, text)  # Raise superscript
            x += styleStringWidth(c, text, font, font_size * SCRIPT_SIZE_FONT)
        elif style == "subscript":
            c.setFont(font, font_size * SCRIPT_SIZE_FONT)  # Smaller font for subscript
            c.drawString(x, y - font_size * Y_SCRIPT, text)  # Lower subscript
            x += styleStringWidth(c, text, font, font_size * SCRIPT_SIZE_FONT)

def styleStringWidth(c:canvas.Canvas, parsed_text: List[str], font: str, font_size: int) -> int:
    """
    wrapper for stringWidth function taking into account superscripts and subscript dimension changes.
    """
    width = 0
    for text, style in parsed_text:
        if style == "normal":
            font_size = base_font_size
        elif style in ["superscript", "subscript"]:
            font_size = base_font_size * SCRIPT_SIZE_FONT  # Adjusted font size for superscripts and subscripts
        else:
            continue  # Skip unsupported styles (shouldn't occur with proper input)

        # Add the width of the current segment
        width += c.stringWidth(text, font, font_size)

    return width


def wrap_string_list(c: canvas.Canvas, font: str, font_size: int, strs: List[str]) -> List[str]:
    """Word-wrap strs to maximize space efficiency, and return the word-wrapped list."""
    if not strs:
        return []

    min_size = float('inf')
    min_res = []
    
    max_str_len = int(max(styleStringWidth(c, s, font, font_size) for s in strs))

    for width in range(max_str_len//2, max_str_len+1):
        res = []
        for s in strs:
            res.extend(wordwrap.wrap(s, c, font, font_size, width))

        size = max(styleStringWidth(c, s, font, font_size) for s in res) * len(res)
        if size < min_size:
            min_size = size
            min_res = res
    #print(min_res)
    return min_res

def get_dimensions(c: canvas.Canvas, content: ContentType, font_size: int) -> Tuple[float, float]:
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
            topic = content['topic']
            bullet_points = wrap_string_list(c, 'Bullet-Font', font_size, content['content'])
            content['wrapped_content'] = bullet_points # Update content for future use
            content['parsed_content'] = parse_style(s for s in content['wrapped_content'])
            #print(content['wrapped_content'])
            print(content['parsed_content']) # use for debugging

            topic_width = max([c.stringWidth(topic, "Topic-Font", font_size)] + [styleStringWidth(c, s, "Bullet-Font", font_size) for s in content['parsed_content']]) 
            topic_height = font_size * (len(bullet_points)+1) # +1 for topic
            return topic_width, topic_height
        case MediaType.IMAGE:
            #content width, content height
            img = Image.open(content['content'][0]) 
  
            # get width and height 
            image_width = img.width 
            image_height = img.height
            scale_factor = max(image_height, image_height) / (2*inch)
            image_height /= scale_factor
            image_width /= scale_factor

            content['content'][1] = image_width
            content['content'][2] = image_height
            return image_width, image_height

def place_content(
    c: canvas.Canvas,
    content: ContentType,
    x: float,
    y: float,
    font_size: int,
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
            topic = content['topic']
            #bullet_points = content['wrapped_content']
            bullet_points = content['parsed_content']

            y -= font_size
            # Draw the topic in bold
            c.setFont("Topic-Font", font_size)
            c.drawString(x, y, topic)

            c.setFont("Bullet-Font", font_size)  # Smaller font size to fit more text
            for i, bullet in enumerate(bullet_points):
                # Draw bullet point
                render_parsed_text(c, x, y-((i+1)*font_size), bullet, "Bullet-Font", font_size)
                #c.drawString(x, y-((i+1)*font_size), bullet)

        case MediaType.IMAGE:
            image_path = content['content'][0]
            image_width = content['content'][1]
            image_height = content['content'][2]
            c.drawImage(image_path, x, y - image_height, width=image_width, height=image_height)

def create_pdf(data_dict: List[ContentType]) -> None:
    """
    Create a fully optimized cheatsheet from a list of topics. Utilizes formatting and
    positioning to make efficient use of white space.
    """
    pdf_buffer = io.BytesIO()
    c = canvas.Canvas(pdf_buffer, pagesize=A4)
    page_width, page_height = A4
    font_size = 5
    
    packer = newPacker(mode=PackingMode.Online, rotation=False)

    print("Creating cheatsheet...")
    # Add infinite A4 bins
    packer.add_bin(float2dec(page_width, DEC_PRECISION), float2dec(page_height, DEC_PRECISION), count=float('inf'))

    # Add topics to rectpack
    for i, content in enumerate(data_dict):
        w, h = get_dimensions(c, content, font_size)
        packer.add_rect(float2dec(w, DEC_PRECISION), float2dec(h, DEC_PRECISION), i)

    # Display rectpacked topics on PDF
    for abin in packer:
        for rect in abin:
            x = float(rect.x)
            y = page_height-float(rect.y) # rectpack uses bottom-left origin, adjust for reportlab
            w = float(rect.width)
            h = float(rect.height)
            rid = rect.rid
            
            content = data_dict[rid]
            place_content(c, content, x, y, font_size)

        # Create new blank page
        c.showPage()
    # print(packer.rect_list())
    # Save the PDF
    c.save()

    pdf_buffer.seek(0)
    return pdf_buffer

def create_cheatsheet_pdf(data_dict: List[ContentType]) -> str:
    """
    Create a cheatsheet on the filesystem from the given list of topics. Returns the path of the created cheatsheet.
    """
    return create_pdf(data_dict)

if __name__ == "__main__":
    data_dict = []
    images = [
        {
            "topic": "Images",
            "content": [
                "example/dag.png", 4, 2
            ],
            "media": "image"
        },
        {
            "topic": "Images",
            "content": [
                "example/graph.png", 4, 2
            ],
            "media": "image"
        },
        {
            "topic": "Images",
            "content": [
                "example/proof.png", 4, 2
            ],
            "media": "image"
        },
        {
            "topic": "Images",
            "content": [
                "example/rules.png", 4, 2
            ],
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
        data_dict.insert(3 + 2*i, v)

    with open("cheatsheet.pdf", "wb") as f:
        f.write(create_pdf(data_dict).read())
