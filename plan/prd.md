# Product Requirements Document (PRD)

## 📌 프로젝트 개요

본 프로젝트는 주요 테크 기업들의 SEC 공시 자료(10-K 연간 보고서, 10-Q 분기 보고서, 8-K 수시 공시)를 수집하고, **Graph DB와 Vector DB로 적재**하여 사용자의 질의에 대한 심도 깊은 답변을 제공하는 시스템입니다. Graphiti + FalkorDB를 활용한 Knowledge Graph와 Vector DB를 결합하여 "애플의 기회 요소를 알려줘"와 같은 자연어 질의에 대해 구조화된 그래프 기반 답변과 의미 기반 검색을 제공합니다.

**현재 상태**: ✅ Phase 1-9 완료 (API 구현 포함)

## 🎯 목표

1. ✅ **데이터 수집**: 7개 테크 기업의 최근 3년간 SEC 공시(10-K, 10-Q, 8-K) 자료 자동 다운로드
2. ✅ **데이터 저장**: `/data/{ticker_name}/{filing_type}` 폴더 구조로 체계적 저장
3. ✅ **Knowledge Graph 구축**: Graphiti + FalkorDB 기반 구조화된 그래프 데이터베이스 구축
4. ✅ **Vector DB 구축**: 문서 및 엔티티의 의미 기반 검색을 위한 벡터 임베딩 저장
5. ✅ **질의 응답**: 자연어 질의에 대한 그래프 기반 검색 및 벡터 유사도 검색을 결합한 답변 제공
6. ✅ **REST API**: FastAPI 기반 REST API 및 Streamlit 클라이언트 구현

## 🏢 대상 기업

| 회사명 | 티커 | 섹터 |
|--------|------|------|
| Apple | AAPL | Technology |
| Amazon | AMZN | Consumer Cyclical |
| Tesla | TSLA | Consumer Cyclical |
| Alphabet (Google) | GOOGL | Communication Services |
| Microsoft | MSFT | Technology |
| Meta Platforms | META | Communication Services |
| NVIDIA | NVDA | Technology |

## 📋 기능 요구사항

### FR-01: SEC 공시 자료 다운로드 ✅
- ✅ SEC EDGAR API를 통해 다음 공시 유형 다운로드:
  - **10-K**: 연간 보고서 (Annual Report) - 최근 3년
  - **10-Q**: 분기 보고서 (Quarterly Report) - 최근 3년 (연 4회 × 3년 = 12건)
  - **8-K**: 수시 공시 (Current Report) - 최근 3년간 주요 이벤트
- ✅ 최근 3년간(2022, 2023, 2024) 자료 수집
- ✅ `/data/{ticker_name}/{filing_type}/` 폴더에 저장
- ✅ 다운로드 진행 상황 로깅
- ✅ **API 엔드포인트**: `/download` (POST)

**구현 파일**: `app/services/download/sec_downloader.py`

### FR-02: 공시 자료 파싱 및 텍스트 추출 ✅
- ✅ 다운로드된 공시 파일에서 주요 섹션 추출

**10-K (연간 보고서) 섹션:**
  - Item 1: Business
  - Item 1A: Risk Factors
  - Item 7: Management's Discussion and Analysis (MD&A)

**10-Q (분기 보고서) 섹션:**
  - Part I, Item 2: Management's Discussion and Analysis
  - Part II, Item 1A: Risk Factors (변경 사항)

**8-K (수시 공시) 섹션:**
  - Item 2.02: Results of Operations and Financial Condition
  - Item 5.02: Departure/Appointment of Directors or Officers
  - Item 8.01: Other Events

- ✅ HTML/SGML 형식에서 텍스트 추출

**구현 파일**: `app/services/processing/filing_parser.py`

### FR-03: Knowledge Triplet 추출 ✅
- ✅ LLM을 활용한 엔티티 및 관계 추출
- ✅ 추출 대상:
  - **기회 요소 (Opportunities)**
  - **리스크 요소 (Risks)**
  - **주요 이벤트 (Key Events)**
  - **전략 (Strategies)**
  - **재무 지표 (Financial Metrics)**
- ✅ 출력: `data/extracted/{ticker}/{filing_type}/{accession_number}.json`
- ✅ 각 엔티티에 `source_section` 정보 포함
- ✅ **프롬프트 관리**: YAML 파일로 분리 (`app/prompts/triplet_extractor.yaml`)

**구현 파일**: `app/services/processing/triplet_extractor.py`

