# Phase 3.2: 파싱 스크립트

## 📋 Sub-task 개요

파서 모듈을 실행하여 모든 다운로드된 공시 파일을 파싱하는 스크립트를 구현합니다. 다운로드된 파일을 순회하며 파서를 통해 섹션을 추출하고 JSON 형식으로 저장합니다.

### 파일 경로
**파일**: `scripts/02_parse_filings.py`

### Phase 전체 목표 기여
- 공시 파싱 프로세스 자동화
- 여러 기업의 공시 파일 일괄 파싱
- 구조화된 JSON 데이터 생성

### 입력 데이터
- **다운로드된 파일**: `data/raw/{ticker}/{filing_type}/` 폴더의 HTML/SGML 파일들

### 출력 데이터
- **파싱된 JSON 파일**: `data/parsed/{ticker}/{filing_type}/` 폴더의 JSON 파일들
- **콘솔 출력**: 파싱 진행 상황 및 결과 요약

### Class 구조
**해당 없음** (스크립트 파일)

## 🎯 주요 기능

1. **파일 순회**
   - 모든 다운로드된 공시 파일 순회
   - 티커별, 공시 유형별 처리

2. **파싱 실행**
   - `FilingParserBatch`를 사용하여 일괄 파싱
   - 섹션 추출 및 메타데이터 생성

3. **JSON 저장**
   - 파싱된 데이터를 JSON 형식으로 저장
   - `data/parsed/{ticker}/{filing_type}/` 경로에 저장

4. **진행 상황 로깅**
   - 실시간 파싱 진행 상황 출력
   - 결과 요약 출력

## 📊 데이터 구조

### 입력 데이터 구조
- **HTML/SGML 파일**: `data/raw/{ticker}/{filing_type}/{accession_number}/` 폴더의 파일들

### 출력 데이터 구조
- **파싱된 JSON 파일**:
  ```json
  {
    "metadata": {
      "ticker": "AAPL",
      "filing_type": "10-K",
      "accession_number": "0000320193-24-000077",
      "file_path": "...",
      "text_length": 12345
    },
    "sections": {
      "business": "...",
      "risk_factors": "...",
      "mda": "..."
    }
  }
  ```

## 💻 코드 예시 및 전체 코드 구현

### 스크립트 구조
```python
#!/usr/bin/env python
"""SEC 공시 파싱 스크립트"""
import json
import logging
from pathlib import Path
from app.services.processing.filing_parser import FilingParserBatch

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def main():
    parser_batch = FilingParserBatch(data_dir="./data/raw")
    results = parser_batch.parse_all()
    
    # 결과 저장
    output_dir = Path("./data/parsed")
    for parsed in results:
        ticker = parsed.metadata.ticker
        filing_type = parsed.metadata.filing_type
        accession = parsed.metadata.accession_number
        
        # 출력 디렉토리 생성
        output_path = output_dir / ticker / filing_type
        output_path.mkdir(parents=True, exist_ok=True)
        
        # JSON 파일로 저장
        output_file = output_path / f"{accession}.json"
        with open(output_file, 'w', encoding='utf-8') as f:
            json.dump(parsed.to_dict(), f, indent=2, ensure_ascii=False)
        
        logger.info(f"✅ Saved: {output_file}")
    
    print("✅ 파싱 완료!")
    print(f"총 {len(results)}개 파일 파싱됨")

if __name__ == "__main__":
    main()
```

### 실행 방법
```bash
python scripts/02_parse_filings.py
```

### 에러 핸들링
- 파일 읽기 실패: 로깅 및 계속 진행
- 파싱 실패: 로깅 및 계속 진행
- 저장 실패: 예외 처리 및 로깅

## 🔄 상세 알고리즘/프로세스

### 실행 프로세스
1. **FilingParserBatch 초기화**
   - 원본 데이터 디렉토리 지정

2. **일괄 파싱 실행**
   - `parse_all()` 메서드 호출
   - 모든 공시 파일 파싱

3. **결과 저장**
   - 각 파싱된 결과를 JSON 파일로 저장
   - 티커별, 공시 유형별 폴더 구조 유지

4. **결과 요약 출력**
   - 파싱된 파일 수 출력
   - 완료 메시지 출력

### 예외 처리
- 파일 읽기 실패: 로깅 및 계속 진행
- 파싱 실패: 로깅 및 계속 진행
- 저장 실패: 예외 처리 및 로깅

## ⚙️ 설정 및 의존성

### 필요한 환경 변수
- 없음

### 외부 라이브러리 의존성
- `beautifulsoup4`: HTML 파싱
- `lxml`: XML/HTML 파서

### 설정 파일
- 없음

## 🧪 테스트 케이스

### 단위 테스트 예시
```python
def test_main():
    # 메인 함수 테스트
    # ...
```

### 통합 테스트 시나리오
- 실제 공시 파일로 파싱 테스트
- 생성된 JSON 파일 확인
- 섹션 추출 정확도 확인

### 검증 방법
- 파싱된 JSON 파일 존재 확인
- JSON 파일 구조 확인
- 섹션 내용 확인

## ⚠️ 주의사항

- HTML 구조가 다양하여 섹션 추출이 불완전할 수 있음
- 대용량 파일 처리 시 메모리 고려
- 파싱 시간: 파일당 약 1-2분 소요

## 📝 History
