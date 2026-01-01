# Phase 6.3: Embedding 생성

## 📋 Sub-task 개요

Risk, Opportunity, Event, Technology 노드에 의미 기반 검색을 위한 embedding을 추가합니다. Gemini text-embedding-004 모델을 사용하여 768차원 벡터를 생성하고, 배치 처리로 효율성을 향상시킵니다.

### 파일 경로
**파일**: `app/services/shared/embedding_generator.py`

### Phase 전체 목표 기여
- 의미 기반 검색 지원
- Phase 8의 Vector 검색을 위한 embedding 데이터 제공
- 유사도 기반 노드 검색 가능

### 입력 데이터
- **노드 리스트** (List[Dict]): Risk/Opportunity/Event/Technology 노드 리스트
- **환경 변수**: `GOOGLE_API_KEY` (Gemini API 키)

### 출력 데이터
- **Embedding이 추가된 노드 리스트** (List[Dict]): `description_embedding` 필드가 추가된 노드들

### Class 구조
이 Sub-task는 함수 기반 구현으로, 별도의 Class 구조는 없습니다.

#### 함수: `add_embeddings_to_nodes_sync(nodes: List[Dict]) -> List[Dict]`
- **목적**: 노드 리스트에 embedding 추가 (동기 버전)
- **Input 구조 및 내용**:
  - `nodes` (List[Dict]): 노드 리스트
- **Output 형식 및 내용**:
  - `List[Dict]`: `description_embedding` 필드가 추가된 노드 리스트
- **함수 내부 동작 방식**:
  1. 각 노드의 description 텍스트 추출
  2. 배치 단위로 embedding 생성
  3. 노드에 `description_embedding` 필드 추가
  4. 업데이트된 노드 리스트 반환

#### 함수: `generate_embeddings_batch(texts: List[str], batch_size: int = 100) -> List[List[float]]`
- **목적**: 배치 단위 embedding 생성
- **Input 구조 및 내용**:
  - `texts` (List[str]): 텍스트 리스트
  - `batch_size` (int, optional): 배치 크기 (기본값: 100)
- **Output 형식 및 내용**:
  - `List[List[float]]`: 768차원 벡터 리스트
- **함수 내부 동작 방식**:
  1. 텍스트 리스트를 배치로 분할
  2. 각 배치에 대해 Gemini API 호출
  3. Embedding 벡터 추출 및 반환

## 🎯 주요 기능

1. **Embedding 텍스트 생성**
   - Risk: `{entity}: {description}`
   - Opportunity: `{entity}: {description}`
   - Event: `{entity} ({date}): {description}`
   - Technology: `{entity}: {description}`

2. **배치 처리**
   - 여러 텍스트를 배치로 묶어서 처리
   - API 호출 횟수 최소화

3. **노드 업데이트**
   - 각 노드에 `description_embedding` 필드 추가
   - 768차원 벡터 저장

## 📊 데이터 구조

### 입력 데이터 구조
- **노드 리스트**:
  ```python
  [
    {
      "id": "risk_aapl_intense_competition_2024",
      "node_type": "Risk",
      "entity": "Intense Competition",
      "description": "..."
    }
  ]
  ```

### 출력 데이터 구조
- **Embedding이 추가된 노드**:
  ```python
  {
    "id": "risk_aapl_intense_competition_2024",
    "node_type": "Risk",
    "entity": "Intense Competition",
    "description": "...",
    "description_embedding": [0.123, 0.456, ...]  # 768차원
  }
  ```

### Embedding 대상 노드
- **Risk**: `{entity}: {description}`
- **Opportunity**: `{entity}: {description}`
- **Event**: `{entity} ({date}): {description}`
- **Technology**: `{entity}: {description}`

## 💻 코드 예시 및 전체 코드 구현

### 함수 구현 코드
전체 코드는 `app/services/shared/embedding_generator.py` 파일을 참조하세요.

### 사용 예시
```python
from app.services.shared.embedding_generator import add_embeddings_to_nodes_sync

# 노드 리스트
risk_nodes = [
    {
        "id": "risk_aapl_intense_competition_2024",
        "entity": "Intense Competition",
        "description": "..."
    }
]

# Embedding 추가
risk_nodes_with_embedding = add_embeddings_to_nodes_sync(risk_nodes)

# Embedding 확인
for node in risk_nodes_with_embedding:
    assert "description_embedding" in node
    assert len(node["description_embedding"]) == 768
```

### 에러 핸들링
- API 호출 실패: 예외 처리 및 로깅
- 텍스트가 없는 노드: embedding 없이 유지

## 🔄 상세 알고리즘/프로세스

### Embedding 생성 프로세스
1. **텍스트 추출**
   - 각 노드의 entity와 description 조합
   - 노드 타입별 텍스트 형식 적용

2. **배치 처리**
   - 텍스트 리스트를 배치로 분할
   - 배치 크기: 기본 100개

3. **API 호출**
   - Gemini text-embedding-004 모델 사용
   - 배치 단위로 API 호출

4. **노드 업데이트**
   - 각 노드에 `description_embedding` 필드 추가
   - 768차원 벡터 저장

### 예외 처리
- API 호출 실패: 예외 처리 및 로깅
- 텍스트가 없는 노드: embedding 없이 유지

## ⚙️ 설정 및 의존성

### 필요한 환경 변수
- `GOOGLE_API_KEY`: Gemini API 키 (필수)

### 외부 라이브러리 의존성
- `google-genai`: Gemini API 클라이언트

### 설정 파일
- 없음

## 🧪 테스트 케이스

### 단위 테스트 예시
```python
def test_add_embeddings_to_nodes_sync():
    nodes = [
        {"id": "test", "entity": "Test", "description": "Test description"}
    ]
    nodes_with_embedding = add_embeddings_to_nodes_sync(nodes)
    
    assert "description_embedding" in nodes_with_embedding[0]
    assert len(nodes_with_embedding[0]["description_embedding"]) == 768

def test_generate_embeddings_batch():
    # 배치 embedding 생성 테스트
    # ...
```

### 통합 테스트 시나리오
- 실제 노드 리스트로 embedding 생성 테스트
- 배치 처리 확인
- Embedding 벡터 차원 확인

### 검증 방법
- Embedding 필드 존재 확인
- 벡터 차원 확인 (768차원)
- 배치 처리 효율성 확인

## ⚠️ 주의사항

- API 호출량: ~1,569 노드 → ~19회 배치 호출 (배치 크기 100 기준)
- API 비용 발생
- 배치 크기 조정 가능 (기본값: 100)
- Embedding 생성 시간: 노드 수에 비례

## 📝 History
