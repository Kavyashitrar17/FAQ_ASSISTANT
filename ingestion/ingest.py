import json
import os

from langchain_core.documents import Document

from ingestion.indexer import build_indexes

# ── Config ─────────────────────────────────────────────────────────────────────

DATA_DIR   = "data"
FAISS_PATH = "vector_store/faiss_index"
BM25_PATH  = "vector_store/bm25_index.pkl"
os.makedirs("vector_store", exist_ok=True)
# ── Load JSON files ─────────────────────────────────────────────────────────────

docs = []

files_loaded     = 0
topics_loaded    = 0
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

        for faq in questions:
            # ── Skip if not a dict (e.g. old format with plain strings) ──
            if not isinstance(faq, dict):
                print(f"[SKIP] {filename} → topic='{topic_name}' | "
                      f"expected dict, got {type(faq).__name__}: {faq!r}")
                continue

            question = faq.get("question", "").strip()
            answer   = faq.get("answer",   "").strip()

            if not question or not answer:
                print(f"[SKIP] {filename} → topic='{topic_name}' | "
                      f"missing question or answer")
                continue

            docs.append(
                Document(
                    page_content=(
                        f"Service: {service_name}\n"
                        f"Topic: {topic_name}\n\n"
                        f"Question: {question}\n\n"
                        f"Answer: {answer}"
                    ),
                    metadata={
                        "service": service_name.lower().strip(),
                        "topic": topic_name,
                        "source_file": filename,
                        "question": question,
                    },
                )
            )
            file_questions += 1  # ✅ FIXED: inside faq loop, not topic loop

        file_topics += 1

    topics_loaded    += file_topics
    questions_loaded += file_questions
    files_loaded     += 1

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
if not docs:
    raise ValueError(
        "No valid FAQ documents found."
    )
build_indexes(
    docs=docs,
    faiss_path=FAISS_PATH,
    bm25_path=BM25_PATH,
)

print()
print("Indexes created successfully!")
print(f"  FAISS → {FAISS_PATH}")
print(f"  BM25  → {BM25_PATH}")