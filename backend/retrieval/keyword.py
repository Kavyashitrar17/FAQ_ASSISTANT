import pickle, re
from rank_bm25 import BM25Okapi
from langchain_core.documents import Document
from backend.config import settings

def _tokenise(text: str) -> list[str]:
    return re.findall(r"\w+", text.lower())

class BM25Index:
    def __init__(self):
        with open(settings.bm25_path, "rb") as f:
            data = pickle.load(f)
        self.bm25: BM25Okapi = data["bm25"]
        self.docs: list[Document] = data["docs"]

    def search(self, query: str, top_k: int = 5) -> list[tuple]:
        k = top_k or settings.bm25_top_k
        tokens = _tokenise(query)
        scores = self.bm25.get_scores(tokens)
        top_indices = sorted(range(len(scores)), key=lambda i: scores[i], reverse=True)[:k]
        return [(self.docs[i], float(scores[i])) for i in top_indices if scores[i] > 0]

_bm25_index = BM25Index()

def keyword_search(query: str) -> list[tuple]:
    return _bm25_index.search(query)