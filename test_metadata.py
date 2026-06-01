# test_metadata.py

from langchain_community.vectorstores import FAISS
from langchain_huggingface import HuggingFaceEmbeddings

embedding_model = HuggingFaceEmbeddings(
    model_name="sentence-transformers/all-MiniLM-L6-v2"
)

db = FAISS.load_local(
    "vector_store/faiss_index",
    embedding_model,
    allow_dangerous_deserialization=True
)

docs = db.similarity_search("slow internet", k=3)

for i, doc in enumerate(docs, start=1):
    print("\n====================")
    print("DOC", i)
    print("TEXT:", doc.page_content)
    print("METADATA:", doc.metadata)