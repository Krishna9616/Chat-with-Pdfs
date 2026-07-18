import fitz  # PyMuPDF
import os

def load_pdfs(pdf_files: list[tuple[str, str]]) -> list[dict]:
    """Parse uploaded PDFs into text chunks with page metadata."""
    chunks = []

    for path, filename in pdf_files:
        doc = fitz.open(path)

        for page_num, page in enumerate(doc, start=1):
            text = page.get_text().strip()

            if not text:
                continue

            for chunk in split_text(text):
                chunks.append({
                    "text": chunk,
                    "source": filename,
                    "page": page_num
                })

    return chunks


def split_text(text: str, chunk_size: int = 500, overlap: int = 50) -> list[str]:
    chunks = []

    start = 0

    while start < len(text):
        chunks.append(text[start:start + chunk_size])
        start += chunk_size - overlap

    return chunks