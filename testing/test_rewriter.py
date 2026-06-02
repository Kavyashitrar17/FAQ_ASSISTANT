# test_rewriter.py

from backend.generation.query_rewriter import rewrite_query

history = [
    {
        "role": "user",
        "content": "What is Airtel Black?"
    },
    {
        "role": "assistant",
        "content": "Airtel Black is a bundled service."
    }
]

print(
    rewrite_query(
        "Does it include DTH?",
        history
    )
)