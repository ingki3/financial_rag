# Phase 6: Dynamic Graph 생성 실행 계획

## 📌 목적

Phase 5에서 생성된 Static Graph (`{TICKER}_static_graph.json`)를 기반으로, extracted 데이터에서 Dynamic 노드와 링크를 생성하여 `{TICKER}_dynamic_graph.json` 파일로 저장합니다.

---

## 📊 입력/출력 파일

### 입력 파일
| 파일 | 위치 | 설명 |
|------|------|------|
| Extracted 데이터 | `data/extracted/{TICKER}/{FILING_TYPE}/*.json` | LLM이 추출한 triplet 데이터 |
| Static Graph | `data/graph/{TICKER}_static_graph.json` | Phase 5에서 생성한 Static 노드/링크 |

### 출력 파일
| 파일 | 위치 | 설명 |
|------|------|------|
| Dynamic Graph | `data/graph/{TICKER}_dynamic_graph.json` | Dynamic 노드/링크 |

---

## 🔧 생성할 노드 (6종)

### 1. Document Node
각 extracted 파일당 1개의 Document 노드 생성

**ID 규칙**: `doc_{ticker}_{filing_type_lower}_{accession_number}`
- 예: `doc_aapl_10k_0000320193-23-000106`

**스키마**:
```json
{
  "id": "doc_aapl_10k_0000320193-23-000106",
  "node_type": "Document",
  "ticker": "AAPL",
  "filing_type": "10-K",
  "accession_number": "0000320193-23-000106",
  "year": 2023,
  "quarter": null,
  "sections_included": ["business", "risk_factors"],
  "extracted_at": "2025-12-28T16:26:51Z",
  "node_style": "dynamic"
}
```

### 2. Section Node
`sections_included` 배열의 각 섹션당 1개 노드 생성

**ID 규칙**: `section_{ticker}_{filing_type_lower}_{year}_{section_name}`
- 예: `section_aapl_10k_2023_business`

**스키마**:
```json
{
  "id": "section_aapl_10k_2023_business",
  "node_type": "Section",
  "section_name": "business",
  "filing_type": "10-K",
  "ticker": "AAPL",
  "year": 2023,
  "accession_number": "0000320193-23-000106",
  "node_style": "dynamic"
}
```

### 3-6. Risk / Opportunity / Event / Technology Nodes

**ID 규칙**:
- Risk: `risk_{ticker}_{normalized_entity}_{year}`
- Opportunity: `opp_{ticker}_{normalized_entity}_{year}`
- Event: `event_{ticker}_{normalized_entity}_{year}`
- Technology: `tech_{ticker}_{normalized_entity}_{year}`

**스키마 (Risk 예시)**:
```json
{
  "id": "risk_aapl_intense_price_competition_2023",
  "node_type": "Risk",
  "ticker": "AAPL",
  "entity": "Intense Price Competition",
  "description": "The Company faces aggressive price competition...",
  "description_embedding": [0.0123, -0.0456, ...],
  "node_style": "dynamic",
  "extracted_at": "2025-12-28T16:26:51Z",
  "metadata": {
    "source_section": "business",
    "filing_type": "10-K",
    "accession_number": "0000320193-23-000106"
  }
}
```

**Embedding 생성**:
- 대상 노드: Risk, Opportunity, Event, Technology
- 벡터화 텍스트: `{entity}: {description}` (Event는 `{entity} ({date}): {description}`)
- Embedding 모델: Gemini `text-embedding-004` (768차원)
- 필드명: `description_embedding`

---

## 🔗 생성할 링크 (6종)

### 1. IS_INCLUDED (Section → Document)
각 Section이 어떤 Document에 포함되는지 연결

```json
{
  "from": "section_aapl_10k_2023_business",
  "to": "doc_aapl_10k_0000320193-23-000106",
  "relationship_type": "IS_INCLUDED",
  "metadata": { "section_order": 1 }
}
```

### 2. IS_EXTRACTED_FROM (Risk/Opp/Event/Tech → Section)
각 Dynamic 노드가 어떤 Section에서 추출되었는지 연결

```json
{
  "from": "risk_aapl_intense_competition_2023",
  "to": "section_aapl_10k_2023_business",
  "relationship_type": "IS_EXTRACTED_FROM",
  "metadata": { "extraction_method": "llm_extraction" }
}
```

