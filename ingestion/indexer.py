# ingestion/indexer.py  (run once)
import pickle
from rank_bm25 import BM25Okapi
from langchain_community.vectorstores import FAISS
from langchain_huggingface import HuggingFaceEmbeddings
from langchain_core.documents import Document
import re

def build_indexes(docs: list[Document], faiss_path: str, bm25_path: str):
    # FAISS
    embedding_model = HuggingFaceEmbeddings(model_name="sentence-transformers/all-MiniLM-L6-v2")
    vectorstore = FAISS.from_documents(docs, embedding_model)
    vectorstore.save_local(faiss_path)

    # BM25
    tokenised = [re.findall(r"\w+", d.page_content.lower()) for d in docs]
    bm25 = BM25Okapi(tokenised)
    with open(bm25_path, "wb") as f:
        pickle.dump({"bm25": bm25, "docs": docs}, f)

    print(f"Indexed {len(docs)} documents.")