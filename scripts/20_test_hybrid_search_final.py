"""
Hybrid 검색 최종 테스트

Graph + Vector 검색 통합 및 RRF 가중치 튜닝
"""

import sys
from pathlib import Path
import time
from statistics import mean
sys.path.insert(0, str(Path(__file__).parent.parent))

from dotenv import load_dotenv
load_dotenv()

from app.services.query_engine import QueryEngine

def main():
    engine = QueryEngine(graph_name="financial_kg")
    
    test_queries = [
        "애플의 기회 요소는?",
        "테슬라의 리스크는?",
        "구글의 AI 기술에 대해 알려줘",
    ]
    
    print("=" * 80)
    print("Hybrid 검색 최종 테스트")
    print("=" * 80)
    
    for query in test_queries:
        print(f"\n📝 질의: {query}")
        print("-" * 80)
        
        # Hybrid 검색
        start_time = time.time()
        result = engine.query(
            user_query=query,
            use_vector_search=True,
            use_graph_search=True,
            generate_answer=False,
            top_k=10
        )
        elapsed = (time.time() - start_time) * 1000
        
        graph_count = len(result.get("graph_results", []))
        vector_count = len(result.get("vector_results", []))
        merged_count = len(result.get("merged_results", []))
        
        print(f"Graph 검색: {graph_count}개")
        print(f"Vector 검색: {vector_count}개")
        print(f"통합 결과: {merged_count}개")
        print(f"소요 시간: {elapsed:.2f}ms")
        
        if merged_count > 0:
            print(f"\nTop 5 통합 결과:")
            for i, r in enumerate(result["merged_results"][:5], 1):
                entity = r.get("entity") or r.get("description", "")[:50]
                graph_score = r.get("graph_score", 0.0)
                vector_score = r.get("vector_score", 0.0)
                final_score = r.get("final_score", 0.0)
                print(f"  {i}. {entity}")
                print(f"     Graph: {graph_score:.4f}, Vector: {vector_score:.4f}, 최종: {final_score:.4f}")
        else:
            print("⚠️ 통합 결과 없음")
    
    engine.close()
    
    print("\n" + "=" * 80)
    print("✅ 테스트 완료")
    print("=" * 80)

if __name__ == "__main__":
    main()

