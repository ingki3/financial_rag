# Phase 2: SEC 공시 다운로드

## 📋 개요

Phase 2는 SEC EDGAR API를 통해 7개 테크 기업의 공시 자료(10-K, 10-Q, 8-K)를 다운로드하는 단계입니다.

## 🎯 목표

- 7개 기업의 최근 3년간 공시 자료 다운로드
- 10-K (연간 보고서): 최근 3년
- 10-Q (분기 보고서): 최근 12분기 (3년)
- 8-K (수시 공시): 최근 20건
- 체계적인 폴더 구조로 저장

## 📥 입력 데이터 상세

### 데이터 소스
- **SEC EDGAR API**: https://www.sec.gov/edgar/sec-api-documentation
- **환경 변수**: `SEC_USER_AGENT` (SEC API 접근을 위한 User-Agent)

### 데이터 형식
- **API 응답**: JSON (메타데이터), HTML/SGML (공시 파일)

### 데이터 구조
- **API 메타데이터**:
  ```json
  {
    "cik": "0000320193",
    "entityType": "operating",
    "sic": "3571",
    "sicDescription": "Electronic Computers",
    "ticker": "AAPL",
    "name": "Apple Inc."
  }
  ```
- **공시 파일**: HTML 또는 SGML 형식

## 📤 출력 데이터 상세

### 출력 형식
- **파일 경로**: `data/raw/{ticker}/{filing_type}/` 폴더 구조
- **데이터 형식**: HTML, SGML

### 데이터 구조
- **폴더 구조**:
  ```
  data/raw/
    {ticker}/
      10-K/
        {accession_number}.html
        {accession_number}.txt
      10-Q/
        ...
      8-K/
        ...
  ```
- **파일명 형식**: `{accession_number}.{extension}`

## 🔄 주요 작업 단계

1. **다운로더 모듈 구현** (Phase 2.1)
   - SEC EDGAR API 클라이언트 구현
   - 파일 다운로드 로직 구현

2. **다운로드 스크립트 실행** (Phase 2.2)
   - 7개 기업의 공시 자료 다운로드
   - 10-K: 최근 3년
   - 10-Q: 최근 12분기 (3년)
   - 8-K: 최근 20건

## 📊 사용하는 데이터 구조 및 스키마

- **SEC EDGAR API 응답**: JSON 형식의 메타데이터
- **공시 파일**: HTML/SGML 형식의 원본 문서

## 🔗 Phase 간 의존성

### 이전 Phase 의존성
- **Phase 1**: 환경 설정 완료 필요
  - Python 환경 준비
  - 환경 변수 설정

### 다음 Phase로의 데이터 전달
- **Phase 3 (공시 파싱 및 텍스트 추출)**:
  - `data/raw/{ticker}/{filing_type}/` 폴더의 HTML/SGML 파일 전달

## 🔗 관련 문서

- `phase-2-1.md`: 다운로더 모듈 구현 상세
- `phase-2-2.md`: 다운로드 스크립트 상세

## 📝 History

