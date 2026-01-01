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
  - `Technology`: 기술 관련 정보 (ID: `tech_{ticker}_{normalized_name}`)
- **Dynamic Node** (Phase 6에서 생성):
  - `Document`: SEC 공시 문서 (ID: `doc_{ticker}_{filing_type}_{accession_number}`)
  - `Section`: 파싱된 섹션 (ID: `section_{ticker}_{filing_type}_{year}_{section_name}`)
  - `Risk`: 위험 요소 (ID: `risk_{ticker}_{normalized_entity}_{year}`)
  - `Opportunity`: 기회 요소 (ID: `opp_{ticker}_{normalized_entity}_{year}`)
  - `Event`: 주요 이벤트 (ID: `event_{ticker}_{normalized_entity}_{year}`)
  - `Technology`: 기술 관련 정보 (Dynamic, ID: `tech_{ticker}_{normalized_entity}_{year}`)

#### Link 타입
- **Static Links** (Phase 5):
  - `MAKE`: Company → Product
  - `HAS_RELATION`: Company → Person (role 속성 포함)
  - `USES`: Company → Technology
- **Dynamic Links** (Phase 6):
  - `IS_INCLUDED`: Section → Document
  - `IS_EXTRACTED_FROM`: Risk/Opportunity/Event/Technology → Section
  - `HAS_RISKS`: Company → Risk
  - `HAS_OPPORTUNITIES`: Company → Opportunity
  - `HAS_EVENTS`: Company → Event
  - `HAS_TECHNOLOGIES`: Company → Technology
  - `IS_MENTIONED_IN`: Product/Person/Company → Risk/Opportunity/Event/Technology (mention_context 속성 포함)

#### Node 스타일
- **Static**: Company, Product, Person, Technology (행위의 주체나 대상, 정규화된 엔티티)
- **Dynamic**: Document, Section, Risk, Opportunity, Event, Technology (정보성 노드, 시간/문서 컨텍스트 포함)

**상세 스키마 정의**: `docs/5-2-graph-ontology-design.md` 참조

### 데이터 파일 구조
- `data/raw/{ticker}/{filing_type}/`: 원본 다운로드 파일 (HTML/SGML)
- `data/parsed/{ticker}/{filing_type}/`: 파싱된 섹션 데이터 (JSON)
  - 구조: `{metadata: {...}, sections: {...}}`
- `data/extracted/{ticker}/{filing_type}/`: 추출된 엔티티 데이터 (JSON)
  - 구조: `{metadata: {...}, opportunities: [...], risks: [...], events: [...], technologies: [...], mentioned_products: [...], mentioned_persons: [...]}`
- `data/graph/{TICKER}_static_graph.json`: Static Graph 데이터
  - 구조: `{nodes: {Company: [...], Product: [...], Person: [...], Technology: [...]}, links: [...]}`
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
  → data/graph/{TICKER}_static_graph.json (Company, Product, Person, Technology)

Phase 6: Dynamic Graph 생성
  → data/graph/{TICKER}_dynamic_graph.json (Document, Section, Risk, Opportunity, Event, Technology)

Phase 7: Graph DB 저장
  → FalkorDB (Cypher 쿼리로 적재)
