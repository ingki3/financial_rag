# Phase 5: Dynamic Node 간 Link 생성 상세 구현 방안

## 📌 목적

Phase 4에서 생성된 Dynamic 노드들 (Document, Section, Risk, Opportunity, Event, Technology) 간의 관계를 링크로 생성합니다. 이 링크들은 Graph DB 적재 시 Cypher 쿼리로 변환되어 사용됩니다.

---

## 📊 입력 데이터 구조 분석

### Extracted 데이터 구조

```json
{
  "ticker": "AAPL",
  "filing_type": "10-K",
  "accession_number": "0000320193-23-000106",
  "sections_included": ["business", "risk_factors"],
  "year": 2023,
  "quarter": null,
  "extracted_at": "2024-12-26T16:17:03Z",
  "risks": [
    {
      "entity": "Intense Price Competition",
      "description": "The Company faces aggressive price competition...",
      "mentioned_products": [],
      "mentioned_persons": [],
      "mentioned_companies": [],
      "source_section": "business",
      "extracted_at": "2024-12-26T16:17:03Z"
    }
  ],
  "opportunities": [...],
  "events": [...],
  "technologies": [...],
  "extraction_stats": {
    "opportunities_count": 8,
    "risks_count": 9,
    "events_count": 4,
    "technologies_count": 6
  }
}
```

### Phase 4에서 생성된 노드 구조

**Document Node:**
```json
{
  "id": "doc_aapl_10k_0000320193-23-000106",
  "node_type": "Document",
  "ticker": "AAPL",
  "filing_type": "10-K",
  "year": 2023,
  "accession_number": "0000320193-23-000106"
}
```

**Section Node:**
```json
{
  "id": "section_aapl_10k_2023_business",
  "node_type": "Section",
  "section_name": "business",
  "filing_type": "10-K",
  "ticker": "AAPL",
  "year": 2023,
  "accession_number": "0000320193-23-000106"
}
```

**Risk/Opportunity/Event/Technology Node:**
```json
{
  "id": "risk_aapl_intense_competition_2023",
  "node_type": "Risk",
  "ticker": "AAPL",
  "entity": "Intense Price Competition",
  "metadata": {
    "source_section": "business",
    "filing_type": "10-K",
    "accession_number": "0000320193-23-000106"
  }
}
```

---

## 🔗 5.1 IS_INCLUDED Link (Section → Document)

### 목적
Section 노드가 어떤 Document 노드에 포함되는지 연결합니다.

### 입력 데이터
- `section_nodes`: Phase 4에서 생성된 Section 노드 리스트
- `doc_node`: Phase 4에서 생성된 Document 노드 (단일 노드)

### 노드 ID 매칭 규칙

**Section ID 형식:**
```
section_{ticker}_{filing_type_lower}_{year}_{section_name}
```
- 예: `section_aapl_10k_2023_business`
- `filing_type_lower`: "10-K" → "10k", "10-Q" → "10q", "8-K" → "8k"

**Document ID 형식:**
```
doc_{ticker}_{filing_type_lower}_{accession_number}
```
- 예: `doc_aapl_10k_0000320193-23-000106`
- **중요**: 현재 프로젝트의 Document ID는 `accession_number`의 하이픈(`-`)을 **그대로 유지**합니다. (예: `0000320193-23-000106`)

### 링크 생성 로직

```python
def generate_is_included_links(
    section_nodes: List[Dict],
    doc_node: Dict
) -> List[Dict]:
    """
    Section → Document 간 IS_INCLUDED 링크 생성
    
    Args:
        section_nodes: Section 노드 리스트
        doc_node: Document 노드 (단일)
    
    Returns:
        IS_INCLUDED 링크 리스트
    """
    links = []
    doc_id = doc_node["id"]
    created_at = datetime.utcnow().isoformat() + "Z"
    
    # sections_included 배열의 순서를 section_order로 사용
    sections_included = doc_node.get("sections_included", [])
    
    for idx, section_node in enumerate(section_nodes):
        section_id = section_node["id"]
        section_name = section_node["section_name"]
        
        # section_order 계산: sections_included 배열에서의 인덱스 (1-base)
        section_order = (
            sections_included.index(section_name) + 1
            if section_name in sections_included
            else idx + 1
        )
        
        link = {
            "from": section_id,
            "to": doc_id,
            "relationship_type": "IS_INCLUDED",
            "created_at": created_at,
            "metadata": {
                "section_order": section_order
            }
        }
        links.append(link)
    
    return links
```

### 메타데이터 추출

- **section_order**: `doc_node["sections_included"]` 배열에서의 인덱스 + 1 (즉 1부터 시작)
- **created_at**: 현재 UTC 시간 (ISO 8601 형식)

