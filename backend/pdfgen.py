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



# Example data with mixed media types
data_list = [
    {"topic": "Python Basics", "content": [
        "print() - Outputs text to the console.",
        "for loops - Used to iterate over a sequence.",
        "if statements - Conditional execution."
    ], "media": "text"},
    {"topic": "Sample Image", "content": ["some other info", "here is more info"], "media": "text"},
    {"topic": "Python Basics", "content": [
        "print() - Outputs text to the console.",
        "for loops - Used to iterate over a sequence.",
        "if statements - Conditional execution."
    ], "media": "text"},
    {"topic": "Sample Image", "content": ["some other info", "here is more info"], "media": "text"},
      {"topic": "Python Basics", "content": [
        "print() - Outputs text to the console.",
        "for loops - Used to iterate over a sequence.",
        "if statements - Conditional execution."
    ], "media": "text"},
    {"topic": "Sample Image", "content": ["some other info", "here is more info"], "media": "text"},
    {"topic": "Python Basics", "content": [
        "print() - Outputs text to the console.",
        "for loops - Used to iterate over a sequence.",
        "if statements - Conditional execution."
    ], "media": "text"},
    {"topic": "Sample Image", "content": ["some other info", "here is more info"], "media": "text"},
      {"topic": "Python Basics", "content": [
        "print() - Outputs text to the console.",
        "for loops - Used to iterate over a sequence.",
        "if statements - Conditional execution."
    ], "media": "text"},
    {"topic": "Sample Image", "content": ["some other info", "here is more info"], "media": "text"},
    {"topic": "Python Basics", "content": [
        "print() - Outputs text to the console.",
        "for loops - Used to iterate over a sequence.",
        "if statements - Conditional execution."
    ], "media": "text"},
    {"topic": "Sample Image", "content": ["some other info", "here is more info"], "media": "text"},
      {"topic": "Python Basics", "content": [
        "print() - Outputs text to the console.",
        "for loops - Used to iterate over a sequence.",
        "if statements - Conditional execution."
    ], "media": "text"},
    {"topic": "Sample Image", "content": ["some other info", "here is more info"], "media": "text"},
    {"topic": "Python Basics", "content": [
        "print() - Outputs text to the console.",
        "for loops - Used to iterate over a sequence.",
        "if statements - Conditional execution."
    ], "media": "text"},
    {"topic": "Sample Image", "content": ["some other info", "here is more info"], "media": "text"},
      {"topic": "Python Basics", "content": [
        "print() - Outputs text to the console.",
        "for loops - Used to iterate over a sequence.",
        "if statements - Conditional execution."
    ], "media": "text"},
    {"topic": "Sample Image", "content": ["some other info", "here is more info"], "media": "text"},
    {"topic": "Python Basics", "content": [
        "print() - Outputs text to the console.",
        "for loops - Used to iterate over a sequence.",
        "if statements - Conditional execution."
    ], "media": "text"},
    {"topic": "Sample Image", "content": ["some other info", "here is more info"], "media": "text"},
      {"topic": "Python Basics", "content": [
        "print() - Outputs text to the console.",
        "for loops - Used to iterate over a sequence.",
        "if statements - Conditional execution."
    ], "media": "text"},
    {"topic": "Sample Image", "content": ["some other info", "here is more info"], "media": "text"},
    {"topic": "Python Basics", "content": [
        "print() - Outputs text to the console.",
        "for loops - Used to iterate over a sequence.",
        "if statements - Conditional execution."
    ], "media": "text"},
    {"topic": "Sample Image", "content": ["some other info", "here is more info"], "media": "text"},
      {"topic": "Python Basics", "content": [
        "print() - Outputs text to the console.",
        "for loops - Used to iterate over a sequence.",
        "if statements - Conditional execution."
    ], "media": "text"},
    {"topic": "Sample Image", "content": ["some other info", "here is more info"], "media": "text"},
    {"topic": "Python Basics", "content": [
        "print() - Outputs text to the console.",
        "for loops - Used to iterate over a sequence.",
        "if statements - Conditional execution."
    ], "media": "text"},
    {"topic": "Sample Image", "content": ["some other info", "here is more info"], "media": "text"}
    
]

# Create the PDF
create_pdf(data_list, "output_mixed_media.pdf")
