import os
import tempfile
from reportlab.lib import pagesizes
from reportlab.lib.styles import getSampleStyleSheet
from reportlab.lib.units import inch
from reportlab.lib.pagesizes import letter
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer
from reportlab.lib.enums import TA_LEFT
from reportlab.lib import colors
from typing import List

def create_cheatsheet_pdf(topics: List[List[str]]) -> str:
    """
    Create a fully optimized cheatsheet from a list of topics. Utilizes formatting and
    positioning to make efficient use of white space. Returns the path to the 
    created PDF on the system.
    """
    temp_dir = tempfile.mkdtemp()
    file_path = os.path.join(temp_dir, 'cheatsheet.pdf')

    # Create a file in the temp directory
    with open(file_path, 'wb') as temp_file:
        # Create a PDF document with the given filename
        pdf = SimpleDocTemplate(
            temp_file, 
            pagesize=letter,
            rightMargin=0.5 * inch, 
            leftMargin=0.5 * inch, 
            topMargin=0.75 * inch, 
            bottomMargin=0.75 * inch
        )
        
        # Use sample stylesheet to manage text styles
        styles = getSampleStyleSheet()
        
        # Modifying default style for better spacing and wrapping
        bullet_style = styles["Normal"]
        bullet_style.leading = 12  # Line height
        bullet_style.alignment = TA_LEFT
        bullet_style.wordWrap = 'CJK'  # Ensure the text wraps

        content = []
        
        for idx, topic in enumerate(topics):
            # Add the topic title
            topic_title = f"Topic {idx + 1}"
            content.append(Paragraph(f"<b>{topic_title}</b>", styles['Title']))
            
            for bullet_point in topic:
                # Add each bullet point with a small indent
                content.append(Paragraph(f"• {bullet_point}", bullet_style))
            
            # Add a spacer between topics
            content.append(Spacer(1, 12))
        
        # Build the PDF
        pdf.build(content)
        
    return file_path
