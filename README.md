# QuizCraft

QuizCraft is an AI-powered quiz generator built with Flask that transforms any content into engaging quizzes.

## Features

- **AI-Powered Generation**: Utilizes Google's Gemini API to create intelligent, relevant questions
- **Multiple Input Methods**: Upload files (PDF, DOCX, TXT, CSV), images (with OCR), or paste text directly
- **Various Quiz Types**: Generate multiple-choice, true/false, fill-in-the-blanks, short answer, or mixed quizzes
- **PDF Export**: Download professionally formatted quiz PDFs with questions and answers
- **User Accounts**: Save your quiz history and access it anytime
- **Modern UI**: Beautiful Tailwind CSS interface with a responsive design

## Requirements

- Python 3.10.11
- Flask and its extensions
- Google Generative AI API (Gemini)
- Tesseract OCR (for image processing)
- Other dependencies listed in requirements.txt

## Local Setup

1. Clone the repository:
```bash
git clone https://github.com/yourusername/quizcraft.git
cd quizcraft