### FR-03.5: Node/Link Data 생성 ✅
- ✅ Extracted Data와 Parsed Data를 결합하여 Graph Ontology 스키마에 맞는 정형화된 데이터 생성
- ✅ **주요 작업**:
  - Document Node 생성: 공시 문서 메타데이터 통합 (filing_date, period_end_date, year, quarter 등)
  - Section Node 생성: 섹션별 상세 정보 (section_text, text_length, parsed_at 등)
  - Risk/Opportunity/Event/Technology Node 생성:
    - 고유 ID 생성 (예: `risk_aapl_intense_price_competition_2023`)
    - `description_embedding` 벡터 생성 (Gemini `text-embedding-004`, 768차원)
    - 벡터화 텍스트: `{entity}: {description}` (Event는 `{entity} ({date}): {description}`)
    - `extracted_at` 타임스탬프 추가
    - Event의 경우 `date_parsed`, `event_type` 분류
  - Link 생성: 엔티티 간 관계 명시적 생성
    - HAS_RISKS, HAS_OPPORTUNITIES, HAS_EVENTS
    - IS_EXTRACTED_FROM, IS_INCLUDED
- ✅ 출력: `data/graph/{ticker}/{filing_type}/{accession_number}.json`
- ✅ 구조: `{nodes: [...], links: [...]}` 형식

**구현 파일**: 
- `app/services/processing/graph_generator.py` (Static Graph)
- `app/services/processing/dynamic_graph_generator.py` (Dynamic Graph)

### FR-04: Graph Database 및 Vector DB 저장 ✅
- ✅ **입력**: 
  - `data/graph/{TICKER}_static_graph.json` - Static 노드 및 링크
  - `data/graph/{TICKER}_dynamic_graph.json` - Dynamic 노드 및 링크
- ✅ **Graph DB (FalkorDB)**: 구조화된 엔티티와 관계 저장
  - Node 타입: Company, Risk, Opportunity, Event, Technology, Section, Document, Product, Person
  - Link 타입: HAS_RISKS, HAS_OPPORTUNITIES, HAS_EVENTS, HAS_TECHNOLOGIES, IS_EXTRACTED_FROM, IS_INCLUDED, MAKE, HAS_RELATION, IS_MENTIONED_IN
  - Node 스타일: 
    - **Static node**: Company, Person, Product (행위의 주체나 대상, 먼저 저장)
    - **Dynamic node**: Risk, Opportunity, Event, Technology, Section, Document (정보성 성격, 정보 추가 시 static node와 link로 연결)
  - 상세 스키마는 `docs/5-2-graph-ontology-design.md` 참조
  - ✅ **GraphLoader 클래스**를 통한 노드/링크 생성 (MERGE 쿼리로 중복 방지)
  - ✅ 적재 순서: Static Graph → Dynamic Graph
  - ✅ 예상 적재량: ~2,037 노드, ~5,275 링크
- ✅ **Vector DB**: 의미 기반 검색을 위한 임베딩 저장
  - Node/Link Data의 `description_embedding` 활용
  - Document, Section, Risk, Opportunity, Event, Technology, Product, Person의 텍스트를 벡터화
  - 유사도 기반 검색 지원
- ✅ **중복 방지**: `DuplicateChecker` 서비스를 통한 중복 문서 체크
- ✅ **API 엔드포인트**: `/process` (POST)

**구현 파일**: 
- `app/services/graph/graph_loader.py`
- `app/services/processing/duplicate_checker.py`
- `app/services/processing/document_processor.py`

### FR-05: 질의 응답 시스템 ✅
- ✅ 자연어 질의 처리
- ✅ **하이브리드 검색**: 그래프 기반 검색 + 벡터 유사도 검색 결합
  - 그래프 검색: 구조화된 관계 탐색 (예: "애플의 기회 요소")
  - 벡터 검색: 의미 기반 유사 문서/엔티티 검색
- ✅ 관련 엔티티 및 관계 기반 답변 생성
- ✅ 출처 추적: 각 답변에 대한 Document, Section 정보 제공
- ✅ **Intent 추출**: Gemini Structured Output을 활용한 의도 분석
- ✅ **Cypher 쿼리 생성**: Intent 기반 동적 Cypher 쿼리 빌더
- ✅ **스트리밍 답변**: Server-Sent Events (SSE)를 통한 실시간 답변 생성
- ✅ **API 엔드포인트**: `/answer` (POST, Streaming)

**구현 파일**:
- `app/services/query/query_engine.py`
- `app/services/query/intent_extractor.py`
- `app/services/query/cypher_query_builder.py`
- `app/services/query/vector_search.py`
- `app/services/query/answer_generator.py`
- `app/api/routes/answer.py`

### FR-06: REST API 및 클라이언트 ✅
- ✅ **FastAPI 기반 REST API**:
  - `/answer`: 질의 응답 (스트리밍)
  - `/download`: SEC 공시 다운로드
  - `/process`: 문서 처리 및 Graph DB 적재
  - `/health`: 헬스 체크
  - `/docs`: Swagger UI 자동 문서화
