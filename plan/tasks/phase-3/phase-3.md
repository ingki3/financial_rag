# Phase 3: 공시 파싱 및 텍스트 추출

## 📋 개요

Phase 3는 다운로드된 HTML/SGML 형식의 공시 파일에서 주요 섹션을 추출하고 텍스트로 변환하는 단계입니다.

## 🎯 목표

- HTML/SGML 파일 파싱
- 공시 유형별 주요 섹션 추출
- 텍스트 변환 및 JSON 형식으로 저장

## 📥 입력 데이터 상세

### 데이터 소스
- **파일 경로**: `data/raw/{ticker}/{filing_type}/` 폴더의 HTML/SGML 파일
- **데이터 형식**: HTML, SGML

### 데이터 구조
- **HTML/SGML 파일**: SEC EDGAR에서 다운로드한 원본 공시 파일
- **파일명 형식**: `{accession_number}.{extension}`

## 📤 출력 데이터 상세

### 출력 형식
- **파일 경로**: `data/parsed/{ticker}/{filing_type}/` 폴더의 JSON 파일
- **데이터 형식**: JSON

### 데이터 구조
```json
{
  "ticker": "AAPL",
  "filing_type": "10-K",
  "accession_number": "0000320193-24-000001",
  "filing_date": "2024-11-01",
  "year": 2024,
  "sections": {
    "Item 1": {
      "title": "Business",
      "content": "..."
    },
    "Item 1A": {
      "title": "Risk Factors",
      "content": "..."
    },
    "Item 7": {
      "title": "Management's Discussion and Analysis",
      "content": "..."
    }
  },
  "metadata": {
    "company_name": "Apple Inc.",
    "parsed_at": "2024-01-01T00:00:00Z"
  }
}
```

## 🔄 주요 작업 단계

1. **파서 모듈 구현** (Phase 3.1)
   - HTML/SGML 파서 구현
   - 공시 유형별 섹션 추출 로직 구현

2. **파싱 스크립트 실행** (Phase 3.2)
   - 모든 다운로드된 파일 파싱
   - JSON 형식으로 저장

## 📊 사용하는 데이터 구조 및 스키마

- **파싱된 JSON 구조**: 
  - `ticker`: 티커 심볼
  - `filing_type`: 공시 유형 (10-K, 10-Q, 8-K)
  - `sections`: 섹션별 텍스트 내용
  - `metadata`: 메타데이터 정보

## 🔗 Phase 간 의존성

### 이전 Phase 의존성
- **Phase 2**: SEC 공시 다운로드 완료 필요
  - `data/raw/{ticker}/{filing_type}/` 폴더에 파일 존재

### 다음 Phase로의 데이터 전달
- **Phase 4 (Knowledge Triplet 추출)**:
  - `data/parsed/{ticker}/{filing_type}/` 폴더의 JSON 파일 전달
  - 파싱된 섹션 텍스트를 LLM에 입력

## 🔗 관련 문서

- `phase-3-1.md`: 파서 모듈 구현 상세
- `phase-3-2.md`: 파싱 스크립트 상세

## 📝 History

