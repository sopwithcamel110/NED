from enum import Enum
from io import BufferedWriter
import os
import random
import tempfile
from media import *
from typing import Any, Dict, List, Tuple

from reportlab.platypus import SimpleDocTemplate, Image, Spacer
from reportlab.lib.units import inch
from reportlab.lib.pagesizes import A4
from reportlab.pdfgen import canvas

ContentType = Dict[str, Any]

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

        c, current_x, current_y, total_height, msf_height = set_dimensions(
            c,
            content,
            page_width,
            page_height,
            current_x,
            current_y,
            total_height,
            msf_height,
            top_margin,
            font_size,
            topic_width,
            topic_height
        )
        # if current_x + topic_width > page_width:
        #     # Topic goes off right of page, go to next line
        #     current_x = 0
        #     total_height += msf_height
        #     msf_height = 0
        #     current_y = page_height-(total_height*font_size)-top_margin  # Move down to the next line
        # elif current_y - (topic_height*font_size) <= 0:
        #     # Topic goes off bottom of page, create a new one
        #     c.showPage()
        #     total_height = msf_height = 0
        #     current_x = 0
        #     current_y = page_height-top_margin 
        msf_height = max(msf_height, topic_height)

        print({f"x: {current_x:.1f}, y: {current_y:.1f}"}, msf_height, content['media'], )
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

# Example data with 20 topics
data_dict = {
    "Python Basics": [
        "print() - Outputs text to the console. Example: print('Hello, World!')",
        "for loops - Used to iterate over a sequence. Example: for i in range(5): print(i)",
        "if statements - Conditional execution. Example: if x > 5: print('x is greater than 5')"
    ],
    "List Comprehension": [
        "[x for x in range(10) if x % 2 == 0] - Generates a list of even numbers from 0 to 9.",
        "Syntax: [expression for item in iterable if condition]",
        "Example: squares = [x**2 for x in range(5)]  # [0, 1, 4, 9, 16]"
    ],
    "Lambda Functions": [
        "Anonymous function: lambda x: x * 2 - This returns double the input.",
        "Usage example: (lambda x, y: x + y)(3, 5)  # Outputs 8",
        "Can be used in higher-order functions like map, filter, reduce.",
        "Here is more information on the subject",
        "Even more bullet points",
    ],
    "Sorting in Python": [
        "sorted(iterable, key=lambda x: x[1]) - Sorts by second element in tuples.",
        "list.sort() - Sorts in place, modifies the list. Example: my_list.sort()",
        "sorted() - Returns a new sorted list, leaves the original unchanged."
    ],
    "Python String Methods": [
        "str.lower() - Converts the string to lowercase. Example: 'ABC'.lower() → 'abc'",
        "str.upper() - Converts the string to uppercase. Example: 'abc'.upper() → 'ABC'",
        "str.replace(old, new) - Replaces occurrences of a substring. Example: 'hello'.replace('e', 'a') → 'hallo'"
    ],
    "NumPy Array Creation": [
        "np.array([1, 2, 3]) - Creates a NumPy array.",
        "np.zeros((2, 3)) - Creates a 2x3 array of zeros.",
        "np.ones((2, 2)) - Creates a 2x2 array of ones."
    ],
    "Pandas DataFrame Basics": [
        "df.head() - Displays the first 5 rows of the DataFrame.",
        "df['column_name'] - Accesses a specific column.",
        "df.groupby('column').mean() - Groups data by a column and returns the mean."
    ],
    "SQL Basics": [
        "SELECT * FROM table WHERE condition; - Retrieves data from a table with a condition.",
        "INSERT INTO table (column1, column2) VALUES (value1, value2); - Inserts a new row into a table.",
        "UPDATE table SET column1 = value1 WHERE condition; - Updates rows in a table."
    ],
    "Git Commands": [
        "git clone <url> - Clones a repository from a URL.",
        "git commit -m 'message' - Commits staged changes with a message.",
        "git pull - Fetches and merges changes from the remote repository."
    ],
    "Mathematical Formulas": [
        "Quadratic Formula: (-b ± sqrt(b^2 - 4ac)) / 2a",
        "Area of Circle: A = πr^2",
        "Pythagorean Theorem: a^2 + b^2 = c^2"
    ],
    "Regular Expressions": [
        "r'\\d+' - Matches one or more digits.",
        "r'\\b\\w{3,}\\b' - Matches words of 3 or more characters.",
        "r'^abc' - Matches a string that starts with 'abc'."
    ],
    "Python Exceptions": [
        "try/except - Catches exceptions. Example: try: 1/0 except ZeroDivisionError: print('Cannot divide by zero')",
        "raise ValueError('message') - Raises a specific exception.",
        "finally - Executes code after try/except, regardless of exceptions."
    ],
    "Python Classes": [
        "class MyClass: - Defines a new class.",
        "def __init__(self, param): - Initializes the class with parameters.",
        "self.attribute - Refers to instance attributes inside the class."
    ],
    "Django Basics": [
        "urlpatterns - List of URL patterns in Django app.",
        "models.Model - Defines a database model in Django.",
        "views.py - Contains the logic for handling HTTP requests."
    ],
    "Flask Basics": [
        "@app.route('/') - Binds a function to a URL.",
        "render_template('template.html') - Renders an HTML template.",
        "request.args.get('param') - Retrieves query parameters from the URL."
    ],
    "Data Structures": [
        "List: Ordered, mutable collection. Example: my_list = [1, 2, 3]",
        "Tuple: Ordered, immutable collection. Example: my_tuple = (1, 2, 3)",
        "Dictionary: Key-value pairs. Example: my_dict = {'a': 1, 'b': 2}"
    ],
    "OOP Principles": [
        "Encapsulation: Hiding internal state and requiring all interaction through methods.",
        "Inheritance: A class inherits attributes and methods from another class.",
        "Polymorphism: Objects of different types can be accessed through the same interface."
    ],
    "Common Bash Commands": [
        "ls - Lists files in a directory.",
        "cd - Changes the current directory.",
        "grep - Searches text using patterns. Example: grep 'pattern' file.txt"
    ],
    "Kubernetes Basics": [
        "kubectl get pods - Lists all pods in the current namespace.",
        "kubectl apply -f config.yaml - Applies a YAML configuration file.",
        "kubectl logs pod_name - Displays logs for a specific pod."
    ],
    "Docker Commands": [
        "docker build -t tag_name . - Builds a Docker image from the current directory.",
        "docker run -d -p 80:80 image_name - Runs a container in detached mode, exposing port 80.",
        "docker-compose up - Starts services defined in docker-compose.yml."
    ]
}

scaled_data = []
for i in range(50):
    items_copy = list(data_dict.items())
    random.shuffle(items_copy)
    if i % 12 == 0:
        for k, v in items_copy:
            scaled_data.append({
                'topic': "Image",
                'content': ["testImage.png", 2, 1],
                'media': 'image',
            })

    for k, v in items_copy:
        scaled_data.append({
            'topic': k+str(i),
            'content': v,
            'media': 'text',
        })

create_pdf(scaled_data, "cheatsheet.pdf")