- ✅ **Streamlit 클라이언트**: API 테스트 및 사용자 인터페이스
- ✅ **의존성 관리**: FastAPI Dependency Injection 패턴
- ✅ **프롬프트 관리**: YAML 파일 기반 프롬프트 관리 시스템

**구현 파일**:
- `app/api/main.py`
- `app/api/routes/answer.py`
- `app/api/routes/download.py`
- `app/api/routes/process.py`
- `app/api/dependencies.py`
- `app/schemas/api_schemas.py`
- `streamlit_app.py`

## 🛠 기술 스택

### 핵심 기술
| 구분 | 기술 | 용도 |
|------|------|------|
| 프로그래밍 언어 | Python 3.11+ | 전체 시스템 개발 |
| Graph DB | FalkorDB | 구조화된 그래프 데이터 저장 |
| Knowledge Graph | Graphiti | 지식 그래프 관리 및 검색 |
| Vector DB | FalkorDB (Vector Search) | 의미 기반 검색을 위한 벡터 저장 |
| LLM | Gemini 3 Flash / Gemini 2.5 Flash Lite | 엔티티 추출 및 질의 응답 |
| Embedding | Gemini Embedding (text-embedding-004) | 텍스트 벡터화 |
| API Framework | FastAPI | REST API 서버 |
| Web Framework | Streamlit | 클라이언트 UI |

### 주요 라이브러리
```
graphiti-core[falkordb]  # Graphiti with FalkorDB support
sec-edgar-downloader     # SEC 공시 다운로드
beautifulsoup4           # HTML 파싱
python-dotenv            # 환경 변수 관리
google-genai             # Gemini LLM API
fastapi                  # REST API 프레임워크
uvicorn                  # ASGI 서버
streamlit                # 웹 클라이언트
pydantic                 # 데이터 검증
pyyaml                   # YAML 프롬프트 관리
```

## 📂 프로젝트 구조

```
graphiti_test/
├── data/
│   ├── raw/              # 원본 다운로드 파일
│   ├── parsed/           # 파싱된 섹션 데이터
│   ├── extracted/        # 추출된 엔티티 데이터
│   └── graph/            # Graph Ontology 스키마에 맞춘 Node/Link 데이터
├── app/
│   ├── api/              # FastAPI 엔드포인트
│   │   ├── routes/       # 라우터 모듈
│   │   ├── dependencies.py
│   │   └── main.py
│   ├── services/         # 비즈니스 로직 서비스
│   │   ├── query/        # 질의 응답 관련
│   │   ├── download/     # 다운로드 관련
│   │   ├── processing/   # 문서 처리 관련
│   │   ├── graph/        # Graph DB 관련
│   │   └── shared/       # 공유 유틸리티
│   ├── schemas/          # Pydantic 모델
│   ├── prompts/          # YAML 프롬프트 파일
│   └── utils/            # 유틸리티 함수
├── plan/                  # 프로젝트 계획 문서
│   ├── prd.md
│   └── plan.md
├── docs/                  # 구현 문서
│   ├── 3-1-sec-filing-sections.md
│   ├── 4-1-extraction-enhancement.md
│   ├── 5-2-graph-ontology-design.md
│   ├── 8-1-query-system-plan.md
│   └── ...
├── scripts/               # 실행 스크립트
├── tests/                 # 테스트 파일
├── streamlit_app.py       # Streamlit 클라이언트
├── requirements.txt
├── .env.example
└── README.md
```

## 🎭 사용자 케이스

### UC-01: 기회 요소 질의 ✅
```
사용자: "애플의 기회 요소를 알려줘"
시스템: 
- Graph 검색: (AAPL) -[HAS_OPPORTUNITIES]-> (Opportunity) 노드 탐색
- Vector 검색: "기회 요소"와 유사한 의미의 Opportunity 엔티티 검색
- Apple의 10-K 공시에서 추출된 기회 요소 목록 반환
- 각 기회 요소의 출처 섹션 및 문서 정보 제공
- 관련 제품 정보 (Product 노드) 연결 정보 제공
```

### UC-02: 리스크 비교 질의 ✅
```
사용자: "테슬라와 엔비디아의 공통 리스크는?"
시스템:
- Graph 검색: 두 기업의 Risk 노드 비교
- Vector 검색: 유사한 의미의 Risk 엔티티 검색
- 두 기업의 리스크 요소 비교 및 공통점 분석
- 공통 리스크의 출처 문서 및 섹션 정보 제공
```

### UC-03: 제품 관련 질의 ✅
```
사용자: "iPhone 15와 관련된 리스크는?"
시스템:
- Graph 검색: (Product: iPhone 15) -[IS_MENTIONED_IN]-> (Risk) 탐색
- Vector 검색: "iPhone 15"와 유사한 컨텍스트의 Risk 검색
- iPhone 15가 언급된 Risk 요소 목록 반환
- 각 리스크의 출처 및 관련 Company 정보 제공
```

