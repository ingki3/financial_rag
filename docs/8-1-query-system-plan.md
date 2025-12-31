# Phase 8: 질의 응답 시스템 구현 계획

## 📌 개요

Phase 8에서는 사용자의 자연어 질의를 분석하여 Knowledge Graph에서 관련 정보를 검색하고, 구조화된 답변을 생성하는 질의 응답 시스템을 구현합니다.

**핵심 목표**:
1. 자연어 질의에서 의도(Intent) 추출
2. Graph 기반 구조적 검색 + Vector 기반 의미 검색 통합
3. 검색 결과를 바탕으로 한 답변 생성

---

## 🏗 시스템 아키텍처

### 전체 흐름

```
사용자 질의
    ↓
[1] Intent 추출 (extract_intent)
    ├─ 알고 싶은 것 (Target Entity Type)
    ├─ 검색 쿼리 (Query Text)
    └─ 필터 조건 (Filters: Company, Context, Time, etc.)
    ↓
[2] Graph 검색 (graph_search)
    └─ Cypher 쿼리 생성 및 실행
    ↓
[3] Vector 검색 (vector_search)
    └─ Embedding 기반 유사도 검색
    ↓
[4] 결과 통합 (merge_results)
    └─ RRF 또는 가중치 기반 통합
    ↓
[5] 재랭킹 (rerank, 선택적)
    └─ Cross-encoder 기반 재랭킹
    ↓
[6] 답변 생성 (generate_answer)
    └─ LLM을 통한 자연어 답변 생성
    ↓
최종 답변
```

---

## 🔍 1. Intent 추출 (extract_intent)

### 1.1 설계 원칙

사용자 질의에서 다음 두 가지를 분류합니다:

1. **알고 싶어 하는 것 (Target Entity Type)**
   - **종류**: 어떤 노드 타입을 검색해야 하는지 판단
   - **내용**: Vector 검색에 사용할 쿼리 텍스트
   - 예: "리스크 항목" → 노드 타입: `Risk`, 쿼리: "리스크 항목"

2. **알고 싶어 하는 것에 대한 맥락 (Context/Filters)**
   - **종류**: 필터 조건의 타입 (Company, Time, Section, Product, etc.)
   - **내용**: 필터 조건의 구체적 값
   - 예: "애플" → 필터: `{type: "company", value: "AAPL"}`
   - 예: "사업상" → 필터: `{type: "context", value: "business"}`

### 1.2 Intent 구조

```python
{
    "target_entity_type": "Risk",  # 또는 "Opportunity", "Event", "Technology", "Product", "Person", "general"
    "query_text": "리스크 항목",  # Vector 검색에 사용할 텍스트
    "filters": {
        "company": "AAPL",  # 티커 심볼
        "context": ["business", "사업상"],  # 맥락 키워드
        "time": {  # 시간 필터
            "year": 2023,
            "period": "recent"  # 또는 "all", "2023", "2022-2023"
        },
        "section": "risk_factors",  # 섹션 필터
        "filing_type": "10-K",  # 공시 유형 필터
        "product": "iPhone 15",  # 제품 필터
        "person": "Tim Cook"  # 인물 필터
    },
    "query_type": "explain",  # 또는 "list", "compare", "analyze"
    "expansion": {  # 확장 검색 옵션
        "include_related_products": True,
        "include_related_persons": True,
        "include_related_companies": False
    }
}
```

### 1.3 구현 방법

#### 1.3.1 Gemini 기반 Intent 추출 (Phase 1)

Gemini 모델을 사용하여 사용자 질의에서 구조화된 Intent를 추출합니다. JSON 스키마 기반 구조화된 출력을 활용하여 일관된 형식의 Intent를 생성합니다.

**모델 설정**:
- 모델: `gemini-3-flash-preview` (또는 `gemini-2.0-flash-exp`)
- API: `google.generativeai`
- 출력 형식: JSON (structured output)

**구현 구조**:
```python
import google.generativeai as genai
from typing import Dict, Optional
import json

class IntentExtractor:
    """Gemini를 활용한 Intent 추출 클래스"""
    
    def __init__(self, model: str = "gemini-3-flash-preview", api_key: Optional[str] = None):
        self.model = model
        api_key = api_key or os.getenv("GEMINI_API_KEY") or os.getenv("GOOGLE_API_KEY")
        genai.configure(api_key=api_key)
        self.client = genai.GenerativeModel(
            model_name=self.model,
            generation_config={
                "response_mime_type": "application/json",
                "response_schema": self._get_intent_schema()
            }
        )
    
    async def extract_intent(self, query: str) -> Dict:
        """질의에서 Intent 추출"""
        prompt = self._build_intent_prompt(query)
        response = await self.client.generate_content_async(prompt)
        intent = json.loads(response.text)
        return self._validate_and_normalize(intent)
```

**Prompt 템플릿**:

