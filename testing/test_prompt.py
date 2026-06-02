# test_prompt.py

from backend.retrieval.semantic import semantic_search
from backend.retrieval.keyword import keyword_search
from backend.retrieval.hybrid import reciprocal_rank_fusion
# from backend.retrieval.reranker import rerank
from backend.generation.prompt import build_prompt

query = "What is Airtel Black?"

semantic = semantic_search(query)
keyword = keyword_search(query)

fused = reciprocal_rank_fusion(
    semantic,
    keyword
)

# reranked = rerank(
#     query,
#     fused
# )

prompt, sources = build_prompt(
    question=query,
    docs=fused[:5],  # Using top 5 fused results directly
    rewritten_query=query
)

print(prompt[:3000])

print("\n\nSources:")
print(sources)