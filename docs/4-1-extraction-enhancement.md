# Phase 4: Knowledge Triplet 추출 개선 방향

## 📌 개요

현재 Phase 4는 모든 카테고리를 추출하고 있으나, Graph Ontology 설계에 따라 **Dynamic Node 중심**으로 추출을 재구성하고, **관련 Product/Person/Company 연결 정보**를 함께 추출하도록 개선합니다.

---

## 🎯 목표

1. **Dynamic Node 중심 추출**: Risk, Opportunity, Event, Technology 추출 (Strategy, Financials는 제외 또는 별도 처리)
2. **각 엔티티별 관계 정보 필수 포함**: **모든 Risk, Opportunity, Event, Technology 엔티티마다** `mentioned_products`, `mentioned_persons`, `mentioned_companies` 필드를 필수로 포함 (언급이 없으면 빈 배열 `[]`)
3. **Link 생성 준비**: Phase 4.5에서 IS_MENTIONED_IN Link 생성에 필요한 정보를 미리 수집
4. **Product name은 고유명사**: Product 노드의 name은 고유명사여야 함 (예: "Tesla Model 3", "iPhone 15 Pro". 일반명사 "car", "phone" 등은 사용하지 않음)

---

## 📊 Graph Ontology 기반 Node 분류

### Static Node (Phase 4에서 추출하지 않음)
- **Company**: ticker로 자동 식별 가능, 별도 추출 불필요
- **Product**: Dynamic Node에서 언급된 제품을 추출하여 나중에 Static Node로 생성
- **Person**: Dynamic Node에서 언급된 인물을 추출하여 나중에 Static Node로 생성

### Dynamic Node (Phase 4에서 추출)
- **Risk**: 위험 요소
- **Opportunity**: 기회 요소
- **Event**: 주요 이벤트
- **Technology**: 기술 (예: 칩셋, 소프트웨어 기술, 제조 공정 등)
- **Section**: Parsed Data에서 이미 생성됨
- **Document**: Parsed Data에서 이미 생성됨

### 제외 대상
- **Strategy**: Graph Ontology에 명시적 Node 타입 없음 → 제외 또는 Opportunity로 통합
- **Financials**: Graph Ontology에 명시적 Node 타입 없음 → 제외 또는 별도 저장

---

## 🔄 수정된 추출 구조

### 1. 추출 대상 카테고리 변경

**현재 구조:**
```json
{
  "opportunities": [...],
  "risks": [...],
  "events": [...],
  "strategies": [...],      // 제거 또는 별도 처리
  "financials": [...]       // 제거 또는 별도 처리
}
```

**수정된 구조:**
```json
{
  "opportunities": [...],
  "risks": [...],
  "events": [...],
  "technologies": [...],         // 새로 추가
  "mentioned_products": [...],  // 새로 추가
  "mentioned_persons": [...],   // 새로 추가
  "strategies": [...],           // 선택: 제거 또는 별도 필드
  "financials": [...]            // 선택: 제거 또는 별도 필드
}
```

---

### 2. 각 Dynamic Node에 연결 정보 추가

#### 2.1 Risk/Opportunity/Event/Technology 엔티티 구조 확장

**현재 구조:**
```json
{
  "entity": "Intense Price Competition",
  "description": "...",
  "source_section": "business"
}
```

**수정된 구조 (각 엔티티마다 필수):**
```json
{
  "entity": "Intense Price Competition",
  "description": "...",
  "source_section": "business",
  "extracted_at": "2024-12-26T16:17:03Z",
  "mentioned_products": [                 // 필수: 각 엔티티마다 포함
    {
      "name": "iPhone 15",
      "mention_context": "mentioned in context of price competition affecting iPhone 15 pricing"
    },
    {
      "name": "iPad",
      "mention_context": "iPad pricing also affected by competition"
    }
  ],
  "mentioned_persons": [                  // 필수: 각 엔티티마다 포함
    {
      "name": "Tim Cook",
      "role": "CEO",
      "mention_context": "Tim Cook discussed pricing strategy in response to competition"
    }
  ],
  "mentioned_companies": [                // 필수: 각 엔티티마다 포함 (경쟁사, 파트너사 등)
    {
      "name": "Samsung",
      "ticker": "SSNLF",
      "mention_context": "Samsung mentioned as competitor in price competition"
    }
  ]
}
```