```python
INTENT_EXTRACTION_PROMPT = """
당신은 금융 공시 문서 기반 Knowledge Graph 질의 시스템의 Intent 추출 전문가입니다.

사용자의 자연어 질의를 분석하여 다음 정보를 추출하세요:

1. **target_entity_type**: 사용자가 알고 싶어 하는 노드 타입
   - 가능한 값: "Risk", "Opportunity", "Event", "Technology", "Product", "Person", "general"
   - "general"은 특정 노드 타입이 명확하지 않을 때 사용

2. **query_text**: Vector 검색에 사용할 핵심 질의 텍스트
   - Entity type 키워드와 필터 키워드를 제외한 핵심 내용
   - 예: "애플의 사업상 리스크" → "리스크" (또는 "사업상 리스크")

3. **filters**: 검색 필터 조건
   - **company**: 기업 티커 심볼 (예: "AAPL", "TSLA", "GOOGL", "MSFT", "META", "NVDA", "AMZN")
     - 한국어 기업명도 티커로 변환: "애플" → "AAPL", "테슬라" → "TSLA", "구글" → "GOOGL", "마이크로소프트" → "MSFT", "메타" → "META", "엔비디아" → "NVDA", "아마존" → "AMZN"
   - **context**: 맥락 키워드 배열 (예: ["business", "사업상"], ["financial", "재무적"])
     - 가능한 값: "business", "financial", "operational", "regulatory", "competitive", "market"
   - **time**: 시간 필터
     - **year**: 특정 연도 (예: 2023)
     - **period**: 기간 (예: "recent", "2022-2023", "all")
   - **section**: 섹션 필터 (예: "risk_factors", "business", "mda")
   - **filing_type**: 공시 유형 (예: "10-K", "10-Q", "8-K")
   - **product**: 제품명 (예: "iPhone 15", "Office 365")
   - **person**: 인물명 (예: "Tim Cook", "Elon Musk")

4. **query_type**: 질의 유형
   - "explain": 설명 요청 (예: "설명해줘", "알려줘", "어떻게")
   - "list": 목록 요청 (예: "목록", "보여줘", "나열")
   - "compare": 비교 요청 (예: "비교", "대비", "차이")
   - "analyze": 분석 요청 (예: "분석", "평가", "검토")

5. **expansion**: 확장 검색 옵션
   - **include_related_products**: 관련 제품 포함 여부 (기본: true)
   - **include_related_persons**: 관련 인물 포함 여부 (기본: false)
   - **include_related_companies**: 관련 기업 포함 여부 (기본: false)

**중요 규칙**:
- 질의에 명시되지 않은 필터는 null로 설정
- 다중 기업 비교 질의의 경우 company를 배열로 설정 (예: ["NVDA", "AAPL"])
- 다중 Entity Type 질의의 경우 target_entity_type을 배열로 설정 (예: ["Opportunity", "Risk"])
- 시간 표현 해석:
  - "최근", "최신", "올해" → period: "recent" (2023년 이후)
  - "최근 2년", "최근 3년" → period: "2022-2023" 또는 "2021-2023"
  - "전체", "모든" → period: "all"

**질의 예시**:
- "애플에게 사업상 리스크 항목에 대해 설명해줘"
  → target_entity_type: "Risk", query_text: "리스크 항목", filters: {company: "AAPL", context: ["business", "사업상"]}, query_type: "explain"

- "테슬라의 최근 기회 요소는?"
  → target_entity_type: "Opportunity", query_text: "기회 요소", filters: {company: "TSLA", time: {period: "recent"}}, query_type: "list"

- "엔비디아와 애플의 AI 기술을 비교해줘"
  → target_entity_type: "Technology", query_text: "AI 기술", filters: {company: ["NVDA", "AAPL"]}, query_type: "compare"

**사용자 질의**:
{query}

위 규칙에 따라 Intent를 JSON 형식으로 추출하세요.
"""
```

**JSON 스키마 정의**:

```python
INTENT_SCHEMA = {
    "type": "object",
    "properties": {
        "target_entity_type": {
            "type": ["string", "array"],
            "description": "검색할 노드 타입 (단일 또는 다중)",
            "oneOf": [
                {"type": "string", "enum": ["Risk", "Opportunity", "Event", "Technology", "Product", "Person", "general"]},
                {"type": "array", "items": {"type": "string", "enum": ["Risk", "Opportunity", "Event", "Technology", "Product", "Person"]}}
            ]
        },
        "query_text": {
            "type": "string",
            "description": "Vector 검색에 사용할 핵심 질의 텍스트"
        },
        "filters": {
            "type": "object",
            "properties": {
                "company": {
                    "type": ["string", "array", "null"],
                    "description": "기업 티커 심볼 (단일 또는 다중)",
                    "oneOf": [
                        {"type": "string", "enum": ["AAPL", "AMZN", "TSLA", "GOOGL", "MSFT", "META", "NVDA"]},
                        {"type": "array", "items": {"type": "string", "enum": ["AAPL", "AMZN", "TSLA", "GOOGL", "MSFT", "META", "NVDA"]}},
                        {"type": "null"}
                    ]
                },
                "context": {
                    "type": ["array", "null"],
                    "description": "맥락 키워드 배열",
                    "items": {"type": "string", "enum": ["business", "financial", "operational", "regulatory", "competitive", "market"]}
                },
                "time": {
                    "type": ["object", "null"],
                    "properties": {
                        "year": {"type": ["integer", "null"], "description": "특정 연도"},
                        "period": {"type": ["string", "null"], "enum": ["recent", "all", "2021-2023", "2022-2023", "2021-2022"]}
                    }
                },
                "section": {
                    "type": ["string", "null"],
                    "enum": ["risk_factors", "business", "mda", "financial_statements", "other_events", "financial_exhibits", None]
                },
                "filing_type": {
                    "type": ["string", "null"],
                    "enum": ["10-K", "10-Q", "8-K", None]
                },
                "product": {
                    "type": ["string", "null"],
                    "description": "제품명"
                },
                "person": {
                    "type": ["string", "null"],
                    "description": "인물명"
                }
            },
            "required": []
        },
        "query_type": {
            "type": "string",
            "enum": ["explain", "list", "compare", "analyze"],
            "description": "질의 유형"
        },
        "expansion": {
            "type": "object",
            "properties": {
                "include_related_products": {"type": "boolean", "default": True},
                "include_related_persons": {"type": "boolean", "default": False},
                "include_related_companies": {"type": "boolean", "default": False}
            },
            "required": ["include_related_products", "include_related_persons", "include_related_companies"]
        }
    },
    "required": ["target_entity_type", "query_text", "filters", "query_type", "expansion"]
}
```

**에러 처리 및 폴백 전략**:

