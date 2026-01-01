# Phase 2.2: 다운로드 스크립트

## 📋 개요

다운로더 모듈을 실행하여 모든 공시 자료를 다운로드하는 스크립트를 구현합니다.

## 🎯 목표

- 환경 변수 로드
- 다운로더 초기화
- 전체 다운로드 실행
- 진행 상황 로깅

## 📝 상세 구현

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

### 출력 형식

- 진행 상황: 로깅을 통한 실시간 출력
- 결과 요약: 다운로드된 파일 수 및 저장 위치
- 에러 처리: 실패한 다운로드에 대한 로그

## 📁 파일 위치

**파일**: `scripts/01_download_filings.py`

## ⚠️ 주의사항

- 다운로드 시간: 기업당 약 5-10분 소요 (API 제한으로 인해)
- 전체 다운로드: 약 30분 ~ 1시간 소요
- 네트워크 연결 필요
- 충분한 디스크 공간 필요 (~1GB)

## 📝 History

