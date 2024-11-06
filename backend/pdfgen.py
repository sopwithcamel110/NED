from enum import Enum
from io import BufferedWriter
import os
import random
import tempfile
from typing import Any, Dict, List, Tuple

from reportlab.platypus import SimpleDocTemplate, Image, Spacer
from reportlab.lib.units import inch
from reportlab.lib.pagesizes import A4
from reportlab.pdfgen import canvas
from reportlab.pdfbase.ttfonts import TTFont
from reportlab.pdfbase import pdfmetrics

pdfmetrics.registerFont(TTFont('Bullet-Font', 'fonts/Notosans-Regular.ttf'))
pdfmetrics.registerFont(TTFont('Topic-Font', 'fonts/NotoSans-Bold.ttf'))

ContentType = Dict[str, Any]

class MediaType(Enum):
    TEXT = "text"
    IMAGE = "image"

def get_dimensions(c, content: ContentType, font_size: int) -> Tuple[float, float]:
    """Calculate the width and height of the given content."""
    match MediaType(content['media']):
        case MediaType.TEXT:
            topic = content['topic']
            bullet_points = content['content']
            topic_width = max(c.stringWidth(s, "Topic-Font", font_size) for s in [topic] + bullet_points) 
            topic_height = len(bullet_points)+1 # +1 for topic
            return topic_width, topic_height
        case MediaType.IMAGE:
            #content width, content height
            return content['content'][1] * inch, (content['content'][2] * inch) // 5

def place_content(c: canvas.Canvas, content: ContentType, x: float, y: float, font_size: int) -> None:
    """Place content directly at x and y on the given canvas."""
    match MediaType(content['media']):
        case MediaType.TEXT:
            topic = content['topic']
            bullet_points = content['content']

            # Draw the topic in bold
            c.setFont("Topic-Font", font_size)
            c.drawString(x, y, topic)

            c.setFont("Bullet-Font", font_size)  # Smaller font size to fit more text
            for i, bullet in enumerate(bullet_points):
                # Draw bullet point
                c.drawString(x, y-((i+1)*font_size), f'• {bullet}')

        case MediaType.IMAGE:
            image_path = content['content'][0]
            image_width = content['content'][1] * inch 
            image_height = content['content'][2] * inch
            c.drawImage(image_path, x, y - image_height, width=image_width, height=image_height)

def create_pdf(data_dict: List[ContentType], file: BufferedWriter) -> None:
    """
    Create a fully optimized cheatsheet from a list of topics. Utilizes formatting and
    positioning to make efficient use of white space.
    """
    c = canvas.Canvas(file, pagesize=A4)
    page_width, page_height = A4
    font_size = 5
    
    top_margin = font_size
    current_x = 0
    current_y = page_height-top_margin

    total_height = 0
    msf_height = 0 # max-so-far height
    for content in data_dict:
        topic_width, topic_height = get_dimensions(c, content, font_size)

        if current_x + topic_width > page_width:
            # Topic goes off right of page, go to next line
            current_x = 0
            total_height += msf_height
            msf_height = 0
            current_y = page_height-(total_height*font_size)-top_margin  # Move down to the next line
        elif current_y - (topic_height*font_size) <= 0:
            # Topic goes off bottom of page, create a new one
            c.showPage()
            total_height = msf_height = 0
            current_x = 0
            current_y = page_height-top_margin 

        msf_height = max(msf_height, topic_height)

        place_content(c, content, current_x, current_y, font_size)

        # Check for page overflow
        current_x += topic_width  # Update x position after the topic

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

data_dict = [
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

create_pdf(data_dict, "test.pdf")