### 예외 처리

1. **Section 노드가 Document의 sections_included에 없는 경우**
   - `section_order`를 배열 인덱스 + 1로 설정
   - 경고 로그 출력

2. **Document 노드에 sections_included가 없는 경우**
   - `section_order`를 순차적으로 1, 2, 3... 으로 설정

### 검증 규칙

- 모든 Section 노드의 `ticker`, `filing_type`, `metadata.year`(또는 구현체에 따라 `year`), `accession_number`가 Document 노드와 일치해야 함
- Section 노드의 `id`가 올바른 형식인지 확인

### 예시 출력

```json
[
  {
    "from": "section_aapl_10k_2023_business",
    "to": "doc_aapl_10k_0000320193-23-000106",
    "relationship_type": "IS_INCLUDED",
    "created_at": "2024-12-28T00:00:00Z",
    "metadata": {
      "section_order": 1
    }
  },
  {
    "from": "section_aapl_10k_2023_risk_factors",
    "to": "doc_aapl_10k_0000320193-23-000106",
    "relationship_type": "IS_INCLUDED",
    "created_at": "2024-12-28T00:00:00Z",
    "metadata": {
      "section_order": 2
    }
  }
]
```

---

## 🔗 5.2 IS_EXTRACTED_FROM Link (Risk/Opportunity/Event/Technology → Section)

### 목적
추출된 엔티티(Risk/Opportunity/Event/Technology)가 어떤 Section에서 추출되었는지 추적합니다.

### 입력 데이터
- `dynamic_nodes`: Risk/Opportunity/Event/Technology 노드 리스트
- `section_nodes`: Section 노드 리스트

### 노드 ID 매칭 규칙

**Dynamic Node ID 형식:**
- Risk: `risk_{ticker}_{normalized_entity}_{year}`
- Opportunity: `opp_{ticker}_{normalized_entity}_{year}`
- Event: `event_{ticker}_{normalized_entity}_{year}`
- Technology: `tech_{ticker}_{normalized_entity}_{year}`

**Section ID 형식:**
```
section_{ticker}_{filing_type_lower}_{year}_{section_name}
```

**매칭 키:**
- Dynamic Node의 `metadata.source_section`과 Section Node의 `section_name` 매칭
- Dynamic Node의 `ticker`, `metadata.filing_type`, `year`, `metadata.accession_number`와 Section Node의 동일 필드 매칭

**중요 (year 처리)**:
- Dynamic Node에는 `year` 필드가 항상 존재하지 않을 수 있으므로, 다음 우선순위로 `year`를 확보합니다.
  1. Dynamic Node의 `id` 접미사 `_YYYY` 파싱 (예: `risk_aapl_xxx_2023` → 2023)
  2. `extracted_data["year"]` (available in extracted JSON top-level)
  3. `doc_node["year"]` (Phase 4 Document node)

### 링크 생성 로직

```python
def generate_is_extracted_from_links(
    dynamic_nodes: List[Dict],
    section_nodes: List[Dict],
    extracted_data: Dict = None,
    doc_node: Dict = None,
) -> List[Dict]:
    """
    Risk/Opportunity/Event/Technology → Section 간 IS_EXTRACTED_FROM 링크 생성
    
    Args:
        dynamic_nodes: Risk/Opportunity/Event/Technology 노드 리스트
        section_nodes: Section 노드 리스트
    
    Returns:
        IS_EXTRACTED_FROM 링크 리스트
    """
    links = []
    created_at = datetime.utcnow().isoformat() + "Z"
    
    # Section 노드를 매칭 키로 인덱싱
    section_map = {}
    for section_node in section_nodes:
        section_year = (
            section_node.get("metadata", {}).get("year")
            if isinstance(section_node.get("metadata"), dict)
            else None
        ) or section_node.get("year")
        key = (
            section_node["ticker"],
            section_node["filing_type"],
            section_year,
            section_node["section_name"],
            section_node.get("accession_number")
        )
        section_map[key] = section_node

    def _year_from_dynamic_id(dynamic_id: str) -> int | None:
        # expected suffix: _YYYY
        try:
            maybe_year = dynamic_id.rsplit("_", 1)[-1]
            return int(maybe_year) if (len(maybe_year) == 4 and maybe_year.isdigit()) else None
        except Exception:
            return None
    
    for dynamic_node in dynamic_nodes:
        dynamic_id = dynamic_node["id"]
        metadata = dynamic_node.get("metadata", {})
        source_section = metadata.get("source_section")
        
        if not source_section:
            logging.warning(f"Dynamic node {dynamic_id} has no source_section")
            continue
        
        # Section 노드 찾기
        dyn_year = (
            _year_from_dynamic_id(dynamic_id)
            or (extracted_data.get("year") if isinstance(extracted_data, dict) else None)
            or (doc_node.get("year") if isinstance(doc_node, dict) else None)
        )
        key = (
            dynamic_node["ticker"],
            metadata.get("filing_type"),
            dyn_year,
            source_section,
            metadata.get("accession_number")
        )
        
        section_node = section_map.get(key)
        if not section_node:
            logging.warning(
                f"Section node not found for dynamic node {dynamic_id}: "
                f"ticker={dynamic_node['ticker']}, "
                f"filing_type={metadata.get('filing_type')}, "
                f"year={dynamic_node.get('year')}, "
                f"source_section={source_section}"
            )
            continue
        
        section_id = section_node["id"]
        
        link = {
            "from": dynamic_id,
            "to": section_id,
            "relationship_type": "IS_EXTRACTED_FROM",
            "created_at": created_at,
            "metadata": {
                "extraction_method": "llm_extraction",
                "confidence": 0.95  # 기본값, 추후 실제 confidence 계산 가능
            }
        }
        links.append(link)
    
    return links
```

