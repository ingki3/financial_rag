#!/usr/bin/env python
"""
자연어 질의 테스트 스크립트

다양한 자연어 질의를 테스트하고 결과를 분석합니다.
"""

import sys
from pathlib import Path
import time
import json
from datetime import datetime
from statistics import mean

# 프로젝트 루트를 Python 경로에 추가
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

from dotenv import load_dotenv
load_dotenv()

from app.services.query_engine import QueryEngine

# ANSI 색상 코드
class Colors:
    HEADER = '\033[95m'
    OKBLUE = '\033[94m'
    OKCYAN = '\033[96m'
    OKGREEN = '\033[92m'
    WARNING = '\033[93m'
    FAIL = '\033[91m'
    ENDC = '\033[0m'
    BOLD = '\033[1m'


def format_result(result: dict, index: int, total: int) -> str:
    """결과 포맷팅"""
    output = []
    
    query = result.get("query", "")
    intent = result.get("intent", {})
    graph_results = result.get("graph_results", [])
    vector_results = result.get("vector_results", [])
    merged_results = result.get("merged_results", [])
    answer = result.get("answer")
    time_ms = result.get("time_ms", 0)
    
    # Intent 정보
    target = intent.get("target", {})
    if isinstance(target, dict):
        target_type = target.get("node_type", "unknown")
    else:
        target_type = intent.get("target_entity_type", "unknown")
    
    query_type = intent.get("query_type", "unknown")
    query_text = intent.get("query_text", "")
    
    output.append(f"\n{Colors.HEADER}{Colors.BOLD}{'=' * 80}{Colors.ENDC}")
    output.append(f"{Colors.HEADER}{Colors.BOLD}[{index}/{total}] {query}{Colors.ENDC}")
    output.append(f"{Colors.HEADER}{Colors.BOLD}{'=' * 80}{Colors.ENDC}")
    
    output.append(f"\n{Colors.OKCYAN}Intent 분석:{Colors.ENDC}")
    output.append(f"  Target: {Colors.BOLD}{target_type}{Colors.ENDC}")
    output.append(f"  Query Type: {query_type}")
    output.append(f"  Query Text: {query_text}")
    
    filters = intent.get("filters", {})
    if filters:
        if isinstance(filters, dict):
            filter_str = ", ".join([f"{k}: {v}" for k, v in filters.items() if v])
        elif isinstance(filters, list):
            filter_str = ", ".join([f"{f.get('node_type', 'unknown')}" for f in filters if isinstance(f, dict)])
        else:
            filter_str = str(filters)
        if filter_str:
            output.append(f"  Filters: {filter_str}")
    
    output.append(f"\n{Colors.OKCYAN}검색 결과:{Colors.ENDC}")
    output.append(f"  Graph 검색: {Colors.OKGREEN}{len(graph_results)}개{Colors.ENDC}")
    output.append(f"  Vector 검색: {Colors.OKGREEN}{len(vector_results)}개{Colors.ENDC}")
    output.append(f"  통합 결과: {Colors.OKGREEN}{len(merged_results)}개{Colors.ENDC}")
    output.append(f"  총 소요 시간: {Colors.WARNING}{time_ms:.2f}ms ({time_ms/1000:.2f}초){Colors.ENDC}")
    
    # 상세 시간 정보
    timing = result.get("timing", {})
    if timing:
        output.append(f"\n{Colors.OKCYAN}상세 시간 분석:{Colors.ENDC}")
        output.append(f"  Intent 추출: {timing.get('intent_extraction_ms', 0):.2f}ms")
        output.append(f"  Graph 검색: {timing.get('graph_search_ms', 0):.2f}ms")
        output.append(f"  Vector 검색: {timing.get('vector_search_ms', 0):.2f}ms")
        output.append(f"  결과 통합: {timing.get('merge_results_ms', 0):.2f}ms")
        answer_time = timing.get('answer_generation_ms', 0)
        if answer_time > 0:
            output.append(f"  답변 생성: {Colors.WARNING}{answer_time:.2f}ms ({answer_time/1000:.2f}초){Colors.ENDC}")
        else:
            output.append(f"  답변 생성: {Colors.WARNING}생성 안 됨{Colors.ENDC}")
    
    # 통합 결과 분석
    if merged_results:
        graph_only = sum(1 for r in merged_results if r.get("graph_rank") and not r.get("vector_rank"))
        vector_only = sum(1 for r in merged_results if r.get("vector_rank") and not r.get("graph_rank"))
        both = sum(1 for r in merged_results if r.get("graph_rank") and r.get("vector_rank"))
        
        output.append(f"\n{Colors.OKCYAN}통합 분석:{Colors.ENDC}")
        output.append(f"  Graph만: {graph_only}개")
        output.append(f"  Vector만: {vector_only}개")
        output.append(f"  둘 다: {both}개")
    
    # 답변 출력
    if answer:
        output.append(f"\n{Colors.OKGREEN}{Colors.BOLD}답변:{Colors.ENDC}")
        # 답변이 너무 길면 잘라서 표시
        answer_short = answer[:300] + "..." if len(answer) > 300 else answer
        output.append(f"{Colors.OKGREEN}{answer_short}{Colors.ENDC}")
    
    # Top 5 결과 출력
    if merged_results:
        output.append(f"\n{Colors.OKCYAN}Top 5 결과:{Colors.ENDC}")
        for i, res in enumerate(merged_results[:5], 1):
            entity = res.get("entity") or res.get("description", "")[:60]
            description = res.get("description", "")
            final_score = res.get("final_score", 0.0)
            
            output.append(f"  {Colors.BOLD}{i}. {entity}{Colors.ENDC}")
            if description and len(description) > 0:
                desc_short = description[:80] + "..." if len(description) > 80 else description
                output.append(f"     {desc_short}")
            output.append(f"     점수: {final_score:.4f}")
    else:
        output.append(f"\n{Colors.WARNING}⚠️ 검색 결과가 없습니다.{Colors.ENDC}")
    
    return "\n".join(output)


