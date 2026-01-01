# Phase 6: Dynamic Graph 생성

## 📋 개요

Phase 6는 추출된 데이터에서 Dynamic Graph를 생성하는 단계입니다. Dynamic Graph는 Document, Section, Risk, Opportunity, Event, Technology 노드와 이들 간의 관계를 포함합니다.

## 🎯 목표

- Dynamic Node 생성 (Document, Section, Risk, Opportunity, Event, Technology)
- Dynamic Link 생성 (IS_INCLUDED, IS_EXTRACTED_FROM, HAS_*, IS_MENTIONED_IN)
- Embedding 생성 (의미 기반 검색 지원)

## 📥 입력 데이터 상세

### 데이터 소스
- **파일 경로**: 
  - `data/extracted/{ticker}/{filing_type}/` 폴더의 JSON 파일
  - `data/graph/{TICKER}_static_graph.json`
- **데이터 형식**: JSON

### 데이터 구조
- **Extracted JSON**: Phase 4에서 추출된 Knowledge Triplet 데이터
- **Static Graph JSON**: Phase 5에서 생성된 Static Graph

## 📤 출력 데이터 상세

### 출력 형식
- **파일 경로**: `data/graph/{TICKER}_dynamic_graph.json`
- **데이터 형식**: JSON

### 데이터 구조
```json
{
  "ticker": "AAPL",
  "generated_at": "2024-01-01T00:00:00Z",
  "nodes": {
    "Document": [...],
    "Section": [...],
    "Risk": [...],
    "Opportunity": [...],
    "Event": [...],
    "Technology": [...]
  },
  "links": [
    {
      "from": "doc_aapl_10k_2024",
      "to": "section_aapl_10k_2024_item1a",
      "link_type": "IS_INCLUDED",
      "link_style": "dynamic"
    }
  ]
}
```

## 🔄 주요 작업 단계

1. **Dynamic Node 생성** (Phase 6.1)
   - Document 노드 생성
   - Section 노드 생성
   - Risk/Opportunity/Event/Technology 노드 생성

2. **Dynamic Link 생성** (Phase 6.2)
   - IS_INCLUDED 링크 (Document → Section)
   - IS_EXTRACTED_FROM 링크 (Entity → Section)
   - HAS_* 링크 (Document → Entity)
   - IS_MENTIONED_IN 링크 (Static Node → Dynamic Node)

3. **Embedding 생성** (Phase 6.3)
   - Risk/Opportunity/Event/Technology 노드의 description에 대한 embedding 생성

4. **JSON 파일 저장** (Phase 6.4)
   - `data/graph/{TICKER}_dynamic_graph.json` 파일로 저장

## 📊 사용하는 데이터 구조 및 스키마

### Node 구조
- **Document Node**: 공시 문서 노드
- **Section Node**: 공시 섹션 노드
- **Risk/Opportunity/Event/Technology Node**: 동적 엔티티 노드

### Link 구조
- **IS_INCLUDED**: Document → Section
- **IS_EXTRACTED_FROM**: Entity → Section
- **HAS_***: Document → Entity
- **IS_MENTIONED_IN**: Static Node → Dynamic Node

## 🔗 Phase 간 의존성

### 이전 Phase 의존성
- **Phase 4**: Knowledge Triplet 추출 완료 필요
  - `data/extracted/{ticker}/{filing_type}/` 폴더에 JSON 파일 존재
- **Phase 5**: Static Graph 생성 완료 필요
  - `data/graph/{TICKER}_static_graph.json` 파일 존재

### 다음 Phase로의 데이터 전달
- **Phase 7 (Graph DB 저장)**:
  - `data/graph/{TICKER}_dynamic_graph.json` 파일 전달

## 🔗 관련 문서

- `phase-6-1.md`: Dynamic Node 생성 상세
- `phase-6-2.md`: Dynamic Link 생성 상세
- `phase-6-3.md`: Embedding 생성 상세
- `phase-6-4.md`: 생성 스크립트 상세

## 📝 History

