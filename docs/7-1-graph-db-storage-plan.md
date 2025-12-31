# Phase 7: Graph DB 저장 실행 계획

## 📌 목적

Phase 5~6에서 생성된 Static/Dynamic Graph JSON 파일을 FalkorDB에 적재합니다.
- `{TICKER}_static_graph.json` → Company, Product, Person 노드 및 MAKE, HAS_RELATION 링크
- `{TICKER}_dynamic_graph.json` → Document, Section, Risk, Opportunity, Event, Technology 노드 및 모든 Dynamic 링크
  - **Embedding 포함**: Risk, Opportunity, Event, Technology 노드에 `description_embedding` (768차원)

---

## 📊 입력 파일

| 파일 | 위치 | 내용 |
|------|------|------|
| Static Graph | `data/graph/{TICKER}_static_graph.json` | Company, Product, Person 노드 + 링크 |
| Dynamic Graph | `data/graph/{TICKER}_dynamic_graph.json` | Document, Section, Risk, Opp, Event, Tech 노드 + 링크 + **Embedding** |

### 현재 생성된 파일 (Phase 6 완료 후)

| 티커 | Static Graph | Dynamic Graph | Embeddings |
|------|-------------|---------------|------------|
| AAPL | 17 KB | **4.9 MB** | 253 |
| AMZN | 13 KB | **2.0 MB** | 103 |
| GOOGL | 26 KB | **4.8 MB** | 243 |
| META | 12 KB | **5.7 MB** | 291 |
| MSFT | 26 KB | **3.4 MB** | 174 |
| NVDA | 28 KB | **6.8 MB** | 344 |
| TSLA | 10 KB | **3.2 MB** | 161 |
| **합계** | **132 KB** | **30.8 MB** | **1,569** |

> ⚠️ Dynamic Graph 파일 크기가 크게 증가한 것은 768차원 Embedding 벡터가 각 노드에 포함되었기 때문입니다.

---

## 🗄️ FalkorDB 설정

### 연결 정보
```
Host: localhost (또는 환경변수 FALKORDB_HOST)
Port: 6379 (또는 환경변수 FALKORDB_PORT)
Graph Name: financial_kg
```

### Docker 실행 (필요시)
```bash
docker run -d \
  --name falkordb \
  -p 6379:6379 \
  falkordb/falkordb:latest
```

---

## 🔧 구현 구조

### 파일 구조
```
app/services/
  └── graph_loader.py           # FalkorDB 적재 서비스

scripts/
  └── 07_load_graph_to_db.py    # 실행 스크립트
```

### 주요 클래스/함수

```python
# app/services/graph_loader.py

class GraphLoader:
    """FalkorDB에 노드 및 링크를 적재하는 클래스"""
    
    def __init__(self, host: str, port: int, graph_name: str):
        """FalkorDB 연결 초기화"""
    
    async def initialize(self):
        """인덱스 및 제약조건 생성"""
    
    async def create_node(self, node: Dict):
        """노드 생성 (MERGE 사용하여 중복 방지)"""
    
    async def create_link(self, link: Dict):
        """링크 생성 (MERGE 사용하여 중복 방지)"""
    
    async def load_static_graph(self, ticker: str, static_graph: Dict):
        """Static Graph 적재"""
    
    async def load_dynamic_graph(self, ticker: str, dynamic_graph: Dict):
        """Dynamic Graph 적재"""
    
    def get_stats(self) -> Dict:
        """적재 통계 반환"""
```

---

## 📝 Cypher 쿼리 패턴

### 노드 생성 (MERGE)

```cypher
// Company 노드
MERGE (n:Company {id: $id})
SET n.ticker = $ticker,
    n.name = $name,
    n.sector = $sector,
    n.description = $description,
    n.node_style = $node_style

// Product 노드
MERGE (n:Product {id: $id})
SET n.name = $name,
    n.product_type = $product_type,
    n.category = $category,
    n.description = $description,
    n.node_style = $node_style

// Risk/Opportunity/Event/Technology 노드 (Embedding 포함)
MERGE (n:Risk {id: $id})
SET n.ticker = $ticker,
    n.entity = $entity,
    n.description = $description,
    n.description_embedding = $description_embedding,
    n.node_style = $node_style,
    n.extracted_at = $extracted_at,
    n.source_section = $metadata.source_section,
    n.filing_type = $metadata.filing_type,
    n.accession_number = $metadata.accession_number
```

> ⚠️ **Embedding 저장 주의**: `description_embedding`은 768차원 float 배열입니다. FalkorDB에서 배열 속성으로 저장됩니다.

### 링크 생성 (MERGE)

