# Airtel RAG Chatbot

A production-oriented Retrieval-Augmented Generation (RAG) chatbot built for Airtel knowledge assistance. The system combines semantic search, BM25 keyword retrieval, hybrid ranking, query rewriting, reranking, conversational memory, and hallucination detection to generate accurate responses grounded in Airtel service documentation.

## Features

* Retrieval-Augmented Generation (RAG)
* Semantic Search using FAISS
* BM25 Keyword Retrieval
* Hybrid Retrieval Pipeline
* Query Rewriting for Follow-up Questions
* Context-Aware Conversational Memory
* Cross-Encoder Reranking
* Hallucination Detection
* FastAPI REST Backend
* Streamlit Frontend
* Ollama Local LLM Integration
* Docker Support
* Airtel Domain-Specific Knowledge Base

---

## System Architecture

```text
User Question
      │
      ▼
Conversation History
      │
      ▼
Query Rewriter
      │
      ▼
Hybrid Retrieval
 ┌─────────────┐
 │ FAISS       │
 │ BM25 Index  │
 └─────────────┘
      │
      ▼
Reranker
      │
      ▼
Context Assembly
      │
      ▼
Prompt Builder
      │
      ▼
Ollama LLM
      │
      ▼
Hallucination Check
      │
      ▼
Final Response
```

---

## Project Structure

```text
airtel_rag/
│
├── backend/
│   ├── api.py
│   ├── config.py
│   │
│   ├── generation/
│   │   ├── generator.py
│   │   ├── hallucination.py
│   │   ├── prompt.py
│   │   └── query_rewriter.py
│   │
│   └── retrieval/
│       ├── semantic.py
│       ├── keyword.py
│       ├── hybrid.py
│       ├── reranker.py
│       └── retriever.py
│
├── ingestion/
│   ├── ingest.py
│   └── indexer.py
│
├── frontend/
│   ├── app.py
│   ├── style.css
│   └── utils.py
│
├── data/
│   ├── prepaid.json
│   ├── postpaid.json
│   ├── wifi.json
│   ├── dth.json
│   ├── airtelblack.json
│   ├── paymentsbank.json
│   └── faq.json
│
├── vector_store/
│   ├── bm25_index.pkl
│   └── faiss_index/
│       ├── index.faiss
│       └── index.pkl
│
├── testing/
│   ├── test_full_rag.py
│   ├── test_hybrid.py
│   ├── test_reranker.py
│   ├── test_rewriter.py
│   ├── test_semantic.py
│   └── additional unit tests
│
├── Dockerfile
├── docker-compose.yml
├── requirements.txt
├── requirements-prod.txt
├── chat_history.json
└── README.md
```

---

## Knowledge Base

The chatbot is trained on Airtel service information including:

* Airtel Prepaid Plans
* Airtel Postpaid Plans
* Airtel Xstream Fiber
* Airtel DTH Services
* Airtel Black
* Airtel Payments Bank
* Frequently Asked Questions

---

## Retrieval Pipeline

### 1. Query Rewriting

Follow-up questions are rewritten into standalone queries using conversation history.

Example:

User:

```
What is Airtel Black?
```

User:

```
What are its benefits?
```

Rewritten Query:

```
What are the benefits of Airtel Black?
```

### 2. Hybrid Retrieval

The system combines:

* Semantic Retrieval (FAISS + Sentence Transformers)
* Keyword Retrieval (BM25)

Results from both retrievers are merged to improve recall and precision.

### 3. Reranking

Retrieved documents are reranked using a cross-encoder model to prioritize the most relevant context.

### 4. Response Generation

A structured prompt containing:

* Conversation History
* Retrieved Context
* Current Question

is sent to the Ollama-hosted LLM.

### 5. Hallucination Detection

Generated responses are checked against retrieved context to identify unsupported claims before being returned to the user.

---

## Installation

### Clone Repository

```bash
git clone <repository-url>

cd airtel_rag
```

### Create Virtual Environment

```bash
python -m venv venv

venv\Scripts\activate
```

### Install Dependencies

```bash
pip install -r requirements.txt
```

---

## Running the Application

### Step 1: Start Ollama

```bash
ollama serve
```

Pull your preferred model:

```bash
ollama pull llama3
```

### Step 2: Build Vector Index

```bash
python ingestion/ingest.py
```

### Step 3: Start Backend

```bash
uvicorn backend.api:app --reload
```

Backend URL:

```text
http://localhost:8000
```

Swagger Documentation:

```text
http://localhost:8000/docs
```

### Step 4: Launch Frontend

```bash
streamlit run frontend/app.py
```

Frontend URL:

```text
http://localhost:8501
```

---

## Docker Deployment

Build and run the complete application:

```bash
docker-compose up --build
```

---

## Future Enhancements

* PostgreSQL-based Conversation Memory
* User Authentication
* LangSmith Monitoring
* Retrieval Evaluation Dashboard
* Multi-Collection Knowledge Bases
* Feedback Learning Loop
* Kubernetes Deployment

---

## Author

Kavyashi Trar

B.Tech Computer Science Engineering

Manipal University Jaipur

---

## License

MIT License
