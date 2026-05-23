⚡ Offline Exam Assistant
An offline AI-powered exam assistant for JEE and NEET students. No internet required. No smartphone distractions.

Offline Exam Assistant
(<Screenshot 2026-05-19 000749.png>) (<Screenshot 2026-05-23 141647.png>) (<Screenshot 2026-05-23 202425.png>)

What It Does
📷 Captures printed MCQ questions via image upload
🔍 Extracts text using EasyOCR
🗄️ Searches a verified database of past paper solutions first
🤖 Falls back to local Llama 3.2 AI when no match found
✅ Displays correct answer with detailed explanation
🌐 Runs completely offline via local web interface
Why It Exists
JEE and NEET students use smartphones "for studying" but end up distracted. This device gives them everything they need during self-study hours without internet access — removing the reason to pick up the phone.

Architecture
Image → EasyOCR → Question Text ↓ Search Verified Database ↓ Match Found? YES → Return verified answer + explanation NO → Llama 3.2 generates explanation ↓ Display in Web Interface

Tech Stack
Component	Technology
OCR	EasyOCR
AI Model	Llama 3.2 (via Ollama)
Embeddings	sentence-transformers (MiniLM)
Database	SQLite
Backend	Flask
Frontend	HTML, CSS, JavaScript
Papers Folder
Add your exam PDF files here before running db_builder.py

Naming Convention
NEET_2025.pdf
JEE_MAIN_2023.pdf
NEET_2024.pdf
Supported Formats
Any MCQ exam paper with questions, options, answers and solutions.

Current Database
NEET 2025 — 179 questions
JEE Main 2023 — 77 questions
Total — 256 verified Q&A with explanations
Setup Instructions
Note on Requirements
Core dependencies are listed in requirements.txt. PyTorch installation varies by system. If pip install fails for torch, visit https://pytorch.org and install the CPU version for your OS manually first.

Prerequisites
Python 3.10+
Ollama installed
Llama 3.2 model pulled
Installation
# Clone the repository
git clone https://github.com/YOUR_USERNAME/offline-exam-assistant.git
cd offline-exam-assistant

# Install dependencies
pip install -r requirements.txt

# Pull the AI model
ollama pull llama3.2

# Build the question database
# Add your exam PDFs to the papers/ folder first
python db_builder.py

# Run the application
python app.py
Open http://localhost:5000 in your browser.

Project Structure
offline-exam-assistant/ ├── app.py # Flask backend ├── ocr.py # EasyOCR pipeline ├── ai_engine.py # Llama 3.2 connection ├── retriever.py # Semantic search ├── db_builder.py # Database builder from PDFs ├── requirements.txt ├── templates/ │ └── index.html # Web interface ├── static/ │ ├── style.css │ └── script.js └── papers/ # Add your exam PDFs here └── README.md

Roadmap
 Add more exam papers (NEET 2024, 2023, JEE Advanced)
 Support handwritten questions
 Raspberry Pi hardware deployment
 Voice output
 Multilingual OCR
 UPSC, GATE, State board support
Open For
Freelance projects
Collaboration
Adding new exam databases on demand
Contact
Built by Shivam Choudhary 📧 beginnershivam28@gmail.com 🔗 linkedin.com/in/choudharyshivam28/
