# Implementation Plan (구현 계획)

## 📊 데이터 구조 및 온톨로지

### 데이터베이스 구조
- **DB 타입**: FalkorDB (Graph Database)
- **연결 정보**: 
  - Host: localhost (환경변수 `FALKORDB_HOST`)
  - Port: 6379 (환경변수 `FALKORDB_PORT`)
  - Graph Name: `financial_kg`
- **인덱스**: 
  - Node 타입별 `id` 인덱스
  - Node 타입별 `ticker` 인덱스

### 그래프 온톨로지

#### Node 타입
- **Static Node** (Phase 5에서 생성):
  - `Company`: 기업 정보 (ID: `{ticker}`)
  - `Product`: 제품/서비스 (ID: `product_{ticker}_{normalized_name}`)
  - `Person`: 인물 (ID: `person_{ticker}_{normalized_name}`)
- **Dynamic Node** (Phase 6에서 생성):
  - `Document`: SEC 공시 문서 (ID: `doc_{ticker}_{filing_type}_{accession_number}`)
  - `Section`: 파싱된 섹션 (ID: `section_{ticker}_{filing_type}_{year}_{section_name}`)
  - `Risk`: 위험 요소 (ID: `risk_{ticker}_{normalized_entity}_{year}`)
  - `Opportunity`: 기회 요소 (ID: `opp_{ticker}_{normalized_entity}_{year}`)
  - `Event`: 주요 이벤트 (ID: `event_{ticker}_{normalized_entity}_{year}`)
  - `Technology`: 기술 관련 정보 (ID: `tech_{ticker}_{normalized_entity}_{year}`)

#### Link 타입
- **Static Links** (Phase 5):
  - `MAKE`: Company → Product
  - `HAS_RELATION`: Company → Person (role 속성 포함)
- **Dynamic Links** (Phase 6):
  - `IS_INCLUDED`: Section → Document
  - `IS_EXTRACTED_FROM`: Risk/Opportunity/Event/Technology → Section
  - `HAS_RISKS`: Company → Risk
  - `HAS_OPPORTUNITIES`: Company → Opportunity
  - `HAS_EVENTS`: Company → Event
  - `HAS_TECHNOLOGIES`: Company → Technology
  - `IS_MENTIONED_IN`: Product/Person/Company → Risk/Opportunity/Event/Technology (mention_context 속성 포함)

#### Node 스타일
- **Static**: Company, Product, Person (행위의 주체나 대상)
- **Dynamic**: Document, Section, Risk, Opportunity, Event, Technology (정보성 노드)

**상세 스키마 정의**: `docs/5-2-graph-ontology-design.md` 참조

### 데이터 파일 구조
- `data/raw/{ticker}/{filing_type}/`: 원본 다운로드 파일 (HTML/SGML)
- `data/parsed/{ticker}/{filing_type}/`: 파싱된 섹션 데이터 (JSON)
  - 구조: `{metadata: {...}, sections: {...}}`
- `data/extracted/{ticker}/{filing_type}/`: 추출된 엔티티 데이터 (JSON)
  - 구조: `{metadata: {...}, opportunities: [...], risks: [...], events: [...], technologies: [...], mentioned_products: [...], mentioned_persons: [...]}`
- `data/graph/{TICKER}_static_graph.json`: Static Graph 데이터
  - 구조: `{nodes: {Company: [...], Product: [...], Person: [...]}, links: [...]}`
- `data/graph/{TICKER}_dynamic_graph.json`: Dynamic Graph 데이터
  - 구조: `{nodes: {Document: [...], Section: [...], Risk: [...], Opportunity: [...], Event: [...], Technology: [...]}, links: [...]}`
- `data/normalization_maps/{TICKER}_normalization_map.json`: 정규화 맵 데이터
  - 구조: `{metadata: {...}, categories: [...], filtered_terms: [...], normalization_rules: [...]}`

