# test_bm25.py

from backend.retrieval.keyword import keyword_search

results = keyword_search(
    "Airtel Black"
)

print("Results:", len(results))

for i, (doc, score) in enumerate(results, start=1):
    print("\n====================")
    print("DOC", i)
    print("SCORE:", score)
    print(doc.page_content[:300])