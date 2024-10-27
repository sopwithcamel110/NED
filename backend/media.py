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
            topic_width = max(c.stringWidth(s, "Helvetica-Bold", font_size) for s in [topic] + bullet_points) 
            topic_height = len(bullet_points)+1 # +1 for topic
            return topic_width, topic_height
        case MediaType.IMAGE:
            #content width, content height
            return content['content'][1] * inch, (content['content'][2] * inch) // 5

def set_dimensions(c: canvas.Canvas, content: ContentType, page_width, page_height, current_x: int, current_y: int, total_height: int, 
                msf_height: int, top_margin: int, font_size: int, topic_width: int, topic_height):
    """
    Sets/controls dimensions of content on page depending on media type
    """
    match MediaType(content['media']):
        case MediaType.TEXT:
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

        case MediaType.IMAGE:
            if current_x + topic_width > page_width:
                current_x = 0
                total_height += msf_height
                msf_height = 0
                current_y = page_height-total_height-top_margin 
            elif current_y - topic_height <= 0:
                c.showPage()
                total_height = msf_height = 0
                current_x = 0
                current_y = page_height-top_margin 

    return (c, current_x, current_y, total_height, msf_height)