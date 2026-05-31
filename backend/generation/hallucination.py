from langchain_core.documents import Document
import re

_UNCERTAINTY_PHRASES = [
    "i could not find",
    "not available in the context",
    "not mentioned",
    "i don't know",
    "no information",
]

def is_grounded(answer: str, docs: list[Document]) -> bool:
    """
    Lightweight faithfulness check: verify answer tokens overlap
    meaningfully with retrieved docs. Flags probable hallucinations.
    """
    if any(phrase in answer.lower() for phrase in _UNCERTAINTY_PHRASES):
        return True  # model correctly abstained

    answer_words = set(re.findall(r"\b\w{4,}\b", answer.lower()))
    doc_words = set(
        w for doc in docs
        for w in re.findall(r"\b\w{4,}\b", doc.page_content.lower())
    )

    if not answer_words:
        return False

    overlap = len(answer_words & doc_words) / len(answer_words)
    return overlap >= 0.35   # tune this threshold

def add_confidence_note(answer: str, docs: list[Document]) -> str:
    if not is_grounded(answer, docs):
        return (
            answer
            + "\n\n> ⚠️ *Low confidence: this answer may not be fully grounded "
            "in the knowledge base. Please verify with Airtel support.*"
        )
    return answer