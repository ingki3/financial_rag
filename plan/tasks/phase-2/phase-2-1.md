# Phase 2.1: 다운로더 모듈 구현

## 📋 개요

SEC EDGAR API를 통해 공시 자료를 다운로드하는 모듈을 구현합니다. `sec-edgar-downloader` 라이브러리를 사용하여 10-K, 10-Q, 8-K 공시를 다운로드하고, 프로젝트의 디렉토리 구조로 정리합니다.

## 🎯 목표

- SEC EDGAR API를 통한 공시 다운로드
- 티커별, 공시 유형별 다운로드 관리
- 다운로드된 파일을 프로젝트 디렉토리 구조로 이동
- 다운로드된 파일 목록 조회

## 📝 상세 구현

### 클래스 구조

```python
class SECFilingDownloader:
    """SEC EDGAR에서 10-K, 10-Q, 8-K 공시 자료를 다운로드하는 클래스"""
    
    TICKERS = ["AAPL", "AMZN", "TSLA", "GOOGL", "MSFT", "META", "NVDA"]
    
    FILING_TYPES: Dict[str, int] = {
        "10-K": 3,   # 연간 보고서: 최근 3년
        "10-Q": 12,  # 분기 보고서: 최근 12분기 (3년)
        "8-K": 20,   # 수시 공시: 최근 20건
    }
```

### 주요 메서드

1. **`__init__`**: 초기화 및 Downloader 설정
2. **`download_filing`**: 특정 티커의 특정 유형 공시 다운로드
3. **`download_all_filings`**: 특정 티커의 모든 유형 공시 다운로드
4. **`download_all`**: 모든 대상 기업의 모든 공시 다운로드
5. **`get_downloaded_files`**: 다운로드된 파일 목록 반환

### 다운로드 프로세스

1. `sec-edgar-downloader`를 사용하여 다운로드
2. 기본 저장 위치: `sec-edgar-filings/{ticker}/{filing_type}/`
3. 프로젝트 디렉토리로 이동: `data/raw/{ticker}/{filing_type}/`
4. 각 공시는 accession number 폴더로 저장

### 에러 처리

- 다운로드 실패 시 로깅 및 0 반환
- 파일 이동 실패 시 예외 처리
- API 속도 제한 준수 (초당 10건 이하)

## 📁 파일 위치

**파일**: `app/services/download/sec_downloader.py`

## ⚠️ 주의사항

- SEC EDGAR API 속도 제한 준수 (초당 10건 이하)
- User-Agent는 SEC 정책에 따라 실제 정보 사용
- 다운로드 중 네트워크 오류 처리 필요

## 📝 History

