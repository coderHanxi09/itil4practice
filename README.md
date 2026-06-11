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

⸻

Installation

1. Clone the repository

git clone https://github.com/YOUR_USERNAME/YOUR_REPOSITORY.git
cd YOUR_REPOSITORY

Replace YOUR_USERNAME and YOUR_REPOSITORY with your GitHub information.

2. Create a virtual environment (recommended)

Windows

python -m venv venv
venv\Scripts\activate

macOS / Linux

python3 -m venv venv
source venv/bin/activate

⸻

3. Install dependencies

pip install -r requirements.txt

If you don’t have a requirements.txt, install manually:

pip install streamlit

⸻

4. Prepare the question bank

Place your question file in the project directory:

questions.json

The expected format is:

[
  {
    "id": 1,
    "question": "...",
    "options": {
      "A": "...",
      "B": "...",
      "C": "...",
      "D": "..."
    },
    "answer": "A"
  }
]

⸻

Running the App

Start the application:

streamlit run app.py

Streamlit will automatically open the application in your browser.

If it doesn’t, open:

http://localhost:8501

⸻

Usage

📚 Bank Mode

Study all questions sequentially with progress automatically saved.

📝 Exam Mode

Take a random 40-question practice exam.

❌ Wrong Mode

Review questions you’ve answered incorrectly.

🧹 Clear Wrong Questions

Reset your wrong-question collection.

⸻

Data Storage

The application automatically creates a local SQLite database:

quiz.db

It stores:

* Current study progress
* Last active mode
* Wrong questions

You can delete quiz.db at any time to reset all local data.

⸻

Technologies

* Python
* Streamlit
* SQLite
* JSON

⸻

Contributing

Feel free to fork this repository, open issues, or submit pull requests for improvements.

⸻

License

This project is intended for educational and personal learning purposes.
