# 정규화 개선 계획

## 📌 목적

현재 하드코딩된 정규화 로직을 개선하여:
1. Normalization Map을 티커별 JSON 파일로 관리
2. 표준명을 찾고, 없으면 LLM으로 찾기
3. 매칭 실패 시 자동으로 Normalization Map에 추가
4. 질의 Intent 처리에도 동일한 로직 재사용

---

## 📁 Normalization Map 파일 구조

### 파일 위치
```
data/normalization_maps/
├── AAPL_normalization_map.json
├── AMZN_normalization_map.json
├── GOOGL_normalization_map.json
├── META_normalization_map.json
├── MSFT_normalization_map.json
├── NVDA_normalization_map.json
└── TSLA_normalization_map.json
```

### JSON 파일 구조

```json
{
  "metadata": {
    "ticker": "AAPL",
    "version": "1.0.0",
    "created_at": "2025-01-15T10:00:00Z",
    "last_updated": "2025-01-15T15:30:00Z",
    "total_mappings": 45,
    "llm_generated_count": 12,
    "auto_added_count": 5
  },
  "categories": [
    {
      "category": "Product",
      "standard_items": [
        "iPhone",
        "iPhone 15",
        "iPhone 15 Pro",
        "iPhone 15 Pro Max",
        "iPad",
        "Mac",
        "MacBook Pro",
        "Apple Watch",
        "AirPods",
        "Apple TV+",
        "iCloud",
        "App Store",
        "Apple Music",
        "iOS",
        "macOS"
      ],
      "normalized_map": [
        {
          "standard_item": "iPhone",
          "variants": ["iphone", "iphone 15", "iphone 15 pro"],
          "metadata": {
            "added_at": "2025-01-15T10:00:00Z",
            "total_usage_count": 0,
            "source": "manual"
          }
        },
        {
          "standard_item": "iPhone 15",
          "variants": ["iphone 15"],
          "metadata": {
            "added_at": "2025-01-15T10:00:00Z",
            "total_usage_count": 0,
            "source": "manual"
          }
        },
        {
          "standard_item": "iPhone 15 Pro",
          "variants": ["iphone 15 pro", "iphone 15 pro max"],
          "metadata": {
            "added_at": "2025-01-15T10:00:00Z",
            "total_usage_count": 0,
            "source": "manual"
          }
        },
        {
          "standard_item": "iPhone 15 Pro Max",
          "variants": ["iphone 15 pro max"],
          "metadata": {
            "added_at": "2025-01-15T12:30:00Z",
            "total_usage_count": 3,
            "source": "llm",
            "llm_confidence": 0.95,
            "llm_model": "gemini-2.5-flash-lite"
          }
        },
        {
          "standard_item": "Mac",
          "variants": ["mac", "macbook", "macbook pro"],
          "metadata": {
            "added_at": "2025-01-15T10:00:00Z",
            "total_usage_count": 1,
            "source": "manual"
          }
        },
        {
          "standard_item": "New Product XYZ",
          "variants": ["new_product_xyz"],
          "metadata": {
            "added_at": "2025-01-15T14:00:00Z",
            "total_usage_count": 0,
            "source": "auto_added",
            "llm_confidence": 0.92,
            "pending_review": true,
            "suggested_by_llm": true
          }
        }
      ]
    },
    {
      "category": "Person",
      "standard_items": [
        "Tim Cook",
        "Craig Federighi",
        "Luca Maestri",
        "Katherine Adams"
      ],
      "normalized_map": [
        {
          "standard_item": "Tim Cook",
          "variants": ["tim cook", "timothy cook"],
          "metadata": {
            "added_at": "2025-01-15T10:00:00Z",
            "total_usage_count": 2,
            "source": "manual"
          }
        },
        {
          "standard_item": "Craig Federighi",
          "variants": ["craig federighi"],
          "metadata": {
            "added_at": "2025-01-15T10:00:00Z",
            "total_usage_count": 0,
            "source": "manual"
          }
        }
      ]
    },
    {
      "category": "Technology",
      "standard_items": [
        "Machine Learning",
        "Artificial Intelligence",
        "Neural Engine",
        "Face ID",
        "Touch ID"
      ],
      "normalized_map": [
        {
          "standard_item": "Artificial Intelligence",
          "variants": ["ai", "artificial intelligence"],
          "metadata": {
            "added_at": "2025-01-15T10:00:00Z",
            "total_usage_count": 0,
            "source": "manual"
          }
        },
        {
          "standard_item": "Machine Learning",
          "variants": ["ml", "machine learning"],
          "metadata": {
            "added_at": "2025-01-15T13:00:00Z",
            "total_usage_count": 5,
            "source": "llm",
            "llm_confidence": 0.90
          }
        }
      ]
    }
  ],
  "filtered_terms": [
    {
      "category": "Product",
      "terms": [
        {
          "term": "apple",
          "reason": "brand_name",
          "added_at": "2025-01-15T10:00:00Z"
        },
        {
          "term": "2028 notes",
          "reason": "financial_instrument",
          "added_at": "2025-01-15T11:00:00Z"
        }
      ]
    }
  ],
  "normalization_rules": [
    {
      "category": "Product",
      "rules": [
        {
          "rule_id": "rule_001",
          "rule_type": "pattern",
          "pattern": "^model\\s+[sx3y]$",
          "target_standard": "Tesla Model {match}",
          "description": "모든 'Model S', 'Model X', 'Model 3', 'Model Y'는 'Tesla Model {match}'로 정규화",
          "source": "llm",
          "discovered_at": "2025-01-15T13:00:00Z",
          "usage_count": 5,
          "llm_confidence": 0.92,
          "examples": [
            {
              "input": "model 3",
              "output": "Tesla Model 3"
            },
            {
              "input": "model s",
              "output": "Tesla Model S"
            }
          ],
          "active": true
        },
        {
          "rule_id": "rule_002",
          "rule_type": "suffix",
          "pattern": ".*\\s+15\\s+pro.*",
          "target_standard": "iPhone 15 Pro",
          "description": "'15 Pro'가 포함된 모든 변형은 'iPhone 15 Pro'로 정규화",
          "source": "llm",
          "discovered_at": "2025-01-15T14:00:00Z",
          "usage_count": 3,
          "llm_confidence": 0.88,
          "examples": [
            {
              "input": "iphone 15 pro max",
              "output": "iPhone 15 Pro"
            }
          ],
          "active": true
        },
        {
          "rule_id": "rule_003",
          "rule_type": "abbreviation",
          "pattern": "^ml$",
          "target_standard": "Machine Learning",
          "description": "'ML' 약어는 'Machine Learning'으로 정규화",
          "source": "llm",
          "discovered_at": "2025-01-15T15:00:00Z",
          "usage_count": 8,
          "llm_confidence": 0.95,
          "examples": [
            {
              "input": "ml",
              "output": "Machine Learning"
            }
          ],
          "active": true
        }
      ]
    },
    {
      "category": "Technology",
      "rules": [
        {
          "rule_id": "rule_004",
          "rule_type": "abbreviation",
          "pattern": "^ai$",
          "target_standard": "Artificial Intelligence",
          "description": "'AI' 약어는 'Artificial Intelligence'로 정규화",
          "source": "llm",
          "discovered_at": "2025-01-15T16:00:00Z",
          "usage_count": 12,
          "llm_confidence": 0.98,
          "examples": [
            {
              "input": "ai",
              "output": "Artificial Intelligence"
            }
          ],
          "active": true
        }
      ]
    }
  ]
}
```

