from groq import Groq
import os
from dotenv import load_dotenv
from src.embeddings import search

load_dotenv()
client = Groq(api_key=os.getenv("GROQ_API_KEY"))

def answer_question(question: str) -> dict:
    """Retrieve relevant chunks and generate a grounded answer using Groq."""
    chunks = search(question, n_results=5)

    context = "\n".join(
        f"[Source: {c['source']}, Page {c['page']}]\n{c['text']}"
        for c in chunks
    )

    prompt = f"""You are a document Q&A assistant. Answer ONLY using the context below.
Always cite the source document name and page number in your answer.
If the answer is not found in the context, say "I don't have enough information."

Context:
{context}

Question: {question}

Answer (with citations):"""

    response = client.chat.completions.create(
        model="llama-3.3-70b-versatile",
        messages=[{"role": "user", "content": prompt}],
        max_tokens=1000
    )

    return {
        "answer": response.choices[0].message.content,
        "sources": [{"source": c["source"], "page": c["page"]} for c in chunks]
    }