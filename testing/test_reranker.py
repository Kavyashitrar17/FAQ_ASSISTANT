# test_reranker.py

from backend.retrieval.semantic import semantic_search
from backend.retrieval.keyword import keyword_search
from backend.retrieval.hybrid import reciprocal_rank_fusion
from backend.retrieval.reranker import rerank

query = "What is Airtel Black?"

semantic = semantic_search(query)
keyword = keyword_search(query)

fused = reciprocal_rank_fusion(
    semantic,
    keyword
)

reranked = rerank(
    query,
    fused
)

print("Results:", len(reranked))

for i, doc in enumerate(reranked, start=1):
    print("\n================")
    print("DOC", i)
    print(doc.page_content[:300])