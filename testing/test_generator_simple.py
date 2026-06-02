# test_generator_simple.py

from backend.generation.generator import stream_answer

prompt = "Say hello in one sentence."

for token in stream_answer(prompt):
    print(token, end="")