🎓 ITIL Exam System

A lightweight ITIL practice and exam application built with Streamlit and SQLite. The app provides multiple learning modes and automatically saves your progress, making it easy to study for the ITIL Foundation exam.

Features

📚 Question Bank

* Browse the entire question database.
* Resume from where you left off after restarting the app.

📝 Exam Mode

* Generates a random 40-question mock exam.
* Tracks your score during the session.

❌ Wrong Question Mode

* Automatically saves incorrectly answered questions.
* Review and practice only your mistakes.

💾 Progress Persistence

* Saves your current mode and question index.
* Automatically restores your previous session.

🗂 Wrong Question Management

* Stores incorrect answers in a local SQLite database.
* Clear the wrong question collection at any time.

⸻

Project Structure

project/
│
├── app.py              # Streamlit application
├── questions.json      # Question bank
├── quiz.db             # SQLite database (auto-generated)
├── requirements.txt
└── README.md


🚀 ITIL Exam System — Setup & Run Guide

Cross-platform guide for Windows / macOS / Linux

⸻

📦 1. Install Python

Windows

Download Python:
https://www.python.org/downloads/

⚠️ Important:

* Check “Add Python to PATH” during installation

⸻

macOS

brew install python

⸻

Linux

sudo apt update
sudo apt install python3 python3-pip python3-venv

⸻

📁 2. Clone repository

git clone https://github.com/coderHanxi09/itil4practice
cd itil4practice

⸻

🧪 3. Create virtual environment

macOS / Linux

python3 -m venv venv
source venv/bin/activate

Windows (CMD)

python -m venv venv
venv\Scripts\activate

Windows (PowerShell)

python -m venv venv
venv\Scripts\Activate.ps1

⸻

📥 4. Install dependencies

python -m pip install streamlit

If requirements.txt exists:

python -m pip install -r requirements.txt

⸻

▶️ 5. Run the app

streamlit run app.py

Then open:

http://localhost:8501

⸻

💾 6. Data storage

The app automatically creates:

quiz.db

It stores:

* Progress
* Exam mode state
* Wrong answers

To reset all data:

macOS / Linux

rm quiz.db

Windows

del quiz.db

⸻

⚠️ Important pip rule (all systems)

If pip doesn’t work, always use:

python -m pip install <package>