### 데이터 흐름
```
Phase 2: SEC 공시 다운로드
  → data/raw/{ticker}/{filing_type}/ (HTML/SGML)

Phase 3: 공시 파싱
  → data/parsed/{ticker}/{filing_type}/ (JSON: metadata + sections)

Phase 4: Triplet 추출
  → data/extracted/{ticker}/{filing_type}/ (JSON: metadata + entities)

Phase 5: Static Graph 생성
  → data/graph/{TICKER}_static_graph.json (Company, Product, Person)

Phase 6: Dynamic Graph 생성
  → data/graph/{TICKER}_dynamic_graph.json (Document, Section, Risk, Opportunity, Event, Technology)

Phase 7: Graph DB 저장
  → FalkorDB (Cypher 쿼리로 적재)
```

---

## 📅 프로젝트 타임라인

| 단계 | 작업 내용 | 예상 소요 시간 |
|------|----------|---------------|
| Phase 1 | 환경 설정 | 2시간 |
| Phase 2 | SEC 공시 다운로드 | 3시간 |
| Phase 3 | 공시 파싱 및 텍스트 추출 | 3시간 |
| Phase 4 | Knowledge Triplet 추출 | 4시간 |
| Phase 5 | Static Graph 생성 (Company, Product, Person) | 2시간 |
| Phase 6 | Dynamic Graph 생성 (Document, Section, Risk, Opp, Event, Tech + Links + Embedding) | 3시간 |
| Phase 7 | Graph DB 저장 | 3시간 |
| Phase 8 | 질의 응답 시스템 | 3시간 |
| Phase 9 | 테스트 및 검증 | 2시간 |
| **총계** | | **25시간** |

---

## Phase 1: 환경 설정 (2시간)

> 📖 **상세 구현**: `plan/tasks/phase-1/` 폴더의 문서를 참고하세요.
> - `phase-1.md`: Phase 1 전체 개요
> - `phase-1-1.md`: FalkorDB 설치 및 실행 상세
> - `phase-1-2.md`: Python 가상환경 및 의존성 설치 상세
> - `phase-1-3.md`: requirements.txt 생성 상세
> - `phase-1-4.md`: 환경 변수 설정 상세

### 1.1 FalkorDB 설치 및 실행
**목적**: Docker를 통한 FalkorDB 설치 및 실행

**주요 작업**:
- Docker 컨테이너 실행
- 포트 설정 (6379, 3000)
- 컨테이너 상태 확인

**파일**: 없음 (Docker 명령어 실행)

### 1.2 Python 가상환경 및 의존성 설치
**목적**: Python 개발 환경 구축

**주요 작업**:
- 가상환경 생성
- 의존성 설치

**파일**: `requirements.txt`

### 1.3 requirements.txt 생성
**목적**: 프로젝트 의존성 정의

**주요 의존성**:
- Core: graphiti-core[falkordb], sec-edgar-downloader, beautifulsoup4, lxml
- LLM: openai, anthropic
- Utilities: python-dotenv, tqdm, aiohttp
- Development: pytest, pytest-asyncio

**파일**: `requirements.txt`

### 1.4 환경 변수 설정
**목적**: 프로젝트 설정 및 API 키 관리

**주요 환경 변수**:
- SEC_USER_AGENT: SEC EDGAR API 사용자 정보
- FALKORDB_HOST, FALKORDB_PORT: FalkorDB 연결 정보
- OPENAI_API_KEY, ANTHROPIC_API_KEY: LLM API 키
- GRAPHITI_MODEL: Graphiti 모델 설정

**파일**: `.env.example`, `.env`

---

## Phase 2: SEC 공시 다운로드 (3시간)

> 📖 **상세 구현**: `plan/tasks/phase-2/` 폴더의 문서를 참고하세요.
> - `phase-2.md`: Phase 2 전체 개요
> - `phase-2-1.md`: 다운로더 모듈 구현 상세
> - `phase-2-2.md`: 다운로드 스크립트 상세

### 2.1 다운로더 모듈 구현
**목적**: SEC EDGAR API를 통한 공시 자료 다운로드

