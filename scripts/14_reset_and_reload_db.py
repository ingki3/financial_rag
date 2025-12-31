"""
데이터베이스 삭제 및 재적재 스크립트

financial_kg 그래프를 삭제하고 다시 적재합니다.
"""

import sys
import os
from pathlib import Path

# 프로젝트 루트를 Python 경로에 추가
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

from dotenv import load_dotenv
load_dotenv()

import logging
from falkordb import FalkorDB
from app.services.graph_loader import GraphLoader

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


def reset_and_reload():
    """데이터베이스 삭제 및 재적재"""
    
    print("=" * 80)
    print("데이터베이스 삭제 및 재적재")
    print("=" * 80)
    
    # FalkorDB 연결
    host = os.getenv("FALKORDB_HOST", "localhost")
    port = int(os.getenv("FALKORDB_PORT", "6379"))
    graph_name = "financial_kg"
    
    try:
        client = FalkorDB(host=host, port=port)
        
        # 그래프 삭제
        print(f"\n🗑️  그래프 삭제 중: {graph_name}")
        try:
            graph = client.select_graph(graph_name)
            # 모든 노드와 링크 삭제
            result = graph.query("MATCH (n) DETACH DELETE n")
            print(f"  ✅ 모든 노드 및 링크 삭제 완료")
        except Exception as e:
            print(f"  ⚠️  그래프가 없거나 이미 삭제됨: {e}")
        
        # GraphLoader로 재적재
        print(f"\n📥 데이터 재적재 중...")
        loader = GraphLoader(graph_name=graph_name)
        loader.connect()
        loader.initialize()
        
        # Static 그래프 적재
        graph_dir = Path("data/graph")
        static_files = sorted(graph_dir.glob("*_static_graph.json"))
        
        print(f"\n📦 Static 그래프 적재 ({len(static_files)}개):")
        for static_file in static_files:
            ticker = static_file.stem.replace("_static_graph", "").upper()
            print(f"  - {ticker}...", end=" ")
            try:
                loader.load_static_graph_file(static_file)
                print("✅")
            except Exception as e:
                print(f"❌ {e}")
        
        # Dynamic 그래프 적재
        dynamic_files = sorted(graph_dir.glob("*_dynamic_graph.json"))
        
        print(f"\n📦 Dynamic 그래프 적재 ({len(dynamic_files)}개):")
        for dynamic_file in dynamic_files:
            ticker = dynamic_file.stem.replace("_dynamic_graph", "").upper()
            print(f"  - {ticker}...", end=" ")
            try:
                loader.load_dynamic_graph_file(dynamic_file)
                print("✅")
            except Exception as e:
                print(f"❌ {e}")
        
        # 검증
        print(f"\n🔍 데이터 검증:")
        stats = loader.verify()
        print(f"  총 노드: {stats['total_nodes']}")
        print(f"  총 링크: {stats['total_links']}")
        print(f"  총 Embedding: {stats['total_embeddings']}")
        
        loader.close()
        
        print("\n" + "=" * 80)
        print("✅ 데이터베이스 재적재 완료")
        print("=" * 80)
        
    except Exception as e:
        logger.error(f"오류 발생: {e}", exc_info=True)
        print(f"\n❌ 오류 발생: {e}\n")


if __name__ == "__main__":
    reset_and_reload()

