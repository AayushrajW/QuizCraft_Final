
# 📚 QuizCraft AI — Local Python Mini Project

QuizCraft is a Flask-based AI-powered quiz generator that lets you upload text, documents, or images and instantly generate customizable quizzes. It supports editing, previewing, and downloading quizzes as PDFs — all running **locally in VS Code**, for desktop browsers only.

---

## 🚀 Features

- ✨ Generate quizzes using **Google Gemini 1.5 Pro**
- 🧠 Input formats: PDF, DOCX, TXT, CSV, text, or image (via Tesseract OCR)
- 🎴 Quiz types: Multiple Choice, True/False, Fill in the Blanks, Short Answer, Mixed
- 📝 Edit your quiz before downloading
- 📄 Export as clean PDF (questions + answers)
- 👥 Login/Register system with quiz history
- 💾 SQLite local database support
- 🧠 Math expressions supported as clean Unicode (optional MathJax for frontend)

---

## ⚙️ Tech Stack

- **Python 3.10.11**
- Flask + SQLAlchemy + Flask-WTF
- Google Generative AI (Gemini API)
- Tesseract OCR
- Tailwind CSS
- reportlab, PyPDF2

---

## 🖥️ How to Run Locally (VS Code)

### 1. Clone the Repo

```bash
git clone https://github.com/yourusername/quizcraft.git
cd quizcraft
```

### 2. Create & Activate Virtual Environment (Python 3.10.11)

```bash
py -3.10 -m venv venv
venv\Scripts\activate  # On Windows
```

### 3. Install Dependencies

```bash
pip install -r requirements.txt
```

### 4. Create `.env` File

Create a `.env` file in the root folder with:

```env
SESSION_SECRET=your_secret_key
DATABASE_URL=sqlite:///quizcraft.db
GEMINI_API_KEY=your_google_gemini_api_key
```

> You can rename `.env.example` to `.env` and fill in your values.

### 5. Run the App

```bash
python main.py
```

Visit [http://127.0.0.1:5000](http://127.0.0.1:5000)

---

## 📁 Project Structure

```
QuizCraftAI/
├── main.py
├── app.py
├── templates/
├── static/
├── utils/
├── database/
├── requirements.txt
├── .env.example
└── README.md
```

---

## ✅ Notes

- This app is built for **local desktop use only**
- Python version **must be 3.10.11**
- Math formatting (like `H₂O`, `CO₂`) is supported using UTF-8 characters
- For advanced math, you can optionally enable **MathJax** in the frontend

---

## 🙌 Author

Created with ❤️ by Aayushraj Wadke  
For use as a local Python mini project — open source, customizable, and lightweight.
#   Q u i z C r a f t _ F i n a l  
 #   Q u i z C r a f t _ F i n a l  
 