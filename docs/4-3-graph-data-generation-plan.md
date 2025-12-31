# Phase 4.5: Graph Node/Link Data Generation Plan

## 📌 목적

`extracted` 데이터를 `graph_ontology_design.md`의 스키마에 맞게 Node와 Link 데이터로 변환하여 저장합니다. 이후 이 데이터를 읽어서 Graph DB (FalkorDB)로 적재할 수 있도록 구조화합니다.

## 🎯 전체 프로세스 개요

```
extracted JSON files
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
4. Cypher 쿼리 생성 가능한 형태로 저장
```

---

## 📁 출력 파일 구조

### Static Graph 파일: `{TICKER}_static_graph.json`
- **위치**: `data/graph/{TICKER}_static_graph.json`
- **내용**: Company, Product, Person 노드 및 이들 간의 링크

### Dynamic Graph 파일: `{TICKER}_dynamic_graph.json`
- **위치**: `data/graph/{TICKER}_dynamic_graph.json`
- **내용**: Risk, Opportunity, Event, Technology, Section, Document 노드 및 이들 간의 링크, Static 노드와의 링크

---

## 🔧 Phase 1: Static Node 생성

### 1.1 입력 데이터 분석

**소스**: `data/extracted/{TICKER}/**/*.json` 파일들

각 extracted 파일에서 다음 정보를 수집:
- `mentioned_products_global`: 전체 제품 목록
- `mentioned_persons_global`: 전체 인물 목록
- `ticker`: 회사 티커

### 1.2 Company Node 생성

**규칙**:
- 각 티커당 **1개의 Company 노드**만 생성
- ID: `{ticker}` (예: `AAPL`)
- 기본 정보는 외부 데이터 소스 또는 설정 파일에서 가져오기

**스키마**:
```json
{
  "id": "AAPL",
  "node_type": "Company",
  "ticker": "AAPL",
  "name": "Apple Inc.",
  "sector": "Technology",
  "description": "Apple Inc.는 스마트폰, 개인용 컴퓨터, 태블릿, 웨어러블 디바이스 등을 설계, 제조 및 판매하는 글로벌 기술 기업입니다.",
  "node_style": "static"
}
```

**구현**:
- `app/services/graph_generator.py`에 `generate_company_node(ticker: str) -> Dict` 함수 생성
- Company 정보는 설정 파일(`data/company_info.json`) 또는 외부 API에서 가져오기

### 1.3 Product Node 생성

**규칙**:
- `mentioned_products_global`에서 중복 제거하여 Product 노드 생성
- ID: `product_{ticker}_{normalized_name}` (예: `product_aapl_iphone`)
- `normalized_name`: 소문자, 공백/특수문자 → 언더스코어

**스키마**:
```json
{
  "id": "product_aapl_iphone",
  "node_type": "Product",
  "name": "iPhone",
  "product_type": "hardware",
  "category": "smartphone",
  "description": "Apple의 스마트폰 제품 라인",
  "node_style": "static"
}
```

**구현**:
- `generate_product_nodes(ticker: str, extracted_files: List[Path]) -> List[Dict]`
- 모든 extracted 파일을 순회하며 `mentioned_products_global` 수집
- 중복 제거 (이름 기준, 대소문자 무시)
- `product_type`, `category`는 LLM 또는 규칙 기반으로 분류

**Product 분류 규칙**:
- `product_type`: `hardware`, `software`, `service`, `platform`, `other`
- `category`: `smartphone`, `wearable`, `cloud_service`, `electric_vehicle`, `software_platform` 등
- **중요**: Product의 `name`은 반드시 고유명사여야 합니다 (예: "Tesla Model 3", "iPhone 15 Pro", "NVIDIA H100 GPU"). 일반명사 "car", "phone", "chip" 등은 사용하지 않습니다.

### 1.4 Person Node 생성

**규칙**:
- `mentioned_persons_global`에서 중복 제거하여 Person 노드 생성
- ID: `person_{ticker}_{normalized_name}` (예: `person_aapl_tim_cook`)
- `normalized_name`: 소문자, 공백/특수문자 → 언더스코어

