from langchain_community.document_loaders import TextLoader
from langchain_community.embeddings import HuggingFaceEmbeddings
from langchain_community.vectorstores import FAISS
import re
from langchain_core.documents import Document
loader = TextLoader("data/faq.txt", encoding="utf-8")
documents = loader.load()
faq_text = documents[0].page_content

faq_list = re.findall(
    r"\d+\.\s.*?(?=\n\d+\.|\Z)",
    faq_text,
    re.DOTALL
)

chunks = []

for faq in faq_list:

    faq = faq.strip()

    if faq:

        chunks.append(
            Document(page_content=faq)
        )

print(chunks[:3])
print("Total FAQ chunks:", len(chunks))

embedding_model = HuggingFaceEmbeddings(
    model_name="sentence-transformers/all-MiniLM-L6-v2"
)
sample_embedding = embedding_model.embed_query(chunks[0].page_content)

print("Embedding Dimension:", len(sample_embedding))

print("\nFirst 20 values:\n")
print(sample_embedding[:20])

vector_store = FAISS.from_documents(
    chunks,
    embedding_model
)
vector_store.save_local("vector_store")
print("FAISS vector store created successfully!")