#!/usr/bin/env python
"""SEC 10-K, 10-Q, 8-K 공시 자료 다운로드 스크립트"""
import os
import sys
import logging
from pathlib import Path

# 프로젝트 루트를 path에 추가
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

from dotenv import load_dotenv
from app.services.download.sec_downloader import SECFilingDownloader

# 로깅 설정
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s",
    datefmt="%Y-%m-%d %H:%M:%S"
)
logger = logging.getLogger(__name__)


def main():
    load_dotenv()

    print("=" * 60)
    print("SEC Filing Downloader")
    print("=" * 60)

    # SEC User-Agent 확인
    user_agent = os.getenv("SEC_USER_AGENT")
    if not user_agent or user_agent == "Your Name your.email@example.com":
        logger.warning("⚠️ SEC_USER_AGENT가 설정되지 않았습니다. 기본값 사용")
        user_agent = "FinancialKG Research research@example.com"

    downloader = SECFilingDownloader(
        data_dir="./data/raw",
        user_agent=user_agent
    )

    print(f"\n📋 대상 기업: {', '.join(downloader.TICKERS)}")
    print(f"📄 공시 유형:")
    for filing_type, limit in downloader.FILING_TYPES.items():
        print(f"   - {filing_type}: 최근 {limit}건")
    print("=" * 60)

    # 다운로드 실행
    print("\n🚀 다운로드 시작...\n")
    results = downloader.download_all()

    # 임시 디렉토리 정리
    downloader.cleanup_temp_dir()

    # 결과 요약
    print("\n" + "=" * 60)
    print("📊 다운로드 결과 요약")
    print("=" * 60)
    
    total_files = 0
    for ticker, filing_results in results.items():
        ticker_total = sum(filing_results.values())
        total_files += ticker_total
        print(f"\n{ticker}:")
        for filing_type, count in filing_results.items():
            print(f"   {filing_type}: {count}건")
        print(f"   소계: {ticker_total}건")

    print("\n" + "-" * 60)
    print(f"✅ 총 다운로드: {total_files}건")
    print(f"📁 저장 위치: ./data/raw/{{ticker}}/{{filing_type}}/")
    print("=" * 60)


if __name__ == "__main__":
    main()