**스키마**:
```json
{
  "id": "person_aapl_tim_cook",
  "node_type": "Person",
  "name": "Tim Cook",
  "description": "Apple Inc.의 CEO로서 2011년부터 회사를 이끌고 있으며, 제품 개발 및 글로벌 운영 전략을 담당하고 있습니다.",
  "node_style": "static"
}
```

**구현**:
- `generate_person_nodes(ticker: str, extracted_files: List[Path]) -> List[Dict]`
- 모든 extracted 파일을 순회하며 `mentioned_persons_global` 수집
- 중복 제거 (이름 기준)
- `description`은 LLM 또는 외부 데이터 소스에서 가져오기

---

## 🔗 Phase 2: Static Node 간 Link 생성

### 2.1 MAKE Link (Company → Product)

**규칙**:
- 모든 Product 노드에 대해 `{ticker}` Company 노드와 `MAKE` 링크 생성

**스키마**:
```json
{
  "from": "AAPL",
  "to": "product_aapl_iphone",
  "relationship_type": "MAKE",
  "created_at": "2024-12-28T00:00:00Z",
  "metadata": {
    "launch_date": null,
    "status": "active"
  }
}
```

**구현**:
- `generate_make_links(company_id: str, product_nodes: List[Dict]) -> List[Dict]`
- 모든 Product 노드에 대해 Company → Product 링크 생성

### 2.2 HAS_RELATION Link (Company → Person)

**규칙**:
- 모든 Person 노드에 대해 `{ticker}` Company 노드와 `HAS_RELATION` 링크 생성
- `role`은 `mentioned_persons_global`에서 가져오거나 외부 데이터 소스에서 가져오기

**스키마**:
```json
{
  "from": "AAPL",
  "to": "person_aapl_tim_cook",
  "relationship_type": "HAS_RELATION",
  "role": "CEO",
  "created_at": "2024-12-28T00:00:00Z",
  "metadata": {
    "start_date": "2011-08-24",
    "end_date": null
  }
}
```

**구현**:
- `generate_has_relation_links(company_id: str, person_nodes: List[Dict], extracted_files: List[Path]) -> List[Dict]`
- `mentioned_persons_global`에서 `role` 정보 추출
- 외부 데이터 소스에서 `start_date`, `end_date` 정보 가져오기 (선택)

---

## 📊 Phase 3: Static Graph 파일 저장

### 3.1 파일 구조

**파일명**: `{TICKER}_static_graph.json`

**구조**:
```json
{
  "ticker": "AAPL",
  "generated_at": "2024-12-28T00:00:00Z",
  "nodes": {
    "Company": [
      {
        "id": "AAPL",
        "node_type": "Company",
        ...
      }
    ],
    "Product": [
      {
        "id": "product_aapl_iphone",
        "node_type": "Product",
        ...
      }
    ],
    "Person": [
      {
        "id": "person_aapl_tim_cook",
        "node_type": "Person",
        ...
      }
    ]
  },
  "links": [
    {
      "from": "AAPL",
      "to": "product_aapl_iphone",
      "relationship_type": "MAKE",
      ...
    },
    {
      "from": "AAPL",
      "to": "person_aapl_tim_cook",
      "relationship_type": "HAS_RELATION",
      "role": "CEO",
      ...
    }
  ]
}
```

### 3.2 구현 함수

```python
def generate_static_graph(ticker: str, extracted_dir: Path) -> Dict:
    """
    Static 노드와 링크를 생성하여 반환
    
    Returns:
        {
            "ticker": str,
            "generated_at": str,
            "nodes": {
                "Company": List[Dict],
                "Product": List[Dict],
                "Person": List[Dict]
            },
            "links": List[Dict]
        }
    """
    # 1. Company 노드 생성
    company_node = generate_company_node(ticker)
    
    # 2. Product 노드 생성
    extracted_files = list(extracted_dir.rglob("*.json"))
    product_nodes = generate_product_nodes(ticker, extracted_files)
    
    # 3. Person 노드 생성
    person_nodes = generate_person_nodes(ticker, extracted_files)
    
    # 4. 링크 생성
    make_links = generate_make_links(company_node["id"], product_nodes)
    has_relation_links = generate_has_relation_links(
        company_node["id"], person_nodes, extracted_files
    )
    
    return {
        "ticker": ticker,
        "generated_at": datetime.utcnow().isoformat() + "Z",
        "nodes": {
            "Company": [company_node],
            "Product": product_nodes,
            "Person": person_nodes
        },
        "links": make_links + has_relation_links
    }
```

