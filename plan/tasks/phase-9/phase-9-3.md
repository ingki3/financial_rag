# Phase 9.3: 검증 시나리오

## 📋 Sub-task 개요

실제 사용 케이스를 기반으로 한 검증 시나리오를 실행합니다. 주요 질의 케이스를 검증하고, 답변 품질을 확인하며, 성능을 측정합니다.

### 파일 경로
**파일**: `tests/test_validation_scenarios.py` 또는 `scripts/validate_scenarios.py`

### Phase 전체 목표 기여
- 실제 사용 케이스 검증
- 답변 품질 확인
- 성능 측정

### 입력 데이터
- **검증 시나리오**: 주요 질의 케이스

### 출력 데이터
- **검증 결과**: 성공/실패 여부 및 상세 리포트

### Class 구조
**해당 없음** (검증 스크립트)

## 🎯 주요 기능

1. **주요 질의 케이스 검증**
   - 다양한 질의 유형 테스트
   - 답변 품질 확인

2. **답변 품질 확인**
   - 답변 정확성 확인
   - 출처 정보 확인

3. **성능 측정**
   - 응답 시간 측정
   - 처리량 측정

## 📊 데이터 구조

### 검증 시나리오

| 테스트 케이스 | 입력 | 기대 결과 |
|--------------|------|----------|
| TC-01 | "애플의 기회 요소를 알려줘" | Apple 관련 기회 요소 목록 |
| TC-02 | "테슬라의 리스크는?" | Tesla 관련 리스크 요소 |
| TC-03 | "구글의 AI 전략" | Alphabet AI 관련 전략 |
| TC-04 | "엔비디아 vs AMD 비교" | 두 기업 비교 분석 |

## 💻 코드 예시 및 전체 코드 구현

### 검증 스크립트 구조
```python
#!/usr/bin/env python
"""검증 시나리오 실행 스크립트"""
from app.services.query.query_engine import QueryEngine

SCENARIOS = [
    {
        "id": "TC-01",
        "query": "애플의 기회 요소를 알려줘",
        "expected": "Apple 관련 기회 요소 목록"
    },
    # ...
]

def validate_scenarios():
    """검증 시나리오 실행"""
    engine = QueryEngine()
    
    for scenario in SCENARIOS:
        result = engine.query(scenario["query"])
        # 검증 로직
        print(f"✅ {scenario['id']}: {scenario['query']}")

if __name__ == "__main__":
    validate_scenarios()
```

### 실행 방법
```bash
python scripts/validate_scenarios.py
```

## 🔄 상세 알고리즘/프로세스

### 검증 프로세스
1. **시나리오 로드**
   - 검증 시나리오 목록 로드

2. **각 시나리오 실행**
   - QueryEngine을 통한 질의 처리
   - 결과 검증

3. **결과 리포트 생성**
   - 성공/실패 여부 기록
   - 성능 측정 결과 기록

## ⚙️ 설정 및 의존성

### 필요한 환경 변수
- `GOOGLE_API_KEY`: Gemini API 키
- `FALKORDB_HOST`: FalkorDB 호스트
- `FALKORDB_PORT`: FalkorDB 포트

### 외부 라이브러리 의존성
- 없음 (표준 라이브러리만 사용)

### 설정 파일
- 없음

## 🧪 테스트 케이스

### 검증 시나리오
- TC-01: 애플의 기회 요소
- TC-02: 테슬라의 리스크
- TC-03: 구글의 AI 전략
- TC-04: 엔비디아 vs AMD 비교

### 검증 방법
- 답변 내용 확인
- 출처 정보 확인
- 성능 측정

## ⚠️ 주의사항

- 실제 데이터가 있어야 검증 가능
- 답변 품질은 주관적일 수 있음
- 성능 측정 시 환경 영향 고려

## 📝 History
