# Phase 5.5: 정규화 단계

## 📋 Sub-task 개요

생성된 모든 Static Node (Company, Product, Person, Technology)에 대해 정규화를 수행합니다. 정규화는 동일한 의미를 가진 다양한 표현을 표준 키워드로 통일하는 과정입니다. normalization_map 파일을 활용하고, 매핑이 없는 경우 LLM을 통해 새로운 매핑을 결정합니다.

### 파일 경로
**파일**: `app/services/processing/graph_generator.py`

**사용 서비스**:
- `app/services/shared/normalization_service.py`: 정규화 로직
- `app/services/shared/normalization_map_loader.py`: normalization_map 파일 로드/저장

### Phase 전체 목표 기여
- Static Node 이름의 표준화 및 통일
- 중복 노드 제거를 위한 정규화된 이름 기반 ID 재생성
- 그래프 데이터의 일관성 및 품질 향상

### 입력 데이터
- **티커 심볼** (str): 회사 티커 (예: "AAPL")
- **Product 노드 리스트** (List[Dict]): Phase 5.2에서 생성된 Product 노드들
- **Person 노드 리스트** (List[Dict]): Phase 5.3에서 생성된 Person 노드들
- **Technology 노드 리스트** (List[Dict]): Phase 5.4에서 생성된 Technology 노드들
- **normalization_map 파일**: `data/normalization_maps/{TICKER}_normalization_map.json`

### 출력 데이터
- **정규화된 Product 노드 리스트** (List[Dict]): 정규화된 이름과 ID를 가진 Product 노드들
- **정규화된 Person 노드 리스트** (List[Dict]): 정규화된 이름과 ID를 가진 Person 노드들
- **정규화된 Technology 노드 리스트** (List[Dict]): 정규화된 이름과 ID를 가진 Technology 노드들
- **업데이트된 normalization_map 파일**: 새로운 매핑이 추가된 파일

### Class 구조
이 Sub-task는 함수 기반 구현으로, 별도의 Class 구조는 없습니다. `NormalizationService`와 `NormalizationMapLoader`를 사용합니다.

#### 함수: `normalize_static_nodes(ticker: str, product_nodes: List[Dict], person_nodes: List[Dict], technology_nodes: List[Dict]) -> tuple[List[Dict], List[Dict], List[Dict]]`
- **목적**: Static 노드들을 정규화
- **Input 구조 및 내용**:
  - `ticker` (str): 티커 심볼
  - `product_nodes` (List[Dict]): Product 노드 리스트
  - `person_nodes` (List[Dict]): Person 노드 리스트
  - `technology_nodes` (List[Dict]): Technology 노드 리스트
- **Output 형식 및 내용**:
  - `tuple[List[Dict], List[Dict], List[Dict]]`: 정규화된 Product, Person, Technology 노드 리스트
- **함수 내부 동작 방식**:
  1. NormalizationService 인스턴스 생성
  2. 각 노드 타입별로 정규화 수행:
     - normalization_map 파일 참조
     - 매핑이 없으면 LLM을 통한 매핑 결정
     - 새로운 매핑 등록
  3. 정규화된 이름으로 노드 업데이트
  4. ID 재생성 (정규화된 이름 기반)
  5. 중복 제거 (정규화된 ID 기준)
  6. 정규화된 노드 리스트 반환

## 🎯 주요 기능

1. **normalization_map 파일 참조**
   - `data/normalization_maps/{TICKER}_normalization_map.json` 파일 로드
   - 해당 카테고리의 `normalized_map`에서 매핑 확인
   - `variants` 배열에 현재 이름이 포함되어 있으면, 해당 `standard_item`로 매핑

2. **LLM을 통한 매핑 결정**
   - normalization_map에 매핑이 없는 경우
   - LLM에게 현재 이름, 카테고리, 기존 standard_items 목록 제공
   - LLM이 적절한 표준 키워드를 추천하거나, 새로운 표준 키워드를 제안

3. **새로운 매핑 등록**
   - LLM이 제안한 표준 키워드가 기존 standard_items에 없는 경우
   - normalization_map 파일에 새로운 항목 추가
   - `metadata`에 생성 정보 기록

4. **노드 업데이트**
   - 노드의 `name` 필드를 정규화된 이름으로 업데이트
   - 노드의 `normalized_name` 필드에 정규화된 이름 저장
   - 노드 ID 재생성: `{type}_{ticker}_{normalized_name}`

5. **중복 제거**
   - 정규화된 ID 기준으로 중복 제거
   - 동일한 정규화된 이름을 가진 노드는 하나만 유지

## 📊 데이터 구조

### 입력 데이터 구조
- **Product/Person/Technology 노드**:
  ```python
  {
    "id": str,  # 임시 ID
    "node_type": str,
    "name": str,  # 원본 이름
    ...
  }
  ```

### 출력 데이터 구조
- **정규화된 노드**:
  ```python
  {
    "id": str,  # 정규화된 이름 기반 ID
    "node_type": str,
    "name": str,  # 정규화된 이름
    "normalized_name": str,  # 정규화된 이름 (명시적)
    ...
  }
  ```