```cypher
// MAKE 링크
MATCH (a:Company {id: $from_id})
MATCH (b:Product {id: $to_id})
MERGE (a)-[r:MAKE]->(b)
SET r.created_at = $created_at

// HAS_RISKS 링크
MATCH (a:Company {id: $from_id})
MATCH (b:Risk {id: $to_id})
MERGE (a)-[r:HAS_RISKS]->(b)
SET r.created_at = $created_at

// IS_MENTIONED_IN 링크
MATCH (a {id: $from_id})
MATCH (b {id: $to_id})
MERGE (a)-[r:IS_MENTIONED_IN]->(b)
SET r.mention_context = $mention_context,
    r.created_at = $created_at
```

### 인덱스 생성

```cypher
// 각 노드 타입별 id 인덱스
CREATE INDEX FOR (n:Company) ON (n.id)
CREATE INDEX FOR (n:Product) ON (n.id)
CREATE INDEX FOR (n:Person) ON (n.id)
CREATE INDEX FOR (n:Document) ON (n.id)
CREATE INDEX FOR (n:Section) ON (n.id)
CREATE INDEX FOR (n:Risk) ON (n.id)
CREATE INDEX FOR (n:Opportunity) ON (n.id)
CREATE INDEX FOR (n:Event) ON (n.id)
CREATE INDEX FOR (n:Technology) ON (n.id)

// ticker 기반 검색용 인덱스
CREATE INDEX FOR (n:Company) ON (n.ticker)
CREATE INDEX FOR (n:Risk) ON (n.ticker)
CREATE INDEX FOR (n:Opportunity) ON (n.ticker)
CREATE INDEX FOR (n:Event) ON (n.ticker)
CREATE INDEX FOR (n:Technology) ON (n.ticker)
```

---

## 🚀 실행 단계

### Step 1: FalkorDB 실행 확인
```bash
# Docker 컨테이너 상태 확인
docker ps | grep falkordb

# 없으면 실행
docker run -d --name falkordb -p 6379:6379 falkordb/falkordb:latest
```

### Step 2: 서비스 모듈 구현
`app/services/graph_loader.py` 생성

### Step 3: 실행 스크립트 구현
`scripts/07_load_graph_to_db.py` 생성

### Step 4: 단일 티커 테스트
```bash
cd /home/ingki3/Dev/graphiti_test
source venv/bin/activate
python scripts/07_load_graph_to_db.py --ticker AAPL
```

### Step 5: 전체 티커 적재
```bash
python scripts/07_load_graph_to_db.py --ticker AAPL AMZN GOOGL META MSFT NVDA TSLA
```

### Step 6: 적재 결과 검증
```bash
python scripts/07_load_graph_to_db.py --verify
```

---

## 📋 체크리스트

### 사전 준비
- [ ] FalkorDB Docker 컨테이너 실행 확인
- [ ] falkordb Python 패키지 설치 확인 (`pip install falkordb`)

### 구현 ✅ 완료
- [x] `app/services/graph_loader.py` 구현 ✅
  - [x] `__init__()` - FalkorDB 연결 ✅
  - [x] `connect()` - 연결 수립 ✅
  - [x] `initialize()` - 인덱스 생성 ✅
  - [x] `create_node()` - 노드 MERGE (Embedding 지원) ✅
  - [x] `create_link()` - 링크 MERGE ✅
  - [x] `load_static_graph()` - Static Graph 적재 ✅
  - [x] `load_dynamic_graph()` - Dynamic Graph 적재 ✅
  - [x] `get_stats()` - 통계 조회 ✅
  - [x] `verify()` - 적재 결과 검증 ✅
- [x] `scripts/07_load_graph_to_db.py` 구현 ✅

### 테스트 (대기 중)
- [ ] 단일 티커 테스트 (AAPL)
- [ ] 노드 생성 확인
- [ ] 링크 생성 확인
- [ ] Embedding 저장 확인
- [ ] 중복 방지 확인 (MERGE 동작)

### 전체 적재 (대기 중)
- [ ] 7개 티커 전체 적재
- [ ] 적재 통계 확인
- [ ] 검증 쿼리 실행

---

## 📊 실제 적재량 (Phase 6 완료 기준)

### 노드 수

| 노드 타입 | 수량 | Embedding |
|----------|------|-----------|
| Company | 7 | - |
| Product | ~210 | - |
| Person | ~27 | - |
| Document | 134 | - |
| Section | 90 | - |
| Risk | 375 | ✅ 768차원 |
| Opportunity | 348 | ✅ 768차원 |
| Event | 464 | ✅ 768차원 |
| Technology | 382 | ✅ 768차원 |
| **총 노드** | **~2,037** | **1,569개** |

### 티커별 노드 상세

| 티커 | Doc | Section | Risk | Opp | Event | Tech | Embeddings |
|------|-----|---------|------|-----|-------|------|------------|
| AAPL | 25 | 14 | 79 | 62 | 67 | 45 | 253 |
| AMZN | 4 | 7 | 28 | 29 | 26 | 20 | 103 |
| GOOGL | 26 | 14 | 54 | 54 | 82 | 53 | 243 |
| META | 19 | 14 | 69 | 65 | 91 | 66 | 291 |
| MSFT | 20 | 15 | 33 | 33 | 55 | 53 | 174 |
| NVDA | 23 | 17 | 79 | 73 | 99 | 93 | 344 |
| TSLA | 17 | 9 | 33 | 32 | 44 | 52 | 161 |

