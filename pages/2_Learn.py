
"""Learn page: AI teacher with a modern chat interface."""

import streamlit as st

from core import llm_client, teacher, ui, vector_store


# ============================================================
# 1. PAGE CONFIGURATION
# ============================================================

st.set_page_config(
    page_title="Learn · TutorLens",
    page_icon="📖",
    layout="wide",
)

ui.init()

# Do not call ui.sidebar_student() here because the student
# name is entered on the Home page.
student_name = st.session_state.get("student_name", "").strip()

doc = ui.sidebar_document()


# ============================================================
# 2. CUSTOM CSS
# ============================================================

st.html("""
<style>

    .block-container {
        max-width: 1100px;
        padding-top: 2rem;
        padding-bottom: 2rem;
    }

    /* Main heading */
    .learn-subtitle {
        color: #aab2c3;
        font-size: 15px;
        margin-top: -10px;
        margin-bottom: 25px;
    }

    /* Chat introduction */
    .chat-intro {
        border: 1px solid rgba(150, 165, 200, 0.25);
        background: rgba(100, 120, 160, 0.07);
        border-radius: 16px;
        padding: 20px;
        margin: 15px 0 22px 0;
    }

    .chat-intro h3 {
        margin-bottom: 8px;
        font-size: 19px;
    }

    .chat-intro p {
        color: #aab2c3;
        margin-bottom: 0;
        font-size: 14px;
    }

    /* Chat message boxes */
    [data-testid="stChatMessage"] {
        border: 1px solid rgba(150, 165, 200, 0.18);
        border-radius: 17px;
        padding: 17px;
        margin-bottom: 15px;
    }

    /* Quick actions */
    .quick-title {
        font-size: 17px;
        font-weight: 700;
        margin-top: 25px;
        margin-bottom: 12px;
    }

    /* Quick action buttons */
    div.stButton > button {
        border-radius: 30px;
        min-height: 42px;
        font-weight: 600;
        border: 1px solid rgba(150, 165, 200, 0.3);
    }

    /* PDF source information */
    .source-label {
        color: #929bb0;
        font-size: 12px;
    }

</style>
""")


# ============================================================
# 3. PERSONALIZED HEADER
# ============================================================

if student_name:
    st.title(f"👋 {student_name}, what would you like to learn today?")
else:
    st.title("📖 What would you like to learn today?")

st.markdown(
    '<div class="learn-subtitle">'
    'Ask your AI teacher anything about your uploaded course materials.'
    '</div>',
    unsafe_allow_html=True,
)


# ============================================================
# 4. CHECK PDF
# ============================================================

if doc is None:

    st.info("📄 No PDF found. Please visit the Upload page first.")

    st.page_link(
        "pages/1_Upload.py",
        label="Upload your course PDF",
        icon="📤",
    )

    st.stop()


# ============================================================
# 5. CHECK OLLAMA
# ============================================================

ok, message = llm_client.check_ollama()

if not ok:
    st.error(message)
    st.stop()


# ============================================================
# 6. CHAT MODE
# ============================================================

mode = st.sidebar.radio(
    "Learning Mode",
    ["Ask a question", "Explain a section"],
)

# ============================================================
# 7. STREAMING ANSWER FUNCTION
# ============================================================

def stream_answer(messages: list[dict]) -> str:
    """Display the AI answer as it is generated."""

    placeholder = st.empty()
    answer_text = ""

    for piece in llm_client.stream_chat(messages):
        answer_text += piece
        placeholder.markdown(answer_text + "▌")

    final_answer = teacher.clean_answer(answer_text)

    placeholder.markdown(final_answer)

    return final_answer


# ============================================================
# 8. ASK A QUESTION MODE
# ============================================================