def main():
    """메인 테스트 함수"""
    print(f"{Colors.HEADER}{Colors.BOLD}{'=' * 80}{Colors.ENDC}")
    print(f"{Colors.HEADER}{Colors.BOLD}자연어 질의 테스트{Colors.ENDC}")
    print(f"{Colors.HEADER}{Colors.BOLD}{'=' * 80}{Colors.ENDC}\n")
    
    # 다양한 자연어 질의 테스트 케이스
    test_queries = [
        # 기본 질의
        "애플의 기회 요소는?",
        "테슬라의 리스크는?",
        "구글의 기술은?",
        
        # 설명 요청
        "구글의 AI 기술에 대해 알려줘",
        "애플의 사업상 리스크에 대해 설명해줘",
        "테슬라의 재무적 기회 요소를 분석해줘",
        
        # Product 필터
        "애플의 iPhone과 관련된 기회 요소는?",
        "애플의 Mac과 관련된 리스크는?",
        "테슬라의 Model 3와 관련된 이벤트는?",
        
        # Technology 필터
        "구글의 AI 기술과 관련된 기회 요소는?",
        "엔비디아의 GPU 기술은?",
        
        # 시간 필터
        "애플의 2023년 기회 요소는?",
        "테슬라의 최근 리스크는?",
        
        # 비교 질의
        "애플과 테슬라의 리스크를 비교해줘",
        "구글과 엔비디아의 기술을 비교해줘",
        
        # 복합 질의
        "애플의 2023년 iPhone과 관련된 기회 요소는?",
        "테슬라의 최근 Model 3와 관련된 이벤트는?",
    ]
    
    print(f"{Colors.OKCYAN}총 {len(test_queries)}개의 질의를 테스트합니다.{Colors.ENDC}\n")
    
    # QueryEngine 초기화
    print(f"{Colors.OKCYAN}QueryEngine 초기화 중...{Colors.ENDC}")
    engine = QueryEngine(graph_name="financial_kg")
    print(f"{Colors.OKGREEN}✅ 초기화 완료{Colors.ENDC}\n")
    
    results = []
    
    # 각 질의 테스트
    for i, query in enumerate(test_queries, 1):
        print(f"{Colors.OKCYAN}[{i}/{len(test_queries)}] 처리 중: {query}{Colors.ENDC}")
        
        total_start_time = time.time()
        timing = {}
        
        try:
            # 1. Intent 추출 시간 측정
            intent_start = time.time()
            intent = engine.extract_intent(query)
            timing["intent_extraction_ms"] = (time.time() - intent_start) * 1000
            
            # 2. Graph 검색 시간 측정
            graph_start = time.time()
            graph_results = engine.graph_search(intent)
            timing["graph_search_ms"] = (time.time() - graph_start) * 1000
            
            # 3. Vector 검색 시간 측정
            vector_start = time.time()
            vector_results = engine._vector_search(intent, top_k=10)
            timing["vector_search_ms"] = (time.time() - vector_start) * 1000
            
            # 4. 결과 통합 시간 측정
            merge_start = time.time()
            merged_results = engine.merge_results(graph_results, vector_results)
            merged_results = merged_results[:10]
            timing["merge_results_ms"] = (time.time() - merge_start) * 1000
            
            # 5. 답변 생성 시간 측정
            answer = None
            timing["answer_generation_ms"] = 0
            if engine.answer_generator and merged_results:
                answer_start = time.time()
                try:
                    answer = engine.answer_generator.generate_answer(
                        query=query,
                        results=merged_results,
                        intent=intent,
                        max_results=min(5, len(merged_results))
                    )
                    timing["answer_generation_ms"] = (time.time() - answer_start) * 1000
                except Exception as e:
                    print(f"{Colors.WARNING}답변 생성 실패: {e}{Colors.ENDC}")
            
            total_elapsed = (time.time() - total_start_time) * 1000
            
            result = {
                "intent": intent,
                "graph_results": graph_results,
                "vector_results": vector_results,
                "merged_results": merged_results,
                "answer": answer,
                "query": query,
                "time_ms": total_elapsed,
                "timing": timing
            }
            results.append(result)
            
            # 결과 출력
            print(format_result(result, i, len(test_queries)))
            
        except Exception as e:
            print(f"{Colors.FAIL}❌ 오류 발생: {e}{Colors.ENDC}\n")
            results.append({
                "query": query,
                "error": str(e),
                "time_ms": (time.time() - start_time) * 1000
            })
    
    # 통계 요약
    print(f"\n{Colors.HEADER}{Colors.BOLD}{'=' * 80}{Colors.ENDC}")
    print(f"{Colors.HEADER}{Colors.BOLD}테스트 결과 통계{Colors.ENDC}")
    print(f"{Colors.HEADER}{Colors.BOLD}{'=' * 80}{Colors.ENDC}\n")
    
    successful = [r for r in results if "error" not in r]
    failed = [r for r in results if "error" in r]
    
    print(f"{Colors.OKCYAN}전체 통계:{Colors.ENDC}")
    print(f"  총 질의 수: {len(test_queries)}개")
    print(f"  성공: {Colors.OKGREEN}{len(successful)}개{Colors.ENDC}")
    print(f"  실패: {Colors.FAIL}{len(failed)}개{Colors.ENDC}")
    
    if successful:
        avg_graph = mean([len(r.get("graph_results", [])) for r in successful])
        avg_vector = mean([len(r.get("vector_results", [])) for r in successful])
        avg_merged = mean([len(r.get("merged_results", [])) for r in successful])
        avg_time = mean([r.get("time_ms", 0) for r in successful])
        
        results_with_data = [r for r in successful if len(r.get("merged_results", [])) > 0]
        results_with_answer = [r for r in successful if r.get("answer")]
        
        print(f"\n{Colors.OKCYAN}검색 결과:{Colors.ENDC}")
        print(f"  평균 Graph 검색: {avg_graph:.1f}개")
        print(f"  평균 Vector 검색: {avg_vector:.1f}개")
        print(f"  평균 통합 결과: {avg_merged:.1f}개")
        print(f"  결과 있는 질의: {len(results_with_data)}개 ({len(results_with_data)/len(successful)*100:.1f}%)")
        print(f"  답변 생성된 질의: {len(results_with_answer)}개 ({len(results_with_answer)/len(successful)*100:.1f}%)")
        
        print(f"\n{Colors.OKCYAN}성능:{Colors.ENDC}")
        print(f"  평균 총 소요 시간: {avg_time:.2f}ms ({avg_time/1000:.2f}초)")
        
        # 상세 시간 통계
        avg_intent = mean([r.get("timing", {}).get("intent_extraction_ms", 0) for r in successful])
        avg_graph = mean([r.get("timing", {}).get("graph_search_ms", 0) for r in successful])
        avg_vector = mean([r.get("timing", {}).get("vector_search_ms", 0) for r in successful])
        avg_merge = mean([r.get("timing", {}).get("merge_results_ms", 0) for r in successful])
        answer_times = [r.get("timing", {}).get("answer_generation_ms", 0) for r in successful if r.get("timing", {}).get("answer_generation_ms", 0) > 0]
        avg_answer = mean(answer_times) if answer_times else 0
        
        print(f"\n{Colors.OKCYAN}상세 시간 분석:{Colors.ENDC}")
        print(f"  평균 Intent 추출: {avg_intent:.2f}ms ({avg_intent/1000:.2f}초)")
        print(f"  평균 Graph 검색: {avg_graph:.2f}ms ({avg_graph/1000:.2f}초)")
        print(f"  평균 Vector 검색: {avg_vector:.2f}ms ({avg_vector/1000:.2f}초)")
        print(f"  평균 결과 통합: {avg_merge:.2f}ms ({avg_merge/1000:.2f}초)")
        if avg_answer > 0:
            print(f"  평균 답변 생성: {Colors.WARNING}{avg_answer:.2f}ms ({avg_answer/1000:.2f}초){Colors.ENDC}")
            print(f"  답변 생성 비율: {len(answer_times)}/{len(successful)} ({len(answer_times)/len(successful)*100:.1f}%)")
        else:
            print(f"  평균 답변 생성: {Colors.WARNING}생성 안 됨{Colors.ENDC}")
    
    # 실패한 질의 출력
    if failed:
        print(f"\n{Colors.FAIL}실패한 질의:{Colors.ENDC}")
        for r in failed:
            print(f"  - {r['query']}: {r.get('error', 'Unknown error')}")
    
    # 결과 저장
    output_file = Path("test_result/natural_language_query_test.json")
    output_file.parent.mkdir(exist_ok=True)
    
    with open(output_file, 'w', encoding='utf-8') as f:
        json.dump({
            "timestamp": datetime.now().isoformat(),
            "total_queries": len(test_queries),
            "successful": len(successful),
            "failed": len(failed),
            "results": results
        }, f, ensure_ascii=False, indent=2)
    
    print(f"\n{Colors.OKGREEN}💾 결과 저장: {output_file}{Colors.ENDC}")
    
    # 리소스 정리
    engine.close()
    
    print(f"\n{Colors.OKGREEN}{Colors.BOLD}✅ 테스트 완료{Colors.ENDC}\n")


if __name__ == "__main__":
    main()