### 메타데이터 추출

- **extraction_method**: 항상 "llm_extraction" (현재는 LLM 기반 추출만 사용)
- **confidence**: 기본값 0.95 (추후 실제 confidence 점수 계산 가능)

### 예외 처리

1. **source_section이 없는 경우**
   - 경고 로그 출력 후 해당 노드 스킵

2. **매칭되는 Section 노드가 없는 경우**
   - 경고 로그 출력 후 해당 노드 스킵
   - 매칭 키 정보를 로그에 포함

3. **ticker, filing_type, year, accession_number 불일치**
   - 경고 로그 출력 후 해당 노드 스킵

### 검증 규칙

- Dynamic Node의 `metadata.source_section`이 Section Node의 `section_name`과 일치해야 함
- Dynamic Node와 Section Node의 `ticker`, `filing_type`, `year`, `accession_number`가 일치해야 함

### 예시 출력

```json
[
  {
    "from": "risk_aapl_intense_competition_2023",
    "to": "section_aapl_10k_2023_business",
    "relationship_type": "IS_EXTRACTED_FROM",
    "created_at": "2024-12-28T00:00:00Z",
    "metadata": {
      "extraction_method": "llm_extraction",
      "confidence": 0.95
    }
  },
  {
    "from": "opp_aapl_ecosystem_2023",
    "to": "section_aapl_10k_2023_risk_factors",
    "relationship_type": "IS_EXTRACTED_FROM",
    "created_at": "2024-12-28T00:00:00Z",
    "metadata": {
      "extraction_method": "llm_extraction",
      "confidence": 0.95
    }
  },
  {
    "from": "tech_aapl_a17_pro_chip_2023",
    "to": "section_aapl_10k_2023_business",
    "relationship_type": "IS_EXTRACTED_FROM",
    "created_at": "2024-12-28T00:00:00Z",
    "metadata": {
      "extraction_method": "llm_extraction",
      "confidence": 0.95
    }
  }
]
```

---

## 🔗 5.3 HAS_RISKS/HAS_OPPORTUNITIES/HAS_EVENTS/HAS_TECHNOLOGIES Link (Company → Risk/Opportunity/Event/Technology)

### 목적
회사가 어떤 위험/기회/이벤트/기술을 보유하는지 연결합니다.

### 입력 데이터
- `ticker`: 회사 티커 심볼 (예: "AAPL")
- `dynamic_nodes`: Risk/Opportunity/Event/Technology 노드 리스트
- `extracted_data`: Extracted 데이터 (날짜 정보 추출용, 선택사항)

### 노드 ID 매칭 규칙

**Company ID:**
- `{ticker}` (예: "AAPL")

**Dynamic Node ID:**
- Risk: `risk_{ticker}_{normalized_entity}_{year}`
- Opportunity: `opp_{ticker}_{normalized_entity}_{year}`
- Event: `event_{ticker}_{normalized_entity}_{year}`
- Technology: `tech_{ticker}_{normalized_entity}_{year}`

**매칭 키:**
- Dynamic Node의 `ticker`가 Company의 `ticker`와 일치해야 함

### 링크 생성 로직

#### 5.3.1 HAS_RISKS Link