```python
def _validate_and_normalize(self, intent: Dict) -> Dict:
    """Intent 검증 및 정규화"""
    # 1. 필수 필드 확인
    if "target_entity_type" not in intent:
        intent["target_entity_type"] = "general"
    
    if "query_text" not in intent or not intent["query_text"]:
        # query_text가 없으면 원본 질의 사용
        intent["query_text"] = self._original_query
    
    # 2. filters 기본값 설정
    if "filters" not in intent:
        intent["filters"] = {}
    
    # 3. company 티커 정규화 (한국어 → 티커)
    if "company" in intent["filters"] and intent["filters"]["company"]:
        company = intent["filters"]["company"]
        if isinstance(company, str):
            intent["filters"]["company"] = self._normalize_company(company)
        elif isinstance(company, list):
            intent["filters"]["company"] = [self._normalize_company(c) for c in company]
    
    # 4. query_type 기본값
    if "query_type" not in intent:
        intent["query_type"] = "explain"
    
    # 5. expansion 기본값
    if "expansion" not in intent:
        intent["expansion"] = {
            "include_related_products": True,
            "include_related_persons": False,
            "include_related_companies": False
        }
    
    return intent

def _normalize_company(self, company: str) -> str:
    """한국어 기업명을 티커로 변환"""
    company_map = {
        "애플": "AAPL", "apple": "AAPL",
        "아마존": "AMZN", "amazon": "AMZN",
        "테슬라": "TSLA", "tesla": "TSLA",
        "구글": "GOOGL", "google": "GOOGL", "알파벳": "GOOGL",
        "마이크로소프트": "MSFT", "microsoft": "MSFT", "ms": "MSFT",
        "메타": "META", "meta": "META", "페이스북": "META", "facebook": "META",
        "엔비디아": "NVDA", "nvidia": "NVDA"
    }
    return company_map.get(company.lower(), company.upper())
```

**사용 예시**:

```python
# Intent 추출기 초기화
extractor = IntentExtractor(
    model="gemini-3-flash-preview",
    api_key=os.getenv("GEMINI_API_KEY")
)

# Intent 추출
query = "애플에게 사업상 리스크 항목에 대해 설명해줘"
intent = await extractor.extract_intent(query)

# 결과:
# {
#     "target_entity_type": "Risk",
#     "query_text": "리스크 항목",
#     "filters": {
#         "company": "AAPL",
#         "context": ["business", "사업상"]
#     },
#     "query_type": "explain",
#     "expansion": {
#         "include_related_products": True,
#         "include_related_persons": False,
#         "include_related_companies": False
#     }
# }
```

#### 1.3.2 규칙 기반 폴백 (선택적)

Gemini API 호출 실패 시 또는 빠른 응답이 필요한 경우를 위한 규칙 기반 폴백 메커니즘을 제공합니다. (선택적 구현)
<｜tool▁calls▁begin｜><｜tool▁call▁begin｜>
read_file

---

## 📝 2. 질의 예시 및 Intent 매핑

### 2.1 기본 질의 예시

#### 예시 1: "애플에게 사업상 리스크 항목에 대해 설명해줘"

```python
{
    "target_entity_type": "Risk",
    "query_text": "리스크 항목",
    "filters": {
        "company": "AAPL",
        "context": ["business", "사업상"]
    },
    "query_type": "explain",
    "expansion": {
        "include_related_products": True,
        "include_related_persons": False,
        "include_related_companies": False
    }
}
```

**생성되는 Cypher 쿼리**:
```cypher
MATCH (c:Company {id: 'AAPL'})-[:HAS_RISKS]->(r:Risk)
MATCH (r)-[:IS_EXTRACTED_FROM]->(s:Section)
WHERE s.section_name = 'business' OR s.section_name = 'risk_factors'
RETURN r.id, r.entity, r.description, s.section_name, s.filing_type, s.year
ORDER BY s.year DESC, r.extracted_at DESC
LIMIT 20
```

#### 예시 2: "테슬라의 최근 기회 요소는?"

```python
{
    "target_entity_type": "Opportunity",
    "query_text": "기회 요소",
    "filters": {
        "company": "TSLA",
        "time": {"period": "recent"}
    },
    "query_type": "list",
    "expansion": {
        "include_related_products": True,
        "include_related_persons": False,
        "include_related_companies": False
    }
}
```

**생성되는 Cypher 쿼리**:
```cypher
MATCH (c:Company {id: 'TSLA'})-[:HAS_OPPORTUNITIES]->(o:Opportunity)
MATCH (o)-[:IS_EXTRACTED_FROM]->(s:Section)
WHERE s.year >= 2023
RETURN o.id, o.entity, o.description, s.section_name, s.filing_type, s.year
ORDER BY s.year DESC, o.extracted_at DESC
LIMIT 20
```

#### 예시 3: "엔비디아의 AI 기술에 대해 알려줘"

```python
{
    "target_entity_type": "Technology",
    "query_text": "AI 기술",
    "filters": {
        "company": "NVDA"
    },
    "query_type": "explain",
    "expansion": {
        "include_related_products": True,
        "include_related_persons": False,
        "include_related_companies": False
    }
}
```

**생성되는 Cypher 쿼리**:
```cypher
MATCH (c:Company {id: 'NVDA'})-[:HAS_TECHNOLOGIES]->(t:Technology)
WHERE t.entity CONTAINS 'AI' OR t.description CONTAINS 'AI' OR t.entity CONTAINS 'artificial intelligence'
RETURN t.id, t.entity, t.description
ORDER BY t.extracted_at DESC
LIMIT 20
```

#### 예시 4: "구글의 2023년 주요 이벤트 목록 보여줘"

```python
{
    "target_entity_type": "Event",
    "query_text": "주요 이벤트",
    "filters": {
        "company": "GOOGL",
        "time": {"year": 2023}
    },
    "query_type": "list",
    "expansion": {
        "include_related_products": True,
        "include_related_persons": True,
        "include_related_companies": False
    }
}
```

