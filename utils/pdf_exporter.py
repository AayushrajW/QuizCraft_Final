import io
import logging
import re
import unicodedata
from reportlab.lib.pagesizes import letter
from reportlab.lib import colors
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import inch
from reportlab.platypus import (
    SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, 
    PageBreak, Image, HRFlowable, KeepTogether
)
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
from reportlab.lib.enums import TA_LEFT, TA_CENTER, TA_RIGHT

# Register a UTF-8 compatible font if necessary
# Uncomment these lines if you have DejaVu fonts available
# pdfmetrics.registerFont(TTFont('DejaVuSans', 'DejaVuSans.ttf'))
# pdfmetrics.registerFont(TTFont('DejaVuSans-Bold', 'DejaVuSans-Bold.ttf'))
# pdfmetrics.registerFont(TTFont('DejaVuSans-Italic', 'DejaVuSans-Italic.ttf'))

def clean_text(text):
    """
    Clean and prepare text for PDF rendering by handling special characters.
    
    Args:
        text (str): The input text to clean
        
    Returns:
        str: Cleaned text safe for PDF rendering
    """
    if not text:
        return ""
    
    # Replace smart quotes with straight quotes
    text = text.replace('"', '"').replace('"', '"')
    text = text.replace(''', "'").replace(''', "'")
    
    # Replace em-dashes with regular dashes
    text = text.replace('—', '-')
    
    # Normalize Unicode to closest ASCII equivalent when possible
    # This helps with many scientific and math symbols
    text = unicodedata.normalize('NFKD', text)
    
    # Handle subscripts and superscripts by using regular characters
    # Example: H₂O becomes H2O, etc.
    # This regex looks for Unicode subscript/superscript and replaces with regular numbers
    text = re.sub(r'[₀₁₂₃₄₅₆₇₈₉]', lambda m: '0123456789'['₀₁₂₃₄₅₆₇₈₉'.index(m.group(0))], text)
    text = re.sub(r'[⁰¹²³⁴⁵⁶⁷⁸⁹]', lambda m: '0123456789'['⁰¹²³⁴⁵⁶⁷⁸⁹'.index(m.group(0))], text)
    
    # Ensure proper space after numbers followed by periods (like "1.Test" becomes "1. Test")
    text = re.sub(r'(\d+)\.(\S)', r'\1. \2', text)
    
    return text

