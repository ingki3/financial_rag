# Phase 4.2: 추출 스크립트

## 📋 Sub-task 개요

추출기 모듈을 실행하여 모든 파싱된 파일에서 Triplet을 추출하는 스크립트를 구현합니다. 파싱된 파일을 순회하며 LLM을 통한 Triplet 추출을 수행하고 JSON 형식으로 저장합니다.

### 파일 경로
**파일**: `scripts/03_extract_triplets.py`

### Phase 전체 목표 기여
- Knowledge Triplet 추출 프로세스 자동화
- 여러 기업의 공시 파일 일괄 추출
- 구조화된 Triplet 데이터 생성

### 입력 데이터
- **파싱된 JSON 파일**: `data/parsed/{ticker}/{filing_type}/` 폴더의 JSON 파일들
- **환경 변수**: `GOOGLE_API_KEY` (Gemini API 키)

### 출력 데이터
- **추출된 JSON 파일**: `data/extracted/{ticker}/{filing_type}/` 폴더의 JSON 파일들
- **콘솔 출력**: 추출 진행 상황 및 결과 요약

### Class 구조
**해당 없음** (스크립트 파일)

## 🎯 주요 기능

1. **파일 순회**
   - 모든 파싱된 공시 파일 순회
   - 티커별, 공시 유형별 처리

2. **Triplet 추출**
   - `TripletExtractorBatch`를 사용하여 일괄 추출
   - LLM을 통한 구조화된 Triplet 추출

3. **JSON 저장**
   - 추출된 데이터를 JSON 형식으로 저장
   - `data/extracted/{ticker}/{filing_type}/` 경로에 저장

4. **진행 상황 로깅**
   - 실시간 추출 진행 상황 출력
   - 결과 요약 출력

## 📊 데이터 구조

### 입력 데이터 구조
- **파싱된 JSON 파일**: `data/parsed/{ticker}/{filing_type}/{accession_number}.json`

### 출력 데이터 구조
- **추출된 JSON 파일**:
  ```json
  {
    "ticker": "AAPL",
    "filing_type": "10-K",
    "accession_number": "0000320193-24-000077",
    "extracted_at": "2024-01-01T00:00:00Z",
    "risks": [...],
    "opportunities": [...],
    "events": [...],
    "technologies": [...],
    "mentioned_products_global": [...],
    "mentioned_persons_global": [...]
  }
  ```

## 💻 코드 예시 및 전체 코드 구현

### 스크립트 구조
```python
#!/usr/bin/env python
"""Knowledge Triplet 추출 스크립트"""
import logging
from dotenv import load_dotenv
from app.services.processing.triplet_extractor import TripletExtractorBatch

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def main():
    load_dotenv()
    
    extractor_batch = TripletExtractorBatch(
        parsed_dir="./data/parsed",
        output_dir="./data/extracted",
        combine_sections_per_filing=True  # 파일 단위로 합쳐서 저장
    )
    
    results = extractor_batch.extract_all()
    
    print("✅ 추출 완료!")
    print(f"총 {len(results)}개 섹션에서 추출됨")

if __name__ == "__main__":
    main()
```

### 실행 방법
```bash
# 전체 추출
python scripts/03_extract_triplets.py

# 특정 모드 (section/filing)
python scripts/03_extract_triplets.py --mode section
```

### 에러 핸들링
- 환경 변수 누락: 에러 메시지 출력 및 종료
- LLM API 호출 실패: 로깅 및 계속 진행
- 파일 저장 실패: 예외 처리 및 로깅

## 🔄 상세 알고리즘/프로세스

### 실행 프로세스
1. **환경 변수 로드**
   - `load_dotenv()`로 `.env` 파일 로드
   - `GOOGLE_API_KEY` 확인

2. **TripletExtractorBatch 초기화**
   - 파싱된 파일 디렉토리 지정
   - 출력 디렉토리 지정
   - 모드 설정 (섹션별/파일별)

3. **일괄 추출 실행**
   - `extract_all()` 메서드 호출
   - 모든 파싱된 파일에서 Triplet 추출

4. **결과 저장**
   - 각 추출된 결과를 JSON 파일로 저장
   - 티커별, 공시 유형별 폴더 구조 유지

5. **결과 요약 출력**
   - 추출된 Triplet 수 출력
   - 완료 메시지 출력

### 예외 처리
- 환경 변수 누락: 에러 메시지 출력 및 종료
- LLM API 호출 실패: 로깅 및 계속 진행
- 파일 저장 실패: 예외 처리 및 로깅

## ⚙️ 설정 및 의존성

### 필요한 환경 변수
- `GOOGLE_API_KEY`: Gemini API 키 (필수)

### 외부 라이브러리 의존성
- `python-dotenv`: 환경 변수 로드
- `google-genai`: Gemini LLM API 클라이언트

### 설정 파일
- `.env`: 환경 변수 파일
- `app/prompts/triplet_extractor.yaml`: 추출 프롬프트 템플릿

## 🧪 테스트 케이스

### 단위 테스트 예시
```python
def test_main():
    # 메인 함수 테스트
    # ...
```

### 통합 테스트 시나리오
- 실제 파싱된 파일로 추출 테스트
- 생성된 JSON 파일 확인
- Triplet 구조 확인

### 검증 방법
- 추출된 JSON 파일 존재 확인
- JSON 파일 구조 확인
- Triplet 내용 확인

## ⚠️ 주의사항

- 추출 시간: 파일당 약 1-2분 소요
- LLM API 비용 발생
- 백그라운드 실행 권장
- API 속도 제한 준수 필요

## 📝 History