**생성되는 Cypher 쿼리**:
```cypher
MATCH (c:Company {id: 'GOOGL'})-[:HAS_EVENTS]->(e:Event)
MATCH (e)-[:IS_EXTRACTED_FROM]->(s:Section)
WHERE s.year = 2023
RETURN e.id, e.entity, e.description, e.date, s.section_name, s.filing_type
ORDER BY e.date DESC, e.extracted_at DESC
LIMIT 20
```

#### 예시 5: "마이크로소프트의 Office 365 제품과 관련된 리스크는?"

```python
{
    "target_entity_type": "Risk",
    "query_text": "리스크",
    "filters": {
        "company": "MSFT",
        "product": "Office 365"
    },
    "query_type": "list",
    "expansion": {
        "include_related_products": False,
        "include_related_persons": False,
        "include_related_companies": False
    }
}
```

**생성되는 Cypher 쿼리**:
```cypher
MATCH (c:Company {id: 'MSFT'})-[:HAS_RISKS]->(r:Risk)
MATCH (p:Product {name: 'Office 365'})-[m:IS_MENTIONED_IN]->(r)
RETURN r.id, r.entity, r.description, m.mention_context
ORDER BY r.extracted_at DESC
LIMIT 20
```

#### 예시 6: "애플의 iPhone 15가 언급된 기회 요소는?"

```python
{
    "target_entity_type": "Opportunity",
    "query_text": "기회 요소",
    "filters": {
        "company": "AAPL",
        "product": "iPhone 15"
    },
    "query_type": "list",
    "expansion": {
        "include_related_products": False,
        "include_related_persons": False,
        "include_related_companies": False
    }
}
```

**생성되는 Cypher 쿼리**:
```cypher
MATCH (c:Company {id: 'AAPL'})-[:HAS_OPPORTUNITIES]->(o:Opportunity)
MATCH (p:Product)-[m:IS_MENTIONED_IN]->(o)
WHERE p.name CONTAINS 'iPhone 15'
RETURN o.id, o.entity, o.description, p.name, m.mention_context
ORDER BY o.extracted_at DESC
LIMIT 20
```

#### 예시 7: "메타의 재무적 리스크를 분석해줘"

```python
{
    "target_entity_type": "Risk",
    "query_text": "재무적 리스크",
    "filters": {
        "company": "META",
        "context": ["financial", "재무적"]
    },
    "query_type": "analyze",
    "expansion": {
        "include_related_products": True,
        "include_related_persons": False,
        "include_related_companies": True
    }
}
```

**생성되는 Cypher 쿼리**:
```cypher
MATCH (c:Company {id: 'META'})-[:HAS_RISKS]->(r:Risk)
MATCH (r)-[:IS_EXTRACTED_FROM]->(s:Section)
WHERE r.description CONTAINS 'financial' OR r.description CONTAINS '재무'
RETURN r.id, r.entity, r.description, s.section_name, s.filing_type, s.year
ORDER BY s.year DESC, r.extracted_at DESC
LIMIT 20
```

#### 예시 8: "아마존의 경쟁적 위험 요소는 무엇인가?"

```python
{
    "target_entity_type": "Risk",
    "query_text": "경쟁적 위험 요소",
    "filters": {
        "company": "AMZN",
        "context": ["competitive", "경쟁적"]
    },
    "query_type": "explain",
    "expansion": {
        "include_related_products": True,
        "include_related_persons": False,
        "include_related_companies": True
    }
}
```

**생성되는 Cypher 쿼리**:
```cypher
MATCH (c:Company {id: 'AMZN'})-[:HAS_RISKS]->(r:Risk)
WHERE r.description CONTAINS 'competition' OR r.description CONTAINS '경쟁'
OPTIONAL MATCH (comp:Company)-[m:IS_MENTIONED_IN]->(r)
RETURN r.id, r.entity, r.description, collect(DISTINCT comp.id) AS mentioned_companies
ORDER BY r.extracted_at DESC
LIMIT 20
```

#### 예시 9: "엔비디아와 애플의 AI 기술을 비교해줘"

```python
{
    "target_entity_type": "Technology",
    "query_text": "AI 기술",
    "filters": {
        "company": ["NVDA", "AAPL"]  # 다중 기업
    },
    "query_type": "compare",
    "expansion": {
        "include_related_products": True,
        "include_related_persons": False,
        "include_related_companies": False
    }
}
```

**생성되는 Cypher 쿼리**:
```cypher
MATCH (c:Company)-[:HAS_TECHNOLOGIES]->(t:Technology)
WHERE c.id IN ['NVDA', 'AAPL']
  AND (t.entity CONTAINS 'AI' OR t.description CONTAINS 'AI')
RETURN c.id AS company, t.id, t.entity, t.description
ORDER BY c.id, t.extracted_at DESC
LIMIT 40
```

#### 예시 10: "테슬라의 최근 2년간 운영상 이벤트를 보여줘"

```python
{
    "target_entity_type": "Event",
    "query_text": "운영상 이벤트",
    "filters": {
        "company": "TSLA",
        "context": ["operational", "운영상"],
        "time": {"period": "2022-2023"}
    },
    "query_type": "list",
    "expansion": {
        "include_related_products": True,
        "include_related_persons": True,
        "include_related_companies": False
    }
}
```

**생성되는 Cypher 쿼리**:
```cypher
MATCH (c:Company {id: 'TSLA'})-[:HAS_EVENTS]->(e:Event)
MATCH (e)-[:IS_EXTRACTED_FROM]->(s:Section)
WHERE s.year >= 2022 AND s.year <= 2023
  AND (e.description CONTAINS 'operational' OR e.description CONTAINS '운영')
RETURN e.id, e.entity, e.description, e.date, s.section_name, s.filing_type
ORDER BY e.date DESC, e.extracted_at DESC
LIMIT 20
```

#### 예시 11: "구글의 Tim Cook이 언급된 기회 요소는?"

