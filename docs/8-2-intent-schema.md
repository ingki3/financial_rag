# Intent 분석 결과 스키마

Intent Extractor가 반환하는 Intent 객체의 스키마 정의입니다.

## 개요

Intent 분석은 **사용자의 질의를 노드로 변환**하는 과정입니다. Intent는 **target**과 **filters**로 구분됩니다:

- **target**: 검색할 대상 노드 (node_type만 추출)
- **filters**: 검색 조건으로 사용할 노드들 (node_type + ticker 또는 name 필수)
  - **중요**: filters에 포함된 노드는 반드시 실제 필터로 사용할 수 있는 값(ticker, name 등)이 포함되어야 합니다.

## 전체 구조

```json
{
  "target": Node,
  "filters": Node[],
  "query_text": string,
  "query_type": string,
  "expansion": Expansion
}
```

---

## 1. Intent (최상위 모델)

### 필드 설명

| 필드 | 타입 | 필수 | 설명 |
|------|------|------|------|
| `target` | `Node` | ✅ | 검색할 대상 노드 (node_type만 포함) |
| `filters` | `Node[]` | ✅ | 검색 조건으로 사용할 노드 배열 |
| `query_text` | `string` | ✅ | Vector 검색에 사용할 핵심 질의 텍스트 |
| `query_type` | `string` | ✅ | 질의 유형 |
| `expansion` | `Expansion` | ✅ | 확장 검색 옵션 |

### target

**타입:** `Node`

**설명:** 검색할 대상 노드. `node_type`만 추출됩니다.

**구조:**
```json
{
  "node_type": string
}
```

**가능한 node_type 값:**
- `"Risk"`: 리스크
- `"Opportunity"`: 기회
- `"Event"`: 이벤트
- `"Technology"`: 기술
- `"Product"`: 제품
- `"Person"`: 인물
- `"Company"`: 기업
- `"Document"`: 문서
- `"Section"`: 섹션
- `"general"`: 일반

**예시:**
```json
"target": {
  "node_type": "Risk"
}
"target": {
  "node_type": "Opportunity"
}
```

### filters

**타입:** `Node[]`

**설명:** 검색 조건으로 사용할 노드 배열. **filters로 들어간 node들은 반드시 실제 필터로 사용할 수 있는 값(ticker, name 등)이 포함되어야 합니다.**

**구조:**
```json
[
  {
    "node_type": string,
    "ticker"?: string,  // Company 노드인 경우 필수
    "name"?: string     // Product, Person 등 다른 노드 타입인 경우 필수
  }
]
```

**노드 타입별 구조:**

1. **Company 노드:**
```json
{
  "node_type": "Company",
  "ticker": "AAPL"  // 필수: 기업 티커 심볼
}
```

2. **Product 노드:**
```json
{
  "node_type": "Product",
  "name": "iPhone 15"  // 필수: 제품명
}
```

3. **Person 노드:**
```json
{
  "node_type": "Person",
  "name": "Tim Cook"  // 필수: 인물명
}
```

4. **Technology 노드:**
```json
{
  "node_type": "Technology",
  "name": "AI 기술"  // 필수: 기술명
}
```

**예시:**
```json
"filters": [
  {
    "node_type": "Company",
    "ticker": "AAPL"
  }
]
"filters": [
  {
    "node_type": "Company",
    "ticker": "TSLA"
  },
  {
    "node_type": "Product",
    "name": "Model 3"
  }
]
```

### query_text

**설명:** 사용자의 기본 질의 텍스트

**예시:**
```json
"query_text": "테슬라의 최근 기회 요소는?"
"query_text": "애플의 iPhone과 관련된 사업상 리스크"
"query_text": "엔비디아와 애플의 AI 기술을 비교해줘"
```

### query_type

**설명:** 사용자 질의의 의도를 분류하는 필드. 질의 응답 시스템에서 결과를 어떻게 처리할지 결정하는 데 사용됩니다.

**가능한 값:**

1. **`"explain"`**: 설명 요청
   - 질의 예시: "애플의 리스크에 대해 설명해줘", "테슬라의 기회 요소를 알려줘"
   - 용도: 특정 주제에 대한 상세한 설명이나 개요를 제공
   - 응답 형식: 설명형 텍스트

2. **`"list"`**: 목록 요청
   - 질의 예시: "애플의 리스크 목록 보여줘", "테슬라의 기회 요소는?"
   - 용도: 여러 항목을 나열하여 보여줌
   - 응답 형식: 리스트 형식

3. **`"compare"`**: 비교 요청
   - 질의 예시: "엔비디아와 애플의 AI 기술을 비교해줘", "테슬라의 기회와 리스크를 비교해줘"
   - 용도: 두 개 이상의 엔티티나 개념을 비교
   - 응답 형식: 비교형 텍스트 또는 표 형식

