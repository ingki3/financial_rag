#!/usr/bin/env python
"""특정 티커의 데이터를 FalkorDB에서 삭제하는 스크립트"""
import os
import sys
import argparse
import logging
from pathlib import Path
from dotenv import load_dotenv

load_dotenv()

# 프로젝트 루트 추가
sys.path.insert(0, str(Path(__file__).parent.parent))

from app.services.falkor_driver_ext import FalkorDriverWithTimeout
from falkordb import FalkorDB

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


def delete_ticker_data(ticker: str, host: str = "localhost", port: int = 6379, database: str = "default_db"):
    """특정 티커의 모든 데이터 삭제"""
    logger.info(f"Deleting data for ticker: {ticker}")
    
    # FalkorDB 연결
    db = FalkorDB(host=host, port=port)
    graph = db.select_graph(database)
    
    try:
        # 1. group_id가 ticker인 모든 엣지(RELATES_TO) 삭제
        logger.info(f"Deleting edges with group_id='{ticker}'...")
        delete_edges_query = """
        MATCH ()-[e:RELATES_TO]->()
        WHERE e.group_id = $group_id
        DELETE e
        """
        result = graph.query(delete_edges_query, {"group_id": ticker})
        deleted_edges = len(result.result_set) if result.result_set else 0
        logger.info(f"Deleted {deleted_edges} edges")
        
        # 2. group_id가 ticker인 모든 Episode 노드 삭제
        logger.info(f"Deleting Episode nodes with group_id='{ticker}'...")
        delete_episodes_query = """
        MATCH (n:Episode)
        WHERE n.group_id = $group_id
        DELETE n
        """
        result = graph.query(delete_episodes_query, {"group_id": ticker})
        deleted_episodes = len(result.result_set) if result.result_set else 0
        logger.info(f"Deleted {deleted_episodes} Episode nodes")
        
        # 3. group_id가 ticker인 모든 Entity 노드 삭제 (연결이 없는 경우)
        logger.info(f"Deleting Entity nodes with group_id='{ticker}'...")
        # 먼저 연결이 있는 Entity는 건너뛰고, 연결이 없는 Entity만 삭제
        delete_entities_query = """
        MATCH (n:Entity)
        WHERE n.group_id = $group_id
        AND NOT (n)-[:RELATES_TO]-()
        DELETE n
        """
        result = graph.query(delete_entities_query, {"group_id": ticker})
        deleted_entities = len(result.result_set) if result.result_set else 0
        logger.info(f"Deleted {deleted_entities} Entity nodes")
        
        logger.info(f"✅ Successfully deleted all data for ticker: {ticker}")
        logger.info(f"   - Edges: {deleted_edges}")
        logger.info(f"   - Episodes: {deleted_episodes}")
        logger.info(f"   - Entities: {deleted_entities}")
        
    except Exception as e:
        logger.error(f"❌ Error deleting data for {ticker}: {e}")
        raise


def main():
    parser = argparse.ArgumentParser(description="Delete ticker data from FalkorDB")
    parser.add_argument(
        "--ticker",
        type=str,
        required=True,
        help="Ticker to delete (e.g., NVDA)"
    )
    parser.add_argument(
        "--host",
        type=str,
        default=os.getenv("FALKORDB_HOST", "localhost"),
        help="FalkorDB host"
    )
    parser.add_argument(
        "--port",
        type=int,
        default=int(os.getenv("FALKORDB_PORT", "6379")),
        help="FalkorDB port"
    )
    parser.add_argument(
        "--database",
        type=str,
        default="default_db",
        help="FalkorDB database/graph name"
    )
    
    args = parser.parse_args()
    
    print("=" * 60)
    print(f"🗑️  데이터 삭제 - {args.ticker}")
    print("=" * 60)
    print(f"FalkorDB: {args.host}:{args.port}")
    print(f"Database: {args.database}")
    print("=" * 60)
    
    # 확인 메시지
    confirm = input(f"\n⚠️  '{args.ticker}' 티커의 모든 데이터를 삭제하시겠습니까? (yes/no): ")
    if confirm.lower() != "yes":
        print("❌ 삭제가 취소되었습니다.")
        return
    
    delete_ticker_data(
        ticker=args.ticker.upper(),
        host=args.host,
        port=args.port,
        database=args.database
    )


if __name__ == "__main__":
    main()