```python
def generate_has_risks_links(
    ticker: str,
    risk_nodes: List[Dict],
    extracted_data: Dict = None
) -> List[Dict]:
    """
    Company → Risk 간 HAS_RISKS 링크 생성
    
    Args:
        ticker: 회사 티커 심볼
        risk_nodes: Risk 노드 리스트
        extracted_data: Extracted 데이터 (날짜 정보 추출용)
    
    Returns:
        HAS_RISKS 링크 리스트
    """
    links = []
    company_id = ticker.upper()
    created_at = datetime.utcnow().isoformat() + "Z"
    
    # extracted_data에서 날짜 정보 추출 (있는 경우)
    filing_date = extracted_data.get("filing_date") if extracted_data else None
    year = extracted_data.get("year") if extracted_data else None
    
    for risk_node in risk_nodes:
        # ticker 일치 확인
        if risk_node.get("ticker", "").upper() != company_id:
            logging.warning(
                f"Risk node {risk_node['id']} ticker mismatch: "
                f"expected {company_id}, got {risk_node.get('ticker')}"
            )
            continue
        
        risk_id = risk_node["id"]
        
        # 메타데이터 생성
        metadata = {}
        
        # first_mentioned: extracted_at 또는 filing_date 사용
        if risk_node.get("extracted_at"):
            metadata["first_mentioned"] = risk_node["extracted_at"][:10]  # YYYY-MM-DD
        elif filing_date:
            metadata["first_mentioned"] = filing_date
        elif year:
            metadata["first_mentioned"] = f"{year}-01-01"
        
        # last_mentioned: first_mentioned와 동일 (단일 문서 기준)
        if "first_mentioned" in metadata:
            metadata["last_mentioned"] = metadata["first_mentioned"]
        
        link = {
            "from": company_id,
            "to": risk_id,
            "relationship_type": "HAS_RISKS",
            "created_at": created_at,
            "metadata": metadata
        }
        links.append(link)
    
    return links
```

#### 5.3.2 HAS_OPPORTUNITIES Link

```python
def generate_has_opportunities_links(
    ticker: str,
    opp_nodes: List[Dict],
    extracted_data: Dict = None
) -> List[Dict]:
    """
    Company → Opportunity 간 HAS_OPPORTUNITIES 링크 생성
    
    Args:
        ticker: 회사 티커 심볼
        opp_nodes: Opportunity 노드 리스트
        extracted_data: Extracted 데이터 (날짜 정보 추출용)
    
    Returns:
        HAS_OPPORTUNITIES 링크 리스트
    """
    links = []
    company_id = ticker.upper()
    created_at = datetime.utcnow().isoformat() + "Z"
    
    filing_date = extracted_data.get("filing_date") if extracted_data else None
    year = extracted_data.get("year") if extracted_data else None
    
    for opp_node in opp_nodes:
        if opp_node.get("ticker", "").upper() != company_id:
            logging.warning(
                f"Opportunity node {opp_node['id']} ticker mismatch: "
                f"expected {company_id}, got {opp_node.get('ticker')}"
            )
            continue
        
        opp_id = opp_node["id"]
        
        metadata = {}
        if opp_node.get("extracted_at"):
            metadata["first_mentioned"] = opp_node["extracted_at"][:10]
        elif filing_date:
            metadata["first_mentioned"] = filing_date
        elif year:
            metadata["first_mentioned"] = f"{year}-01-01"
        
        if "first_mentioned" in metadata:
            metadata["last_mentioned"] = metadata["first_mentioned"]
        
        link = {
            "from": company_id,
            "to": opp_id,
            "relationship_type": "HAS_OPPORTUNITIES",
            "created_at": created_at,
            "metadata": metadata
        }
        links.append(link)
    
    return links
```

#### 5.3.3 HAS_EVENTS Link

```python
def generate_has_events_links(
    ticker: str,
    event_nodes: List[Dict],
    extracted_data: Dict = None
) -> List[Dict]:
    """
    Company → Event 간 HAS_EVENTS 링크 생성
    
    Args:
        ticker: 회사 티커 심볼
        event_nodes: Event 노드 리스트
        extracted_data: Extracted 데이터 (날짜 정보 추출용)
    
    Returns:
        HAS_EVENTS 링크 리스트
    """
    links = []
    company_id = ticker.upper()
    created_at = datetime.utcnow().isoformat() + "Z"
    
    filing_date = extracted_data.get("filing_date") if extracted_data else None
    year = extracted_data.get("year") if extracted_data else None
    
    for event_node in event_nodes:
        if event_node.get("ticker", "").upper() != company_id:
            logging.warning(
                f"Event node {event_node['id']} ticker mismatch: "
                f"expected {company_id}, got {event_node.get('ticker')}"
            )
            continue
        
        event_id = event_node["id"]
        
        metadata = {}
        
        # Event의 경우 event_date를 우선 사용
        if event_node.get("date_parsed"):
            event_date = event_node["date_parsed"]
            metadata["event_date"] = event_date
        elif event_node.get("date"):
            # date가 "2023" 형식인 경우
            date_str = event_node["date"]
            if len(date_str) == 4:
                metadata["event_date"] = f"{date_str}-01-01"
            else:
                metadata["event_date"] = date_str
        elif filing_date:
            metadata["event_date"] = filing_date
        elif year:
            metadata["event_date"] = f"{year}-01-01"
        
        link = {
            "from": company_id,
            "to": event_id,
            "relationship_type": "HAS_EVENTS",
            "created_at": created_at,
            "metadata": metadata
        }
        links.append(link)
    
    return links
```