---

## 🔄 Phase 4: Dynamic Node 생성

### 4.1 Document Node 생성

**소스**: 각 extracted JSON 파일의 메타데이터

**규칙**:
- ID: `doc_{ticker}_{filing_type}_{accession_number}` (예: `doc_aapl_10k_0000320193-23-000106`)
- `parsed` 데이터에서 추가 메타데이터 가져오기 (필요시)

**스키마**:
```json
{
  "id": "doc_aapl_10k_0000320193-23-000106",
  "node_type": "Document",
  "accession_number": "0000320193-23-000106",
  "filing_type": "10-K",
  "ticker": "AAPL",
  "node_style": "dynamic",
  "filing_date": "2023-11-03",
  "period_end_date": "2023-09-30",
  "year": 2023,
  "quarter": null,
  "sections_included": ["business", "risk_factors"],
  "extracted_at": "2024-12-26T16:17:03Z",
  "metadata": {
    "extraction_stats": {
      "opportunities_count": 8,
      "risks_count": 9,
      "events_count": 4,
      "technologies_count": 6
    }
  }
}
```

**구현**:
- `generate_document_node(extracted_data: Dict, parsed_data: Dict = None) -> Dict`
- `parsed` 데이터가 있으면 `filing_date`, `period_end_date` 등 추가 정보 가져오기

### 4.2 Section Node 생성

**소스**: `extracted_data["sections_included"]`

**규칙**:
- ID: `section_{ticker}_{filing_type}_{year}_{section_name}` (예: `section_aapl_10k_2023_business`)
- `parsed` 데이터에서 `section_text`, `text_length` 가져오기

**스키마**:
```json
{
  "id": "section_aapl_10k_2023_business",
  "node_type": "Section",
  "section_name": "business",
  "filing_type": "10-K",
  "node_style": "dynamic",
  "ticker": "AAPL",
  "accession_number": "0000320193-23-000106",
  "section_text": "Item 1. Business\n\nGeneral\n\n...",
  "text_length": 45230,
  "parsed_at": "2024-12-26T10:00:00Z",
  "metadata": {
    "year": 2023,
    "quarter": null
  }
}
```

**구현**:
- `generate_section_nodes(extracted_data: Dict, parsed_data: Dict = None) -> List[Dict]`
- `sections_included` 배열을 순회하며 각 섹션 노드 생성
- `parsed` 데이터에서 해당 섹션의 텍스트 가져오기

### 4.3 Risk/Opportunity/Event/Technology Node 생성

**소스**: `extracted_data["risks"]`, `extracted_data["opportunities"]`, `extracted_data["events"]`, `extracted_data["technologies"]`

