# Phase 5.4: Technology Node 생성

## 📋 Sub-task 개요

추출된 데이터에서 언급된 기술을 수집하여 Technology 노드를 생성합니다. `mentioned_technologies` 또는 `technologies` 필드에서 기술 정보를 수집하고, 중복을 제거한 후 Technology 노드를 생성합니다.

### 파일 경로
**파일**: `app/services/processing/graph_generator.py`

### Phase 전체 목표 기여
- Static Graph의 Technology 노드 생성
- Company와 Technology 간의 USES 링크 생성을 위한 노드 제공
- 기술 정보의 구조화 및 표준화

### 입력 데이터
- **티커 심볼** (str): 회사 티커 (예: "AAPL")
- **Extracted 파일 리스트** (List[Path]): `data/extracted/{ticker}/{filing_type}/` 폴더의 JSON 파일들
- **Extracted JSON 구조**:
  ```json
  {
    "mentioned_technologies": ["Artificial Intelligence", "Machine Learning"],
    "technologies": [
      {"entity": "Artificial Intelligence", "description": "..."}
    ],
    "opportunities": [
      {"mentioned_technologies": ["AI", "ML"]}
    ],
    "risks": [...],
    "events": [...]
  }
  ```

### 출력 데이터
- **Technology 노드 리스트** (List[Dict]):
  ```python
  [
    {
      "id": "tech_aapl_artificial_intelligence",
      "node_type": "Technology",
      "name": "Artificial Intelligence",
      "category": "...",
      "description": "...",
      "node_style": "static"
    }
  ]
  ```

### Class 구조
이 Sub-task는 함수 기반 구현으로, 별도의 Class 구조는 없습니다.

#### 함수: `generate_technology_nodes(ticker: str, extracted_files: List[Path]) -> List[Dict]`
- **목적**: 추출된 파일에서 Technology 노드 생성
- **Input 구조 및 내용**:
  - `ticker` (str): 티커 심볼
  - `extracted_files` (List[Path]): extracted JSON 파일 경로 리스트
- **Output 형식 및 내용**:
  - `List[Dict]`: Technology 노드 리스트
- **함수 내부 동작 방식**:
  1. 모든 extracted 파일에서 `mentioned_technologies` 및 `technologies` 수집
  2. 중복 제거 (원본 이름 기준, 대소문자 무시)
  3. Technology 노드 생성 및 반환

## 🎯 주요 기능

1. **기술 수집**
   - `mentioned_technologies` 배열에서 기술 수집
   - `technologies` 카테고리의 엔티티 수집
   - 각 카테고리(opportunities, risks, events)의 `mentioned_technologies` 수집

2. **중복 제거**
   - 원본 이름 기준으로 중복 제거 (대소문자 무시)
   - 정규화는 Phase 5.5에서 수행

3. **노드 생성**
   - Technology 노드 딕셔너리 생성
   - ID 형식: `tech_{ticker}_{normalized_name}` (정규화 전에는 임시 ID)

## 📊 데이터 구조

### 입력 데이터 구조
- **Extracted JSON 파일**:
  ```json
  {
    "mentioned_technologies": ["Artificial Intelligence", "Machine Learning"],
    "technologies": [
      {"entity": "Artificial Intelligence", "description": "..."}
    ],
    "opportunities": [
      {"mentioned_technologies": ["AI", "ML"]}
    ]
  }
  ```

### 출력 데이터 구조
- **Technology 노드**:
  ```python
  {
    "id": str,  # tech_{ticker}_{normalized_name}
    "node_type": "Technology",
    "name": str,  # 정규화 전 원본 이름
    "category": str,  # 기술 카테고리 (선택적)
    "description": str,  # 기술 설명 (선택적)
    "node_style": "static"
  }
  ```

### ID 생성 규칙
- **ID 형식**: `tech_{ticker}_{normalized_name}`
- **정규화**: Phase 5.5 정규화 단계에서 수행
- **임시 ID**: 정규화 전에는 `normalize_id` 함수로 생성된 임시 ID 사용

### 데이터 소스
- `data/extracted/{ticker}/{filing_type}/` 파일의 `technologies` 필드
- 또는 `mentioned_technologies` 필드

## 💻 코드 예시 및 전체 코드 구현

### 함수 구현 코드
전체 코드는 `app/services/processing/graph_generator.py` 파일의 `generate_technology_nodes` 함수를 참조하세요.

### 사용 예시
```python
from app.services.processing.graph_generator import generate_technology_nodes
from pathlib import Path

# Extracted 파일 목록
extracted_files = list(Path("data/extracted/AAPL").rglob("*.json"))

# Technology 노드 생성
technology_nodes = generate_technology_nodes("AAPL", extracted_files)

print(f"Generated {len(technology_nodes)} Technology nodes")
for node in technology_nodes[:5]:
    print(f"  - {node['name']} ({node['id']})")
```

### 에러 핸들링
- 파일 읽기 실패: 경고 로그 및 계속 진행
- 기술 정보 부재: 빈 리스트 반환

## 🔄 상세 알고리즘/프로세스

### 처리 흐름
1. **기술 수집**
   - 모든 extracted 파일 순회
   - `mentioned_technologies` 배열 수집
   - `technologies` 카테고리의 엔티티 수집
   - 각 카테고리의 `mentioned_technologies` 수집

2. **중복 제거**
   - 원본 이름을 소문자로 변환하여 키로 사용
   - 중복 제거 (첫 번째 항목 유지)

3. **노드 생성**
   - Technology 노드 딕셔너리 생성
   - ID, 이름, 카테고리, 설명 설정

4. **반환**
   - Technology 노드 리스트 반환

### 예외 처리
- 파일 읽기 실패: 경고 로그 및 계속 진행
- 기술 정보 부재: 빈 리스트 반환

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
def test_generate_technology_nodes():
    extracted_files = [Path("test_data/extracted.json")]
    nodes = generate_technology_nodes("AAPL", extracted_files)
    
    assert len(nodes) > 0
    assert all(node["node_type"] == "Technology" for node in nodes)
    assert all("id" in node for node in nodes)
    assert all("name" in node for node in nodes)

def test_technology_deduplication():
    # 중복 제거 테스트
    # ...
```

### 통합 테스트 시나리오
- 실제 extracted 파일로 Technology 노드 생성 테스트
- 중복 제거 확인

### 검증 방법
- 생성된 노드 수 확인
- 노드 구조 확인
- 중복 제거 확인

## ⚠️ 주의사항

- 정규화는 Phase 5.5에서 수행되므로, 이 단계에서는 원본 이름 사용
- 중복 제거는 대소문자 무시하지만, 정규화 전 단계이므로 완전한 중복 제거는 아님
- `mentioned_technologies`와 `technologies` 필드 모두에서 수집하므로 중복 가능성 있음

## 📝 History