**중요**: 모든 Risk, Opportunity, Event, Technology 엔티티는 반드시 `mentioned_products`, `mentioned_persons`, `mentioned_companies` 필드를 포함해야 합니다. 언급이 없는 경우 빈 배열 `[]`로 표시합니다.

---

### 3. 각 엔티티별 Product/Person/Company 추출 규칙

**핵심 원칙**: 각 Risk, Opportunity, Event, Technology 엔티티는 반드시 해당 엔티티의 `entity`와 `description`에서 언급된 Product, Person, Company 정보를 포함해야 합니다.

**Product name 규칙**: Product의 name은 반드시 고유명사여야 합니다. 예: "Tesla Model 3", "iPhone 15 Pro", "NVIDIA H100 GPU". 일반명사 "car", "phone", "chip" 등은 사용하지 않습니다.

#### 3.1 추출 범위
- **Entity 필드**: 엔티티 제목에서 언급된 제품/인물/회사
- **Description 필드**: 설명 텍스트에서 언급된 제품/인물/회사
- **컨텍스트**: 해당 엔티티와의 관련성 있는 언급만 포함

#### 3.2 추출 방법
1. **LLM 기반 NER**: 프롬프트에서 각 엔티티마다 Product/Person/Company 추출 지시
2. **Entity 패턴 매칭**: "Release of iPhone 15" → "iPhone 15" 추출
3. **Description 분석**: 설명 텍스트에서 제품명, 인물명, 회사명 인식

#### 3.3 데이터 구조 (각 엔티티마다)

**Opportunity 예시:**
```json
{
  "entity": "Integrated Ecosystem Strategy",
  "description": "The Company focuses on the integration of hardware, software, and services to provide a unique and seamless customer experience. This integration is designed to strengthen brand loyalty and create a competitive advantage through a unified platform of products like iPhone, Mac, and iPad.",
  "source_section": "risk_factors",
  "extracted_at": "2024-12-26T16:17:03Z",
  "mentioned_products": [
    {
      "name": "iPhone",
      "mention_context": "mentioned as part of unified platform"
    },
    {
      "name": "Mac",
      "mention_context": "mentioned as part of unified platform"
    },
    {
      "name": "iPad",
      "mention_context": "mentioned as part of unified platform"
    }
  ],
  "mentioned_persons": [],
  "mentioned_companies": []
}
```

**Event 예시:**
```json
{
  "entity": "Release of iPhone 15 Lineup",
  "date": "2023",
  "description": "The Company introduced the iPhone 15 Pro and iPhone 15 as part of its smartphone line based on the iOS operating system. These product introductions significantly impact net sales, cost of sales, and operating expenses during the period.",
  "source_section": "business",
  "extracted_at": "2024-12-26T16:17:03Z",
  "mentioned_products": [
    {
      "name": "iPhone 15 Pro",
      "mention_context": "product introduced in this event"
    },
    {
      "name": "iPhone 15",
      "mention_context": "product introduced in this event"
    }
  ],
  "mentioned_persons": [],
  "mentioned_companies": []
}
```

**Risk 예시:**
```json
{
  "entity": "Intense Price Competition",
  "description": "The Company faces aggressive price competition and downward pressure on gross margins from competitors with lower cost structures. Some competitors provide products at little or no profit, or even at a loss, to gain market share.",
  "source_section": "business",
  "extracted_at": "2024-12-26T16:17:03Z",
  "mentioned_products": [],
  "mentioned_persons": [],
  "mentioned_companies": [
    {
      "name": "competitors",
      "ticker": null,
      "mention_context": "competitors with lower cost structures mentioned"
    }
  ]
}
```

---

### 4. 전역 Product/Person 목록 (선택적)

