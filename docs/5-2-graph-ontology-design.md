# Knowledge Graph Ontology 설계

## 📌 목적

공시 데이터를 Graph DB와 Vector DB로 적재하여, 사용자의 질의에 대한 심도 깊은 답변을 제공합니다.

## 🏗 Graph 구조 개요

### Node 타입
- **Company**: 기업 정보
- **Risk**: 위험 요소
- **Opportunity**: 기회 요소
- **Event**: 주요 이벤트
- **Technology**: 기술/기술 혁신
- **Section**: 파싱된 문서의 섹션
- **Document**: SEC 공시 문서
- **Product**: 제품/서비스 (명시적 추출 또는 description에서 추출)
- **Person**: 인물 (임원, 직원 등)

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

---

## 📊 Node 스키마 정의

### 1. Company Node

```json
{
  "$schema": "http://json-schema.org/draft-07/schema#",
  "type": "object",
  "title": "Company",
  "description": "기업 정보를 나타내는 노드",
  "required": ["id", "node_type", "ticker", "name", "description", "node_style"],
  "properties": {
    "id": {
      "type": "string",
      "description": "고유 식별자 (예: 'AAPL', 'TSLA')",
      "pattern": "^[A-Z]{1,5}$"
    },
    "node_type": {
      "type": "string",
      "description": "노드 타입",
      "const": "Company"
    },
    "node_style": {
      "type": "string",
      "description": "노드 스타일",
      "enum": ["static", "dynamic"],
      "const": "static"
    },
    "ticker": {
      "type": "string",
      "description": "주식 티커 심볼",
      "pattern": "^[A-Z]{1,5}$"
    },
    "name": {
      "type": "string",
      "description": "기업 공식 명칭",
      "examples": ["Apple Inc.", "Tesla, Inc.", "Microsoft Corporation"]
    },
    "sector": {
      "type": "string",
      "description": "산업 섹터",
      "enum": ["Technology", "Consumer Cyclical", "Communication Services"]
    },
    "description": {
      "type": "string",
      "description": "기업에 대한 설명 (사업 영역, 주요 제품/서비스, 비즈니스 모델 등)",
      "minLength": 10
    }
  }
}
```

**샘플 데이터:**
```json
{
  "id": "AAPL",
  "node_type": "Company",
  "ticker": "AAPL",
  "name": "Apple Inc.",
  "sector": "Technology",
  "description": "Apple Inc.는 스마트폰, 개인용 컴퓨터, 태블릿, 웨어러블 디바이스 등을 설계, 제조 및 판매하는 글로벌 기술 기업입니다. iPhone, iPad, Mac, Apple Watch 등의 하드웨어 제품과 iOS, macOS 등의 소프트웨어, 그리고 iCloud, App Store, Apple Music 등의 서비스를 제공합니다.",
  "node_style": "static"
}
```

### 2. Risk/Opportunity/Event/Technology Node (통합 스키마)

```json
{
  "$schema": "http://json-schema.org/draft-07/schema#",
  "type": "object",
  "title": "Risk/Opportunity/Event/Technology",
  "description": "위험 요소, 기회 요소, 주요 이벤트, 기술을 나타내는 통합 노드",
  "required": ["id", "node_type", "entity", "description", "node_style", "ticker"],
  "properties": {
    "id": {
      "type": "string",
      "description": "고유 식별자",
      "oneOf": [
        {"pattern": "^risk_[a-z0-9_]+$"},
        {"pattern": "^opp_[a-z0-9_]+$"},
        {"pattern": "^event_[a-z0-9_]+$"},
        {"pattern": "^tech_[a-z0-9_]+$"}
      ],
      "examples": [
        "risk_aapl_intense_competition_2023",
        "opp_aapl_ecosystem_2023",
        "event_aapl_iphone15_2023",
        "tech_aapl_a17_pro_chip_2023"
      ]
    },
    "node_type": {
      "type": "string",
      "description": "노드 타입",
      "enum": ["Risk", "Opportunity", "Event", "Technology"]
    },
    "node_style": {
      "type": "string",
      "description": "노드 스타일",
      "enum": ["static", "dynamic"],
      "const": "dynamic"
    },
    "ticker": {
      "type": "string",
      "description": "기업 티커 심볼",
      "pattern": "^[A-Z]{1,5}$"
    },
    "entity": {
      "type": "string",
      "description": "엔티티의 제목/이름",
      "examples": [
        "Intense Price Competition",
        "Integrated Ecosystem Strategy",
        "Release of iPhone 15 Lineup"
      ]
    },
    "description": {
      "type": "string",
      "description": "상세 설명 (2-3 문장)",
      "minLength": 50
    },
    "description_embedding": {
      "type": "array",
      "description": "description 텍스트의 embedding 벡터",
      "items": {
        "type": "number"
      },
      "minItems": 1
    },
    "date": {
      "type": "string",
      "description": "날짜 (Event의 경우 필수, Risk/Opportunity의 경우 선택사항)",
      "pattern": "^(\\d{4}(-\\d{2}(-\\d{2})?)?)?$",
      "examples": ["2023", "2023-09-01", ""]
    },
    "date_parsed": {
      "type": "string",
      "format": "date",
      "description": "파싱된 날짜 (ISO 8601 형식, Event의 경우 사용)"
    },
    "extracted_at": {
      "type": "string",
      "format": "date-time",
      "description": "추출 시각"
    },
    "metadata": {
      "type": "object",
      "description": "추가 메타데이터",
      "properties": {
        "source_section": {
          "type": "string",
          "description": "추출된 원본 섹션",
          "enum": ["business", "risk_factors", "mda", "results_operations", "other_events"]
        },
        "filing_type": {
          "type": "string",
          "enum": ["10-K", "10-Q", "8-K"]
        },
        "accession_number": {
          "type": "string",
          "description": "SEC Accession Number"
        },
        "event_type": {
          "type": "string",
          "description": "이벤트 유형 (Event 노드의 경우 사용)",
          "enum": ["product_launch", "financial_announcement", "m&a", "regulatory_change", "other"]
        }
      }
    }
  }
}
```

**샘플 데이터:**

**Risk 샘플:**
```json
{
  "id": "risk_aapl_intense_price_competition_2023",
  "node_type": "Risk",
  "ticker": "AAPL",
  "entity": "Intense Price Competition",
  "description": "The Company faces aggressive price competition and downward pressure on gross margins from competitors with lower cost structures. Some competitors provide products at little or no profit, or even at a loss, to gain market share.",
  "description_embedding": [0.0123, -0.0456, 0.0789, -0.0234, 0.0567, 0.0890, -0.0345, 0.0678, -0.0123, 0.0456],
  "node_style": "dynamic",
  "extracted_at": "2024-12-26T16:17:03Z",
  "metadata": {
    "source_section": "business",
    "filing_type": "10-K",
    "accession_number": "0000320193-23-000106"
  }
}
```

