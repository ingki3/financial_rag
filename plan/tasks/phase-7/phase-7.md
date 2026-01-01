# Phase 7: Graph DB 저장

## 📋 개요

Phase 7는 생성된 Static/Dynamic Graph JSON 파일을 FalkorDB에 적재하는 단계입니다.

## 🎯 목표

- FalkorDB 연결
- 인덱스 및 제약조건 생성
- 노드 및 링크 적재
- 중복 방지 메커니즘

## 📥 입력

- `data/graph/{TICKER}_static_graph.json`
- `data/graph/{TICKER}_dynamic_graph.json`

## 📤 출력

- FalkorDB에 저장된 노드 및 링크
- 적재 통계

## 🔗 관련 문서

- `phase-7-1.md`: Graph Loader 모듈 구현 상세
- `phase-7-2.md`: Cypher 쿼리 패턴 상세
- `phase-7-3.md`: 저장 스크립트 상세

## 📝 History