#### 5.3.4 HAS_TECHNOLOGIES Link

```python
def generate_has_technologies_links(
    ticker: str,
    tech_nodes: List[Dict],
    extracted_data: Dict = None
) -> List[Dict]:
    """
    Company → Technology 간 HAS_TECHNOLOGIES 링크 생성
    
    Args:
        ticker: 회사 티커 심볼
        tech_nodes: Technology 노드 리스트
        extracted_data: Extracted 데이터 (날짜 정보 추출용)
    
    Returns:
        HAS_TECHNOLOGIES 링크 리스트
    """
    links = []
    company_id = ticker.upper()
    created_at = datetime.utcnow().isoformat() + "Z"
    
    filing_date = extracted_data.get("filing_date") if extracted_data else None
    year = extracted_data.get("year") if extracted_data else None
    
    for tech_node in tech_nodes:
        if tech_node.get("ticker", "").upper() != company_id:
            logging.warning(
                f"Technology node {tech_node['id']} ticker mismatch: "
                f"expected {company_id}, got {tech_node.get('ticker')}"
            )
            continue
        
        tech_id = tech_node["id"]
        
        metadata = {}
        if tech_node.get("extracted_at"):
            metadata["first_mentioned"] = tech_node["extracted_at"][:10]
        elif filing_date:
            metadata["first_mentioned"] = filing_date
        elif year:
            metadata["first_mentioned"] = f"{year}-01-01"
        
        if "first_mentioned" in metadata:
            metadata["last_mentioned"] = metadata["first_mentioned"]
        
        link = {
            "from": company_id,
            "to": tech_id,
            "relationship_type": "HAS_TECHNOLOGIES",
            "created_at": created_at,
            "metadata": metadata
        }
        links.append(link)
    
    return links
```

### 메타데이터 추출

#### HAS_RISKS/HAS_OPPORTUNITIES/HAS_TECHNOLOGIES
- **first_mentioned**: 우선순위
  1. Dynamic Node의 `extracted_at` (YYYY-MM-DD 형식으로 변환)
  2. `extracted_data["filing_date"]`
  3. `extracted_data["year"]` → `{year}-01-01`
- **last_mentioned**: `first_mentioned`와 동일 (단일 문서 기준)

#### HAS_EVENTS
- **event_date**: 우선순위
  1. Event Node의 `date_parsed` (ISO 8601 형식)
  2. Event Node의 `date` (파싱 필요: "2023" → "2023-01-01")
  3. `extracted_data["filing_date"]`
  4. `extracted_data["year"]` → `{year}-01-01`

### 예외 처리

1. **ticker 불일치**
   - 경고 로그 출력 후 해당 노드 스킵

2. **날짜 정보가 없는 경우**
   - `first_mentioned`/`event_date`를 생략하거나 기본값 사용
   - 경고 로그 출력

### 검증 규칙

- Dynamic Node의 `ticker`가 Company의 `ticker`와 일치해야 함
- 링크 타입이 노드 타입과 일치해야 함 (Risk → HAS_RISKS, Opportunity → HAS_OPPORTUNITIES 등)

### 예시 출력

```json
[
  {
    "from": "AAPL",
    "to": "risk_aapl_intense_competition_2023",
    "relationship_type": "HAS_RISKS",
    "created_at": "2024-12-28T00:00:00Z",
    "metadata": {
      "first_mentioned": "2023-11-03",
      "last_mentioned": "2023-11-03"
    }
  },
  {
    "from": "AAPL",
    "to": "opp_aapl_ecosystem_2023",
    "relationship_type": "HAS_OPPORTUNITIES",
    "created_at": "2024-12-28T00:00:00Z",
    "metadata": {
      "first_mentioned": "2023-11-03",
      "last_mentioned": "2023-11-03"
    }
  },
  {
    "from": "AAPL",
    "to": "event_aapl_iphone15_2023",
    "relationship_type": "HAS_EVENTS",
    "created_at": "2024-12-28T00:00:00Z",
    "metadata": {
      "event_date": "2023-09-01"
    }
  },
  {
    "from": "AAPL",
    "to": "tech_aapl_a17_pro_chip_2023",
    "relationship_type": "HAS_TECHNOLOGIES",
    "created_at": "2024-12-28T00:00:00Z",
    "metadata": {
      "first_mentioned": "2023-11-03",
      "last_mentioned": "2023-11-03"
    }
  }
]
```

