#!/usr/bin/env python3
"""
API 테스트 스크립트
"""

import requests
import json
import time
from typing import Dict, Any

BASE_URL = "http://localhost:8001"


def test_health_check():
    """헬스체크 테스트"""
    print("=" * 60)
    print("1. 헬스체크 테스트")
    print("=" * 60)
    
    try:
        response = requests.get(f"{BASE_URL}/health", timeout=5)
        print(f"Status: {response.status_code}")
        print(f"Response: {response.json()}")
        return response.status_code == 200
    except Exception as e:
        print(f"❌ 에러: {e}")
        return False


def test_root():
    """루트 엔드포인트 테스트"""
    print("\n" + "=" * 60)
    print("2. 루트 엔드포인트 테스트")
    print("=" * 60)
    
    try:
        response = requests.get(f"{BASE_URL}/", timeout=5)
        print(f"Status: {response.status_code}")
        print(f"Response: {json.dumps(response.json(), indent=2, ensure_ascii=False)}")
        return response.status_code == 200
    except Exception as e:
        print(f"❌ 에러: {e}")
        return False


def test_answer_api():
    """질의 응답 API 테스트 (스트리밍)"""
    print("\n" + "=" * 60)
    print("3. 질의 응답 API 테스트 (스트리밍)")
    print("=" * 60)
    
    request_data = {
        "query": "애플의 기회 요소를 알려줘",
        "use_vector_search": False,
        "top_k": 5
    }
    
    try:
        print(f"요청: {json.dumps(request_data, indent=2, ensure_ascii=False)}")
        print("\n스트리밍 응답:")
        print("-" * 60)
        
        response = requests.post(
            f"{BASE_URL}/answer",
            json=request_data,
            stream=True,
            timeout=30
        )
        
        if response.status_code != 200:
            print(f"❌ Status: {response.status_code}")
            print(f"Response: {response.text}")
            return False
        
        full_text = ""
        for line in response.iter_lines():
            if line:
                line_str = line.decode('utf-8')
                if line_str.startswith('data: '):
                    chunk = line_str[6:]  # 'data: ' 제거
                    if chunk == '[DONE]':
                        print("\n[DONE]")
                        break
                    print(chunk, end='', flush=True)
                    full_text += chunk
        
        print(f"\n\n전체 응답 길이: {len(full_text)} 문자")
        return True
        
    except Exception as e:
        print(f"❌ 에러: {e}")
        import traceback
        traceback.print_exc()
        return False


def test_download_api():
    """공시 다운로드 API 테스트"""
    print("\n" + "=" * 60)
    print("4. 공시 다운로드 API 테스트")
    print("=" * 60)
    
    request_data = {
        "ticker": "AAPL",
        "filing_types": ["10-K"],
        "limits": {"10-K": 1}  # 테스트용으로 1건만
    }
    
    try:
        print(f"요청: {json.dumps(request_data, indent=2, ensure_ascii=False)}")
        print("\n다운로드 중... (시간이 걸릴 수 있습니다)")
        
        response = requests.post(
            f"{BASE_URL}/download",
            json=request_data,
            timeout=300  # 5분 타임아웃
        )
        
        print(f"Status: {response.status_code}")
        
        if response.status_code == 200:
            result = response.json()
            print(f"Response: {json.dumps(result, indent=2, ensure_ascii=False)}")
            return True
        else:
            print(f"❌ Response: {response.text}")
            return False
            
    except Exception as e:
        print(f"❌ 에러: {e}")
        import traceback
        traceback.print_exc()
        return False


def test_process_api():
    """문서 처리 API 테스트"""
    print("\n" + "=" * 60)
    print("5. 문서 처리 API 테스트")
    print("=" * 60)
    
    request_data = {
        "ticker": "AAPL",
        "skip_duplicates": True,
        "with_embedding": False,  # 테스트용으로 embedding 생성 안 함
        "filing_types": ["10-K"]
    }
    
    try:
        print(f"요청: {json.dumps(request_data, indent=2, ensure_ascii=False)}")
        print("\n처리 중... (시간이 걸릴 수 있습니다)")
        
        response = requests.post(
            f"{BASE_URL}/process",
            json=request_data,
            timeout=600  # 10분 타임아웃
        )
        
        print(f"Status: {response.status_code}")
        
        if response.status_code == 200:
            result = response.json()
            print(f"Response: {json.dumps(result, indent=2, ensure_ascii=False)}")
            return True
        else:
            print(f"❌ Response: {response.text}")
            return False
            
    except Exception as e:
        print(f"❌ 에러: {e}")
        import traceback
        traceback.print_exc()
        return False


def main():
    """메인 테스트 함수"""
    print("🚀 API 테스트 시작\n")
    
    results = {
        "헬스체크": test_health_check(),
        "루트 엔드포인트": test_root(),
        "질의 응답 API": test_answer_api(),
        # "공시 다운로드 API": test_download_api(),  # 시간이 오래 걸리므로 주석 처리
        # "문서 처리 API": test_process_api(),  # 시간이 오래 걸리므로 주석 처리
    }
    
    print("\n" + "=" * 60)
    print("테스트 결과 요약")
    print("=" * 60)
    
    for test_name, result in results.items():
        status = "✅ 통과" if result else "❌ 실패"
        print(f"{test_name}: {status}")
    
    total = len(results)
    passed = sum(results.values())
    print(f"\n총 {total}개 테스트 중 {passed}개 통과")


if __name__ == "__main__":
    main()

