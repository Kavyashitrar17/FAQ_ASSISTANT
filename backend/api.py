from fastapi import FastAPI
from pydantic import BaseModel
from typing import List, Dict
from backend.retriever import retrieve_docs
from backend.prompt import build_prompt
from backend.generator import generate_answer

app = FastAPI()


class QueryRequest(BaseModel):
    question: str
    history: List[Dict] = []


@app.get("/")
def home():
    return {"message": "Airtel RAG API is running"}


@app.post("/chat")
def chat(request: QueryRequest):

    question = request.question

    # ─────────────────────────────────────────────
    # BUILD HISTORY STRING  (for prompt context)
    # ─────────────────────────────────────────────
    history_text = ""
    for msg in request.history:
        role    = msg.get("role", "")
        content = msg.get("content", "")
        history_text += f"{role}: {content}\n"

    # ─────────────────────────────────────────────
    # ENHANCE QUESTION FOR RETRIEVAL
    # Combine the most-recent previous user query
    # with the current question so FAISS retrieval
    # has better context for follow-up questions.
    # ─────────────────────────────────────────────
    enhanced_question = question                    # safe default

    if request.history:
        last_user_messages = [
            msg["content"]
            for msg in request.history
            if msg["role"] == "user"
        ]

        # FIX 3: use [-1] (most recent previous turn),
        #         not [-2] (two turns ago)
        if len(last_user_messages) >= 1:
            previous_query = last_user_messages[-1]

            # FIX 4: no leading whitespace — stray spaces
            #         degrade FAISS embedding quality
            enhanced_question = (
                f"Previous topic: {previous_query}\n"
                f"Current question: {question}"
            )
            print("Enhanced Query:", enhanced_question)

    # ─────────────────────────────────────────────
    # RETRIEVE DOCUMENTS
    # ─────────────────────────────────────────────
    docs = retrieve_docs(enhanced_question)
    print("\n===== RETRIEVED DOCS =====")
    for i, doc in enumerate(docs):
        print(f"\nDOC {i + 1}:\n")
        print(doc.page_content)
    print("\n==========================\n")

    # ─────────────────────────────────────────────
    # BUILD PROMPT  &  GENERATE ANSWER
    # ─────────────────────────────────────────────
    prompt = build_prompt(
        context=docs,
        question=question,
        history=history_text,
    )

    answer = generate_answer(prompt)

    return {
        "question": request.question,
        "answer": answer,
    }