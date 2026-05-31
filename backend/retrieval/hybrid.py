from langchain_core.documents import Document

def reciprocal_rank_fusion(
    semantic_results: list[tuple],
    keyword_results: list[tuple],
    k: int = 60,
) -> list[Document]:
    """
    Merges two ranked lists using Reciprocal Rank Fusion.
    RRF score = Σ 1 / (rank + k)  across all lists.
    """
    scores: dict[str, float] = {}
    doc_map: dict[str, Document] = {}

    for rank, (doc, _) in enumerate(semantic_results):
        key = doc.page_content
        scores[key] = scores.get(key, 0.0) + 1.0 / (rank + k)
        doc_map[key] = doc

    for rank, (doc, _) in enumerate(keyword_results):
        key = doc.page_content
        scores[key] = scores.get(key, 0.0) + 1.0 / (rank + k)
        doc_map[key] = doc

    ranked_keys = sorted(scores, key=lambda x: scores[x], reverse=True)
    return [doc_map[k] for k in ranked_keys]