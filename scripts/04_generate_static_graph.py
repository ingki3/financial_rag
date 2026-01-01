"""
Phase 4.5: Static Graph 생성 스크립트

extracted 데이터를 읽어서 Static 노드(Company, Product, Person)와
이들 간의 링크를 생성하여 {TICKER}_static_graph.json 파일로 저장합니다.

사용법:
    python scripts/04_generate_static_graph.py --ticker AAPL
    python scripts/04_generate_static_graph.py --ticker AAPL TSLA
"""

import argparse
import json
import logging
import sys
from pathlib import Path

# 프로젝트 루트를 경로에 추가
sys.path.insert(0, str(Path(__file__).parent.parent))

from app.services.processing.graph_generator import generate_static_graph

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


def parse_args() -> argparse.Namespace:
    """커맨드라인 인자 파싱"""
    parser = argparse.ArgumentParser(
        description="Static Graph 생성 스크립트",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
예제:
  # 단일 티커 처리
  python scripts/04_generate_static_graph.py --ticker AAPL
  
  # 여러 티커 처리
  python scripts/04_generate_static_graph.py --ticker AAPL TSLA
        """
    )
    parser.add_argument(
        "--ticker",
        type=str,
        nargs='+',
        required=True,
        help="처리할 티커 심볼 (하나 이상 지정 가능, 예: AAPL 또는 AAPL TSLA)"
    )
    return parser.parse_args()


def main():
    """Static graph 생성 및 저장"""
    args = parse_args()
    tickers = [t.upper() for t in args.ticker]  # 대문자로 변환
    
    for ticker in tickers:
        logger.info(f"🚀 Processing {ticker}...")
        
        extracted_dir = Path(f"data/extracted/{ticker}")
        if not extracted_dir.exists():
            logger.error(f"Extracted directory not found: {extracted_dir}")
            continue
        
        # Static graph 생성
        try:
            static_graph = generate_static_graph(ticker, extracted_dir)
        except Exception as e:
            logger.error(f"Error generating static graph for {ticker}: {e}", exc_info=True)
            continue
        
        # 저장
        output_dir = Path("data/graph")
        output_dir.mkdir(parents=True, exist_ok=True)
        
        output_path = output_dir / f"{ticker}_static_graph.json"
        
        try:
            with open(output_path, 'w', encoding='utf-8') as f:
                json.dump(static_graph, f, indent=2, ensure_ascii=False)
            
            logger.info(f"✅ Saved: {output_path}")
            
            # 요약 출력
            nodes = static_graph["nodes"]
            logger.info(
                f"📊 Summary: "
                f"Company={len(nodes['Company'])}, "
                f"Products={len(nodes['Product'])}, "
                f"Persons={len(nodes['Person'])}, "
                f"Links={len(static_graph['links'])}"
            )
            
        except Exception as e:
            logger.error(f"Error saving static graph for {ticker}: {e}", exc_info=True)
            continue
    
    logger.info("✅ Static graph generation completed!")


if __name__ == "__main__":
    main()

