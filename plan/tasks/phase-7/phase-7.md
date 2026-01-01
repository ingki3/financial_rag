# Phase 7: Graph DB 저장

## 📋 개요

Phase 7는 생성된 Static/Dynamic Graph JSON 파일을 FalkorDB에 적재하는 단계입니다.

## 🎯 목표

- FalkorDB 연결
- 인덱스 및 제약조건 생성
- 노드 및 링크 적재
- 중복 방지 메커니즘

## 📥 입력 데이터 상세

### 데이터 소스
- **파일 경로**: 
  - `data/graph/{TICKER}_static_graph.json`
  - `data/graph/{TICKER}_dynamic_graph.json`
- **데이터 형식**: JSON

### 데이터 구조
- **Static Graph JSON**: Phase 5에서 생성된 Static Graph
- **Dynamic Graph JSON**: Phase 6에서 생성된 Dynamic Graph

## 📤 출력 데이터 상세

### 출력 형식
- **FalkorDB**: 그래프 데이터베이스에 저장된 노드 및 링크
- **통계**: 적재 통계 딕셔너리

### 데이터 구조
- **FalkorDB 노드**: Cypher 쿼리로 생성된 노드
- **FalkorDB 링크**: Cypher 쿼리로 생성된 관계
- **적재 통계**:
  ```python
  {
      "nodes_created": int,
      "links_created": int,
      "errors": int,
      "embeddings_stored": int
  }
  ```

## 🔄 주요 작업 단계

1. **Graph Loader 모듈 구현** (Phase 7.1)
   - FalkorDB 연결 관리
   - 인덱스 생성
   - 노드/링크 적재 로직 구현

2. **Cypher 쿼리 패턴 정의** (Phase 7.2)
   - MERGE 쿼리 패턴 정의
   - 중복 방지 메커니즘

3. **저장 스크립트 실행** (Phase 7.3)
   - Static/Dynamic Graph 파일 로드
   - FalkorDB에 적재
   - 검증 수행

## 📊 사용하는 데이터 구조 및 스키마

- **FalkorDB 노드 라벨**: Company, Product, Person, Technology, Document, Section, Risk, Opportunity, Event
- **FalkorDB 관계 타입**: MAKE, HAS_RELATION, USES, IS_INCLUDED, IS_EXTRACTED_FROM, HAS_*, IS_MENTIONED_IN
- **인덱스**: 노드 타입별 id 인덱스, ticker 인덱스

## 🔗 Phase 간 의존성

### 이전 Phase 의존성
- **Phase 5**: Static Graph 생성 완료 필요
  - `data/graph/{TICKER}_static_graph.json` 파일 존재
- **Phase 6**: Dynamic Graph 생성 완료 필요
  - `data/graph/{TICKER}_dynamic_graph.json` 파일 존재
- **Phase 1**: FalkorDB 실행 필요
  - Docker 컨테이너 실행 중

### 다음 Phase로의 데이터 전달
- **Phase 8 (질의 응답 시스템)**:
  - FalkorDB에 저장된 그래프 데이터 활용
  - Cypher 쿼리 및 Vector 검색 수행

## 🔗 관련 문서

- `phase-7-1.md`: Graph Loader 모듈 구현 상세
- `phase-7-2.md`: Cypher 쿼리 패턴 상세
- `phase-7-3.md`: 저장 스크립트 상세

## 📝 History