### 필드 설명

#### metadata
- `ticker`: 티커 심볼
- `version`: 스키마 버전
- `created_at`: 파일 생성 시간
- `last_updated`: 마지막 업데이트 시간
- `total_mappings`: 전체 매핑 수
- `llm_generated_count`: LLM으로 생성된 매핑 수
- `auto_added_count`: 자동 추가된 매핑 수

#### categories
- 카테고리별 정규화 맵 배열
- 각 카테고리는 `Product`, `Person`, `Technology` 등

#### categories[].category
- 카테고리 이름 (`Product`, `Person`, `Technology` 등)

#### categories[].standard_items
- 표준 이름 목록 (정렬된 배열)
- 중복 제거된 고유한 이름들
- 노드 생성 시 사용되는 실제 이름
- `normalized_map`의 `standard_item`과 일치해야 함

#### categories[].normalized_map
- 표준명 중심의 정규화 맵 배열
- 각 항목:
  - `standard_item`: 표준 이름 (원본 대소문자 유지)
  - `variants`: 이 표준명으로 매핑되는 변형명 배열
    - **중요**: variants는 모두 **소문자로 정규화**하여 저장
    - 비교 시에도 소문자로 변환하여 매칭
    - 예: `["iphone", "iphone 15", "iphone 15 pro"]`
  - `metadata`: 메타데이터 객체
    - `added_at`: 추가 시간
    - `total_usage_count`: 전체 사용 횟수 (모든 variants 합산)
    - `source`: 출처 (`manual`, `llm`, `auto_added`)
    - `llm_confidence`: LLM 신뢰도 (0.0-1.0, LLM 생성 시)
    - `llm_model`: 사용된 LLM 모델명 (LLM 생성 시)
    - `pending_review`: 검토 대기 중인지 여부 (auto_added인 경우)
    - `suggested_by_llm`: LLM이 제안한 새로운 표준명인지 여부