**규칙**:
- Risk ID: `risk_{ticker}_{normalized_entity}_{year}` (예: `risk_aapl_intense_competition_2023`)
- Opportunity ID: `opp_{ticker}_{normalized_entity}_{year}`
- Event ID: `event_{ticker}_{normalized_entity}_{year}`
- Technology ID: `tech_{ticker}_{normalized_entity}_{year}` (예: `tech_aapl_a17_pro_chip_2023`)
- `normalized_entity`: 소문자, 공백/특수문자 → 언더스코어
- `description_embedding`: 생성 (나중에 Vector DB에 저장)

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
  "extracted_at": "2024-12-26T16:17:03Z",
  "metadata": {
    "source_section": "business",
    "filing_type": "10-K",
    "accession_number": "0000320193-23-000106"
  }
}
```

**스키마 (Technology 예시)**:
```json
{
  "id": "tech_aapl_a17_pro_chip_2023",
  "node_type": "Technology",
  "ticker": "AAPL",
  "entity": "A17 Pro Chip Technology",
  "description": "The A17 Pro chip represents Apple's latest advancement in semiconductor technology...",
  "description_embedding": [0.0123, -0.0456, ...],
  "node_style": "dynamic",
  "extracted_at": "2024-12-26T16:17:03Z",
  "metadata": {
    "source_section": "business",
    "filing_type": "10-K",
    "accession_number": "0000320193-23-000106"
  }
}
```

**구현**:
- `generate_risk_nodes(extracted_data: Dict) -> List[Dict]`
- `generate_opportunity_nodes(extracted_data: Dict) -> List[Dict]`
- `generate_event_nodes(extracted_data: Dict) -> List[Dict]`
- `generate_technology_nodes(extracted_data: Dict) -> List[Dict]`
- `description_embedding`은 나중에 생성 (Phase 5에서 처리 가능)

---

## 🔗 Phase 5: Dynamic Node 간 Link 생성

### 5.1 IS_INCLUDED Link (Section → Document)

**규칙**:
- 각 Section 노드에 대해 해당 Document 노드와 `IS_INCLUDED` 링크 생성

**스키마**:
```json
{
  "from": "section_aapl_10k_2023_business",
  "to": "doc_aapl_10k_0000320193-23-000106",
  "relationship_type": "IS_INCLUDED",
  "created_at": "2024-12-28T00:00:00Z",
  "metadata": {
    "section_order": 1
  }
}
```

### 5.2 IS_EXTRACTED_FROM Link (Risk/Opportunity/Event/Technology → Section)

**규칙**:
- 각 Risk/Opportunity/Event/Technology 노드에 대해 해당 Section 노드와 `IS_EXTRACTED_FROM` 링크 생성
- `metadata.source_section`을 사용하여 Section 노드 찾기

**스키마**:
```json
{
  "from": "risk_aapl_intense_competition_2023",
  "to": "section_aapl_10k_2023_business",
  "relationship_type": "IS_EXTRACTED_FROM",
  "created_at": "2024-12-28T00:00:00Z",
  "metadata": {
    "extraction_method": "llm_extraction",
    "confidence": 0.95
  }
}
```

### 5.3 HAS_RISKS/HAS_OPPORTUNITIES/HAS_EVENTS/HAS_TECHNOLOGIES Link (Company → Risk/Opportunity/Event/Technology)

**규칙**:
- 각 Risk/Opportunity/Event/Technology 노드에 대해 Company 노드와 링크 생성

**스키마 (HAS_RISKS 예시)**:
```json
{
  "from": "AAPL",
  "to": "risk_aapl_intense_competition_2023",
  "relationship_type": "HAS_RISKS",
  "created_at": "2024-12-28T00:00:00Z",
  "metadata": {
    "first_mentioned": "2023-01-01",
    "last_mentioned": "2023-11-03"
  }
}
```

**스키마 (HAS_TECHNOLOGIES 예시)**:
```json
{
  "from": "AAPL",
  "to": "tech_aapl_a17_pro_chip_2023",
  "relationship_type": "HAS_TECHNOLOGIES",
  "created_at": "2024-12-28T00:00:00Z",
  "metadata": {
    "first_mentioned": "2023-01-01",
    "last_mentioned": "2023-11-03"
  }
}
```

---

## 🔗 Phase 6: Static-Dynamic 간 Link 생성

### 6.1 IS_MENTIONED_IN Link (Product/Person/Company → Risk/Opportunity/Event/Technology)

**소스**: 각 Risk/Opportunity/Event/Technology의 `mentioned_products`, `mentioned_persons`, `mentioned_companies`

**규칙**:
- 각 Risk/Opportunity/Event/Technology 노드의 `mentioned_products`를 순회하며 Product 노드와 `IS_MENTIONED_IN` 링크 생성
- 각 Risk/Opportunity/Event/Technology 노드의 `mentioned_persons`를 순회하며 Person 노드와 `IS_MENTIONED_IN` 링크 생성
- 각 Risk/Opportunity/Event/Technology 노드의 `mentioned_companies`를 순회하며 Company 노드와 `IS_MENTIONED_IN` 링크 생성
- **필수**: `mention_context` 속성 포함

**스키마 (Product → Event 예시)**:
```json
{
  "from": "product_aapl_iphone",
  "to": "event_aapl_iphone15_2023",
  "relationship_type": "IS_MENTIONED_IN",
  "mention_context": "iPhone 15 was launched as part of the company's product lineup",
  "created_at": "2024-12-28T00:00:00Z",
  "metadata": {
    "mention_type": "event"
  }
}
```

**스키마 (Person → Opportunity 예시)**:
```json
{
  "from": "person_aapl_tim_cook",
  "to": "opp_aapl_ecosystem_2023",
  "relationship_type": "IS_MENTIONED_IN",
  "mention_context": "Tim Cook discussed the integrated ecosystem strategy during the earnings call",
  "created_at": "2024-12-28T00:00:00Z",
  "metadata": {
    "mention_type": "opportunity"
  }
}
```

**스키마 (Company → Risk 예시)**:
```json
{
  "from": "SSNLF",
  "to": "risk_aapl_intense_competition_2023",
  "relationship_type": "IS_MENTIONED_IN",
  "mention_context": "Samsung Electronics is mentioned as a key competitor in the smartphone market",
  "created_at": "2024-12-28T00:00:00Z",
  "metadata": {
    "mention_type": "risk"
  }
}
```

**구현**:
- `generate_is_mentioned_in_links(
    dynamic_nodes: List[Dict],
    static_nodes: Dict,
    extracted_data: Dict
) -> List[Dict]`
- 각 Risk/Opportunity/Event/Technology 노드의 `mentioned_products`, `mentioned_persons`, `mentioned_companies`를 확인
- Static 노드 ID와 매칭하여 링크 생성
- `mention_context` 추출 방법:
  - 각 `mentioned_products`/`mentioned_persons`/`mentioned_companies` 배열의 각 항목에서 `mention_context` 필드를 읽어옴
  - extracted 데이터 구조: `risks[i].mentioned_products[j].mention_context` 형태
  - `mention_context`가 없는 경우, 해당 엔티티의 `description`에서 관련 문장을 추출하거나 빈 문자열 사용
  - 링크 생성 시 `mention_context`를 필수 속성으로 포함

---

## 📊 Phase 7: Dynamic Graph 파일 저장

### 7.1 파일 구조

**파일명**: `{TICKER}_dynamic_graph.json`

**구조**:
```json
{
  "ticker": "AAPL",
  "generated_at": "2024-12-28T00:00:00Z",
  "nodes": {
    "Document": [
      {
        "id": "doc_aapl_10k_0000320193-23-000106",
        "node_type": "Document",
        ...
      }
    ],
    "Section": [
      {
        "id": "section_aapl_10k_2023_business",
        "node_type": "Section",
        ...
      }
    ],
    "Risk": [
      {
        "id": "risk_aapl_intense_competition_2023",
        "node_type": "Risk",
        ...
      }
    ],
    "Opportunity": [
      {
        "id": "opp_aapl_ecosystem_2023",
        "node_type": "Opportunity",
        ...
      }
    ],
    "Event": [
      {
        "id": "event_aapl_iphone15_2023",
        "node_type": "Event",
        ...
      }
    ],
    "Technology": [
      {
        "id": "tech_aapl_a17_pro_chip_2023",
        "node_type": "Technology",
        ...
      }
    ]
  },
  "links": [
    {
      "from": "section_aapl_10k_2023_business",
      "to": "doc_aapl_10k_0000320193-23-000106",
      "relationship_type": "IS_INCLUDED",
      ...
    },
    {
      "from": "risk_aapl_intense_competition_2023",
      "to": "section_aapl_10k_2023_business",
      "relationship_type": "IS_EXTRACTED_FROM",
      ...
    },
    {
      "from": "AAPL",
      "to": "risk_aapl_intense_competition_2023",
      "relationship_type": "HAS_RISKS",
      ...
    },
    {
      "from": "product_aapl_iphone",
      "to": "event_aapl_iphone15_2023",
      "relationship_type": "IS_MENTIONED_IN",
      "mention_context": "...",
      ...
    }
  ]
}
```

### 7.2 구현 함수

```python
def generate_dynamic_graph(
    ticker: str,
    extracted_files: List[Path],
    static_graph: Dict
) -> Dict:
    """
    Dynamic 노드와 링크를 생성하여 반환
    
    Args:
        ticker: 티커 심볼
        extracted_files: extracted JSON 파일 경로 리스트
        static_graph: Static graph 데이터 (Product/Person 노드 ID 참조용)
    
    Returns:
        {
            "ticker": str,
            "generated_at": str,
            "nodes": {
                "Document": List[Dict],
                "Section": List[Dict],
                "Risk": List[Dict],
                "Opportunity": List[Dict],
                "Event": List[Dict],
                "Technology": List[Dict]
            },
            "links": List[Dict]
        }
    """
    all_nodes = {
        "Document": [],
        "Section": [],
        "Risk": [],
        "Opportunity": [],
        "Event": [],
        "Technology": []
    }
    all_links = []
    
    for extracted_file in extracted_files:
        extracted_data = json.load(open(extracted_file))
        parsed_data = load_parsed_data(extracted_data)  # 필요시
        
        # Document 노드 생성
        doc_node = generate_document_node(extracted_data, parsed_data)
        all_nodes["Document"].append(doc_node)
        
        # Section 노드 생성
        section_nodes = generate_section_nodes(extracted_data, parsed_data)
        all_nodes["Section"].extend(section_nodes)
        
        # Risk/Opportunity/Event/Technology 노드 생성
        risk_nodes = generate_risk_nodes(extracted_data)
        opp_nodes = generate_opportunity_nodes(extracted_data)
        event_nodes = generate_event_nodes(extracted_data)
        tech_nodes = generate_technology_nodes(extracted_data)
        all_nodes["Risk"].extend(risk_nodes)
        all_nodes["Opportunity"].extend(opp_nodes)
        all_nodes["Event"].extend(event_nodes)
        all_nodes["Technology"].extend(tech_nodes)
        
        # Dynamic 노드 간 링크 생성
        all_links.extend(generate_is_included_links(section_nodes, doc_node))
        all_links.extend(generate_is_extracted_from_links(
            risk_nodes + opp_nodes + event_nodes + tech_nodes, section_nodes
        ))
        
        # Company → Risk/Opportunity/Event/Technology 링크 생성
        all_links.extend(generate_has_risks_links(ticker, risk_nodes))
        all_links.extend(generate_has_opportunities_links(ticker, opp_nodes))
        all_links.extend(generate_has_events_links(ticker, event_nodes))
        all_links.extend(generate_has_technologies_links(ticker, tech_nodes))
        
        # Static-Dynamic 간 링크 생성
        all_links.extend(generate_is_mentioned_in_links(
            risk_nodes + opp_nodes + event_nodes + tech_nodes,
            static_graph["nodes"],
            extracted_data
        ))
    
    return {
        "ticker": ticker,
        "generated_at": datetime.utcnow().isoformat() + "Z",
        "nodes": all_nodes,
        "links": all_links
    }