**주요 기능**:
- 10-K, 10-Q, 8-K 공시 다운로드
- 티커별 다운로드 관리
- 다운로드된 파일 목록 조회

**입력 데이터**: SEC EDGAR API (환경변수: `SEC_USER_AGENT`)

**출력 데이터**: 
- 형식: HTML/SGML 파일
- 위치: `data/raw/{ticker}/{filing_type}/{accession_number}/`
- 구조: 원본 SEC 공시 파일

**파일**: `app/services/download/sec_downloader.py`

### 2.2 다운로드 스크립트
**목적**: 다운로더 모듈을 실행하는 스크립트

**주요 기능**:
- 환경 변수 로드
- 다운로더 초기화
- 전체 다운로드 실행

**파일**: `scripts/01_download_filings.py`

---

## Phase 3: 공시 파싱 및 텍스트 추출 (3시간)

> 📖 **상세 구현**: `plan/tasks/phase-3/` 폴더의 문서를 참고하세요.
> - `phase-3.md`: Phase 3 전체 개요
> - `phase-3-1.md`: 파서 모듈 구현 상세
> - `phase-3-2.md`: 파싱 스크립트 상세

### 3.1 파서 모듈 구현
**목적**: HTML/SGML 형식의 공시 파일에서 주요 섹션 추출

**주요 기능**:
- 10-K, 10-Q, 8-K 공시 유형별 섹션 패턴 정의
- HTML 파싱 및 텍스트 추출
- 섹션별 텍스트 추출

**입력 데이터**:
- 형식: HTML/SGML 파일
- 위치: `data/raw/{ticker}/{filing_type}/`

**출력 데이터**:
- 형식: JSON
- 위치: `data/parsed/{ticker}/{filing_type}/`
- 구조:
  ```json
  {
    "metadata": {
      "ticker": "AAPL",
      "filing_type": "10-K",
      "accession_number": "...",
      "file_path": "...",
      "text_length": 12345
    },
    "sections": {
      "business": "...",
      "risk_factors": "...",
      "mda": "..."
    }
  }
  ```

**파일**: `app/services/processing/filing_parser.py`

### 3.2 파싱 스크립트
**목적**: 파서 모듈을 실행하여 모든 공시 파일 파싱

**주요 기능**:
- 다운로드된 공시 파일 순회
- 파서를 통한 섹션 추출
- JSON 형식으로 저장

**파일**: `scripts/02_parse_filings.py`

---

## Phase 4: Knowledge Triplet 추출 (4시간)

> 📖 **상세 구현**: `plan/tasks/phase-4/` 폴더의 문서를 참고하세요.
> - `phase-4.md`: Phase 4 전체 개요
> - `phase-4-1.md`: 추출기 모듈 구현 상세
> - `phase-4-2.md`: 추출 스크립트 상세

### 4.1 추출기 모듈 구현
**목적**: LLM을 활용한 Knowledge Triplet 추출

**주요 기능**:
- 기회 요소 (Opportunities) 추출
- 리스크 요소 (Risks) 추출
- 주요 이벤트 (Key Events) 추출
- 전략 (Strategies) 추출
- 재무 지표 (Financial Metrics) 추출
- 제품/인물/기업 언급 추출

**입력 데이터**:
- 형식: JSON (파싱된 섹션 데이터)
- 위치: `data/parsed/{ticker}/{filing_type}/`
- 내용: 섹션별 텍스트

**출력 데이터**:
- 형식: JSON
- 위치: `data/extracted/{ticker}/{filing_type}/`
- 구조:
  ```json
  {
    "metadata": {
      "ticker": "AAPL",
      "filing_type": "10-K",
      "accession_number": "...",
      "section": "risk_factors"
    },
    "opportunities": [{"entity": "...", "description": "..."}],
    "risks": [{"entity": "...", "description": "..."}],
    "events": [{"entity": "...", "date": "...", "description": "..."}],
    "technologies": [{"entity": "...", "description": "..."}],
    "mentioned_products": ["iPhone 15", "iPad Pro"],
    "mentioned_persons": ["Tim Cook"],
    "mentioned_companies": ["Samsung"]
  }
  ```

