# Phase 8.3: Vector 검색 구현

## 📋 Sub-task 개요

의미 기반 검색을 위한 Vector 검색 모듈을 구현합니다. Embedding 기반 유사도 검색을 수행하고, 하이브리드 검색(Graph + Vector)을 지원하며 Top-K 결과를 반환합니다.

### 파일 경로
**파일**: `app/services/query/vector_search.py`

### Phase 전체 목표 기여
- 의미 기반 검색 지원
- Graph 검색과의 하이브리드 검색
- 유사도 기반 노드 검색

### 입력 데이터
- **질의 텍스트** (str): 검색할 텍스트
- **Target 노드 타입** (str, optional): 검색할 노드 타입
- **Top-K** (int): 반환할 결과 수
- **Similarity Threshold** (float): 최소 유사도 임계값

### 출력 데이터
- **검색 결과 리스트** (List[Dict]): 유사도가 높은 노드 리스트
  ```python
  [
    {
      "node_id": str,
      "node_type": str,
      "entity": str,
      "description": str,
      "ticker": str,
      "similarity": float
    }
  ]
  ```

### Class 구조

#### Class: `VectorSearch`
Vector 기반 유사도 검색 클래스

##### 속성 (Attributes)
- `graph_loader` (GraphLoader): GraphLoader 인스턴스

##### 함수 (Methods)

###### `__init__(self, graph_loader: GraphLoader)`
- **목적**: VectorSearch 인스턴스 초기화
- **Input 구조 및 내용**:
  - `graph_loader` (GraphLoader): GraphLoader 인스턴스
- **Output 형식 및 내용**: 없음 (생성자)
- **함수 내부 동작 방식**:
  1. GraphLoader 인스턴스 저장

###### `search(self, query_text: str, target_node_type: Optional[str] = None, top_k: int = 10, similarity_threshold: float = 0.7) -> List[Dict]`
- **목적**: Vector 기반 유사도 검색
- **Input 구조 및 내용**:
  - `query_text` (str): 검색할 텍스트
  - `target_node_type` (str, optional): 검색할 노드 타입 (None이면 모든 타입)
  - `top_k` (int): 반환할 결과 수
  - `similarity_threshold` (float): 최소 유사도 임계값
- **Output 형식 및 내용**:
  - `List[Dict]`: 검색 결과 리스트
- **함수 내부 동작 방식**:
  1. Query 텍스트를 embedding으로 변환
  2. 해당 노드 타입의 모든 노드에서 embedding 가져오기
  3. 코사인 유사도 계산
  4. 유사도 순으로 정렬
  5. Top-K 반환

##### 상속 관계
- 없음 (독립 클래스)

#### 함수: `cosine_similarity(vec1: List[float], vec2: List[float]) -> float`
- **목적**: 코사인 유사도 계산
- **Input 구조 및 내용**:
  - `vec1` (List[float]): 첫 번째 벡터
  - `vec2` (List[float]): 두 번째 벡터
- **Output 형식 및 내용**:
  - `float`: 코사인 유사도 (0.0 ~ 1.0)
- **함수 내부 동작 방식**:
  1. NumPy를 사용하여 벡터 연산
  2. 내적 및 노름 계산
  3. 코사인 유사도 반환

## 🎯 주요 기능

1. **Embedding 기반 유사도 검색**
   - 질의 텍스트를 embedding으로 변환
   - 노드의 description_embedding과 유사도 계산
   - Top-K 노드 반환

2. **하이브리드 검색**
- Graph 검색: 구조화된 관계 탐색
- Vector 검색: 의미 기반 유사도 검색
- 결과 통합 및 정렬

3. **유사도 임계값 필터링**
   - 최소 유사도 임계값 이상인 노드만 반환
   - 기본값: 0.7

## 📊 데이터 구조

### 입력 데이터 구조
- **질의 텍스트**: 검색할 텍스트 문자열
- **Target 노드 타입**: Risk, Opportunity, Event, Technology 등

### 출력 데이터 구조
- **검색 결과**:
  ```python
  {
    "node_id": str,
    "node_type": str,
    "entity": str,
    "description": str,
    "ticker": str,
    "similarity": float  # 0.0 ~ 1.0
  }
  ```

## 💻 코드 예시 및 전체 코드 구현

### 클래스 전체 구현
전체 코드는 `app/services/query/vector_search.py` 파일을 참조하세요.

### 사용 예시
```python
from app.services.query.vector_search import VectorSearch
from app.services.graph.graph_loader import GraphLoader

graph_loader = GraphLoader()
graph_loader.connect()

vector_search = VectorSearch(graph_loader)

# Vector 검색
results = vector_search.search(
    query_text="애플의 기회 요소",
    target_node_type="Opportunity",
    top_k=10,
    similarity_threshold=0.7
)

for result in results:
    print(f"{result['entity']}: {result['similarity']:.2f}")
```

### 에러 핸들링
- Embedding 생성 실패: 빈 리스트 반환
- 노드 embedding 없음: 해당 노드 건너뛰기

## 🔄 상세 알고리즘/프로세스

### 검색 프로세스
1. **질의 텍스트 Embedding 변환**
   - `generate_embedding_sync` 함수 사용
   - Gemini text-embedding-004 모델 사용

2. **노드 Embedding 수집**
   - Graph DB에서 해당 노드 타입의 모든 노드 조회
   - description_embedding 필드 추출

3. **유사도 계산**
   - 각 노드의 embedding과 질의 embedding 간 코사인 유사도 계산
   - 유사도 임계값 이상인 노드만 선택

4. **정렬 및 반환**
   - 유사도 순으로 정렬 (내림차순)
   - Top-K 반환

### 예외 처리
- Embedding 생성 실패: 빈 리스트 반환
- 노드 embedding 없음: 해당 노드 건너뛰기

## ⚙️ 설정 및 의존성

### 필요한 환경 변수
- `GOOGLE_API_KEY`: Gemini API 키 (Embedding 생성 시 필요)

### 외부 라이브러리 의존성
- `numpy`: 벡터 연산
- `google-genai`: Gemini API 클라이언트

### 설정 파일
- 없음

## 🧪 테스트 케이스

### 단위 테스트 예시
```python
def test_cosine_similarity():
    vec1 = [1.0, 0.0, 0.0]
    vec2 = [1.0, 0.0, 0.0]
    similarity = cosine_similarity(vec1, vec2)
    assert similarity == 1.0

def test_vector_search():
    # Vector 검색 테스트
    # ...
```

### 통합 테스트 시나리오
- 실제 Graph DB에서 Vector 검색 테스트
- 유사도 계산 정확도 확인
- Top-K 결과 확인

### 검증 방법
- 검색 결과 수 확인
- 유사도 값 확인 (0.0 ~ 1.0)
- 유사도 순 정렬 확인

## ⚠️ 주의사항

- Embedding이 없는 노드는 검색 결과에 포함되지 않음
- 유사도 임계값 조정 필요 (기본값: 0.7)
- 대량의 노드 검색 시 성능 고려

## 📝 History
