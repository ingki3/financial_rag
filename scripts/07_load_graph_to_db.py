#!/usr/bin/env python
"""
Phase 7: Graph DB 저장

Static/Dynamic Graph JSON 파일을 FalkorDB에 적재

사용법:
    # 단일 티커
    python scripts/07_load_graph_to_db.py --ticker AAPL
    
    # 여러 티커
    python scripts/07_load_graph_to_db.py --ticker AAPL AMZN GOOGL META MSFT NVDA TSLA
    
    # 검증만
    python scripts/07_load_graph_to_db.py --verify
    
    # 초기화 후 적재
    python scripts/07_load_graph_to_db.py --ticker AAPL --initialize
"""

import argparse
import json
import logging
import sys
from datetime import datetime
from pathlib import Path

# 프로젝트 루트 추가
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

from dotenv import load_dotenv
load_dotenv()

from app.services.graph_loader import GraphLoader, load_graph_file

# 로깅 설정
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# 기본 티커 목록
DEFAULT_TICKERS = ["AAPL", "AMZN", "GOOGL", "META", "MSFT", "NVDA", "TSLA"]

# 그래프 데이터 디렉토리
GRAPH_DIR = project_root / "data" / "graph"


def load_ticker_graphs(loader: GraphLoader, ticker: str) -> dict:
    """단일 티커의 Static/Dynamic Graph 적재
    
    Args:
        loader: GraphLoader 인스턴스
        ticker: 티커 심볼
        
    Returns:
        적재 결과 통계
    """
    ticker = ticker.upper()
    result = {
        "ticker": ticker,
        "static": None,
        "dynamic": None,
        "errors": []
    }
    
    # Static Graph 로드
    static_file = GRAPH_DIR / f"{ticker}_static_graph.json"
    if static_file.exists():
        try:
            logger.info(f"📂 Loading static graph: {static_file}")
            static_graph = load_graph_file(static_file)
            result["static"] = loader.load_static_graph(ticker, static_graph)
        except Exception as e:
            logger.error(f"Failed to load static graph for {ticker}: {e}")
            result["errors"].append(f"static: {e}")
    else:
        logger.warning(f"Static graph file not found: {static_file}")
        result["errors"].append(f"static file not found")
    
    # Dynamic Graph 로드
    dynamic_file = GRAPH_DIR / f"{ticker}_dynamic_graph.json"
    if dynamic_file.exists():
        try:
            logger.info(f"📂 Loading dynamic graph: {dynamic_file}")
            dynamic_graph = load_graph_file(dynamic_file)
            result["dynamic"] = loader.load_dynamic_graph(ticker, dynamic_graph)
        except Exception as e:
            logger.error(f"Failed to load dynamic graph for {ticker}: {e}")
            result["errors"].append(f"dynamic: {e}")
    else:
        logger.warning(f"Dynamic graph file not found: {dynamic_file}")
        result["errors"].append(f"dynamic file not found")
    
    return result


def print_summary(results: list, loader: GraphLoader):
    """적재 결과 요약 출력
    
    Args:
        results: 티커별 적재 결과 리스트
        loader: GraphLoader 인스턴스
    """
    print("\n" + "=" * 80)
    print("📊 Graph DB 적재 결과")
    print("=" * 80)
    
    # 티커별 결과
    for result in results:
        ticker = result["ticker"]
        errors = result["errors"]
        
        static_info = ""
        if result["static"]:
            nodes = result["static"]["nodes"]
            links = result["static"]["links"]
            static_info = f"노드={sum(nodes.values())}, 링크={links}"
        
        dynamic_info = ""
        if result["dynamic"]:
            nodes = result["dynamic"]["nodes"]
            links = result["dynamic"]["links"]
            dynamic_info = f"노드={sum(nodes.values())}, 링크={links}"
        
        status = "✅" if not errors else "⚠️"
        print(f"\n{status} {ticker}")
        if static_info:
            print(f"   Static:  {static_info}")
        if dynamic_info:
            print(f"   Dynamic: {dynamic_info}")
        if errors:
            for err in errors:
                print(f"   ❌ Error: {err}")
    
    # 전체 통계
    stats = loader.get_stats()
    print("\n" + "-" * 80)
    print("📈 전체 통계")
    print("-" * 80)
    print(f"  노드 생성: {stats['nodes_created']}")
    print(f"  링크 생성: {stats['links_created']}")
    print(f"  Embedding 저장: {stats['embeddings_stored']}")
    print(f"  오류: {stats['errors']}")


