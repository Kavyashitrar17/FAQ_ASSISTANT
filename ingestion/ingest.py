from langchain_community.document_loaders import TextLoader
from langchain_core.documents import Document
import re

from ingestion.indexer import build_indexes

# Load FAQ file
loader = TextLoader("data/faq.txt", encoding="utf-8")
documents = loader.load()

faq_text = documents[0].page_content

# Split FAQs
faq_list = re.findall(
    r"\d+\.\s.*?(?=\n\d+\.|\Z)",
    faq_text,
    re.DOTALL
)

docs = []

for faq in faq_list:
    faq = faq.strip()

    if faq:
        docs.append(
            Document(page_content=faq)
        )

print(f"Loaded {len(docs)} FAQ chunks")

# Build indexes
build_indexes(
    docs=docs,
    faiss_path="vector_store/faiss_index",
    bm25_path="vector_store/bm25_index.pkl"
)

print("Indexes created successfully!")