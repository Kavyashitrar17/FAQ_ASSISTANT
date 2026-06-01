import pickle
import re

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

    def search(
        self,
        query: str,
        top_k: int = 0,
        service: str | None = None,
    ) -> list[tuple]:
        """
        Args:
            query:   Query string to score against the BM25 corpus.
            top_k:   How many results to return. Falls back to settings.bm25_top_k.
            service: Optional service name to filter results.
                     If None, returns results across all services (existing behavior).
                     If provided, only returns documents where
                     doc.metadata["service"] == service.
        """
        k = top_k or settings.bm25_top_k
        tokens = _tokenise(query)
        scores = self.bm25.get_scores(tokens)

        # Rank all documents by score descending
        ranked = sorted(
            range(len(scores)),
            key=lambda i: scores[i],
            reverse=True,
        )

        results = []
        for i in ranked:
            if scores[i] <= 0:
                break                          # BM25 scores are monotone; safe to stop

            doc = self.docs[i]

            # ── Service filter ────────────────────────────────────────────────
            if (
                 service is not None
                 and doc.metadata.get("service", "").lower()
                   != service.lower()
                ):
             continue
                

            results.append((doc, float(scores[i])))

            if len(results) == k:
                break

        return results


_bm25_index = BM25Index()


def keyword_search(query: str, service: str | None = None) -> list[tuple]:
    """
    Public interface for BM25 keyword search.

    Args:
        query:   User query string (possibly rewritten).
        service: Optional service name to filter results.
                 If None, returns results across all services (existing behavior).
                 If provided, only returns documents where
                 doc.metadata["service"] == service.
    """
    return _bm25_index.search(query, service=service)