"""Upload page: read a PDF, split it into chunks, embed them and store them."""
import hashlib
import re

import streamlit as st

from core import chunker, config, embeddings, pdf_parser, ui, vector_store
from db import queries

st.set_page_config(page_title="Upload · TutorLens", page_icon="📄", layout="wide")
ui.init()
student_id = ui.sidebar_student()

ui.page_heading("what would you like to learn today?")
st.write("📄 Upload your course materials and start learning.")
st.write("Use a text-based PDF (lecture notes, slides exported as PDF, a textbook chapter).")

uploaded = st.file_uploader("Drag and drop a PDF here, or browse", type=["pdf"])

if uploaded is not None:
    data = uploaded.getvalue()
    file_hash = hashlib.sha256(data).hexdigest()
    existing = queries.get_document_by_hash(file_hash)

    if existing:
        st.info(f"This PDF is already processed as “{existing['title']}”. Go to the Learn page.")
    elif st.button("Process PDF", type="primary"):
        try:
            with st.status("Processing the PDF...", expanded=True) as status:
                st.write("Reading the PDF...")
                parsed = pdf_parser.parse_pdf(data)
                chunks = chunker.build_chunks(parsed)
                if not chunks:
                    raise ValueError("No text could be extracted from this PDF.")
                st.write(
                    f"Found {parsed.n_pages} pages and {len(chunks)} chunks. "
                    "Creating embeddings (the first run downloads the model, so please wait)..."
                )
                bar = st.progress(0.0)
                vectors = embeddings.embed_texts(
                    [c.for_embedding for c in chunks],
                    progress=lambda done, total: bar.progress(done / total),
                )
                title = re.sub(r"\.pdf$", "", uploaded.name, flags=re.IGNORECASE)
                doc_id = queries.add_document(title, uploaded.name, file_hash, parsed.n_pages)
                try:
                    vector_store.add_document_chunks(doc_id, chunks, vectors)
                except Exception:
                    queries.delete_document(doc_id)
                    raise
                (config.PDF_DIR / f"{doc_id}.pdf").write_bytes(data)
                status.update(label="PDF is ready!", state="complete")
            st.session_state["doc_id"] = doc_id
            st.rerun()
        except Exception as error:  # show a friendly message instead of a crash
            st.error(f"Could not process this PDF: {error}")

st.divider()
st.subheader("Your PDFs")
documents = queries.list_documents()
if not documents:
    st.caption("Nothing uploaded yet.")
for doc in documents:
    left, right = st.columns([5, 1])
    left.write(f"**{doc['title']}** · {doc['n_pages']} pages")
    if right.button("Delete", key=f"delete_{doc['id']}"):
        vector_store.delete_document(doc["id"])
        queries.delete_document(doc["id"])
        (config.PDF_DIR / f"{doc['id']}.pdf").unlink(missing_ok=True)
        st.rerun()