### 3-6. HAS_RISKS / HAS_OPPORTUNITIES / HAS_EVENTS / HAS_TECHNOLOGIES
Company → Dynamic 노드 연결

```json
{
  "from": "AAPL",
  "to": "risk_aapl_intense_competition_2023",
  "relationship_type": "HAS_RISKS"
}
```

### 7. IS_MENTIONED_IN (Static → Dynamic)
Product/Person/Company가 Risk/Opp/Event/Tech에서 언급된 경우

```json
{
  "from": "product_aapl_iphone",
  "to": "opp_aapl_expansion_2023",
  "relationship_type": "IS_MENTIONED_IN",
  "mention_context": "mentioned as a market opportunity for expansion"
}
```

---

## 📁 구현 구조

### 파일 구조
```
app/services/
  ├── dynamic_graph_generator.py    # Dynamic Graph 생성 서비스
  └── embedding_generator.py        # Embedding 생성 서비스

scripts/
  └── 06_generate_dynamic_graph.py  # 실행 스크립트
```

### 주요 함수

```python
# app/services/dynamic_graph_generator.py

def generate_document_node(extracted_data: Dict) -> Dict:
    """Document 노드 생성"""

def generate_section_nodes(extracted_data: Dict) -> List[Dict]:
    """Section 노드 생성"""

def generate_risk_nodes(extracted_data: Dict) -> List[Dict]:
    """Risk 노드 생성"""

def generate_opportunity_nodes(extracted_data: Dict) -> List[Dict]:
    """Opportunity 노드 생성"""

def generate_event_nodes(extracted_data: Dict) -> List[Dict]:
    """Event 노드 생성"""

def generate_technology_nodes(extracted_data: Dict) -> List[Dict]:
    """Technology 노드 생성"""

def generate_is_included_links(section_nodes: List, doc_node: Dict) -> List[Dict]:
    """IS_INCLUDED 링크 생성"""

def generate_is_extracted_from_links(
    dynamic_nodes: List, 
    section_nodes: List,
    extracted_data: Dict
) -> List[Dict]:
    """IS_EXTRACTED_FROM 링크 생성"""

def generate_has_links(ticker: str, nodes: List, link_type: str) -> List[Dict]:
    """HAS_RISKS/HAS_OPPORTUNITIES/HAS_EVENTS/HAS_TECHNOLOGIES 링크 생성"""

def generate_is_mentioned_in_links(
    dynamic_nodes: List,
    static_nodes: Dict,
    extracted_data: Dict
) -> List[Dict]:
    """IS_MENTIONED_IN 링크 생성"""

def generate_dynamic_graph(
    ticker: str,
    extracted_files: List[Path],
    static_graph: Dict,
    with_embedding: bool = True
) -> Dict:
    """전체 Dynamic Graph 생성"""

# app/services/embedding_generator.py

def get_embedding_text(node: Dict) -> str:
    """노드에서 embedding 대상 텍스트 추출"""

async def generate_embedding(text: str, model: str = "text-embedding-004") -> List[float]:
    """단일 텍스트 embedding 생성"""

async def generate_embeddings_batch(texts: List[str], batch_size: int = 100) -> List[List[float]]:
    """배치 단위 embedding 생성"""

async def add_embeddings_to_nodes(nodes: List[Dict]) -> List[Dict]:
    """노드 리스트에 embedding 추가"""
```

---

## 🚀 실행 단계

### Step 1: 서비스 모듈 구현
`app/services/dynamic_graph_generator.py` 생성

### Step 2: 실행 스크립트 구현
`scripts/06_generate_dynamic_graph.py` 생성

### Step 3: 실행
```bash
cd /home/ingki3/Dev/graphiti_test
source venv/bin/activate
python scripts/06_generate_dynamic_graph.py --ticker AAPL
```

### Step 4: 전체 티커 실행
```bash
python scripts/06_generate_dynamic_graph.py --ticker AAPL AMZN GOOGL META MSFT NVDA TSLA
```

---

## 📋 체크리스트

