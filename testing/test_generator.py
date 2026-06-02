# test_generator.py

from backend.generation.generator import stream_answer

prompt = """
Answer shortly.

Question:
What is Airtel Black?

Answer:
"""

for token in stream_answer(prompt):
    print(token, end="", flush=True)