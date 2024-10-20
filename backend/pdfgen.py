# from reportlab.lib.pagesizes import letter
# from reportlab.lib import colors
# from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
# from reportlab.platypus import BaseDocTemplate, Paragraph, Frame, PageTemplate

# #Take max min length to find max width margin for column 
# # FUTURE: have page size param to determine max length of allowed columns
# def content_size(content : list[str]) -> tuple[int,int]: 
#     max_width_len = len(max(content, key=len))
#     min_width_len = len(min(content, key=len))

#     dif_width_len = (max_len - min_len) // 2


#     return (min_width_len + dif_width_len), 0

# def createpdf(topics: dict[str, list[str]], filename: str): 
#     pdf = BaseDocTemplate(filename, pagesize=letter)

#     width, height = letter
#     styles = getSampleStyleSheet()
#     custom_style = ParagraphStyle(
#         name="CustomStyle",
#         fontName="Helvetica",
#         fontSize=10,
#         leading=14,  # Line spacing
#         textColor=colors.black,
#         leftIndent=0,
#         rightIndent=0,
#         firstLineIndent=0,
#         spaceAfter=10,  # Space after the paragraph
#         alignment=0,  # Left-aligned
#     )

#     paragraph = Paragraph(text_content, custom_style)
#     frame_width = 200
#     frame_height = height - 50


# # Create a paragraph object with the custom style
# paragraph = Paragraph(text_content, custom_style)

# # Create a narrow frame to resemble the width from the image
# frame_width = 200  # Set the width to be narrower (200 points wide)
# frame_height = height - 50  # Adjust the height to leave a small margin at the bottom

# # Define the frame, placing it at the top-left corner
# narrow_frame = Frame(0, height - frame_height, frame_width, frame_height)  # (x=0, y=top, width, height)

# # Create a PageTemplate using the Frame
# template = PageTemplate(id="narrow_frame_template", frames=[narrow_frame])

# # Add the PageTemplate to the document
# doc.addPageTemplates([template])

# # Build the document with the paragraph
# doc.build([paragraph])

from reportlab.lib.pagesizes import letter
from reportlab.lib import colors
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.platypus import BaseDocTemplate, Paragraph, Frame, PageTemplate, Spacer

# Create a PDF document using BaseDocTemplate
doc = BaseDocTemplate("narrow_paragraphs_example.pdf", pagesize=letter)

# Get width and height of the page
width, height = letter

# Get a stylesheet and create custom paragraph styles
styles = getSampleStyleSheet()

# Create custom paragraph styles for title and content
title_style = ParagraphStyle(
    name="TitleStyle",
    fontName="Helvetica-Bold",
    fontSize=14,
    leading=16,  # Line spacing for the title
    textColor=colors.black,
    spaceAfter=4,  # Reduced space after the title
)

content_style = ParagraphStyle(
    name="ContentStyle",
    fontName="Helvetica",
    fontSize=12,
    leading=14,  # Line spacing for the content
    textColor=colors.black,
    leftIndent=0,
    rightIndent=0,
    firstLineIndent=0,
    spaceBefore=0,  # No space before each paragraph
    spaceAfter=4,  # Reduced space after each content string
    alignment=0,  # Left-aligned
)

# Example dictionary: title (key) and content (value)
content_dict = {
    "Charge": [
        "You are hereby charged that on the 28th day of May, 1970, you did willfully, unlawfully,",
        "and with malice of forethought, publish an alleged English-Hungarian phrase book with",
        "intent to cause a breach of the peace. How do you plead?"
    ],
    "Defense": [
        "The accused pleads not guilty on all charges.",
        "The defense will provide evidence that the phrase book was intended as a cultural aid."
    ],
    "Prosecution": [
        "The prosecution contends that the phrase book was created with malicious intent.",
        "Several witnesses have testified to its inflammatory nature."
    ],
    "S1": [
        "You are hereby charged that on the 28th day of May, 1970, you did willfully, unlawfully,",
        "and with malice of forethought, publish an alleged English-Hungarian phrase book with",
        "intent to cause a breach of the peace. How do you plead?"
    ],
    "S2": [
        "The accused pleads not guilty on all charges.",
        "The defense will provide evidence that the phrase book was intended as a cultural aid."
    ],
    "S3": [
        "The prosecution contends that the phrase book was created with malicious intent.",
        "Several witnesses have testified to its inflammatory nature."
    ],
    "S4": [
        "You are hereby charged that on the 28th day of May, 1970, you did willfully, unlawfully,",
        "and with malice of forethought, publish an alleged English-Hungarian phrase book with",
        "intent to cause a breach of the peace. How do you plead?"
    ],
    "S5": [
        "The accused pleads not guilty on all charges.",
        "The defense will provide evidence that the phrase book was intended as a cultural aid."
    ],
    "S6": [
        "The prosecution contends that the phrase book was created with malicious intent.",
        "Several witnesses have testified to its inflammatory nature."
    ]
}

# Create a list to store the flowables (paragraphs, spacers, etc.)
flowables = []

# Loop over the dictionary and create paragraphs for each title and its content
for title, content_list in content_dict.items():
    # Create a title paragraph
    title_paragraph = Paragraph(title, title_style)
    flowables.append(title_paragraph)

    # Create content paragraphs
    for content in content_list:
        content_paragraph = Paragraph(content, content_style)
        flowables.append(content_paragraph)

    # Add small space after each section (title + content)
    flowables.append(Spacer(1, 8))  # Spacer with reduced space between sections

# Create a narrow frame to resemble the width from the image
frame_width = 200  # Set the width to be narrower (200 points wide)
frame_height = height - 50  # Adjust the height to leave a small margin at the bottom

# Define the frame, placing it at the top-left corner
narrow_frame = Frame(0, height - frame_height, frame_width, frame_height)  # (x=0, y=top, width, height)

# Create a PageTemplate using the Frame
template = PageTemplate(id="narrow_frame_template", frames=[narrow_frame])

# Add the PageTemplate to the document
doc.addPageTemplates([template])

# Build the document with the list of flowables (title + content paragraphs)
doc.build(flowables)