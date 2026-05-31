from sentence_transformers import CrossEncoder
from langchain_core.documents import Document
from backend.config import settings

_reranker = CrossEncoder(settings.reranker_model)

def rerank(query: str, docs: list[Document]) -> list[Document]:
    """
    Score every candidate against the query; return top-k by score.
    Cross-encoders see both query + doc jointly → much higher precision.
    """
    if not docs:
        return []
    pairs = [(query, doc.page_content) for doc in docs]
    scores = _reranker.predict(pairs)
    ranked = sorted(zip(docs, scores), key=lambda x: x[1], reverse=True)
    return [doc for doc, _ in ranked[:settings.final_top_k]]