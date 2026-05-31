from langchain_core.documents import Document

_SYSTEM = """You are an Airtel customer support assistant.

Rules:
1. Answer ONLY from the provided context.
2. Cite sources inline as [Source N] when used.
3. If the answer is not found in context, say:
   "I could not find that in my knowledge base."
4. Keep answers short, direct, factual, and friendly.
5. Never invent plan prices, speeds, benefits, or features.
6. Do not add unnecessary explanations.
7. For follow-up questions, use conversation history naturally.
"""

def build_prompt(
    question: str,
    docs: list[Document],
    rewritten_query: str,
) -> tuple[str, list[dict]]:

    context_parts = []
    sources = []

    for i, doc in enumerate(docs, 1):

        source_name = doc.metadata.get(
            "source",
            f"FAQ chunk {i}"
        )

        section = doc.metadata.get(
            "section",
            ""
        )

        context_parts.append(
            f"[Source {i}] ({source_name} — {section})\n{doc.page_content}"
        )

        sources.append({
            "index": i,
            "source": source_name,
            "section": section,
            "snippet": doc.page_content[:120] + "…",
        })

    context_text = "\n\n".join(context_parts)

    prompt = f"""{_SYSTEM}

Retrieved Context:
{context_text}

User Question:
{rewritten_query}

Answer:
"""

    return prompt, sources