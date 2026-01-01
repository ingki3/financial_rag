# Phase 4: Knowledge Triplet 추출

## 📋 개요

Phase 4는 LLM을 활용하여 파싱된 텍스트에서 Knowledge Triplet을 추출하는 단계입니다.

## 🎯 목표

- 기회 요소 (Opportunities) 추출
- 리스크 요소 (Risks) 추출
- 주요 이벤트 (Key Events) 추출
- 전략 (Strategies) 추출
- 재무 지표 (Financial Metrics) 추출
- 제품/인물/기업 언급 추출

## 📥 입력 데이터 상세

### 데이터 소스
- **파일 경로**: `data/parsed/{ticker}/{filing_type}/` 폴더의 JSON 파일
- **데이터 형식**: JSON

### 데이터 구조
```json
{
  "ticker": "AAPL",
  "filing_type": "10-K",
  "sections": {
    "Item 1A": {
      "title": "Risk Factors",
      "content": "..."
    }
  }
}
```

## 📤 출력 데이터 상세

### 출력 형식
- **파일 경로**: `data/extracted/{ticker}/{filing_type}/` 폴더의 JSON 파일
- **데이터 형식**: JSON

### 데이터 구조
```json
{
  "ticker": "AAPL",
  "filing_type": "10-K",
  "year": 2024,
  "accession_number": "0000320193-24-000001",
  "extracted_at": "2024-01-01T00:00:00Z",
  "risks": [
    {
      "entity": "Supply Chain Disruption",
      "description": "...",
      "source_section": "Item 1A",
      "mentioned_products": ["iPhone", "Mac"],
      "mentioned_persons": ["Tim Cook"],
      "mentioned_companies": ["Foxconn"]
    }
  ],
  "opportunities": [...],
  "events": [...],
  "technologies": [...],
  "mentioned_products_global": [...],
  "mentioned_persons": [...],
  "mentioned_technologies": [...]
}
```

## 🔄 주요 작업 단계

1. **추출기 모듈 구현** (Phase 4.1)
   - LLM 기반 추출 로직 구현
   - Structured Output 활용

2. **추출 스크립트 실행** (Phase 4.2)
   - 모든 파싱된 파일에서 Knowledge Triplet 추출
   - JSON 형식으로 저장

## 📊 사용하는 데이터 구조 및 스키마

- **추출된 JSON 구조**:
  - `risks`: 리스크 요소 리스트
  - `opportunities`: 기회 요소 리스트
  - `events`: 주요 이벤트 리스트
  - `technologies`: 기술 언급 리스트
  - `mentioned_products_global`: 전역 제품 언급
  - `mentioned_persons`: 인물 언급
  - `mentioned_technologies`: 기술 언급

## 🔗 Phase 간 의존성

### 이전 Phase 의존성
- **Phase 3**: 공시 파싱 완료 필요
  - `data/parsed/{ticker}/{filing_type}/` 폴더에 JSON 파일 존재

### 다음 Phase로의 데이터 전달
- **Phase 5 (Static Graph 생성)**:
  - `data/extracted/{ticker}/{filing_type}/` 폴더의 JSON 파일 전달
  - `mentioned_products`, `mentioned_persons`, `mentioned_technologies` 필드 활용
- **Phase 6 (Dynamic Graph 생성)**:
  - `risks`, `opportunities`, `events`, `technologies` 필드 활용

## 🔗 관련 문서

- `phase-4-1.md`: 추출기 모듈 구현 상세
- `phase-4-2.md`: 추출 스크립트 상세

## 📝 History

