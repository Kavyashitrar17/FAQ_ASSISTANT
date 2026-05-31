import ollama
from typing import Generator
from backend.config import settings

def stream_answer(prompt: str) -> Generator[str, None, None]:
    """Yield tokens one by one from Ollama."""
    stream = ollama.chat(
        model=settings.ollama_model,
        messages=[{"role": "user", "content": prompt}],
        stream=True,
        options={
            "temperature": settings.temperature,
            "top_p": 0.85,
            "num_predict": settings.max_tokens,
        },
    )
    for chunk in stream:
        token = chunk["message"]["content"]
        if token:
            yield token