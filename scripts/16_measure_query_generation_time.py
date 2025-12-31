"""
질의를 Cypher 쿼리로 변환하는 시간 측정

Intent 추출 및 Cypher 쿼리 생성까지의 소요 시간을 측정합니다.
"""

import sys
import os
from pathlib import Path
import time

# 프로젝트 루트를 Python 경로에 추가
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

from dotenv import load_dotenv
load_dotenv()

import logging
import json
from statistics import mean, median
from app.services.query_engine import QueryEngine
from app.services.cypher_query_builder import CypherQueryBuilder

# 로깅 설정 (WARNING으로 설정하여 불필요한 로그 제거)
logging.basicConfig(level=logging.WARNING)
logger = logging.getLogger(__name__)


def measure_query_generation_time():
    """질의를 Cypher 쿼리로 변환하는 시간 측정"""
    
    # 다양한 패턴의 테스트 질의
    test_queries = [
        "애플의 기회 요소는?",
        "테슬라의 리스크는?",
        "구글의 기술은?",
        "애플의 iPhone과 관련된 기회 요소는?",
        "애플의 Mac과 관련된 리스크는?",
        "구글의 AI 기술에 대해 알려줘",
        "애플의 2023년 기회 요소는?",
        "테슬라의 최근 리스크는?",
        "애플의 2023년 iPhone과 관련된 기회 요소는?",
        "애플과 테슬라의 리스크를 비교해줘",
    ]
    
    print("=" * 80)
    print("질의 → Cypher 쿼리 변환 시간 측정")
    print("=" * 80)
    
    try:
        engine = QueryEngine()
        query_builder = CypherQueryBuilder()
        
        print("\n✅ QueryEngine 초기화 완료\n")
        
        results = []
        
        for i, query in enumerate(test_queries, 1):
            print(f"[{i}/{len(test_queries)}] {query}")
            print("-" * 80)
            
            # 1. Intent 추출 시간 측정
            start_intent = time.time()
            intent = engine.extract_intent(query)
            intent_time = time.time() - start_intent
            
            # 2. 이름 표준화 시간 측정 (dictionary 보정)
            # build_query 내부에서 normalize_filters가 호출되므로
            # 별도로 측정하기 위해 직접 호출
            normalizer = query_builder.name_normalizer
            
            start_normalize = time.time()
            filters = intent.get("filters", [])
            if not isinstance(filters, list):
                # 기존 스키마인 경우 변환
                filters = query_builder._convert_filters_to_list(filters, intent)
            
            # ticker 추출
            ticker = None
            if isinstance(filters, list):
                company_filter = next((f for f in filters if isinstance(f, dict) and f.get("node_type") == "Company"), None)
                if company_filter:
                    ticker = company_filter.get("ticker")
            
            # 이름 표준화 수행 (dictionary 보정)
            normalized_filters = filters
            if ticker and isinstance(filters, list):
                normalized_filters = normalizer.normalize_filters(filters, ticker)
            normalize_time = time.time() - start_normalize
            
            # 3. Cypher 쿼리 생성 시간 측정 (표준화된 filters 사용)
            # 표준화된 intent로 쿼리 생성 (표준화 과정 제외)
            start_cypher = time.time()
            # 표준화된 filters를 사용하여 쿼리 생성
            intent_for_cypher = intent.copy()
            intent_for_cypher["filters"] = normalized_filters
            
            # Target 타입 추출
            target = intent_for_cypher.get("target", {})
            target_type = None
            if isinstance(target, dict):
                target_type = target.get("node_type")
            if not target_type:
                target_type = intent_for_cypher.get("target_entity_type")
            
            # 쿼리 생성 (표준화는 이미 완료)
            if not target_type or target_type == "general":
                cypher_query, params = query_builder._build_general_query(intent_for_cypher)
            elif target_type in ["Opportunity", "Risk", "Event"]:
                cypher_query, params = query_builder._build_pattern_query(target_type, normalized_filters, intent_for_cypher)
            else:
                cypher_query, params = query_builder._build_other_query(target_type, normalized_filters, intent_for_cypher)
            cypher_time = time.time() - start_cypher
            
            # 전체 시간
            total_time = intent_time + normalize_time + cypher_time
            
            print(f"  Intent 추출: {intent_time*1000:.2f}ms")
            print(f"  이름 표준화 (dictionary 보정): {normalize_time*1000:.2f}ms")
            print(f"  Cypher 생성: {cypher_time*1000:.2f}ms")
            print(f"  총 시간: {total_time*1000:.2f}ms")
            
            results.append({
                "query": query,
                "intent_time_ms": intent_time * 1000,
                "normalize_time_ms": normalize_time * 1000,
                "cypher_time_ms": cypher_time * 1000,
                "total_time_ms": total_time * 1000,
                "target_type": intent.get("target_entity_type", "unknown"),
                "has_filters": bool(intent.get("filters", {}).get("company") or 
                                   intent.get("filters", {}).get("product") or
                                   intent.get("filters", {}).get("person") or
                                   intent.get("filters", {}).get("time"))
            })
            
            print()
        
        # 통계 계산
        intent_times = [r["intent_time_ms"] for r in results]
        normalize_times = [r["normalize_time_ms"] for r in results]
        cypher_times = [r["cypher_time_ms"] for r in results]
        total_times = [r["total_time_ms"] for r in results]
        
        print("=" * 80)
        print("시간 측정 결과 통계")
        print("=" * 80)
        
        print(f"\n📊 Intent 추출 시간:")
        print(f"   평균: {mean(intent_times):.2f}ms")
        print(f"   중앙값: {median(intent_times):.2f}ms")
        print(f"   최소: {min(intent_times):.2f}ms")
        print(f"   최대: {max(intent_times):.2f}ms")
        
        print(f"\n📊 이름 표준화 시간 (dictionary 보정):")
        print(f"   평균: {mean(normalize_times):.2f}ms")
        print(f"   중앙값: {median(normalize_times):.2f}ms")
        print(f"   최소: {min(normalize_times):.2f}ms")
        print(f"   최대: {max(normalize_times):.2f}ms")
        
        print(f"\n📊 Cypher 쿼리 생성 시간:")
        print(f"   평균: {mean(cypher_times):.2f}ms")
        print(f"   중앙값: {median(cypher_times):.2f}ms")
        print(f"   최소: {min(cypher_times):.2f}ms")
        print(f"   최대: {max(cypher_times):.2f}ms")
        
        print(f"\n📊 전체 시간 (Intent + 표준화 + Cypher):")
        print(f"   평균: {mean(total_times):.2f}ms")
        print(f"   중앙값: {median(total_times):.2f}ms")
        print(f"   최소: {min(total_times):.2f}ms")
        print(f"   최대: {max(total_times):.2f}ms")
        
        # 필터 유무별 통계
        with_filters = [r for r in results if r["has_filters"]]
        without_filters = [r for r in results if not r["has_filters"]]
        
        if with_filters:
            print(f"\n📊 필터 있는 질의 ({len(with_filters)}개):")
            filter_times = [r["total_time_ms"] for r in with_filters]
            print(f"   평균: {mean(filter_times):.2f}ms")
            print(f"   중앙값: {median(filter_times):.2f}ms")
        
        if without_filters:
            print(f"\n📊 필터 없는 질의 ({len(without_filters)}개):")
            no_filter_times = [r["total_time_ms"] for r in without_filters]
            print(f"   평균: {mean(no_filter_times):.2f}ms")
            print(f"   중앙값: {median(no_filter_times):.2f}ms")
        
        # 상세 결과 표
        print(f"\n📋 상세 결과:")
        print("-" * 100)
        print(f"{'질의':<40} {'Intent':<12} {'표준화':<12} {'Cypher':<12} {'총 시간':<12}")
        print("-" * 100)
        for r in results:
            query_short = r["query"][:38] + ".." if len(r["query"]) > 40 else r["query"]
            print(f"{query_short:<40} {r['intent_time_ms']:>10.2f}ms {r['normalize_time_ms']:>10.2f}ms {r['cypher_time_ms']:>10.2f}ms {r['total_time_ms']:>10.2f}ms")
        
        # 결과를 JSON 파일로 저장
        output_file = Path("test_result/query_generation_time_measurement.json")
        output_file.parent.mkdir(exist_ok=True)
        with open(output_file, 'w', encoding='utf-8') as f:
            json.dump({
                "summary": {
                    "total_queries": len(test_queries),
                    "intent_time": {
                        "mean_ms": mean(intent_times),
                        "median_ms": median(intent_times),
                        "min_ms": min(intent_times),
                        "max_ms": max(intent_times)
                    },
                    "normalize_time": {
                        "mean_ms": mean(normalize_times),
                        "median_ms": median(normalize_times),
                        "min_ms": min(normalize_times),
                        "max_ms": max(normalize_times)
                    },
                    "cypher_time": {
                        "mean_ms": mean(cypher_times),
                        "median_ms": median(cypher_times),
                        "min_ms": min(cypher_times),
                        "max_ms": max(cypher_times)
                    },
                    "total_time": {
                        "mean_ms": mean(total_times),
                        "median_ms": median(total_times),
                        "min_ms": min(total_times),
                        "max_ms": max(total_times)
                    }
                },
                "details": results
            }, f, ensure_ascii=False, indent=2)
        
        print(f"\n💾 결과 저장: {output_file}")
        
        engine.close()
        
        print("\n" + "=" * 80)
        print("✅ 측정 완료")
        print("=" * 80)
        
    except Exception as e:
        logger.error(f"측정 실패: {e}", exc_info=True)
        print(f"\n❌ 측정 실패: {e}\n")


if __name__ == "__main__":
    measure_query_generation_time()

