import json
import os

from langchain_core.documents import Document

from ingestion.indexer import build_indexes

# ── Config ─────────────────────────────────────────────────────────────────────

DATA_DIR    = "data"
FAISS_PATH  = "vector_store/faiss_index"
BM25_PATH   = "vector_store/bm25_index.pkl"

# ── Load JSON files ─────────────────────────────────────────────────────────────

docs = []

files_loaded    = 0
topics_loaded   = 0
questions_loaded = 0

json_files = [f for f in sorted(os.listdir(DATA_DIR)) if f.endswith(".json")]

if not json_files:
    raise FileNotFoundError(f"No JSON files found in '{DATA_DIR}/'")

for filename in json_files:
    filepath = os.path.join(DATA_DIR, filename)
    try:
      with open(filepath, "r", encoding="utf-8") as f:
        data = json.load(f)
    except Exception as e:
      print(f"[ERROR] Failed to load {filename}: {e}")
      continue

    service_name = data.get("service", "Unknown Service")
    topics       = data.get("topics", [])

    file_topics    = 0
    file_questions = 0

    for topic in topics:
        topic_name = topic.get("name", "Unknown Topic")
        questions  = topic.get("questions", [])

        for question in questions:
            question = question.strip()
            if not question:
                continue

            docs.append(
                Document(
                    page_content=question,
                    metadata={
                        "service": service_name.lower().strip(),
                        "topic":   topic_name,
                         "source_file": filename,
                    }
                )
            )
            file_questions += 1

        file_topics += 1

    topics_loaded   += file_topics
    questions_loaded += file_questions
    files_loaded    += 1

    print(f"  [✓] {filename:<25}  service='{service_name}'  "
          f"topics={file_topics}  questions={file_questions}")

# ── Statistics ──────────────────────────────────────────────────────────────────

print()
print("=" * 52)
print("  Ingestion Summary")
print("=" * 52)
print(f"  Files loaded      : {files_loaded}")
print(f"  Topics loaded     : {topics_loaded}")
print(f"  Questions indexed : {questions_loaded}")
print(f"  Documents created : {len(docs)}")
print("=" * 52)
print()

# ── Build indexes ───────────────────────────────────────────────────────────────

build_indexes(
    docs=docs,
    faiss_path=FAISS_PATH,
    bm25_path=BM25_PATH,
)

print()
print("Indexes created successfully!")
print(f"  FAISS → {FAISS_PATH}")
print(f"  BM25  → {BM25_PATH}")