### UC-04: 전략 분석 질의 ✅
```
사용자: "구글의 AI 전략은 어떻게 되어있어?"
시스템:
- Graph 검색: (GOOGL) -[HAS_OPPORTUNITIES]-> (Opportunity) 중 AI 관련 탐색
- Vector 검색: "AI 전략"과 유사한 의미의 Opportunity/Event 검색
- Alphabet의 AI 관련 전략 요소 추출
- 관련 엔티티 및 관계 시각화
- 관련 제품 및 이벤트 정보 제공
```

## ⚙️ 비기능 요구사항

### NFR-01: 성능 ✅
- ✅ 공시 다운로드: 기업당 5분 이내
- ✅ 그래프 저장: 문서당 10분 이내
- ✅ 질의 응답: 5초 이내 (스트리밍 시작)

### NFR-02: 확장성 ✅
- ✅ 새로운 기업 추가 용이
- ✅ 새로운 문서 유형(10-Q, 8-K) 확장 가능
- ✅ 모듈화된 서비스 구조

### NFR-03: 신뢰성 ✅
- ✅ 다운로드 실패 시 재시도 로직
- ✅ 트랜잭션 기반 그래프 저장
- ✅ 중복 문서 방지 메커니즘

### NFR-04: 보안 ✅
- ✅ API 키 환경 변수 관리
- ✅ SEC User-Agent 정책 준수

## 📊 Knowledge Graph Ontology

### Node 타입
- **Company**: 기업 정보 (static node)
- **Risk**: 위험 요소 (dynamic node)
- **Opportunity**: 기회 요소 (dynamic node)
- **Event**: 주요 이벤트 (dynamic node)
- **Technology**: 기술 관련 정보 (dynamic node)
- **Section**: 파싱된 문서의 섹션 (dynamic node)
- **Document**: SEC 공시 문서 (dynamic node)
- **Product**: 제품/서비스 (static node)
- **Person**: 인물 (임원, 직원 등) (static node)

### Link 타입
- `HAS_RISKS`: Company → Risk
- `HAS_OPPORTUNITIES`: Company → Opportunity
- `HAS_EVENTS`: Company → Event
- `HAS_TECHNOLOGIES`: Company → Technology
- `IS_EXTRACTED_FROM`: Risk/Opportunity/Event/Technology → Section
- `IS_INCLUDED`: Section → Document
- `MAKE`: Company → Product
- `HAS_RELATION`: Company → Person (role 속성 포함)
- `IS_MENTIONED_IN`: Product/Person/Company → Risk/Opportunity/Event/Technology

### Node 스타일
- **Static node**: Company, Person, Product
  - 행위의 주체나 대상이 될 수 있는 성격의 노드
  - 먼저 저장됨
- **Dynamic node**: Risk, Opportunity, Event, Technology, Section, Document
  - 정보성 성격의 노드
  - 정보가 추가됨에 따라 static node와 link로 연결됨

**상세 스키마 정의**: `docs/5-2-graph-ontology-design.md` 참조

## 📚 참고 자료

- **공시 다운로드 및 Knowledge Triplet 추출**: [Financial_ADK_Agent_Graph_Database](https://github.com/RubensZimbres/Financial_ADK_Agent_Graph_Database)
- **Graphiti**: [getzep/graphiti](https://github.com/getzep/graphiti)
- **FalkorDB + Graphiti 통합**: [Graphiti + FalkorDB Integration](https://www.falkordb.com/blog/graphiti-falkordb-multi-agent-performance/)
- **SEC EDGAR**: [SEC EDGAR Full-Text Search](https://www.sec.gov/cgi-bin/browse-edgar)
- **Graph Ontology 설계**: `docs/5-2-graph-ontology-design.md`

## ⚠️ 제약 사항

1. SEC EDGAR API 사용 시 User-Agent 헤더 필수
2. API 요청 속도 제한 (초당 10건 이하 권장)
3. LLM API 비용 발생 (토큰 기반 과금)
4. FalkorDB Docker 컨테이너 필요

## 🎯 성공 지표

1. ✅ 7개 기업의 3년간 공시 100% 다운로드 완료
   - 10-K: 7 × 3 = 21건
   - 10-Q: 7 × 12 = 84건 (연 4회 × 3년)
   - 8-K: 기업별 다수 (예상 100건 이상)
2. ✅ 각 공시에서 최소 50개 이상의 Knowledge Triplet 추출
3. ✅ 샘플 질의 10건에 대해 관련 정보 검색 성공률 90% 이상
4. ✅ REST API 및 클라이언트 구현 완료

## 📝 변경 이력

- **2025-12-30**: Phase 1-9 완료, API 구현 완료, 프롬프트 YAML 분리 완료