4. **`"analyze"`**: 분석 요청
   - 질의 예시: "메타의 재무적 리스크를 분석해줘", "애플의 시장 기회를 분석해줘"
   - 용도: 데이터를 분석하고 인사이트를 제공
   - 응답 형식: 분석 결과 및 인사이트

**예시:**
```json
"query_type": "list"
"query_type": "explain"
"query_type": "compare"
"query_type": "analyze"
```

---

## 2. Node (노드 구조)

### 필드 설명

| 필드 | 타입 | 필수 | 설명 |
|------|------|------|------|
| `node_type` | `string` | ✅ | 노드 타입 |
| `ticker` | `string` | 조건부 | 기업 티커 (Company 노드인 경우 필수) |
| `name` | `string` | 조건부 | 노드 이름 (Company가 아닌 노드 타입인 경우 필수) |

### node_type

**가능한 값:**
- `"Risk"`: 리스크
- `"Opportunity"`: 기회
- `"Event"`: 이벤트
- `"Technology"`: 기술
- `"Product"`: 제품
- `"Person"`: 인물
- `"Company"`: 기업
- `"Document"`: 문서
- `"Section"`: 섹션
- `"general"`: 일반

### ticker

**타입:** `string` (Company 노드인 경우 필수)

**설명:** 기업 티커 심볼. **filters에 포함된 Company 노드는 반드시 ticker가 포함되어야 합니다.**

**한국어 기업명 → 티커 변환:**
- "애플" → "AAPL"
- "테슬라" → "TSLA"
- "구글" → "GOOGL"
- "마이크로소프트" → "MSFT"
- "메타" → "META"
- "엔비디아" → "NVDA"
- "아마존" → "AMZN"

**예시:**
```json
{
  "node_type": "Company",
  "ticker": "AAPL"
}
```

### name

**타입:** `string` (Company가 아닌 노드 타입인 경우 필수)

**설명:** 노드의 실제 이름 값. **filters에 포함된 노드(Company 제외)는 반드시 name이 포함되어야 합니다.**

**노드 타입별 name 예시:**
- Product: "iPhone 15", "Office 365", "Model 3"
- Person: "Tim Cook", "Elon Musk"
- Technology: "AI 기술", "Machine Learning"
- Section: "risk_factors", "business"
- Document: "10-K", "10-Q"

**예시:**
```json
{
  "node_type": "Product",
  "name": "iPhone 15"
}
{
  "node_type": "Person",
  "name": "Tim Cook"
}
```

---

## 3. Expansion (확장 검색 옵션)

### 필드 설명

| 필드 | 타입 | 필수 | 기본값 | 설명 |
|------|------|------|--------|------|
| `include_related_products` | `boolean` | ✅ | `true` | 관련 제품 포함 여부 |
| `include_related_persons` | `boolean` | ✅ | `false` | 관련 인물 포함 여부 |
| `include_related_companies` | `boolean` | ✅ | `false` | 관련 기업 포함 여부 |

### include_related_products

**설명:** 관련 제품 노드도 검색에 포함할지 여부

**예시:**
```json
"include_related_products": true
"include_related_products": false
```

### include_related_persons

**설명:** 관련 인물 노드도 검색에 포함할지 여부

**예시:**
```json
"include_related_persons": true
"include_related_persons": false
```

### include_related_companies

**설명:** 관련 기업 노드도 검색에 포함할지 여부

**예시:**
```json
"include_related_companies": true
"include_related_companies": false
```

---

## 전체 예시

### 예시 1: 기본 케이스

**질의:** "테슬라의 최근 기회 요소는?"

```json
{
  "target": {
    "node_type": "Opportunity"
  },
  "filters": [
    {
      "node_type": "Company",
      "ticker": "TSLA"
    }
  ],
  "query_text": "테슬라의 최근 기회 요소는?",
  "query_type": "list",
  "expansion": {
    "include_related_products": false,
    "include_related_persons": false,
    "include_related_companies": false
  }
}
```

### 예시 2: 복합 필터

**질의:** "애플의 2023년 사업상 리스크 중 iPhone과 관련된 것은?"

```json
{
  "target": {
    "node_type": "Risk"
  },
  "filters": [
    {
      "node_type": "Company",
      "ticker": "AAPL"
    },
    {
      "node_type": "Product",
      "name": "iPhone"
    }
  ],
  "query_text": "애플의 2023년 사업상 리스크 중 iPhone과 관련된 것은?",
  "query_type": "list",
  "expansion": {
    "include_related_products": false,
    "include_related_persons": false,
    "include_related_companies": false
  }
}
```

### 예시 3: 다중 Company (비교 질의)