```

---

## 🚀 Phase 8: 메인 실행 스크립트

### 8.1 스크립트 구조

**파일**: `scripts/04_generate_graph_data.py`

**기능**:
1. `data/extracted/{TICKER}/**/*.json` 파일들을 읽어서
2. Static graph 생성 및 저장
3. Dynamic graph 생성 및 저장

**구현**:
```python
def main():
    tickers = ["AAPL"]  # 또는 모든 티커
    
    for ticker in tickers:
        extracted_dir = Path(f"data/extracted/{ticker}")
        
        # 1. Static graph 생성
        static_graph = generate_static_graph(ticker, extracted_dir)
        static_path = Path(f"data/graph/{ticker}_static_graph.json")
        static_path.parent.mkdir(parents=True, exist_ok=True)
        json.dump(static_graph, open(static_path, "w"), indent=2, ensure_ascii=False)
        
        # 2. Dynamic graph 생성
        extracted_files = list(extracted_dir.rglob("*.json"))
        dynamic_graph = generate_dynamic_graph(ticker, extracted_files, static_graph)
        dynamic_path = Path(f"data/graph/{ticker}_dynamic_graph.json")
        json.dump(dynamic_graph, open(dynamic_path, "w"), indent=2, ensure_ascii=False)
        
        print(f"✅ {ticker}: Static={len(static_graph['nodes'])} nodes, "
              f"Dynamic={sum(len(v) for v in dynamic_graph['nodes'].values())} nodes")
