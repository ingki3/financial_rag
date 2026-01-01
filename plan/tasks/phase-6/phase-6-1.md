# Phase 6.1: Dynamic Node 생성

## 📋 Sub-task 개요

Document, Section, Risk, Opportunity, Event, Technology 노드를 생성합니다. Extracted 데이터에서 동적 엔티티를 추출하여 Dynamic Graph의 노드로 변환합니다.

### 파일 경로
**파일**: `app/services/processing/dynamic_graph_generator.py`

### Phase 전체 목표 기여
- Dynamic Graph의 노드 생성
- 공시 문서, 섹션, 리스크, 기회, 이벤트, 기술 정보의 구조화
- Static Graph와의 연결을 위한 노드 제공

### 입력 데이터
- **Extracted JSON 파일**: `data/extracted/{ticker}/{filing_type}/` 폴더의 JSON 파일들
- **Extracted JSON 구조**:
  ```json
  {
    "ticker": "AAPL",
    "filing_type": "10-K",
    "accession_number": "0000320193-24-000077",
    "year": 2024,
    "risks": [...],
    "opportunities": [...],
    "events": [...],
    "technologies": [...]
  }
  ```

### 출력 데이터
- **Document 노드 리스트** (List[Dict])
- **Section 노드 리스트** (List[Dict])
- **Risk 노드 리스트** (List[Dict])
- **Opportunity 노드 리스트** (List[Dict])
- **Event 노드 리스트** (List[Dict])
- **Technology 노드 리스트** (List[Dict])

### Class 구조
이 Sub-task는 함수 기반 구현으로, 별도의 Class 구조는 없습니다.

#### 함수: `generate_document_node(extracted_data: Dict) -> Dict`
- **목적**: Document 노드 생성
- **Input 구조 및 내용**:
  - `extracted_data` (Dict): extracted JSON 데이터
- **Output 형식 및 내용**:
  - `Dict`: Document 노드 딕셔너리
- **함수 내부 동작 방식**:
  1. 티커, 공시 유형, Accession Number 추출
  2. Document ID 생성: `doc_{ticker}_{filing_type}_{accession_number}`
  3. Document 노드 딕셔너리 생성 및 반환

#### 함수: `generate_section_nodes(extracted_data: Dict) -> List[Dict]`
- **목적**: Section 노드 생성
- **Input 구조 및 내용**:
  - `extracted_data` (Dict): extracted JSON 데이터
- **Output 형식 및 내용**:
  - `List[Dict]`: Section 노드 리스트
- **함수 내부 동작 방식**:
  1. Extracted 데이터에서 섹션 정보 추출
  2. 각 섹션에 대해 Section 노드 생성
  3. Section ID 생성: `section_{ticker}_{filing_type}_{year}_{section_name}`
  4. Section 노드 리스트 반환

#### 함수: `generate_entity_nodes(extracted_data: Dict, category: str, node_type: str, id_prefix: str) -> List[Dict]`
- **목적**: Risk/Opportunity/Event/Technology 노드 생성 (공통 로직)
- **Input 구조 및 내용**:
  - `extracted_data` (Dict): extracted JSON 데이터
  - `category` (str): 카테고리 키 (risks, opportunities, events, technologies)
  - `node_type` (str): 노드 타입 (Risk, Opportunity, Event, Technology)
  - `id_prefix` (str): ID 접두사 (risk, opp, event, tech)
- **Output 형식 및 내용**:
  - `List[Dict]`: 노드 리스트
- **함수 내부 동작 방식**:
  1. Extracted 데이터에서 해당 카테고리의 엔티티 추출
  2. 각 엔티티에 대해 노드 생성
  3. 노드 ID 생성: `{id_prefix}_{ticker}_{normalized_entity}_{year}`
  4. 메타데이터 및 임시 필드 설정
  5. 노드 리스트 반환

#### 함수: `generate_risk_nodes(extracted_data: Dict) -> List[Dict]`
- **목적**: Risk 노드 생성
- **Input 구조 및 내용**:
  - `extracted_data` (Dict): extracted JSON 데이터
- **Output 형식 및 내용**:
  - `List[Dict]`: Risk 노드 리스트
- **함수 내부 동작 방식**:
  - `generate_entity_nodes(extracted_data, "risks", "Risk", "risk")` 호출

#### 함수: `generate_opportunity_nodes(extracted_data: Dict) -> List[Dict]`
- **목적**: Opportunity 노드 생성
- **Input 구조 및 내용**:
  - `extracted_data` (Dict): extracted JSON 데이터
- **Output 형식 및 내용**:
  - `List[Dict]`: Opportunity 노드 리스트
- **함수 내부 동작 방식**:
  - `generate_entity_nodes(extracted_data, "opportunities", "Opportunity", "opp")` 호출

#### 함수: `generate_event_nodes(extracted_data: Dict) -> List[Dict]`
- **목적**: Event 노드 생성
- **Input 구조 및 내용**:
  - `extracted_data` (Dict): extracted JSON 데이터
- **Output 형식 및 내용**:
  - `List[Dict]`: Event 노드 리스트
- **함수 내부 동작 방식**:
  - `generate_entity_nodes(extracted_data, "events", "Event", "event")` 호출

