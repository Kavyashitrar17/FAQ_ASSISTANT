# test_ollama_only.py

import ollama

response = ollama.chat(
    model="llama3.2:3b",
    messages=[
        {
            "role": "user",
            "content": "What is Airtel Black?"
        }
    ]
)

print(response["message"]["content"])