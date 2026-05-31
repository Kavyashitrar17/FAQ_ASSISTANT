from fastapi import FastAPI
from fastapi.responses import StreamingResponse
from pydantic import BaseModel
import json

from backend.retrieval.semantic import semantic_search
from backend.retrieval.keyword import keyword_search
from backend.retrieval.hybrid import reciprocal_rank_fusion
from backend.retrieval.reranker import rerank
from backend.generation.query_rewriter import rewrite_query
from backend.generation.prompt import build_prompt
from backend.generation.generator import stream_answer
from backend.generation.hallucination import add_confidence_note
# from backend.memory.session import trim_history, history_to_string

app = FastAPI(title="Airtel RAG API v3")


class QueryRequest(BaseModel):
    question: str
    history: list[dict] = []


@app.post("/chat/stream")
async def chat_stream(request: QueryRequest):
    """
    Server-Sent Events endpoint.
    Yields: data: {"token": "..."} and finally data: {"sources": [...], "done": true}
    """
    async def event_generator():
        # 1. Memory
        
        history = request.history
        history_str = ""

        for msg in history:
         role = msg.get("role", "")
         content = msg.get("content", "")
         history_str += f"{role}: {content}\n" 

        # 2. Query rewriting (key fix)
        rewritten = rewrite_query(request.question, request.history)

        # 3. Hybrid retrieval
        sem_results = semantic_search(rewritten)
        kw_results = keyword_search(rewritten)
        fused_docs = reciprocal_rank_fusion(sem_results, kw_results)

        # 4. Reranking
        reranked_docs = rerank(rewritten, fused_docs)

        # 5. Prompt + sources
        prompt, sources = build_prompt(
            question=request.question,
            docs=reranked_docs,
            # history_str=history_str,
            rewritten_query=rewritten,
        )

        # 6. Stream tokens
        full_answer = ""
        for token in stream_answer(prompt):
            full_answer += token
            yield f"data: {json.dumps({'token': token})}\n\n"

        # 7. Hallucination check on completed answer
        checked_answer = add_confidence_note(full_answer, reranked_docs)
        if checked_answer != full_answer:
            suffix = checked_answer[len(full_answer):]
            yield f"data: {json.dumps({'token': suffix})}\n\n"

        # 8. Final metadata frame
        yield f"data: {json.dumps({'sources': sources, 'rewritten_query': rewritten, 'done': True})}\n\n"

    return StreamingResponse(
        event_generator(),
        media_type="text/event-stream",
        headers={"Cache-Control": "no-cache", "X-Accel-Buffering": "no"},
    )


@app.get("/health")
def health():
    return {"status": "ok"}