**Opportunity 샘플:**
```json
{
  "id": "opp_aapl_integrated_ecosystem_strategy_2023",
  "node_type": "Opportunity",
  "ticker": "AAPL",
  "entity": "Integrated Ecosystem Strategy",
  "description": "The Company focuses on the integration of hardware, software, and services to provide a unique and seamless customer experience. This integration is designed to strengthen brand loyalty and create a competitive advantage through a unified platform of products like iPhone, Mac, and iPad.",
  "description_embedding": [0.0234, -0.0567, 0.0890, -0.0345, 0.0678, 0.0123, -0.0456, 0.0789, -0.0234, 0.0567],
  "node_style": "dynamic",
  "extracted_at": "2024-12-26T16:17:03Z",
  "metadata": {
    "source_section": "risk_factors",
    "filing_type": "10-K",
    "accession_number": "0000320193-23-000106"
  }
}
```

**Event 샘플:**
```json
{
  "id": "event_aapl_iphone15_lineup_2023",
  "node_type": "Event",
  "ticker": "AAPL",
  "entity": "Release of iPhone 15 Lineup",
  "description": "The Company introduced the iPhone 15 Pro and iPhone 15 as part of its smartphone line based on the iOS operating system. These product introductions significantly impact net sales, cost of sales, and operating expenses during the period.",
  "description_embedding": [0.0345, -0.0678, 0.0123, -0.0456, 0.0789, 0.0234, -0.0567, 0.0890, -0.0345, 0.0678],
  "node_style": "dynamic",
  "date": "2023",
  "date_parsed": "2023-09-01",
  "extracted_at": "2024-12-26T16:17:03Z",
  "metadata": {
    "source_section": "business",
    "filing_type": "10-K",
    "accession_number": "0000320193-23-000106",
    "event_type": "product_launch"
  }
}
```

### 3. Section Node

```json
{
  "$schema": "http://json-schema.org/draft-07/schema#",
  "type": "object",
  "title": "Section",
  "description": "파싱된 문서의 섹션을 나타내는 노드",
  "required": ["id", "node_type", "section_name", "filing_type", "node_style"],
  "properties": {
    "id": {
      "type": "string",
      "description": "고유 식별자 (예: 'section_aapl_10k_2023_business')",
      "pattern": "^section_[a-z0-9_]+$"
    },
    "node_type": {
      "type": "string",
      "description": "노드 타입",
      "const": "Section"
    },
    "node_style": {
      "type": "string",
      "description": "노드 스타일",
      "enum": ["static", "dynamic"],
      "const": "dynamic"
    },
    "section_name": {
      "type": "string",
      "description": "섹션 이름",
      "enum": ["business", "risk_factors", "mda", "financial_statements", "results_operations", "other_events"]
    },
    "filing_type": {
      "type": "string",
      "description": "공시 유형",
      "enum": ["10-K", "10-Q", "8-K"]
    },
    "ticker": {
      "type": "string",
      "description": "기업 티커",
      "pattern": "^[A-Z]{1,5}$"
    },
    "accession_number": {
      "type": "string",
      "description": "SEC Accession Number"
    },
    "section_text": {
      "type": "string",
      "description": "섹션의 원문 텍스트"
    },
    "text_length": {
      "type": "integer",
      "description": "섹션 텍스트 길이 (문자 수)",
      "minimum": 0
    },
    "parsed_at": {
      "type": "string",
      "format": "date-time",
      "description": "파싱 시각"
    },
    "metadata": {
      "type": "object",
      "description": "추가 메타데이터",
      "properties": {
        "year": {
          "type": "integer",
          "description": "공시 연도"
        },
        "quarter": {
          "type": "integer",
          "description": "분기 (10-Q의 경우, 1-4)",
          "minimum": 1,
          "maximum": 4
        }
      }
    }
  }
}
```

**샘플 데이터:**
```json
{
  "id": "section_aapl_10k_2023_business",
  "node_type": "Section",
  "section_name": "business",
  "filing_type": "10-K",
  "node_style": "dynamic",
  "ticker": "AAPL",
  "accession_number": "0000320193-23-000106",
  "section_text": "Item 1. Business\n\nGeneral\n\nApple Inc. (the \"Company\" or \"Apple\") designs, manufactures and markets smartphones, personal computers, tablets, wearables and accessories worldwide and sells a variety of related services. The Company's products and services include iPhone, Mac, iPad, AirPods, Apple TV, Apple Watch, Beats products, HomePod, iPod touch, and accessories. The Company also delivers digital content and applications through the App Store, Apple Music, Apple TV+, Apple Arcade, Apple Fitness+, Apple News+, Apple Podcasts, iCloud, Apple Card, Apple Pay, Apple Books, and other services...",
  "text_length": 45230,
  "parsed_at": "2024-12-26T10:00:00Z",
  "metadata": {
    "year": 2023,
    "quarter": null
  }
}
```

### 4. Document Node