### normalization_map 파일 구조
```json
{
  "metadata": {
    "ticker": "AAPL",
    "version": "1.0.0",
    "created_at": "...",
    "last_updated": "...",
    "total_mappings": 34,
    "llm_generated_count": 5,
    "auto_added_count": 2
  },
  "categories": [
    {
      "category": "Product",
      "standard_items": ["iPhone 15", "Mac", ...],
      "normalized_map": [
        {
          "standard_item": "iPhone 15",
          "variants": ["iphone", "iphone 15", "iphone 15 pro"],
          "metadata": {
            "added_at": "...",
            "total_usage_count": 54,
            "source": "static_graph"
          }
        }
      ]
    },
    {
      "category": "Person",
      "standard_items": [...],
      "normalized_map": [...]
    },
    {
      "category": "Technology",
      "standard_items": [...],
      "normalized_map": [...]
    }
  ]
}
```

### 정규화 대상
- **Product Node**: `name` 필드
- **Person Node**: `name` 필드
- **Technology Node**: `name` 필드
- **Company Node**: 정규화 불필요 (티커가 고유 ID)

### 정규화 결과 반영
- 노드의 `name` 필드를 정규화된 이름으로 업데이트
- 노드의 `normalized_name` 필드에 정규화된 이름 저장
- 노드 ID는 정규화된 이름을 기반으로 재생성: `{type}_{ticker}_{normalized_name}`

## 💻 코드 예시 및 전체 코드 구현

### 함수 구현 코드
전체 코드는 `app/services/processing/graph_generator.py` 파일의 `normalize_static_nodes` 함수를 참조하세요.

### 사용 예시
```python
from app.services.processing.graph_generator import normalize_static_nodes

# 노드 리스트
product_nodes = [...]
person_nodes = [...]
technology_nodes = [...]

# 정규화 수행
normalized_products, normalized_persons, normalized_technologies = normalize_static_nodes(
    "AAPL", product_nodes, person_nodes, technology_nodes
)

print(f"Normalized: Products={len(normalized_products)}, "
      f"Persons={len(normalized_persons)}, "
      f"Technologies={len(normalized_technologies)}")
```

### 에러 핸들링
- 정규화 실패: 원본 이름 유지 및 경고 로그
- LLM API 호출 실패: 예외 처리 및 원본 이름 유지
- 파일 저장 실패: 예외 처리 및 로깅

## 🔄 상세 알고리즘/프로세스

### 정규화 프로세스
각 노드 타입(Product, Person, Technology)에 대해 다음 순서로 정규화를 수행:

1. **normalization_map 파일 참조**
   - `data/normalization_maps/{TICKER}_normalization_map.json` 파일 로드
   - 해당 카테고리(Product/Person/Technology)의 `normalized_map`에서 매핑 확인
   - `variants` 배열에 현재 이름이 포함되어 있으면, 해당 `standard_item`로 매핑

2. **LLM을 통한 매핑 결정**
   - normalization_map에 매핑이 없는 경우
   - LLM에게 다음 정보 제공:
     - 현재 이름
     - 카테고리 (Product/Person/Technology)
     - 기존 standard_items 목록
   - LLM이 적절한 표준 키워드를 추천하거나, 새로운 표준 키워드를 제안

3. **새로운 매핑 등록**
   - LLM이 제안한 표준 키워드가 기존 standard_items에 없는 경우
   - normalization_map 파일에 새로운 항목 추가:
     - `standard_items`에 추가
     - `normalized_map`에 새로운 매핑 추가
     - `metadata`에 생성 정보 기록 (source: "llm_suggested" 또는 "auto_added")

4. **노드 업데이트**
   - 노드의 `name` 필드를 정규화된 이름으로 업데이트
   - 노드의 `normalized_name` 필드에 정규화된 이름 저장
   - 노드 ID 재생성: `{type}_{ticker}_{normalized_name}`

5. **중복 제거**
   - 정규화된 ID 기준으로 중복 제거
   - 동일한 정규화된 이름을 가진 노드는 하나만 유지

### 예외 처리
- 정규화 실패: 원본 이름 유지 및 경고 로그
- LLM API 호출 실패: 예외 처리 및 원본 이름 유지
- 파일 저장 실패: 예외 처리 및 로깅

## ⚙️ 설정 및 의존성

### 필요한 환경 변수
- `GOOGLE_API_KEY`: Gemini API 키 (LLM 매핑 결정 시 필요)

### 외부 라이브러리 의존성
- `google-genai`: Gemini LLM API 클라이언트 (LLM 매핑 결정 시)

### 설정 파일
- `data/normalization_maps/{TICKER}_normalization_map.json`: 정규화 매핑 파일

## 🧪 테스트 케이스

### 단위 테스트 예시
```python
def test_normalize_static_nodes():
    product_nodes = [{"id": "product_aapl_iphone", "name": "iPhone"}]
    person_nodes = []
    technology_nodes = []
    
    normalized_products, normalized_persons, normalized_technologies = normalize_static_nodes(
        "AAPL", product_nodes, person_nodes, technology_nodes
    )
    
    assert len(normalized_products) > 0
    assert "normalized_name" in normalized_products[0]

def test_normalization_map_loading():
    # normalization_map 파일 로드 테스트
    # ...
```

### 통합 테스트 시나리오
- 실제 노드 리스트로 정규화 테스트
- normalization_map 파일 업데이트 확인
- 중복 제거 확인

### 검증 방법
- 정규화된 노드 수 확인
- normalization_map 파일 내용 확인
- 중복 제거 확인

## ⚠️ 주의사항

- LLM API 비용 발생 (새로운 매핑 결정 시)
- 정규화 실패 시 원본 이름 유지
- normalization_map 파일은 자동으로 업데이트됨
- 정규화 후 ID가 변경되므로 링크 생성 전에 수행해야 함

## 📝 History
