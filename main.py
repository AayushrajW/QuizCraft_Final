import os
import logging
from app import app, init_login_manager
from flask import Flask, render_template, redirect, url_for, request, flash, session, send_file
from flask_login import login_user, logout_user, login_required, current_user
from werkzeug.security import generate_password_hash, check_password_hash
from werkzeug.utils import secure_filename
import tempfile
import io
import json

from models import User, Quiz
from app import db
from utils.quiz_generator import generate_quiz_with_gemini
from utils.ocr_reader import extract_text_from_image
from utils.pdf_exporter import create_quiz_pdf

# Set up logging
logging.basicConfig(level=logging.DEBUG)

# Initialize login manager
init_login_manager(app)

# Home route
@app.route('/')
def index():
    return render_template('index.html')

# Login route
@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username_or_email = request.form.get('username_or_email')
        password = request.form.get('password')
        
        # Try to find user by email first
        user = User.query.filter_by(email=username_or_email).first()
        
        # If not found, try by username
        if not user:
            user = User.query.filter_by(username=username_or_email).first()
        
        if user and check_password_hash(user.password_hash, password):
            login_user(user)
            flash('Login successful!', 'success')
            return redirect(url_for('dashboard'))
        else:
            flash('Invalid username/email or password.', 'error')
            
    return render_template('login.html')

# Register route
@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        username = request.form.get('username')
        email = request.form.get('email')
        password = request.form.get('password')
        
        # Check if user already exists
        existing_user = User.query.filter_by(email=email).first()
        if existing_user:
            flash('Email already in use.', 'error')
            return render_template('register.html')
        
        # Create new user
        new_user = User(
            username=username,
            email=email,
            password_hash=generate_password_hash(password)
        )
        
        try:
            db.session.add(new_user)
            db.session.commit()
            flash('Registration successful! Please login.', 'success')
            return redirect(url_for('login'))
        except Exception as e:
            db.session.rollback()
            flash(f'An error occurred during registration: {str(e)}', 'error')
            
    return render_template('register.html')

# Logout route
@app.route('/logout')
@login_required
def logout():
    logout_user()
    flash('You have been logged out.', 'info')
    return redirect(url_for('index'))

# Dashboard route
@app.route('/dashboard')
@login_required
def dashboard():
    user_quizzes = Quiz.query.filter_by(user_id=current_user.id).order_by(Quiz.created_at.desc()).all()
    return render_template('dashboard.html', quizzes=user_quizzes)

# Quiz generator route
@app.route('/generate', methods=['GET', 'POST'])
def generate():
    if request.method == 'POST':
        quiz_title = request.form.get('quiz_title', 'Untitled Quiz')
        quiz_type = request.form.get('quiz_type')
        question_count = int(request.form.get('question_count', 10))
        
        # Validate input
        if not quiz_type or question_count < 5 or question_count > 75:
            flash('Please select a quiz type and enter a valid number of questions (5-75).', 'error')
            return redirect(url_for('generate'))
        
        content = ''
        
        # Handle different input methods
        input_method = request.form.get('input_method')
        
        if input_method == 'text':
            content = request.form.get('content', '')
            
        elif input_method == 'file':
            file = request.files.get('file')
            if file and file.filename:
                filename = secure_filename(file.filename)
                file_ext = filename.rsplit('.', 1)[1].lower() if '.' in filename else ''
                
                if file_ext == 'pdf':
                    # Handle PDF
                    try:
                        from PyPDF2 import PdfReader
                        reader = PdfReader(file)
                        content = ""
                        for page in reader.pages:
                            content += page.extract_text() + "\n"
                    except Exception as e:
                        flash(f'Error processing PDF: {str(e)}', 'error')
                        return redirect(url_for('generate'))
                        
                elif file_ext == 'docx':
                    # Handle DOCX
                    try:
                        import docx
                        doc = docx.Document(file)
                        content = "\n".join([para.text for para in doc.paragraphs])
                    except Exception as e:
                        flash(f'Error processing DOCX: {str(e)}', 'error')
                        return redirect(url_for('generate'))
                        
                elif file_ext in ['txt', 'csv']:
                    # Handle text files
                    content = file.read().decode('utf-8')
                else:
                    flash('Unsupported file format. Please upload PDF, DOCX, TXT, or CSV files.', 'error')
                    return redirect(url_for('generate'))
        
        elif input_method == 'image':
            file = request.files.get('image')
            if file and file.filename:
                try:
                    # Extract text using OCR
                    content = extract_text_from_image(file)
                except Exception as e:
                    flash(f'Error processing image: {str(e)}', 'error')
                    return redirect(url_for('generate'))
        
        if not content:
            flash('Please provide some content for the quiz.', 'error')
            return redirect(url_for('generate'))
        
        try:
            # Generate quiz using Gemini API
            quiz_data = generate_quiz_with_gemini(content, quiz_type, question_count)
            
            # Save quiz to database if user is logged in
            if current_user.is_authenticated:
                quiz = Quiz(
                    title=quiz_title,
                    quiz_type=quiz_type,
                    question_count=question_count,
                    content=json.dumps(quiz_data),
                    user_id=current_user.id
                )
                db.session.add(quiz)
                db.session.commit()
                quiz_id = quiz.id
            else:
                # Store in session for guest users
                session['quiz_data'] = quiz_data
                session['quiz_title'] = quiz_title
                session['quiz_type'] = quiz_type
                quiz_id = None
            
            return redirect(url_for('preview_quiz', quiz_id=quiz_id))
            
        except Exception as e:
            flash(f'Error generating quiz: {str(e)}', 'error')
            return redirect(url_for('generate'))
    
    return render_template('generate_quiz.html')