각 엔티티별 추출 외에, 문서 전체에서 추출된 Product/Person 목록을 별도로 유지할 수 있습니다. 이는 Phase 4.5에서 Product/Person Node 생성 시 중복 제거에 활용됩니다.

**데이터 구조:**
```json
{
  "mentioned_products_global": [
    {
      "name": "iPhone 15",
      "category": "smartphone",
      "mentioned_in_entities": ["events", "opportunities"],
      "mention_count": 3
    }
  ],
  "mentioned_persons_global": [
    {
      "name": "Tim Cook",
      "role": "CEO",
      "mentioned_in_entities": ["opportunities"],
      "mention_count": 1
    }
  ]
}
```

---

## 📝 프롬프트 수정 방향

### `app/prompts/triplet_extractor.yaml` 수정

**현재 프롬프트:**
- Opportunities, Risks, Events, Strategies, Financials 추출

**수정된 프롬프트:**
- Opportunities, Risks, Events, Technologies 추출 (Dynamic Node)
- 각 엔티티에서 언급된 Products, Persons 추출
- Product name은 반드시 고유명사로 추출 (예: "Tesla Model 3", "iPhone 15 Pro")
- Strategies, Financials는 선택적으로 별도 필드로 저장

**새로운 JSON Schema (각 엔티티마다 필수 필드 포함):**
```json
{
  "opportunities": [
    {
      "entity": "Short title",
      "description": "2–3 sentences, English",
      "mentioned_products": [                    // 필수: 빈 배열도 가능
        {
          "name": "Product Name",
          "mention_context": "how it was mentioned in this entity"
        }
      ],
      "mentioned_persons": [                     // 필수: 빈 배열도 가능
        {
          "name": "Person Name",
          "role": "CEO|CFO|CTO|Director|other",
          "mention_context": "how they were mentioned"
        }
      ],
      "mentioned_companies": [                   // 필수: 빈 배열도 가능
        {
          "name": "Company Name",
          "ticker": "TICKER or null",
          "mention_context": "how they were mentioned"
        }
      ]
    }
  ],
  "risks": [
    {
      "entity": "Short title",
      "description": "2–3 sentences, English",
      "mentioned_products": [],                  // 필수: 반드시 포함
      "mentioned_persons": [],                   // 필수: 반드시 포함
      "mentioned_companies": []                  // 필수: 반드시 포함
    }
  ],
  "events": [
    {
      "entity": "Event name",
      "date": "YYYY-MM-DD or YYYY or empty string",
      "description": "2–3 sentences, English",
      "mentioned_products": [],                  // 필수: 반드시 포함
      "mentioned_persons": [],                   // 필수: 반드시 포함
      "mentioned_companies": []                  // 필수: 반드시 포함
    }
  ],
  "mentioned_products_global": [                 // 선택: 전체 문서 통합 목록
    {
      "name": "Product Name",
      "category": "smartphone|wearable|service|other",
      "first_mentioned_in": "opportunity|risk|event"
    }
  ],
  "mentioned_persons_global": [                  // 선택: 전체 문서 통합 목록
    {
      "name": "Person Name",
      "role": "CEO|CFO|CTO|Director|other",
      "first_mentioned_in": "opportunity|risk|event"
    }
  ]
}
```

**중요**: 모든 opportunities, risks, events, technologies 배열의 각 항목은 반드시 `mentioned_products`, `mentioned_persons`, `mentioned_companies` 필드를 포함해야 합니다. 언급이 없는 경우 빈 배열 `[]`로 표시합니다.

**Product name 규칙**: Product의 name은 반드시 고유명사여야 합니다. 예: "Tesla Model 3", "iPhone 15 Pro", "NVIDIA H100 GPU". 일반명사 "car", "phone", "chip" 등은 사용하지 않습니다.

---

## 🔧 코드 수정 사항

### 1. `app/services/triplet_extractor.py`

#### 1.1 `ExtractedTriplets` 데이터 클래스 수정

