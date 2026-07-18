# from src.ingestion import load_pdfs
# from src.embeddings import index_chunks, collection
# from src.qa import answer_question

# # Index PDFs if needed
# if collection.count() == 0:
#     chunks = load_pdfs("./pdfs")
#     index_chunks(chunks)

# # Test a question
# result = answer_question("What is the main topic of these documents?")
# print(result["answer"])
# print("\nSources:")
# for s in result["sources"]:
#     print(f"  - {s['source']} (page {s['page']})")


print("=== STARTING TEST ===")

import sys
import os
sys.path.insert(0, os.path.abspath("."))

print("Step 1: imports ok")

from dotenv import load_dotenv
load_dotenv()

api_key = os.getenv("GROQ_API_KEY")
print(f"Step 2: API key loaded = {'YES' if api_key else 'NO - check .env file'}")

print("Step 3: loading ingestion...")
from src.ingestion import load_pdfs
print("Step 4: loading embeddings...")
from src.embeddings import index_chunks, collection
print("Step 5: loading qa...")
from src.qa import answer_question

print(f"Step 6: chunks in DB = {collection.count()}")

if collection.count() == 0:
    print("Step 7: indexing PDFs...")
    chunks = load_pdfs("./pdfs")
    print(f"  Found {len(chunks)} chunks")
    index_chunks(chunks)
else:
    print(f"Step 7: already indexed, skipping")

print("\nStep 8: asking question...")
result = answer_question("What is the main topic of these documents?")

print("\n=== ANSWER ===")
print(result["answer"])
print("\n=== SOURCES ===")
for s in result["sources"]:
    print(f"  - {s['source']} (page {s['page']})")