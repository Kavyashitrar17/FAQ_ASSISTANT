from langchain_community.vectorstores import FAISS
from langchain_huggingface import HuggingFaceEmbeddings
from backend.config import settings

_embedding_model = HuggingFaceEmbeddings(model_name=settings.embedding_model)
_vectorstore = FAISS.load_local(
    settings.faiss_path, _embedding_model, allow_dangerous_deserialization=True
)


def semantic_search(query: str, service: str | None = None) -> list[tuple]:
    """
    Returns (doc, score) pairs above the similarity threshold.
    FAISS returns L2 distance; we convert to cosine-like score.

    Args:
        query:   User query string (possibly rewritten).
        service: Optional service name to filter results.
                 If None, returns results across all services (existing behavior).
                 If provided, only returns documents where
                 doc.metadata["service"] == service.
    """
    # Fetch a larger candidate pool when filtering so that after dropping
    # non-matching services we still return up to semantic_top_k results.
    fetch_k = settings.semantic_top_k if service is None else settings.semantic_top_k * 6

    results = _vectorstore.similarity_search_with_score(query, k=fetch_k)

    filtered = []
    for doc, score in results:
        # ── Service filter ────────────────────────────────────────────────────
        if (
             service is not None
             and doc.metadata.get("service", "").lower()
               != service.lower()
            ):
            continue

        # ── Similarity threshold ──────────────────────────────────────────────
        normalised = 1 / (1 + score)   # L2 → 0-1; lower distance = higher score
        if normalised < settings.similarity_threshold:
            continue

        filtered.append((doc, normalised))

    # Honour top-k cap after filtering
    return filtered[: settings.semantic_top_k]