```python
@dataclass
class ExtractedTriplets:
    """추출된 Knowledge Triplets"""
    ticker: str
    filing_type: str
    accession_number: str
    section: str
    opportunities: List[Dict]
    risks: List[Dict]
    events: List[Dict]
    strategies: List[Dict]          # 선택: 제거 또는 유지
    financials: List[Dict]          # 선택: 제거 또는 유지
    mentioned_products: List[Dict]   # 새로 추가
    mentioned_persons: List[Dict]   # 새로 추가
```

#### 1.2 `TripletExtractor.extract()` 수정

- 프롬프트에 Product/Person 추출 지시 추가
- 결과 파싱 시 `mentioned_products`, `mentioned_persons` 필드 처리

#### 1.3 `TripletExtractorBatch._combine_sections()` 수정

**핵심 원칙**: 각 엔티티(opportunity, risk, event)는 LLM 추출 단계에서 이미 `mentioned_products`, `mentioned_persons`, `mentioned_companies` 필드를 포함하므로, `_combine_sections()`에서는 이를 그대로 보존합니다.

```python
def _combine_sections(...) -> dict:
    from datetime import datetime
    
    extracted_at = datetime.now().isoformat() + "Z"
    
    combined: dict = {
        "ticker": ticker,
        "filing_type": filing_type,
        "accession_number": accession_number,
        "sections_included": [...],
        "year": self._extract_year(accession_number, parsed_metadata),
        "quarter": self._extract_quarter(filing_type, parsed_metadata),
        "extracted_at": extracted_at,
        "opportunities": [],
        "risks": [],
        "events": [],
        "mentioned_products_global": [],    # 전역 목록 (선택)
        "mentioned_persons_global": [],     # 전역 목록 (선택)
        "strategies": [],                   # 선택
        "financials": [],                   # 선택
    }
    
    # 각 섹션의 결과 병합
    for t in per_section:
        # Opportunities 병합 (각 엔티티에 mentioned_products/persons/companies 포함)
        for opp in t.opportunities:
            opp_with_meta = dict(opp)
            opp_with_meta["source_section"] = t.section
            opp_with_meta["extracted_at"] = extracted_at
            # mentioned_products, mentioned_persons, mentioned_companies는 이미 LLM이 추출
            # 필드가 없으면 빈 배열로 초기화
            if "mentioned_products" not in opp_with_meta:
                opp_with_meta["mentioned_products"] = []
            if "mentioned_persons" not in opp_with_meta:
                opp_with_meta["mentioned_persons"] = []
            if "mentioned_companies" not in opp_with_meta:
                opp_with_meta["mentioned_companies"] = []
            combined["opportunities"].append(opp_with_meta)
        
        # Risks 병합
        for risk in t.risks:
            risk_with_meta = dict(risk)
            risk_with_meta["source_section"] = t.section
            risk_with_meta["extracted_at"] = extracted_at
            if "mentioned_products" not in risk_with_meta:
                risk_with_meta["mentioned_products"] = []
            if "mentioned_persons" not in risk_with_meta:
                risk_with_meta["mentioned_persons"] = []
            if "mentioned_companies" not in risk_with_meta:
                risk_with_meta["mentioned_companies"] = []
            combined["risks"].append(risk_with_meta)
        
        # Events 병합
        for event in t.events:
            event_with_meta = dict(event)
            event_with_meta["source_section"] = t.section
            event_with_meta["extracted_at"] = extracted_at
            event_with_meta["date_parsed"] = self._parse_event_date(event.get("date", ""))
            event_with_meta["event_type"] = self._classify_event_type(
                event.get("entity", ""),
                event.get("description", "")
            )
            if "mentioned_products" not in event_with_meta:
                event_with_meta["mentioned_products"] = []
            if "mentioned_persons" not in event_with_meta:
                event_with_meta["mentioned_persons"] = []
            if "mentioned_companies" not in event_with_meta:
                event_with_meta["mentioned_companies"] = []
            combined["events"].append(event_with_meta)
        
        # 전역 Product/Person 목록 수집 (중복 제거용)
        for category in ["opportunities", "risks", "events"]:
            for item in getattr(t, category, []):
                combined["mentioned_products_global"].extend(
                    item.get("mentioned_products", [])
                )
                combined["mentioned_persons_global"].extend(
                    item.get("mentioned_persons", [])
                )
    
    # 전역 목록 중복 제거 및 통합
    combined["mentioned_products_global"] = self._deduplicate_products(
        combined["mentioned_products_global"]
    )
    combined["mentioned_persons_global"] = self._deduplicate_persons(
        combined["mentioned_persons_global"]
    )
    
    # extraction_stats 추가
    combined["extraction_stats"] = {
        "opportunities_count": len(combined["opportunities"]),
        "risks_count": len(combined["risks"]),
        "events_count": len(combined["events"]),
        "mentioned_products_count": len(combined["mentioned_products_global"]),
        "mentioned_persons_count": len(combined["mentioned_persons_global"]),
    }
    
    return combined
```

