"""
Answer API Router

질의 응답 API 엔드포인트
"""

import logging
from fastapi import APIRouter, Depends
from fastapi.responses import StreamingResponse

from app.schemas.api_schemas import AnswerRequest
from app.api.dependencies import get_query_engine
from app.services.query.query_engine import QueryEngine

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/answer", tags=["answer"])


@router.post("")
async def answer_stream(
    request: AnswerRequest,
    query_engine: QueryEngine = Depends(get_query_engine)
):
    """
    질의에 대한 답변을 스트리밍으로 반환
    
    Args:
        request: AnswerRequest (query, use_vector_search, top_k)
        query_engine: QueryEngine 인스턴스
    
    Returns:
        Server-Sent Events (SSE) 스트리밍 응답
    """
    logger.info(f"Answer request: query='{request.query}', use_vector_search={request.use_vector_search}")
    
    # 질의 처리 (답변 생성은 스트리밍으로)
    result = query_engine.query(
        user_query=request.query,
        use_vector_search=request.use_vector_search,
        top_k=request.top_k,
        generate_answer=False  # 답변은 스트리밍으로 생성
    )
    
    # AnswerGenerator 인스턴스
    answer_generator = query_engine.answer_generator
    
    if not answer_generator:
        def error_generator():
            yield "data: 에러: 답변 생성기가 초기화되지 않았습니다.\n\n"
            yield "data: [DONE]\n\n"
        
        return StreamingResponse(
            error_generator(),
            media_type="text/event-stream",
            headers={
                "Cache-Control": "no-cache",
                "Connection": "keep-alive",
            }
        )
    
    # 스트리밍 생성기
    def generate():
        try:
            for chunk in answer_generator.generate_answer_stream(
                query=request.query,
                results=result["merged_results"],
                intent=result["intent"]
            ):
                # SSE 형식으로 전송
                yield f"data: {chunk}\n\n"
            
            # 완료 신호
            yield "data: [DONE]\n\n"
        except Exception as e:
            logger.error(f"Error in streaming answer: {e}")
            yield f"data: 에러: {str(e)}\n\n"
            yield "data: [DONE]\n\n"
    
    return StreamingResponse(
        generate(),
        media_type="text/event-stream",
        headers={
            "Cache-Control": "no-cache",
            "Connection": "keep-alive",
            "X-Accel-Buffering": "no",  # Nginx 버퍼링 비활성화
        }
    )

