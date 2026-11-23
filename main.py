
"""TutorLens - Student Home Dashboard."""

import html
import streamlit as st

from core import config, llm_client, ui


# ============================================================
# 1. PAGE CONFIGURATION
# ============================================================

st.set_page_config(
    page_title="TutorLens | Home",
    page_icon="🎓",
    layout="wide",
    initial_sidebar_state="expanded",
)

ui.init()


# ============================================================
# 2. STUDENT SESSION
# ============================================================

if "student_name_input" not in st.session_state:
    st.session_state["student_name_input"] = st.session_state.get(
        "student_name", ""
    )


# ============================================================
# 3. CUSTOM CSS
# ============================================================

st.html("""
<style>

    .block-container {
        max-width: 1250px;
        padding-top: 2rem;
        padding-bottom: 3rem;
    }

    /* Main welcome banner */
    .hero {
        background: linear-gradient(
            120deg,
            #172c50,
            #344c91,
            #6045a5
        );
        padding: 40px;
        border-radius: 20px;
        margin: 20px 0 30px 0;
        color: white;
    }

    .hero h1 {
        color: white;
        font-size: 36px;
        font-weight: 750;
        margin-bottom: 12px;
    }

    .hero p {
        color: #e0e7ff;
        font-size: 17px;
        margin-bottom: 0;
    }

    .hero-label {
        font-size: 14px;
        letter-spacing: 2px;
        color: #d5dcff;
        font-weight: 600;
        margin-bottom: 12px;
    }

    /* Section headings */
    .section-heading {
        font-size: 25px;
        font-weight: 700;
        margin-top: 30px;
        margin-bottom: 18px;
    }

    /* Feature cards */
    .feature-card {
        background: rgba(100, 120, 160, 0.09);
        border: 1px solid rgba(150, 165, 200, 0.22);
        border-radius: 16px;
        padding: 25px;
        min-height: 175px;
        margin-bottom: 12px;
    }

    .feature-card h3 {
        font-size: 21px;
        color: #f1f3f9;
        margin-bottom: 12px;
    }

    .feature-card p {
        font-size: 15px;
        color: #b8bdc9;
        line-height: 1.6;
    }

    .feature-icon {
        font-size: 32px;
        margin-bottom: 12px;
    }

    /* Student profile */
    .profile-description {
        color: #aab2c3;
        font-size: 14px;
        margin-bottom: 15px;
    }

    /* Footer */
    .footer {
        text-align: center;
        color: #858b99;
        font-size: 13px;
        padding: 30px 0 10px 0;
    }

    /* Buttons */
    div.stButton > button {
        border-radius: 10px;
        min-height: 42px;
        font-weight: 600;
    }

</style>
""")


# ============================================================
# 4. TOP HEADER
# ============================================================

st.html("""
<div style="margin-bottom:25px;">

    <div style="
        font-size:14px;
        color:#929bb0;
        letter-spacing:2px;
        font-weight:600;
    ">
        YOUR PERSONAL AI LEARNING PLATFORM
    </div>

    <h1 style="
        font-size:36px;
        margin-top:8px;
        margin-bottom:8px;
        font-weight:800;
    ">
        🎓 TutorLens
    </h1>

    <p style="
        color:#aab2c3;
        font-size:16px;
    ">
        Learn smarter. Practice better. Track your progress.
    </p>

</div>
""")


# ============================================================
# 5. GET STUDENT NAME
# ============================================================

student_name = st.session_state.get(
    "student_name", ""
).strip()

display_name = html.escape(student_name) if student_name else "Student"


# ============================================================
# 6. PERSONALIZED WELCOME BANNER
# ============================================================

if student_name:
    welcome_message = f"Hello, {display_name}!"
else:
    welcome_message = "Welcome to TutorLens!"

st.html(f"""
<div class="hero">

    <div class="hero-label">
        WELCOME TO TUTORLENS
    </div>

    <h1>
        👋 {welcome_message}
    </h1>

    <p>
        What would you like to learn today?
        Your personal AI teacher is ready to help.
    </p>

</div>
""")