```python
{
    "target_entity_type": "Opportunity",
    "query_text": "기회 요소",
    "filters": {
        "company": "GOOGL",
        "person": "Tim Cook"
    },
    "query_type": "list",
    "expansion": {
        "include_related_products": False,
        "include_related_persons": True,
        "include_related_companies": False
    }
}
```

**생성되는 Cypher 쿼리**:
```cypher
MATCH (c:Company {id: 'GOOGL'})-[:HAS_OPPORTUNITIES]->(o:Opportunity)
MATCH (p:Person {name: 'Tim Cook'})-[m:IS_MENTIONED_IN]->(o)
RETURN o.id, o.entity, o.description, m.mention_context
ORDER BY o.extracted_at DESC
LIMIT 20
```

#### 예시 12: "애플의 10-K 공시에서 추출된 리스크 요소는?"

```python
{
    "target_entity_type": "Risk",
    "query_text": "리스크 요소",
    "filters": {
        "company": "AAPL",
        "filing_type": "10-K"
    },
    "query_type": "list",
    "expansion": {
        "include_related_products": True,
        "include_related_persons": False,
        "include_related_companies": False
    }
}
```

**생성되는 Cypher 쿼리**:
```cypher
MATCH (c:Company {id: 'AAPL'})-[:HAS_RISKS]->(r:Risk)
MATCH (r)-[:IS_EXTRACTED_FROM]->(s:Section)
WHERE s.filing_type = '10-K'
RETURN r.id, r.entity, r.description, s.section_name, s.year
ORDER BY s.year DESC, r.extracted_at DESC
LIMIT 20
```

#### 예시 13: "마이크로소프트의 규제 관련 리스크를 설명해줘"

```python
{
    "target_entity_type": "Risk",
    "query_text": "규제 관련 리스크",
    "filters": {
        "company": "MSFT",
        "context": ["regulatory", "규제"]
    },
    "query_type": "explain",
    "expansion": {
        "include_related_products": False,
        "include_related_persons": False,
        "include_related_companies": True
    }
}
```

**생성되는 Cypher 쿼리**:
```cypher
MATCH (c:Company {id: 'MSFT'})-[:HAS_RISKS]->(r:Risk)
WHERE r.description CONTAINS 'regulatory' OR r.description CONTAINS '규제' OR r.entity CONTAINS 'regulatory'
OPTIONAL MATCH (comp:Company)-[m:IS_MENTIONED_IN]->(r)
RETURN r.id, r.entity, r.description, collect(DISTINCT comp.id) AS mentioned_companies
ORDER BY r.extracted_at DESC
LIMIT 20
```

#### 예시 14: "엔비디아의 제품군을 보여줘"

```python
{
    "target_entity_type": "Product",
    "query_text": "제품군",
    "filters": {
        "company": "NVDA"
    },
    "query_type": "list",
    "expansion": {
        "include_related_products": False,
        "include_related_persons": False,
        "include_related_companies": False
    }
}
```

**생성되는 Cypher 쿼리**:
```cypher
MATCH (c:Company {id: 'NVDA'})-[:MAKE]->(p:Product)
RETURN p.id, p.name, p.product_type, p.category, p.description
ORDER BY p.name
```

#### 예시 15: "애플의 시장 확장 기회는?"

```python
{
    "target_entity_type": "Opportunity",
    "query_text": "시장 확장 기회",
    "filters": {
        "company": "AAPL",
        "context": ["market", "시장"]
    },
    "query_type": "list",
    "expansion": {
        "include_related_products": True,
        "include_related_persons": False,
        "include_related_companies": True
    }
}
```

**생성되는 Cypher 쿼리**:
```cypher
MATCH (c:Company {id: 'AAPL'})-[:HAS_OPPORTUNITIES]->(o:Opportunity)
WHERE o.description CONTAINS 'market' OR o.description CONTAINS '시장' OR o.entity CONTAINS 'market'
OPTIONAL MATCH (p:Product)-[m:IS_MENTIONED_IN]->(o)
RETURN o.id, o.entity, o.description, collect(DISTINCT p.name) AS mentioned_products
ORDER BY o.extracted_at DESC
LIMIT 20
```

### 2.2 복합 질의 예시

#### 예시 16: "애플의 2023년 사업상 리스크 중 iPhone과 관련된 것은?"

```python
{
    "target_entity_type": "Risk",
    "query_text": "리스크",
    "filters": {
        "company": "AAPL",
        "context": ["business", "사업상"],
        "time": {"year": 2023},
        "product": "iPhone"
    },
    "query_type": "list",
    "expansion": {
        "include_related_products": True,
        "include_related_persons": False,
        "include_related_companies": False
    }
}
```

**생성되는 Cypher 쿼리**:
```cypher
MATCH (c:Company {id: 'AAPL'})-[:HAS_RISKS]->(r:Risk)
MATCH (r)-[:IS_EXTRACTED_FROM]->(s:Section)
MATCH (p:Product)-[m:IS_MENTIONED_IN]->(r)
WHERE s.year = 2023
  AND (s.section_name = 'business' OR s.section_name = 'risk_factors')
  AND p.name CONTAINS 'iPhone'
RETURN r.id, r.entity, r.description, p.name, m.mention_context
ORDER BY r.extracted_at DESC
LIMIT 20
```

#### 예시 17: "테슬라의 최근 3년간 재무적 기회와 리스크를 비교해줘"

```python
{
    "target_entity_type": ["Opportunity", "Risk"],  # 다중 타입
    "query_text": "재무적 기회와 리스크",
    "filters": {
        "company": "TSLA",
        "context": ["financial", "재무적"],
        "time": {"period": "2021-2023"}
    },
    "query_type": "compare",
    "expansion": {
        "include_related_products": True,
        "include_related_persons": False,
        "include_related_companies": False
    }
}
```

