from langchain_community.vectorstores import FAISS
from langchain_huggingface import HuggingFaceEmbeddings
from backend.config import settings

_embedding_model = HuggingFaceEmbeddings(model_name=settings.embedding_model)
_vectorstore = FAISS.load_local(
    settings.faiss_path, _embedding_model, allow_dangerous_deserialization=True
)

def semantic_search(query: str) -> list[tuple]:
    """
    Returns (doc, score) pairs above the similarity threshold.
    FAISS returns L2 distance; we convert to cosine-like score.
    """
    results = _vectorstore.similarity_search_with_score(
        query, k=settings.semantic_top_k
    )
    # FAISS L2 → normalise to 0-1 (lower distance = higher score)
    filtered = [
        (doc, 1 / (1 + score))      # monotone transform; score now 0→1
        for doc, score in results
        if 1 / (1 + score) >= settings.similarity_threshold
    ]
    return filtered