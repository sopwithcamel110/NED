import random
from enum import Enum
from reportlab.lib.pagesizes import A4
from reportlab.pdfgen import canvas
from reportlab.lib.units import inch

# Enum for media types
class MediaType(Enum):
    TEXT = "text"
    IMAGE = "image"

def image_create():
    return 0

def text_create(c, topic, bullet_points, current_x, current_y, font_size, page_width, page_height, top_margin, msf_height, total_height):
    topic_width = max(c.stringWidth(s, "Helvetica-Bold", font_size) for s in [topic] + bullet_points) 
    if current_y - (len(bullet_points)+1)*font_size <= 0:
        c.showPage()
        total_height = msf_height = 0
        current_x = 0
        current_y = page_height-top_margin
    elif current_x + topic_width > page_width:
        # Move to the next line if the topic doesn't fit horizontally
        current_x = 0
        total_height += msf_height
        msf_height = 0
        current_y = page_height-(total_height*font_size)-top_margin  # Move down to the next line
    msf_height = max(msf_height, len(bullet_points)+1) # +1 for topic

    # Draw the topic in bold
    c.setFont("Helvetica-Bold", font_size)
    c.drawString(current_x, current_y, topic)

    c.setFont("Helvetica", font_size)  # Smaller font size to fit more text
    for i, bullet in enumerate(bullet_points):
        bullet_text = f'• {bullet}'
        bullet_width = c.stringWidth(bullet_text, "Helvetica", font_size)

        # Draw bullet point
        c.drawString(current_x, current_y-((i+1)*font_size), bullet_text)
    
    # If the next topic exceeds the right margin, move to the next line
    if current_x > page_width:
        current_x = 0
        current_y -= font_size

    # Check for page overflow
    current_x += topic_width  # Update x position after the topic

    return msf_height, total_height, current_x, current_y
# Mapping media types to functions
media_function_map = {
    MediaType.TEXT: text_create,
    MediaType.IMAGE: image_create
}

# Stub function for handling image creation (to be implemented)
def create_pdf(data_list, filename):
    c = canvas.Canvas(filename, pagesize=A4)
    page_width, page_height = A4
    font_size = 5
    top_margin = font_size
    current_x = 0
    current_y = page_height - top_margin

    total_height = 0
    msf_height = 0
    for entry in data_list:
        topic = entry["topic"]
        content = entry["content"]
        media_type_str = entry["media"]

        try:
            media_type_enum = MediaType(media_type_str)
            
            # Pass the parameters, including page dimensions
            msf_height, total_height, current_x, current_y = media_function_map[media_type_enum](
                c, topic, content, current_x, current_y, font_size, page_width, page_height, top_margin,
                msf_height, total_height)
        except KeyError:
            print(f"No function found for media type: {media_type_str}")
        except ValueError:
            print(f"Invalid media type: {media_type_str}")

    # Save the PDF
    c.save()


# Example data
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
        "Can be used in higher-order functions like map, filter, reduce."
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
    for k, v in items_copy:
        scaled_data.append({
            'topic': k+str(i),
            'content': v,
            'media': 'text',
        })

create_pdf(scaled_data, "cheatsheet.pdf")
