"""
Vector 검색 테스트 스크립트

Phase 8.4: Vector 검색 활성화 및 통합 테스트
"""

import sys
import os
from pathlib import Path
import time
from statistics import mean, median

# 프로젝트 루트를 Python 경로에 추가
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

from dotenv import load_dotenv
load_dotenv()

import logging
from app.services.graph_loader import GraphLoader
from app.services.vector_search import VectorSearch
from app.services.query_engine import QueryEngine

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


def check_embeddings_in_db():
    """데이터베이스에 embedding이 있는지 확인"""
    print("=" * 80)
    print("1. 데이터베이스 Embedding 확인")
    print("=" * 80)
    
    loader = GraphLoader(graph_name="financial_kg")
    loader.connect()
    
    # 각 노드 타입별로 embedding이 있는 노드 수 확인
    node_types = ["Risk", "Opportunity", "Event", "Technology"]
    
    for node_type in node_types:
        query = f"""
        MATCH (n:{node_type})
        WHERE n.description_embedding IS NOT NULL
        RETURN count(n) AS count
        """
        try:
            results = loader.execute_query(query)
            count = results[0].get("count", 0) if results else 0
            print(f"  {node_type}: {count}개 노드에 embedding 있음")
        except Exception as e:
            print(f"  {node_type}: 오류 - {e}")
    
    # 전체 노드 중 embedding이 있는 비율
    query = """
    MATCH (n)
    WHERE n.description_embedding IS NOT NULL
    RETURN count(n) AS count_with_embedding
    """
    try:
        results = loader.execute_query(query)
        count_with = results[0].get("count_with_embedding", 0) if results else 0
    except:
        count_with = 0
    
    query = """
    MATCH (n)
    RETURN count(n) AS total_count
    """
    try:
        results = loader.execute_query(query)
        total = results[0].get("total_count", 0) if results else 0
    except:
        total = 0
    
    print(f"\n  전체 노드: {total}개")
    print(f"  Embedding 있는 노드: {count_with}개")
    if total > 0:
        print(f"  Embedding 비율: {count_with/total*100:.1f}%")
    
    loader.close()
    return count_with > 0


def test_vector_search_standalone():
    """Vector 검색 단독 테스트"""
    print("\n" + "=" * 80)
    print("2. Vector 검색 단독 테스트")
    print("=" * 80)
    
    loader = GraphLoader(graph_name="financial_kg")
    loader.connect()
    vector_search = VectorSearch(loader)
    
    test_queries = [
        ("애플의 기회 요소는?", "Opportunity"),
        ("테슬라의 리스크는?", "Risk"),
        ("구글의 AI 기술", "Technology"),
        ("iPhone과 관련된 기회", "Opportunity"),
    ]
    
    results_summary = []
    
    for query_text, target_type in test_queries:
        print(f"\n📝 질의: {query_text}")
        print(f"   Target: {target_type}")
        print("-" * 80)
        
        start_time = time.time()
        
        # Vector 검색 수행
        results = vector_search.search(
            query_text=query_text,
            target_node_type=target_type,
            top_k=10,
            similarity_threshold=0.5  # 임계값을 낮춰서 더 많은 결과 확인
        )
        
        elapsed = (time.time() - start_time) * 1000
        
        print(f"   결과 수: {len(results)}개")
        print(f"   소요 시간: {elapsed:.2f}ms")
        
        if results:
            print(f"\n   Top 5 결과:")
            for i, result in enumerate(results[:5], 1):
                entity = result.get("entity") or result.get("description", "")[:50]
                similarity = result.get("similarity", 0.0)
                print(f"   {i}. {entity} (유사도: {similarity:.3f})")
        else:
            print("   ⚠️ 결과 없음")
        
        results_summary.append({
            "query": query_text,
            "target": target_type,
            "count": len(results),
            "time_ms": elapsed
        })
    
    loader.close()
    
    # 통계
    print("\n" + "=" * 80)
    print("Vector 검색 통계")
    print("=" * 80)
    avg_time = mean([r["time_ms"] for r in results_summary])
    avg_count = mean([r["count"] for r in results_summary])
    print(f"평균 결과 수: {avg_count:.1f}개")
    print(f"평균 소요 시간: {avg_time:.2f}ms")
    
    return results_summary