**생성되는 Cypher 쿼리**:
```cypher
// Opportunity
MATCH (c:Company {id: 'TSLA'})-[:HAS_OPPORTUNITIES]->(o:Opportunity)
MATCH (o)-[:IS_EXTRACTED_FROM]->(s:Section)
WHERE s.year >= 2021 AND s.year <= 2023
  AND (o.description CONTAINS 'financial' OR o.description CONTAINS '재무')
RETURN 'Opportunity' AS type, o.id, o.entity, o.description, s.year
UNION ALL
// Risk
MATCH (c:Company {id: 'TSLA'})-[:HAS_RISKS]->(r:Risk)
MATCH (r)-[:IS_EXTRACTED_FROM]->(s:Section)
WHERE s.year >= 2021 AND s.year <= 2023
  AND (r.description CONTAINS 'financial' OR r.description CONTAINS '재무')
RETURN 'Risk' AS type, r.id, r.entity, r.description, s.year
ORDER BY type, year DESC
LIMIT 40
```

---

## 🔧 3. 구현 모듈

### 3.1 QueryEngine 클래스

**파일**: `app/services/query_engine.py`

```python
class QueryEngine:
    """질의 응답 엔진"""
    
    def __init__(
        self,
        graph_loader: GraphLoader,
        embedder=None,
        intent_extractor: Optional[IntentExtractor] = None
    ):
        self.graph_loader = graph_loader
        self.embedder = embedder  # Graphiti embedder 또는 GeminiEmbedder
        self.intent_extractor = intent_extractor or IntentExtractor()
        
    async def extract_intent(self, query: str) -> Dict:
        """질의에서 Intent 추출 (Gemini 기반)"""
        return await self.intent_extractor.extract_intent(query)
    
    def build_cypher_query(self, intent: Dict) -> str:
        """Intent를 기반으로 Cypher 쿼리 생성"""
        pass
    
    async def graph_search(self, intent: Dict) -> List[Dict]:
        """Graph 기반 검색"""
        cypher_query = self.build_cypher_query(intent)
        results = self.graph_loader.execute_query(cypher_query)
        return results
    
    async def vector_search(self, intent: Dict, top_k: int = 10) -> List[Dict]:
        """Vector 기반 검색"""
        # 1. Query text를 embedding으로 변환
        query_embedding = await self.embedder.embed(intent["query_text"])
        
        # 2. 해당 노드 타입의 모든 노드에서 유사도 계산
        # 3. 상위 top_k개 반환
        pass
    
    async def merge_results(self, graph_results: List[Dict], vector_results: List[Dict]) -> List[Dict]:
        """Graph 검색과 Vector 검색 결과 통합"""
        # RRF 또는 가중치 기반 통합
        pass
    
    async def rerank(self, query: str, results: List[Dict]) -> List[Dict]:
        """Cross-encoder 기반 재랭킹 (선택적)"""
        pass
    
    async def generate_answer(self, query: str, results: List[Dict]) -> str:
        """검색 결과를 바탕으로 답변 생성"""
        # LLM을 통한 자연어 답변 생성
        pass
    
    async def query(self, user_query: str) -> str:
        """사용자 질의 처리 메인 함수"""
        # 1. Intent 추출
        intent = self.extract_intent(user_query)
        
        # 2. Graph 검색
        graph_results = await self.graph_search(intent)
        
        # 3. Vector 검색
        vector_results = await self.vector_search(intent)
        
        # 4. 결과 통합
        merged_results = await self.merge_results(graph_results, vector_results)
        
        # 5. 재랭킹 (선택적)
        reranked_results = await self.rerank(user_query, merged_results)
        
        # 6. 답변 생성
        answer = await self.generate_answer(user_query, reranked_results)
        
        return answer
```

### 3.2 IntentExtractor 클래스

**파일**: `app/services/intent_extractor.py`