**중요**: 각 엔티티의 `mentioned_products`, `mentioned_persons`, `mentioned_companies`는 LLM이 추출 단계에서 이미 포함하므로, `_combine_sections()`에서는 그대로 보존만 하면 됩니다. 필드가 없는 경우 빈 배열로 초기화합니다.

#### 1.4 새로운 헬퍼 메서드 추가

```python
def _deduplicate_products(self, products: List[Dict]) -> List[Dict]:
    """제품명 기준 중복 제거 및 통합"""
    seen = {}
    for p in products:
        name = p.get("name", "").lower().strip()
        if name and name not in seen:
            seen[name] = p
        elif name in seen:
            # 언급 횟수 증가, 컨텍스트 병합
            seen[name]["mention_count"] = seen[name].get("mention_count", 1) + 1
    return list(seen.values())

def _deduplicate_persons(self, persons: List[Dict]) -> List[Dict]:
    """인물명 기준 중복 제거 및 통합"""
    seen = {}
    for p in persons:
        name = p.get("name", "").lower().strip()
        if name and name not in seen:
            seen[name] = p
        elif name in seen:
            # 역할 정보 업데이트, 컨텍스트 병합
            if p.get("role") and not seen[name].get("role"):
                seen[name]["role"] = p["role"]
            seen[name]["mention_count"] = seen[name].get("mention_count", 1) + 1
    return list(seen.values())
```

---

### 2. `app/prompts/triplet_extractor.yaml` 수정

**추가할 지시사항:**