```json
{
  "$schema": "http://json-schema.org/draft-07/schema#",
  "type": "object",
  "title": "Document",
  "description": "SEC 공시 문서를 나타내는 노드",
  "required": ["id", "node_type", "accession_number", "filing_type", "ticker", "node_style"],
  "properties": {
    "id": {
      "type": "string",
      "description": "고유 식별자 (예: 'doc_aapl_10k_0000320193-23-000106')",
      "pattern": "^doc_[a-z0-9_-]+$"
    },
    "node_type": {
      "type": "string",
      "description": "노드 타입",
      "const": "Document"
    },
    "node_style": {
      "type": "string",
      "description": "노드 스타일",
      "enum": ["static", "dynamic"],
      "const": "dynamic"
    },
    "accession_number": {
      "type": "string",
      "description": "SEC Accession Number",
      "pattern": "^\\d{10}-\\d{2}-\\d{6}$"
    },
    "filing_type": {
      "type": "string",
      "description": "공시 유형",
      "enum": ["10-K", "10-Q", "8-K"]
    },
    "ticker": {
      "type": "string",
      "description": "기업 티커",
      "pattern": "^[A-Z]{1,5}$"
    },
    "filing_date": {
      "type": "string",
      "format": "date",
      "description": "공시 제출일"
    },
    "period_end_date": {
      "type": "string",
      "format": "date",
      "description": "보고 기간 종료일"
    },
    "year": {
      "type": "integer",
      "description": "공시 연도"
    },
    "quarter": {
      "type": "integer",
      "description": "분기 (10-Q의 경우, 1-4)",
      "minimum": 1,
      "maximum": 4
    },
    "sections_included": {
      "type": "array",
      "description": "포함된 섹션 목록",
      "items": {
        "type": "string",
        "enum": ["business", "risk_factors", "mda", "financial_statements", "results_operations", "other_events"]
      }
    },
    "file_path": {
      "type": "string",
      "description": "원본 파일 경로"
    },
    "downloaded_at": {
      "type": "string",
      "format": "date-time",
      "description": "다운로드 시각"
    },
    "parsed_at": {
      "type": "string",
      "format": "date-time",
      "description": "파싱 시각"
    },
    "extracted_at": {
      "type": "string",
      "format": "date-time",
      "description": "Triplet 추출 시각"
    },
    "metadata": {
      "type": "object",
      "description": "추가 메타데이터",
      "properties": {
        "total_text_length": {
          "type": "integer",
          "description": "전체 문서 텍스트 길이"
        },
        "extraction_stats": {
          "type": "object",
          "description": "추출 통계",
          "properties": {
            "opportunities_count": {"type": "integer"},
            "risks_count": {"type": "integer"},
            "events_count": {"type": "integer"},
            "strategies_count": {"type": "integer"},
            "financials_count": {"type": "integer"}
          }
        }
      }
    }
  }
}
```

