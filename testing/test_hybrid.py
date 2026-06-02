# test_hybrid.py

from backend.retrieval.semantic import semantic_search
from backend.retrieval.keyword import keyword_search
from backend.retrieval.hybrid import reciprocal_rank_fusion

query = "What is Airtel Black?"

semantic = semantic_search(query)
keyword = keyword_search(query)

results = reciprocal_rank_fusion(
    semantic,
    keyword
)

print("Results:", len(results))

for i, doc in enumerate(results[:10], start=1):
    print("\n================")
    print("DOC", i)
    print(doc.page_content[:300])