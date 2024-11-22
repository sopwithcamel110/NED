import re
import logging
from rectpack import float2dec, newPacker, PackingMode
from reportlab.platypus import SimpleDocTemplate, Spacer
from reportlab.lib.units import inch
from reportlab.lib.pagesizes import A4
from reportlab.pdfgen import canvas
from reportlab.pdfbase.ttfonts import TTFont
from reportlab.pdfbase import pdfmetrics

from typing import Any, Dict, List, Tuple

logging.basicConfig(level=logging.DEBUG)

SCRIPT_FONT_SIZE = 0.7 # super/subscript font size
Y_SCRIPT = 1 - SCRIPT_FONT_SIZE

PATTERN = re.compile(
    r"([^\^_]+)"              # Normal text
    r"|(\^)\{([^\}]+)\}"      # Superscripts
    r"|(_)\{([^\}]+)\}"       # Subscripts
    r"|([^\^_]+)_\{([^\}]+)\}\^\{([^\}]+)\}"  # Combined subscript and superscript
)

def parse_style(input_list: List[str]) -> List[List[Tuple[str, str]]]:
    """
    Parse a string for superscripts (^{}) and subscripts (_{}).
    Returns a list of lists of tuples (text, style), where style can be 'normal', 'superscript', or 'subscript'.
    """
    results = []

    for s in input_list:
        matches = PATTERN.finditer(s)
        
        for match in matches:
            if match.group(1):  # Normal text
                results.append([(match.group(1), "normal")])
            elif match.group(2):  # Superscript
                results.append([(match.group(3), "superscript")])
            elif match.group(4):  # Subscript
                results.append([(match.group(5), "subscript")])
            elif match.group(6):  # Combined subscript and superscript
                results.append([(match.group(6), "combined", match.group(7), match.group(8))])
    
    return results

def render_parsed_text(c, x, y, parsed_text, font="Helvetica", base_font_size=12):
    """
    Render parsed text with LaTeX-style superscripts, subscripts, and combinations
    on a ReportLab canvas.
    """
    for item in parsed_text:
        if isinstance(item, tuple) and len(item) == 2:
            text, style = item
            if style == "normal":
                c.setFont(font, base_font_size)
                c.drawString(x, y, text)
                x += c.stringWidth(text, font, base_font_size)
            elif style == "superscript":
                c.setFont(font, base_font_size * SCRIPT_FONT_SIZE)
                c.drawString(x, y + base_font_size * Y_SCRIPT, text)
                x += c.stringWidth(text, font, base_font_size * SCRIPT_FONT_SIZE)
            elif style == "subscript":
                c.setFont(font, base_font_size * SCRIPT_FONT_SIZE)
                c.drawString(x, y - base_font_size * Y_SCRIPT, text)
                x += c.stringWidth(text, font, base_font_size * SCRIPT_FONT_SIZE)

        elif isinstance(item, tuple) and len(item) == 4: #combined
            base, _, subscript, superscript = item
            # Render base character
            c.setFont(font, base_font_size)
            c.drawString(x, y, base)
            base_width = c.stringWidth(base, font, base_font_size)
            x += base_width

            # Render subscript
            c.setFont(font, base_font_size * SCRIPT_FONT_SIZE)
            subscript_width = c.stringWidth(subscript, font, base_font_size * SCRIPT_FONT_SIZE)
            c.drawString(x, y - base_font_size * Y_SCRIPT, subscript)

            # Render superscript
            c.setFont(font, base_font_size * SCRIPT_FONT_SIZE)
            c.drawString(x + subscript_width, y + base_font_size * Y_SCRIPT, superscript)
            x += subscript_width + c.stringWidth(superscript, font, base_font_size * SCRIPT_FONT_SIZE)

    return x

def styleStringWidth(c: canvas.Canvas, text: List[List[Tuple[str, str]]], font: str, font_size: int) -> int:
    """
    Wrapper for stringWidth function that accounts for superscripts and subscript dimension changes.
    Takes a nested list (List[List[Tuple[str, str]]]) of text and styles.
    """
    width = 0

    for sublist in text:  # Iterate through each sublist
        for content, style in sublist:  # Iterate through tuples in the sublist
            if style == "normal":
                current_font_size = font_size
            elif style in ["superscript", "subscript", "combined"]:
                current_font_size = font_size * SCRIPT_FONT_SIZE
            else:
                continue  # Skip unsupported styles

            # Add the width of the current text with the current font size
            width += c.stringWidth(content, font, current_font_size)

    return width   

if __name__ == "__main__":
    print("Hello there. mathsymbols.py is running")