**비교 로직**:
- 모든 비교는 **소문자로 변환**하여 수행
- 입력: `name.lower().strip()`
- variants 검색: `variant.lower() == name_lower`
- standard_items 검색: `std_name.lower().strip() == name_lower`

#### filtered_terms
- 제품이 아닌 것으로 판단된 용어들
- 카테고리별로 그룹화
- 각 항목:
  - `category`: 카테고리 이름
  - `terms`: 필터링된 용어 배열
    - `term`: 필터링된 용어
    - `reason`: 필터링 이유 (`brand_name`, `financial_instrument`, `not_a_product`, `competitor_product` 등)
    - `added_at`: 추가 시간

#### normalization_rules
- LLM이 발견한 정규화 규칙(패턴) 저장
- 카테고리별로 그룹화
- 각 규칙:
  - `rule_id`: 고유 규칙 ID
  - `rule_type`: 규칙 타입 (`pattern`, `suffix`, `prefix`, `abbreviation`, `regex`, `custom`)
  - `pattern`: 정규식 패턴 또는 패턴 문자열
  - `target_standard`: 매칭 시 반환할 표준명 (패턴 매칭 변수 포함 가능)
  - `description`: 규칙 설명
  - `source`: 출처 (`llm`, `manual`)
  - `discovered_at`: 규칙 발견/생성 시간
  - `usage_count`: 규칙 사용 횟수
  - `llm_confidence`: LLM 신뢰도 (0.0-1.0, LLM 발견 시)
  - `examples`: 규칙 적용 예시 배열
    - `input`: 입력 예시
    - `output`: 출력 예시
  - `active`: 규칙 활성화 여부 (false면 비활성화)

---

## 🔄 정규화 프로세스 개선

### 1. 정규화 플로우