**샘플 데이터:**
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
  "file_path": "data/raw/AAPL/10-K/0000320193-23-000106/full-submission.txt",
  "downloaded_at": "2024-12-26T08:00:00Z",
  "parsed_at": "2024-12-26T10:00:00Z",
  "extracted_at": "2024-12-26T16:17:03Z",
  "metadata": {
    "total_text_length": 125000,
    "extraction_stats": {
      "opportunities_count": 8,
      "risks_count": 9,
      "events_count": 4,
      "strategies_count": 6,
      "financials_count": 6
    }
  }
}
```

### 5. Product Node

```json
{
  "$schema": "http://json-schema.org/draft-07/schema#",
  "type": "object",
  "title": "Product",
  "description": "제품/서비스를 나타내는 노드",
  "required": ["id", "node_type", "name", "product_type", "category", "description", "node_style"],
  "properties": {
    "id": {
      "type": "string",
      "description": "고유 식별자 (예: 'product_aapl_iphone15')",
      "pattern": "^product_[a-z0-9_]+$"
    },
    "node_type": {
      "type": "string",
      "description": "노드 타입",
      "const": "Product"
    },
    "node_style": {
      "type": "string",
      "description": "노드 스타일",
      "enum": ["static", "dynamic"],
      "const": "static"
    },
    "name": {
      "type": "string",
      "description": "제품/서비스 이름 (고유명사, 예: 'Tesla Model 3', 'iPhone 15 Pro', 'Azure Cloud Services'. 일반명사 'car', 'phone' 등은 사용하지 않음)",
      "examples": ["iPhone 15 Pro", "Apple Watch Ultra 2", "Tesla Model 3", "Azure Cloud Services", "NVIDIA H100 GPU"]
    },
    "product_type": {
      "type": "string",
      "description": "제품 유형",
      "enum": ["hardware", "software", "service", "platform", "other"]
    },
    "category": {
      "type": "string",
      "description": "제품 카테고리",
      "examples": ["smartphone", "wearable", "cloud_service", "electric_vehicle", "software_platform"]
    },
    "description": {
      "type": "string",
      "description": "제품/서비스에 대한 설명 (주요 기능, 특징, 용도 등)",
      "minLength": 10
    }
  }
}
```

**샘플 데이터:**
```json
{
  "id": "product_aapl_iphone15",
  "node_type": "Product",
  "name": "iPhone 15",
  "product_type": "hardware",
  "category": "smartphone",
  "description": "Apple의 최신 스마트폰으로, A17 Pro 칩셋, 48MP 메인 카메라, USB-C 포트, Dynamic Island 등의 기능을 제공하는 프리미엄 스마트폰입니다.",
  "node_style": "static"
}
```

### 6. Person Node

```json
{
  "$schema": "http://json-schema.org/draft-07/schema#",
  "type": "object",
  "title": "Person",
  "description": "인물 정보를 나타내는 노드",
  "required": ["id", "node_type", "name", "description", "node_style"],
  "properties": {
    "id": {
      "type": "string",
      "description": "고유 식별자 (예: 'person_aapl_tim_cook')",
      "pattern": "^person_[a-z0-9_]+$"
    },
    "node_type": {
      "type": "string",
      "description": "노드 타입",
      "const": "Person"
    },
    "node_style": {
        "type": "string",
      "description": "노드 스타일",
      "enum": ["static", "dynamic"],
      "const": "static"
    },
    "name": {
      "type": "string",
      "description": "인물 이름",
      "examples": ["Tim Cook", "Elon Musk", "Satya Nadella"]
    },
    "description": {
      "type": "string",
      "description": "인물에 대한 설명 (직책, 역할, 배경 등)",
      "minLength": 10
    }
  }
}
```

**샘플 데이터:**
```json
{
  "id": "person_aapl_tim_cook",
  "node_type": "Person",
  "name": "Tim Cook",
  "description": "Apple Inc.의 CEO로서 2011년부터 회사를 이끌고 있으며, 제품 개발 및 글로벌 운영 전략을 담당하고 있습니다.",
  "node_style": "static"
}
```

---

## 🔗 Link (Edge) 스키마 정의

### 1. HAS_RISKS

```json
{
  "$schema": "http://json-schema.org/draft-07/schema#",
  "type": "object",
  "title": "HAS_RISKS",
  "description": "Company와 Risk 간의 관계",
  "required": ["from", "to", "relationship_type"],
  "properties": {
    "from": {
      "type": "string",
      "description": "Company 노드 ID"
    },
    "to": {
      "type": "string",
      "description": "Risk 노드 ID"
    },
    "relationship_type": {
      "type": "string",
      "const": "HAS_RISKS"
    },
    "created_at": {
      "type": "string",
      "format": "date-time"
    },
    "metadata": {
      "type": "object",
      "properties": {
        "first_mentioned": {
          "type": "string",
          "format": "date"
        },
        "last_mentioned": {
          "type": "string",
          "format": "date"
        }
      }
    }
  }
}
```

**샘플 데이터:**
```json
{
  "from": "AAPL",
  "to": "risk_aapl_intense_competition_2023",
  "relationship_type": "HAS_RISKS",
  "created_at": "2024-12-26T16:17:03Z",
  "metadata": {
    "first_mentioned": "2023-01-01",
    "last_mentioned": "2023-11-03"
  }
}
```

### 2. HAS_OPPORTUNITIES

```json
{
  "$schema": "http://json-schema.org/draft-07/schema#",
  "type": "object",
  "title": "HAS_OPPORTUNITIES",
  "description": "Company와 Opportunity 간의 관계",
  "required": ["from", "to", "relationship_type"],
  "properties": {
    "from": {
      "type": "string",
      "description": "Company 노드 ID"
    },
    "to": {
      "type": "string",
      "description": "Opportunity 노드 ID"
    },
    "relationship_type": {
      "type": "string",
      "const": "HAS_OPPORTUNITIES"
    },
    "created_at": {
      "type": "string",
      "format": "date-time"
    },
    "metadata": {
      "type": "object",
      "properties": {
        "first_mentioned": {
          "type": "string",
          "format": "date"
        },
        "last_mentioned": {
          "type": "string",
          "format": "date"
        }
      }
    }
  }
}
```

**샘플 데이터:**
```json
{
  "from": "AAPL",
  "to": "opp_aapl_ecosystem_2023",
  "relationship_type": "HAS_OPPORTUNITIES",
  "created_at": "2024-12-26T16:17:03Z",
  "metadata": {
    "first_mentioned": "2023-01-01",
    "last_mentioned": "2023-11-03"
  }
}
```

### 3. HAS_EVENTS

```json
{
  "$schema": "http://json-schema.org/draft-07/schema#",
  "type": "object",
  "title": "HAS_EVENTS",
  "description": "Company와 Event 간의 관계",
  "required": ["from", "to", "relationship_type"],
  "properties": {
    "from": {
      "type": "string",
      "description": "Company 노드 ID"
    },
    "to": {
      "type": "string",
      "description": "Event 노드 ID"
    },
    "relationship_type": {
      "type": "string",
      "const": "HAS_EVENTS"
    },
    "created_at": {
      "type": "string",
      "format": "date-time"
    },
    "metadata": {
      "type": "object",
      "properties": {
        "event_date": {
          "type": "string",
          "format": "date"
        }
      }
    }
  }
}
```

**샘플 데이터:**
```json
{
  "from": "AAPL",
  "to": "event_aapl_iphone15_2023",
  "relationship_type": "HAS_EVENTS",
  "created_at": "2024-12-26T16:17:03Z",
  "metadata": {
    "event_date": "2023-09-01"
  }
}
```

### 4. HAS_TECHNOLOGIES

```json
{
  "$schema": "http://json-schema.org/draft-07/schema#",
  "type": "object",
  "title": "HAS_TECHNOLOGIES",
  "description": "Company와 Technology 간의 관계",
  "required": ["from", "to", "relationship_type"],
  "properties": {
    "from": {
      "type": "string",
      "description": "Company 노드 ID"
    },
    "to": {
      "type": "string",
      "description": "Technology 노드 ID"
    },
    "relationship_type": {
      "type": "string",
      "const": "HAS_TECHNOLOGIES"
    },
    "created_at": {
      "type": "string",
      "format": "date-time"
    },
    "metadata": {
      "type": "object",
      "properties": {
        "first_mentioned": {
          "type": "string",
          "format": "date"
        },
        "last_mentioned": {
          "type": "string",
          "format": "date"
        }
      }
    }
  }
}
```

**샘플 데이터:**
```json
{
  "from": "AAPL",
  "to": "tech_aapl_a17_pro_chip_2023",
  "relationship_type": "HAS_TECHNOLOGIES",
  "created_at": "2024-12-26T16:17:03Z",
  "metadata": {
    "first_mentioned": "2023-01-01",
    "last_mentioned": "2023-11-03"
  }
}
```

### 5. IS_EXTRACTED_FROM

```json
{
  "$schema": "http://json-schema.org/draft-07/schema#",
  "type": "object",
  "title": "IS_EXTRACTED_FROM",
  "description": "Risk/Opportunity/Event/Technology와 Section 간의 관계",
  "required": ["from", "to", "relationship_type"],
  "properties": {
    "from": {
      "type": "string",
      "description": "Risk/Opportunity/Event/Technology 노드 ID"
    },
    "to": {
      "type": "string",
      "description": "Section 노드 ID"
    },
    "relationship_type": {
      "type": "string",
      "const": "IS_EXTRACTED_FROM"
    },
    "created_at": {
      "type": "string",
      "format": "date-time"
    },
    "metadata": {
      "type": "object",
      "properties": {
        "extraction_method": {
          "type": "string",
          "enum": ["llm_extraction", "manual"]
        },
        "confidence": {
          "type": "number",
          "minimum": 0,
          "maximum": 1
        }
      }
    }
  }
}
```

**샘플 데이터:**
```json
{
  "from": "risk_aapl_intense_competition_2023",
  "to": "section_aapl_10k_2023_business",
  "relationship_type": "IS_EXTRACTED_FROM",
  "created_at": "2024-12-26T16:17:03Z",
  "metadata": {
    "extraction_method": "llm_extraction",
    "confidence": 0.95
  }
}
```

### 6. IS_INCLUDED

```json
{
  "$schema": "http://json-schema.org/draft-07/schema#",
  "type": "object",
  "title": "IS_INCLUDED",
  "description": "Section과 Document 간의 관계",
  "required": ["from", "to", "relationship_type"],
  "properties": {
    "from": {
      "type": "string",
      "description": "Section 노드 ID"
    },
    "to": {
      "type": "string",
      "description": "Document 노드 ID"
    },
    "relationship_type": {
      "type": "string",
      "const": "IS_INCLUDED"
    },
    "created_at": {
      "type": "string",
      "format": "date-time"
    },
    "metadata": {
      "type": "object",
      "properties": {
        "section_order": {
          "type": "integer",
          "description": "문서 내 섹션 순서"
        }
      }
    }
  }
}
```

**샘플 데이터:**
```json
{
  "from": "section_aapl_10k_2023_business",
  "to": "doc_aapl_10k_0000320193-23-000106",
  "relationship_type": "IS_INCLUDED",
  "created_at": "2024-12-26T10:00:00Z",
  "metadata": {
    "section_order": 1
  }
}
```

### 7. MAKE

```json
{
  "$schema": "http://json-schema.org/draft-07/schema#",
  "type": "object",
  "title": "MAKE",
  "description": "Company와 Product 간의 관계",
  "required": ["from", "to", "relationship_type"],
  "properties": {
    "from": {
      "type": "string",
      "description": "Company 노드 ID"
    },
    "to": {
      "type": "string",
      "description": "Product 노드 ID"
    },
    "relationship_type": {
      "type": "string",
      "const": "MAKE"
    },
    "created_at": {
      "type": "string",
      "format": "date-time"
    },
    "metadata": {
      "type": "object",
      "properties": {
        "launch_date": {
          "type": "string",
          "format": "date"
        },
        "status": {
          "type": "string",
          "enum": ["active", "discontinued", "upcoming"]
        }
      }
    }
  }
}
```

**샘플 데이터:**
```json
{
  "from": "AAPL",
  "to": "product_aapl_iphone15",
  "relationship_type": "MAKE",
  "created_at": "2024-12-26T16:17:03Z",
  "metadata": {
    "launch_date": "2023-09-01",
    "status": "active"
  }
}
```

### 8. HAS_RELATION

```json
{
  "$schema": "http://json-schema.org/draft-07/schema#",
  "type": "object",
  "title": "HAS_RELATION",
  "description": "Company와 Person 간의 관계",
  "required": ["from", "to", "relationship_type", "role"],
  "properties": {
    "from": {
      "type": "string",
      "description": "Company 노드 ID"
    },
    "to": {
      "type": "string",
      "description": "Person 노드 ID"
    },
    "relationship_type": {
      "type": "string",
      "const": "HAS_RELATION"
    },
    "role": {
      "type": "string",
      "description": "Person의 역할/직책",
      "examples": ["CEO", "CFO", "CTO", "Board Member", "Executive", "Director"]
    },
    "created_at": {
      "type": "string",
      "format": "date-time"
    },
    "metadata": {
      "type": "object",
      "properties": {
        "start_date": {
          "type": "string",
          "format": "date",
          "description": "역할 시작일"
        },
        "end_date": {
          "type": "string",
          "format": "date",
          "description": "역할 종료일 (현재 역할인 경우 null)"
        }
      }
    }
  }
}
```

**샘플 데이터:**
```json
{
  "from": "AAPL",
  "to": "person_aapl_tim_cook",
  "relationship_type": "HAS_RELATION",
  "role": "CEO",
  "created_at": "2024-12-26T16:17:03Z",
  "metadata": {
    "start_date": "2011-08-24",
    "end_date": null
  }
}
```

### 9. IS_MENTIONED_IN

```json
{
  "$schema": "http://json-schema.org/draft-07/schema#",
  "type": "object",
  "title": "IS_MENTIONED_IN",
  "description": "Product/Person/Company와 Risk/Opportunity/Event/Technology 간의 관계",
  "required": ["from", "to", "relationship_type", "mention_context"],
  "properties": {
    "from": {
      "type": "string",
      "description": "Product, Person, 또는 Company 노드 ID"
    },
    "to": {
      "type": "string",
      "description": "Risk/Opportunity/Event/Technology 노드 ID"
    },
    "relationship_type": {
      "type": "string",
      "const": "IS_MENTIONED_IN"
        },
        "mention_context": {
          "type": "string",
      "description": "언급된 컨텍스트 요약 (필수 속성)",
      "minLength": 1
    },
    "created_at": {
      "type": "string",
      "format": "date-time"
    },
    "metadata": {
      "type": "object",
      "properties": {
        "mention_type": {
          "type": "string",
          "enum": ["risk", "opportunity", "event", "technology"]
        }
      }
    }
  }
}
```

**샘플 데이터:**

**Product → Risk/Opportunity/Event:**
```json
{
  "from": "product_aapl_iphone15",
  "to": "event_aapl_iphone15_2023",
  "relationship_type": "IS_MENTIONED_IN",
  "mention_context": "iPhone 15 was launched as part of the company's product lineup",
  "created_at": "2024-12-26T16:17:03Z",
  "metadata": {
    "mention_type": "event"
  }
}
```

**Person → Risk/Opportunity/Event:**
```json
{
  "from": "person_aapl_tim_cook",
  "to": "opp_aapl_ecosystem_2023",
  "relationship_type": "IS_MENTIONED_IN",
  "mention_context": "Tim Cook discussed the integrated ecosystem strategy during the earnings call",
  "created_at": "2024-12-26T16:17:03Z",
  "metadata": {
    "mention_type": "opportunity"
  }
}
```

**Company → Risk/Opportunity/Event:**
```json
{
  "from": "SSNLF",
  "to": "risk_aapl_intense_competition_2023",
  "relationship_type": "IS_MENTIONED_IN",
  "mention_context": "Samsung mentioned as competitor in price competition",
  "created_at": "2024-12-26T16:17:03Z",
  "metadata": {
    "mention_type": "risk"
  }
}
```

---

## 📐 Graph 구조 다이어그램

### 전체 구조

```
                    ┌─────────────┐
                    │   Company   │
                    │  (AAPL)     │
                    └──────┬──────┘
                           │
        ┌──────────────────┼──────────────────┐
        │                  │                  │
   [HAS_RISKS]    [HAS_OPPORTUNITIES]    [HAS_EVENTS]
        │                  │                  │
        │                  │                  │