### 노드 생성
- [x] `generate_document_node()` 구현 ✅
- [x] `generate_section_nodes()` 구현 ✅
- [x] `generate_risk_nodes()` 구현 ✅
- [x] `generate_opportunity_nodes()` 구현 ✅
- [x] `generate_event_nodes()` 구현 ✅
- [x] `generate_technology_nodes()` 구현 ✅

### 링크 생성
- [x] `generate_is_included_links()` 구현 ✅
- [x] `generate_is_extracted_from_links()` 구현 ✅
- [x] `generate_has_links()` 구현 ✅ (HAS_RISKS, HAS_OPPORTUNITIES, HAS_EVENTS, HAS_TECHNOLOGIES)
- [x] `generate_is_mentioned_in_links()` 구현 ✅

### Embedding 생성
- [x] `app/services/embedding_generator.py` 구현 ✅
- [x] `get_embedding_text()` 구현 ✅
- [x] `generate_embedding()` 구현 (Gemini API) ✅
- [x] `generate_embeddings_batch()` 구현 ✅
- [x] `add_embeddings_to_nodes()` 구현 ✅

### 통합
- [x] `generate_dynamic_graph()` 구현 ✅
- [x] Embedding 생성 통합 ✅
- [x] `scripts/06_generate_dynamic_graph.py` 구현 ✅
- [x] `--no-embedding` 옵션 추가 ✅
- [ ] 단일 티커 테스트 (AAPL) - Embedding 포함
- [ ] 전체 티커 실행

---

## 🛠️ 구현 완료된 파일

### `app/services/dynamic_graph_generator.py`
Dynamic Graph 생성 서비스 모듈 - 약 500줄

**핵심 구현 내용:**

```python
# 유틸리티 함수
def normalize_id(text: str) -> str:
    """텍스트를 ID로 정규화 (소문자, 언더스코어)"""

def normalize_filing_type(filing_type: str) -> str:
    """Filing type 정규화 (10-K -> 10k)"""

# 노드 생성 함수
def generate_document_node(extracted_data: Dict) -> Dict:
    """Document 노드 생성 - ID: doc_{ticker}_{filing_type}_{accession}"""

def generate_section_nodes(extracted_data: Dict) -> List[Dict]:
    """Section 노드 생성 - ID: section_{ticker}_{filing_type}_{year}_{section}"""

def generate_entity_nodes(extracted_data, category, node_type, id_prefix) -> List[Dict]:
    """Risk/Opp/Event/Tech 공통 노드 생성 로직"""

def generate_risk_nodes(extracted_data: Dict) -> List[Dict]:
def generate_opportunity_nodes(extracted_data: Dict) -> List[Dict]:
def generate_event_nodes(extracted_data: Dict) -> List[Dict]:
def generate_technology_nodes(extracted_data: Dict) -> List[Dict]:

# 링크 생성 함수
def generate_is_included_links(section_nodes, doc_node) -> List[Dict]:
    """Section → Document 링크"""

def generate_is_extracted_from_links(dynamic_nodes, section_nodes, extracted_data) -> List[Dict]:
    """Dynamic Node → Section 링크"""

def generate_has_links(ticker, nodes, link_type) -> List[Dict]:
    """Company → Dynamic Node 링크 (HAS_RISKS 등)"""

def generate_is_mentioned_in_links(dynamic_nodes, static_nodes, extracted_data) -> List[Dict]:
    """Product/Person/Company → Dynamic Node 링크"""

# 메인 함수
def generate_dynamic_graph(ticker, extracted_files, static_graph) -> Dict:
    """전체 Dynamic Graph 생성 - 노드 중복 제거 포함"""
```

### `scripts/06_generate_dynamic_graph.py`
실행 스크립트 - 티커별 Dynamic Graph JSON 파일 생성

**사용법:**
```bash
# 단일 티커
python scripts/06_generate_dynamic_graph.py --ticker AAPL

# 여러 티커
python scripts/06_generate_dynamic_graph.py --ticker AAPL AMZN GOOGL META MSFT NVDA TSLA
```

**처리 흐름:**
1. Static Graph 로드 (`{TICKER}_static_graph.json`)
2. Extracted 파일들 순회
3. Dynamic 노드 생성 (Document, Section, Risk, Opp, Event, Tech)
4. 링크 생성 (IS_INCLUDED, IS_EXTRACTED_FROM, HAS_*, IS_MENTIONED_IN)
5. 중복 제거 및 저장 (`{TICKER}_dynamic_graph.json`)

