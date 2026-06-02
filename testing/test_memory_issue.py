# test_memory_issue.py

from backend.retrieval.semantic import semantic_search
from backend.retrieval.keyword import keyword_search
from backend.retrieval.hybrid import reciprocal_rank_fusion
from backend.generation.prompt import build_prompt

query = "What is Airtel Black?"

semantic = semantic_search(query)
keyword = keyword_search(query)

fused = reciprocal_rank_fusion(
    semantic,
    keyword
)

prompt, _ = build_prompt(
    question=query,
    docs=[fused[0]],   # ONLY ONE DOCUMENT
    rewritten_query=query
)

print("PROMPT LENGTH =", len(prompt))
print("\nFIRST 500 CHARS:\n")
print(prompt[:500])