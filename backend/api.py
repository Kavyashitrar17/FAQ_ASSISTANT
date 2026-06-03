from fastapi import FastAPI
from fastapi.responses import StreamingResponse
from pydantic import BaseModel
import json

from backend.retrieval.semantic import semantic_search
from backend.retrieval.keyword import keyword_search
from backend.retrieval.hybrid import reciprocal_rank_fusion
# from backend.retrieval.reranker import rerank
from backend.generation.query_rewriter import rewrite_query
from backend.generation.prompt import build_prompt
from backend.generation.generator import stream_answer
from backend.generation.hallucination import add_confidence_note

app = FastAPI(title="Airtel RAG API")
# Retrieval Cache
retrieval_cache = {}
answer_cache = {}
answer_cache_hits = 0
retrieval_cache_hits = 0
total_requests = 0

class QueryRequest(BaseModel):
    question: str
    service:  str | None = None   # e.g. "Prepaid", "DTH", "WiFi Broadband"
    history:  list[dict] = []


@app.post("/chat/stream")
async def chat_stream(request: QueryRequest):
    print("POST /chat/stream CALLED")
    """
    Server-Sent Events endpoint.
    Yields: data: {"token": "..."} and finally data: {"sources": [...], "done": true}
    """
    
    async def event_generator():
      global total_requests
      total_requests += 1
      # 1. Memory
      history = request.history[-6:]
      question_key = f"{request.service}:{request.question.lower().strip()}"
      history_str = "\n".join(
        f"{m.get('role', '')}: {m.get('content', '')}"
        for m in history
    )
      if question_key in answer_cache:
       global answer_cache_hits

       answer_cache_hits += 1
       print("ANSWER CACHE HIT")
       
       cached = answer_cache[question_key]

       yield f"data: {json.dumps({'token': cached['answer']})}\n\n"

       yield f"data: {json.dumps({'sources': cached['sources'], 'rewritten_query': request.question, 'done': True})}\n\n"

       return
      print("ANSWER CACHE MISS")
        
      try:
        rewritten = rewrite_query(
            request.question,
            request.history[-6:]
          )
        print("1. Query rewritten")
        cache_key = f"{request.service}:{rewritten.lower().strip()}"
        if cache_key in retrieval_cache:
          global retrieval_cache_hits

          retrieval_cache_hits += 1
          print("CACHE HIT")

          reranked_docs = retrieval_cache[cache_key]

        else:
           print("CACHE MISS")

           sem_results = semantic_search(
            rewritten,
            request.service
            )
           print("2. Semantic done")

           kw_results = keyword_search(
             rewritten,
             request.service
            )
           print("3. Keyword done")

           fused_docs = reciprocal_rank_fusion(
            sem_results,
            kw_results
            )
           print("4. Fusion done")

           reranked_docs = fused_docs[:5]
           print("5. Rerank done")

           retrieval_cache[cache_key] = reranked_docs
        prompt, sources = build_prompt(
            question=request.question,
             docs=reranked_docs,
                rewritten_query=rewritten,
                history=history_str,
            )
        print("6. Prompt built")   

           

      except Exception as e:
            print("ERROR:", str(e))
            raise
   
       
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
      answer_cache[question_key] = {
        "answer": checked_answer,
         "sources": sources
          } 
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
@app.get("/metrics")
def metrics():

    answer_rate = (
        answer_cache_hits / total_requests * 100
        if total_requests else 0
    )

    retrieval_rate = (
        retrieval_cache_hits / total_requests * 100
        if total_requests else 0
    )

    return {
        "total_requests": total_requests,
        "answer_cache_hits": answer_cache_hits,
        "retrieval_cache_hits": retrieval_cache_hits,
        "answer_cache_hit_rate": round(answer_rate, 2),
        "retrieval_cache_hit_rate": round(retrieval_rate, 2),
    }