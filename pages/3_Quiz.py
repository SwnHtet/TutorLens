"""Quiz page: generate questions, answer them, get AI marks and feedback."""
import streamlit as st

from core import grader, llm_client, question_gen, ui, vector_store
from db import queries
from models.schemas import Question

st.set_page_config(page_title="Quiz · TutorLens", page_icon="📝", layout="wide")
ui.init()

doc = ui.sidebar_document()
student_id = ui.sidebar_student()

ui.page_heading("are you ready for a quiz?")

if doc is None:
    st.info("No PDF yet. Go to the **Upload** page first.")
    st.stop()
if student_id is None:
    st.warning("Please enter your name on the Home page first.")
    st.stop()

ok, message = llm_client.check_ollama()
if not ok:
    st.error(message)
    st.stop()

quiz = st.session_state.get("quiz")
if quiz and quiz["doc_id"] != doc["id"]:
    quiz = None  # the student switched to another PDF
    st.session_state.pop("quiz", None)

# ---- 1. settings and generation -----------------------------------------
if quiz is None:
    st.subheader(f"New quiz from “{doc['title']}”")
    sections = ["Whole PDF"] + vector_store.get_sections(doc["id"])
    col1, col2 = st.columns(2)
    section = col1.selectbox("Part of the PDF", sections)
    difficulty = col2.selectbox("Difficulty", ["mixed", "easy", "medium", "hard"])
    n = col1.slider("Number of questions", 3, 8, 5)
    types = col2.multiselect(
        "Question types",
        ["mcq", "short", "exercise"],
        default=["mcq", "short"],
        format_func={"mcq": "Multiple choice", "short": "Short answer", "exercise": "Exercise"}.get,
    )
    if st.button("Generate quiz", type="primary", disabled=not types):
        with st.spinner("The teacher is writing your questions... (a local model can take a minute)"):
            try:
                questions = question_gen.generate_quiz(
                    doc["id"], n=n, difficulty=difficulty, types=types,
                    section=None if section == "Whole PDF" else section,
                )
                quiz_no = queries.next_quiz_no(doc["id"])
                ids = queries.save_questions(doc["id"], quiz_no, questions)
            except Exception as error:
                st.error(f"Could not generate the quiz: {error}")
                st.stop()
        st.session_state["quiz"] = {
            "doc_id": doc["id"],
            "quiz_no": quiz_no,
            "items": list(zip(ids, [q.model_dump() for q in questions])),
            "results": None,
        }
        st.rerun()
    st.stop()

items = [(qid, Question(**data)) for qid, data in quiz["items"]]

# ---- 2. answering ---------------------------------------------------------
if quiz["results"] is None:
    st.subheader(f"Quiz {quiz['quiz_no']} · {len(items)} questions")
    with st.form("quiz_form"):
        for number, (qid, q) in enumerate(items, start=1):
            st.markdown(f"**Q{number}. {q.question}**")
            st.caption(f"{q.type} · {q.difficulty} · {q.topic}")
            if q.type == "mcq":
                st.radio("Your answer", q.options, index=None, key=f"answer_{qid}", label_visibility="collapsed")
            else:
                st.text_area("Your answer", key=f"answer_{qid}", label_visibility="collapsed", height=100)
            st.divider()
        submitted = st.form_submit_button("Submit answers", type="primary")

    if submitted:
        results = []
        with st.spinner("Marking your answers..."):
            try:
                for qid, q in items:
                    answer = st.session_state.get(f"answer_{qid}")
                    grade = grader.grade(q, answer)
                    queries.save_attempt(student_id, qid, answer, grade)
                    results.append({"answer": answer, "grade": grade.model_dump()})
            except Exception as error:
                st.error(f"Marking failed: {error}")
                st.stop()
        quiz["results"] = results
        st.rerun()
    st.stop()

# ---- 3. results -----------------------------------------------------------
total = sum(r["grade"]["points"] for r in quiz["results"])
maximum = sum(r["grade"]["max_points"] for r in quiz["results"])
st.subheader(f"Quiz {quiz['quiz_no']} result")
st.metric("Your score", f"{total} / {maximum}", f"{(100 * total / maximum) if maximum else 0:.0f}%", delta_color="off")

for number, ((qid, q), result) in enumerate(zip(items, quiz["results"]), start=1):
    grade = result["grade"]
    with st.container(border=True):
        st.markdown(f"**Q{number}. {q.question}**  ·  {grade['points']} / {grade['max_points']}")
        st.write(f"**Your answer:** {result['answer'] or '(no answer)'}")
        for check in grade["checks"]:
            st.write(("✅ " if check["covered"] else "❌ ") + check["point"])
        st.info(f"**Feedback:** {grade['feedback']}")
        st.caption(f"Model answer: {q.answer} · Source: page {q.source_page}")

if st.button("Start a new quiz", type="primary"):
    st.session_state.pop("quiz", None)
    st.rerun()