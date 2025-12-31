#!/usr/bin/env python
"""
인텐트 분석 모델 비교 테스트

인텐트 분석 모델만 변경하여 테스트:
- gemini-2.5-flash-lite
- gemini-3-flash-preview

답변 생성은 gemini-3-flash-preview로 통일
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
from app.services.intent_extractor import IntentExtractor
from app.services.answer_generator import AnswerGenerator

def test_with_intent_model(intent_model: str, test_queries: list):
    """특정 인텐트 모델로 테스트"""
    print(f"\n{'=' * 80}")
    print(f"인텐트 분석 모델: {intent_model}")
    print(f"{'=' * 80}\n")
    
    # QueryEngine 초기화 (인텐트 모델 지정)
    intent_extractor = IntentExtractor(model=intent_model)
    answer_generator = AnswerGenerator(model="gemini-3-flash-preview")
    
    engine = QueryEngine(
        intent_extractor=intent_extractor,
        answer_generator=answer_generator,
        graph_name="financial_kg"
    )
    
    results = []
    
    for i, query in enumerate(test_queries, 1):
        print(f"[{i}/{len(test_queries)}] {query}")
        
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
            
            # 3. Vector 검색 비활성화
            vector_results = []
            timing["vector_search_ms"] = 0
            
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
                    print(f"  ⚠️ 답변 생성 실패: {e}")
            
            total_elapsed = (time.time() - total_start_time) * 1000
            
            result = {
                "query": query,
                "intent": intent,
                "answer": answer or "답변 생성 실패",
                "time_ms": total_elapsed,
                "time_sec": total_elapsed / 1000,
                "timing": timing,
                "search_results": {
                    "graph_results_count": len(graph_results),
                    "vector_results_count": len(vector_results),
                    "merged_results_count": len(merged_results),
                }
            }
            results.append(result)
            
            print(f"  ✅ 완료 ({total_elapsed/1000:.2f}초)")
            
        except Exception as e:
            print(f"  ❌ 오류: {e}")
            results.append({
                "query": query,
                "intent": None,
                "answer": f"오류 발생: {str(e)}",
                "time_ms": (time.time() - total_start_time) * 1000,
                "time_sec": (time.time() - total_start_time),
                "timing": timing,
                "search_results": {}
            })
    
    engine.close()
    
    return results

def main():
    """메인 테스트 함수"""
    print("=" * 80)
    print("인텐트 분석 모델 비교 테스트")
    print("=" * 80)
    
    # 테스트 질의
    test_queries = [
        "애플의 기회 요소는?",
        "테슬라의 리스크는?",
        "구글의 기술은?",
        "애플의 사업상 리스크에 대해 설명해줘",
        "엔비디아의 GPU 기술은?",
    ]
    
    print(f"\n총 {len(test_queries)}개의 질의를 테스트합니다.")
    print("답변 생성 모델: gemini-3-flash-preview (통일)")
    
    # 1. gemini-2.5-flash-lite로 인텐트 분석
    results_25 = test_with_intent_model("gemini-2.5-flash-lite", test_queries)
    
    # 2. gemini-3-flash-preview로 인텐트 분석
    results_3 = test_with_intent_model("gemini-3-flash-preview", test_queries)
    
    # 결과 비교
    print("\n" + "=" * 80)
    print("결과 비교")
    print("=" * 80)
    
    comparison = {
        "timestamp": datetime.now().isoformat(),
        "test_queries": test_queries,
        "answer_model": "gemini-3-flash-preview",
        "results": {
            "gemini-2.5-flash-lite": results_25,
            "gemini-3-flash-preview": results_3
        }
    }
    
    # JSON 저장
    json_file = Path("test_result/intent_model_comparison.json")
    json_file.parent.mkdir(exist_ok=True)
    with open(json_file, 'w', encoding='utf-8') as f:
        json.dump(comparison, f, ensure_ascii=False, indent=2)
    
    # 통계 비교
    from statistics import mean
    
    print("\n인텐트 분석 시간 비교:")
    intent_times_25 = [r.get('timing', {}).get('intent_extraction_ms', 0) for r in results_25 if r.get('timing', {}).get('intent_extraction_ms', 0) > 0]
    intent_times_3 = [r.get('timing', {}).get('intent_extraction_ms', 0) for r in results_3 if r.get('timing', {}).get('intent_extraction_ms', 0) > 0]
    
    if intent_times_25 and intent_times_3:
        print(f"  gemini-2.5-flash-lite: 평균 {mean(intent_times_25):.2f}ms ({mean(intent_times_25)/1000:.2f}초)")
        print(f"  gemini-3-flash-preview: 평균 {mean(intent_times_3):.2f}ms ({mean(intent_times_3)/1000:.2f}초)")
        print(f"  차이: {mean(intent_times_3) - mean(intent_times_25):.2f}ms ({((mean(intent_times_3) - mean(intent_times_25))/mean(intent_times_25)*100):.1f}%)")
    
    print("\n전체 처리 시간 비교:")
    total_times_25 = [r.get('time_sec', 0) for r in results_25 if r.get('time_sec', 0) > 0]
    total_times_3 = [r.get('time_sec', 0) for r in results_3 if r.get('time_sec', 0) > 0]
    
    if total_times_25 and total_times_3:
        print(f"  gemini-2.5-flash-lite: 평균 {mean(total_times_25):.2f}초")
        print(f"  gemini-3-flash-preview: 평균 {mean(total_times_3):.2f}초")
        print(f"  차이: {mean(total_times_3) - mean(total_times_25):.2f}초 ({((mean(total_times_3) - mean(total_times_25))/mean(total_times_25)*100):.1f}%)")
    
    # 인텐트 비교
    print("\n인텐트 추출 결과 비교:")
    for i, query in enumerate(test_queries):
        if i < len(results_25) and i < len(results_3):
            intent_25 = results_25[i].get('intent', {})
            intent_3 = results_3[i].get('intent', {})
            
            print(f"\n[{i+1}] {query}")
            print(f"  gemini-2.5-flash-lite:")
            print(f"    target: {intent_25.get('target_entity_type', 'N/A')}")
            print(f"    company: {intent_25.get('filters', {}).get('company', 'N/A')}")
            print(f"  gemini-3-flash-preview:")
            print(f"    target: {intent_3.get('target_entity_type', 'N/A')}")
            print(f"    company: {intent_3.get('filters', {}).get('company', 'N/A')}")
    
    print(f"\n✅ 비교 완료")
    print(f"💾 결과 저장: {json_file}")

if __name__ == "__main__":
    main()