---

## 🔧 통합 구현 함수

### generate_dynamic_links()

```python
from datetime import datetime
from typing import List, Dict
import logging

def generate_dynamic_links(
    ticker: str,
    doc_node: Dict,
    section_nodes: List[Dict],
    risk_nodes: List[Dict],
    opp_nodes: List[Dict],
    event_nodes: List[Dict],
    tech_nodes: List[Dict],
    extracted_data: Dict = None
) -> List[Dict]:
    """
    Phase 5: Dynamic Node 간 모든 링크 생성
    
    Args:
        ticker: 회사 티커 심볼
        doc_node: Document 노드
        section_nodes: Section 노드 리스트
        risk_nodes: Risk 노드 리스트
        opp_nodes: Opportunity 노드 리스트
        event_nodes: Event 노드 리스트
        tech_nodes: Technology 노드 리스트
        extracted_data: Extracted 데이터 (선택사항)
    
    Returns:
        모든 Dynamic 링크 리스트
    """
    all_links = []
    
    # 5.1: IS_INCLUDED (Section → Document)
    is_included_links = generate_is_included_links(section_nodes, doc_node)
    all_links.extend(is_included_links)
    logging.info(f"Generated {len(is_included_links)} IS_INCLUDED links")
    
    # 5.2: IS_EXTRACTED_FROM (Risk/Opp/Event/Tech → Section)
    dynamic_nodes = risk_nodes + opp_nodes + event_nodes + tech_nodes
    is_extracted_from_links = generate_is_extracted_from_links(
        dynamic_nodes, 
        section_nodes,
        extracted_data=extracted_data,
        doc_node=doc_node
    )
    all_links.extend(is_extracted_from_links)
    logging.info(f"Generated {len(is_extracted_from_links)} IS_EXTRACTED_FROM links")
    
    # 5.3: HAS_RISKS/HAS_OPPORTUNITIES/HAS_EVENTS/HAS_TECHNOLOGIES (Company → Dynamic)
    has_risks_links = generate_has_risks_links(ticker, risk_nodes, extracted_data)
    all_links.extend(has_risks_links)
    logging.info(f"Generated {len(has_risks_links)} HAS_RISKS links")
    
    has_opp_links = generate_has_opportunities_links(ticker, opp_nodes, extracted_data)
    all_links.extend(has_opp_links)
    logging.info(f"Generated {len(has_opp_links)} HAS_OPPORTUNITIES links")
    
    has_events_links = generate_has_events_links(ticker, event_nodes, extracted_data)
    all_links.extend(has_events_links)
    logging.info(f"Generated {len(has_events_links)} HAS_EVENTS links")
    
    has_tech_links = generate_has_technologies_links(ticker, tech_nodes, extracted_data)
    all_links.extend(has_tech_links)
    logging.info(f"Generated {len(has_tech_links)} HAS_TECHNOLOGIES links")
    
    return all_links
```

---

## 🧪 테스트 케이스

### 테스트 1: IS_INCLUDED Link 생성

**입력:**
- Section 노드: `section_aapl_10k_2023_business`, `section_aapl_10k_2023_risk_factors`
- Document 노드: `doc_aapl_10k_0000320193-23-000106` (sections_included: ["business", "risk_factors"])

**예상 출력:**
- 2개의 IS_INCLUDED 링크
- section_order: 1, 2

### 테스트 2: IS_EXTRACTED_FROM Link 생성

**입력:**
- Risk 노드: `risk_aapl_intense_competition_2023` (source_section: "business")
- Section 노드: `section_aapl_10k_2023_business`

**예상 출력:**
- 1개의 IS_EXTRACTED_FROM 링크
- extraction_method: "llm_extraction"

### 테스트 3: HAS_RISKS Link 생성

**입력:**
- Ticker: "AAPL"
- Risk 노드: `risk_aapl_intense_competition_2023` (ticker: "AAPL", extracted_at: "2024-12-26T16:17:03Z")

**예상 출력:**
- 1개의 HAS_RISKS 링크
- from: "AAPL", to: "risk_aapl_intense_competition_2023"
- first_mentioned: "2024-12-26"

### 테스트 4: HAS_EVENTS Link 생성 (event_date 포함)

**입력:**
- Ticker: "AAPL"
- Event 노드: `event_aapl_iphone15_2023` (date_parsed: "2023-09-01")

**예상 출력:**
- 1개의 HAS_EVENTS 링크
- metadata.event_date: "2023-09-01"

### 테스트 5: 예외 처리 (ticker 불일치)

