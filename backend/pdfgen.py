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

def place_content(c: canvas.Canvas, content: ContentType, x: float, y: float, font_size: int) -> None:
    """Place content directly at x and y on the given canvas."""
    match MediaType(content['media']):
        case MediaType.TEXT:
            topic = content['topic']
            bullet_points = content['content']

            # Draw the topic in bold
            c.setFont("Helvetica-Bold", font_size)
            c.drawString(x, y, topic)

            c.setFont("Helvetica", font_size)  # Smaller font size to fit more text
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
        "topic": "Python Basics",
        "content": [
            "Variables store data and can be of various types such as int, float, and str.",
            "Control structures like if-else, for, and while loops allow for flow control.",
            "Functions are defined using the def keyword and help modularize code.",
            "Comments are added with a # and are not executed by the interpreter."
        ],
        "media": "text"
    },
    {
        "topic": "Object-Oriented Programming",
        "content": [
            "Classes are blueprints for creating objects, defined using the class keyword.",
            "An object is an instance of a class and has attributes and methods.",
            "Inheritance allows classes to derive properties from other classes.",
            "Encapsulation restricts access to methods and variables."
        ],
        "media": "text"
    },
    {
        "topic": "Python Libraries",
        "content": [
            "NumPy is used for numerical computations and handling arrays.",
            "Pandas is great for data manipulation and analysis.",
            "Matplotlib helps create visualizations like line charts and bar charts.",
            "Requests is a library for making HTTP requests in Python."
        ],
        "media": "text"
    },
    # {
    #     "topic": "Images",
    #     "content": [
    #         "Image1.png", 4, 2
    #     ],
    #     "media": "image"
    # },
    {
        "topic": "Images",
        "content": [
            "Image1.png", 4, 2
        ],
        "media": "image"
    },
    {
        "topic": "Error Handling",
        "content": [
            "Exceptions are handled using try, except, and finally blocks.",
            "Custom exceptions can be created by inheriting from the Exception class.",
            "Using else after try-except allows code to run if no exceptions are raised.",
            "Raise keyword is used to trigger exceptions manually."
        ],
        "media": "text"
    },
    {
        "topic": "Data Structures in Python",
        "content": [
            "Lists are mutable collections of items, defined using square brackets.",
            "Tuples are immutable sequences, useful for fixed data.",
            "Dictionaries store key-value pairs and are defined using curly braces.",
            "Sets are unordered collections of unique elements."
        ],
        "media": "text"
    },
    {
        "topic": "File Handling",
        "content": [
            "Open files using open(filename, mode) where mode can be 'r', 'w', or 'a'.",
            "Use with statement for automatic file closing.",
            "Read files using read(), readline(), or readlines() methods.",
            "Write data using write() or writelines() for multiple lines."
        ],
        "media": "text"
    },
    {
        "topic": "Web Development with Flask",
        "content": [
            "Flask is a micro web framework for Python, used to create web apps.",
            "Routes define the URL structure and are created using the @app.route decorator.",
            "Templates are used to render dynamic HTML using Jinja2.",
            "Flask can connect to databases like SQLite, PostgreSQL, and MySQL."
        ],
        "media": "text"
    },
    {
        "topic": "Testing in Python",
        "content": [
            "Unit tests are created using the unittest library for testing functions.",
            "pytest is a popular testing framework for more complex testing needs.",
            "Mocks are used to replace parts of the system under test.",
            "Coverage.py is used to measure code coverage during testing."
        ],
        "media": "text"
    },
    {
        "topic": "Python Packaging",
        "content": [
            "Use setup.py to define package metadata and dependencies.",
            "Virtual environments help isolate project dependencies.",
            "pip is the default package manager used for installing libraries.",
            "Publishing packages to PyPI can be done using twine."
        ],
        "media": "text"
    }
]

create_pdf(data_dict, "test.pdf")