def create_quiz_pdf(quiz_data, quiz_title):
    """
    Create a PDF document containing the quiz questions and answers.
    
    Args:
        quiz_data (list): A list of quiz questions and answers
        quiz_title (str): The title of the quiz
        
    Returns:
        BytesIO: A buffer containing the PDF data
    """
    logging.debug(f"Creating PDF for quiz: {quiz_title}")
    
    buffer = io.BytesIO()
    
    try:
        # Create the PDF document with proper margins for better readability
        doc = SimpleDocTemplate(
            buffer,
            pagesize=letter,
            title=clean_text(quiz_title),
            author="QuizCraft",
            subject="Generated Quiz",
            leftMargin=0.75*inch,
            rightMargin=0.75*inch,
            topMargin=0.75*inch,
            bottomMargin=0.75*inch
        )
        
        # Define styles
        styles = getSampleStyleSheet()
        
        # Create custom styles with consistent font usage
        title_style = ParagraphStyle(
            'CustomTitle',
            parent=styles['Title'],
            fontName='Helvetica-Bold',
            fontSize=18,
            alignment=TA_CENTER,
            spaceAfter=24
        )
        
        heading_style = ParagraphStyle(
            'CustomHeading',
            parent=styles['Heading2'],
            fontName='Helvetica-Bold',
            fontSize=14,
            spaceBefore=12,
            spaceAfter=6
        )
        
        question_style = ParagraphStyle(
            'QuestionStyle',
            parent=styles['Normal'],
            fontName='Helvetica-Bold',
            fontSize=12,
            spaceBefore=8,
            spaceAfter=6,
            leading=14  # Line spacing
        )
        
        option_style = ParagraphStyle(
            'OptionStyle',
            parent=styles['Normal'],
            fontName='Helvetica',
            fontSize=11,
            leftIndent=20,
            spaceAfter=4,
            leading=14
        )
        
        answer_style = ParagraphStyle(
            'AnswerStyle',
            parent=styles['Normal'],
            fontName='Helvetica-Bold',
            fontSize=11,
            spaceBefore=4,
            spaceAfter=4,
            leading=14
        )
        
        explanation_style = ParagraphStyle(
            'ExplanationStyle',
            parent=styles['Italic'],
            fontName='Helvetica-Oblique',
            fontSize=10,
            leftIndent=20,
            textColor=colors.blue,
            spaceBefore=2,
            spaceAfter=10,
            leading=14
        )
        
        footer_style = ParagraphStyle(
            'FooterStyle',
            parent=styles['Normal'],
            fontName='Helvetica',
            fontSize=8,
            textColor=colors.darkgrey,
            alignment=TA_CENTER
        )
        
        # Build the document content
        content = []
        
        # Add title with proper formatting
        clean_title = clean_text(quiz_title)
        content.append(Paragraph(clean_title, title_style))
        
        # Add a divider line
        content.append(HRFlowable(width="100%", thickness=1, color=colors.black, spaceBefore=6, spaceAfter=12))
        
        # Add questions section
        content.append(Paragraph("Questions", heading_style))
        content.append(Spacer(1, 12))
        
        # Add each question with proper formatting
        for i, question in enumerate(quiz_data):
            # Determine question type and format accordingly
            if 'question_type' in question:
                question_type = question['question_type']
            elif 'options' in question:
                question_type = "Multiple Choice"
            elif question.get('answer') in ['True', 'False']:
                question_type = "True/False"
            elif '_____' in question.get('question', ''):
                question_type = "Fill in the Blanks"
            else:
                question_type = "Short Answer"
            
            # Clean and format the question text
            q_text = clean_text(f"{i+1}. [{question_type}] {question['question']}")
            
            # Use KeepTogether to prevent awkward breaks within a question
            question_elements = [Paragraph(q_text, question_style)]
            
            # Add options for multiple choice questions
            if 'options' in question:
                options = question['options']
                for j, option in enumerate(options):
                    option_letter = chr(65 + j)  # A, B, C, D, etc.
                    option_text = clean_text(f"{option_letter}. {option}")
                    question_elements.append(Paragraph(option_text, option_style))
            
            question_elements.append(Spacer(1, 8))
            
            # Keep the question and its options together when possible
            content.append(KeepTogether(question_elements))
        
        # Add page break before answers
        content.append(PageBreak())
        
        # Add answers section with heading
        content.append(Paragraph("Answers", heading_style))
        content.append(HRFlowable(width="100%", thickness=1, color=colors.black, spaceBefore=6, spaceAfter=12))
        
        # Add each answer with proper formatting
        for i, question in enumerate(quiz_data):
            # Clean the text for the answer
            answer_prefix = f"{i+1}. Answer: "
            answer_value = clean_text(question['answer'])
            
            answer_elements = [Paragraph(f"{answer_prefix}{answer_value}", answer_style)]
            
            # Add explanation if available
            if 'explanation' in question and question['explanation']:
                explanation_text = clean_text(f"Explanation: {question['explanation']}")
                answer_elements.append(Paragraph(explanation_text, explanation_style))
            
            answer_elements.append(Spacer(1, 6))
            
            # Keep answer and its explanation together
            content.append(KeepTogether(answer_elements))
        
        # Add footer with page numbers
        def add_page_number(canvas, doc):
            canvas.saveState()
            canvas.setFont('Helvetica', 8)
            # Add just the current page number - simpler but still professional
            page_num = canvas._pageNumber  # Access the current page number
            page_text = f"Page {page_num}"
            # Bottom center footer
            canvas.drawCentredString(doc.width/2 + doc.leftMargin, 0.5*inch, page_text)
            # Add branding footer
            canvas.drawString(doc.leftMargin, 0.5*inch, "Generated by QuizCraft")
            canvas.restoreState()
        
        # Build the PDF with page numbers
        doc.build(content, onFirstPage=add_page_number, onLaterPages=add_page_number)
        
        buffer.seek(0)
        return buffer
    
    except Exception as e:
        logging.error(f"Error creating PDF: {str(e)}")
        raise
