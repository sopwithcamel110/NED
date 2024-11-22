from enum import Enum
from io import BufferedWriter
import os
import random
import tempfile

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
from mathsymbols import *

pdfmetrics.registerFont(TTFont('Bullet-Font', 'fonts/NotoSans-Regular.ttf'))
pdfmetrics.registerFont(TTFont('Topic-Font', 'fonts/NotoSans-Bold.ttf'))

ContentType = Dict[str, Any]
DEC_PRECISION = 6

class MediaType(Enum):
    TEXT = "text"
    IMAGE = "image"

def wrap_string_list(c: canvas.Canvas, font: str, font_size: int, strs: List[str]) -> List[str]:
    """Word-wrap strs to maximize space efficiency, and return the word-wrapped list."""
    if not strs:
        return []

    min_size = float('inf')
    min_res = []

    parsed_text = parse_style(strs)
    
    max_str_len = int(max(styleStringWidth(c, parsed_text, font, font_size)))

    for width in range(max_str_len//2, max_str_len+1):
        res = []
        for s in parsed_text:
            res.extend(wordwrap.wrap(s, c, font, font_size, width))
        #print(res)
        size = max(styleStringWidth(c, s, font, font_size) for s in res) * len(res) 
        if size < min_size:
            min_size = size
            min_res = res

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
            #print(content['content'])
            bullet_points = wrap_string_list(c, 'Bullet-Font', font_size, content['content'])
            content['wrapped_content'] = bullet_points # Update content for future use
            content['parsed_content'] = parse_style(content['wrapped_content'])
            #print(content['wrapped_content'])
            #print(content['parsed_content']) # use for debugging

            topic_width = max([c.styleStringWidth(topic, "Topic-Font", font_size)] + [c.styleStringWidth(content['parsed_content'], "Bullet-Font", font_size)]) 
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
                render_parsed_text(c, x, y-((i+1)*font_size), bullet, "Bullet-Font", font_size)


        case MediaType.IMAGE:
            image_path = content['content'][0]
            image_width = content['content'][1]
            image_height = content['content'][2]
            c.drawImage(image_path, x, y - image_height, width=image_width, height=image_height)

def create_pdf(data_dict: List[ContentType], file: BufferedWriter) -> None:
    """
    Create a fully optimized cheatsheet from a list of topics. Utilizes formatting and
    positioning to make efficient use of white space.
    """
    c = canvas.Canvas(file, pagesize=A4)
    page_width, page_height = A4
    font_size = 5
    
    packer = newPacker(mode=PackingMode.Online, rotation=False)

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
    
    # Save the PDF
    c.save()

def create_cheatsheet_pdf(data_dict: List[ContentType]) -> str:
    """
    Create a cheatsheet on the filesystem from the given list of topics. Returns the path of the created cheatsheet.
    """
    temp_dir = tempfile.mkdtemp()
    file_path = os.path.join(temp_dir, 'cheatsheet.pdf')

    # Create a file in the temp directory
    with open(file_path, 'wb') as temp_file:
        create_pdf(data_dict, temp_file)

    return file_path

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
with open('./example/neil_cheatsheet.txt', 'r', encoding='utf-8') as f:
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

create_pdf(data_dict, "test.pdf")