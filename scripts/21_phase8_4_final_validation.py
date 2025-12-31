"""
Phase 8.4 최종 검증 스크립트

Vector 검색 활성화 및 통합 테스트
"""

import sys
from pathlib import Path
import time
import json
from statistics import mean, median
sys.path.insert(0, str(Path(__file__).parent.parent))

from dotenv import load_dotenv
load_dotenv()

from app.services.query_engine import QueryEngine

def main():
    print("=" * 80)
    print("Phase 8.4: Vector 검색 활성화 및 통합 테스트 - 최종 검증")
    print("=" * 80)
    
    engine = QueryEngine(graph_name="financial_kg")
    
    # 다양한 테스트 케이스
    test_cases = [
        {
            "query": "애플의 기회 요소는?",
            "expected_graph": True,
            "expected_vector": False,  # query_text가 짧아서 Vector 검색이 어려울 수 있음
        },
        {
            "query": "테슬라의 리스크는?",
            "expected_graph": True,
            "expected_vector": True,
        },
        {
            "query": "구글의 AI 기술에 대해 알려줘",
            "expected_graph": True,
            "expected_vector": True,
        },
        {
            "query": "iPhone과 관련된 기회 요소는?",
            "expected_graph": True,
            "expected_vector": True,
        },
        {
            "query": "엔비디아의 GPU 기술은?",
            "expected_graph": True,
            "expected_vector": True,
        },
    ]
    
    results = []
    
    for i, test_case in enumerate(test_cases, 1):
        query = test_case["query"]
        print(f"\n[{i}/{len(test_cases)}] {query}")
        print("-" * 80)
        
        start_time = time.time()
        
        # Hybrid 검색 수행
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
        
        print(f"  Graph 검색: {graph_count}개")
        print(f"  Vector 검색: {vector_count}개")
        print(f"  통합 결과: {merged_count}개")
        print(f"  소요 시간: {elapsed:.2f}ms")
        
        # 통합 결과 분석
        if merged_count > 0:
            graph_only = sum(1 for r in result["merged_results"] if r.get("graph_rank") and not r.get("vector_rank"))
            vector_only = sum(1 for r in result["merged_results"] if r.get("vector_rank") and not r.get("graph_rank"))
            both = sum(1 for r in result["merged_results"] if r.get("graph_rank") and r.get("vector_rank"))
            
            print(f"  통합 분석:")
            print(f"    Graph만: {graph_only}개")
            print(f"    Vector만: {vector_only}개")
            print(f"    둘 다: {both}개")
            
            # 점수 분포 확인
            scores = [r.get("final_score", 0.0) for r in result["merged_results"]]
            if scores:
                print(f"    최종 점수 범위: {min(scores):.4f} ~ {max(scores):.4f}")
        else:
            print("  ⚠️ 통합 결과 없음")
        
        results.append({
            "query": query,
            "graph_count": graph_count,
            "vector_count": vector_count,
            "merged_count": merged_count,
            "time_ms": elapsed,
            "graph_only": graph_only if merged_count > 0 else 0,
            "vector_only": vector_only if merged_count > 0 else 0,
            "both": both if merged_count > 0 else 0,
        })
    
    engine.close()
    
    # 통계 요약
    print("\n" + "=" * 80)
    print("통계 요약")
    print("=" * 80)
    
    avg_graph = mean([r["graph_count"] for r in results])
    avg_vector = mean([r["vector_count"] for r in results])
    avg_merged = mean([r["merged_count"] for r in results])
    avg_time = mean([r["time_ms"] for r in results])
    
    total_graph_only = sum([r["graph_only"] for r in results])
    total_vector_only = sum([r["vector_only"] for r in results])
    total_both = sum([r["both"] for r in results])
    
    print(f"\n평균 결과 수:")
    print(f"  Graph 검색: {avg_graph:.1f}개")
    print(f"  Vector 검색: {avg_vector:.1f}개")
    print(f"  통합 결과: {avg_merged:.1f}개")
    
    print(f"\n통합 결과 분석:")
    print(f"  Graph만: {total_graph_only}개")
    print(f"  Vector만: {total_vector_only}개")
    print(f"  둘 다: {total_both}개")
    
    print(f"\n평균 소요 시간: {avg_time:.2f}ms")
    
    # Vector 검색 활성화 상태 확인
    print(f"\nVector 검색 활성화 상태:")
    vector_active_count = sum(1 for r in results if r["vector_count"] > 0)
    print(f"  Vector 검색 결과가 있는 쿼리: {vector_active_count}/{len(results)}개 ({vector_active_count/len(results)*100:.1f}%)")
    
    # 결과 저장
    output_file = Path("test_result/phase8_4_validation.json")
    output_file.parent.mkdir(exist_ok=True)
    with open(output_file, 'w', encoding='utf-8') as f:
        json.dump({
            "summary": {
                "avg_graph_count": avg_graph,
                "avg_vector_count": avg_vector,
                "avg_merged_count": avg_merged,
                "avg_time_ms": avg_time,
                "vector_active_queries": vector_active_count,
                "total_queries": len(results),
            },
            "details": results
        }, f, ensure_ascii=False, indent=2)
    
    print(f"\n💾 결과 저장: {output_file}")
    
    print("\n" + "=" * 80)
    print("✅ Phase 8.4 검증 완료")
    print("=" * 80)
    
    # 최종 권장사항
    print("\n📋 권장사항:")
    if avg_vector < 2:
        print("  - Vector 검색 결과가 적습니다. similarity_threshold를 낮추거나 query_text 개선 고려")
    if total_both < total_graph_only:
        print("  - Graph와 Vector 검색 결과의 교집합이 적습니다. RRF 가중치 튜닝 고려")
    if avg_time > 10000:
        print("  - 검색 시간이 길습니다. 캐싱 또는 최적화 고려")

if __name__ == "__main__":
    main()

