# Phase 6.2: Dynamic Link 생성

## 📋 Sub-task 개요

Dynamic Node 간의 관계를 나타내는 링크를 생성합니다. Document, Section, Risk, Opportunity, Event, Technology 노드 간의 관계와 Static Node와의 연결을 링크로 표현합니다.

### 파일 경로
**파일**: `app/services/processing/dynamic_graph_generator.py`

### Phase 전체 목표 기여
- Dynamic Graph의 관계 구조화
- Dynamic Node 간의 관계 표현
- Static Node와 Dynamic Node 간의 연결

### 입력 데이터
- **Document 노드** (Dict): Document 노드 딕셔너리
- **Section 노드 리스트** (List[Dict]): Section 노드 리스트
- **Dynamic 노드 리스트** (List[Dict]): Risk/Opportunity/Event/Technology 노드 리스트
- **Static Graph** (Dict): Static Graph 데이터 (IS_MENTIONED_IN 링크 생성용)
- **Extracted 데이터** (Dict): Extracted JSON 데이터

### 출력 데이터
- **IS_INCLUDED 링크 리스트** (List[Dict]): Section → Document 링크들
- **IS_EXTRACTED_FROM 링크 리스트** (List[Dict]): Entity → Section 링크들
- **HAS_* 링크 리스트** (List[Dict]): Company → Entity 링크들
- **IS_MENTIONED_IN 링크 리스트** (List[Dict]): Static Node → Dynamic Node 링크들

### Class 구조
이 Sub-task는 함수 기반 구현으로, 별도의 Class 구조는 없습니다.

#### 함수: `generate_is_included_links(section_nodes: List[Dict], doc_node: Dict) -> List[Dict]`
- **목적**: IS_INCLUDED 링크 생성 (Section → Document)
- **Input 구조 및 내용**:
  - `section_nodes` (List[Dict]): Section 노드 리스트
  - `doc_node` (Dict): Document 노드
- **Output 형식 및 내용**:
  - `List[Dict]`: IS_INCLUDED 링크 리스트
- **함수 내부 동작 방식**:
  1. 각 Section 노드에 대해 Document로의 링크 생성
  2. 섹션 순서 정보 포함 (section_order)
  3. 링크 리스트 반환

#### 함수: `generate_is_extracted_from_links(dynamic_nodes: List[Dict], section_nodes: List[Dict], extracted_data: Dict) -> List[Dict]`
- **목적**: IS_EXTRACTED_FROM 링크 생성 (Entity → Section)
- **Input 구조 및 내용**:
  - `dynamic_nodes` (List[Dict]): Dynamic 노드 리스트 (Risk/Opportunity/Event/Technology)
  - `section_nodes` (List[Dict]): Section 노드 리스트
  - `extracted_data` (Dict): Extracted JSON 데이터
- **Output 형식 및 내용**:
  - `List[Dict]`: IS_EXTRACTED_FROM 링크 리스트
- **함수 내부 동작 방식**:
  1. 각 Dynamic 노드의 메타데이터에서 source_section 확인
  2. 해당 Section 노드 찾기
  3. Entity에서 Section으로의 링크 생성
  4. 링크 리스트 반환

#### 함수: `generate_has_links(ticker: str, nodes: List[Dict], link_type: str) -> List[Dict]`
- **목적**: HAS_* 링크 생성 (Company → Entity)
- **Input 구조 및 내용**:
  - `ticker` (str): 티커 심볼
  - `nodes` (List[Dict]): Entity 노드 리스트
  - `link_type` (str): 링크 타입 (HAS_RISKS, HAS_OPPORTUNITIES, HAS_EVENTS, HAS_TECHNOLOGIES)
- **Output 형식 및 내용**:
  - `List[Dict]`: HAS_* 링크 리스트
- **함수 내부 동작 방식**:
  1. Company 노드 ID 생성 (티커 심볼)
  2. 각 Entity 노드에 대해 Company에서 Entity로의 링크 생성
  3. 링크 리스트 반환

#### 함수: `generate_is_mentioned_in_links(dynamic_nodes: List[Dict], static_nodes: Dict, extracted_data: Dict) -> List[Dict]`
- **목적**: IS_MENTIONED_IN 링크 생성 (Static Node → Dynamic Node)
- **Input 구조 및 내용**:
  - `dynamic_nodes` (List[Dict]): Dynamic 노드 리스트
  - `static_nodes` (Dict): Static Graph의 nodes 딕셔너리
  - `extracted_data` (Dict): Extracted JSON 데이터
- **Output 형식 및 내용**:
  - `List[Dict]`: IS_MENTIONED_IN 링크 리스트
- **함수 내부 동작 방식**:
  1. Static 노드 매핑 생성 (name_lower -> id)
  2. 각 Dynamic 노드의 임시 필드(`_mentioned_products`, `_mentioned_persons`, `_mentioned_companies`) 확인
  3. Static 노드와 매칭하여 링크 생성
  4. 링크 리스트 반환

## 🎯 주요 기능

