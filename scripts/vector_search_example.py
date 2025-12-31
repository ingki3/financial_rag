#!/usr/bin/env python
"""FalkorDB Vector Search 예제 스크립트

특정 노드의 속성값을 embedding한 후 vector search를 통해 유사한 노드를 찾는 예제

사용법:
  python scripts/vector_search_example.py --query "supply chain risk" --group-id AAPL
  python scripts/vector_search_example.py --node-property "description" --search-text "competition"
"""

import os
import sys
import json
import asyncio
import argparse
from pathlib import Path
from dotenv import load_dotenv
from typing import List, Dict, Optional

load_dotenv()

# 프로젝트 루트 추가
sys.path.insert(0, str(Path(__file__).parent.parent))

from app.services.graphiti_manager import GraphitiManager
from falkordb import FalkorDB


def _json_default(o):
    """JSON 직렬화 헬퍼"""
    if hasattr(o, "model_dump"):
        try:
            return o.model_dump()
        except Exception:
            pass
    if hasattr(o, "dict"):
        try:
            return o.dict()
        except Exception:
            pass
    if hasattr(o, "__dict__"):
        try:
            return dict(o.__dict__)
        except Exception:
            pass
    return str(o)


async def vector_search_by_query(
    manager: GraphitiManager,
    query: str,
    group_ids: Optional[List[str]] = None,
    num_results: int = 10
):
    """
    Graphiti를 사용한 vector search (가장 간단한 방법)
    
    Args:
        manager: GraphitiManager 인스턴스
        query: 검색 쿼리 텍스트
        group_ids: 필터링할 group_id 목록
        num_results: 반환할 결과 수
    """
    print(f"\n🔍 Vector Search: '{query}'")
    print(f"   Group IDs: {group_ids or '전체'}")
    print(f"   결과 수: {num_results}")
    print("-" * 60)
    
    results = await manager.search(
        query=query,
        group_ids=group_ids,
        num_results=num_results
    )
    
    print(f"\n✅ {len(results)}개 결과 발견:\n")
    for i, result in enumerate(results, 1):
        print(f"{i}. {json.dumps(result, ensure_ascii=False, indent=2, default=_json_default)}")
        print()
    
    return results


async def find_similar_nodes_by_reference(
    manager: GraphitiManager,
    reference_query: str,
    search_query: str,
    group_ids: Optional[List[str]] = None,
    num_results: int = 10
):
    """
    기준 노드를 찾은 후, 그 노드와 유사한 노드 검색
    
    Args:
        manager: GraphitiManager 인스턴스
        reference_query: 기준 노드를 찾기 위한 쿼리
        search_query: 유사 노드를 찾기 위한 쿼리 (또는 기준 노드의 텍스트)
        group_ids: 필터링할 group_id 목록
        num_results: 반환할 결과 수
    """
    print(f"\n📌 1단계: 기준 노드 찾기 - '{reference_query}'")
    print("-" * 60)
    
    # 1. 기준 노드 찾기
    reference_results = await manager.search(
        query=reference_query,
        group_ids=group_ids,
        num_results=1
    )
    
    if not reference_results:
        print("❌ 기준 노드를 찾을 수 없습니다.")
        return []
    
    reference_node = reference_results[0]
    print(f"✅ 기준 노드 발견:")
    print(json.dumps(reference_node, ensure_ascii=False, indent=2, default=_json_default))
    
    # 2. 기준 노드의 텍스트 추출
    if hasattr(reference_node, 'episode_body'):
        reference_text = reference_node.episode_body
    elif hasattr(reference_node, 'content'):
        reference_text = reference_node.content
    else:
        reference_text = str(reference_node)
    
    print(f"\n📌 2단계: 유사 노드 검색 - '{search_query}'")
    print("-" * 60)
    
    # 3. 유사 노드 검색 (기준 노드의 텍스트 또는 별도 쿼리 사용)
    search_text = search_query if search_query else reference_text
    similar_results = await manager.search(
        query=search_text,
        group_ids=group_ids,
        num_results=num_results
    )
    
    print(f"\n✅ {len(similar_results)}개 유사 노드 발견:\n")
    for i, result in enumerate(similar_results, 1):
        print(f"{i}. {json.dumps(result, ensure_ascii=False, indent=2, default=_json_default)}")
        print()
    
    return similar_results


