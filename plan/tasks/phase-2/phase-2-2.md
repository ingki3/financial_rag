# Phase 2.2: 다운로드 스크립트

## 📋 Sub-task 개요

다운로더 모듈을 실행하여 모든 공시 자료를 다운로드하는 스크립트를 구현합니다. 환경 변수를 로드하고, 다운로더를 초기화한 후 전체 다운로드를 실행합니다.

### 파일 경로
**파일**: `scripts/01_download_filings.py`

### Phase 전체 목표 기여
- SEC 공시 다운로드 프로세스 자동화
- 여러 기업의 공시 자료 일괄 다운로드
- 진행 상황 로깅 및 결과 요약

### 입력 데이터
- **환경 변수**: `SEC_USER_AGENT` (SEC API 접근을 위한 User-Agent)
- **커맨드라인 인자**: 선택적 (특정 티커만 다운로드하는 경우)

### 출력 데이터
- **다운로드된 파일**: `data/raw/{ticker}/{filing_type}/` 폴더 구조
- **콘솔 출력**: 다운로드 진행 상황 및 결과 요약

### Class 구조
**해당 없음** (스크립트 파일)

## 🎯 주요 기능

1. **환경 변수 로드**
   - `python-dotenv`를 사용하여 `.env` 파일에서 환경 변수 로드
   - `SEC_USER_AGENT` 확인

2. **다운로더 초기화**
   - `SECFilingDownloader` 인스턴스 생성
   - 환경 변수 전달

3. **전체 다운로드 실행**
   - 모든 대상 기업의 모든 공시 다운로드
   - 또는 특정 티커만 다운로드 (argparse 지원 시)

4. **진행 상황 로깅**
   - 실시간 다운로드 진행 상황 출력
   - 결과 요약 출력

## 📊 데이터 구조

### 입력 데이터 구조
- **환경 변수**: `SEC_USER_AGENT="Your Name your.email@example.com"`

### 출력 데이터 구조
- **다운로드 통계**:
  ```python
  {
      "AAPL": {
          "10-K": 3,
          "10-Q": 12,
          "8-K": 20
      },
      ...
  }
  ```

## 💻 코드 예시 및 전체 코드 구현

### 스크립트 구조
```python
#!/usr/bin/env python
"""SEC 10-K, 10-Q, 8-K 공시 자료 다운로드 스크립트"""
import os
import logging
from dotenv import load_dotenv
from app.services.download.sec_downloader import SECFilingDownloader

logging.basicConfig(level=logging.INFO)

def main():
    load_dotenv()
    
    downloader = SECFilingDownloader(
        data_dir="./data/raw",
        user_agent=os.getenv("SEC_USER_AGENT")
    )
    
    print("=" * 60)
    print("SEC Filing Downloader")
    print("=" * 60)
    print(f"대상 기업: {', '.join(downloader.TICKERS)}")
    print(f"공시 유형: 10-K (연간), 10-Q (분기), 8-K (수시)")
    print("=" * 60)
    
    results = downloader.download_all()
    
    # 결과 요약 출력
    print("\n✅ 다운로드 완료!")
    print("저장 위치: ./data/raw/{ticker}/{filing_type}/")
    
    # 통계 출력
    total = sum(sum(counts.values()) for counts in results.values())
    print(f"총 다운로드: {total}건")

if __name__ == "__main__":
    main()
```

### 실행 방법
```bash
# 스크립트 실행
python scripts/01_download_filings.py

# 특정 티커만 다운로드 (스크립트 수정 필요)
# 또는 argparse를 추가하여 --ticker 옵션 지원
```

### 에러 핸들링
- 환경 변수 누락: 에러 메시지 출력 및 종료
- 다운로드 실패: 로깅 및 계속 진행
- 네트워크 오류: 예외 처리 및 재시도 고려

## 🔄 상세 알고리즘/프로세스

### 실행 프로세스
1. **환경 변수 로드**
   - `load_dotenv()`로 `.env` 파일 로드
   - `SEC_USER_AGENT` 확인

2. **다운로더 초기화**
   - `SECFilingDownloader` 인스턴스 생성
   - 환경 변수 전달

3. **다운로드 실행**
   - `download_all()` 메서드 호출
   - 모든 기업의 모든 공시 다운로드

4. **결과 출력**
   - 다운로드 통계 출력
   - 저장 위치 안내

### 예외 처리
- 환경 변수 누락: 에러 메시지 출력 및 종료
- 다운로드 실패: 로깅 및 계속 진행
- 네트워크 오류: 예외 처리 및 재시도 고려

## ⚙️ 설정 및 의존성

### 필요한 환경 변수
- `SEC_USER_AGENT`: SEC API 접근을 위한 User-Agent (필수)

### 외부 라이브러리 의존성
- `python-dotenv`: 환경 변수 로드
- `sec-edgar-downloader`: SEC EDGAR 공시 다운로드

### 설정 파일
- `.env`: 환경 변수 파일

## 🧪 테스트 케이스

### 단위 테스트 예시
```python
def test_main():
    # 메인 함수 테스트
    # ...
```

### 통합 테스트 시나리오
- 실제 다운로드 실행 테스트
- 다운로드된 파일 확인
- 통계 정확성 확인

### 검증 방법
- 다운로드된 파일 존재 확인
- 파일 수 확인
- 통계 정확성 확인

## ⚠️ 주의사항

- 다운로드 시간: 기업당 약 5-10분 소요 (API 제한으로 인해)
- 전체 다운로드: 약 30분 ~ 1시간 소요
- 네트워크 연결 필요
- 충분한 디스크 공간 필요 (~1GB)
- SEC_USER_AGENT는 SEC 정책에 따라 실제 이름과 이메일을 사용해야 함

## 📝 History