# Quiz preview route
@app.route('/preview/<int:quiz_id>', methods=['GET'])
def preview_quiz(quiz_id=None):
    if quiz_id:
        # Get quiz from database
        quiz = Quiz.query.get_or_404(quiz_id)
        quiz_data = json.loads(quiz.content)
        quiz_title = quiz.title
        quiz_type = quiz.quiz_type
    else:
        # Get quiz from session (guest mode)
        quiz_data = session.get('quiz_data')
        quiz_title = session.get('quiz_title', 'Untitled Quiz')
        quiz_type = session.get('quiz_type', 'Mixed')
        
        if not quiz_data:
            flash('No quiz data found. Please generate a new quiz.', 'error')
            return redirect(url_for('generate'))
    
    return render_template('preview_quiz.html', 
                           quiz_data=quiz_data, 
                           quiz_title=quiz_title, 
                           quiz_type=quiz_type,
                           quiz_id=quiz_id)

# Download quiz as PDF
@app.route('/download/<int:quiz_id>', methods=['GET'])
def download_quiz(quiz_id=None):
    if quiz_id:
        # Get quiz from database
        quiz = Quiz.query.get_or_404(quiz_id)
        quiz_data = json.loads(quiz.content)
        quiz_title = quiz.title
    else:
        # Get quiz from session (guest mode)
        quiz_data = session.get('quiz_data')
        quiz_title = session.get('quiz_title', 'Untitled Quiz')
        
        if not quiz_data:
            flash('No quiz data found. Please generate a new quiz.', 'error')
            return redirect(url_for('generate'))
    
    try:
        # Create PDF
        pdf_buffer = create_quiz_pdf(quiz_data, quiz_title)
        
        # Return PDF as download
        return send_file(
            io.BytesIO(pdf_buffer.getvalue()),
            mimetype='application/pdf',
            as_attachment=True,
            download_name=f"{quiz_title.replace(' ', '_')}.pdf"
        )
    except Exception as e:
        flash(f'Error generating PDF: {str(e)}', 'error')
        return redirect(url_for('preview_quiz', quiz_id=quiz_id))

# Save quiz edits route
@app.route('/save-edits', methods=['POST'])
def save_quiz_edits():
    quiz_id = request.args.get('quiz_id', None)
    quiz_title = request.form.get('quiz_title', 'Untitled Quiz')
    
    try:
        # Collect all form data to reconstruct the quiz
        new_quiz_data = []
        
        # Determine how many questions we're dealing with
        question_count = 0
        for key in request.form.keys():
            if key.startswith('question_'):
                question_index = int(key.split('_')[1])
                question_count = max(question_count, question_index + 1)
        
        # Process each question
        for i in range(question_count):
            question_text = request.form.get(f'question_{i}', '')
            answer_text = request.form.get(f'answer_{i}', '')
            explanation_text = request.form.get(f'explanation_{i}', '')
            question_type = request.form.get(f'question_type_{i}', '')
            
            # Skip empty questions
            if not question_text:
                continue
                
            question_data = {
                'question': question_text,
                'answer': answer_text
            }
            
            # Add question type if available
            if question_type:
                question_data['question_type'] = question_type
                
            # Add explanation if available
            if explanation_text:
                question_data['explanation'] = explanation_text
                
            # Check for options (multiple choice questions)
            options = []
            
            # Collect all option keys for this question
            option_keys = [key for key in request.form.keys() if key.startswith(f'option_{i}_')]
            
            # Extract the option values
            for key in sorted(option_keys, key=lambda k: int(k.split('_')[-1]) if k.split('_')[-1].isdigit() else 0):
                option_text = request.form.get(key, '')
                if option_text:
                    options.append(option_text)
                    
            if options:
                question_data['options'] = options
                
            new_quiz_data.append(question_data)
            
        # Update quiz in database or session
        if quiz_id is not None and str(quiz_id).isdigit():
            quiz_id_int = int(quiz_id)
            # Update existing quiz in database
            if current_user.is_authenticated:
                quiz = Quiz.query.get_or_404(quiz_id_int)
                
                # Check if the quiz belongs to the current user
                if quiz.user_id != current_user.id:
                    flash('You do not have permission to edit this quiz.', 'error')
                    return redirect(url_for('dashboard'))
                
                quiz.title = quiz_title
                quiz.content = json.dumps(new_quiz_data)
                quiz.question_count = len(new_quiz_data)
                db.session.commit()
                flash('Quiz updated successfully!', 'success')
            else:
                flash('You need to be logged in to edit saved quizzes.', 'error')
                return redirect(url_for('login'))
            
            return redirect(url_for('preview_quiz', quiz_id=quiz_id_int))
        else:
            # Update quiz in session for guest users
            session['quiz_data'] = new_quiz_data
            session['quiz_title'] = quiz_title
            flash('Quiz updated successfully!', 'success')
            
            return redirect(url_for('preview_quiz'))
        
    except Exception as e:
        flash(f'Error saving quiz: {str(e)}', 'error')
        return redirect(url_for('preview_quiz', quiz_id=quiz_id if quiz_id and quiz_id.isdigit() else None))

# Delete quiz
@app.route('/delete/<int:quiz_id>', methods=['POST'])
@login_required
def delete_quiz(quiz_id):
    quiz = Quiz.query.get_or_404(quiz_id)
    
    # Check if the quiz belongs to the current user
    if quiz.user_id != current_user.id:
        flash('You do not have permission to delete this quiz.', 'error')
        return redirect(url_for('dashboard'))
    
    try:
        db.session.delete(quiz)
        db.session.commit()
        flash('Quiz deleted successfully.', 'success')
    except Exception as e:
        db.session.rollback()
        flash(f'Error deleting quiz: {str(e)}', 'error')
    
    return redirect(url_for('dashboard'))

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)
