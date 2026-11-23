"""Marks page: the student's scores for every quiz."""
import pandas as pd
import streamlit as st

from core import ui
from db import queries

st.set_page_config(page_title="Marks · TutorLens", page_icon="📊", layout="wide")
ui.init()
student_id = ui.sidebar_student()

student_name = st.session_state.get("student_name", "Student")
ui.page_heading("here's your learning progress!")
st.caption("Your personal learning performance")

if student_id is None:
    st.warning("Please enter your name on the Home page first.")
    st.stop()

summary = queries.get_quiz_summary(student_id)
if not summary:
    st.info("No marks yet. Take a quiz on the **Quiz** page.")
    st.stop()

total_points = sum(row["points"] for row in summary)
total_max = sum(row["max_points"] for row in summary)
col1, col2, col3 = st.columns(3)
col1.metric("Overall score", f"{(100 * total_points / total_max) if total_max else 0:.0f}%")
col2.metric("Quizzes taken", len(summary))
col3.metric("Questions answered", sum(row["questions"] for row in summary))

st.subheader("Quizzes")
quiz_table = pd.DataFrame(
    {
        "Quiz": [f"Quiz {row['quiz_no']}" for row in summary],
        "PDF": [row["pdf"] for row in summary],
        "Score": [f"{row['points']} / {row['max_points']}" for row in summary],
        "Percent": [
            f"{(100 * row['points'] / row['max_points']) if row['max_points'] else 0:.0f}%"
            for row in summary
        ],
        "Date": [row["date"].strftime("%Y-%m-%d %H:%M") if row["date"] else "" for row in summary],
    }
)
st.dataframe(quiz_table, hide_index=True)

st.subheader("Every answer")
attempts = queries.get_attempts(student_id)
detail = pd.DataFrame(
    {
        "Quiz": [f"Quiz {a['quiz_no']}" for a in attempts],
        "Type": [a["type"] for a in attempts],
        "Question": [a["question"] for a in attempts],
        "Your answer": [a["answer_text"] for a in attempts],
        "Points": [f"{a['points']} / {a['max_points']}" for a in attempts],
        "Feedback": [a["feedback"] for a in attempts],
    }
)
st.dataframe(detail, hide_index=True)

st.download_button(
    "Download my marks (CSV)",
    data=detail.to_csv(index=False).encode("utf-8-sig"),
    file_name="tutorlens_marks.csv",
    mime="text/csv",
)