```
입력: name, node_type, ticker
    ↓
[1] Normalization Map 로드
    ↓
[2] 카테고리 찾기 (categories에서 node_type으로 찾기)
    ↓
[3] normalized_map에서 variants 검색
    ├─ name을 소문자로 변환: name_lower = name.lower().strip()
    ├─ 각 normalized_map 항목의 variants 배열에서 검색
    │   ├─ variant.lower() == name_lower 인 경우
    │   │   ├─ 해당 standard_item 반환
    │   │   └─ total_usage_count 증가
    │   └─ 없음 → 다음 단계
    └─ 없음 → 다음 단계
    ↓
[4] standard_items에서 직접 매칭 (모두 소문자로 변환하여 비교)
    ├─ Exact Match: std_name.lower().strip() == name_lower
    ├─ Partial Match: name_lower in std_name.lower() or std_name.lower() in name_lower
    └─ Abbreviation Match: 약어 패턴 매칭 (소문자로 비교)
    ↓
[5] 매칭 성공 시
    ├─ name_lower를 variants에 추가 (소문자로 저장)
    ├─ normalized_map에 새 항목 추가 또는 기존 항목의 variants에 추가
    │   └─ metadata.source = "manual"
    └─ 표준명 반환 (원본 대소문자 유지)
    ↓
[6] normalization_rules에서 패턴 매칭 시도
    ├─ 카테고리별 활성화된 규칙 순회
    ├─ 규칙 패턴과 name_lower 매칭
    ├─ 매칭 성공 시
    │   ├─ 규칙의 target_standard 반환
    │   ├─ 규칙의 usage_count 증가
    │   └─ 표준명 반환
    └─ 매칭 실패 → 다음 단계
    ↓
[7] 매칭 실패 시 → LLM 호출
    ├─ LLM이 standard_items에서 매칭 찾음
    │   ├─ normalized_map의 해당 항목의 variants에 name_lower 추가 (소문자로 저장)
    │   │   └─ metadata.source = "llm", llm_confidence 설정
    │   └─ 표준명 반환 (원본 대소문자 유지)
    ├─ LLM이 새로운 패턴 규칙 발견
    │   ├─ normalization_rules에 새 규칙 추가
    │   │   ├─ rule_id: 자동 생성
    │   │   ├─ rule_type: LLM이 판단한 타입
    │   │   ├─ pattern: LLM이 추출한 패턴
    │   │   ├─ target_standard: 매칭된 표준명 또는 LLM 제안
    │   │   ├─ source: "llm"
    │   │   ├─ llm_confidence: LLM 신뢰도
    │   │   ├─ examples: [{"input": name_lower, "output": standard_name}]
    │   │   └─ active: true
    │   ├─ 규칙 적용하여 표준명 반환
    │   └─ 규칙의 usage_count = 1로 설정
    └─ LLM이 매칭 못 찾음
        ├─ LLM이 새로운 표준명 제안
        │   ├─ standard_items에 추가 (원본 대소문자 유지)
        │   ├─ normalized_map에 새 항목 추가
        │   │   ├─ standard_item: LLM이 제안한 표준명 (원본 대소문자)
        │   │   ├─ variants: [name_lower] (소문자로 저장)
        │   │   └─ metadata.source = "auto_added", pending_review = true
        │   └─ 표준명 반환 (원본 대소문자 유지)
        └─ LLM이 완전히 실패
            ├─ filtered_terms에 추가 (term: name_lower, 소문자로 저장)
            └─ 원본 이름 반환 (또는 None)
    ↓
[8] Normalization Map 저장 (변경사항 있으면)
    ├─ variants 추가/업데이트
    ├─ standard_items 추가
    ├─ normalization_rules 추가 (LLM이 발견한 규칙)
    └─ filtered_terms 추가
```

### 2. LLM 프롬프트 개선

현재 프롬프트를 확장하여:
- 표준명 목록에서 매칭 찾기
- 매칭 실패 시 새로운 표준명 제안
- **새로운 정규화 규칙(패턴) 발견 및 제안**
  - 예: "모든 'Model X' 형태는 'Tesla Model X'로 정규화"
  - 예: "'15 Pro'가 포함된 것은 'iPhone 15 Pro'로 정규화"
  - 예: "'ML' 약어는 'Machine Learning'으로 정규화"
- 신뢰도 점수 제공
- 규칙 타입 판단 (`pattern`, `suffix`, `prefix`, `abbreviation` 등)