# ============================================================
# 7. OLLAMA STATUS
# ============================================================

st.html("""
<div class="section-heading">
    🤖 AI Assistant Status
</div>
""")

try:
    ok, message = llm_client.check_ollama()

    if ok:
        st.success(message)
    else:
        st.warning(message)

except Exception as error:
    st.warning(f"Could not check Ollama status: {error}")


# ============================================================
# 8. LEARNING SPACE
# ============================================================

st.html("""
<div class="section-heading">
    🚀 Your Learning Space
</div>
""")

col1, col2 = st.columns(2)


# ---------------- UPLOAD MATERIALS ----------------

with col1:

    st.html("""
    <div class="feature-card">

        <div class="feature-icon">📤</div>

        <h3>Upload Materials</h3>

        <p>
            Upload your course PDFs, lecture notes,
            and learning materials.
        </p>

    </div>
    """)

    st.page_link(
        "pages/1_Upload.py",
        label="Upload a PDF",
        icon="📄",
        use_container_width=True,
    )


# ---------------- LEARN WITH AI ----------------

with col1:

    st.html("""
    <div class="feature-card">

        <div class="feature-icon">📖</div>

        <h3>Learn with AI</h3>

        <p>
            Ask questions and get explanations
            based on your uploaded PDFs.
        </p>

    </div>
    """)

    st.page_link(
        "pages/2_Learn.py",
        label="Start Learning",
        icon="📚",
        use_container_width=True,
    )


# ---------------- QUIZ ----------------

with col2:

    st.html("""
    <div class="feature-card">

        <div class="feature-icon">📝</div>

        <h3>Take a Quiz</h3>

        <p>
            Test your knowledge with AI-generated
            questions and automatic grading.
        </p>

    </div>
    """)

    st.page_link(
        "pages/3_Quiz.py",
        label="Start Quiz",
        icon="✏️",
        use_container_width=True,
    )


# ---------------- MARKS ----------------

with col2:

    st.html("""
    <div class="feature-card">

        <div class="feature-icon">📊</div>

        <h3>My Marks</h3>

        <p>
            Check your quiz scores, review answers,
            and monitor your learning progress.
        </p>

    </div>
    """)

    st.page_link(
        "pages/4_Marks.py",
        label="View My Marks",
        icon="📈",
        use_container_width=True,
    )


# ============================================================
# 9. HOW TUTORLENS WORKS
# ============================================================

st.divider()

st.subheader("💡 How TutorLens Works")

step1, step2, step3 = st.columns(3)

with step1:
    st.markdown("### 01 · Upload")
    st.caption("Add your course PDF materials.")

with step2:
    st.markdown("### 02 · Learn")
    st.caption("Ask the AI teacher about your materials.")

with step3:
    st.markdown("### 03 · Practice")
    st.caption("Take quizzes and track your marks.")


# ============================================================
# 10. STUDENT PROFILE AT THE BOTTOM
# ============================================================

st.divider()

st.subheader("👤 Student Profile")

st.markdown(
    '<p class="profile-description">'
    'Manage your student name here. '
    'Your quiz results will be saved under this profile.'
    '</p>',
    unsafe_allow_html=True,
)

with st.container(border=True):

    student_name_input = st.text_input(
        "Your name",
        placeholder="Enter your name...",
        key="student_name_input",
    )

    student_name = student_name_input.strip()

    st.session_state["student_name"] = student_name

    if student_name:

        student_id = ui.sidebar_student()

        st.success(
            f"Welcome, {student_name}! "
            "Your student profile is ready."
        )

    else:

        st.session_state.pop("student_id", None)

        st.info(
            "Enter your name to personalize "
            "your learning experience."
        )


# ============================================================
# 11. FOOTER
# ============================================================

st.html("""
<div class="footer">

    TutorLens · Powered by Ollama

    <br><br>

    Your AI Learning Companion 🎓

</div>
""")
