import os
import json
import logging
import google.generativeai as genai

# Configure the Gemini API
GEMINI_API_KEY = os.environ.get("GEMINI_API_KEY", "")
genai.configure(api_key=GEMINI_API_KEY)

def generate_quiz_with_gemini(content, quiz_type, question_count):
    """
    Generate a quiz using Google's Gemini API based on the provided content.
    
    Args:
        content (str): The text content to generate a quiz from
        quiz_type (str): The type of quiz to generate (Multiple Choice, True/False, etc.)
        question_count (int): The number of questions to generate (between 5-75)
        
    Returns:
        dict: A dictionary containing the quiz questions and answers
    """
    logging.debug(f"Generating {quiz_type} quiz with {question_count} questions")
    
    if not GEMINI_API_KEY:
        logging.error("No Gemini API key provided")
        raise ValueError("Gemini API key is required. Please set the GEMINI_API_KEY environment variable.")
    
    # Validate inputs
    if not content or len(content.strip()) < 50:
        raise ValueError("Content is too short. Please provide more text to generate a meaningful quiz.")
    
    if question_count < 5 or question_count > 75:
        raise ValueError("Question count must be between 5 and 75.")
    
    # Keep content within a reasonable length for the API
    max_content_length = 10000
    if len(content) > max_content_length:
        content = content[:max_content_length]
        logging.info(f"Content truncated to {max_content_length} characters")
    
    # Create the appropriate prompt based on quiz type
    if quiz_type == "Multiple Choice":
        prompt = f"""
        Create a multiple-choice quiz with {question_count} questions based on the following content. 
        For each question, provide 4 options (A, B, C, D) with exactly one correct answer.
        Format the response as a JSON array with the following structure:
        [
            {{
                "question": "Question text",
                "options": [
                    "Option A",
                    "Option B",
                    "Option C",
                    "Option D"
                ],
                "answer": "The correct option letter (A, B, C, or D)",
                "explanation": "Brief explanation of the correct answer"
            }}
        ]
        
        Content:
        {content}
        """
    elif quiz_type == "True/False":
        prompt = f"""
        Create a true/false quiz with {question_count} questions based on the following content.
        Format the response as a JSON array with the following structure:
        [
            {{
                "question": "Question text",
                "answer": "True or False",
                "explanation": "Brief explanation of the correct answer"
            }}
        ]
        
        Content:
        {content}
        """
    elif quiz_type == "Fill in the Blanks":
        prompt = f"""
        Create a fill-in-the-blanks quiz with {question_count} questions based on the following content.
        Use _____ to indicate blanks in the question text.
        Format the response as a JSON array with the following structure:
        [
            {{
                "question": "Question text with _____",
                "answer": "The word or phrase that goes in the blank",
                "explanation": "Brief explanation of the correct answer"
            }}
        ]
        
        Content:
        {content}
        """
    elif quiz_type == "Short Answer":
        prompt = f"""
        Create a short answer quiz with {question_count} questions based on the following content.
        Format the response as a JSON array with the following structure:
        [
            {{
                "question": "Question text",
                "answer": "The correct answer",
                "explanation": "Brief explanation of the correct answer"
            }}
        ]
        
        Content:
        {content}
        """
    else:  # Mixed type
        prompt = f"""
        Create a mixed-type quiz with {question_count} questions based on the following content.
        Include a combination of multiple-choice, true/false, fill-in-the-blanks, and short answer questions.
        Format the response as a JSON array with the following structure:
        [
            {{
                "question_type": "Multiple Choice",
                "question": "Question text",
                "options": ["Option A", "Option B", "Option C", "Option D"],
                "answer": "The correct option letter (A, B, C, or D)",
                "explanation": "Brief explanation of the correct answer"
            }},
            {{
                "question_type": "True/False",
                "question": "Question text",
                "answer": "True or False",
                "explanation": "Brief explanation of the correct answer"
            }},
            {{
                "question_type": "Fill in the Blanks",
                "question": "Question text with _____",
                "answer": "The word or phrase that goes in the blank",
                "explanation": "Brief explanation of the correct answer"
            }},
            {{
                "question_type": "Short Answer",
                "question": "Question text",
                "answer": "The correct answer",
                "explanation": "Brief explanation of the correct answer"
            }}
        ]
        
        Content:
        {content}
        """
    
    try:
        # Initialize the Gemini model - using Gemini 1.5 Pro
        model = genai.GenerativeModel('gemini-1.5-pro')
        
        # Generate response
        response = model.generate_content(prompt)
        
        # Extract and parse the JSON content
        response_text = response.text
        
        # Find the start and end of the JSON array
        start_idx = response_text.find('[')
        end_idx = response_text.rfind(']') + 1
        
        if start_idx == -1 or end_idx == 0:
            raise ValueError("Invalid response format from Gemini API")
        
        json_content = response_text[start_idx:end_idx]
        quiz_data = json.loads(json_content)
        
        # Validate the response
        if not isinstance(quiz_data, list) or len(quiz_data) == 0:
            raise ValueError("Invalid quiz data format")
        
        return quiz_data
    
    except Exception as e:
        logging.error(f"Error generating quiz: {str(e)}")
        raise
