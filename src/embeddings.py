import chromadb
from sentence_transformers import SentenceTransformer

MODEL = SentenceTransformer("all-MiniLM-L6-v2")

client = chromadb.Client()


def get_collection():
    return client.get_or_create_collection("documents")


def index_chunks(chunks: list[dict]):
    collection = get_collection()

    texts = [c["text"] for c in chunks]
    embeddings = MODEL.encode(texts).tolist()

    ids = [f"chunk_{i}" for i in range(len(chunks))]
    metadatas = [
        {
            "source": c["source"],
            "page": c["page"]
        }
        for c in chunks
    ]

    collection.add(
        documents=texts,
        embeddings=embeddings,
        metadatas=metadatas,
        ids=ids
    )

    print(f"Indexed {len(chunks)} chunks")


def search(query: str, n_results: int = 5):
    collection = get_collection()

    query_emb = MODEL.encode([query]).tolist()

    results = collection.query(
        query_embeddings=query_emb,
        n_results=n_results
    )

    output = []

    for i, doc in enumerate(results["documents"][0]):
        output.append({
            "text": doc,
            "source": results["metadatas"][0][i]["source"],
            "page": results["metadatas"][0][i]["page"]
        })

    return output