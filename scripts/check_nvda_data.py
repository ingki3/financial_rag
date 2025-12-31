#!/usr/bin/env python
"""NVDA 데이터 저장 여부 확인 스크립트"""
import os
import sys
from pathlib import Path
from dotenv import load_dotenv

load_dotenv()

sys.path.insert(0, str(Path(__file__).parent.parent))

from falkordb import FalkorDB

def check_nvda_data(host: str = "localhost", port: int = 6379, database: str = "default_db"):
    """NVDA 데이터 확인"""
    print("=" * 60)
    print("🔍 NVDA 데이터 저장 확인")
    print("=" * 60)
    print(f"FalkorDB: {host}:{port}")
    print(f"Database: {database}")
    print("=" * 60)
    
    try:
        db = FalkorDB(host=host, port=port)
        graph = db.select_graph(database)
        
        # 1. NVDA group_id를 가진 노드 수 확인
        print("\n1️⃣ NVDA 노드 수 확인...")
        result = graph.query(
            "MATCH (n) WHERE n.group_id = $group_id RETURN count(n) AS total",
            {"group_id": "NVDA"}
        )
        total_nodes = result.result_set[0][0] if result.result_set else 0
        print(f"   총 노드 수: {total_nodes}개")
        
        # 2. Episode 노드 수 확인
        print("\n2️⃣ Episode 노드 수 확인...")
        result = graph.query(
            "MATCH (n:Episode) WHERE n.group_id = $group_id RETURN count(n) AS total",
            {"group_id": "NVDA"}
        )
        episode_nodes = result.result_set[0][0] if result.result_set else 0
        print(f"   Episode 노드: {episode_nodes}개")
        
        # 3. Entity 노드 수 확인
        print("\n3️⃣ Entity 노드 수 확인...")
        result = graph.query(
            "MATCH (n:Entity) WHERE n.group_id = $group_id RETURN count(n) AS total",
            {"group_id": "NVDA"}
        )
        entity_nodes = result.result_set[0][0] if result.result_set else 0
        print(f"   Entity 노드: {entity_nodes}개")
        
        # 4. 엣지 수 확인
        print("\n4️⃣ 엣지(RELATES_TO) 수 확인...")
        result = graph.query(
            "MATCH ()-[e:RELATES_TO]->() WHERE e.group_id = $group_id RETURN count(e) AS total",
            {"group_id": "NVDA"}
        )
        total_edges = result.result_set[0][0] if result.result_set else 0
        print(f"   총 엣지 수: {total_edges}개")
        
        # 5. 최근 생성된 노드 확인 (최근 5개)
        print("\n5️⃣ 최근 생성된 Episode 확인...")
        result = graph.query(
            "MATCH (n:Episode) WHERE n.group_id = $group_id RETURN n.name AS name, n.created_at AS created_at ORDER BY n.created_at DESC LIMIT 5",
            {"group_id": "NVDA"}
        )
        if result.result_set:
            print("   최근 Episode:")
            for row in result.result_set:
                name = row[0] if len(row) > 0 else "N/A"
                created = row[1] if len(row) > 1 else "N/A"
                print(f"     - {name} (created: {created})")
        else:
            print("   최근 Episode 없음")
        
        print("\n" + "=" * 60)
        print("📊 종합 결과")
        print("=" * 60)
        
        if total_nodes > 0:
            print(f"✅ NVDA 데이터가 저장되어 있습니다!")
            print(f"   - 총 노드: {total_nodes}개")
            print(f"   - Episode: {episode_nodes}개")
            print(f"   - Entity: {entity_nodes}개")
            print(f"   - 엣지: {total_edges}개")
        else:
            print("❌ NVDA 데이터가 저장되지 않았습니다.")
            print("   - 노드 수: 0개")
        
        print("=" * 60)
        
    except Exception as e:
        print(f"\n❌ 오류 발생: {e}")
        import traceback
        traceback.print_exc()
        return False
    
    return True

if __name__ == "__main__":
    host = os.getenv("FALKORDB_HOST", "localhost")
    port = int(os.getenv("FALKORDB_PORT", "6379"))
    database = "default_db"
    
    check_nvda_data(host=host, port=port, database=database)

