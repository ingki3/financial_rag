# Phase 6: Dynamic Graph 생성

## 📋 개요

Phase 6는 추출된 데이터에서 Dynamic Graph를 생성하는 단계입니다. Dynamic Graph는 Document, Section, Risk, Opportunity, Event, Technology 노드와 이들 간의 관계를 포함합니다.

## 🎯 목표

- Dynamic Node 생성 (Document, Section, Risk, Opportunity, Event, Technology)
- Dynamic Link 생성 (IS_INCLUDED, IS_EXTRACTED_FROM, HAS_*, IS_MENTIONED_IN)
- Embedding 생성 (의미 기반 검색 지원)

## 📥 입력

- `data/extracted/{ticker}/{filing_type}/` 폴더의 JSON 파일
- `data/graph/{TICKER}_static_graph.json`

## 📤 출력

- `data/graph/{TICKER}_dynamic_graph.json`
- 구조: `{nodes: {...}, links: [...]}`

## 🔗 관련 문서

- `phase-6-1.md`: Dynamic Node 생성 상세
- `phase-6-2.md`: Dynamic Link 생성 상세
- `phase-6-3.md`: Embedding 생성 상세
- `phase-6-4.md`: 생성 스크립트 상세

## 📝 History