---

## 📊 예상 출력

### `{TICKER}_dynamic_graph.json` 구조
```json
{
  "ticker": "AAPL",
  "generated_at": "2025-12-29T00:00:00Z",
  "nodes": {
    "Document": [...],
    "Section": [...],
    "Risk": [...],
    "Opportunity": [...],
    "Event": [...],
    "Technology": [...]
  },
  "links": [
    { "from": "...", "to": "...", "relationship_type": "IS_INCLUDED", ... },
    { "from": "...", "to": "...", "relationship_type": "IS_EXTRACTED_FROM", ... },
    { "from": "...", "to": "...", "relationship_type": "HAS_RISKS", ... },
    { "from": "...", "to": "...", "relationship_type": "IS_MENTIONED_IN", ... }
  ]
}
```

### 예상 노드/링크 수 (AAPL 기준)

| 노드 타입 | 예상 수 |
|----------|--------|
| Document | ~28개 (10-K 3개 + 10-Q 15개 + 8-K 10개) |
| Section | ~56개 (Document당 ~2개 섹션) |
| Risk | ~50개 |
| Opportunity | ~50개 |
| Event | ~30개 |
| Technology | ~30개 |

| 링크 타입 | 예상 수 |
|----------|--------|
| IS_INCLUDED | ~56개 |
| IS_EXTRACTED_FROM | ~160개 |
| HAS_* | ~160개 |
| IS_MENTIONED_IN | ~100개 |

---

## ⚠️ 주의사항

1. **ID 정규화**: `normalize_id()` 함수 사용하여 일관된 ID 생성
   - 소문자 변환, 특수문자 → 언더스코어, 연속 언더스코어 제거

2. **중복 제거**: 동일한 entity는 년도별로 1개만 생성
   - `seen_node_ids` set으로 중복 체크

3. **Section 매칭**: `source_section` 필드를 사용하여 정확한 Section 노드와 매칭
   - Section ID 형식: `section_{ticker}_{filing_type}_{year}_{section_name}`

4. **Static 노드 참조**: IS_MENTIONED_IN 링크 생성 시 Static Graph의 노드 ID와 정확히 매칭
   - Product/Person 이름(소문자)으로 매핑 테이블 생성

5. **mention_context 필수**: IS_MENTIONED_IN 링크에는 반드시 `mention_context` 포함
   - extracted 데이터의 `mentioned_products[].mention_context` 사용

6. **임시 필드 제거**: 노드 생성 시 `_mentioned_*` 필드는 링크 생성 후 제거
   - 최종 JSON에는 포함되지 않음

7. **Embedding 생성**: Risk/Opportunity/Event/Technology 노드에 `description_embedding` 필드 추가
   - Gemini `text-embedding-004` 모델 사용 (768차원)
   - 배치 처리로 API 호출 최적화 (100개 단위)
   - 환경변수 `GOOGLE_API_KEY` 필요

---

## 🔧 구현 세부사항

### ID 생성 규칙

| 노드 타입 | ID 형식 | 예시 |
|----------|--------|------|
| Document | `doc_{ticker}_{filing_type}_{accession}` | `doc_aapl_10k_0000320193-23-000106` |
| Section | `section_{ticker}_{filing_type}_{year}_{section}` | `section_aapl_10k_2023_business` |
| Risk | `risk_{ticker}_{entity}_{year}` | `risk_aapl_intense_competition_2023` |
| Opportunity | `opp_{ticker}_{entity}_{year}` | `opp_aapl_expansion_2023` |
| Event | `event_{ticker}_{entity}_{year}` | `event_aapl_iphone15_launch_2023` |
| Technology | `tech_{ticker}_{entity}_{year}` | `tech_aapl_a17_pro_2023` |

### 링크 생성 순서

1. **IS_INCLUDED**: Section → Document (섹션 순서 포함)
2. **IS_EXTRACTED_FROM**: Dynamic Node → Section (source_section 기반)
3. **HAS_RISKS**: Company → Risk
4. **HAS_OPPORTUNITIES**: Company → Opportunity
5. **HAS_EVENTS**: Company → Event
6. **HAS_TECHNOLOGIES**: Company → Technology
7. **IS_MENTIONED_IN**: Product/Person/Company → Dynamic Node

