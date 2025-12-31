"""
이름 표준화 테스트 스크립트

시간 측정 및 정확도 확인
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
import json
from app.services.name_normalizer import NameNormalizer

logging.basicConfig(level=logging.WARNING)
logger = logging.getLogger(__name__)


def test_name_normalization():
    """이름 표준화 테스트"""
    
    print("=" * 80)
    print("이름 표준화 테스트 (선 매칭 후 LLM 처리)")
    print("=" * 80)
    
    normalizer = NameNormalizer()
    
    # 다양한 테스트 케이스
    test_cases = [
        # (입력 이름, 노드 타입, 티커, 예상 결과, 매칭 방식)
        # 정확 매칭 케이스
        ("iPhone", "Product", "AAPL", "iPhone", "정확 매칭"),
        ("iPhone 15", "Product", "AAPL", "iPhone 15", "정확 매칭"),
        ("Mac", "Product", "AAPL", "Mac", "정확 매칭"),
        ("iPad", "Product", "AAPL", "iPad", "정확 매칭"),
        
        # 부분 매칭 케이스
        ("MacBook", "Product", "AAPL", "Mac", "부분 매칭"),
        ("MacBook Pro", "Product", "AAPL", "Mac", "부분 매칭"),
        ("iPhone 15 Pro Max", "Product", "AAPL", "iPhone 15 Pro", "부분 매칭"),
        
        # LLM 필요 케이스 (다양한 표현)
        ("아이폰", "Product", "AAPL", "iPhone", "LLM 매칭"),
        ("맥북", "Product", "AAPL", "Mac", "LLM 매칭"),
        ("아이패드", "Product", "AAPL", "iPad", "LLM 매칭"),
        
        # Technology 케이스
        ("AI", "Technology", "GOOGL", None, "부분 매칭 또는 LLM"),
        ("Machine Learning", "Technology", "GOOGL", None, "부분 매칭 또는 LLM"),
        ("인공지능", "Technology", "GOOGL", None, "LLM 매칭"),
        
        # 대소문자 변형
        ("IPHONE", "Product", "AAPL", "iPhone", "정확 매칭"),
        ("iphone", "Product", "AAPL", "iPhone", "정확 매칭"),
        ("iPHONE 15", "Product", "AAPL", "iPhone 15", "정확 매칭"),
        
        # 공백 처리
        (" iPhone ", "Product", "AAPL", "iPhone", "정확 매칭"),
        ("iPhone  15", "Product", "AAPL", "iPhone 15", "정확 매칭"),
    ]
    
    print(f"\n총 테스트 케이스: {len(test_cases)}개\n")
    
    results = []
    exact_match_count = 0
    partial_match_count = 0
    llm_match_count = 0
    failed_count = 0
    
    for i, (input_name, node_type, ticker, expected, match_type) in enumerate(test_cases, 1):
        print(f"[{i}/{len(test_cases)}] {input_name} ({node_type}, {ticker})")
        print("-" * 80)
        
        # 시간 측정
        start_time = time.time()
        
        # LLM 없이 테스트 (매칭만)
        result_no_llm = normalizer.normalize(input_name, node_type, ticker, use_llm=False)
        time_no_llm = (time.time() - start_time) * 1000
        
        # LLM 포함 테스트
        start_time_llm = time.time()
        result_with_llm = normalizer.normalize(input_name, node_type, ticker, use_llm=True)
        time_with_llm = (time.time() - start_time_llm) * 1000
        
        # 매칭 방식 판단
        if result_no_llm == result_with_llm:
            if result_no_llm == input_name or result_no_llm is None:
                actual_match_type = "실패"
                failed_count += 1
            elif input_name.lower().strip() == result_no_llm.lower().strip():
                actual_match_type = "정확 매칭"
                exact_match_count += 1
            else:
                actual_match_type = "부분 매칭"
                partial_match_count += 1
        else:
            actual_match_type = "LLM 매칭"
            llm_match_count += 1
        
        # 정확도 판단
        is_correct = False
        if expected:
            is_correct = (result_with_llm == expected)
        else:
            # 예상 결과가 None인 경우, 표준 이름 목록에 있는지만 확인
            standard_names = normalizer._standard_dicts.get(ticker, {}).get(node_type, [])
            is_correct = (result_with_llm in standard_names) if result_with_llm else False
        
        print(f"  입력: {input_name}")
        print(f"  결과 (매칭만): {result_no_llm} ({time_no_llm:.2f}ms)")
        print(f"  결과 (LLM 포함): {result_with_llm} ({time_with_llm:.2f}ms)")
        print(f"  매칭 방식: {actual_match_type}")
        print(f"  정확도: {'✅ 정확' if is_correct else '❌ 오류'}")
        if expected and result_with_llm != expected:
            print(f"  예상: {expected}, 실제: {result_with_llm}")
        
        results.append({
            "input": input_name,
            "node_type": node_type,
            "ticker": ticker,
            "result_no_llm": result_no_llm,
            "result_with_llm": result_with_llm,
            "time_no_llm_ms": time_no_llm,
            "time_with_llm_ms": time_with_llm,
            "match_type": actual_match_type,
            "is_correct": is_correct,
            "expected": expected
        })
        
        print()
    
    # 통계 계산
    times_no_llm = [r["time_no_llm_ms"] for r in results]
    times_with_llm = [r["time_with_llm_ms"] for r in results]
    correct_count = sum(1 for r in results if r["is_correct"])
    
    print("=" * 80)
    print("테스트 결과 통계")
    print("=" * 80)
    
    print(f"\n📊 매칭 방식 분포:")
    print(f"   정확 매칭: {exact_match_count}개 ({exact_match_count/len(test_cases)*100:.1f}%)")
    print(f"   부분 매칭: {partial_match_count}개 ({partial_match_count/len(test_cases)*100:.1f}%)")
    print(f"   LLM 매칭: {llm_match_count}개 ({llm_match_count/len(test_cases)*100:.1f}%)")
    print(f"   실패: {failed_count}개 ({failed_count/len(test_cases)*100:.1f}%)")
    
    print(f"\n📊 시간 측정 (매칭만, LLM 없음):")
    print(f"   평균: {mean(times_no_llm):.2f}ms")
    print(f"   중앙값: {median(times_no_llm):.2f}ms")
    print(f"   최소: {min(times_no_llm):.2f}ms")
    print(f"   최대: {max(times_no_llm):.2f}ms")
    
    print(f"\n📊 시간 측정 (LLM 포함):")
    print(f"   평균: {mean(times_with_llm):.2f}ms")
    print(f"   중앙값: {median(times_with_llm):.2f}ms")
    print(f"   최소: {min(times_with_llm):.2f}ms")
    print(f"   최대: {max(times_with_llm):.2f}ms")
    
    # LLM이 실제로 사용된 케이스만 필터링
    llm_used_times = [r["time_with_llm_ms"] for r in results if r["match_type"] == "LLM 매칭"]
    if llm_used_times:
        print(f"\n📊 LLM 사용 케이스 시간:")
        print(f"   평균: {mean(llm_used_times):.2f}ms")
        print(f"   중앙값: {median(llm_used_times):.2f}ms")
        print(f"   최소: {min(llm_used_times):.2f}ms")
        print(f"   최대: {max(llm_used_times):.2f}ms")
    
    print(f"\n📊 정확도:")
    print(f"   정확한 결과: {correct_count}개 / {len(test_cases)}개")
    print(f"   정확도: {correct_count/len(test_cases)*100:.1f}%")
    
    # 상세 결과 표
    print(f"\n📋 상세 결과:")
    print("-" * 100)
    print(f"{'입력':<25} {'결과':<25} {'매칭':<12} {'시간(매칭)':<12} {'시간(LLM)':<12} {'정확도':<8}")
    print("-" * 100)
    for r in results:
        input_short = r["input"][:23] + ".." if len(r["input"]) > 25 else r["input"]
        result_short = (r["result_with_llm"] or "None")[:23] + ".." if r["result_with_llm"] and len(r["result_with_llm"]) > 25 else (r["result_with_llm"] or "None")
        print(f"{input_short:<25} {result_short:<25} {r['match_type']:<12} {r['time_no_llm_ms']:>10.2f}ms {r['time_with_llm_ms']:>10.2f}ms {'✅' if r['is_correct'] else '❌':<8}")
    
    # 결과를 JSON 파일로 저장
    output_file = Path("test_result/name_normalization_test.json")
    output_file.parent.mkdir(exist_ok=True)
    with open(output_file, 'w', encoding='utf-8') as f:
        json.dump({
            "summary": {
                "total_cases": len(test_cases),
                "exact_match": exact_match_count,
                "partial_match": partial_match_count,
                "llm_match": llm_match_count,
                "failed": failed_count,
                "accuracy": correct_count / len(test_cases) * 100,
                "time_stats": {
                    "no_llm": {
                        "mean_ms": mean(times_no_llm),
                        "median_ms": median(times_no_llm),
                        "min_ms": min(times_no_llm),
                        "max_ms": max(times_no_llm)
                    },
                    "with_llm": {
                        "mean_ms": mean(times_with_llm),
                        "median_ms": median(times_with_llm),
                        "min_ms": min(times_with_llm),
                        "max_ms": max(times_with_llm)
                    }
                }
            },
            "details": results
        }, f, ensure_ascii=False, indent=2)
    
    print(f"\n💾 결과 저장: {output_file}")
    
    print("\n" + "=" * 80)
    print("✅ 테스트 완료")
    print("=" * 80)


if __name__ == "__main__":
    test_name_normalization()


