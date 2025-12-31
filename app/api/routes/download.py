"""
Download API Router

공시 다운로드 API 엔드포인트
"""

import logging
from fastapi import APIRouter, Depends, HTTPException
from typing import Dict

from app.schemas.api_schemas import DownloadRequest, DownloadResponse
from app.api.dependencies import get_downloader
from app.services.download.sec_downloader import SECFilingDownloader

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/download", tags=["download"])


@router.post("", response_model=DownloadResponse)
async def download_filings(
    request: DownloadRequest,
    downloader: SECFilingDownloader = Depends(get_downloader)
):
    """
    ticker에 대한 공시 자료 다운로드 및 저장
    
    Args:
        request: DownloadRequest (ticker, filing_types, limits)
        downloader: SECFilingDownloader 인스턴스
    
    Returns:
        DownloadResponse (다운로드 결과)
    """
    ticker = request.ticker.upper()
    logger.info(f"Download request: ticker={ticker}, filing_types={request.filing_types}")
    
    try:
        # 다운로드 실행
        if request.filing_types:
            # 특정 공시 유형만 다운로드
            results = {}
            for filing_type in request.filing_types:
                limit = request.limits.get(filing_type) if request.limits else None
                if limit is None:
                    # 기본값 사용
                    limit = downloader.FILING_TYPES.get(filing_type, 3)
                
                count = downloader.download_filing(ticker, filing_type, limit)
                results[filing_type] = count
        else:
            # 모든 공시 유형 다운로드
            if request.limits:
                # limits가 있으면 기존 FILING_TYPES를 업데이트
                original_types = downloader.FILING_TYPES.copy()
                downloader.FILING_TYPES.update(request.limits)
                results = downloader.download_all_filings(ticker)
                downloader.FILING_TYPES = original_types  # 복원
            else:
                results = downloader.download_all_filings(ticker)
        
        total_files = sum(results.values())
        
        # 임시 디렉토리 정리
        downloader.cleanup_temp_dir()
        
        return DownloadResponse(
            ticker=ticker,
            results=results,
            total_files=total_files,
            message=f"{ticker} 공시 자료 다운로드 완료: 총 {total_files}건"
        )
        
    except Exception as e:
        logger.error(f"Error downloading filings for {ticker}: {e}")
        raise HTTPException(
            status_code=500,
            detail=f"다운로드 실패: {str(e)}"
        )