```

---

## Phase 1: 환경 설정

### Phase 1 개요

**목적**: 프로젝트 개발 및 실행에 필요한 환경을 구축합니다. Docker를 통한 FalkorDB 설치, Python 개발 환경 설정, 프로젝트 의존성 관리, 환경 변수 설정을 포함합니다.

**참고 문서**: `plan/tasks/phase-1/phase-1.md` (입력/출력 데이터, 주요 작업 단계, Phase 간 의존성 등 상세 내용)

### 1.1 FalkorDB 설치 및 실행

**목적**: Docker를 사용하여 FalkorDB 그래프 데이터베이스를 설치하고 실행합니다.

**Description**: FalkorDB는 Redis 기반의 그래프 데이터베이스로, 프로젝트의 모든 그래프 데이터를 저장하는 핵심 인프라입니다.

**참고 문서**: `plan/tasks/phase-1/phase-1-1.md` (파일 경로, 주요 기능, 데이터 구조, Docker 명령어 및 실행 방법 상세)

### 1.2 Python 가상환경 및 의존성 설치

**목적**: Python 개발 환경을 구축하고 프로젝트에 필요한 모든 의존성을 설치합니다.

**Description**: 가상환경을 사용하여 프로젝트별 의존성을 격리하고 관리합니다.

**참고 문서**: `plan/tasks/phase-1/phase-1-2.md` (파일 경로, 주요 기능, 데이터 구조, 가상환경 생성 및 의존성 설치 명령어 상세)

### 1.3 requirements.txt 생성

**목적**: 프로젝트에 필요한 모든 Python 패키지와 버전을 정의합니다.

**Description**: 의존성 관리를 통해 프로젝트의 재현 가능한 환경을 보장합니다.

**참고 문서**: `plan/tasks/phase-1/phase-1-3.md` (파일 경로, 주요 기능, 데이터 구조, requirements.txt 구조 및 작성 방법 상세)

### 1.4 환경 변수 설정

**목적**: 프로젝트 설정 및 외부 API 키를 환경 변수로 관리합니다.

**Description**: 보안을 위해 API 키는 `.env` 파일에 저장하며, `.env.example`을 템플릿으로 제공합니다.

**참고 문서**: `plan/tasks/phase-1/phase-1-4.md` (파일 경로, 주요 기능, 데이터 구조, 환경 변수 설정 방법 및 보안 주의사항 상세)

---

## Phase 2: SEC 공시 다운로드

### Phase 2 개요

**목적**: SEC EDGAR API를 통해 기업의 공시 자료(10-K, 10-Q, 8-K)를 다운로드합니다. 다운로드된 파일은 후속 Phase에서 파싱 및 분석에 사용됩니다.

**참고 문서**: `plan/tasks/phase-2/phase-2.md` (입력/출력 데이터, 주요 작업 단계, Phase 간 의존성 등 상세 내용)

### 2.1 다운로더 모듈 구현

**목적**: SEC EDGAR API를 통한 공시 자료 다운로드를 담당하는 모듈을 구현합니다.

**Description**: `sec-edgar-downloader` 라이브러리를 활용하여 공시 파일을 다운로드하고, 로컬 파일 시스템에 저장합니다.

**참고 문서**: `plan/tasks/phase-2/phase-2-1.md` (파일 경로, 주요 기능, 데이터 구조, 다운로더 모듈 전체 코드 및 사용법 상세)

### 2.2 다운로드 스크립트

**목적**: 다운로더 모듈을 실행하여 모든 티커의 공시 파일을 일괄 다운로드하는 스크립트입니다.

**Description**: 명령줄 인자를 통해 다운로드할 티커와 공시 유형을 지정할 수 있습니다.

**참고 문서**: `plan/tasks/phase-2/phase-2-2.md` (파일 경로, 주요 기능, 데이터 구조, 스크립트 전체 코드, 실행 방법, 명령줄 인자 상세)

---

## Phase 3: 공시 파싱 및 텍스트 추출

### Phase 3 개요

**목적**: HTML/SGML 형식의 SEC 공시 파일에서 주요 섹션을 추출하고 텍스트로 변환합니다. 파싱된 섹션 데이터는 Phase 4에서 Knowledge Triplet 추출에 사용됩니다.

**참고 문서**: `plan/tasks/phase-3/phase-3.md` (입력/출력 데이터, 주요 작업 단계, Phase 간 의존성 등 상세 내용)

### 3.1 파서 모듈 구현

**목적**: HTML/SGML 형식의 공시 파일을 파싱하여 주요 섹션을 추출하는 모듈을 구현합니다.

**Description**: BeautifulSoup과 lxml을 사용하여 HTML을 파싱하고, 공시 유형별 섹션 패턴에 따라 텍스트를 추출합니다.

**참고 문서**: `plan/tasks/phase-3/phase-3-1.md` (파일 경로, 주요 기능, 데이터 구조, 파서 모듈 전체 코드 및 섹션 패턴 정의 상세)

### 3.2 파싱 스크립트

**목적**: 파서 모듈을 실행하여 모든 다운로드된 공시 파일을 파싱하는 스크립트입니다.

**Description**: 명령줄 인자를 통해 파싱할 티커와 공시 유형을 지정할 수 있습니다.

**참고 문서**: `plan/tasks/phase-3/phase-3-2.md` (파일 경로, 주요 기능, 데이터 구조, 스크립트 전체 코드, 실행 방법, 명령줄 인자 상세)

---

## Phase 4: Knowledge Triplet 추출

### Phase 4 개요

**목적**: LLM을 활용하여 파싱된 공시 섹션에서 Knowledge Triplet을 추출합니다. 기회 요소, 리스크 요소, 주요 이벤트, 기술, 그리고 언급된 제품/인물/기업을 구조화된 형태로 추출하여 그래프 생성에 사용합니다.

**참고 문서**: `plan/tasks/phase-4/phase-4.md` (입력/출력 데이터, 주요 작업 단계, Phase 간 의존성 등 상세 내용)

### 4.1 추출기 모듈 구현

**목적**: LLM을 활용하여 파싱된 섹션 텍스트에서 Knowledge Triplet을 추출하는 모듈을 구현합니다.

**Description**: Gemini의 Structured Output 기능을 사용하여 구조화된 데이터를 추출합니다.

**참고 문서**: `plan/tasks/phase-4/phase-4-1.md` (파일 경로, 주요 기능, 데이터 구조, 추출기 모듈 전체 코드, LLM 프롬프트 구조, Pydantic 모델 정의 상세)

### 4.2 추출 스크립트

**목적**: 추출기 모듈을 실행하여 모든 파싱된 파일에서 Knowledge Triplet을 추출하는 스크립트입니다.

**Description**: 명령줄 인자를 통해 추출할 티커와 공시 유형을 지정할 수 있습니다.

**참고 문서**: `plan/tasks/phase-4/phase-4-2.md` (파일 경로, 주요 기능, 데이터 구조, 스크립트 전체 코드, 실행 방법, 명령줄 인자 상세)

---

## Phase 5: Static Graph 생성

### Phase 5 개요

**목적**: 추출된 데이터에서 Static Graph를 생성하는 단계입니다. Static Graph는 Company, Product, Person, Technology 노드와 이들 간의 관계를 포함합니다. 모든 노드 생성 후 정규화 단계를 거쳐 표준 키워드로 통일합니다.

**참고 문서**: `plan/tasks/phase-5/phase-5.md` (입력/출력 데이터, 주요 작업 단계, Phase 간 의존성, 사용하는 데이터 구조 등 상세 내용)

### 5.1 Company Node 생성

**목적**: 각 티커에 대해 Company 노드를 생성합니다.

**Description**: 티커당 1개의 Company 노드를 생성하며, 티커 정보를 기반으로 회사명, 섹터, 설명 등을 포함합니다.

**참고 문서**: `plan/tasks/phase-5/phase-5-1.md` (파일 경로, 주요 기능, 데이터 구조, Company Node 생성 함수 전체 코드 등 상세 내용)

### 5.2 Product Node 생성

**목적**: 추출된 데이터에서 언급된 제품을 수집하여 Product 노드를 생성합니다.

**Description**: `mentioned_products` 필드에서 제품명을 수집하고, 중복을 제거한 후 Product 노드를 생성합니다. 정규화는 Phase 5.5에서 수행됩니다.

**참고 문서**: `plan/tasks/phase-5/phase-5-2.md` (파일 경로, 주요 기능, 데이터 구조, Product Node 생성 함수 전체 코드, 필터링 로직, 분류 규칙 상세)

### 5.3 Person Node 생성

**목적**: 추출된 데이터에서 언급된 인물을 수집하여 Person 노드를 생성합니다.

**Description**: `mentioned_persons` 필드에서 인물명을 수집하고, 중복을 제거한 후 Person 노드를 생성합니다. 정규화는 Phase 5.5에서 수행됩니다.

**참고 문서**: `plan/tasks/phase-5/phase-5-3.md` (파일 경로, 주요 기능, 데이터 구조, Person Node 생성 함수 전체 코드 및 역할 추출 로직 상세)

### 5.4 Technology Node 생성

**목적**: 추출된 데이터에서 언급된 기술을 수집하여 Technology 노드를 생성합니다.

**Description**: `technologies` 또는 `mentioned_technologies` 필드에서 기술 정보를 수집하고, 중복을 제거한 후 Technology 노드를 생성합니다. 정규화는 Phase 5.5에서 수행됩니다.

**참고 문서**: `plan/tasks/phase-5/phase-5-4.md` (파일 경로, 주요 기능, 데이터 구조, Technology Node 생성 함수 전체 코드 상세)

### 5.5 정규화 단계

**목적**: 생성된 모든 Static Node (Company, Product, Person, Technology)에 대해 정규화를 수행합니다.

**Description**: 정규화는 동일한 의미를 가진 다양한 표현을 표준 키워드로 통일하는 과정입니다.

**참고 문서**: `plan/tasks/phase-5/phase-5-5.md` (파일 경로, 주요 기능, 데이터 구조, 정규화 함수 전체 코드, normalization_map 구조, LLM 매핑 프로세스 상세)

### 5.6 Static Link 생성

**목적**: Static Node 간의 관계를 나타내는 링크를 생성합니다.

**Description**: Company와 Product, Person, Technology 간의 관계를 링크로 표현합니다.

**참고 문서**: `plan/tasks/phase-5/phase-5-6.md` (파일 경로, 주요 기능, 데이터 구조, Link 생성 함수 전체 코드 및 role 추출 로직 상세)

### 5.7 생성 스크립트

**목적**: Static Graph 생성을 실행하는 스크립트입니다.

**Description**: 티커별로 Static Graph를 생성하고 JSON 파일로 저장합니다.

**참고 문서**: `plan/tasks/phase-5/phase-5-7.md` (파일 경로, 주요 기능, 데이터 구조, 스크립트 전체 코드, 실행 방법, 명령줄 인자 상세)

---

## Phase 6: Dynamic Graph 생성

### Phase 6 개요

**목적**: 추출된 엔티티 데이터와 파싱된 섹션 데이터를 기반으로 Dynamic Graph를 생성합니다. Dynamic Graph는 Document, Section, Risk, Opportunity, Event, Technology 노드와 이들 간의 관계를 포함하며, 시간/문서 컨텍스트를 포함하는 정보성 노드입니다.

**참고 문서**: `plan/tasks/phase-6/phase-6.md` (입력/출력 데이터, 주요 작업 단계, Phase 간 의존성, 사용하는 데이터 구조 등 상세 내용)

---

## Phase 7: Graph DB 저장

### Phase 7 개요

**목적**: Phase 5~6에서 생성된 Static/Dynamic Graph JSON 파일을 FalkorDB 그래프 데이터베이스에 적재합니다. 모든 노드와 링크를 Cypher 쿼리로 변환하여 데이터베이스에 저장합니다.

**참고 문서**: `plan/tasks/phase-7/phase-7.md` (입력/출력 데이터, 주요 작업 단계, Phase 간 의존성, 사용하는 데이터 구조 등 상세 내용)

---

## Phase 8: 질의 응답 시스템

### Phase 8 개요

**목적**: 자연어 질의를 처리하여 그래프 기반 답변을 생성하는 시스템을 구현합니다. FalkorDB 그래프 데이터와 Embedding 벡터를 활용하여 하이브리드 검색을 수행하고, LLM을 통해 자연어 답변을 생성합니다.

**참고 문서**: `plan/tasks/phase-8/phase-8.md` (입력/출력 데이터, 주요 작업 단계, Phase 간 의존성, 사용하는 데이터 구조 등 상세 내용)

---

## Phase 9: 테스트 및 검증

### Phase 9 개요

**목적**: 전체 시스템의 기능과 성능을 검증합니다. 단위 테스트, 통합 테스트, 그리고 실제 사용 시나리오를 통한 검증을 수행합니다.

**참고 문서**: `plan/tasks/phase-9/phase-9.md` (입력/출력 데이터, 주요 작업 단계, Phase 간 의존성, 사용하는 데이터 구조 등 상세 내용)

---

## 🚀 실행 순서

각 Phase의 실행 스크립트와 상세 실행 방법은 해당 Phase의 tasks 문서를 참고하세요.

**실행 순서**:
1. Phase 1: 환경 설정 (FalkorDB, Python 환경, 의존성, 환경 변수)
2. Phase 2: SEC 공시 다운로드 (`scripts/01_download_filings.py`)
3. Phase 3: 공시 파싱 (`scripts/02_parse_filings.py`)
4. Phase 4: Knowledge Triplet 추출 (`scripts/03_extract_triplets.py`)
5. Phase 5: Static Graph 생성 (`scripts/04_generate_static_graph.py`)
6. Phase 6: Dynamic Graph 생성 (`scripts/05_generate_dynamic_graph.py`)
7. Phase 7: Graph DB 저장 (`scripts/06_load_graph_to_db.py`)
8. Phase 8: 질의 응답 시스템 (API 서버 실행)
9. Phase 9: 테스트 및 검증

**상세 실행 방법**: 각 Phase의 tasks 문서 (`plan/tasks/phase-{N}/phase-{N}-{M}.md`)에서 스크립트 전체 코드 및 실행 방법을 확인하세요.

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

