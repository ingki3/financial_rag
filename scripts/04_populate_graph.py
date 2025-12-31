#!/usr/bin/env python
"""추출된 Knowledge Triplets를 Graphiti/FalkorDB에 저장하는 스크립트"""
import os
import sys
import asyncio
import argparse
import json
import logging
from pathlib import Path
from datetime import datetime
from dotenv import load_dotenv

load_dotenv()

# 성능 최적화: SEMAPHORE_LIMIT 설정 (동시 LLM 호출 수 제한)
# "Max pending queries exceeded" 에러를 줄이기 위해 최소값으로 설정
# Graphiti 내부 fulltext 쿼리 때문에 매우 낮은 값 필요
# API 계정의 Tier가 높을수록 이 값을 높일 수 있지만, DB 부하를 고려해야 합니다.
if not os.getenv("SEMAPHORE_LIMIT"):
    os.environ["SEMAPHORE_LIMIT"] = "1"
    logging.info(f"SEMAPHORE_LIMIT set to {os.getenv('SEMAPHORE_LIMIT')}")

# 프로젝트 루트 추가
sys.path.insert(0, str(Path(__file__).parent.parent))

from app.services.graphiti_manager import GraphitiPopulator

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


async def populate_single_ticker(ticker: str) -> dict:
    """단일 티커 저장"""
    populator = GraphitiPopulator(
        extracted_dir="./data/extracted",
        host=os.getenv("FALKORDB_HOST", "localhost"),
        port=int(os.getenv("FALKORDB_PORT", "6379"))
    )
    
    print("=" * 60)
    print(f"📊 Knowledge Graph 저장 - {ticker}")
    print("=" * 60)
    print(f"📁 데이터 위치: ./data/extracted/{ticker}/")
    print(f"🗄️ FalkorDB: {populator.manager.host}:{populator.manager.port}")
    print(f"🧠 LLM: {populator.manager.model}")
    print("=" * 60)
    
    files = populator.get_ticker_files(ticker)
    print(f"\n📄 처리할 파일: {len(files)}개")
    
    if not files:
        print(f"❌ {ticker}에 대한 추출 파일이 없습니다.")
        return {}
    
    print("\n🚀 저장 시작...\n")
    
    start_time = datetime.now()
    stats = await populator.populate_ticker(ticker)
    elapsed = (datetime.now() - start_time).total_seconds()
    
    print(f"\n{'=' * 60}")
    print(f"📊 저장 결과 요약 - {ticker}")
    print(f"{'=' * 60}")
    print(f"처리된 파일: {stats['files_processed']}개")
    print(f"\n카테고리별 Episode 수:")
    print(f"   🔵 Opportunities: {stats['opportunities']}개")
    print(f"   🔴 Risks: {stats['risks']}개")
    print(f"   📅 Events: {stats['events']}개")
    print(f"   📈 Strategies: {stats['strategies']}개")
    print(f"   💰 Financials: {stats['financials']}개")
    print(f"\n   총 Episodes: {stats['total_episodes']}개")
    print(f"   소요 시간: {elapsed:.1f}초")
    print(f"{'=' * 60}")
    
    # 결과 저장
    result_dir = Path("./result")
    result_dir.mkdir(exist_ok=True)
    result_file = result_dir / f"populate_{ticker}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
    
    with open(result_file, 'w', encoding='utf-8') as f:
        json.dump({
            "ticker": ticker,
            "stats": stats,
            "elapsed_seconds": elapsed,
            "completed_at": datetime.now().isoformat()
        }, f, ensure_ascii=False, indent=2)
    
    print(f"\n📁 결과 저장: {result_file}")
    
    return stats


async def populate_all_tickers():
    """모든 티커 저장"""
    populator = GraphitiPopulator(
        extracted_dir="./data/extracted",
        host=os.getenv("FALKORDB_HOST", "localhost"),
        port=int(os.getenv("FALKORDB_PORT", "6379"))
    )
    
    print("=" * 60)
    print("📊 Knowledge Graph 전체 저장")
    print("=" * 60)
    print(f"📋 대상 기업: {', '.join(populator.TICKERS)}")
    print("=" * 60)
    
    all_stats = await populator.populate_all()
    
    # 전체 통계
    total = {
        "files_processed": 0,
        "opportunities": 0,
        "risks": 0,
        "events": 0,
        "strategies": 0,
        "financials": 0,
        "total_episodes": 0
    }
    
    for ticker, stats in all_stats.items():
        for key in total.keys():
            total[key] += stats.get(key, 0)
    
    print(f"\n{'=' * 60}")
    print("📊 전체 저장 결과 요약")
    print(f"{'=' * 60}")
    
    for ticker, stats in all_stats.items():
        print(f"\n{ticker}:")
        print(f"   Episodes: {stats['total_episodes']}개")
    
    print(f"\n{'=' * 60}")
    print(f"전체 총 Episodes: {total['total_episodes']}개")
    print(f"{'=' * 60}")
    
    return all_stats


def main():
    parser = argparse.ArgumentParser(description="Knowledge Graph Populator")
    parser.add_argument(
        "--ticker",
        type=str,
        help="특정 티커만 저장 (예: AAPL)"
    )
    parser.add_argument(
        "--all",
        action="store_true",
        help="모든 티커 저장"
    )
    
    args = parser.parse_args()
    
    if args.ticker:
        asyncio.run(populate_single_ticker(args.ticker.upper()))
    elif args.all:
        asyncio.run(populate_all_tickers())
    else:
        print("사용법:")
        print("  python scripts/04_populate_graph.py --ticker AAPL   # 특정 티커")
        print("  python scripts/04_populate_graph.py --all           # 전체 티커")


if __name__ == "__main__":
    main()

