"""
API Request/Response Schemas

FastAPI 엔드포인트에서 사용하는 Pydantic 모델
"""

from pydantic import BaseModel, Field
from typing import Optional, List, Dict, Any


# ============================================================================
# Answer API Schemas
# ============================================================================

class AnswerRequest(BaseModel):
    """질의 응답 API 요청"""
    query: str = Field(..., description="사용자 질의")
    use_vector_search: bool = Field(default=False, description="Vector 검색 사용 여부")
    top_k: int = Field(default=10, ge=1, le=50, description="반환할 최대 결과 수")


class AnswerStreamChunk(BaseModel):
    """스트리밍 답변 청크"""
    chunk: str = Field(..., description="답변 텍스트 청크")
    done: bool = Field(default=False, description="스트리밍 완료 여부")


# ============================================================================
# Download API Schemas
# ============================================================================

class DownloadRequest(BaseModel):
    """공시 다운로드 API 요청"""
    ticker: str = Field(..., description="티커 심볼 (예: AAPL)")
    filing_types: Optional[List[str]] = Field(
        default=None,
        description="다운로드할 공시 유형 리스트 (None이면 모든 유형: 10-K, 10-Q, 8-K)"
    )
    limits: Optional[Dict[str, int]] = Field(
        default=None,
        description="공시 유형별 다운로드 제한 (예: {'10-K': 3, '10-Q': 12})"
    )


class DownloadResponse(BaseModel):
    """공시 다운로드 API 응답"""
    ticker: str = Field(..., description="티커 심볼")
    results: Dict[str, int] = Field(..., description="공시 유형별 다운로드 수")
    total_files: int = Field(..., description="총 다운로드된 파일 수")
    message: str = Field(..., description="처리 결과 메시지")


# ============================================================================
# Process API Schemas
# ============================================================================

class ProcessRequest(BaseModel):
    """문서 처리 및 Graph DB 적재 API 요청"""
    ticker: str = Field(..., description="티커 심볼 (예: AAPL)")
    skip_duplicates: bool = Field(
        default=True,
        description="중복 문서 건너뛰기 여부"
    )
    with_embedding: bool = Field(
        default=True,
        description="Embedding 생성 여부"
    )
    filing_types: Optional[List[str]] = Field(
        default=None,
        description="처리할 공시 유형 리스트 (None이면 모든 유형)"
    )


class ProcessResponse(BaseModel):
    """문서 처리 및 Graph DB 적재 API 응답"""
    ticker: str = Field(..., description="티커 심볼")
    processed_files: int = Field(..., description="처리된 파일 수")
    skipped_files: int = Field(..., description="건너뛴 파일 수 (중복 등)")
    graph_stats: Dict[str, Any] = Field(..., description="Graph DB 적재 통계")
    message: str = Field(..., description="처리 결과 메시지")