**LLM 응답 형식**:
```json
{
  "matched_standard": "iPhone 15 Pro" | null,
  "suggested_standard": "New Product Name" | null,
  "discovered_rule": {
    "rule_type": "pattern" | "suffix" | "abbreviation" | null,
    "pattern": "정규식 패턴",
    "target_standard": "표준명",
    "description": "규칙 설명",
    "confidence": 0.95
  } | null,
  "confidence": 0.92
}
```

### 3. 자동 업데이트 메커니즘

#### 3.1 즉시 저장 vs 배치 저장
- **옵션 1: 즉시 저장** (권장)
  - 매핑 추가/업데이트 시 즉시 파일 저장
  - 장점: 데이터 손실 방지, 실시간 반영
  - 단점: 파일 I/O 오버헤드

- **옵션 2: 배치 저장**
  - 메모리에 변경사항 누적 후 주기적으로 저장
  - 장점: 성능 향상
  - 단점: 데이터 손실 위험

#### 3.2 파일 잠금 (File Locking)
- 동시 접근 방지를 위한 파일 잠금 메커니즘
- `fcntl` (Linux) 또는 `msvcrt` (Windows) 사용

#### 3.3 백업 및 버전 관리
- 변경 전 백업 파일 생성 (`{ticker}_normalization_map.json.backup`)
- Git으로 추적 가능하도록 설정 (선택적)

---

## 🔍 질의 Intent 통합 고려사항

### 1. Intent에서 사용하는 필터 타입

현재 Intent 구조:
```python
{
  "filters": {
    "product": "iPhone 15",  # 문자열
    "person": "Tim Cook",    # 문자열
    "company": "AAPL"        # 티커
  }
}
```

### 2. 정규화 적용 시점

```
사용자 질의
    ↓
Intent 추출 (IntentExtractor)
    ↓
Intent 정규화 (NameNormalizer.normalize_filters)
    ├─ product 필터 → normalize(product, "Product", ticker)
    ├─ person 필터 → normalize(person, "Person", ticker)
    └─ company 필터 → _normalize_company() (기존 로직)
    ↓
Cypher 쿼리 생성 (CypherQueryBuilder)
    └─ 정규화된 이름으로 쿼리 생성
```

### 3. 공통 Normalization Map 사용

- **Phase 5 (Graph 생성)**: `normalize_product_name()` → Normalization Map 사용
- **Phase 8 (질의 처리)**: `NameNormalizer.normalize()` → 동일한 Normalization Map 사용

**장점**:
- 일관된 정규화
- Graph 생성 시 학습한 매핑이 질의에도 적용
- 질의 시 새로 발견된 매핑이 Graph 생성에도 반영

### 4. Intent 필터 확장 고려

향후 Intent 필터에 추가될 수 있는 항목:
- `technology`: Technology 노드 타입
- `section`: Section 필터 (이미 존재)
- `filing_type`: 공시 유형 (이미 존재)

Normalization Map 구조가 확장 가능하도록 설계:
- `mappings` 객체에 새로운 노드 타입 추가 가능
- 각 노드 타입별로 동일한 구조 (`standard_names`, `variants`)

---

## 📊 통계 및 모니터링

### 1. 사용 통계
- `usage_count`: 각 variant의 사용 횟수
- `llm_confidence`: LLM 매칭의 평균 신뢰도
- `auto_added_count`: 자동 추가된 매핑 수

### 2. 품질 지표
- 매칭 성공률
- LLM 호출 횟수
- `pending_review` 항목 수

### 3. 로깅
- 정규화 실패 케이스 로깅
- LLM 호출 로깅 (비용 추적용)
- 새로운 표준명 제안 로깅

---

## 🛠 구현 단계

### Phase 1: 파일 구조 및 기본 로더
1. Normalization Map JSON 파일 구조 정의
2. `NormalizationMapLoader` 클래스 구현
   - 파일 로드
   - 메모리 캐싱
   - 파일 저장

