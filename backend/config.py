from pydantic_settings import BaseSettings

class Settings(BaseSettings):
    # Models
    ollama_model: str = "llama3.2:3b"
    embedding_model: str = "sentence-transformers/all-MiniLM-L6-v2"
    reranker_model: str = "cross-encoder/ms-marco-MiniLM-L-6-v2"

    # Retrieval
    semantic_top_k: int = 10       # fetch wide, filter narrow
    bm25_top_k: int = 10
    final_top_k: int = 5           # after reranking
    similarity_threshold: float = 0.35   # cosine; below → discard

    # Memory
    history_window: int = 6        # last N messages kept verbatim
    summarise_after: int = 12      # summarise older turns

    # Generation
    temperature: float = 0.15
    max_tokens: int = 512

    # Paths
    faiss_path: str = "vector_store/faiss_index"
    bm25_path: str = "vector_store/bm25_index.pkl"

settings = Settings()