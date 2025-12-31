"""
Process API Router

문서 처리 및 Graph DB 적재 API 엔드포인트
"""

import logging
from fastapi import APIRouter, Depends, HTTPException, BackgroundTasks

from app.schemas.api_schemas import ProcessRequest, ProcessResponse
from app.api.dependencies import get_document_processor
from app.services.processing.document_processor import DocumentProcessor

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/process", tags=["process"])


@router.post("", response_model=ProcessResponse)
async def process_documents(
    request: ProcessRequest,
    background_tasks: BackgroundTasks,
    processor: DocumentProcessor = Depends(get_document_processor)
):
    """
    ticker에 대한 문서 처리 및 Graph DB 적재
    
    프로세스:
    1. 다운로드된 파일 목록 조회
    2. 중복 체크 (skip_duplicates=True인 경우)
    3. 각 파일에 대해:
       - 파싱 (FilingParser)
       - 트리플렛 추출 (TripletExtractor)
       - Static/Dynamic Graph 생성 (GraphGenerator)
       - Graph DB 적재 (GraphLoader)
    
    Args:
        request: ProcessRequest (ticker, skip_duplicates, with_embedding, filing_types)
        background_tasks: FastAPI BackgroundTasks (비동기 처리용)
        processor: DocumentProcessor 인스턴스
    
    Returns:
        ProcessResponse (처리 결과)
    """
    ticker = request.ticker.upper()
    logger.info(f"Process request: ticker={ticker}, skip_duplicates={request.skip_duplicates}")
    
    try:
        # 문서 처리 실행
        stats = processor.process_ticker(
            ticker=ticker,
            skip_duplicates=request.skip_duplicates,
            with_embedding=request.with_embedding,
            filing_types=request.filing_types
        )
        
        return ProcessResponse(
            ticker=ticker,
            processed_files=stats["processed_files"],
            skipped_files=stats["skipped_files"],
            graph_stats=stats.get("graph_stats", {}),
            message=f"{ticker} 문서 처리 완료: {stats['processed_files']}건 처리, {stats['skipped_files']}건 건너뜀"
        )
        
    except Exception as e:
        logger.error(f"Error processing documents for {ticker}: {e}")
        raise HTTPException(
            status_code=500,
            detail=f"문서 처리 실패: {str(e)}"
        )

