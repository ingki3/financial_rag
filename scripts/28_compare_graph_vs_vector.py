#!/usr/bin/env python
"""
Graph DB vs Vector 검색 비교 테스트

1. Graph DB 검색 결과 생성
2. Vector 검색만 사용하여 결과 생성
3. 두 결과 비교
"""

import sys
from pathlib import Path
import time
import json
from datetime import datetime

# 프로젝트 루트를 Python 경로에 추가
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

from dotenv import load_dotenv
load_dotenv()

from app.services.query_engine import QueryEngine

def compare_results(graph_results: list, vector_results: list):
    """두 검색 결과 비교"""
    comparison = {
        "graph_count": len(graph_results),
        "vector_count": len(vector_results),
        "overlap_count": 0,
        "overlap_nodes": [],
        "graph_only": [],
        "vector_only": []
    }
    
    # Graph 결과의 노드 ID 추출
    graph_ids = set()
    graph_id_to_result = {}
    
    for r in graph_results:
        # Graph 결과에서 ID 추출 (다양한 형식 지원)
        node_id = None
        if "target.id" in r:
            node_id = r["target.id"]
        elif "id" in r:
            node_id = r["id"]
        elif "node_id" in r:
            node_id = r["node_id"]
        
        if node_id:
            graph_ids.add(node_id)
            graph_id_to_result[node_id] = r
    
    # Vector 결과의 노드 ID 추출
    vector_ids = set()
    vector_id_to_result = {}
    
    for r in vector_results:
        node_id = r.get("node_id")
        if node_id:
            vector_ids.add(node_id)
            vector_id_to_result[node_id] = r
    
    # 겹치는 노드 찾기
    overlap_ids = graph_ids & vector_ids
    comparison["overlap_count"] = len(overlap_ids)
    comparison["overlap_nodes"] = list(overlap_ids)
    
    # Graph에만 있는 노드
    graph_only_ids = graph_ids - vector_ids
    comparison["graph_only"] = [
        {
            "id": node_id,
            "entity": graph_id_to_result[node_id].get("target.entity") or graph_id_to_result[node_id].get("entity"),
            "description": (graph_id_to_result[node_id].get("target.description") or graph_id_to_result[node_id].get("description", ""))[:100]
        }
        for node_id in list(graph_only_ids)[:10]  # 최대 10개만
    ]
    
    # Vector에만 있는 노드
    vector_only_ids = vector_ids - graph_ids
    comparison["vector_only"] = [
        {
            "id": node_id,
            "entity": vector_id_to_result[node_id].get("entity"),
            "description": (vector_id_to_result[node_id].get("description", ""))[:100],
            "similarity": vector_id_to_result[node_id].get("similarity")
        }
        for node_id in list(vector_only_ids)[:10]  # 최대 10개만
    ]
    
    return comparison