```python
import os
import json
import logging
from typing import Dict, Optional, List
import google.generativeai as genai

logger = logging.getLogger(__name__)

class IntentExtractor:
    """Gemini를 활용한 Intent 추출 클래스"""
    
    def __init__(
        self,
        model: str = "gemini-3-flash-preview",
        api_key: Optional[str] = None
    ):
        """
        Args:
            model: Gemini 모델명
            api_key: Gemini API 키 (없으면 환경변수에서 로드)
        """
        self.model = model
        api_key = api_key or os.getenv("GEMINI_API_KEY") or os.getenv("GOOGLE_API_KEY")
        
        if not api_key:
            raise ValueError("GEMINI_API_KEY or GOOGLE_API_KEY must be provided")
        
        genai.configure(api_key=api_key)
        
        # JSON 스키마 기반 구조화된 출력 설정
        self.client = genai.GenerativeModel(
            model_name=self.model,
            generation_config={
                "response_mime_type": "application/json",
                "response_schema": self._get_intent_schema()
            }
        )
        
        self._original_query = None
    
    def _get_intent_schema(self) -> Dict:
        """Intent JSON 스키마 반환"""
        return {
            "type": "object",
            "properties": {
                "target_entity_type": {
                    "type": ["string", "array"],
                    "oneOf": [
                        {"type": "string", "enum": ["Risk", "Opportunity", "Event", "Technology", "Product", "Person", "general"]},
                        {"type": "array", "items": {"type": "string", "enum": ["Risk", "Opportunity", "Event", "Technology", "Product", "Person"]}}
                    ]
                },
                "query_text": {"type": "string"},
                "filters": {
                    "type": "object",
                    "properties": {
                        "company": {
                            "type": ["string", "array", "null"],
                            "oneOf": [
                                {"type": "string", "enum": ["AAPL", "AMZN", "TSLA", "GOOGL", "MSFT", "META", "NVDA"]},
                                {"type": "array", "items": {"type": "string", "enum": ["AAPL", "AMZN", "TSLA", "GOOGL", "MSFT", "META", "NVDA"]}},
                                {"type": "null"}
                            ]
                        },
                        "context": {
                            "type": ["array", "null"],
                            "items": {"type": "string", "enum": ["business", "financial", "operational", "regulatory", "competitive", "market"]}
                        },
                        "time": {
                            "type": ["object", "null"],
                            "properties": {
                                "year": {"type": ["integer", "null"]},
                                "period": {"type": ["string", "null"], "enum": ["recent", "all", "2021-2023", "2022-2023", "2021-2022"]}
                            }
                        },
                        "section": {
                            "type": ["string", "null"],
                            "enum": ["risk_factors", "business", "mda", "financial_statements", "other_events", "financial_exhibits", None]
                        },
                        "filing_type": {
                            "type": ["string", "null"],
                            "enum": ["10-K", "10-Q", "8-K", None]
                        },
                        "product": {"type": ["string", "null"]},
                        "person": {"type": ["string", "null"]}
                    }
                },
                "query_type": {
                    "type": "string",
                    "enum": ["explain", "list", "compare", "analyze"]
                },
                "expansion": {
                    "type": "object",
                    "properties": {
                        "include_related_products": {"type": "boolean"},
                        "include_related_persons": {"type": "boolean"},
                        "include_related_companies": {"type": "boolean"}
                    },
                    "required": ["include_related_products", "include_related_persons", "include_related_companies"]
                }
            },
            "required": ["target_entity_type", "query_text", "filters", "query_type", "expansion"]
        }
    
    def _build_intent_prompt(self, query: str) -> str:
        """Intent 추출을 위한 Prompt 생성"""
        return f"""
당신은 금융 공시 문서 기반 Knowledge Graph 질의 시스템의 Intent 추출 전문가입니다.

사용자의 자연어 질의를 분석하여 다음 정보를 추출하세요:

1. **target_entity_type**: 사용자가 알고 싶어 하는 노드 타입
   - 가능한 값: "Risk", "Opportunity", "Event", "Technology", "Product", "Person", "general"
   - "general"은 특정 노드 타입이 명확하지 않을 때 사용

2. **query_text**: Vector 검색에 사용할 핵심 질의 텍스트
   - Entity type 키워드와 필터 키워드를 제외한 핵심 내용

3. **filters**: 검색 필터 조건
   - **company**: 기업 티커 심볼 (예: "AAPL", "TSLA", "GOOGL", "MSFT", "META", "NVDA", "AMZN")
     - 한국어 기업명도 티커로 변환: "애플" → "AAPL", "테슬라" → "TSLA", "구글" → "GOOGL", "마이크로소프트" → "MSFT", "메타" → "META", "엔비디아" → "NVDA", "아마존" → "AMZN"
   - **context**: 맥락 키워드 배열 (예: ["business", "사업상"], ["financial", "재무적"])
   - **time**: 시간 필터 (year 또는 period)
   - **section**: 섹션 필터
   - **filing_type**: 공시 유형 ("10-K", "10-Q", "8-K")
   - **product**: 제품명
   - **person**: 인물명

4. **query_type**: 질의 유형 ("explain", "list", "compare", "analyze")

5. **expansion**: 확장 검색 옵션

**중요 규칙**:
- 질의에 명시되지 않은 필터는 null로 설정
- 다중 기업 비교 질의의 경우 company를 배열로 설정
- 다중 Entity Type 질의의 경우 target_entity_type을 배열로 설정
- 시간 표현 해석: "최근" → period: "recent", "전체" → period: "all"

**사용자 질의**:
{query}

위 규칙에 따라 Intent를 JSON 형식으로 추출하세요.
""".format(query=query)
    
    async def extract_intent(self, query: str) -> Dict:
        """질의에서 Intent 추출"""
        self._original_query = query
        
        try:
            prompt = self._build_intent_prompt(query)
            response = await self.client.generate_content_async(prompt)
            
            # JSON 파싱
            intent = json.loads(response.text)
            
            # 검증 및 정규화
            intent = self._validate_and_normalize(intent)
            
            logger.info(f"Intent extracted: {intent}")
            return intent
            
        except Exception as e:
            logger.error(f"Failed to extract intent: {e}")
            # 폴백: 기본 Intent 반환
            return self._get_default_intent(query)
    
    def _validate_and_normalize(self, intent: Dict) -> Dict:
        """Intent 검증 및 정규화"""
        # 필수 필드 확인
        if "target_entity_type" not in intent:
            intent["target_entity_type"] = "general"
        
        if "query_text" not in intent or not intent["query_text"]:
            intent["query_text"] = self._original_query
        
        # filters 기본값 설정
        if "filters" not in intent:
            intent["filters"] = {}
        
        # company 티커 정규화
        if "company" in intent["filters"] and intent["filters"]["company"]:
            company = intent["filters"]["company"]
            if isinstance(company, str):
                intent["filters"]["company"] = self._normalize_company(company)
            elif isinstance(company, list):
                intent["filters"]["company"] = [self._normalize_company(c) for c in company]
        
        # query_type 기본값
        if "query_type" not in intent:
            intent["query_type"] = "explain"
        
        # expansion 기본값
        if "expansion" not in intent:
            intent["expansion"] = {
                "include_related_products": True,
                "include_related_persons": False,
                "include_related_companies": False
            }
        
        return intent
    
    def _normalize_company(self, company: str) -> str:
        """한국어 기업명을 티커로 변환"""
        company_map = {
            "애플": "AAPL", "apple": "AAPL",
            "아마존": "AMZN", "amazon": "AMZN",
            "테슬라": "TSLA", "tesla": "TSLA",
            "구글": "GOOGL", "google": "GOOGL", "알파벳": "GOOGL",
            "마이크로소프트": "MSFT", "microsoft": "MSFT", "ms": "MSFT",
            "메타": "META", "meta": "META", "페이스북": "META", "facebook": "META",
            "엔비디아": "NVDA", "nvidia": "NVDA"
        }
        return company_map.get(company.lower(), company.upper())
    
    def _get_default_intent(self, query: str) -> Dict:
        """기본 Intent 반환 (폴백)"""
        return {
            "target_entity_type": "general",
            "query_text": query,
            "filters": {},
            "query_type": "explain",
            "expansion": {
                "include_related_products": True,
                "include_related_persons": False,
                "include_related_companies": False
            }
        }
```

