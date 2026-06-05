from sentence_transformers import CrossEncoder
from langchain_core.documents import Document
from backend.config import settings
from backend.logger import logger

_reranker = CrossEncoder(settings.reranker_model)

def rerank(query: str, docs: list[Document]) -> list[Document]:
    logger.info(
    f"RERANKER RECEIVED {len(docs)} DOCS"
)

    if not docs:
        return []

    pairs = [(query, doc.page_content) for doc in docs]
    logger.info(
    f"RERANKER RECEIVED {len(docs)} DOCS"
)
    scores = _reranker.predict(pairs)
    logger.info(
    f"RERANKER SCORES: {scores}"
)
    logger.info(
    "RERANKER SCORING COMPLETE"
)
    ranked = sorted(
        zip(docs, scores),
        key=lambda x: x[1],
        reverse=True
    )
    # print("===== TOP 5 RERANKED DOCS =====")
    # for i, (doc, score) in enumerate(ranked[:5], 1):
    #  print(f"{i}. Score={score:.3f}")
    #  print(doc.page_content[:150])
    #  print("-" * 50)
    return [doc for doc, _ in ranked[:settings.final_top_k]]