**질의:** "엔비디아와 애플의 AI 기술을 비교해줘"

```json
{
  "target": {
    "node_type": "Technology"
  },
  "filters": [
    {
      "node_type": "Company",
      "ticker": "NVDA"
    },
    {
      "node_type": "Company",
      "ticker": "AAPL"
    }
  ],
  "query_text": "엔비디아와 애플의 AI 기술을 비교해줘",
  "query_type": "compare",
  "expansion": {
    "include_related_products": false,
    "include_related_persons": false,
    "include_related_companies": false
  }
}
```

### 예시 4: Person 필터

**질의:** "구글의 Tim Cook이 언급된 기회 요소는?"

```json
{
  "target": {
    "node_type": "Opportunity"
  },
  "filters": [
    {
      "node_type": "Company",
      "ticker": "GOOGL"
    },
    {
      "node_type": "Person",
      "name": "Tim Cook"
    }
  ],
  "query_text": "구글의 Tim Cook이 언급된 기회 요소는?",
  "query_type": "list",
  "expansion": {
    "include_related_products": false,
    "include_related_persons": false,
    "include_related_companies": false
  }
}
```

### 예시 5: 단일 필터 (Company만)

**질의:** "애플에게 사업상 리스크 항목에 대해 설명해줘"

```json
{
  "target": {
    "node_type": "Risk"
  },
  "filters": [
    {
      "node_type": "Company",
      "ticker": "AAPL"
    }
  ],
  "query_text": "애플에게 사업상 리스크 항목에 대해 설명해줘",
  "query_type": "explain",
  "expansion": {
    "include_related_products": false,
    "include_related_persons": false,
    "include_related_companies": false
  }
}
```

### 예시 6: 필터 없음

**질의:** "최근 기술 트렌드는?"

```json
{
  "target": {
    "node_type": "Technology"
  },
  "filters": [],
  "query_text": "최근 기술 트렌드는?",
  "query_type": "list",
  "expansion": {
    "include_related_products": false,
    "include_related_persons": false,
    "include_related_companies": false
  }
}
```

---

## 구조 요약

### Target 구조
```
target -> node{node_type}
```

- `target`은 단일 `Node` 객체
- `node_type`만 포함 (검색할 노드 타입)

### Filters 구조
```
filters -> [node{node_type + ticker 또는 name}]
```

- `filters`는 `Node[]` 배열
- **각 노드는 반드시 실제 필터로 사용할 수 있는 값이 포함되어야 함:**
  - `node_type` 필수
  - `Company` 노드인 경우 `ticker` 필수
  - 다른 노드 타입(Product, Person, Technology 등)인 경우 `name` 필수

### 노드 변환 규칙

1. **사용자 질의 → 노드 변환**
   - 질의에서 언급된 엔티티들을 노드로 변환
   - `target`: 검색 대상 노드 (node_type만)
   - `filters`: 검색 조건 노드들 (node_type + ticker 또는 name 필수)

2. **Company 노드 처리**
   - Company 노드는 반드시 `ticker` 포함
   - 한국어 기업명은 자동으로 티커로 변환
   - 예시: `{"node_type": "Company", "ticker": "AAPL"}`

3. **다른 노드 타입 처리**
   - Product, Person, Technology 등은 반드시 `name` 포함
   - `name`은 실제 필터링에 사용할 수 있는 구체적인 값
   - 예시: `{"node_type": "Product", "name": "iPhone 15"}`
   - 예시: `{"node_type": "Person", "name": "Tim Cook"}`

---

## Pydantic 모델 정의

스키마는 Pydantic 모델로 정의되어 있으며, `app/services/intent_extractor.py`에서 확인할 수 있습니다:

- `Node`: 노드 모델 (node_type, ticker, name)
  - `ticker`: Company 노드인 경우 필수
  - `name`: Company가 아닌 노드 타입인 경우 필수
- `Expansion`: 확장 검색 옵션 모델
- `Intent`: 최상위 Intent 모델

모든 모델은 `BaseModel`을 상속받으며, `Field`를 사용하여 필드 설명과 제약 조건을 정의합니다.

## 필터 값 필수 규칙 요약

**filters에 포함된 모든 노드는 반드시 실제 필터로 사용할 수 있는 값이 포함되어야 합니다:**

- **Company 노드**: `ticker` 필수 (예: `"AAPL"`, `"TSLA"`)
- **Product 노드**: `name` 필수 (예: `"iPhone 15"`, `"Office 365"`)
- **Person 노드**: `name` 필수 (예: `"Tim Cook"`, `"Elon Musk"`)
- **Technology 노드**: `name` 필수 (예: `"AI 기술"`, `"Machine Learning"`)
- **기타 노드 타입**: 해당 노드 타입에 맞는 식별자 필드 필수