### 3.3 CypherQueryBuilder 클래스

**파일**: `app/services/cypher_query_builder.py`

```python
class CypherQueryBuilder:
    """Intent를 기반으로 Cypher 쿼리 생성"""
    
    def build_query(self, intent: Dict) -> str:
        """Intent를 기반으로 Cypher 쿼리 생성"""
        entity_type = intent["target_entity_type"]
        filters = intent["filters"]
        
        if entity_type == "Risk":
            return self._build_risk_query(filters, intent)
        elif entity_type == "Opportunity":
            return self._build_opportunity_query(filters, intent)
        elif entity_type == "Event":
            return self._build_event_query(filters, intent)
        elif entity_type == "Technology":
            return self._build_technology_query(filters, intent)
        elif entity_type == "Product":
            return self._build_product_query(filters, intent)
        elif entity_type == "Person":
            return self._build_person_query(filters, intent)
        else:
            return self._build_general_query(filters, intent)
    
    def _build_risk_query(self, filters: Dict, intent: Dict) -> str:
        """Risk 노드 검색 쿼리 생성"""
        # 필터 조건에 따라 동적으로 쿼리 생성
        pass
    
    # ... 기타 쿼리 빌더 메서드들
```

---

## 🚀 4. 구현 단계

### Phase 8.1: Intent 추출 구현 (1시간)
- [ ] `IntentExtractor` 클래스 구현
- [ ] Gemini API 통합 및 JSON 스키마 설정
- [ ] Prompt 템플릿 구현
- [ ] Intent 검증 및 정규화 로직 구현
- [ ] 에러 처리 및 폴백 메커니즘 구현
- [ ] 다양한 질의 예시에 대한 테스트 케이스 작성

### Phase 8.2: Cypher 쿼리 빌더 구현 (1시간)
- [ ] `CypherQueryBuilder` 클래스 구현
- [ ] 각 Entity Type별 쿼리 빌더 메서드 구현
- [ ] 필터 조건 적용 로직 구현

### Phase 8.3: Graph 검색 구현 (30분)
- [ ] `QueryEngine.graph_search()` 구현
- [ ] `GraphLoader.execute_query()` 메서드 추가 (필요 시)
- [ ] 검색 결과 파싱 및 정규화

### Phase 8.4: Vector 검색 구현 (1시간)
- [ ] `QueryEngine.vector_search()` 구현
- [ ] Embedding 생성 및 유사도 계산
- [ ] 노드 타입별 필터링

### Phase 8.5: 결과 통합 및 재랭킹 (30분)
- [ ] `QueryEngine.merge_results()` 구현 (RRF 또는 가중치)
- [ ] `QueryEngine.rerank()` 구현 (선택적)

### Phase 8.6: 답변 생성 (30분)
- [ ] `QueryEngine.generate_answer()` 구현
- [ ] LLM 통합 (Gemini 또는 OpenAI)
- [ ] 컨텍스트 포맷팅

### Phase 8.7: CLI 인터페이스 (30분)
- [ ] `scripts/08_query_interface.py` 구현
- [ ] 대화형 인터페이스
- [ ] 결과 포맷팅 및 출력

---

## 📊 5. 검증 시나리오

### 테스트 케이스

| ID | 질의 | 기대 Intent | 기대 결과 |
|----|------|------------|----------|
| TC-01 | "애플의 기회 요소를 알려줘" | Entity: Opportunity, Company: AAPL | Apple 관련 기회 요소 목록 |
| TC-02 | "테슬라의 리스크는?" | Entity: Risk, Company: TSLA | Tesla 관련 리스크 요소 |
| TC-03 | "구글의 AI 전략" | Entity: Opportunity/Technology, Company: GOOGL, Query: "AI 전략" | Alphabet AI 관련 전략 |
| TC-04 | "엔비디아 vs 애플 비교" | Entity: general, Company: [NVDA, AAPL], Type: compare | 두 기업 비교 분석 |
| TC-05 | "애플의 2023년 사업상 리스크" | Entity: Risk, Company: AAPL, Time: 2023, Context: business | 2023년 사업상 리스크 |
| TC-06 | "iPhone 15와 관련된 기회" | Entity: Opportunity, Product: iPhone 15 | iPhone 15 관련 기회 요소 |

---

## 📝 6. 주의사항

1. **Gemini API**:
   - API 키 설정: `GEMINI_API_KEY` 또는 `GOOGLE_API_KEY` 환경변수 필요
   - Rate Limit: Gemini API 호출 제한 고려 (재시도 로직 구현)
   - 비용: Intent 추출은 모델에 따라 토큰 비용 발생 (gemini-3-flash-preview는 저렴)
   - 응답 시간: API 호출 지연 고려 (비동기 처리 권장)

2. **성능**: 
   - Vector 검색은 Python에서 처리하므로 배치 처리 및 캐싱 고려
   - Intent 추출 결과 캐싱 고려 (동일 질의 재사용)

3. **정확도**: 
   - Graph 검색과 Vector 검색의 가중치 조정 필요
   - Intent 추출 정확도는 Prompt 품질에 의존

4. **확장성**: 
   - 새로운 질의 유형 추가 시 Prompt 업데이트 필요
   - 새로운 Entity Type 추가 시 JSON 스키마 업데이트 필요

5. **에러 처리**: 
   - Gemini API 호출 실패 시 기본 Intent로 폴백
   - JSON 파싱 실패 시 재시도 또는 기본 Intent 반환

---

## 🔄 7. 향후 개선 사항

1. **LLM 기반 Intent 추출**: 복잡한 질의 처리
2. **대화형 컨텍스트**: 이전 질의 기억 및 추론
3. **시각화**: Graph 구조 시각화
4. **멀티모달 검색**: 이미지, 표 등 다양한 데이터 타입 지원

