import ollama
client = ollama.Client(
    host="http://localhost:11434"
)
_REWRITE_TEMPLATE = """\
You are a query rewriter for a conversational RAG system.

Your task:
- Rewrite the current question ONLY if it depends on previous conversation context.
- If the question is already standalone and introduces a new topic, return it EXACTLY unchanged.

Rules:
- Resolve pronouns like "it", "they", "that", "those" only when needed.
- Do NOT inject old topic context into unrelated new questions.
- Do NOT over-explain.
- Output ONLY the rewritten question.

Examples:

Conversation:
user: What is Airtel Black?
assistant: Airtel Black is a bundled service.

Question:
Does it include DTH services?

Rewrite:
Does Airtel Black include DTH services?

---

Conversation:
user: What is Airtel Black?
assistant: Airtel Black is a bundled service.

Question:
How to recharge prepaid plan?

Rewrite:
How to recharge prepaid plan?

---

Conversation:
user: Tell me about international roaming.
assistant: Airtel offers roaming packs.

Question:
What are the charges?

Rewrite:
What are the charges for Airtel international roaming?

---

Conversation history:
{history}

Current question:
{question}

Rewritten question:
"""

def rewrite_query(question: str, history: list[dict]) -> str:
    if not history:
        return question

    # Use only recent history
    recent = history[-6:]

    history_str = "\n".join(
        f"{m['role']}: {m['content']}"
        for m in recent
    )

    prompt = _REWRITE_TEMPLATE.format(
        history=history_str,
        question=question
    )

    response = client.chat(
        model="llama3.2:3b",
        messages=[
            {
                "role": "user",
                "content": prompt
            }
        ],
        options={
            "temperature": 0.0,
            "num_predict": 80
        },
    )

    rewritten = response["message"]["content"].strip()

    # Safety fallback
    if (
        not rewritten
        or len(rewritten) < 3
        or len(rewritten) > 200
    ):
        return question

    return rewritten