def print_verification(loader: GraphLoader):
    """검증 결과 출력
    
    Args:
        loader: GraphLoader 인스턴스
    """
    print("\n" + "=" * 80)
    print("🔍 Graph DB 검증 결과")
    print("=" * 80)
    
    verify = loader.verify()
    
    print("\n📦 노드 수:")
    for label, count in sorted(verify["nodes"].items()):
        print(f"  {label}: {count}")
    print(f"  ─────────────")
    print(f"  총계: {verify['total_nodes']}")
    
    print("\n🔗 링크 수:")
    for rel_type, count in sorted(verify["links"].items()):
        print(f"  {rel_type}: {count}")
    print(f"  ─────────────")
    print(f"  총계: {verify['total_links']}")
    
    print("\n🧬 Embedding 수:")
    for label, count in sorted(verify["embeddings"].items()):
        print(f"  {label}: {count}")
    print(f"  ─────────────")
    print(f"  총계: {verify['total_embeddings']}")


def main():
    parser = argparse.ArgumentParser(
        description="Load graph data to FalkorDB",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
예시:
  # 단일 티커 적재
  python scripts/07_load_graph_to_db.py --ticker AAPL
  
  # 여러 티커 적재
  python scripts/07_load_graph_to_db.py --ticker AAPL AMZN GOOGL
  
  # 전체 티커 적재
  python scripts/07_load_graph_to_db.py --all
  
  # 검증만
  python scripts/07_load_graph_to_db.py --verify
        """
    )
    
    parser.add_argument(
        "--ticker", 
        type=str, 
        nargs="+",
        help="티커 심볼 (예: AAPL AMZN)"
    )
    parser.add_argument(
        "--all", 
        action="store_true",
        help="모든 기본 티커 적재"
    )
    parser.add_argument(
        "--initialize",
        action="store_true",
        help="인덱스 초기화 후 적재"
    )
    parser.add_argument(
        "--verify",
        action="store_true",
        help="적재 결과 검증만 수행"
    )
    parser.add_argument(
        "--host",
        type=str,
        default=None,
        help="FalkorDB 호스트 (기본값: 환경변수 또는 localhost)"
    )
    parser.add_argument(
        "--port",
        type=int,
        default=None,
        help="FalkorDB 포트 (기본값: 환경변수 또는 6379)"
    )
    parser.add_argument(
        "--graph-name",
        type=str,
        default="financial_kg",
        help="그래프 이름 (기본값: financial_kg)"
    )
    
    args = parser.parse_args()
    
    # 티커 결정
    if args.all:
        tickers = DEFAULT_TICKERS
    elif args.ticker:
        tickers = [t.upper() for t in args.ticker]
    elif not args.verify:
        parser.error("--ticker, --all, 또는 --verify 중 하나를 지정하세요")
        return
    else:
        tickers = []
    
    start_time = datetime.now()
    
    print("=" * 80)
    print("🚀 Phase 7: Graph DB 저장")
    print("=" * 80)
    print(f"시작 시간: {start_time.strftime('%Y-%m-%d %H:%M:%S')}")
    if tickers:
        print(f"대상 티커: {', '.join(tickers)}")
    
    # GraphLoader 초기화
    try:
        loader = GraphLoader(
            host=args.host,
            port=args.port,
            graph_name=args.graph_name
        )
        loader.connect()
        
        if args.initialize:
            logger.info("Initializing indexes...")
            loader.initialize()
        
    except Exception as e:
        logger.error(f"Failed to connect to FalkorDB: {e}")
        print("\n❌ FalkorDB 연결 실패")
        print("Docker 컨테이너가 실행 중인지 확인하세요:")
        print("  docker run -d --name falkordb -p 6379:6379 falkordb/falkordb:latest")
        return
    
    try:
        # 적재 수행
        if tickers:
            results = []
            for ticker in tickers:
                print(f"\n{'─' * 60}")
                print(f"🏢 {ticker} 적재 중...")
                print("─" * 60)
                result = load_ticker_graphs(loader, ticker)
                results.append(result)
            
            # 결과 출력
            print_summary(results, loader)
        
        # 검증
        if args.verify or tickers:
            print_verification(loader)
        
    finally:
        loader.close()
    
    end_time = datetime.now()
    duration = (end_time - start_time).total_seconds()
    
    print("\n" + "=" * 80)
    print(f"✅ 완료! (소요 시간: {duration:.1f}초)")
    print("=" * 80)


if __name__ == "__main__":
    main()

