from reportlab.lib.pagesizes import letter
from reportlab.lib import colors
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.platypus import BaseDocTemplate, Paragraph, Frame, PageTemplate

#Take max min length to find max width margin for column 
# FUTURE: have page size param to determine max length of allowed columns
def content_size(content : list[str]) -> tuple[int,int]: 
    max_width_len = len(max(content, key=len))
    min_width_len = len(min(content, key=len))

    dif_width_len = (max_len - min_len) // 2


    return (min_width_len + dif_width_len), 0

# Create a PDF document using BaseDocTemplate
doc = BaseDocTemplate("narrow_paragraph_example.pdf", pagesize=letter)

# Get width and height of the page
width, height = letter

# Get a stylesheet and create a custom paragraph style
styles = getSampleStyleSheet()

# Create a custom paragraph style
custom_style = ParagraphStyle(
    name="CustomStyle",
    fontName="Helvetica",
    fontSize=12,
    leading=14,  # Line spacing
    textColor=colors.black,
    leftIndent=0,
    rightIndent=0,
    firstLineIndent=0,
    spaceAfter=10,  # Space after the paragraph
    alignment=0,  # Left-aligned
)

# Create the paragraph content
text_content = """
You are hereby charged that on the 28th day of May, 1970, you did willfully, unlawfully, 
and with malice of forethought, publish an alleged English-Hungarian phrase book with 
intent to cause a breach of the peace. How do you plead?
"""

# Create a paragraph object with the custom style
paragraph = Paragraph(text_content, custom_style)

# Create a narrow frame to resemble the width from the image
frame_width = 200  # Set the width to be narrower (200 points wide)
frame_height = height - 50  # Adjust the height to leave a small margin at the bottom

# Define the frame, placing it at the top-left corner
narrow_frame = Frame(0, height - frame_height, frame_width, frame_height)  # (x=0, y=top, width, height)

# Create a PageTemplate using the Frame
template = PageTemplate(id="narrow_frame_template", frames=[narrow_frame])

# Add the PageTemplate to the document
doc.addPageTemplates([template])

# Build the document with the paragraph
doc.build([paragraph])
