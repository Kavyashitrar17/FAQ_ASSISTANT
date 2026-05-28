def build_prompt(context, question, history):

    context_text = "\n\n".join(
        [doc.page_content for doc in context]
    )

    prompt = f"""
You are an Airtel customer support assistant.

Use ONLY the provided context to answer.

Conversation History:
{history}

Context:
{context_text}

Current User Question:
{question}

Instructions:
- Answer naturally and conversationally.
- Use the conversation history to understand follow-up questions.
- If the answer is clearly present in the context, answer confidently.
- Keep answers concise and helpful.
- Do NOT say "the context does not mention" if the answer can reasonably be inferred from the context.
- Only say "I could not find that information in the provided context" when the answer is truly unavailable.

Answer:
"""

    return prompt