def test_hybrid_search():
    """Graph + Vector 검색 통합 테스트"""
    print("\n" + "=" * 80)
    print("3. Graph + Vector 검색 통합 테스트")
    print("=" * 80)
    
    engine = QueryEngine(graph_name="financial_kg")
    
    test_queries = [
        "애플의 기회 요소는?",
        "테슬라의 리스크는?",
        "구글의 AI 기술에 대해 알려줘",
        "iPhone과 관련된 기회 요소는?",
    ]
    
    results_summary = []
    
    for query in test_queries:
        print(f"\n📝 질의: {query}")
        print("-" * 80)
        
        start_time = time.time()
        
        # Graph만 검색
        result_graph_only = engine.query(
            user_query=query,
            use_vector_search=False,
            use_graph_search=True,
            generate_answer=False
        )
        time_graph = (time.time() - start_time) * 1000
        
        # Vector만 검색
        start_time = time.time()
        result_vector_only = engine.query(
            user_query=query,
            use_vector_search=True,
            use_graph_search=False,
            generate_answer=False
        )
        time_vector = (time.time() - start_time) * 1000
        
        # Hybrid 검색 (Graph + Vector)
        start_time = time.time()
        result_hybrid = engine.query(
            user_query=query,
            use_vector_search=True,
            use_graph_search=True,
            generate_answer=False
        )
        time_hybrid = (time.time() - start_time) * 1000
        
        graph_count = len(result_graph_only.get("graph_results", []))
        vector_count = len(result_vector_only.get("vector_results", []))
        merged_count = len(result_hybrid.get("merged_results", []))
        
        print(f"   Graph만: {graph_count}개 ({time_graph:.2f}ms)")
        print(f"   Vector만: {vector_count}개 ({time_vector:.2f}ms)")
        print(f"   Hybrid: {merged_count}개 ({time_hybrid:.2f}ms)")
        
        # 결과 비교
        if merged_count > 0:
            print(f"\n   Hybrid Top 3:")
            for i, result in enumerate(result_hybrid["merged_results"][:3], 1):
                entity = result.get("entity") or result.get("description", "")[:50]
                graph_score = result.get("graph_score", 0.0)
                vector_score = result.get("vector_score", 0.0)
                final_score = result.get("final_score", 0.0)
                print(f"   {i}. {entity}")
                print(f"      Graph 점수: {graph_score:.4f}, Vector 점수: {vector_score:.4f}, 최종: {final_score:.4f}")
        
        results_summary.append({
            "query": query,
            "graph_count": graph_count,
            "vector_count": vector_count,
            "merged_count": merged_count,
            "time_graph": time_graph,
            "time_vector": time_vector,
            "time_hybrid": time_hybrid
        })
    
    engine.close()
    
    # 통계
    print("\n" + "=" * 80)
    print("Hybrid 검색 통계")
    print("=" * 80)
    avg_graph = mean([r["graph_count"] for r in results_summary])
    avg_vector = mean([r["vector_count"] for r in results_summary])
    avg_merged = mean([r["merged_count"] for r in results_summary])
    avg_time_graph = mean([r["time_graph"] for r in results_summary])
    avg_time_vector = mean([r["time_vector"] for r in results_summary])
    avg_time_hybrid = mean([r["time_hybrid"] for r in results_summary])
    
    print(f"평균 결과 수:")
    print(f"  Graph만: {avg_graph:.1f}개")
    print(f"  Vector만: {avg_vector:.1f}개")
    print(f"  Hybrid: {avg_merged:.1f}개")
    print(f"\n평균 소요 시간:")
    print(f"  Graph만: {avg_time_graph:.2f}ms")
    print(f"  Vector만: {avg_time_vector:.2f}ms")
    print(f"  Hybrid: {avg_time_hybrid:.2f}ms")
    
    return results_summary


def test_rrf_weights():
    """RRF 가중치 튜닝 테스트"""
    print("\n" + "=" * 80)
    print("4. RRF 가중치 튜닝 테스트")
    print("=" * 80)
    
    engine = QueryEngine(graph_name="financial_kg")
    
    test_query = "애플의 기회 요소는?"
    
    # 다양한 가중치 조합 테스트
    weight_combinations = [
        (0.8, 0.2, "Graph 중심"),
        (0.6, 0.4, "균형"),
        (0.4, 0.6, "Vector 중심"),
        (0.5, 0.5, "동등"),
    ]
    
    print(f"테스트 질의: {test_query}\n")
    
    # Intent 추출
    intent = engine.extract_intent(test_query)
    graph_results = engine.graph_search(intent)
    vector_results = engine._vector_search(intent, top_k=10)
    
    print(f"Graph 결과: {len(graph_results)}개")
    print(f"Vector 결과: {len(vector_results)}개\n")
    
    results_comparison = []
    
    for graph_weight, vector_weight, label in weight_combinations:
        merged = engine.merge_results(
            graph_results,
            vector_results,
            graph_weight=graph_weight,
            vector_weight=vector_weight
        )
        
        print(f"{label} (Graph: {graph_weight}, Vector: {vector_weight})")
        print(f"  통합 결과: {len(merged)}개")
        
        if merged:
            print(f"  Top 3:")
            for i, result in enumerate(merged[:3], 1):
                entity = result.get("entity") or result.get("description", "")[:50]
                final_score = result.get("final_score", 0.0)
                print(f"    {i}. {entity} (점수: {final_score:.4f})")
        
        results_comparison.append({
            "label": label,
            "graph_weight": graph_weight,
            "vector_weight": vector_weight,
            "count": len(merged),
            "top_scores": [r.get("final_score", 0.0) for r in merged[:5]]
        })
        print()
    
    engine.close()
    
    return results_comparison


def main():
    """메인 테스트 함수"""
    print("=" * 80)
    print("Phase 8.4: Vector 검색 활성화 및 통합 테스트")
    print("=" * 80)
    
    # 1. Embedding 확인
    has_embeddings = check_embeddings_in_db()
    
    if not has_embeddings:
        print("\n⚠️ 경고: 데이터베이스에 embedding이 없습니다.")
        print("   Vector 검색을 사용하려면 노드에 embedding을 추가해야 합니다.")
        print("   동적 그래프 생성 시 --with-embedding 옵션을 사용하세요.")
        return
    
    # 2. Vector 검색 단독 테스트
    vector_results = test_vector_search_standalone()
    
    # 3. Hybrid 검색 테스트
    hybrid_results = test_hybrid_search()
    
    # 4. RRF 가중치 튜닝
    rrf_results = test_rrf_weights()
    
    print("\n" + "=" * 80)
    print("✅ Phase 8.4 테스트 완료")
    print("=" * 80)
    
    # 결과 요약
    print("\n📊 결과 요약:")
    print(f"  Vector 검색 평균 결과 수: {mean([r['count'] for r in vector_results]):.1f}개")
    print(f"  Hybrid 검색 평균 결과 수: {mean([r['merged_count'] for r in hybrid_results]):.1f}개")
    print(f"  Hybrid 검색이 Graph만보다 {mean([r['merged_count'] for r in hybrid_results]) / max(mean([r['graph_count'] for r in hybrid_results]), 1):.1f}배 더 많은 결과 반환")


if __name__ == "__main__":
    main()