```yaml
template: |
  ...
  
  Task:
  Extract up to 10 items for each of the following categories:
  1) Opportunities: growth drivers, market opportunities, competitive advantages
  2) Risks: risk factors, regulatory risks, competitive threats, operational risks
  3) Events: major events such as M&A, product launches, litigation, regulatory changes (include a date when stated)
  
  **CRITICAL**: For EACH extracted item (opportunity, risk, event, or technology), you MUST identify:
  - Mentioned Products: product names mentioned in the entity title OR description (e.g., "iPhone 15 Pro", "Tesla Model 3", "Apple Watch Ultra 2")
    * If no products are mentioned, use an empty array []
    * Include the context of how the product was mentioned
    * **IMPORTANT**: Product names must be proper nouns (e.g., "Tesla Model 3", not "car" or "vehicle")
  - Mentioned Persons: person names and their roles mentioned in the entity title OR description (e.g., "Tim Cook", "CEO")
    * If no persons are mentioned, use an empty array []
    * Include the role if mentioned (CEO, CFO, CTO, Director, etc.)
  - Mentioned Companies: competitor, partner, or other company names mentioned (if any)
    * If no companies are mentioned, use an empty array []
    * Include ticker symbol if known
  
  **IMPORTANT**: Every single opportunity, risk, event, and technology item MUST include these three fields:
  - "mentioned_products": [] (can be empty, but field must exist)
  - "mentioned_persons": [] (can be empty, but field must exist)
  - "mentioned_companies": [] (can be empty, but field must exist)
  
  Additionally, extract a global list of:
  - All unique products mentioned across the entire document
  - All unique persons mentioned across the entire document
  
  JSON schema (must match exactly):
  {
    "opportunities": [
      {
        "entity": "Short title",
        "description": "2–3 sentences, English",
        "mentioned_products": [                                    // 필수: 반드시 포함
          {
            "name": "Product Name",
            "mention_context": "how it was mentioned in this entity"
          }
        ],
        "mentioned_persons": [                                      // 필수: 반드시 포함
          {
            "name": "Person Name",
            "role": "CEO|CFO|CTO|Director|other or null",
            "mention_context": "how they were mentioned"
          }
        ],
        "mentioned_companies": [                                    // 필수: 반드시 포함
          {
            "name": "Company Name",
            "ticker": "TICKER or null",
            "mention_context": "how they were mentioned"
          }
        ]
      }
    ],
    "risks": [
      {
        "entity": "Short title",
        "description": "2–3 sentences, English",
        "mentioned_products": [],                                  // 필수: 빈 배열도 가능
        "mentioned_persons": [],                                   // 필수: 빈 배열도 가능
        "mentioned_companies": []                                   // 필수: 빈 배열도 가능
      }
    ],
    "events": [
      {
        "entity": "Event name",
        "date": "YYYY-MM-DD or YYYY or empty string",
        "description": "2–3 sentences, English",
        "mentioned_products": [],                                  // 필수: 빈 배열도 가능
        "mentioned_persons": [],                                   // 필수: 빈 배열도 가능
        "mentioned_companies": []                                   // 필수: 빈 배열도 가능
      }
    ],
    "mentioned_products_global": [
      {
        "name": "Product Name",
        "category": "smartphone|wearable|service|other",
        "first_mentioned_in": "opportunity|risk|event"
      }
    ],
    "mentioned_persons_global": [
      {
        "name": "Person Name",
        "role": "CEO|CFO|CTO|Director|other",
        "first_mentioned_in": "opportunity|risk|event"
      }
    ]
  }
```

---

### 3. `scripts/03_extract_triplets.py` 수정

- 출력 메시지에 Product/Person 추출 정보 추가
- 요약 통계에 `mentioned_products_count`, `mentioned_persons_count` 추가

---

## 📊 수정된 Extracted Data 구조 예시

```json
{
  "ticker": "AAPL",
  "filing_type": "10-K",
  "accession_number": "0000320193-23-000106",
  "sections_included": ["business", "risk_factors"],
  "year": 2023,
  "quarter": null,
  "extracted_at": "2024-12-26T16:17:03Z",
  "extraction_stats": {
    "opportunities_count": 8,
    "risks_count": 9,
    "events_count": 4,
    "mentioned_products_count": 5,
    "mentioned_persons_count": 3
  },
  "opportunities": [
    {
      "entity": "Integrated Ecosystem Strategy",
      "description": "...",
      "source_section": "risk_factors",
      "extracted_at": "2024-12-26T16:17:03Z",
      "mentioned_products": [                    // 각 엔티티마다 필수
        {
          "name": "iPhone",
          "mention_context": "mentioned as part of unified platform"
        },
        {
          "name": "Mac",
          "mention_context": "mentioned as part of unified platform"
        },
        {
          "name": "iPad",
          "mention_context": "mentioned as part of unified platform"
        }
      ],
      "mentioned_persons": [],                   // 각 엔티티마다 필수 (빈 배열 가능)
      "mentioned_companies": []                   // 각 엔티티마다 필수 (빈 배열 가능)
    }
  ],
  "risks": [...],
  "events": [
    {
      "entity": "Release of iPhone 15 Lineup",
      "date": "2023",
      "date_parsed": "2023-09-01",
      "description": "...",
      "source_section": "business",
      "extracted_at": "2024-12-26T16:17:03Z",
      "event_type": "product_launch",
      "mentioned_products": [                    // 각 엔티티마다 필수
        {
          "name": "iPhone 15",
          "mention_context": "product introduced in this event"
        },
        {
          "name": "iPhone 15 Pro",
          "mention_context": "product introduced in this event"
        }
      ],
      "mentioned_persons": [],                   // 각 엔티티마다 필수 (빈 배열 가능)
      "mentioned_companies": []                   // 각 엔티티마다 필수 (빈 배열 가능)
    }
  ],
  "mentioned_products_global": [
    {
      "name": "iPhone 15",
      "category": "smartphone",
      "first_mentioned_in": "event",
      "mention_count": 3
    },
    {
      "name": "Apple Watch Ultra 2",
      "category": "wearable",
      "first_mentioned_in": "event",
      "mention_count": 2
    }
  ],
  "mentioned_persons_global": [
    {
      "name": "Tim Cook",
      "role": "CEO",
      "first_mentioned_in": "opportunity",
      "mention_count": 1
    }
  ]
}
```

