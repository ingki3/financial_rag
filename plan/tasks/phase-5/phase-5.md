# Phase 5: Static Graph 생성

## 📋 개요

Phase 5는 추출된 데이터에서 Static Graph를 생성하는 단계입니다. Static Graph는 Company, Product, Person 노드와 이들 간의 관계를 포함합니다.

## 🎯 목표

- Company Node 생성
- Product Node 생성 (정규화 포함)
- Person Node 생성 (정규화 포함)
- Static Link 생성 (MAKE, HAS_RELATION)

## 📥 입력

- `data/extracted/{ticker}/{filing_type}/` 폴더의 JSON 파일

## 📤 출력

- `data/graph/{TICKER}_static_graph.json`
- 구조: `{nodes: {...}, links: [...]}`

## 🔗 관련 문서

- `phase-5-1.md`: Company Node 생성 상세
- `phase-5-2.md`: Product Node 생성 상세
- `phase-5-3.md`: Person Node 생성 상세
- `phase-5-4.md`: Static Link 생성 상세
- `phase-5-5.md`: 생성 스크립트 상세

## 📝 History

