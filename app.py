import streamlit as st
import tempfile
import os
import sys

sys.path.insert(0, os.path.abspath("."))

from dotenv import load_dotenv
from src.ingestion import load_pdfs
from src.qa import answer_question
from src.embeddings import client, get_collection, index_chunks

load_dotenv()

st.set_page_config(
    page_title="Chat With PDF",
    page_icon="📄",
    layout="centered"
)

st.title("📄 Chat With PDF")
st.markdown(
    "Upload PDF documents and ask questions about their contents."
)

# ---------------- Session Init ----------------

if "initialized" not in st.session_state:
    try:
        client.delete_collection("documents")
    except:
        pass

    get_collection()

    st.session_state.initialized = True
    st.session_state.indexed = False
    st.session_state.chunk_count = 0
    st.session_state.uploaded_names = []

st.divider()

# ---------------- Upload PDFs ----------------

uploaded_files = st.file_uploader(
    "Upload PDF file(s)",
    type=["pdf"],
    accept_multiple_files=True
)

if uploaded_files:

    st.write("Selected files:")

    for file in uploaded_files:
        st.write(f"📄 {file.name}")

    if st.button("📤 Index Documents", type="primary"):

        pdf_files = []

        try:
            # Create temporary files
            for uploaded_file in uploaded_files:

                with tempfile.NamedTemporaryFile(
                    delete=False,
                    suffix=".pdf"
                ) as tmp:

                    tmp.write(uploaded_file.read())

                    # Store temp path + original filename
                    pdf_files.append(
                        (tmp.name, uploaded_file.name)
                    )

            with st.spinner("📊 Indexing documents..."):

                chunks = load_pdfs(pdf_files)

                # Clear previous collection
                try:
                    client.delete_collection("documents")
                except:
                    pass

                get_collection()

                index_chunks(chunks)

                st.session_state.indexed = True
                st.session_state.chunk_count = len(chunks)
                st.session_state.uploaded_names = [
                    f.name for f in uploaded_files
                ]

            st.success(
                f"✅ Successfully indexed {len(chunks)} chunks."
            )

        finally:
            # Delete temporary PDF files
            for path, _ in pdf_files:
                try:
                    os.remove(path)
                except:
                    pass

# ---------------- Indexed Documents ----------------

if st.session_state.indexed:

    st.divider()

    st.success(
        f"Indexed {st.session_state.chunk_count} chunks."
    )

    with st.expander("📂 Indexed Documents"):

        for name in st.session_state.uploaded_names:
            st.write(f"📄 {name}")

    # ---------------- Clear Documents ----------------

    if st.button("🗑 Clear Documents"):

        try:
            client.delete_collection("documents")
        except:
            pass

        get_collection()

        st.session_state.indexed = False
        st.session_state.chunk_count = 0
        st.session_state.uploaded_names = []

        st.rerun()

    st.divider()

    # ---------------- Q&A ----------------

    question = st.text_input(
        "Ask a question",
        placeholder="What is the main topic of the document?"
    )

    if st.button("Ask", type="primary"):

        if not question.strip():
            st.warning("Please enter a question.")

        else:

            with st.spinner("Searching documents..."):

                result = answer_question(question)

            st.subheader("Answer")
            st.markdown(result["answer"])

            st.subheader("Sources")

            seen = set()

            for source in result["sources"]:

                key = (
                    f"{source['source']}_{source['page']}"
                )

                if key not in seen:

                    seen.add(key)

                    st.markdown(
                        f"📄 **{source['source']}** — Page {source['page']}"
                    )

    st.divider()

    # ---------------- Example Questions ----------------

    st.markdown("### Example Questions")

    examples = [
        "What is the main topic of the document?",
        "Summarize the document.",
        "What are the key findings?"
    ]

    for example in examples:

        if st.button(example, key=example):

            with st.spinner("Searching documents..."):

                result = answer_question(example)

            st.subheader("Answer")
            st.markdown(result["answer"])

            st.subheader("Sources")

            seen = set()

            for source in result["sources"]:

                key = (
                    f"{source['source']}_{source['page']}"
                )

                if key not in seen:

                    seen.add(key)

                    st.markdown(
                        f"📄 **{source['source']}** — Page {source['page']}"
                    )