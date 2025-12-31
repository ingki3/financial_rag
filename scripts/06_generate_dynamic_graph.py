"""
Phase 6: Dynamic Graph 생성 스크립트

extracted 데이터를 읽어서 Dynamic 노드(Document, Section, Risk, Opportunity, Event, Technology)와
이들 간의 링크를 생성하여 {TICKER}_dynamic_graph.json 파일로 저장합니다.
Embedding도 함께 생성합니다 (Risk, Opportunity, Event, Technology 노드).

사용법:
    python scripts/06_generate_dynamic_graph.py --ticker AAPL
    python scripts/06_generate_dynamic_graph.py --ticker AAPL TSLA
    python scripts/06_generate_dynamic_graph.py --ticker AAPL AMZN GOOGL META MSFT NVDA TSLA
    python scripts/06_generate_dynamic_graph.py --ticker AAPL --no-embedding  # Embedding 생성 스킵
"""

import argparse
import json
import logging
import sys
from pathlib import Path

# 프로젝트 루트를 경로에 추가
sys.path.insert(0, str(Path(__file__).parent.parent))

from app.services.dynamic_graph_generator import generate_dynamic_graph

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


def parse_args() -> argparse.Namespace:
    """커맨드라인 인자 파싱"""
    parser = argparse.ArgumentParser(
        description="Dynamic Graph 생성 스크립트",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
예제:
  # 단일 티커 처리
  python scripts/06_generate_dynamic_graph.py --ticker AAPL
  
  # 여러 티커 처리
  python scripts/06_generate_dynamic_graph.py --ticker AAPL TSLA
  
  # 전체 티커 처리
  python scripts/06_generate_dynamic_graph.py --ticker AAPL AMZN GOOGL META MSFT NVDA TSLA
  
  # Embedding 생성 스킵
  python scripts/06_generate_dynamic_graph.py --ticker AAPL --no-embedding
        """
    )
    parser.add_argument(
        "--ticker",
        type=str,
        nargs='+',
        required=True,
        help="처리할 티커 심볼 (하나 이상 지정 가능)"
    )
    parser.add_argument(
        "--no-embedding",
        action="store_true",
        help="Embedding 생성 스킵 (기본: 생성함)"
    )
    return parser.parse_args()


def main():
    """Dynamic graph 생성 및 저장"""
    args = parse_args()
    tickers = [t.upper() for t in args.ticker]
    with_embedding = not args.no_embedding
    
    if with_embedding:
        logger.info("📍 Embedding generation: ENABLED")
    else:
        logger.info("📍 Embedding generation: DISABLED")
    
    for ticker in tickers:
        logger.info(f"{'='*60}")
        logger.info(f"🚀 Processing {ticker}...")
        logger.info(f"{'='*60}")
        
        # 1. extracted 디렉토리 확인
        extracted_dir = Path(f"data/extracted/{ticker}")
        if not extracted_dir.exists():
            logger.error(f"Extracted directory not found: {extracted_dir}")
            continue
        
        # 2. Static graph 로드
        static_graph_path = Path(f"data/graph/{ticker}_static_graph.json")
        if not static_graph_path.exists():
            logger.error(f"Static graph not found: {static_graph_path}")
            logger.error("Please run Phase 5 (Static Graph generation) first.")
            continue
        
        try:
            with open(static_graph_path, 'r', encoding='utf-8') as f:
                static_graph = json.load(f)
        except Exception as e:
            logger.error(f"Error loading static graph: {e}")
            continue
        
        # 3. extracted 파일 목록
        extracted_files = list(extracted_dir.rglob("*.json"))
        if not extracted_files:
            logger.warning(f"No extracted files found in {extracted_dir}")
            continue
        
        logger.info(f"Found {len(extracted_files)} extracted files")
        
        # 4. Dynamic graph 생성
        try:
            dynamic_graph = generate_dynamic_graph(
                ticker, 
                extracted_files, 
                static_graph,
                with_embedding=with_embedding
            )
        except Exception as e:
            logger.error(f"Error generating dynamic graph for {ticker}: {e}", exc_info=True)
            continue
        
        # 5. 저장
        output_dir = Path("data/graph")
        output_dir.mkdir(parents=True, exist_ok=True)
        
        output_path = output_dir / f"{ticker}_dynamic_graph.json"
        
        try:
            with open(output_path, 'w', encoding='utf-8') as f:
                json.dump(dynamic_graph, f, indent=2, ensure_ascii=False)
            
            logger.info(f"✅ Saved: {output_path}")
            
            # 요약 출력
            nodes = dynamic_graph["nodes"]
            links = dynamic_graph["links"]
            
            logger.info(f"📊 Summary:")
            logger.info(f"   Nodes:")
            for node_type, node_list in nodes.items():
                logger.info(f"     - {node_type}: {len(node_list)}")
            logger.info(f"   Links: {len(links)}")
            
            # 링크 타입별 통계
            link_types = {}
            for link in links:
                lt = link.get("relationship_type", "UNKNOWN")
                link_types[lt] = link_types.get(lt, 0) + 1
            
            logger.info(f"   Link breakdown:")
            for lt, count in sorted(link_types.items()):
                logger.info(f"     - {lt}: {count}")
            
            # Embedding 통계
            if with_embedding:
                embedding_count = 0
                for node_type in ["Risk", "Opportunity", "Event", "Technology"]:
                    for node in nodes.get(node_type, []):
                        if node.get("description_embedding"):
                            embedding_count += 1
                logger.info(f"   Embeddings generated: {embedding_count}")
            
        except Exception as e:
            logger.error(f"Error saving dynamic graph for {ticker}: {e}", exc_info=True)
            continue
    
    logger.info(f"\n{'='*60}")
    logger.info("✅ Dynamic graph generation completed!")
    logger.info(f"{'='*60}")


if __name__ == "__main__":
    main()