async def vector_search_then_graph_query(
    manager: GraphitiManager,
    search_query: str,
    group_ids: Optional[List[str]] = None,
    num_results: int = 5
):
    """
    Vector search로 노드를 찾은 후, 그 노드들에 대해 그래프 쿼리 실행
    
    Args:
        manager: GraphitiManager 인스턴스
        search_query: 검색 쿼리
        group_ids: 필터링할 group_id 목록
        num_results: 검색할 노드 수
    """
    print(f"\n🔍 1단계: Vector Search - '{search_query}'")
    print("-" * 60)
    
    # 1. Vector search로 노드 찾기
    search_results = await manager.search(
        query=search_query,
        group_ids=group_ids,
        num_results=num_results
    )
    
    if not search_results:
        print("❌ 검색 결과가 없습니다.")
        return
    
    print(f"✅ {len(search_results)}개 노드 발견")
    
    # 2. FalkorDB에 직접 연결하여 그래프 쿼리 실행
    print(f"\n🔍 2단계: 찾은 노드들에 대한 그래프 쿼리")
    print("-" * 60)
    
    db = FalkorDB(host=manager.host, port=manager.port)
    graph = db.select_graph(manager.database)
    
    # Graphiti 결과에서 노드 정보 추출
    # 주의: Graphiti의 결과 구조는 버전에 따라 다를 수 있음
    for i, result in enumerate(search_results, 1):
        print(f"\n📌 노드 {i}:")
        print(json.dumps(result, ensure_ascii=False, indent=2, default=_json_default))
        
        # 노드 ID 추출 시도
        node_id = None
        if hasattr(result, 'id'):
            node_id = result.id
        elif hasattr(result, 'node_id'):
            node_id = result.node_id
        elif isinstance(result, dict):
            node_id = result.get('id') or result.get('node_id')
        
        if node_id:
            # 해당 노드와 연결된 노드 찾기
            try:
                query = """
                MATCH (n)-[r]->(connected)
                WHERE id(n) = $node_id
                RETURN type(r) AS relationship_type, 
                       labels(connected) AS connected_labels,
                       properties(connected) AS connected_props
                LIMIT 5
                """
                
                graph_result = graph.query(query, {"node_id": node_id})
                
                if graph_result.result_set:
                    print(f"   연결된 노드 {len(graph_result.result_set)}개:")
                    for row in graph_result.result_set:
                        rel_type = row[0]
                        labels = row[1]
                        props = row[2]
                        print(f"     - {rel_type} -> {labels}")
                        if props:
                            print(f"       속성: {json.dumps(props, ensure_ascii=False, default=str)}")
                else:
                    print("   연결된 노드 없음")
            except Exception as e:
                print(f"   ⚠️ 그래프 쿼리 오류: {e}")


async def main_async(
    query: Optional[str] = None,
    reference_query: Optional[str] = None,
    search_text: Optional[str] = None,
    group_id: Optional[str] = None,
    node_property: Optional[str] = None,
    limit: int = 10,
    graph_query: bool = False
):
    """메인 함수"""
    manager = GraphitiManager(
        host=os.getenv("FALKORDB_HOST", "localhost"),
        port=int(os.getenv("FALKORDB_PORT", "6379")),
        database=os.getenv("FALKORDB_DATABASE", "default_db"),
    )
    
    await manager.initialize()
    
    try:
        group_ids = [group_id] if group_id else None
        
        if graph_query and query:
            # Vector search 후 그래프 쿼리 실행
            await vector_search_then_graph_query(
                manager=manager,
                search_query=query,
                group_ids=group_ids,
                num_results=limit
            )
        elif reference_query:
            # 기준 노드를 찾은 후 유사 노드 검색
            await find_similar_nodes_by_reference(
                manager=manager,
                reference_query=reference_query,
                search_query=search_text or "",
                group_ids=group_ids,
                num_results=limit
            )
        elif query:
            # 일반 vector search
            await vector_search_by_query(
                manager=manager,
                query=query,
                group_ids=group_ids,
                num_results=limit
            )
        else:
            print("❌ 검색 쿼리를 제공해주세요. --query 또는 --reference-query 옵션을 사용하세요.")
            
    finally:
        await manager.close()


def main():
    """CLI 진입점"""
    ap = argparse.ArgumentParser(
        description="FalkorDB Vector Search 예제",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
예제:
  # 기본 vector search
  python scripts/vector_search_example.py --query "supply chain risk" --group-id AAPL
  
  # 기준 노드를 찾은 후 유사 노드 검색
  python scripts/vector_search_example.py --reference-query "Intense Competition" --search-text "competition risk"
  
  # Vector search 후 그래프 쿼리 실행
  python scripts/vector_search_example.py --query "iPhone 15" --group-id AAPL --graph-query
        """
    )
    
    ap.add_argument("--query", type=str, help="검색 쿼리 텍스트")
    ap.add_argument("--reference-query", type=str, help="기준 노드를 찾기 위한 쿼리")
    ap.add_argument("--search-text", type=str, help="유사 노드 검색용 텍스트 (--reference-query와 함께 사용)")
    ap.add_argument("--group-id", type=str, help="필터링할 group_id (예: AAPL, TSLA)")
    ap.add_argument("--node-property", type=str, help="검색할 노드 속성명 (향후 구현)")
    ap.add_argument("--limit", type=int, default=10, help="반환할 결과 수")
    ap.add_argument("--graph-query", action="store_true", help="Vector search 후 그래프 쿼리 실행")
    
    args = ap.parse_args()
    
    asyncio.run(main_async(
        query=args.query,
        reference_query=args.reference_query,
        search_text=args.search_text,
        group_id=args.group_id,
        node_property=args.node_property,
        limit=args.limit,
        graph_query=args.graph_query
    ))


if __name__ == "__main__":
    main()