**파일**: `app/services/processing/triplet_extractor.py`

### 4.2 추출 스크립트
**목적**: 추출기 모듈을 실행하여 모든 파싱된 파일에서 Triplet 추출

**주요 기능**:
- 파싱된 파일 순회
- LLM을 통한 Triplet 추출
- JSON 형식으로 저장

**파일**: `scripts/03_extract_triplets.py`

---

## Phase 5: Static Graph 생성 (2시간)

> 📖 **상세 구현**: `plan/tasks/phase-5/` 폴더의 문서를 참고하세요.
> - `phase-5.md`: Phase 5 전체 개요
> - `phase-5-1.md`: Company Node 생성 상세
> - `phase-5-2.md`: Product Node 생성 상세
> - `phase-5-3.md`: Person Node 생성 상세
> - `phase-5-4.md`: Static Link 생성 상세
> - `phase-5-5.md`: 생성 스크립트 상세

### 5.1 데이터 파이프라인 구조
```
Extracted Data
    ↓
1. Static Node 생성 (Company, Product, Person)
    → {TICKER}_static_graph.json
    ↓
2. Dynamic Node 생성 (Risk, Opportunity, Event, Technology, Section, Document)
    → {TICKER}_dynamic_graph.json
    ↓
3. Link 생성 (Static ↔ Static, Dynamic ↔ Dynamic, Static ↔ Dynamic)
    → 각 JSON 파일에 links 배열로 저장
    ↓
4. Graph DB 적재 (Cypher 쿼리 변환)
```

### 5.2 Static Graph 생성 모듈 구현
**파일**: `app/services/processing/graph_generator.py`

**입력 데이터**:
- 형식: JSON (추출된 엔티티 데이터)
- 위치: `data/extracted/{ticker}/{filing_type}/`
- 사용 필드: `mentioned_products`, `mentioned_persons`

**출력 데이터**:
- 형식: JSON
- 위치: `data/graph/{TICKER}_static_graph.json`
- 구조:
  ```json
  {
    "nodes": {
      "Company": [{
        "id": "AAPL",
        "node_type": "Company",
        "ticker": "AAPL",
        "name": "Apple Inc.",
        "sector": "Technology",
        "node_style": "static"
      }],
      "Product": [{
        "id": "product_aapl_iphone_15_pro",
        "node_type": "Product",
        "name": "iPhone 15 Pro",
        "node_style": "static"
      }],
      "Person": [{
        "id": "person_aapl_tim_cook",
        "node_type": "Person",
        "name": "Tim Cook",
        "node_style": "static"
      }]
    },
    "links": [
      {
        "from": "AAPL",
        "to": "product_aapl_iphone_15_pro",
        "relationship_type": "MAKE"
      },
      {
        "from": "AAPL",
        "to": "person_aapl_tim_cook",
        "relationship_type": "HAS_RELATION",
        "role": "CEO"
      }
    ]
  }
  ```

**주요 기능**:
1. **Company Node 생성**: 티커당 1개, ID: `{ticker}`
2. **Product Node 생성**: `mentioned_products`에서 중복 제거, 정규화 적용, ID: `product_{ticker}_{normalized_name}`
3. **Person Node 생성**: `mentioned_persons`에서 중복 제거, 정규화 적용, ID: `person_{ticker}_{normalized_name}`
4. **Static Link 생성**: MAKE (Company → Product), HAS_RELATION (Company → Person)

### 5.3 생성 스크립트
**파일**: `scripts/04_generate_static_graph.py`

**주요 기능**:
- 티커별 Static Graph 생성
- JSON 파일로 저장

---

## Phase 6: Dynamic Graph 생성 (3시간)

