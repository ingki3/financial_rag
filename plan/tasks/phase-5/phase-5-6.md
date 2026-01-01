# Phase 5.6: Static Link 생성

## 📋 Sub-task 개요

Static Node 간의 관계를 나타내는 링크를 생성합니다. Company와 Product, Person, Technology 노드 간의 관계를 링크로 표현합니다.

### 파일 경로
**파일**: `app/services/processing/graph_generator.py`

### Phase 전체 목표 기여
- Static Graph의 관계 구조화
- Company와 다른 Static Node 간의 관계 표현
- 그래프 탐색 및 분석을 위한 링크 제공

### 입력 데이터
- **Company 노드 ID** (str): Company 노드의 ID (예: "AAPL")
- **Product 노드 리스트** (List[Dict]): Phase 5.2에서 생성된 Product 노드들
- **Person 노드 리스트** (List[Dict]): Phase 5.3에서 생성된 Person 노드들
- **Technology 노드 리스트** (List[Dict]): Phase 5.4에서 생성된 Technology 노드들
- **Extracted 파일 리스트** (List[Path]): HAS_RELATION 링크의 role 정보 추출용

### 출력 데이터
- **MAKE 링크 리스트** (List[Dict]): Company → Product 링크들
- **HAS_RELATION 링크 리스트** (List[Dict]): Company → Person 링크들
- **USES 링크 리스트** (List[Dict]): Company → Technology 링크들

### Class 구조
이 Sub-task는 함수 기반 구현으로, 별도의 Class 구조는 없습니다.

#### 함수: `generate_make_links(company_id: str, product_nodes: List[Dict]) -> List[Dict]`
- **목적**: MAKE 링크 생성 (Company → Product)
- **Input 구조 및 내용**:
  - `company_id` (str): Company 노드 ID
  - `product_nodes` (List[Dict]): Product 노드 리스트
- **Output 형식 및 내용**:
  - `List[Dict]`: MAKE 링크 리스트
- **함수 내부 동작 방식**:
  1. 각 Product 노드에 대해 Company에서 Product로의 MAKE 링크 생성
  2. 링크 딕셔너리 생성 및 반환

#### 함수: `generate_has_relation_links(company_id: str, person_nodes: List[Dict], extracted_files: List[Path]) -> List[Dict]`
- **목적**: HAS_RELATION 링크 생성 (Company → Person)
- **Input 구조 및 내용**:
  - `company_id` (str): Company 노드 ID
  - `person_nodes` (List[Dict]): Person 노드 리스트
  - `extracted_files` (List[Path]): extracted JSON 파일 경로 리스트 (role 정보 추출용)
- **Output 형식 및 내용**:
  - `List[Dict]`: HAS_RELATION 링크 리스트
- **함수 내부 동작 방식**:
  1. Extracted 파일에서 Person 이름 → role 매핑 생성
  2. 각 Person 노드에 대해 Company에서 Person으로의 HAS_RELATION 링크 생성
  3. role 정보가 있으면 링크에 포함
  4. 링크 딕셔너리 생성 및 반환

#### 함수: `generate_uses_links(company_id: str, technology_nodes: List[Dict]) -> List[Dict]`
- **목적**: USES 링크 생성 (Company → Technology)
- **Input 구조 및 내용**:
  - `company_id` (str): Company 노드 ID
  - `technology_nodes` (List[Dict]): Technology 노드 리스트
- **Output 형식 및 내용**:
  - `List[Dict]`: USES 링크 리스트
- **함수 내부 동작 방식**:
  1. 각 Technology 노드에 대해 Company에서 Technology로의 USES 링크 생성
  2. 링크 딕셔너리 생성 및 반환

## 🎯 주요 기능

1. **MAKE Link 생성**
   - Company → Product 관계 표현
   - 모든 Product 노드에 대해 링크 생성

2. **HAS_RELATION Link 생성**
   - Company → Person 관계 표현
   - Extracted 파일에서 role 정보 추출
   - role 정보가 있으면 링크에 포함

3. **USES Link 생성**
   - Company → Technology 관계 표현
   - 모든 Technology 노드에 대해 링크 생성

## 📊 데이터 구조

### 입력 데이터 구조
- **Company 노드 ID**: `"AAPL"`
- **Product/Person/Technology 노드 리스트**: 각 노드의 `id` 필드 사용

