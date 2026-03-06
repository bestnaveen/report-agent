"""Phase 2: RAG via ChromaDB + sentence-transformers."""
import uuid
from config import RAG_CHUNK_SIZE, RAG_CHUNK_OVERLAP, RAG_COLLECTION_NAME


def _chunk_text(text: str, chunk_size: int = RAG_CHUNK_SIZE, overlap: int = RAG_CHUNK_OVERLAP) -> list[str]:
    """Split text into overlapping chunks."""
    if not text:
        return []
    chunks = []
    start = 0
    while start < len(text):
        end = start + chunk_size
        chunks.append(text[start:end])
        start += chunk_size - overlap
    return chunks


def build_vector_store(text: str, chunk_size: int = RAG_CHUNK_SIZE, overlap: int = RAG_CHUNK_OVERLAP):
    """
    Chunk text, embed, and store in ChromaDB.
    Returns a ChromaDB collection.
    """
    import chromadb
    from sentence_transformers import SentenceTransformer

    chunks = _chunk_text(text, chunk_size, overlap)
    if not chunks:
        return None

    model = SentenceTransformer("all-MiniLM-L6-v2")
    embeddings = model.encode(chunks).tolist()

    client = chromadb.Client()
    # Use a unique collection name per session to avoid conflicts
    collection_name = f"{RAG_COLLECTION_NAME}_{uuid.uuid4().hex[:8]}"
    collection = client.create_collection(name=collection_name)

    collection.add(
        documents=chunks,
        embeddings=embeddings,
        ids=[f"chunk_{i}" for i in range(len(chunks))],
    )
    return collection


def query_vector_store(collection, question: str, n: int = 5) -> list[str]:
    """
    Query the vector store for the most relevant chunks.
    Returns list of text chunks.
    """
    if collection is None:
        return []

    from sentence_transformers import SentenceTransformer
    model = SentenceTransformer("all-MiniLM-L6-v2")
    q_embedding = model.encode([question]).tolist()

    results = collection.query(
        query_embeddings=q_embedding,
        n_results=min(n, collection.count()),
    )
    return results.get("documents", [[]])[0]
