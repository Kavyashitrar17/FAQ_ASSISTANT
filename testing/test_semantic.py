# test_semantic.py

from backend.retrieval.semantic import semantic_search

results = semantic_search(
    "What is Airtel Black?"
)

print("Results:", len(results))

for i, (doc, score) in enumerate(results, start=1):
    print("\n====================")
    print("DOC", i)
    print("SCORE:", score)
    print(doc.page_content[:300])