┌───────▼───────┐  ┌───────▼───────┐  ┌───────▼───────┐
│     Risk      │  │  Opportunity  │  │     Event     │
│               │  │               │  │               │
│ entity:       │  │ entity:       │  │ entity:       │
│ "Intense      │  │ "Integrated   │  │ "iPhone 15    │
│  Competition" │  │  Ecosystem"   │  │  Launch"      │
└───────┬───────┘  └───────┬───────┘  └───────┬───────┘
        │                  │                  │
        │                  │                  │
        └──────────────────┼──────────────────┘
                           │
                  [IS_EXTRACTED_FROM]
                           │
                  ┌────────▼────────┐
                  │     Section     │
                  │  (business,     │
                  │   risk_factors) │
                  └────────┬────────┘
                           │
                  [IS_INCLUDED]
                           │
                  ┌────────▼────────┐
                  │    Document     │
                  │  (10-K,         │
                  │   accession)    │
                  └─────────────────┘

┌─────────────┐
│   Company   │
│   (AAPL)    │
└──────┬──────┘
       │
       ├──────────────┬────────────┐
       │              │            │
     [MAKE]    [HAS_RELATION]   [HAS_RISKS]
       │            {role}         │
       │              │            │
┌──────▼──────┐  ┌───▼─────┐       │
│   Product   │  │ Person  │       │
│ (iPhone 15) │  │(Tim Cook│       │
└──────┬──────┘  └────┬────┘       │
       │              │            │
       [IS_MENTIONED_IN]           │
       │              │            │
       └──────────────┴────────────┘
                      │
              ┌───────▼──────┐
              │     Risk     │
              │ "Supply      │
              │  Chain Risk" │
              └──────────────┘
                                               
              (Company, Product, Person이 동일한 Risk 노드에 연결)
```

### 관계 체인 예시

**질의: "애플의 기회 요소를 알려줘"**

```
(AAPL) 
  └─[HAS_OPPORTUNITIES]→ (opp_aapl_ecosystem_2023)
                            └─[IS_EXTRACTED_FROM]→ (section_aapl_10k_2023_risk_factors)
                                                    └─[IS_INCLUDED]→ (doc_aapl_10k_0000320193-23-000106)
```

**질의: "iPhone 15와 관련된 리스크는?"**

```
(product_aapl_iphone15)
  └─[IS_MENTIONED_IN]→ (risk_aapl_supply_chain_2023)
                          └─[IS_EXTRACTED_FROM]→ (section_aapl_10k_2023_business)
                                                  └─[IS_INCLUDED]→ (doc_aapl_10k_0000320193-23-000106)
```

---

## 🔍 실제 데이터 매핑 예시

### 예시: AAPL 10-K 2023

**Document Node:**
```json
{
  "id": "doc_aapl_10k_0000320193-23-000106",
  "node_type": "Document",
  "accession_number": "0000320193-23-000106",
  "filing_type": "10-K",
  "ticker": "AAPL",
  "year": 2023,
  "sections_included": ["business", "risk_factors"]
}
```

**Section Nodes:**
```json
[
  {
    "id": "section_aapl_10k_2023_business",
    "node_type": "Section",
    "section_name": "business",
    "filing_type": "10-K",
    "ticker": "AAPL",
    "accession_number": "0000320193-23-000106"
  },
  {
    "id": "section_aapl_10k_2023_risk_factors",
    "node_type": "Section",
    "section_name": "risk_factors",
    "filing_type": "10-K",
    "ticker": "AAPL",
    "accession_number": "0000320193-23-000106"
  }
]
```

**Risk Node:**
```json
{
  "id": "risk_aapl_intense_competition_2023",
  "node_type": "Risk",
  "entity": "Intense Price Competition",
  "description": "The Company faces aggressive price competition...",
  "metadata": {
    "source_section": "business",
    "filing_type": "10-K",
    "accession_number": "0000320193-23-000106"
  }
}
```

**Opportunity Node:**
```json
{
  "id": "opp_aapl_ecosystem_2023",
  "node_type": "Opportunity",
  "entity": "Integrated Ecosystem Strategy",
  "description": "The Company focuses on the integration of hardware...",
  "metadata": {
    "source_section": "risk_factors",
    "filing_type": "10-K",
    "accession_number": "0000320193-23-000106"
  }
}
```

**Event Node:**
```json
{
  "id": "event_aapl_iphone15_2023",
  "node_type": "Event",
  "entity": "Release of iPhone 15 Lineup",
  "description": "The Company introduced the iPhone 15 Pro...",
  "date": "2023",
  "date_parsed": "2023-01-01",
  "metadata": {
    "source_section": "business",
    "filing_type": "10-K",
    "accession_number": "0000320193-23-000106",
    "event_type": "product_launch"
  }
}
```

**Product Node (추출 필요):**
```json
{
  "id": "product_aapl_iphone15",
  "node_type": "Product",
  "name": "iPhone 15",
  "product_type": "hardware",
  "category": "smartphone",
  "first_mentioned_date": "2023-01-01",
  "mentioned_in": ["event"]
}
```

**Links (전체 관계 체인):**
```
# Company → Risk/Opportunity/Event
(AAPL) -[HAS_RISKS]-> (risk_aapl_intense_competition_2023)
(AAPL) -[HAS_OPPORTUNITIES]-> (opp_aapl_ecosystem_2023)
(AAPL) -[HAS_EVENTS]-> (event_aapl_iphone15_2023)

# Risk/Opportunity/Event → Section
(risk_aapl_intense_competition_2023) -[IS_EXTRACTED_FROM]-> (section_aapl_10k_2023_business)
(opp_aapl_ecosystem_2023) -[IS_EXTRACTED_FROM]-> (section_aapl_10k_2023_risk_factors)
(event_aapl_iphone15_2023) -[IS_EXTRACTED_FROM]-> (section_aapl_10k_2023_business)

# Section → Document
(section_aapl_10k_2023_business) -[IS_INCLUDED]-> (doc_aapl_10k_0000320193-23-000106)
(section_aapl_10k_2023_risk_factors) -[IS_INCLUDED]-> (doc_aapl_10k_0000320193-23-000106)

# Company → Product
(AAPL) -[MAKE]-> (product_aapl_iphone15)
(AAPL) -[MAKE]-> (product_aapl_applewatch_ultra2)

# Company → Person
(AAPL) -[HAS_RELATION {role: "CEO"}]-> (person_aapl_tim_cook)
(AAPL) -[HAS_RELATION {role: "CFO"}]-> (person_aapl_luca_maestri)

# Product → Risk/Opportunity/Event
(product_aapl_iphone15) -[IS_MENTIONED_IN {mention_context: "..."}]-> (event_aapl_iphone15_2023)
(product_aapl_iphone15) -[IS_MENTIONED_IN {mention_context: "..."}]-> (risk_aapl_supply_chain_2023)
(product_aapl_applepay) -[IS_MENTIONED_IN {mention_context: "..."}]-> (opp_aapl_payments_2023)

# Person → Risk/Opportunity/Event
(person_aapl_tim_cook) -[IS_MENTIONED_IN {mention_context: "..."}]-> (event_aapl_iphone15_2023)
(person_aapl_tim_cook) -[IS_MENTIONED_IN {mention_context: "..."}]-> (opp_aapl_ecosystem_2023)

# Company → Risk/Opportunity/Event
(SSNLF) -[IS_MENTIONED_IN {mention_context: "Samsung mentioned as competitor"}]-> (risk_aapl_intense_competition_2023)
```

### 실제 데이터에서 추출 가능한 Product 예시

**AAPL 10-K 2023에서:**
- Event: "Release of iPhone 15 Lineup" → Product: "iPhone 15"
- Event: "Launch of Apple Watch Ultra 2" → Product: "Apple Watch Ultra 2"
- Opportunity: "Apple Pay, Apple Card" → Product: "Apple Pay", "Apple Card"
- Opportunity: "Apple TV+, Apple Music" → Product: "Apple TV+", "Apple Music"

**TSLA 10-K 2025에서:**
- Opportunity: "Megapack" → Product: "Megapack"
- Opportunity: "Robotaxi" → Product: "Robotaxi"
- Event: "NACS standardization" → Product: "NACS Charging Standard"

---

## 📝 구현 고려사항

### 1. Product 추출 전략

Product는 현재 명시적으로 추출되지 않으므로, 다음 방법으로 추출:

#### 방법 1: Event Entity에서 추출
- **패턴**: Event entity에 제품명이 포함된 경우
- **예시**: 
  - "Release of iPhone 15 Lineup" → Product: "iPhone 15"
  - "Launch of Apple Watch Ultra 2" → Product: "Apple Watch Ultra 2"
- **구현**: 정규식 또는 LLM을 통한 제품명 추출

#### 방법 2: Description에서 NER (Named Entity Recognition)
- **대상**: Opportunities, Risks, Events의 description
- **예시**:
  - "Apple Pay", "Apple Card" → Product: "Apple Pay", "Apple Card"
  - "Tesla Model 3", "Megapack" → Product: "Model 3", "Megapack"
- **구현**: LLM 기반 NER 또는 사전 기반 매칭

#### 방법 3: 별도 Product 추출 단계
- **프롬프트 추가**: `triplet_extractor.yaml`에 products 카테고리 추가
- **장점**: 명시적이고 정확한 추출
- **단점**: API 호출 증가

#### 방법 4: 하이브리드 접근 (권장)
1. Event entity에서 제품명 추출 (고정밀도)
2. Description에서 NER 수행 (보완)
3. Company별 제품 사전 활용 (검증)

### 2. Product/Person/Company-Entity 연결 전략

Product/Person/Company가 Risk/Opportunity/Event에 언급된 경우:
- **자동 연결**: Description에 제품명/인물명/회사명이 포함된 경우 `IS_MENTIONED_IN` 링크 생성 (mention_context 필수)
- **LLM 검증**: 제품명/인물명/회사명이 실제로 해당 컨텍스트에서 의미 있게 언급되었는지 검증
- **mention_context**: 언급된 컨텍스트를 요약하여 링크의 필수 속성으로 저장

### 2. ID 생성 규칙

- **Company**: `{ticker}` (예: `AAPL`)
- **Risk**: `risk_{ticker}_{normalized_entity}_{year}` (예: `risk_aapl_intense_competition_2023`)
  - `normalized_entity`: 소문자, 공백/특수문자 → 언더스코어
- **Opportunity**: `opp_{ticker}_{normalized_entity}_{year}` (예: `opp_aapl_ecosystem_2023`)
- **Event**: `event_{ticker}_{normalized_entity}_{year}` (예: `event_aapl_iphone15_2023`)
- **Section**: `section_{ticker}_{filing_type}_{year}_{section_name}` (예: `section_aapl_10k_2023_business`)
- **Document**: `doc_{ticker}_{filing_type}_{accession_number}` (예: `doc_aapl_10k_0000320193-23-000106`)
- **Product**: `product_{ticker}_{normalized_name}` (예: `product_aapl_iphone15_pro`, `product_tsla_model_3`)
  - `normalized_name`: 소문자, 공백/특수문자 → 언더스코어
  - **중요**: name은 고유명사여야 함 (예: "Tesla Model 3", "iPhone 15 Pro". 일반명사 "car", "phone" 등은 사용하지 않음)
- **Person**: `person_{ticker}_{normalized_name}` (예: `person_aapl_tim_cook`)
  - `normalized_name`: 소문자, 공백/특수문자 → 언더스코어

**ID 정규화 함수 예시:**
```python
def normalize_id(text: str) -> str:
    """텍스트를 ID로 사용 가능한 형태로 정규화"""
    import re
    # 소문자 변환
    text = text.lower()
    # 특수문자 제거 또는 언더스코어로 변환
    text = re.sub(r'[^a-z0-9]+', '_', text)
    # 연속된 언더스코어 제거
    text = re.sub(r'_+', '_', text)
    # 앞뒤 언더스코어 제거
    return text.strip('_')
```

### 3. Vector DB 통합

Vector DB는 의미 기반 검색을 위해 다음 엔티티의 텍스트를 벡터화합니다:

| Node 타입 | 벡터화 대상 텍스트 | 용도 |
|-----------|------------------|------|
| **Document** | `full_text` (전체 문서 텍스트) | 문서 레벨 유사도 검색 |
| **Section** | `section_text` (섹션 원문 텍스트) | 섹션 레벨 유사도 검색 |
| **Risk** | `entity + description` | 위험 요소 의미 검색 |
| **Opportunity** | `entity + description` | 기회 요소 의미 검색 |
| **Event** | `entity + description + date` | 이벤트 의미 검색 |
| **Product** | `name + category + description` | 제품 의미 검색 |
| **Person** | `name + description` | 인물 의미 검색 |

**임베딩 모델**: Gemini Embedding API (`embedding-001`) 또는 동등한 모델

**검색 전략**:
- **하이브리드 검색**: Graph 검색 결과와 Vector 검색 결과를 결합
- **재랭킹**: Graph 구조 정보와 벡터 유사도를 결합하여 최종 순위 결정

### 4. 중복 처리 전략

#### 옵션 A: 연도별 별도 노드 (권장)
- **장점**: 시간적 변화 추적 가능, 연도별 필터링 용이
- **단점**: 노드 수 증가
- **예시**: 
  - `risk_aapl_competition_2022`
  - `risk_aapl_competition_2023`
  - `risk_aapl_competition_2024`

#### 옵션 B: 단일 노드 + 메타데이터
- **장점**: 노드 수 감소, 중복 제거
- **단점**: 시간적 추적 복잡
- **구현**: 
  - `risk_aapl_competition` (단일 노드)
  - `metadata.years`: [2022, 2023, 2024]
  - `metadata.sources`: [accession_number 리스트]

#### 권장 방식: 하이브리드
- **Risk/Opportunity/Event**: 연도별 별도 노드 (시간적 추적 중요)
- **Product**: 단일 노드 (제품은 지속적)
- **Section/Document**: 단일 노드 (이미 고유함)

---

## 🎯 질의 예시

### 질의 1: "애플의 기회 요소를 알려줘"

**Graph Query (Cypher-like):**
```cypher
MATCH (c:Company {ticker: "AAPL"})-[r:HAS_OPPORTUNITIES]->(o:Opportunity)
MATCH (o)-[r2:IS_EXTRACTED_FROM]->(s:Section)
MATCH (s)-[r3:IS_INCLUDED]->(d:Document)
RETURN o.entity, o.description, s.section_name, d.filing_type, d.year
ORDER BY d.year DESC
```

**Vector Search:**
- Query: "Apple opportunities growth drivers"
- Search in: Opportunity nodes
- Filter: ticker = "AAPL"

**결합**: Graph 결과와 Vector 결과를 재랭킹하여 최종 답변 생성

### 질의 2: "iPhone 15와 관련된 리스크는?"

**Graph Query:**
```cypher
MATCH (p:Product {name: "iPhone 15"})-[r:IS_MENTIONED_IN]->(risk:Risk)
MATCH (risk)-[r2:IS_EXTRACTED_FROM]->(s:Section)
MATCH (s)-[r3:IS_INCLUDED]->(d:Document)
RETURN risk.entity, risk.description, d.filing_type, d.year
```

**Vector Search:**
- Query: "iPhone 15 risks vulnerabilities"
- Search in: Risk nodes
- Filter: description contains "iPhone 15"

### 질의 3: "2023년 애플의 주요 이벤트와 관련 제품"

**Graph Query:**
```cypher
MATCH (c:Company {ticker: "AAPL"})-[r1:HAS_EVENTS]->(e:Event)
WHERE e.date_parsed >= "2023-01-01" AND e.date_parsed < "2024-01-01"
OPTIONAL MATCH (p:Product)-[r2:IS_MENTIONED_IN]->(e)
RETURN e.entity, e.date, e.description, 
       COLLECT(p.name) as products,
       e.metadata.source_section
ORDER BY e.date_parsed DESC
```

### 질의 4: "테슬라와 엔비디아의 공통 리스크는?"

**Graph Query:**
```cypher
MATCH (c1:Company {ticker: "TSLA"})-[r1:HAS_RISKS]->(r:Risk)
MATCH (c2:Company {ticker: "NVDA"})-[r2:HAS_RISKS]->(r)
RETURN r.entity, r.description,
       COLLECT(DISTINCT c1.ticker + c2.ticker) as companies
```

**Vector Search:**
- Query: "Tesla NVIDIA common risks"
- Search in: Risk nodes
- Filter: ticker IN ["TSLA", "NVDA"]
- Group by: entity similarity

---

## 🔄 데이터 적재 프로세스

### 1. Document & Section 생성
```
extracted JSON → Document Node 생성
              → Section Nodes 생성 (sections_included 기반)
              → [IS_INCLUDED] 링크 생성
```

### 2. Risk/Opportunity/Event 생성
```
extracted JSON → Risk/Opportunity/Event Nodes 생성
              → [HAS_RISKS/HAS_OPPORTUNITIES/HAS_EVENTS] 링크 생성
              → [IS_EXTRACTED_FROM] 링크 생성 (Section 연결)
```

### 3. Product 추출 및 생성
```
Event/Opportunity/Risk description → Product 추출 (NER/LLM)
                                  → Product Nodes 생성
                                  → [MAKE] 링크 생성 (Company 연결)
                                  → [IS_MENTIONED_IN] 링크 생성 (mention_context 포함)
```

### 4. Person 추출 및 생성
```
Document/Section 텍스트 → Person 추출 (NER/LLM)
                       → Person Nodes 생성
                       → [HAS_RELATION] 링크 생성 (Company 연결, role 속성 포함)
                       → [IS_MENTIONED_IN] 링크 생성 (Risk/Opportunity/Event 연결, mention_context 포함)
```

### 4.5. Company 추출 및 연결
```
Risk/Opportunity/Event description → Company 추출 (competitor, partner 등)
                                   → [IS_MENTIONED_IN] 링크 생성 (Risk/Opportunity/Event 연결, mention_context 포함)
```

### 5. Vector Embedding 생성
```
각 Node의 텍스트 → Embedding 생성 → Vector DB 저장
```

### 6. Graph + Vector 통합 검색
```
사용자 질의 → Graph Query 실행
           → Vector Search 실행
           → 결과 재랭킹
           → 최종 답변 생성
```

---

## 📋 요약

### Node 타입 (6개)
1. **Company**: 기업 기본 정보
2. **Risk/Opportunity/Event/Technology**: 위험 요소, 기회 요소, 주요 이벤트, 기술 (통합 스키마, node_type으로 구분)
3. **Section**: 파싱된 섹션 (section_name, filing_type, ticker)
4. **Document**: SEC 공시 문서 (accession_number, filing_type, ticker, year)
5. **Product**: 제품/서비스 (name, product_type, category, description)
6. **Person**: 인물 (name, description)

### Link 타입 (9개)
1. **HAS_RISKS**: Company → Risk
2. **HAS_OPPORTUNITIES**: Company → Opportunity
3. **HAS_EVENTS**: Company → Event
4. **HAS_TECHNOLOGIES**: Company → Technology
5. **IS_EXTRACTED_FROM**: Risk/Opportunity/Event/Technology → Section
6. **IS_INCLUDED**: Section → Document
7. **MAKE**: Company → Product
8. **HAS_RELATION**: Company → Person (role 속성 포함)
9. **IS_MENTIONED_IN**: Product/Person/Company → Risk/Opportunity/Event/Technology (mention_context 속성 포함)

### 주요 특징
- **출처 추적**: 모든 엔티티는 Section과 Document까지 추적 가능
- **시간적 추적**: 연도별 노드 생성으로 시간에 따른 변화 추적
- **제품 연결**: Product를 통해 Risk/Opportunity/Event/Technology와 연결 (IS_MENTIONED_IN, mention_context 포함)
- **인물 연결**: Person을 통해 Risk/Opportunity/Event/Technology와 연결, Company와의 관계는 role 속성으로 표현 (IS_MENTIONED_IN, mention_context 포함)
- **회사 연결**: Company를 통해 Risk/Opportunity/Event/Technology와 연결 (competitor, partner 등, IS_MENTIONED_IN, mention_context 포함)
- **기술 추적**: Technology 노드를 통해 기업의 기술 혁신 및 R&D 활동 추적
- **하이브리드 검색**: Graph 구조 검색 + Vector 의미 검색 결합

### 다음 단계
1. Graph 적재 로직 구현 (`app/services/graph_loader.py`)
2. Product 추출 로직 구현 (`app/services/product_extractor.py`)
3. Vector DB 통합 (`app/services/vector_store.py`)
4. 하이브리드 검색 엔진 구현 (`app/services/hybrid_search.py`)