---

## 🔗 Phase 4.5에서의 활용

### 1. Product Node 생성
- `mentioned_products_global`를 기반으로 Product Node 생성
- 각 Product의 `first_mentioned_in` 정보로 초기 연결 파악

### 2. Person Node 생성
- `mentioned_persons_global`를 기반으로 Person Node 생성
- `role` 정보로 Company와의 HAS_RELATION Link 생성

### 3. Link 생성
- **IS_MENTIONED_IN**: 
  - `(Product: iPhone 15) -[IS_MENTIONED_IN]-> (Event: Release of iPhone 15 Lineup)`
  - 각 엔티티의 `mentioned_products` 필드 활용
- **HAS_RELATION**:
  - `(Company: AAPL) -[HAS_RELATION {role: "CEO"}]-> (Person: Tim Cook)`
  - `mentioned_persons_global`의 role 정보 활용

---

## ✅ 구현 체크리스트

### Phase 4 수정
- [ ] `triplet_extractor.yaml` 프롬프트 수정 (Product/Person 추출 추가)
- [ ] `ExtractedTriplets` 데이터 클래스에 `mentioned_products`, `mentioned_persons` 필드 추가
- [ ] `TripletExtractor.extract()` 메서드에서 새 필드 처리
- [ ] `TripletExtractorBatch._combine_sections()`에서 Product/Person 중복 제거 및 통합
- [ ] `_deduplicate_products()`, `_deduplicate_persons()` 헬퍼 메서드 구현
- [ ] `extracted_at` 필드 추가 (각 엔티티 및 최상위 레벨)
- [ ] `extraction_stats`에 Product/Person 통계 추가
- [ ] Event의 `date_parsed`, `event_type` 추가
- [ ] Document 메타데이터 추가 (`year`, `quarter` 등)

### 테스트
- [ ] 샘플 데이터로 추출 테스트
- [ ] Product/Person 추출 정확도 검증
- [ ] 중복 제거 로직 검증

---

## 📌 주의사항

1. **Strategy/Financials 처리**: 
   - Graph Ontology에 명시적 Node 타입이 없으므로 제거하거나 별도 필드로 저장
   - 필요시 Phase 4.5에서 Opportunity로 통합하거나 별도 저장소에 저장

2. **Product/Person 추출 정확도**:
   - LLM 기반 추출이므로 오탐 가능성 있음
   - Phase 4.5에서 검증 및 필터링 로직 추가 권장

3. **Company 연결**:
   - Company는 ticker로 자동 식별 가능하므로 명시적 추출 불필요
   - 경쟁사나 파트너사만 `mentioned_companies`에 포함

4. **성능 고려**:
   - Product/Person 추출로 프롬프트가 길어지면 토큰 사용량 증가
   - 필요시 별도 추출 단계로 분리 고려

---

## 🎯 기대 효과

1. **Graph 구조 명확화**: Dynamic Node만 추출하여 Graph Ontology와 일치
2. **Link 생성 준비**: Phase 4.5에서 Product/Person Node 및 Link 생성이 용이
3. **관계 정보 보강**: 엔티티 간 관계 정보를 미리 수집하여 Graph 품질 향상
4. **확장성**: 향후 Product/Person 기반 질의 응답 지원 가능