> 📖 **상세 구현**: `plan/tasks/phase-6/` 폴더의 문서를 참고하세요.
> - `phase-6.md`: Phase 6 전체 개요
> - `phase-6-1.md`: Dynamic Node 생성 상세
> - `phase-6-2.md`: Dynamic Link 생성 상세
> - `phase-6-3.md`: Embedding 생성 상세
> - `phase-6-4.md`: 생성 스크립트 상세

### 6.1 실행 단계 개요

| 단계 | 작업 내용 | 생성되는 노드/링크 |
|------|----------|------------------|
| **6.1** | Dynamic Node 생성 | Document, Section, Risk, Opportunity, Event, Technology |
| **6.2** | IS_INCLUDED Link 생성 | Section → Document |
| **6.3** | IS_EXTRACTED_FROM Link 생성 | Risk/Opp/Event/Tech → Section |
| **6.4** | HAS_* Link 생성 | Company → Risk/Opp/Event/Tech |
| **6.5** | IS_MENTIONED_IN Link 생성 | Product/Person/Company → Dynamic Node |
| **6.6** | Embedding 생성 | 노드에 `description_embedding` 추가 (768차원) |

### 6.2 Dynamic Node 생성
**파일**: `app/services/processing/dynamic_graph_generator.py`

**입력 데이터**:
- 형식: JSON (추출된 엔티티 데이터, 파싱된 섹션 데이터)
- 위치: `data/extracted/{ticker}/{filing_type}/`, `data/parsed/{ticker}/{filing_type}/`
- 사용 필드: `opportunities`, `risks`, `events`, `technologies`, `sections`, `metadata`

**출력 데이터**:
- 형식: JSON
- 위치: `data/graph/{TICKER}_dynamic_graph.json`
- 구조:
  ```json
  {
    "nodes": {
      "Document": [{
        "id": "doc_aapl_10-k_0000320193-24-000077",
        "node_type": "Document",
        "ticker": "AAPL",
        "filing_type": "10-K",
        "accession_number": "0000320193-24-000077",
        "year": 2024,
        "node_style": "dynamic"
      }],
      "Section": [{
        "id": "section_aapl_10-k_2024_risk_factors",
        "node_type": "Section",
        "section_name": "risk_factors",
        "ticker": "AAPL",
        "year": 2024,
        "node_style": "dynamic"
      }],
      "Risk": [{
        "id": "risk_aapl_intense_competition_2024",
        "node_type": "Risk",
        "entity": "Intense Competition",
        "description": "...",
        "ticker": "AAPL",
        "node_style": "dynamic",
        "description_embedding": [0.123, 0.456, ...]
      }]
    },
    "links": [...]
  }
  ```

**주요 기능**:
1. **Document Node 생성**: ID: `doc_{ticker}_{filing_type_lower}_{accession_number}`
2. **Section Node 생성**: ID: `section_{ticker}_{filing_type_lower}_{year}_{section_name}`
3. **Risk/Opportunity/Event/Technology Node 생성**: 각각 고유 ID 패턴 사용
4. **Embedding 추가**: Risk, Opportunity, Event, Technology 노드에 `description_embedding` 필드 추가 (768차원)

### 6.3 Dynamic Link 생성
**주요 링크 타입**:
- IS_INCLUDED: Section → Document
- IS_EXTRACTED_FROM: Risk/Opp/Event/Tech → Section
- HAS_RISKS, HAS_OPPORTUNITIES, HAS_EVENTS, HAS_TECHNOLOGIES: Company → Dynamic Node
- IS_MENTIONED_IN: Product/Person/Company → Dynamic Node

### 6.4 Embedding 생성
**파일**: `app/services/processing/embedding_generator.py`

**설정**:
- 모델: Gemini `text-embedding-004` (768차원)
- 배치 처리: 100개/배치

### 6.5 생성 스크립트
**파일**: `scripts/05_generate_dynamic_graph.py`

**주요 기능**:
- 티커별 Dynamic Graph 생성
- Embedding 생성 옵션 지원

---

## Phase 7: Graph DB 저장 (3시간)

