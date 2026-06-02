# test_after_cleanup.py

from backend.retrieval.semantic import semantic_search
from backend.retrieval.keyword import keyword_search
from backend.retrieval.hybrid import reciprocal_rank_fusion
from backend.generation.prompt import build_prompt

import gc

query = "What is Airtel Black?"

semantic = semantic_search(query)
keyword = keyword_search(query)

fused = reciprocal_rank_fusion(
    semantic,
    keyword
)

prompt, _ = build_prompt(
    question=query,
    docs=[fused[0]],
    rewritten_query=query
)

# free retrieval memory
del semantic
del keyword
del fused

gc.collect()

from backend.generation.generator import stream_answer

print("STARTING GENERATION\n")

for token in stream_answer(prompt):
    print(token, end="", flush=True)