if mode == "Ask a question":

    st.html(f"""
    <div class="chat-intro">
        <h3>🤖 AI Learning Assistant</h3>
        <p>
            I am ready to help you understand
            <b>{doc['title']}</b>.
            Ask questions, request explanations,
            or explore important concepts from your PDF.
        </p>
    </div>
    """)

    # Store conversations separately for each PDF
    chats = st.session_state.setdefault("chats", {})

    history = chats.setdefault(doc["id"], [])

    # --------------------------------------------------------
    # INITIAL GREETING
    # --------------------------------------------------------

    if not history:

        with st.chat_message("assistant", avatar="🤖"):

            st.markdown(
                f"Hello {student_name or 'there'}! 👋 "
                f"I'm your AI teacher. What would you like "
                f"to know about **{doc['title']}**?"
            )

    # --------------------------------------------------------
    # DISPLAY CHAT HISTORY
    # --------------------------------------------------------

    for item in history:

        with st.chat_message(
            item["role"],
            avatar="🤖" if item["role"] == "assistant" else "👤",
        ):

            st.markdown(item["content"])

            if item.get("sources"):

                st.caption(
                    ui.format_sources(item["sources"])
                )

    # --------------------------------------------------------
    # QUICK ACTIONS
    # --------------------------------------------------------

    st.markdown(
        '<div class="quick-title">✨ Quick Actions</div>',
        unsafe_allow_html=True,
    )

    def queue_question(prompt: str):
        """Queue a suggested question for the AI teacher."""
        st.session_state["learn_pending_question"] = prompt

    quick_col1, quick_col2 = st.columns(2)

    with quick_col1:

        st.button(
            "💬 Generate Summary",
            use_container_width=True,
            on_click=queue_question,
            args=(
                "Please summarize the main ideas and important "
                "concepts from the uploaded PDF in simple terms.",
            ),
        )

        st.button(
            "💬 Explain More",
            use_container_width=True,
            on_click=queue_question,
            args=(
                "Please explain the important concepts in more "
                "detail using simple language and examples.",
            ),
        )

    with quick_col2:

        st.page_link(
            "pages/3_Quiz.py",
            label="📝 Create Quiz",
            use_container_width=True,
        )

        st.button(
            "💬 Relate Topics",
            use_container_width=True,
            on_click=queue_question,
            args=(
                "Explain how the important topics in this PDF "
                "are connected to each other.",
            ),
        )

    # --------------------------------------------------------
    # CHAT INPUT
    # --------------------------------------------------------

    question_from_input = st.chat_input(
        "Ask me anything about your PDF...",
        key="learn_chat_input",
    )

    # Suggested questions take priority when clicked
    question = st.session_state.pop(
        "learn_pending_question", None
    )

    if not question:
        question = question_from_input

    # --------------------------------------------------------
    # PROCESS QUESTION
    # --------------------------------------------------------

    if question:

        # Display user message
        with st.chat_message("user", avatar="👤"):
            st.markdown(question)

        sources = []
        answer = ""

        # Generate AI response
        with st.chat_message("assistant", avatar="🤖"):

            try:

                sources = teacher.retrieve(
                    doc["id"],
                    question,
                    history,
                )

                if not sources:

                    answer = teacher.NOT_FOUND_MESSAGE
                    st.markdown(answer)

                else:

                    messages = teacher.build_answer_messages(
                        question,
                        sources,
                        history,
                    )

                    answer = stream_answer(messages)

                    if answer == teacher.NOT_FOUND_MESSAGE:
                        sources = []

                    else:

                        st.caption(
                            ui.format_sources(sources)
                        )

                        with st.expander(
                            "📚 View PDF sources used for this answer"
                        ):

                            for source in sources:

                                st.markdown(
                                    f"**Page {source.page} · "
                                    f"{source.section}**"
                                )

                                st.write(source.text)

            except Exception as error:

                st.error(
                    f"Something went wrong: {error}"
                )

                st.stop()

        # Save conversation
        history.append({
            "role": "user",
            "content": question,
        })

        history.append({
            "role": "assistant",
            "content": answer,
            "sources": sources,
        })


# ============================================================
# 9. EXPLAIN A SECTION MODE
# ============================================================

else:

    st.subheader("📚 Learn a specific section")

    st.caption(
        "Choose a section from your PDF and let the AI teacher "
        "explain it step by step."
    )

    sections = vector_store.get_sections(doc["id"])

    if not sections:

        st.warning("No sections were found in this PDF.")

    else:

        section = st.selectbox(
            "Choose a section to learn",
            sections,
        )

        if st.button(
            "✨ Explain This Section",
            type="primary",
            use_container_width=True,
        ):

            with st.chat_message("assistant", avatar="🤖"):

                try:

                    sources = teacher.section_sources(
                        doc["id"],
                        section,
                    )

                    if not sources:

                        st.warning(
                            "No readable content was found "
                            "for this section."
                        )

                    else:

                        messages = teacher.build_section_messages(
                            section,
                            sources,
                        )

                        stream_answer(messages)

                        st.caption(
                            ui.format_sources(sources)
                        )

                        with st.expander(
                            "📚 View source text"
                        ):

                            for source in sources:

                                st.markdown(
                                    f"**Page {source.page} · "
                                    f"{source.section}**"
                                )

                                st.write(source.text)

                except Exception as error:

                    st.error(
                        f"Something went wrong: {error}"
                    )