> 📖 **상세 구현**: `plan/tasks/phase-7/` 폴더의 문서를 참고하세요.
> - `phase-7.md`: Phase 7 전체 개요
> - `phase-7-1.md`: Graph Loader 모듈 구현 상세
> - `phase-7-2.md`: Cypher 쿼리 패턴 상세
> - `phase-7-3.md`: 저장 스크립트 상세

### 7.1 개요
Phase 5~6에서 생성된 Static/Dynamic Graph JSON 파일을 FalkorDB에 적재합니다.

**입력 데이터**:
- 형식: JSON
- 위치: 
  - `data/graph/{TICKER}_static_graph.json` - Company, Product, Person 노드 및 MAKE, HAS_RELATION 링크
  - `data/graph/{TICKER}_dynamic_graph.json` - Document, Section, Risk, Opportunity, Event, Technology 노드 및 모든 Dynamic 링크

**출력 데이터**:
- 형식: FalkorDB Graph Database
- 연결 정보:
  - Host: localhost (환경변수 `FALKORDB_HOST`)
  - Port: 6379 (환경변수 `FALKORDB_PORT`)
  - Graph Name: `financial_kg`
- 저장 내용: 모든 Node와 Link가 Cypher 쿼리로 적재됨

### 7.2 Graph Loader 모듈
**파일**: `app/services/graph/graph_loader.py`

**주요 기능**:
- 인덱스 및 제약조건 생성
- 노드 생성 (MERGE 사용하여 중복 방지)
- 링크 생성 (MERGE 사용하여 중복 방지)
- Static/Dynamic Graph 적재
- 통계 조회

### 7.3 Cypher 쿼리 패턴
**노드 생성**: MERGE를 사용하여 중복 방지
**링크 생성**: MATCH + MERGE를 사용하여 관계 생성

### 7.4 저장 스크립트
**파일**: `scripts/06_load_graph_to_db.py`

**주요 기능**:
- Static/Dynamic Graph JSON 파일 로드
- FalkorDB에 적재
- 검증 옵션 지원

### 7.6 예상 적재량

| 노드 타입 | 예상 수 |
|----------|--------|
| Company | 7 |
| Product | ~210 |
| Person | ~27 |
| Document | ~134 |
| Section | ~90 |
| Risk | ~375 |
| Opportunity | ~348 |
| Event | ~464 |
| Technology | ~382 |
| **총 노드** | **~2,037** |

| 링크 타입 | 예상 수 |
|----------|--------|
| MAKE | ~210 |
| HAS_RELATION | ~27 |
| IS_INCLUDED | ~186 |
| IS_EXTRACTED_FROM | ~1,650 |
| HAS_RISKS | ~395 |
| HAS_OPPORTUNITIES | ~356 |
| HAS_EVENTS | ~471 |
| HAS_TECHNOLOGIES | ~428 |
| IS_MENTIONED_IN | ~1,552 |
| **총 링크** | **~5,275** |

---

## Phase 8: 질의 응답 시스템 (3시간)

> 📖 **상세 구현**: `plan/tasks/phase-8/` 폴더의 문서를 참고하세요.
> - `phase-8.md`: Phase 8 전체 개요
> - `phase-8-1.md`: Intent 추출 구현 상세
> - `phase-8-2.md`: Cypher 쿼리 빌더 구현 상세
> - `phase-8-3.md`: Vector 검색 구현 상세
> - `phase-8-4.md`: 답변 생성 구현 상세
> - `phase-8-5.md`: API 엔드포인트 구현 상세

### 8.1 질의 엔진 구현
**목적**: 자연어 질의를 처리하여 그래프 기반 답변 생성

**입력 데이터**:
- 형식: 자연어 질의 (문자열)
- 예시: "애플의 기회 요소를 알려줘"

**출력 데이터**:
- 형식: 구조화된 답변 (스트리밍)
- 구조:
  ```json
  {
    "answer": "...",
    "sources": [
      {
        "document_id": "doc_aapl_10-k_...",
        "section_id": "section_aapl_10-k_2024_business",
        "entity": "..."
      }
    ]
  }
  ```