### Phase 2: 정규화 로직 개선
1. `normalize_product_name()` → `NormalizationMap` 사용하도록 변경
2. `NameNormalizer.normalize()` → `NormalizationMap` 사용하도록 변경
3. 정확한 매칭, 부분 매칭 로직 구현

### Phase 3: LLM 통합
1. LLM 프롬프트 개선
   - 새로운 표준명 제안 기능 추가
   - **새로운 정규화 규칙 발견 기능 추가**
2. LLM 호출 로직 구현
3. 신뢰도 점수 처리
4. **규칙 발견 시 normalization_rules에 자동 추가**

### Phase 4: 자동 업데이트
1. 매핑 추가/업데이트 로직
2. 파일 저장 메커니즘 (즉시 저장 또는 배치)
3. 파일 잠금 처리

### Phase 5: 통합 및 테스트
1. Phase 5 (Graph 생성)에 통합
2. Phase 8 (질의 처리)에 통합
3. 통합 테스트

### Phase 6: 모니터링 및 최적화
1. 통계 수집
2. 로깅 개선
3. 성능 최적화

---

## 🔐 보안 및 안정성

### 1. 파일 무결성
- JSON 파싱 에러 처리
- 백업 파일 자동 생성
- 파일 손상 시 복구 메커니즘

### 2. 동시성 제어
- 파일 잠금으로 동시 쓰기 방지
- 읽기 전용 모드 지원

### 3. LLM 호출 제한
- Rate limiting
- 에러 핸들링 및 재시도 로직
- LLM 실패 시 폴백 메커니즘

---

## 📝 마이그레이션 계획

### 기존 하드코딩된 매핑 변환

현재 `normalize_product_name()`의 하드코딩된 매핑을 Normalization Map으로 변환:

```python
# 기존 코드
normalization_map = {
    'model 3': 'Tesla Model 3',
    'model s': 'Tesla Model S',
    ...
}

# → JSON 파일로 변환
{
  "categories": [
    {
      "category": "Product",
      "standard_items": ["Tesla Model 3", "Tesla Model S", ...],
      "normalized_map": [
        {
          "standard_item": "Tesla Model 3",
          "variants": ["model 3", "tesla model 3"],
          "metadata": {
            "source": "manual",
            "added_at": "...",
            "total_usage_count": 0
          }
        },
        {
          "standard_item": "Tesla Model S",
          "variants": ["model s", "tesla model s"],
          "metadata": {
            "source": "manual",
            "added_at": "...",
            "total_usage_count": 0
          }
        }
      ]
    }
  ]
}
```

### 마이그레이션 스크립트
- 기존 하드코딩된 매핑을 JSON 파일로 변환
- `data/standard_dicts/`의 기존 파일과 병합 (있는 경우)

---

## 🎯 성공 기준

1. ✅ Normalization Map이 티커별 JSON 파일로 관리됨
2. ✅ 표준명을 찾고, 없으면 LLM으로 찾기
3. ✅ 매칭 실패 시 자동으로 Normalization Map에 추가
4. ✅ **LLM이 발견한 새로운 정규화 규칙이 normalization_rules에 자동 저장됨**
5. ✅ **규칙 기반 매칭이 variants 검색 전에 수행되어 성능 향상**
6. ✅ Phase 5와 Phase 8에서 동일한 Normalization Map 사용
7. ✅ 정규화 성공률 향상
8. ✅ LLM 호출 비용 최적화 (규칙 재사용으로 중복 호출 방지)

---

## 📚 참고사항

### 기존 코드 구조
- `app/services/processing/graph_generator.py`: `normalize_product_name()`
- `app/services/shared/name_normalizer.py`: `NameNormalizer` 클래스
- `app/services/query/cypher_query_builder.py`: Intent 필터 정규화

### 확장 가능성
- 향후 다른 노드 타입 추가 가능 (예: `Event`, `Risk`, `Opportunity`)
- 다른 정규화 규칙 추가 가능 (예: 동의어 사전, 약어 사전)
- 다국어 지원 확장 가능

