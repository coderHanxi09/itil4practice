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
# MODE SWITCHER (🔥 新增：统一的模式切换器，负责读取进度)
# =========================================================
def switch_mode(target_mode):
    """切换模式并安全加载该模式的进度"""
    st.session_state.mode = target_mode
    
    # 核心：根据不同模式获取当前题库长度，防止历史 index 超出新题库的范围
    if target_mode == "bank":
        max_len = len(questions)
    elif target_mode == "wrong":
        max_len = len(st.session_state.wrong_questions)
    else: # exam
        max_len = len(st.session_state.quiz)

    # 从数据库读取进度
    saved_index = load_progress(f"{target_mode}_index", default=0)
    
    # 如果读取的进度越界了，重置为 0
    if saved_index >= max_len or max_len == 0:
        st.session_state.index = 0
    else:
        st.session_state.index = saved_index
        
    reset_state()

def reset_state():
    st.session_state.submitted = False
    st.session_state.selected = None
    st.session_state.feedback = None

# =========================================================
# INIT STATE (🔥 优化：首次进入时从数据库加载历史 Mode 和 Index)
# =========================================================
if "mode" not in st.session_state:
    # 首次启动，恢复上一次的 Mode，默认是 bank
    saved_mode = load_progress("current_mode", default="bank")
    st.session_state.wrong_questions = load_wrong()
    
    # 初始化其余状态
    st.session_state.quiz = []
    st.session_state.score = 0
    reset_state()
    
    # 触发一次模式切换以正确读取该模式的 index
    switch_mode(saved_mode)

if "wrong_questions" not in st.session_state:
    st.session_state.wrong_questions = load_wrong()

# =========================================================
# MODE STARTERS
# =========================================================
def start_exam():
    st.session_state.quiz = random.sample(questions, min(40, len(questions)))
    st.session_state.score = 0
    # 考试模式属于全新生成，直接重置进度为 0 并保存
    save_progress("exam_index", 0)
    switch_mode("exam")
    st.rerun()

def start_wrong():
    wrong = st.session_state.wrong_questions
    if not wrong:
        st.warning("No wrong questions 🎉")
        return
    
    # 错题模式我们通常也随机，如果你想记住错题模式的进度，可以用 switch_mode
    st.session_state.quiz = random.sample(wrong, len(wrong))
    st.session_state.score = 0
    switch_mode("wrong")
    st.rerun()

# =========================================================
# SIDEBAR
# =========================================================
st.sidebar.title("🎓 Navigation")

if st.sidebar.button("📚 Bank Mode"):
    # 记住当前模式
    save_progress("current_mode", "bank")
    switch_mode("bank")
    st.rerun()

if st.sidebar.button("📝 Exam Mode"):
    save_progress("current_mode", "exam")
    start_exam()

if st.sidebar.button("❌ Wrong Mode"):
    save_progress("current_mode", "wrong")
    start_wrong()

st.sidebar.divider()

if st.sidebar.button("🧹 Clear Wrong Questions"):
    st.session_state.wrong_questions = []
    clear_wrong()
    # 错题清空后，如果还在错题模式，强行切回 bank
    if st.session_state.mode == "wrong":
        save_progress("current_mode", "bank")
        switch_mode("bank")
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

# 兜底保护：确保 index 绝不越界
if st.session_state.index >= len(source):
    st.session_state.index = 0

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

        if st.session_state.index >= len(source):
            st.session_state.index = 0

        # ⭐ 核心修复：点击 Next 时，立刻写入数据库
        save_progress(f"{st.session_state.mode}_index", st.session_state.index)
        reset_state()
        st.rerun()