def main():
    """메인 테스트 함수"""
    print("=" * 80)
    print("Graph DB vs Vector 검색 비교 테스트")
    print("=" * 80)
    
    # 테스트 질의
    test_queries = [
        "애플의 기회 요소는?",
        "테슬라의 리스크는?",
        "구글의 기술은?",
        "애플의 사업상 리스크에 대해 설명해줘",
        "엔비디아의 GPU 기술은?",
        "애플의 iPhone과 관련된 기회 요소는?",
        "애플의 2023년 기회 요소는?",
        "구글의 AI 기술과 관련된 기회 요소는?",
    ]
    
    print(f"\n총 {len(test_queries)}개의 질의를 테스트합니다.\n")
    
    # QueryEngine 초기화
    print("QueryEngine 초기화 중...")
    engine = QueryEngine(graph_name="financial_kg")
    print("✅ 초기화 완료\n")
    
    results = []
    
    for i, query in enumerate(test_queries, 1):
        print(f"[{i}/{len(test_queries)}] {query}")
        
        total_start = time.time()
        timing = {}
        
        try:
            # 1. Intent 추출
            intent_start = time.time()
            intent = engine.extract_intent(query)
            timing["intent_extraction_ms"] = (time.time() - intent_start) * 1000
            
            # 2. Graph 검색 (비교용)
            graph_start = time.time()
            graph_results = engine.graph_search(intent)
            timing["graph_search_ms"] = (time.time() - graph_start) * 1000
            
            # 3. Vector 검색만 사용 (Graph 검색 제외)
            vector_start = time.time()
            vector_results = engine._vector_search(intent, top_k=20)
            timing["vector_search_ms"] = (time.time() - vector_start) * 1000
            
            # 4. 결과 비교
            comparison = compare_results(graph_results, vector_results)
            
            total_elapsed = (time.time() - total_start) * 1000
            
            result = {
                "query": query,
                "intent": intent,
                "graph_results_count": len(graph_results),
                "vector_results_count": len(vector_results),
                "comparison": comparison,
                "graph_results_sample": graph_results[:5],  # 샘플만 저장
                "vector_results_sample": vector_results[:5],  # 샘플만 저장
                "time_ms": total_elapsed,
                "time_sec": total_elapsed / 1000,
                "timing": timing
            }
            results.append(result)
            
            # 간단한 결과 출력
            print(f"  Graph 검색: {len(graph_results)}개")
            print(f"  Vector 검색: {len(vector_results)}개")
            print(f"  겹치는 결과: {comparison['overlap_count']}개")
            print(f"  Graph만: {len(comparison['graph_only'])}개")
            print(f"  Vector만: {len(comparison['vector_only'])}개")
            print(f"  소요 시간: {total_elapsed/1000:.2f}초")
            print()
            
        except Exception as e:
            print(f"  ❌ 오류: {e}")
            import traceback
            traceback.print_exc()
            results.append({
                "query": query,
                "error": str(e),
                "time_ms": (time.time() - total_start) * 1000
            })
    
    engine.close()
    
    # JSON 저장
    json_file = Path("test_result/graph_vs_vector_comparison.json")
    json_file.parent.mkdir(exist_ok=True)
    
    output = {
        "timestamp": datetime.now().isoformat(),
        "test_queries": test_queries,
        "results": results
    }
    
    with open(json_file, 'w', encoding='utf-8') as f:
        json.dump(output, f, ensure_ascii=False, indent=2)
    
    # 통계 출력
    print("=" * 80)
    print("전체 통계")
    print("=" * 80)
    
    from statistics import mean
    
    graph_counts = [r.get("graph_results_count", 0) for r in results if "graph_results_count" in r]
    vector_counts = [r.get("vector_results_count", 0) for r in results if "vector_results_count" in r]
    overlap_counts = [r.get("comparison", {}).get("overlap_count", 0) for r in results if "comparison" in r]
    
    if graph_counts and vector_counts:
        print(f"\n평균 결과 수:")
        print(f"  Graph 검색: {mean(graph_counts):.1f}개")
        print(f"  Vector 검색: {mean(vector_counts):.1f}개")
        print(f"  평균 겹침: {mean(overlap_counts):.1f}개")
        
        if mean(graph_counts) > 0:
            overlap_ratio = mean(overlap_counts) / mean(graph_counts) * 100
            print(f"  겹침 비율: {overlap_ratio:.1f}%")
    
    # 시간 통계
    intent_times = [r.get("timing", {}).get("intent_extraction_ms", 0) for r in results if "timing" in r]
    graph_times = [r.get("timing", {}).get("graph_search_ms", 0) for r in results if "timing" in r]
    vector_times = [r.get("timing", {}).get("vector_search_ms", 0) for r in results if "timing" in r]
    
    if intent_times and graph_times and vector_times:
        print(f"\n평균 소요 시간:")
        print(f"  Intent 추출: {mean(intent_times):.2f}ms ({mean(intent_times)/1000:.2f}초)")
        print(f"  Graph 검색: {mean(graph_times):.2f}ms ({mean(graph_times)/1000:.2f}초)")
        print(f"  Vector 검색: {mean(vector_times):.2f}ms ({mean(vector_times)/1000:.2f}초)")
    
    print(f"\n✅ 비교 완료")
    print(f"💾 결과 저장: {json_file}")

if __name__ == "__main__":
    main()