#### 함수: `generate_technology_nodes(extracted_data: Dict) -> List[Dict]`
- **목적**: Technology 노드 생성 (Dynamic)
- **Input 구조 및 내용**:
  - `extracted_data` (Dict): extracted JSON 데이터
- **Output 형식 및 내용**:
  - `List[Dict]`: Technology 노드 리스트
- **함수 내부 동작 방식**:
  - `generate_entity_nodes(extracted_data, "technologies", "Technology", "tech")` 호출

## 🎯 주요 기능

1. **Document Node 생성**
   - 공시 문서를 나타내는 노드 생성
   - 티커, 공시 유형, Accession Number 포함

2. **Section Node 생성**
   - 공시 섹션을 나타내는 노드 생성
   - 섹션 이름, 연도 정보 포함

3. **Entity Node 생성**
   - Risk, Opportunity, Event, Technology 노드 생성
   - 엔티티 이름, 설명, 메타데이터 포함
   - 임시 필드 보존 (링크 생성 시 사용)

## 📊 데이터 구조

### 입력 데이터 구조
- **Extracted JSON 파일**: Phase 4에서 추출된 Triplet 데이터

### 출력 데이터 구조
- **Document Node**:
  ```python
  {
    "id": "doc_aapl_10-k_0000320193-24-000077",
    "node_type": "Document",
    "ticker": "AAPL",
    "filing_type": "10-K",
    "accession_number": "0000320193-24-000077",
    "year": 2024,
    "sections_included": [...],
    "node_style": "dynamic"
  }
  ```

- **Section Node**:
  ```python
  {
    "id": "section_aapl_10-k_2024_business",
    "node_type": "Section",
    "section_name": "business",
    "filing_type": "10-K",
    "ticker": "AAPL",
    "year": 2024,
    "node_style": "dynamic"
  }
  ```

- **Risk/Opportunity/Event/Technology Node**:
  ```python
  {
    "id": "risk_aapl_intense_competition_2024",
    "node_type": "Risk",
    "ticker": "AAPL",
    "entity": "Intense Competition",
    "description": "...",
    "node_style": "dynamic",
    "metadata": {
      "source_section": "risk_factors",
      "filing_type": "10-K",
      "accession_number": "..."
    },
    "_mentioned_products": [...],  # 임시 필드
    "_mentioned_persons": [...],   # 임시 필드
    "_mentioned_companies": [...]  # 임시 필드
  }
  ```

## 💻 코드 예시 및 전체 코드 구현

### 함수 구현 코드
전체 코드는 `app/services/processing/dynamic_graph_generator.py` 파일을 참조하세요.

### 사용 예시
```python
from app.services.processing.dynamic_graph_generator import (
    generate_document_node,
    generate_section_nodes,
    generate_risk_nodes
)

# Extracted 데이터
extracted_data = {
    "ticker": "AAPL",
    "filing_type": "10-K",
    "risks": [...]
}

# 노드 생성
doc_node = generate_document_node(extracted_data)
section_nodes = generate_section_nodes(extracted_data)
risk_nodes = generate_risk_nodes(extracted_data)
```

### 에러 핸들링
- 파일 읽기 실패: 경고 로그 및 계속 진행
- 엔티티 정보 부재: 빈 리스트 반환

## 🔄 상세 알고리즘/프로세스

### 노드 생성 프로세스
1. **Extracted 파일 읽기**
   - 각 extracted JSON 파일 읽기
   - 데이터 파싱

2. **Document 노드 생성**
   - 각 파일에 대해 Document 노드 생성
   - 중복 체크 (ID 기준)

3. **Section 노드 생성**
   - Extracted 데이터에서 섹션 정보 추출
   - 각 섹션에 대해 Section 노드 생성
   - 중복 체크

4. **Entity 노드 생성**
   - 각 카테고리(risks, opportunities, events, technologies)에 대해 노드 생성
   - 엔티티 이름, 설명, 메타데이터 포함
   - 임시 필드 보존 (링크 생성 시 사용)
   - 중복 체크

### 예외 처리
- 파일 읽기 실패: 경고 로그 및 계속 진행
- 엔티티 정보 부재: 빈 리스트 반환

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
def test_generate_document_node():
    extracted_data = {
        "ticker": "AAPL",
        "filing_type": "10-K",
        "accession_number": "0000320193-24-000077"
    }
    node = generate_document_node(extracted_data)
    
    assert node["node_type"] == "Document"
    assert node["ticker"] == "AAPL"

def test_generate_risk_nodes():
    # Risk 노드 생성 테스트
    # ...
```

### 통합 테스트 시나리오
- 실제 extracted 파일로 노드 생성 테스트
- 중복 제거 확인
- 노드 구조 확인

### 검증 방법
- 생성된 노드 수 확인
- 노드 구조 확인
- 중복 제거 확인

## ⚠️ 주의사항

- 임시 필드(`_mentioned_products`, `_mentioned_persons`, `_mentioned_companies`)는 링크 생성 후 제거됨
- 중복 체크는 노드 ID 기준으로 수행
- 동일한 엔티티가 여러 파일에 나타날 수 있음 (연도별로 구분)

## 📝 History