**주요 기능**:
- Intent 추출 (Gemini Structured Output)
- Cypher 쿼리 빌더 (FalkorDB 그래프 쿼리)
- Vector 검색 (하이브리드: Graph + Embedding)
- 답변 생성 (스트리밍)

**데이터 소스**:
- FalkorDB 그래프 데이터 (Node, Link)
- Embedding 벡터 (의미 기반 검색)

**파일**: `app/services/query/query_engine.py`

### 8.2 API 엔드포인트
**파일**: `app/api/routes/answer.py`

**주요 기능**:
- `/answer` 엔드포인트 (스트리밍 답변)
- FastAPI 기반 REST API
- Server-Sent Events (SSE) 지원

---

## Phase 9: 테스트 및 검증 (2시간)

> 📖 **상세 구현**: `plan/tasks/phase-9/` 폴더의 문서를 참고하세요.
> - `phase-9.md`: Phase 9 전체 개요
> - `phase-9-1.md`: 단위 테스트 상세
> - `phase-9-2.md`: 통합 테스트 상세
> - `phase-9-3.md`: 검증 시나리오 상세

### 9.1 단위 테스트
**목적**: 각 모듈의 개별 기능 검증

**테스트 파일**:
- `tests/test_downloader.py`: 다운로더 모듈 테스트
- `tests/test_parser.py`: 파서 모듈 테스트
- `tests/test_extractor.py`: 추출기 모듈 테스트

### 9.2 통합 테스트
**목적**: 전체 시스템 통합 검증

**테스트 파일**: `tests/test_integration.py`

### 9.3 검증 시나리오
**주요 테스트 케이스**:
- TC-01: "애플의 기회 요소를 알려줘"
- TC-02: "테슬라의 리스크는?"
- TC-03: "구글의 AI 전략"
- TC-04: "엔비디아 vs AMD 비교"

---

## 🚀 실행 순서

```bash
# 1. 환경 설정
cp .env.example .env
# .env 파일 수정 (API 키 설정)

# 2. FalkorDB 시작
docker run -d --name falkordb -p 6379:6379 -p 3000:3000 falkordb/falkordb:latest

# 3. 의존성 설치
pip install -r requirements.txt

# 4. 공시 다운로드 (10-K, 10-Q, 8-K)
python scripts/01_download_filings.py
# 예상 소요 시간: 30분 ~ 1시간 (API 제한으로 인해)
# 저장 위치: ./data/raw/{ticker}/{filing_type}/

# 5. 파싱
python scripts/02_parse_filings.py
# 저장 위치: ./data/parsed/{ticker}/{filing_type}/

# 6. 트리플렛 추출
python scripts/03_extract_triplets.py
# 저장 위치: ./data/extracted/{ticker}/{filing_type}/

# 7. Static Graph 생성 (Company, Product, Person 노드)
python scripts/05_generate_static_graph.py --ticker AAPL TSLA NVDA
# 저장 위치: ./data/graph/{TICKER}_static_graph.json

# 8. Dynamic Graph 생성 (Document, Section, Risk, Opp, Event, Tech 노드 + 링크)
python scripts/06_generate_dynamic_graph.py --ticker AAPL TSLA NVDA
# 옵션: --with-embedding (Embedding 생성 포함)
# 저장 위치: ./data/graph/{TICKER}_dynamic_graph.json

# 9. Graph DB 적재
python scripts/07_populate_graph.py
# FalkorDB에 노드 및 링크 적재

# 10. 질의 시스템 실행
python scripts/08_query_interface.py
```

---

## 📊 마일스톤 체크리스트

- [x] Phase 1: 환경 설정 완료 ✅
  - [x] FalkorDB Docker 컨테이너 실행
  - [x] Python 환경 및 의존성 설치
  - [x] 환경 변수 설정
  
