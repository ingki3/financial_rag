"""
다양한 샘플 쿼리로 Query Engine 테스트 및 결과 분석

다양한 질의 패턴을 테스트하고 결과를 분석합니다.
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
import json
from datetime import datetime
from app.services.query_engine import QueryEngine

# 로깅 설정
logging.basicConfig(
    level=logging.WARNING,  # INFO 레벨로 하면 너무 많은 로그가 출력됨
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)

logger = logging.getLogger(__name__)


def comprehensive_query_test():
    """다양한 샘플 쿼리 테스트"""
    
    # 다양한 패턴의 테스트 질의
    test_queries = [
        # 기본 질의 (Company만)
        ("애플의 기회 요소는?", "기본 - Company만"),
        ("테슬라의 리스크는?", "기본 - Company만"),
        ("구글의 기술은?", "기본 - Company만"),
        
        # Product 필터
        ("애플의 iPhone과 관련된 기회 요소는?", "Product 필터"),
        ("애플의 Mac과 관련된 리스크는?", "Product 필터"),
        ("테슬라의 Model 3와 관련된 이벤트는?", "Product 필터"),
        
        # Technology 필터
        ("구글의 AI 기술에 대해 알려줘", "Technology 필터"),
        ("엔비디아의 GPU 기술은?", "Technology 필터"),
        
        # 시간 필터
        ("애플의 2023년 기회 요소는?", "시간 필터"),
        ("테슬라의 최근 리스크는?", "시간 필터"),
        
        # 복합 필터
        ("애플의 2023년 iPhone과 관련된 기회 요소는?", "복합 - 시간 + Product"),
        ("구글의 AI 기술과 관련된 기회 요소는?", "복합 - Technology"),
        
        # 비교 질의
        ("애플과 테슬라의 리스크를 비교해줘", "비교 질의"),
        
        # 설명 요청
        ("애플의 사업상 리스크에 대해 설명해줘", "설명 요청"),
        ("테슬라의 재무적 기회 요소를 분석해줘", "분석 요청"),
    ]
    
    print("=" * 80)
    print("다양한 샘플 쿼리 테스트")
    print("=" * 80)
    print(f"테스트 시작 시간: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
    
    try:
        engine = QueryEngine()
        
        print("✅ QueryEngine 초기화 완료\n")
        
        results_summary = {
            "total_queries": len(test_queries),
            "successful": 0,
            "failed": 0,
            "zero_results": 0,
            "has_results": 0,
            "by_category": {},
            "details": []
        }
        
        # 각 질의 테스트
        for i, (query, category) in enumerate(test_queries, 1):
            print("=" * 80)
            print(f"테스트 {i}/{len(test_queries)}: [{category}] {query}")
            print("=" * 80)
            
            try:
                # 질의 처리 (Vector 검색 비활성화)
                result = engine.query(
                    user_query=query,
                    top_k=10,
                    use_vector_search=False,  # Vector 검색 비활성화
                    use_graph_search=True,
                    generate_answer=False  # 답변 생성 비활성화 (빠른 테스트)
                )
                
                intent = result["intent"]
                graph_results = result["graph_results"]
                num_results = len(graph_results)
                
                # Intent 요약
                target_type = intent.get("target_entity_type", "unknown")
                filters = intent.get("filters", {})
                query_type = intent.get("query_type", "unknown")
                
                print(f"\n📋 Intent 요약:")
                print(f"   Target: {target_type}")
                print(f"   Query Type: {query_type}")
                print(f"   Filters: {json.dumps(filters, ensure_ascii=False)}")
                
                # 결과 요약
                print(f"\n🔍 검색 결과: {num_results}개")
                
                if num_results > 0:
                    results_summary["has_results"] += 1
                    results_summary["successful"] += 1
                    
                    # 상위 3개 결과 표시
                    print(f"\n   상위 3개 결과:")
                    for j, res in enumerate(graph_results[:3], 1):
                        entity = res.get("target.entity") or res.get("entity") or res.get("id", "N/A")
                        ticker = res.get("target.ticker") or res.get("ticker", "N/A")
                        print(f"     {j}. {entity} ({ticker})")
                else:
                    results_summary["zero_results"] += 1
                    results_summary["successful"] += 1
                    print("   결과 없음")
                
                # 카테고리별 통계
                if category not in results_summary["by_category"]:
                    results_summary["by_category"][category] = {
                        "total": 0,
                        "has_results": 0,
                        "zero_results": 0
                    }
                
                results_summary["by_category"][category]["total"] += 1
                if num_results > 0:
                    results_summary["by_category"][category]["has_results"] += 1
                else:
                    results_summary["by_category"][category]["zero_results"] += 1
                
                # 상세 정보 저장
                results_summary["details"].append({
                    "query": query,
                    "category": category,
                    "target_type": target_type,
                    "query_type": query_type,
                    "filters": filters,
                    "num_results": num_results,
                    "success": True
                })
                
            except Exception as e:
                logger.error(f"질의 처리 실패: {e}", exc_info=True)
                results_summary["failed"] += 1
                results_summary["details"].append({
                    "query": query,
                    "category": category,
                    "error": str(e),
                    "success": False
                })
                print(f"\n❌ 오류 발생: {e}\n")
            
            print("\n")
        
        # 리소스 정리
        engine.close()
        
        # 최종 결과 분석
        print("=" * 80)
        print("테스트 결과 분석")
        print("=" * 80)
        print(f"\n📊 전체 통계:")
        print(f"   총 질의 수: {results_summary['total_queries']}")
        print(f"   성공: {results_summary['successful']}")
        print(f"   실패: {results_summary['failed']}")
        print(f"   결과 있음: {results_summary['has_results']}")
        print(f"   결과 없음: {results_summary['zero_results']}")
        print(f"   성공률: {results_summary['successful'] / results_summary['total_queries'] * 100:.1f}%")
        print(f"   결과 반환률: {results_summary['has_results'] / results_summary['total_queries'] * 100:.1f}%")
        
        print(f"\n📈 카테고리별 통계:")
        for category, stats in results_summary["by_category"].items():
            success_rate = stats["has_results"] / stats["total"] * 100 if stats["total"] > 0 else 0
            print(f"   [{category}]")
            print(f"      총: {stats['total']}, 결과 있음: {stats['has_results']}, 결과 없음: {stats['zero_results']}")
            print(f"      결과 반환률: {success_rate:.1f}%")
        
        # Target 타입별 통계
        target_stats = {}
        for detail in results_summary["details"]:
            if detail.get("success") and "target_type" in detail:
                target_type = detail["target_type"]
                if target_type not in target_stats:
                    target_stats[target_type] = {"total": 0, "has_results": 0}
                target_stats[target_type]["total"] += 1
                if detail["num_results"] > 0:
                    target_stats[target_type]["has_results"] += 1
        
        print(f"\n🎯 Target 타입별 통계:")
        for target_type, stats in sorted(target_stats.items()):
            success_rate = stats["has_results"] / stats["total"] * 100 if stats["total"] > 0 else 0
            print(f"   {target_type}: {stats['has_results']}/{stats['total']} ({success_rate:.1f}%)")
        
        # 문제가 있는 쿼리 분석
        print(f"\n⚠️  결과가 없는 쿼리:")
        zero_result_queries = [d for d in results_summary["details"] if d.get("success") and d.get("num_results", 0) == 0]
        for detail in zero_result_queries:
            print(f"   - [{detail['category']}] {detail['query']}")
            print(f"     Target: {detail.get('target_type')}, Filters: {json.dumps(detail.get('filters', {}), ensure_ascii=False)}")
        
        # 결과를 JSON 파일로 저장
        output_file = f"test_result/comprehensive_query_test_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
        os.makedirs("test_result", exist_ok=True)
        with open(output_file, "w", encoding="utf-8") as f:
            json.dump(results_summary, f, ensure_ascii=False, indent=2)
        
        print(f"\n💾 결과 저장: {output_file}")
        print("\n" + "=" * 80)
        print("✅ 테스트 완료")
        print("=" * 80)
        
    except Exception as e:
        logger.error(f"테스트 실패: {e}", exc_info=True)
        print(f"\n❌ 테스트 실패: {e}\n")
        return


if __name__ == "__main__":
    comprehensive_query_test()