**입력:**
- Ticker: "AAPL"
- Risk 노드: `risk_tsla_competition_2023` (ticker: "TSLA")

**예상 출력:**
- 경고 로그 출력
- 링크 생성 안 됨

---

## 📋 구현 체크리스트

### Phase 5.1: IS_INCLUDED Link
- [ ] `generate_is_included_links()` 함수 구현
- [ ] Section 노드와 Document 노드 ID 매칭 로직
- [ ] section_order 계산 로직
- [ ] 예외 처리 (sections_included 없음, 순서 불일치)
- [ ] 단위 테스트 작성

### Phase 5.2: IS_EXTRACTED_FROM Link
- [ ] `generate_is_extracted_from_links()` 함수 구현
- [ ] Dynamic Node와 Section Node 매칭 로직 (source_section 기반)
- [ ] 매칭 키 생성 로직 (ticker, filing_type, year, section_name, accession_number)
- [ ] 예외 처리 (source_section 없음, 매칭 실패)
- [ ] 단위 테스트 작성

### Phase 5.3: HAS_RISKS/HAS_OPPORTUNITIES/HAS_EVENTS/HAS_TECHNOLOGIES Link
- [ ] `generate_has_risks_links()` 함수 구현
- [ ] `generate_has_opportunities_links()` 함수 구현
- [ ] `generate_has_events_links()` 함수 구현
- [ ] `generate_has_technologies_links()` 함수 구현
- [ ] 날짜 메타데이터 추출 로직 (first_mentioned, event_date)
- [ ] 예외 처리 (ticker 불일치, 날짜 정보 없음)
- [ ] 단위 테스트 작성

### 통합
- [ ] `generate_dynamic_links()` 통합 함수 구현
- [ ] 로깅 추가
- [ ] 통합 테스트 작성
- [ ] 문서화

### Phase 5.4: Embedding 생성
- [ ] `generate_embeddings_for_nodes()` 함수 구현
- [ ] `generate_embeddings_batch()` 배치 처리 함수 구현
- [ ] Gemini Embedding API 연동
- [ ] Rate limiting 및 에러 처리
- [ ] Embedding 포함 노드 스키마 검증

### 유틸리티
- [ ] `normalize_filing_type()` 함수 구현 (10-K → 10k)
- [ ] ticker 대소문자 정규화 로직
- [ ] 날짜 형식 검증 유틸리티

---

---

## 🔢 Phase 5.4: Embedding 생성 (선택적, Vector DB 적재 시 필요)

### 목적
Risk/Opportunity/Event/Technology 노드의 `description` 텍스트를 벡터로 변환하여 `description_embedding` 필드에 저장합니다. 이는 Vector DB 기반 의미 검색에 사용됩니다.

### 대상 노드
- Risk, Opportunity, Event, Technology 노드

### 벡터화 대상 텍스트
| Node 타입 | 벡터화 대상 텍스트 | 용도 |
|-----------|------------------|------|
| **Risk** | `entity + description` | 위험 요소 의미 검색 |
| **Opportunity** | `entity + description` | 기회 요소 의미 검색 |
| **Event** | `entity + description + date` | 이벤트 의미 검색 |
| **Technology** | `entity + description` | 기술 의미 검색 |

### 임베딩 모델
- **Gemini Embedding API**: `embedding-001` 또는 `text-embedding-004`
- 벡터 차원: 768 또는 모델에 따라 다름

### 구현 로직

```python
from typing import List, Dict
import google.generativeai as genai

async def generate_embeddings_for_nodes(
    nodes: List[Dict],
    api_key: str,
    model_name: str = "models/text-embedding-004"
) -> List[Dict]:
    """
    Dynamic 노드들에 description_embedding 필드 추가
    
    Args:
        nodes: Risk/Opportunity/Event/Technology 노드 리스트
        api_key: Gemini API 키
        model_name: 임베딩 모델 이름
    
    Returns:
        embedding이 추가된 노드 리스트
    """
    genai.configure(api_key=api_key)
    
    for node in nodes:
        # 벡터화 대상 텍스트 생성
        entity = node.get("entity", "")
        description = node.get("description", "")
        date = node.get("date", "") or node.get("date_parsed", "")
        
        # Event의 경우 date 포함
        if node.get("node_type") == "Event" and date:
            text_to_embed = f"{entity} {description} Date: {date}"
        else:
            text_to_embed = f"{entity} {description}"
        
        # Embedding 생성
        try:
            result = genai.embed_content(
                model=model_name,
                content=text_to_embed,
                task_type="retrieval_document"
            )
            node["description_embedding"] = result["embedding"]
        except Exception as e:
            logging.warning(f"Embedding failed for node {node.get('id')}: {e}")
            node["description_embedding"] = None
    
    return nodes
```