- [x] Phase 2: 공시 다운로드 완료 ✅
  - [x] 7개 기업 10-K, 10-Q, 8-K 다운로드
  - [x] 폴더 구조 확인 (data/raw/{ticker}/{filing_type}/)
  - [x] API 엔드포인트 구현 (`/download`)
  
- [x] Phase 3: 파싱 완료 ✅
  - [x] HTML → 텍스트 변환
  - [x] 섹션별 추출
  - [x] 저장 확인 (data/parsed/{ticker}/{filing_type}/)
  
- [x] Phase 4: 트리플렛 추출 완료 ✅
  - [x] LLM 연동 (Gemini)
  - [x] Risk/Opportunity/Event/Technology 추출
  - [x] mentioned_products/persons/companies 추출
  - [x] Extracted Data 저장 확인 (data/extracted/{ticker}/{filing_type}/)
  - [x] 프롬프트 YAML 분리 (`app/prompts/triplet_extractor.yaml`)
  
- [x] Phase 5: Static Graph 생성 완료 ✅
  - [x] Company Node 생성
  - [x] Product Node 생성 (고유명사, 중복 제거)
  - [x] Person Node 생성 (중복 제거)
  - [x] MAKE Link 생성 (Company → Product)
  - [x] HAS_RELATION Link 생성 (Company → Person)
  - [x] 저장 확인 ({TICKER}_static_graph.json)
  
- [x] Phase 6: Dynamic Graph 생성 완료 ✅
  - [x] Document Node 생성
  - [x] Section Node 생성
  - [x] Risk/Opportunity/Event/Technology Node 생성
  - [x] IS_INCLUDED Link 생성 (Section → Document)
  - [x] IS_EXTRACTED_FROM Link 생성 (Dynamic → Section)
  - [x] HAS_RISKS/HAS_OPPORTUNITIES/HAS_EVENTS/HAS_TECHNOLOGIES Link 생성
  - [x] IS_MENTIONED_IN Link 생성 (Static → Dynamic)
  - [x] Embedding 생성 (Gemini text-embedding-004)
  - [x] 저장 확인 ({TICKER}_dynamic_graph.json)
  
- [x] Phase 7: Graph DB 저장 완료 ✅
  - [x] FalkorDB 연동
  - [x] Node/Link Data 로드 및 Cypher 쿼리 생성
  - [x] 데이터 저장 확인
  - [x] 중복 방지 메커니즘 구현 (`DuplicateChecker`)
  
- [x] Phase 8: 질의 시스템 완료 ✅
  - [x] Graph 검색 기능 구현
  - [x] Vector 검색 기능 구현 (하이브리드)
  - [x] 답변 생성 구현
  - [x] Intent 추출 구현 (Gemini Structured Output)
  - [x] Cypher 쿼리 빌더 구현
  - [x] 이름 표준화 시스템 구현
  - [x] 프롬프트 YAML 분리 (`app/prompts/answer_generator.yaml`, `app/prompts/intent_extractor.yaml`)
  
- [x] Phase 9: API 구현 완료 ✅
  - [x] FastAPI 기반 REST API 구현
  - [x] `/answer` 엔드포인트 (스트리밍 답변)
  - [x] `/download` 엔드포인트 (공시 다운로드)
  - [x] `/process` 엔드포인트 (문서 처리 및 Graph DB 적재)
  - [x] Streamlit 클라이언트 구현
  - [x] 의존성 관리 (FastAPI Dependency Injection)
  - [x] API 스키마 정의 (`app/schemas/api_schemas.py`)

---

## ⚠️ 주의사항

1. **SEC API 제한**: 초당 10건 이하 요청 유지
2. **LLM 비용**: GPT-4 사용 시 토큰 비용 발생 (예상: $50-100, 공시 수 증가로 인해)
3. **저장 공간**: 
   - 10-K: 7 × 3 = 21건, 약 210MB
   - 10-Q: 7 × 12 = 84건, 약 420MB
   - 8-K: 7 × 20 = 140건, 약 280MB
   - 총 예상: ~1GB
4. **메모리**: Graphiti 처리 시 최소 8GB RAM 권장

