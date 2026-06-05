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
from backend.logger import logger
app = FastAPI(title="Airtel RAG API")
print("API FILE IMPORTED", flush=True)
# Retrieval Cache
answer_query_counts = {}
retrieval_query_counts = {}
retrieval_cache = {}
answer_cache = {}
answer_cache_hits = 0
retrieval_cache_hits = 0
total_requests = 0
CACHE_PROMOTION_THRESHOLD = 3

class QueryRequest(BaseModel):
    question: str
    service: str | None = None   # e.g. "Prepaid", "DTH", "WiFi Broadband"
    history: list[dict] = []


@app.post("/chat/stream")
async def chat_stream(request: QueryRequest):
    logger.info("=" * 60)
    logger.info(f"QUESTION: {request.question}")
    logger.info(f"SERVICE: {request.service}")
    
    
    """
    Server-Sent Events endpoint.
    Yields: data: {"token": "..."} and finally data: {"sources": [...], "done": true}
    """
    
    async def event_generator():
        global total_requests, answer_cache_hits, retrieval_cache_hits
        
        total_requests += 1
        
        # 1. Memory Setup
        history = request.history[-6:]
        question_key = f"{request.service}:{request.question.lower().strip()}"
        answer_query_counts[question_key] = answer_query_counts.get(question_key, 0) + 1
        logger.info(
    f"QUESTION='{request.question}' "
    f"SERVICE='{request.service}'"
)
        logger.info(
    f"ANSWER QUERY COUNT = {answer_query_counts[question_key]}"
)
        
        history_str = "\n".join(
            f"{m.get('role', '')}: {m.get('content', '')}" for m in history
        )
        
        # 2. Check Answer Cache
        if question_key in answer_cache:
            answer_cache_hits += 1
            logger.info(
    f"ANSWER CACHE HIT | {question_key}"
)
            cached = answer_cache[question_key]
            yield f"data: {json.dumps({'token': cached['answer']})}\n\n"
            yield f"data: {json.dumps({'sources': cached['sources'], 'rewritten_query': request.question, 'done': True})}\n\n"
            return

        logger.info(
    f"ANSWER CACHE MISS | {question_key}"
)
        
        try:
            # 3. Query Rewriting
            rewritten = rewrite_query(request.question, history)
            logger.info(
    f"QUERY REWRITTEN | Original='{request.question}' | Rewritten='{rewritten}'"
)
            cache_key = f"{request.service}:{rewritten.lower().strip()}"
            retrieval_query_counts[cache_key] = retrieval_query_counts.get(cache_key, 0) + 1
            logger.info(
    f"RETRIEVAL QUERY COUNT = {retrieval_query_counts[cache_key]}"
)
            
            # 4. Retrieval Pipeline
            if cache_key in retrieval_cache:
                retrieval_cache_hits += 1
                logger.info(
                       f"RETRIEVAL CACHE HIT | {cache_key}"
                     )
                reranked_docs = retrieval_cache[cache_key]
            else:
                logger.info(
                    f"RETRIEVAL CACHE MISS | {cache_key}"
                 )
                sem_results = semantic_search(rewritten, request.service)
                logger.info(
                         f"SEMANTIC RETRIEVED {len(sem_results)} DOCS"
                  )

                kw_results = keyword_search(rewritten, request.service)
                logger.info(
                f"KEYWORD RETRIEVED {len(kw_results)} DOCS"
               )

                fused_docs = reciprocal_rank_fusion(sem_results, kw_results)
                logger.info(
              f"RRF PRODUCED {len(fused_docs)} DOCS"
                 )

                reranked_docs = rerank(rewritten, fused_docs)
                logger.info(
              f"RERANK COMPLETE | Top Docs={len(reranked_docs)}"
                )

                if retrieval_query_counts[cache_key] >= CACHE_PROMOTION_THRESHOLD:
                    retrieval_cache[cache_key] = reranked_docs
                    logger.info(f"PROMOTED TO RETRIEVAL CACHE: {cache_key}")
            
            # 5. Prompt Generation
            prompt, sources = build_prompt(
                question=request.question,
                docs=reranked_docs,
                rewritten_query=rewritten,
                history=history_str,
            )
            logger.info(
             f"PROMPT BUILT | Docs={len(reranked_docs)}"
             )

        except Exception as e:
            logger.exception(f"ERROR DURING RETRIEVAL: {str(e)}")
            raise

        # 6. Stream tokens
        full_answer = ""
        try:
            for token in stream_answer(prompt):
                full_answer += token
                yield f"data: {json.dumps({'token': token})}\n\n"
        except Exception as e:
            logger.exception(f"ERROR DURING STREAMING: {str(e)}")
            raise

        # 7. Hallucination check on completed answer
        checked_answer = add_confidence_note(full_answer, reranked_docs)
        if checked_answer != full_answer:
            suffix = checked_answer[len(full_answer):]
            yield f"data: {json.dumps({'token': suffix})}\n\n"
            
        if answer_query_counts[question_key] >= CACHE_PROMOTION_THRESHOLD:
            answer_cache[question_key] = {
                "answer": checked_answer,
                "sources": sources
            }
            logger.info(f"PROMOTED TO ANSWER CACHE: {question_key}")
            
        # 8. Final metadata frame
        yield f"data: {json.dumps({'sources': sources, 'rewritten_query': rewritten, 'done': True})}\n\n"

    return StreamingResponse(
        event_generator(),
        media_type="text/event-stream",
        headers={"Cache-Control": "no-cache", "X-Accel-Buffering": "no"},
    )


@app.get("/health")
def health():
    logger.info("HEALTH ENDPOINT HIT")
    return {"status": "ok"}
@app.get("/testlog")
def testlog():
    logger.info("TEST LOG HIT")
    return {"ok": True}

@app.get("/metrics")
def metrics():
    answer_rate = (answer_cache_hits / total_requests * 100) if total_requests else 0
    retrieval_rate = (retrieval_cache_hits / total_requests * 100) if total_requests else 0

    return {
        "total_requests" :total_requests,
        "answer_cache_hits": answer_cache_hits,
        "retrieval_cache_hits": retrieval_cache_hits,
        "answer_cache_hit_rate": round(answer_rate, 2),
        "retrieval_cache_hit_rate": round(retrieval_rate, 2),
    }

@app.get("/cache")
def cache_debug():
    return {
        "answer_cache_size": len(answer_cache),
        "retrieval_cache_size": len(retrieval_cache),
        "answer_query_counts": answer_query_counts,
        "retrieval_query_counts": retrieval_query_counts,
        "answer_keys": list(answer_cache.keys())
    }