### 링크 수

| 링크 타입 | 수량 |
|----------|------|
| MAKE | ~210 |
| HAS_RELATION | ~27 |
| IS_INCLUDED | 186 |
| IS_EXTRACTED_FROM | 1,650 |
| HAS_RISKS | 395 |
| HAS_OPPORTUNITIES | 356 |
| HAS_EVENTS | 471 |
| HAS_TECHNOLOGIES | 428 |
| IS_MENTIONED_IN | 1,552 |
| **총 링크** | **~5,275** |

### 티커별 링크 상세

| 티커 | IS_INCLUDED | IS_EXTRACTED_FROM | HAS_* | IS_MENTIONED_IN | Total |
|------|-------------|-------------------|-------|-----------------|-------|
| AAPL | 28 | 273 | 273 | 194 | 768 |
| AMZN | 7 | 105 | 105 | 107 | 324 |
| GOOGL | 34 | 253 | 253 | 278 | 818 |
| META | 26 | 309 | 309 | 299 | 943 |
| MSFT | 23 | 181 | 181 | 197 | 582 |
| NVDA | 28 | 360 | 360 | 362 | 1,110 |
| TSLA | 20 | 169 | 169 | 115 | 473 |

---

## ⚠️ 주의사항

### 1. 적재 순서
Static Graph를 먼저 적재한 후 Dynamic Graph를 적재해야 합니다.
- Static 노드 (Company, Product, Person) → IS_MENTIONED_IN 링크의 from 노드
- Dynamic 노드 (Risk, Opp, Event, Tech) → IS_MENTIONED_IN 링크의 to 노드

### 2. MERGE vs CREATE
- `MERGE` 사용하여 중복 노드/링크 방지
- 동일 ID의 노드가 이미 존재하면 업데이트

### 3. 트랜잭션 관리
- 대량 적재 시 배치 단위로 트랜잭션 커밋
- 권장 배치 크기: 1000개 노드/링크

### 4. 에러 처리
- 개별 노드/링크 생성 실패 시 로깅 후 계속 진행
- 전체 실패 통계 기록

### 5. 멱등성 보장
- 동일 스크립트를 여러 번 실행해도 동일한 결과
- MERGE 쿼리로 구현

### 6. Embedding 처리
- `description_embedding`은 768차원 float 배열 (약 6KB/노드)
- FalkorDB에서 배열 속성으로 저장
- 향후 벡터 검색을 위해 별도 Vector DB 연동 고려 가능
- 현재 단계에서는 FalkorDB에 그대로 저장

### 7. 대용량 파일 처리
- Dynamic Graph JSON 파일이 최대 6.8MB (NVDA)
- JSON 로드 시 메모리 효율적으로 처리
- 노드/링크 단위로 배치 처리 권장

---

## 🔍 검증 쿼리

### 노드 수 확인
```cypher
MATCH (n) RETURN labels(n)[0] AS label, count(n) AS count ORDER BY label
```

### 링크 수 확인
```cypher
MATCH ()-[r]->() RETURN type(r) AS type, count(r) AS count ORDER BY type
```

### 티커별 노드 수 확인
```cypher
MATCH (n) WHERE n.ticker IS NOT NULL
RETURN n.ticker AS ticker, labels(n)[0] AS label, count(n) AS count
ORDER BY ticker, label
```

### 샘플 데이터 확인
```cypher
// AAPL의 Risk와 연결된 Product 확인
MATCH (p:Product)-[r:IS_MENTIONED_IN]->(risk:Risk)
WHERE risk.ticker = 'AAPL'
RETURN p.name, risk.entity, r.mention_context
LIMIT 10
```

### Embedding 확인
```cypher
// Embedding이 있는 노드 수 확인
MATCH (n)
WHERE n.description_embedding IS NOT NULL
RETURN labels(n)[0] AS label, count(n) AS count
ORDER BY label

// Embedding 차원 확인 (샘플)
MATCH (r:Risk)
WHERE r.description_embedding IS NOT NULL
RETURN r.entity, size(r.description_embedding) AS embedding_dim
LIMIT 5
```

---

## 🔗 관련 문서

- `docs/graph_ontology_design.md` - 노드/링크 스키마 정의
- `docs/phase6_dynamic_graph_execution_plan.md` - Dynamic Graph 생성 계획
- `plan.md` - 전체 프로젝트 계획

---

## 📅 예상 소요 시간

| 작업 | 예상 시간 |
|------|----------|
| FalkorDB 설정 확인 | 15분 |
| graph_loader.py 구현 | 1시간 |
| 실행 스크립트 구현 | 30분 |
| 단일 티커 테스트 | 30분 |
| 전체 티커 적재 | 30분 |
| 검증 및 디버깅 | 30분 |
| **총계** | **~3시간** |

