import os
# import tempfile
# from reportlab.lib import pagesizes
# from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
# from reportlab.lib.units import inch
# from reportlab.lib.pagesizes import letter
# from reportlab.platypus import SimpleDocTemplate, Paragraph, Frame, Spacer
# from reportlab.lib.enums import TA_LEFT
# from reportlab.lib import colors
# from typing import List
# import textwrap
from reportlab.lib.pagesizes import letter
from reportlab.pdfgen import canvas
from reportlab.lib import colors
from reportlab.lib.units import inch
from reportlab.platypus import SimpleDocTemplate, Paragraph, Frame, Spacer, ListFlowable, ListItem
from reportlab.lib.styles import getSampleStyleSheet
from reportlab.platypus.flowables import BalancedColumns
from reportlab.platypus.frames import ShowBoundaryValue

def create_pdf_with_columns(data, file_name="output.pdf"):
    story.append(
        Balanced(
            data,
            nCol = 1,
            needed = 72,
            spaceBefore = 0,
            spaceAfter = 0,
            showBoundary = None,
            leftPadding = None,
            rightPadding = None,
            topPadding = None, 
            bottomPadding = None,
            innerPadding = None,
            name = 'col1',
            endSlask = 0.1,
        )
    )








# # Function to calculate the content size
# def calculate_content_size(text, max_width, font_size):
#     """Calculate the number of lines a given text will take based on word wrapping."""
#     lines = textwrap.wrap(text, width=max_width)
#     return len(lines)

# def create_pdf(data, filename="output.pdf"):
#     """Create a PDF document with the formatted topics and bullet points."""
#     doc = SimpleDocTemplate(filename, pagesize=letter)
#     styles = getSampleStyleSheet()
#     story = []
    
#     # Define custom paragraph style for better word wrapping
#     bullet_style = ParagraphStyle(
#         name='BulletStyle',
#         fontSize=10,
#         leading=12,  # Line height
#         leftIndent=20,
#         firstLineIndent=-10,
#         spaceAfter=5,
#         alignment=TA_LEFT
#     )
    
#     # Define page width and height
#     page_width, page_height = letter
#     margin = 0.5 * inch
#     max_width = int((page_width - 2 * margin) // 6)  # Rough estimate of characters per line

#     # Loop through each topic
#     for topic, bullet_points in data.items():
#         # Add the topic header
#         story.append(Paragraph(f"<b>{topic}</b>", styles['Heading2']))
        
#         # Calculate total content size for this topic
#         total_lines = 0
#         for point in bullet_points:
#             lines = calculate_content_size(point, max_width, 10)  # 10 is the font size
#             total_lines += lines
            
#         # Add bullet points
#         for bullet in bullet_points:
#             wrapped_bullet = "\n".join(textwrap.wrap(bullet, width=max_width))
#             story.append(Paragraph(f"• {wrapped_bullet}", bullet_style))
        
#         # Add some space after each topic
#         story.append(Spacer(1, 12))
    
#     # Build the PDF
#     doc.build(story)

# def create_cheatsheet_pdf(topics: List[List[str]]) -> str:
#     """
#     Create a fully optimized cheatsheet from a list of topics. Utilizes formatting and
#     positioning to make efficient use of white space. Returns the path to the 
#     created PDF on the system.
#     """
#     temp_dir = tempfile.mkdtemp()
#     file_path = os.path.join(temp_dir, 'cheatsheet.pdf')

#     # Create a file in the temp directory
#     with open(file_path, 'wb') as temp_file:
#         # Create a PDF document with the given filename
#         pdf = SimpleDocTemplate(
#             temp_file, 
#             pagesize=letter,
#             rightMargin=0.5 * inch, 
#             leftMargin=0.5 * inch, 
#             topMargin=0.75 * inch, 
#             bottomMargin=0.75 * inch
#         )
        
#         # Use sample stylesheet to manage text styles
#         styles = getSampleStyleSheet()
        
#         # Modifying default style for better spacing and wrapping
#         bullet_style = styles["Normal"]
#         bullet_style.leading = 12  # Line height
#         bullet_style.alignment = TA_LEFT
#         bullet_style.wordWrap = 'CJK'  # Ensure the text wraps

#         content = []
        
#         for idx, topic in enumerate(topics):
#             # Add the topic title
#             topic_title = f"Topic {idx + 1}"
#             content.append(Paragraph(f"<b>{topic_title}</b>", styles['Title']))
            
#             for bullet_point in topic:
#                 # Add each bullet point with a small indent
#                 content.append(Paragraph(f"• {bullet_point}", bullet_style))
            
#             # Add a spacer between topics
#             content.append(Spacer(1, 12))
        
#         # Build the PDF
#         pdf.build(content)
        
#     return file_path


# data = {
#     "Topic 1": [
#         "This is the first bullet point of topic 1. It has several sentences that need to be wrapped appropriately.",
#         "This is the second bullet point with slightly less text.",
#         "Third point. Word wrapping should handle this correctly."
#     ],
#     "Topic 2": [
#         "Topic 2 has different content. Each bullet point may vary in length.",
#         "Ensure that the formatting remains consistent and uses space efficiently."
#     ],
#     "Topic 3": [
#         "This is the first bullet point of topic 1. It has several sentences that need to be wrapped appropriately.",
#         "This is the second bullet point with slightly less text.",
#         "Third point. Word wrapping should handle this correctly."
#     ],
#     "Topic 4": [
#         "This is the first bullet point of topic 1. It has several sentences that need to be wrapped appropriately.",
#         "This is the second bullet point with slightly less text.",
#         "Third point. Word wrapping should handle this correctly."
#     ],
# }

data = [
    "Lorem ipsum dolor sit amet, consectetur adipiscing elit,",
    "sed do eiusmod tempor", 
    "incididunt ut labore et dolore magna aliqua.",
    "Ut enim ad minim veniam,",
    "quis nostrud exercitation ullamco laboris nisi ut",
    "aliquip ex ea commodo consequat.",
    "Duis aute irure dolor in reprehenderit in voluptate velit",
    "Excepteur sint occaecat cupidatat non proident,"
]

create_pdf_with_columns(data)