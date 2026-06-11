import streamlit as st
import sqlite3
import json
import random

st.set_page_config(
    page_title="ITIL Exam System",
    page_icon="🎓",
    layout="wide"
)

# =========================================================
# DATABASE
# =========================================================
DB = "quiz.db"

def get_conn():
    return sqlite3.connect(DB, check_same_thread=False)

def init_db():
    conn = get_conn()
    c = conn.cursor()

    c.execute("""
    CREATE TABLE IF NOT EXISTS wrong_questions (
        id TEXT PRIMARY KEY,
        data TEXT
    )
    """)

    c.execute("""
    CREATE TABLE IF NOT EXISTS progress (
        key TEXT PRIMARY KEY,
        value TEXT
    )
    """)

    conn.commit()
    conn.close()

init_db()

# ================= DB HELPERS =================
def save_progress(key, value):
    conn = get_conn()
    c = conn.cursor()
    c.execute("""
        INSERT OR REPLACE INTO progress (key, value)
        VALUES (?, ?)
    """, (key, json.dumps(value)))
    conn.commit()
    conn.close()

def load_progress(key, default=0):
    conn = get_conn()
    c = conn.cursor()
    c.execute("SELECT value FROM progress WHERE key=?", (key,))
    row = c.fetchone()
    conn.close()

    if row:
        return json.loads(row[0])
    return default

def save_wrong(q):
    conn = get_conn()
    c = conn.cursor()
    c.execute("""
        INSERT OR REPLACE INTO wrong_questions (id, data)
        VALUES (?, ?)
    """, (str(q["id"]), json.dumps(q)))
    conn.commit()
    conn.close()

def load_wrong():
    conn = get_conn()
    c = conn.cursor()
    c.execute("SELECT data FROM wrong_questions")
    rows = c.fetchall()
    conn.close()
    return [json.loads(r[0]) for r in rows]

def clear_wrong():
    conn = get_conn()
    c = conn.cursor()
    c.execute("DELETE FROM wrong_questions")
    conn.commit()
    conn.close()

# =========================================================
# LOAD QUESTIONS
# =========================================================
@st.cache_data
def load_questions():
    with open("questions.json", "r", encoding="utf-8") as f:
        return json.load(f)

questions = load_questions()

# =========================================================
# INIT STATE (SAFE)
# =========================================================
if "mode" not in st.session_state:
    st.session_state.mode = "bank"   # ⭐ 默认 Bank

if "wrong_questions" not in st.session_state:
    st.session_state.wrong_questions = load_wrong()

if "quiz" not in st.session_state:
    st.session_state.quiz = []

if "index" not in st.session_state:
    st.session_state.index = 0

if "submitted" not in st.session_state:
    st.session_state.submitted = False

if "selected" not in st.session_state:
    st.session_state.selected = None

if "feedback" not in st.session_state:
    st.session_state.feedback = None

if "score" not in st.session_state:
    st.session_state.score = 0

# =========================================================
# MODE STARTERS
# =========================================================
def start_exam():
    st.session_state.quiz = random.sample(questions, min(40, len(questions)))
    st.session_state.index = 0
    st.session_state.score = 0

    reset_state()
    st.session_state.mode = "exam"
    st.rerun()

def start_wrong():
    wrong = st.session_state.wrong_questions

    if not wrong:
        st.warning("No wrong questions 🎉")
        return

    st.session_state.quiz = random.sample(wrong, len(wrong))
    st.session_state.index = 0
    st.session_state.score = 0

    reset_state()
    st.session_state.mode = "wrong"
    st.rerun()

def reset_state():
    st.session_state.submitted = False
    st.session_state.selected = None
    st.session_state.feedback = None

# =========================================================
# SIDEBAR
# =========================================================
st.sidebar.title("🎓 Navigation")

if st.sidebar.button("📚 Bank Mode"):
    st.session_state.mode = "bank"
    st.rerun()

if st.sidebar.button("📝 Exam Mode"):
    start_exam()

if st.sidebar.button("❌ Wrong Mode"):
    start_wrong()

st.sidebar.divider()

if st.sidebar.button("🧹 Clear Wrong Questions"):
    st.session_state.wrong_questions = []
    clear_wrong()
    st.rerun()

st.sidebar.write(f"Wrong Questions: {len(st.session_state.wrong_questions)}")

# =========================================================
# GET CURRENT QUESTION SOURCE
# =========================================================
def get_source():
    if st.session_state.mode in ["exam", "wrong"]:
        return st.session_state.quiz
    return questions

source = get_source()

# 防止空
if len(source) == 0:
    st.warning("No questions available")
    st.stop()

q = source[st.session_state.index]

# =========================================================
# TITLE
# =========================================================
if st.session_state.mode == "exam":
    st.title("📝 Exam Mode")
elif st.session_state.mode == "wrong":
    st.title("❌ Wrong Mode")
else:
    st.title("📚 Question Bank")

# =========================================================
# PROGRESS
# =========================================================
st.progress((st.session_state.index + 1) / len(source))

st.write(q["question"])

# =========================================================
# OPTIONS
# =========================================================
if not st.session_state.submitted:

    choice = st.radio(
        "Choose answer",
        list(q["options"].keys()),
        format_func=lambda x: f"{x}. {q['options'][x]}",
        key=f"{st.session_state.mode}_{q['id']}"
    )

    st.session_state.selected = choice

else:
    choice = st.session_state.selected

# =========================================================
# SUBMIT (UNIFIED LOGIC)
# =========================================================
if not st.session_state.submitted:

    if st.button("Submit"):

        st.session_state.submitted = True

        correct = q["answer"]
        user_choice = choice

        if user_choice == correct:
            st.session_state.feedback = ("success", user_choice, correct)
            if st.session_state.mode == "exam":
                st.session_state.score += 1
        else:
            st.session_state.feedback = ("error", user_choice, correct)

            # save wrong
            if q not in st.session_state.wrong_questions:
                st.session_state.wrong_questions.append(q)
                save_wrong(q)

        st.rerun()

# =========================================================
# FEEDBACK UI
# =========================================================
if st.session_state.feedback:

    status, user_choice, correct = st.session_state.feedback

    if status == "success":
        st.success("🎯 Correct!")
    else:
        st.error("❌ Wrong!")

    st.markdown(f"""
    <div style="
        padding:14px;
        border-radius:10px;
        background:#f8f9fa;
        border:1px solid #ddd;">
        <b>Your Answer:</b> {user_choice}. {q['options'][user_choice]} <br><br>
        <b>Correct Answer:</b> {correct}. {q['options'][correct]}
    </div>
    """, unsafe_allow_html=True)

# =========================================================
# NEXT BUTTON (UNIFIED)
# =========================================================
if st.session_state.submitted:

    if st.button("Next"):

        st.session_state.index += 1

        save_progress(f"{st.session_state.mode}_index", st.session_state.index)

        reset_state()

        if st.session_state.index >= len(source):
            st.session_state.index = 0

        st.rerun()