```

---

## 📋 구현 체크리스트

### Phase 1: Static Node 생성
- [ ] `generate_company_node()` 구현
- [ ] `generate_product_nodes()` 구현
- [ ] `generate_person_nodes()` 구현
- [ ] ID 정규화 함수 구현 (`normalize_id()`)
- [ ] Product 분류 로직 구현 (product_type, category)

### Phase 2: Static Link 생성
- [ ] `generate_make_links()` 구현
- [ ] `generate_has_relation_links()` 구현

### Phase 3: Static Graph 저장
- [ ] `generate_static_graph()` 구현
- [ ] JSON 파일 저장 로직 구현

### Phase 4: Dynamic Node 생성
- [ ] `generate_document_node()` 구현
- [ ] `generate_section_nodes()` 구현
- [ ] `generate_risk_nodes()` 구현
- [ ] `generate_opportunity_nodes()` 구현
- [ ] `generate_event_nodes()` 구현
- [ ] `generate_technology_nodes()` 구현
- [ ] Event 날짜 파싱 로직 구현
- [ ] Event 타입 분류 로직 구현

### Phase 5: Dynamic Link 생성
- [ ] `generate_is_included_links()` 구현
- [ ] `generate_is_extracted_from_links()` 구현
- [ ] `generate_has_risks_links()` 구현
- [ ] `generate_has_opportunities_links()` 구현
- [ ] `generate_has_events_links()` 구현
- [ ] `generate_has_technologies_links()` 구현

### Phase 6: Static-Dynamic Link 생성
- [ ] `generate_is_mentioned_in_links()` 구현
- [ ] Product/Person/Company 노드 ID 매칭 로직 구현
- [ ] `mention_context` 추출 및 저장

### Phase 7: Dynamic Graph 저장
- [ ] `generate_dynamic_graph()` 구현
- [ ] JSON 파일 저장 로직 구현

### Phase 8: 메인 스크립트
- [ ] `scripts/04_generate_graph_data.py` 구현
- [ ] 배치 처리 로직 구현
- [ ] 로깅 및 에러 처리

---

## 🔍 검증 및 테스트

### 테스트 케이스

1. **Static Graph 검증**:
   - Company 노드 1개 존재 확인
   - Product 노드 중복 제거 확인
   - Person 노드 중복 제거 확인
   - MAKE 링크가 모든 Product에 대해 생성되었는지 확인
   - HAS_RELATION 링크가 모든 Person에 대해 생성되었는지 확인

2. **Dynamic Graph 검증**:
   - Document 노드가 모든 extracted 파일에 대해 생성되었는지 확인
   - Section 노드가 `sections_included`에 대해 생성되었는지 확인
   - Risk/Opportunity/Event/Technology 노드가 extracted 데이터와 일치하는지 확인
   - 모든 링크가 올바른 노드 ID를 참조하는지 확인

3. **링크 검증**:
   - IS_MENTIONED_IN 링크에 `mention_context` 속성이 포함되었는지 확인
   - 모든 링크의 `from`, `to` 노드가 실제로 존재하는지 확인

---

## 📝 다음 단계 (Phase 5: Graph DB 적재)

생성된 `{TICKER}_static_graph.json`과 `{TICKER}_dynamic_graph.json` 파일을 읽어서:
1. Cypher 쿼리 생성
2. FalkorDB에 노드 및 링크 적재
3. Vector DB에 embedding 저장

이는 별도의 Phase 5에서 처리합니다.

---

## 🎯 요약

이 계획은 `extracted` 데이터를 `graph_ontology_design.md` 스키마에 맞게 변환하여:
- **Static Graph**: Company, Product, Person 노드 및 이들 간의 링크
- **Dynamic Graph**: Risk, Opportunity, Event, Technology, Section, Document 노드 및 모든 링크

를 생성하고 JSON 파일로 저장합니다. 이후 이 파일들을 읽어서 Graph DB로 적재할 수 있습니다.

**주요 변경사항**:
- Technology 노드 추가 (Risk/Opportunity/Event와 동일한 구조)
- HAS_TECHNOLOGIES 링크 추가 (Company → Technology)
- IS_EXTRACTED_FROM 링크에 Technology 포함
- IS_MENTIONED_IN 링크에 Technology 포함
- Product 노드의 name은 고유명사여야 함 (예: "Tesla Model 3", "iPhone 15 Pro")

