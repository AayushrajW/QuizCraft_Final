import io
import logging
from reportlab.lib.pagesizes import letter
from reportlab.lib import colors
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle

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
        # Create the PDF document
        doc = SimpleDocTemplate(
            buffer,
            pagesize=letter,
            title=quiz_title,
            author="QuizCraft",
            subject="Generated Quiz"
        )
        
        # Define styles
        styles = getSampleStyleSheet()
        title_style = styles['Title']
        heading_style = styles['Heading2']
        normal_style = styles['Normal']
        
        # Create custom styles
        question_style = ParagraphStyle(
            'QuestionStyle',
            parent=styles['Normal'],
            fontName='Helvetica-Bold',
            fontSize=12,
            spaceAfter=6
        )
        
        answer_style = ParagraphStyle(
            'AnswerStyle',
            parent=styles['Normal'],
            fontName='Helvetica',
            fontSize=10,
            leftIndent=20,
            spaceAfter=12
        )
        
        explanation_style = ParagraphStyle(
            'ExplanationStyle',
            parent=styles['Italic'],
            fontName='Helvetica-Oblique',
            fontSize=10,
            leftIndent=20,
            textColor=colors.blue,
            spaceAfter=16
        )
        
        # Build the document content
        content = []
        
        # Add title
        content.append(Paragraph(quiz_title, title_style))
        content.append(Spacer(1, 24))
        
        # Add questions section
        content.append(Paragraph("Questions", heading_style))
        content.append(Spacer(1, 12))
        
        # Add each question
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
            
            # Format the question text
            q_text = f"{i+1}. [{question_type}] {question['question']}"
            content.append(Paragraph(q_text, question_style))
            
            # Add options for multiple choice questions
            if 'options' in question:
                options = question['options']
                for j, option in enumerate(options):
                    option_letter = chr(65 + j)  # A, B, C, D, etc.
                    content.append(Paragraph(f"{option_letter}. {option}", answer_style))
            
            content.append(Spacer(1, 8))
        
        # Add page break before answers
        content.append(Paragraph("", styles['Normal']))
        content.append(Spacer(1, 40))
        
        # Add answers section
        content.append(Paragraph("Answers", heading_style))
        content.append(Spacer(1, 12))
        
        # Add each answer
        for i, question in enumerate(quiz_data):
            q_text = f"{i+1}. "
            
            # Format answer based on question type
            if 'options' in question:
                q_text += f"Answer: {question['answer']}"
            else:
                q_text += f"Answer: {question['answer']}"
            
            content.append(Paragraph(q_text, question_style))
            
            # Add explanation if available
            if 'explanation' in question:
                content.append(Paragraph(f"Explanation: {question['explanation']}", explanation_style))
            
            content.append(Spacer(1, 8))
        
        # Build the PDF
        doc.build(content)
        
        buffer.seek(0)
        return buffer
    
    except Exception as e:
        logging.error(f"Error creating PDF: {str(e)}")
        raise