### 배치 처리 (권장)

대량의 노드를 처리할 때는 배치로 처리하여 API 호출을 최적화합니다:

```python
async def generate_embeddings_batch(
    nodes: List[Dict],
    api_key: str,
    batch_size: int = 100,
    model_name: str = "models/text-embedding-004"
) -> List[Dict]:
    """
    배치 단위로 embedding 생성
    """
    genai.configure(api_key=api_key)
    
    for i in range(0, len(nodes), batch_size):
        batch = nodes[i:i + batch_size]
        
        texts = []
        for node in batch:
            entity = node.get("entity", "")
            description = node.get("description", "")
            date = node.get("date", "") or node.get("date_parsed", "")
            
            if node.get("node_type") == "Event" and date:
                texts.append(f"{entity} {description} Date: {date}")
            else:
                texts.append(f"{entity} {description}")
        
        try:
            # 배치 임베딩 요청
            result = genai.embed_content(
                model=model_name,
                content=texts,
                task_type="retrieval_document"
            )
            
            embeddings = result["embedding"]
            for j, node in enumerate(batch):
                node["description_embedding"] = embeddings[j]
                
        except Exception as e:
            logging.error(f"Batch embedding failed: {e}")
            for node in batch:
                node["description_embedding"] = None
        
        # Rate limiting
        await asyncio.sleep(0.1)
    
    return nodes
```

### 노드 스키마 (Embedding 포함)

```json
{
  "id": "risk_aapl_intense_competition_2023",
  "node_type": "Risk",
  "ticker": "AAPL",
  "entity": "Intense Price Competition",
  "description": "The Company faces aggressive price competition...",
  "description_embedding": [0.0123, -0.0456, 0.0789, ...],
  "node_style": "dynamic",
  "extracted_at": "2024-12-26T16:17:03Z",
  "metadata": {
    "source_section": "business",
    "filing_type": "10-K",
    "accession_number": "0000320193-23-000106"
  }
}
```

### Embedding 생성 시점

**옵션 1: Phase 5에서 생성 (권장)**
- Dynamic 노드 생성 직후, 링크 생성 전에 Embedding 추가
- 장점: 노드 데이터가 완전한 상태로 저장됨

**옵션 2: Graph DB 적재 시 생성**
- FalkorDB 적재 직전에 Embedding 생성
- 장점: 필요한 시점에만 생성하여 비용 절감

### 체크리스트

- [ ] `generate_embeddings_for_nodes()` 함수 구현
- [ ] 배치 처리 로직 구현
- [ ] Rate limiting 처리
- [ ] 에러 처리 및 재시도 로직
- [ ] 테스트 (단일 노드, 배치 노드)

---

## ⚠️ 구현 시 주의사항

### 1. filing_type 소문자 변환

Section ID와 Document ID 생성 시 `filing_type`을 소문자로 변환해야 합니다:

```python
def normalize_filing_type(filing_type: str) -> str:
    """10-K → 10k, 10-Q → 10q, 8-K → 8k"""
    return filing_type.lower().replace("-", "")

# 예시
# section_aapl_10k_2023_business (O)
# section_aapl_10-K_2023_business (X)
```

### 2. 통합 함수 호출 시 파라미터 전달

`generate_dynamic_links()` 호출 시 `extracted_data`와 `doc_node`를 `generate_is_extracted_from_links()`에 전달해야 합니다:

```python
# 수정된 호출
is_extracted_from_links = generate_is_extracted_from_links(
    dynamic_nodes, 
    section_nodes,
    extracted_data=extracted_data,  # 추가
    doc_node=doc_node                # 추가
)
```

### 3. ticker 대소문자 일관성

- Company ID: 대문자 (`AAPL`)
- 노드 ID 내 ticker: 소문자 (`risk_aapl_xxx`)
- 비교 시 `.upper()` 또는 `.lower()`로 정규화 필요

### 4. 날짜 필드 타입 일관성

- `extracted_at`: ISO 8601 datetime (`2024-12-26T16:17:03Z`)
- `first_mentioned`, `last_mentioned`, `event_date`: ISO 8601 date (`2024-12-26`)
- 날짜 파싱 시 형식 검증 필요

---

## 🎯 다음 단계

Phase 5 완료 후:
1. **Phase 6**: Static-Dynamic 간 Link 생성 (IS_MENTIONED_IN) - `mentioned_products`, `mentioned_persons`, `mentioned_companies` 활용
2. **Phase 7**: Dynamic Graph 파일 저장 (`{TICKER}_dynamic_graph.json`)
3. **Phase 8**: 메인 실행 스크립트 통합
4. **Phase 9**: Vector DB 적재 및 하이브리드 검색 구현

