#!/usr/bin/env python
"""SEC 공시 파싱 스크립트"""
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
from app.services.filing_parser import FilingParserBatch, ParsedFiling

# 로깅 설정
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s",
    datefmt="%Y-%m-%d %H:%M:%S"
)
logger = logging.getLogger(__name__)


def save_parsed_results(results: list[ParsedFiling], output_dir: Path):
    """파싱 결과를 JSON 파일로 저장"""
    output_dir.mkdir(parents=True, exist_ok=True)
    
    for parsed in results:
        ticker = parsed.metadata.ticker
        filing_type = parsed.metadata.filing_type
        accession = parsed.metadata.accession_number
        
        # 출력 경로: data/parsed/{ticker}/{filing_type}/{accession}.json
        ticker_dir = output_dir / ticker / filing_type
        ticker_dir.mkdir(parents=True, exist_ok=True)
        
        output_file = ticker_dir / f"{accession}.json"
        
        # 저장할 데이터
        data = {
            "metadata": {
                "ticker": parsed.metadata.ticker,
                "filing_type": parsed.metadata.filing_type,
                "accession_number": parsed.metadata.accession_number,
                "file_path": parsed.metadata.file_path,
                "text_length": parsed.metadata.text_length,
                "parsed_at": datetime.now().isoformat()
            },
            "sections": parsed.sections,
            # full_text는 용량 문제로 별도 파일로 저장할 수도 있음
            "full_text": parsed.full_text
        }
        
        with open(output_file, 'w', encoding='utf-8') as f:
            json.dump(data, f, ensure_ascii=False, indent=2)
    
    logger.info(f"💾 {len(results)}개 파일 저장 완료: {output_dir}")


def main():
    load_dotenv()

    print("=" * 60)
    print("SEC Filing Parser")
    print("=" * 60)

    batch_parser = FilingParserBatch(data_dir="./data/raw")

    print(f"\n📋 대상 기업: {', '.join(batch_parser.TICKERS)}")
    print(f"📄 공시 유형: {', '.join(batch_parser.FILING_TYPES)}")
    print("=" * 60)

    # 파싱 실행
    print("\n🚀 파싱 시작...\n")
    results = batch_parser.parse_all()

    # 결과 저장
    output_dir = Path("./data/parsed")
    save_parsed_results(results, output_dir)

    # 결과 요약
    summary = batch_parser.get_summary(results)
    
    print("\n" + "=" * 60)
    print("📊 파싱 결과 요약")
    print("=" * 60)
    
    print(f"\n총 파싱된 공시: {summary['total_filings']}건")
    print(f"추출된 섹션 수: {summary['sections_extracted']}개")
    print(f"총 텍스트 길이: {summary['total_text_length']:,}자")
    
    print("\n📁 기업별:")
    for ticker, count in sorted(summary['by_ticker'].items()):
        print(f"   {ticker}: {count}건")
    
    print("\n📄 공시 유형별:")
    for ftype, count in sorted(summary['by_type'].items()):
        print(f"   {ftype}: {count}건")

    print("\n" + "-" * 60)
    print(f"✅ 파싱 완료!")
    print(f"📁 저장 위치: {output_dir.absolute()}")
    print("=" * 60)
    
    # 요약 정보도 저장
    summary_file = output_dir / "parsing_summary.json"
    summary["parsed_at"] = datetime.now().isoformat()
    with open(summary_file, 'w', encoding='utf-8') as f:
        json.dump(summary, f, ensure_ascii=False, indent=2)


if __name__ == "__main__":
    main()

