#!/usr/bin/env python
"""Knowledge Triplet 추출 테스트 스크립트 (AAPL만)"""
import os
import sys
import json
import logging
from pathlib import Path
from datetime import datetime

# 프로젝트 루트를 path에 추가
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

from dotenv import load_dotenv
from app.services.triplet_extractor import TripletExtractorBatch

# 로깅 설정
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s",
    datefmt="%Y-%m-%d %H:%M:%S"
)
logger = logging.getLogger(__name__)


def main():
    load_dotenv()

    # Gemini API 키 확인
    api_key = os.getenv("GEMINI_API_KEY") or os.getenv("GOOGLE_API_KEY")
    if not api_key:
        logger.warning("⚠️ GEMINI_API_KEY가 설정되지 않았습니다. 기본 인증 사용")

    print("=" * 60)
    print("Knowledge Triplet Extractor - AAPL 테스트")
    print("Model: gemini-3-flash-preview")
    print("Mode: filing (섹션 통합)")
    print("=" * 60)

    batch_extractor = TripletExtractorBatch(
        parsed_dir="./data/parsed",
        output_dir="./data/extracted",
        model="gemini-3-flash-preview",
        combine_sections_per_filing=True,  # filing 모드
    )

    # AAPL만 처리하도록 수정
    original_tickers = batch_extractor.TICKERS
    batch_extractor.TICKERS = ["AAPL"]

    print(f"\n📋 대상 기업: {', '.join(batch_extractor.TICKERS)}")
    print(f"📄 공시 유형: {', '.join(batch_extractor.FILING_TYPES)}")
    print(f"🎯 추출 대상 섹션:")
    for ftype, sections in batch_extractor.TARGET_SECTIONS.items():
        print(f"   {ftype}: {', '.join(sections)}")
    print("=" * 60)

    # 추출 실행
    print("\n🚀 Triplet 추출 시작...\n")
    print("⏳ 이 작업은 시간이 소요됩니다 (API 호출 제한으로 인해)")
    print("-" * 60)
    
    results = batch_extractor.extract_all()

    # 결과 요약
    summary = batch_extractor.get_summary(results)
    
    print("\n" + "=" * 60)
    print("📊 추출 결과 요약")
    print("=" * 60)
    
    print(f"\n총 추출 작업: {summary['total_extractions']}건")
    print(f"총 Triplets: {summary['total_triplets']}개")
    
    print("\n📦 카테고리별:")
    for category, count in summary['by_category'].items():
        print(f"   {category}: {count}개")
    
    print("\n📁 기업별:")
    for ticker, count in sorted(summary['by_ticker'].items()):
        print(f"   {ticker}: {count}개")
    
    print("\n📄 공시 유형별:")
    for ftype, count in sorted(summary['by_filing_type'].items()):
        print(f"   {ftype}: {count}개")
    
    if 'mentioned_products' in summary['by_category']:
        print(f"\n🔗 연결 정보:")
        print(f"   mentioned_products: {summary['by_category']['mentioned_products']}개")
        print(f"   mentioned_persons: {summary['by_category']['mentioned_persons']}개")

    print("\n" + "-" * 60)
    print(f"✅ 추출 완료!")
    print(f"📁 저장 위치: {batch_extractor.output_dir.absolute()}")
    print("=" * 60)
    
    # 요약 정보 저장
    summary_file = batch_extractor.output_dir / "extraction_summary.json"
    summary["extracted_at"] = datetime.now().isoformat()
    summary["model"] = "gemini-3-flash-preview"
    summary["test_mode"] = True
    summary["ticker_filter"] = "AAPL"
    
    batch_extractor.output_dir.mkdir(parents=True, exist_ok=True)
    with open(summary_file, 'w', encoding='utf-8') as f:
        json.dump(summary, f, ensure_ascii=False, indent=2)


if __name__ == "__main__":
    main()

