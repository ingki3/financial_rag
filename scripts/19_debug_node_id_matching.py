"""
Node ID 매칭 디버깅 스크립트

Graph 검색과 Vector 검색 결과의 node_id 필드명 확인
"""

import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent.parent))

from dotenv import load_dotenv
load_dotenv()

from app.services.query_engine import QueryEngine

def main():
    engine = QueryEngine(graph_name="financial_kg")
    
    query = "애플의 기회 요소는?"
    
    print("=" * 80)
    print("Node ID 매칭 디버깅")
    print("=" * 80)
    print(f"질의: {query}\n")
    
    # Intent 추출
    intent = engine.extract_intent(query)
    print(f"Intent: {intent}\n")
    
    # Graph 검색
    graph_results = engine.graph_search(intent)
    print(f"Graph 검색 결과: {len(graph_results)}개")
    if graph_results:
        print("\nGraph 검색 결과 샘플 (첫 번째):")
        first_graph = graph_results[0]
        print(f"  Keys: {list(first_graph.keys())}")
        print(f"  id: {first_graph.get('id')}")
        print(f"  node_id: {first_graph.get('node_id')}")
        print(f"  전체: {first_graph}")
    
    # Vector 검색
    vector_results = engine._vector_search(intent, top_k=10, similarity_threshold=0.5)
    print(f"\nVector 검색 결과: {len(vector_results)}개")
    if vector_results:
        print("\nVector 검색 결과 샘플 (첫 번째):")
        first_vector = vector_results[0]
        print(f"  Keys: {list(first_vector.keys())}")
        print(f"  id: {first_vector.get('id')}")
        print(f"  node_id: {first_vector.get('node_id')}")
        print(f"  전체: {first_vector}")
    
    # 매칭 확인
    print("\n" + "=" * 80)
    print("Node ID 매칭 확인")
    print("=" * 80)
    
    graph_ids = set()
    for r in graph_results[:5]:
        node_id = r.get("id") or r.get("node_id") or r.get("target.id")
        if node_id:
            graph_ids.add(node_id)
            print(f"Graph ID: {node_id}")
    
    vector_ids = set()
    for r in vector_results[:5]:
        node_id = r.get("node_id") or r.get("id")
        if node_id:
            vector_ids.add(node_id)
            print(f"Vector ID: {node_id}")
    
    print(f"\nGraph ID 수: {len(graph_ids)}")
    print(f"Vector ID 수: {len(vector_ids)}")
    print(f"교집합: {len(graph_ids & vector_ids)}개")
    
    if graph_ids & vector_ids:
        print("\n✅ 매칭되는 ID:")
        for common_id in list(graph_ids & vector_ids)[:3]:
            print(f"  {common_id}")
    else:
        print("\n❌ 매칭되는 ID 없음")
        print("\nGraph ID 샘플:")
        for gid in list(graph_ids)[:3]:
            print(f"  {gid}")
        print("\nVector ID 샘플:")
        for vid in list(vector_ids)[:3]:
            print(f"  {vid}")
    
    engine.close()

if __name__ == "__main__":
    main()

