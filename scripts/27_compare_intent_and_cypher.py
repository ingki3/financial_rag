#!/usr/bin/env python
"""
인텐트 및 Cypher 쿼리 비교 테스트

두 모델로 인텐트와 Cypher 쿼리를 추출하여 차이 비교:
- gemini-2.5-flash-lite
- gemini-3-flash-preview
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

from app.services.intent_extractor import IntentExtractor
from app.services.cypher_query_builder import CypherQueryBuilder
from app.services.name_normalizer import NameNormalizer

def extract_intent_and_cypher(intent_model: str, query: str):
    """인텐트와 Cypher 쿼리 추출"""
    # IntentExtractor 초기화
    intent_extractor = IntentExtractor(model=intent_model)
    
    # CypherQueryBuilder 초기화
    cypher_builder = CypherQueryBuilder()
    
    # NameNormalizer 초기화
    name_normalizer = NameNormalizer()
    
    # 1. Intent 추출
    intent_start = time.time()
    intent = intent_extractor.extract_intent_sync(query)
    intent_time = (time.time() - intent_start) * 1000
    
    # 2. Name 정규화 (필터에 이름이 있는 경우)
    normalized_filters = None
    if intent and intent.get('filters'):
        filters = intent.get('filters', {})
        if filters.get('product') or filters.get('person') or filters.get('technology'):
            try:
                normalized_filters = name_normalizer.normalize_filters(intent)
            except Exception as e:
                print(f"  ⚠️ 이름 정규화 실패: {e}")
    
    # 3. Cypher 쿼리 생성
    cypher_start = time.time()
    try:
        cypher_query, params = cypher_builder.build_query(intent)
        cypher_time = (time.time() - cypher_start) * 1000
    except Exception as e:
        print(f"  ⚠️ Cypher 쿼리 생성 실패: {e}")
        cypher_query = None
        params = None
        cypher_time = (time.time() - cypher_start) * 1000
    
    return {
        "intent": intent,
        "normalized_filters": normalized_filters,
        "cypher_query": cypher_query,
        "cypher_params": params,
        "intent_time_ms": intent_time,
        "cypher_time_ms": cypher_time
    }

def compare_results(results_25: dict, results_3: dict, query: str):
    """두 결과 비교"""
    comparison = {
        "query": query,
        "intent_match": False,
        "cypher_match": False,
        "intent_diff": {},
        "cypher_diff": {}
    }
    
    # Intent 비교
    intent_25 = results_25.get("intent", {})
    intent_3 = results_3.get("intent", {})
    
    if intent_25 and intent_3:
        # 주요 필드 비교
        target_match = intent_25.get("target_entity_type") == intent_3.get("target_entity_type")
        query_text_match = intent_25.get("query_text") == intent_3.get("query_text")
        query_type_match = intent_25.get("query_type") == intent_3.get("query_type")
        
        # Filters 비교
        filters_25 = intent_25.get("filters", {})
        filters_3 = intent_3.get("filters", {})
        
        company_match = filters_25.get("company") == filters_3.get("company")
        product_match = filters_25.get("product") == filters_3.get("product")
        person_match = filters_25.get("person") == filters_3.get("person")
        technology_match = filters_25.get("technology") == filters_3.get("technology")
        time_match = filters_25.get("time") == filters_3.get("time")
        context_match = filters_25.get("context") == filters_3.get("context")
        
        comparison["intent_match"] = (
            target_match and query_text_match and query_type_match and
            company_match and product_match and person_match and 
            technology_match and time_match and context_match
        )
        
        comparison["intent_diff"] = {
            "target_entity_type": {
                "25": intent_25.get("target_entity_type"),
                "3": intent_3.get("target_entity_type"),
                "match": target_match
            },
            "query_text": {
                "25": intent_25.get("query_text"),
                "3": intent_3.get("query_text"),
                "match": query_text_match
            },
            "query_type": {
                "25": intent_25.get("query_type"),
                "3": intent_3.get("query_type"),
                "match": query_type_match
            },
            "filters": {
                "company": {
                    "25": filters_25.get("company"),
                    "3": filters_3.get("company"),
                    "match": company_match
                },
                "product": {
                    "25": filters_25.get("product"),
                    "3": filters_3.get("product"),
                    "match": product_match
                },
                "person": {
                    "25": filters_25.get("person"),
                    "3": filters_3.get("person"),
                    "match": person_match
                },
                "technology": {
                    "25": filters_25.get("technology"),
                    "3": filters_3.get("technology"),
                    "match": technology_match
                },
                "time": {
                    "25": filters_25.get("time"),
                    "3": filters_3.get("time"),
                    "match": time_match
                },
                "context": {
                    "25": filters_25.get("context"),
                    "3": filters_3.get("context"),
                    "match": context_match
                }
            }
        }
    
    # Cypher 쿼리 비교
    cypher_25 = results_25.get("cypher_query")
    cypher_3 = results_3.get("cypher_query")
    
    if cypher_25 and cypher_3:
        # 쿼리 문자열 정규화 (공백 제거)
        cypher_25_normalized = " ".join(cypher_25.split())
        cypher_3_normalized = " ".join(cypher_3.split())
        
        comparison["cypher_match"] = cypher_25_normalized == cypher_3_normalized
        
        comparison["cypher_diff"] = {
            "match": comparison["cypher_match"],
            "25": cypher_25,
            "3": cypher_3
        }
        
        # 파라미터 비교
        params_25 = results_25.get("cypher_params", {})
        params_3 = results_3.get("cypher_params", {})
        
        comparison["cypher_params_match"] = params_25 == params_3
        comparison["cypher_params_diff"] = {
            "match": comparison["cypher_params_match"],
            "25": params_25,
            "3": params_3
        }
    elif cypher_25 is None and cypher_3 is None:
        comparison["cypher_match"] = True
    else:
        comparison["cypher_match"] = False
        comparison["cypher_diff"] = {
            "25": cypher_25,
            "3": cypher_3
        }
    
    return comparison

def main():
    """메인 테스트 함수"""
    print("=" * 80)
    print("인텐트 및 Cypher 쿼리 비교 테스트")
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
    
    all_results = {
        "timestamp": datetime.now().isoformat(),
        "test_queries": test_queries,
        "results": []
    }
    
    comparisons = []
    
    for i, query in enumerate(test_queries, 1):
        print(f"[{i}/{len(test_queries)}] {query}")
        
        # gemini-2.5-flash-lite로 추출
        print("  gemini-2.5-flash-lite로 추출 중...")
        results_25 = extract_intent_and_cypher("gemini-2.5-flash-lite", query)
        
        # gemini-3-flash-preview로 추출
        print("  gemini-3-flash-preview로 추출 중...")
        results_3 = extract_intent_and_cypher("gemini-3-flash-preview", query)
        
        # 비교
        comparison = compare_results(results_25, results_3, query)
        comparisons.append(comparison)
        
        # 결과 저장
        all_results["results"].append({
            "query": query,
            "gemini-2.5-flash-lite": results_25,
            "gemini-3-flash-preview": results_3,
            "comparison": comparison
        })
        
        # 간단한 결과 출력
        intent_match = "✅" if comparison["intent_match"] else "❌"
        cypher_match = "✅" if comparison["cypher_match"] else "❌"
        print(f"  인텐트 일치: {intent_match} | Cypher 일치: {cypher_match}")
        if not comparison["intent_match"]:
            print(f"    인텐트 차이 발견!")
        if not comparison["cypher_match"]:
            print(f"    Cypher 쿼리 차이 발견!")
    
    # JSON 저장
    json_file = Path("test_result/intent_cypher_comparison.json")
    json_file.parent.mkdir(exist_ok=True)
    with open(json_file, 'w', encoding='utf-8') as f:
        json.dump(all_results, f, ensure_ascii=False, indent=2)
    
    # 통계 출력
    print("\n" + "=" * 80)
    print("비교 결과 통계")
    print("=" * 80)
    
    intent_matches = sum(1 for c in comparisons if c["intent_match"])
    cypher_matches = sum(1 for c in comparisons if c["cypher_match"])
    
    print(f"\n인텐트 일치: {intent_matches}/{len(comparisons)}개 ({intent_matches/len(comparisons)*100:.1f}%)")
    print(f"Cypher 쿼리 일치: {cypher_matches}/{len(comparisons)}개 ({cypher_matches/len(comparisons)*100:.1f}%)")
    
    # 차이가 있는 케이스 출력
    print("\n차이가 있는 케이스:")
    for i, comp in enumerate(comparisons, 1):
        if not comp["intent_match"] or not comp["cypher_match"]:
            print(f"\n[{i}] {comp['query']}")
            if not comp["intent_match"]:
                print("  인텐트 차이:")
                for key, value in comp["intent_diff"].items():
                    if isinstance(value, dict) and not value.get("match", True):
                        print(f"    {key}: {value}")
            if not comp["cypher_match"]:
                print("  Cypher 쿼리 차이:")
                print(f"    gemini-2.5-flash-lite:")
                print(f"      {comp['cypher_diff'].get('25', 'N/A')[:200]}...")
                print(f"    gemini-3-flash-preview:")
                print(f"      {comp['cypher_diff'].get('3', 'N/A')[:200]}...")
    
    # 시간 비교
    print("\n시간 비교:")
    intent_times_25 = [r["gemini-2.5-flash-lite"]["intent_time_ms"] for r in all_results["results"]]
    intent_times_3 = [r["gemini-3-flash-preview"]["intent_time_ms"] for r in all_results["results"]]
    cypher_times_25 = [r["gemini-2.5-flash-lite"]["cypher_time_ms"] for r in all_results["results"]]
    cypher_times_3 = [r["gemini-3-flash-preview"]["cypher_time_ms"] for r in all_results["results"]]
    
    from statistics import mean
    print(f"  인텐트 추출 시간:")
    print(f"    gemini-2.5-flash-lite: 평균 {mean(intent_times_25):.2f}ms")
    print(f"    gemini-3-flash-preview: 평균 {mean(intent_times_3):.2f}ms")
    print(f"    차이: {mean(intent_times_3) - mean(intent_times_25):.2f}ms ({((mean(intent_times_3) - mean(intent_times_25))/mean(intent_times_25)*100):.1f}%)")
    
    print(f"  Cypher 쿼리 생성 시간:")
    print(f"    gemini-2.5-flash-lite 인텐트: 평균 {mean(cypher_times_25):.2f}ms")
    print(f"    gemini-3-flash-preview 인텐트: 평균 {mean(cypher_times_3):.2f}ms")
    print(f"    차이: {mean(cypher_times_3) - mean(cypher_times_25):.2f}ms ({((mean(cypher_times_3) - mean(cypher_times_25))/mean(cypher_times_25)*100):.1f}%)")
    
    print(f"\n✅ 비교 완료")
    print(f"💾 결과 저장: {json_file}")

if __name__ == "__main__":
    main()