### 예외 처리

- `company.get("ticker")` 가 None인 경우 `company.get("name")` 사용
- Static 노드에 매칭되지 않는 mentioned 항목은 링크 생성 스킵
- 파일 읽기 오류 시 해당 파일 스킵하고 계속 진행

---

## 🧬 Embedding 생성

### 개요
Risk, Opportunity, Event, Technology 노드에 `description_embedding` 필드를 추가하여 의미 기반 검색을 지원합니다.

### Embedding 모델
- **모델**: Gemini `text-embedding-004`
- **차원**: 768
- **API**: `google.generativeai.embed_content()`

### 벡터화 대상 텍스트

| 노드 타입 | 텍스트 형식 |
|----------|-----------|
| Risk | `{entity}: {description}` |
| Opportunity | `{entity}: {description}` |
| Event | `{entity} ({date}): {description}` |
| Technology | `{entity}: {description}` |

### 구현 예시

```python
# app/services/embedding_generator.py

import google.generativeai as genai
from typing import List, Dict
import os

genai.configure(api_key=os.getenv("GOOGLE_API_KEY"))

def get_embedding_text(node: Dict) -> str:
    """노드에서 embedding 대상 텍스트 추출"""
    entity = node.get("entity", "")
    description = node.get("description", "")
    
    # Event 노드는 date 포함
    if node.get("node_type") == "Event":
        date = node.get("metadata", {}).get("date", "")
        if date:
            return f"{entity} ({date}): {description}"
    
    return f"{entity}: {description}"

async def generate_embedding(text: str, model: str = "models/text-embedding-004") -> List[float]:
    """단일 텍스트 embedding 생성"""
    result = genai.embed_content(
        model=model,
        content=text,
        task_type="retrieval_document"
    )
    return result['embedding']

async def generate_embeddings_batch(texts: List[str], batch_size: int = 100) -> List[List[float]]:
    """배치 단위 embedding 생성"""
    embeddings = []
    for i in range(0, len(texts), batch_size):
        batch = texts[i:i + batch_size]
        result = genai.embed_content(
            model="models/text-embedding-004",
            content=batch,
            task_type="retrieval_document"
        )
        embeddings.extend(result['embedding'])
    return embeddings

async def add_embeddings_to_nodes(nodes: List[Dict]) -> List[Dict]:
    """노드 리스트에 embedding 추가"""
    if not nodes:
        return nodes
    
    texts = [get_embedding_text(node) for node in nodes]
    embeddings = await generate_embeddings_batch(texts)
    
    for node, embedding in zip(nodes, embeddings):
        node["description_embedding"] = embedding
    
    return nodes
```

### 처리 흐름

```
1. Dynamic 노드 생성 (Risk, Opp, Event, Tech)
    ↓
2. 각 노드에서 embedding 대상 텍스트 추출
    ↓
3. Gemini API로 배치 embedding 생성 (100개 단위)
    ↓
4. 각 노드에 description_embedding 필드 추가
    ↓
5. Dynamic Graph JSON 저장
```

### 예상 API 호출량

| 티커 | Risk | Opp | Event | Tech | 총 노드 | API 호출 (100개/배치) |
|------|------|-----|-------|------|--------|---------------------|
| AAPL | 79 | 62 | 67 | 45 | 253 | 3회 |
| AMZN | 28 | 29 | 26 | 20 | 103 | 2회 |
| GOOGL | 54 | 54 | 82 | 53 | 243 | 3회 |
| META | 69 | 65 | 91 | 66 | 291 | 3회 |
| MSFT | 33 | 33 | 55 | 53 | 174 | 2회 |
| NVDA | 79 | 73 | 99 | 93 | 344 | 4회 |
| TSLA | 33 | 32 | 44 | 52 | 161 | 2회 |
| **합계** | **375** | **348** | **464** | **382** | **1,569** | **~19회** |

---

## 🔗 관련 문서

- `docs/graph_ontology_design.md` - 노드/링크 스키마 정의
- `docs/phase4_5_graph_data_generation_plan.md` - 상세 구현 계획
- `docs/phase5_dynamic_links_implementation.md` - 링크 생성 상세 구현

