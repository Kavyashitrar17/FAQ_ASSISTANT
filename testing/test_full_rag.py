# test_full_rag.py

from backend.retrieval.semantic import semantic_search
from backend.retrieval.keyword import keyword_search
from backend.retrieval.hybrid import reciprocal_rank_fusion
# from backend.retrieval.reranker import rerank
from backend.generation.prompt import build_prompt
from backend.generation.generator import stream_answer

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

prompt, _ = build_prompt(
    question=query,
    docs=fused[:5],  # Using top 5 fused results directly
    rewritten_query=query
)

print("\n===== ANSWER =====\n")
with open("debug_prompt.txt", "w", encoding="utf-8") as f:
    f.write(prompt)
for token in stream_answer(prompt):
    print(token, end="", flush=True)