import ollama


SYSTEM_PROMPT = """
You are an Airtel FAQ Assistant.

Rules:
1. Answer ONLY from the provided context.
2. If the answer is not present in the context, say:
   "I could not find that information in the provided context."
3. Keep answers concise and helpful.
4. For follow-up questions, use conversation history carefully.
5. Do not make up information.
6. If the context contains bullet points, preserve them nicely.
"""


def generate_answer(prompt):

    response = ollama.chat(
        model="gemma:2b",

        messages=[
            {
                "role": "system",
                "content": SYSTEM_PROMPT
            },
            {
                "role": "user",
                "content": prompt
            }
        ],

        options={
            "temperature": 0.2,
            "top_p": 0.8,
            "top_k": 40,
            "num_predict": 256
        }
    )

    return response["message"]["content"]