1. **IS_INCLUDED Link 생성**
   - Section → Document 관계 표현
   - 섹션 순서 정보 포함

2. **IS_EXTRACTED_FROM Link 생성**
   - Entity → Section 관계 표현
   - 엔티티가 추출된 섹션 정보 포함

3. **HAS_* Link 생성**
   - Company → Risk/Opportunity/Event/Technology 관계 표현
   - 링크 타입별 생성 (HAS_RISKS, HAS_OPPORTUNITIES, HAS_EVENTS, HAS_TECHNOLOGIES)

4. **IS_MENTIONED_IN Link 생성**
   - Static Node → Dynamic Node 관계 표현
   - Product/Person/Company가 Dynamic Node에서 언급된 관계

## 📊 데이터 구조

### 입력 데이터 구조
- **Document/Section/Dynamic 노드 리스트**: 각 노드의 `id` 필드 사용
- **Static Graph**: Static 노드 딕셔너리

### 출력 데이터 구조
- **IS_INCLUDED Link**:
```python
{
    "from": str,  # Section 노드 ID
    "to": str,  # Document 노드 ID
    "relationship_type": "IS_INCLUDED",
    "created_at": str,
    "metadata": {
      "section_order": int  # 섹션 순서
    }
}
```

- **IS_EXTRACTED_FROM Link**:
```python
{
    "from": str,  # Entity 노드 ID
    "to": str,  # Section 노드 ID
    "relationship_type": "IS_EXTRACTED_FROM"
}
```

- **HAS_* Link**:
```python
{
    "from": str,  # Company 노드 ID (티커)
    "to": str,  # Entity 노드 ID
    "relationship_type": str,  # HAS_RISKS, HAS_OPPORTUNITIES, HAS_EVENTS, HAS_TECHNOLOGIES
    "created_at": str
}
```

- **IS_MENTIONED_IN Link**:
```python
{
    "from": str,  # Static 노드 ID
    "to": str,  # Dynamic 노드 ID
    "relationship_type": "IS_MENTIONED_IN",
    "mention_context": str,  # 선택적
    "created_at": str,
    "metadata": {
      "mention_type": str  # 노드 타입
    }
}
```

## 💻 코드 예시 및 전체 코드 구현

### 함수 구현 코드
전체 코드는 `app/services/processing/dynamic_graph_generator.py` 파일의 다음 함수들을 참조하세요:
- `generate_is_included_links`
- `generate_is_extracted_from_links`
- `generate_has_links`
- `generate_is_mentioned_in_links`

### 사용 예시
```python
from app.services.processing.dynamic_graph_generator import (
    generate_is_included_links,
    generate_has_links,
    generate_is_mentioned_in_links
)

# 링크 생성
is_included_links = generate_is_included_links(section_nodes, doc_node)
has_risks_links = generate_has_links("AAPL", risk_nodes, "HAS_RISKS")
is_mentioned_links = generate_is_mentioned_in_links(
    dynamic_nodes, static_nodes, extracted_data
)
```

### 에러 핸들링
- 노드 ID 누락: 해당 노드 건너뛰기
- 매칭 실패: 로깅 및 계속 진행

## 🔄 상세 알고리즘/프로세스

### 링크 생성 프로세스
1. **IS_INCLUDED 링크**
   - 각 Section 노드에 대해 Document로의 링크 생성
   - 섹션 순서 정보 포함

2. **IS_EXTRACTED_FROM 링크**
   - 각 Dynamic 노드의 source_section 확인
   - 해당 Section 노드 찾기 및 링크 생성

3. **HAS_* 링크**
   - Company 노드 ID 생성 (티커 심볼)
   - 각 Entity 노드에 대해 Company에서 Entity로의 링크 생성

4. **IS_MENTIONED_IN 링크**
   - Static 노드 매핑 생성
   - Dynamic 노드의 임시 필드 확인
   - 매칭되는 Static 노드와 링크 생성

### 예외 처리
- 노드 ID 누락: 해당 노드 건너뛰기
- 매칭 실패: 로깅 및 계속 진행

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
def test_generate_is_included_links():
    section_nodes = [...]
    doc_node = {...}
    links = generate_is_included_links(section_nodes, doc_node)
    
    assert len(links) == len(section_nodes)
    assert all(link["relationship_type"] == "IS_INCLUDED" for link in links)

def test_generate_has_links():
    # HAS_* 링크 생성 테스트
    # ...
```

### 통합 테스트 시나리오
- 실제 노드 리스트로 링크 생성 테스트
- 링크 구조 확인
- 매칭 정확도 확인

### 검증 방법
- 생성된 링크 수 확인
- 링크 구조 확인
- 매칭 정확도 확인

## ⚠️ 주의사항

- IS_MENTIONED_IN 링크 생성 시 Static 노드의 정규화된 이름과 매칭해야 함
- 임시 필드는 링크 생성 후 제거됨
- 매칭 실패 시 링크가 생성되지 않을 수 있음

## 📝 History
