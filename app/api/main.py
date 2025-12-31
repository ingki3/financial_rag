"""
FastAPI Application Main Entry Point

API 앱 진입점 및 전역 설정
"""

import logging
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.api.routes import answer, download, process

# 로깅 설정
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)

logger = logging.getLogger(__name__)

# FastAPI 앱 생성
app = FastAPI(
    title="Financial Knowledge Graph API",
    description="금융 공시 문서 기반 Knowledge Graph 질의 응답 시스템",
    version="1.0.0"
)

# CORS 설정
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # 프로덕션에서는 특정 도메인으로 제한
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# 라우터 등록
app.include_router(answer.router)
app.include_router(download.router)
app.include_router(process.router)


@app.get("/")
async def root():
    """루트 엔드포인트"""
    return {
        "message": "Financial Knowledge Graph API",
        "version": "1.0.0",
        "endpoints": {
            "answer": "/answer",
            "download": "/download",
            "process": "/process",
            "docs": "/docs"
        }
    }


@app.get("/health")
async def health_check():
    """헬스체크 엔드포인트"""
    return {"status": "healthy"}


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)