### 출력 데이터 구조
- **MAKE Link**:
  ```python
  {
    "from": str,  # Company 노드 ID
    "to": str,  # Product 노드 ID
    "link_type": "MAKE",
    "link_style": "static"
  }
  ```

- **HAS_RELATION Link**:
  ```python
  {
    "from": str,  # Company 노드 ID
    "to": str,  # Person 노드 ID
    "link_type": "HAS_RELATION",
    "role": str,  # 선택적 (예: "CEO")
    "link_style": "static"
  }
  ```

- **USES Link**:
  ```python
  {
    "from": str,  # Company 노드 ID
    "to": str,  # Technology 노드 ID
    "link_type": "USES",
    "link_style": "static"
  }
  ```

## 💻 코드 예시 및 전체 코드 구현

### 함수 구현 코드
전체 코드는 `app/services/processing/graph_generator.py` 파일의 다음 함수들을 참조하세요:
- `generate_make_links`
- `generate_has_relation_links`
- `generate_uses_links`

### 사용 예시
```python
from app.services.processing.graph_generator import (
    generate_make_links,
    generate_has_relation_links,
    generate_uses_links
)

company_id = "AAPL"
product_nodes = [...]
person_nodes = [...]
technology_nodes = [...]
extracted_files = [...]

# 링크 생성
make_links = generate_make_links(company_id, product_nodes)
has_relation_links = generate_has_relation_links(
    company_id, person_nodes, extracted_files
)
uses_links = generate_uses_links(company_id, technology_nodes)

print(f"Generated {len(make_links)} MAKE links")
print(f"Generated {len(has_relation_links)} HAS_RELATION links")
print(f"Generated {len(uses_links)} USES links")
```

### 에러 핸들링
- 파일 읽기 실패: 경고 로그 및 계속 진행
- 노드 ID 누락: 해당 노드 건너뛰기

## 🔄 상세 알고리즘/프로세스

### MAKE Link 생성 프로세스
1. **Product 노드 순회**
   - 각 Product 노드에 대해 Company에서 Product로의 링크 생성
   - 링크 딕셔너리 생성: `from`, `to`, `link_type`, `link_style`

2. **링크 리스트 반환**
   - 생성된 링크 리스트 반환

### HAS_RELATION Link 생성 프로세스
1. **Role 정보 추출**
   - Extracted 파일에서 Person 이름 → role 매핑 생성
   - `mentioned_persons_global` 및 각 카테고리의 `mentioned_persons`에서 role 정보 수집

2. **Person 노드 순회**
   - 각 Person 노드에 대해 Company에서 Person으로의 링크 생성
   - role 정보가 있으면 링크에 포함

3. **링크 리스트 반환**
   - 생성된 링크 리스트 반환

### USES Link 생성 프로세스
1. **Technology 노드 순회**
   - 각 Technology 노드에 대해 Company에서 Technology로의 링크 생성
   - 링크 딕셔너리 생성: `from`, `to`, `link_type`, `link_style`

2. **링크 리스트 반환**
   - 생성된 링크 리스트 반환

### 예외 처리
- 파일 읽기 실패: 경고 로그 및 계속 진행
- 노드 ID 누락: 해당 노드 건너뛰기

## ⚙️ 설정 및 의존성

### 필요한 환경 변수
- 없음

### 외부 라이브러리 의존성
- 없음 (표준 라이브러리만 사용)

### 설정 파일
- 없음

## 🧪 테스트 케이스

### 단위 테스트 예시
```python
def test_generate_make_links():
    company_id = "AAPL"
    product_nodes = [
        {"id": "product_aapl_iphone", "name": "iPhone"}
    ]
    
    links = generate_make_links(company_id, product_nodes)
    
    assert len(links) == 1
    assert links[0]["from"] == "AAPL"
    assert links[0]["to"] == "product_aapl_iphone"
    assert links[0]["link_type"] == "MAKE"

def test_generate_has_relation_links():
    # HAS_RELATION 링크 생성 테스트
    # ...
```

### 통합 테스트 시나리오
- 실제 노드 리스트로 링크 생성 테스트
- role 정보 포함 확인
- 링크 구조 확인

### 검증 방법
- 생성된 링크 수 확인
- 링크 구조 확인
- role 정보 포함 확인

## ⚠️ 주의사항

- 링크 생성은 정규화 단계(Phase 5.5) 이후에 수행해야 함
- 노드 ID가 정규화된 이름 기반이어야 함
- role 정보는 선택적이므로 없을 수 있음

## 📝 History
