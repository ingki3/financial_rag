# Phase 7.1: Graph Loader 모듈 구현

## 📋 Sub-task 개요

FalkorDB에 노드 및 링크를 적재하는 모듈을 구현합니다. MERGE 쿼리를 사용하여 중복을 방지하고, 인덱스를 생성하여 검색 성능을 최적화합니다.

### 파일 경로
**파일**: `app/services/graph/graph_loader.py`

### Phase 전체 목표 기여
- Static/Dynamic Graph JSON 파일을 FalkorDB에 적재
- 인덱스 및 제약조건 생성으로 검색 성능 최적화
- MERGE 쿼리를 통한 중복 방지 메커니즘 제공
- 적재 통계 및 검증 기능 제공

### 입력 데이터
- **Static Graph JSON 파일**: `data/graph/{TICKER}_static_graph.json`
- **Dynamic Graph JSON 파일**: `data/graph/{TICKER}_dynamic_graph.json`
- **환경 변수**:
  - `FALKORDB_HOST`: FalkorDB 호스트 (기본값: localhost)
  - `FALKORDB_PORT`: FalkorDB 포트 (기본값: 6379)

### 출력 데이터
- **FalkorDB에 저장된 노드 및 링크**
- **적재 통계**:
  ```python
  {
      "nodes_created": int,
      "nodes_updated": int,
      "links_created": int,
      "links_updated": int,
      "errors": int,
      "embeddings_stored": int
  }
  ```

### Class 구조

#### Class: `GraphLoader`
FalkorDB에 노드 및 링크를 적재하는 클래스

##### 속성 (Attributes)
- `host` (str): FalkorDB 호스트 주소
- `port` (int): FalkorDB 포트 번호
- `graph_name` (str): 그래프 이름 (기본값: "financial_kg")
- `_client` (Optional[FalkorDB]): FalkorDB 클라이언트 인스턴스
- `_graph`: FalkorDB 그래프 인스턴스
- `_stats` (Dict): 적재 통계 딕셔너리
- `NODE_LABELS` (Dict[str, str]): 노드 타입별 라벨 매핑 (클래스 변수)
- `EMBEDDING_NODE_TYPES` (Set[str]): Embedding이 있는 노드 타입 집합 (클래스 변수)

##### 함수 (Methods)

###### `__init__(self, host: str = None, port: int = None, graph_name: str = "financial_kg")`
- **목적**: GraphLoader 인스턴스 초기화
- **Input 구조 및 내용**:
  - `host` (str, optional): FalkorDB 호스트 (기본값: 환경변수 또는 localhost)
  - `port` (int, optional): FalkorDB 포트 (기본값: 환경변수 또는 6379)
  - `graph_name` (str, optional): 그래프 이름 (기본값: "financial_kg")
- **Output 형식 및 내용**: 없음 (생성자)
- **함수 내부 동작 방식**:
  1. 호스트, 포트, 그래프 이름 설정
  2. 환경 변수에서 기본값 로드 (없으면 기본값 사용)
  3. 통계 딕셔너리 초기화

###### `connect(self)`
- **목적**: FalkorDB에 연결
- **Input 구조 및 내용**: 없음
- **Output 형식 및 내용**: 없음
- **함수 내부 동작 방식**:
  1. FalkorDB 클라이언트 생성
  2. 그래프 선택
  3. 연결 성공 로그 기록

###### `close(self)`
- **목적**: 연결 종료
- **Input 구조 및 내용**: 없음
- **Output 형식 및 내용**: 없음
- **함수 내부 동작 방식**: 연결 종료 로그 기록 (FalkorDB Python client는 명시적 close 불필요)

###### `initialize(self)`
- **목적**: 인덱스 생성
- **Input 구조 및 내용**: 없음
- **Output 형식 및 내용**: 없음
- **함수 내부 동작 방식**:
  1. 각 노드 타입별 id 인덱스 생성
  2. ticker 기반 검색용 인덱스 생성
  3. 인덱스가 이미 존재하는 경우 경고 무시

###### `create_node(self, node: Dict) -> bool`
- **목적**: 노드 생성 (MERGE 사용하여 중복 방지)
- **Input 구조 및 내용**:
  - `node` (Dict): 노드 데이터
    - `id` (str): 노드 ID (필수)
    - `node_type` (str): 노드 타입 (필수)
    - 기타 노드 속성들
- **Output 형식 및 내용**:
  - `bool`: 성공 여부
- **함수 내부 동작 방식**:
  1. 노드 ID와 타입 검증
  2. 노드 라벨 매핑
  3. 노드 속성을 Cypher SET 절로 변환
  4. MERGE 쿼리 실행 (중복 방지)
  5. 통계 업데이트

###### `create_link(self, link: Dict) -> bool`
- **목적**: 링크 생성 (MERGE 사용하여 중복 방지)
- **Input 구조 및 내용**:
  - `link` (Dict): 링크 데이터
    - `from` (str): 시작 노드 ID (필수)
    - `to` (str): 종료 노드 ID (필수)
    - `relationship_type` (str): 관계 타입 (필수)
    - 기타 링크 속성들
- **Output 형식 및 내용**:
  - `bool`: 성공 여부
- **함수 내부 동작 방식**:
  1. 링크 필수 필드 검증
  2. 시작/종료 노드 매칭
  3. MERGE 쿼리로 링크 생성
  4. 링크 속성 설정
  5. 통계 업데이트

###### `load_static_graph(self, ticker: str, static_graph: Dict) -> Dict`
- **목적**: Static Graph 적재
- **Input 구조 및 내용**:
  - `ticker` (str): 티커 심볼
  - `static_graph` (Dict): Static Graph JSON 데이터
    - `nodes` (Dict): 노드 딕셔너리 (Company, Product, Person, Technology)
    - `links` (List[Dict]): 링크 리스트
- **Output 형식 및 내용**:
  - `Dict`: 적재 통계
    - `ticker`: 티커 심볼
    - `nodes`: 노드 타입별 개수
    - `links`: 링크 개수
- **함수 내부 동작 방식**:
  1. 노드 적재 (순서: Company → Product → Person → Technology)
  2. 링크 적재
  3. 통계 반환

###### `load_dynamic_graph(self, ticker: str, dynamic_graph: Dict) -> Dict`
- **목적**: Dynamic Graph 적재
- **Input 구조 및 내용**:
  - `ticker` (str): 티커 심볼
  - `dynamic_graph` (Dict): Dynamic Graph JSON 데이터
    - `nodes` (Dict): 노드 딕셔너리 (Document, Section, Risk, Opportunity, Event, Technology)
    - `links` (List[Dict]): 링크 리스트
- **Output 형식 및 내용**:
  - `Dict`: 적재 통계
    - `ticker`: 티커 심볼
    - `nodes`: 노드 타입별 개수
    - `links`: 링크 개수
- **함수 내부 동작 방식**:
  1. 노드 적재 (순서: Document → Section → Risk/Opportunity/Event/Technology)
  2. 링크 적재
  3. 통계 반환

###### `get_stats(self) -> Dict`
- **목적**: 적재 통계 반환
- **Input 구조 및 내용**: 없음
- **Output 형식 및 내용**:
  - `Dict`: 통계 딕셔너리 복사본
- **함수 내부 동작 방식**: 통계 딕셔너리 복사본 반환

###### `verify(self) -> Dict`
- **목적**: 적재 결과 검증
- **Input 구조 및 내용**: 없음
- **Output 형식 및 내용**:
  - `Dict`: 검증 결과
    - `nodes`: 노드 타입별 개수
    - `links`: 링크 타입별 개수
    - `embeddings`: Embedding이 있는 노드 타입별 개수
    - `total_nodes`: 전체 노드 수
    - `total_links`: 전체 링크 수
    - `total_embeddings`: 전체 Embedding 수
- **함수 내부 동작 방식**:
  1. Cypher 쿼리로 노드 수 확인
  2. Cypher 쿼리로 링크 수 확인
  3. Cypher 쿼리로 Embedding 수 확인
  4. 통계 반환

##### 상속 관계
- 없음 (독립 클래스)

## 🎯 주요 기능

1. **FalkorDB 연결 관리**
   - 호스트/포트 기반 연결
   - 환경 변수 지원
   - 연결 상태 관리

2. **인덱스 생성**
   - 노드 타입별 id 인덱스
   - ticker 기반 검색용 인덱스
   - 중복 인덱스 생성 방지

3. **노드 적재**
   - MERGE 쿼리를 통한 중복 방지
   - 노드 속성 자동 변환 (문자열, 숫자, 불린, 배열)
   - Embedding 데이터 처리
   - 에러 핸들링 및 통계 기록

4. **링크 적재**
   - MERGE 쿼리를 통한 중복 방지
   - 시작/종료 노드 매칭
   - 링크 속성 설정
   - created_at 자동 추가

5. **통계 및 검증**
   - 적재 통계 수집 (노드/링크 생성 수, 에러 수)
   - 적재 결과 검증 (Cypher 쿼리 기반)

## 📊 데이터 구조

### 입력 데이터 구조

#### Static Graph 구조
```python
{
    "ticker": str,
    "generated_at": str,
    "nodes": {
        "Company": List[Dict],
        "Product": List[Dict],
        "Person": List[Dict],
        "Technology": List[Dict]
    },
    "links": List[Dict]
}
```

#### Dynamic Graph 구조
```python
{
    "ticker": str,
    "generated_at": str,
    "nodes": {
        "Document": List[Dict],
        "Section": List[Dict],
        "Risk": List[Dict],
        "Opportunity": List[Dict],
        "Event": List[Dict],
        "Technology": List[Dict]
    },
    "links": List[Dict]
}
```

### 출력 데이터 구조

#### 적재 통계
```python
{
    "nodes_created": int,
    "nodes_updated": int,
    "links_created": int,
    "links_updated": int,
    "errors": int,
    "embeddings_stored": int
}
```

#### 검증 결과
```python
{
    "nodes": Dict[str, int],  # 노드 타입별 개수
    "links": Dict[str, int],  # 링크 타입별 개수
    "embeddings": Dict[str, int],  # Embedding이 있는 노드 타입별 개수
    "total_nodes": int,
    "total_links": int,
    "total_embeddings": int
}
```

## 💻 코드 예시 및 전체 코드 구현

### 클래스 전체 구현
전체 코드는 `app/services/graph/graph_loader.py` 파일을 참조하세요.

### 사용 예시
```python
from app.services.graph.graph_loader import GraphLoader
from pathlib import Path

# GraphLoader 인스턴스 생성
loader = GraphLoader(host="localhost", port=6379)

# 연결
loader.connect()

# 인덱스 생성
loader.initialize()

# Static Graph 적재
static_graph = {
    "ticker": "AAPL",
    "nodes": {
        "Company": [{"id": "AAPL", "node_type": "Company", ...}],
        "Product": [...],
        "Person": [...]
    },
    "links": [...]
}
stats = loader.load_static_graph("AAPL", static_graph)

# 통계 확인
print(loader.get_stats())

# 검증
verify_result = loader.verify()
print(f"Total nodes: {verify_result['total_nodes']}")

# 연결 종료
loader.close()
```

### 에러 핸들링
- 연결 실패: `RuntimeError` 발생
- 노드/링크 생성 실패: 로그 기록 및 통계 업데이트, `False` 반환
- 쿼리 실행 실패: 예외 로깅 및 재발생

## 🔄 상세 알고리즘/프로세스

### 노드 적재 프로세스
1. **노드 검증**
   - `id`와 `node_type` 필드 존재 확인
   - 없으면 경고 로그 및 통계 업데이트, `False` 반환

2. **라벨 매핑**
   - `NODE_LABELS` 딕셔너리에서 노드 타입에 해당하는 라벨 조회
   - 없으면 노드 타입 그대로 사용

3. **속성 변환**
   - `_build_node_properties` 메서드로 Cypher SET 절 생성
   - 문자열 이스케이프 처리
   - Embedding 데이터 배열 처리
   - metadata flat 처리

4. **MERGE 쿼리 실행**
   - `MERGE (n:Label {id: '...'}) SET ...` 형식
   - 중복 방지 (이미 존재하면 업데이트)

5. **통계 업데이트**
   - `nodes_created` 증가
   - 에러 발생 시 `errors` 증가

### 링크 적재 프로세스
1. **링크 검증**
   - `from`, `to`, `relationship_type` 필드 존재 확인
   - 없으면 경고 로그 및 통계 업데이트, `False` 반환

2. **노드 매칭**
   - 시작 노드와 종료 노드 매칭

3. **속성 설정**
   - 링크 속성을 Cypher SET 절로 변환
   - `created_at` 자동 추가

4. **MERGE 쿼리 실행**
   - `MATCH (a {id: '...'}) MATCH (b {id: '...'}) MERGE (a)-[r:Type]->(b) SET ...` 형식
   - 중복 방지

5. **통계 업데이트**
   - `links_created` 증가
   - 에러 발생 시 `errors` 증가

### 예외 처리
- 연결 실패: 예외 발생 및 로깅
- 쿼리 실행 실패: 예외 로깅 및 통계 업데이트, `False` 반환
- 파일 읽기 실패: 예외 로깅 및 계속 진행

## ⚙️ 설정 및 의존성

### 필요한 환경 변수
- `FALKORDB_HOST`: FalkorDB 호스트 (기본값: localhost)
- `FALKORDB_PORT`: FalkorDB 포트 (기본값: 6379)

### 외부 라이브러리 의존성
- `falkordb`: FalkorDB Python 클라이언트

### 설정 파일
- 없음 (환경 변수 또는 생성자 파라미터로 설정)

## 🧪 테스트 케이스

### 단위 테스트 예시
```python
def test_graph_loader_initialization():
    loader = GraphLoader(host="localhost", port=6379)
    assert loader.host == "localhost"
    assert loader.port == 6379
    assert loader.graph_name == "financial_kg"

def test_create_node():
    loader = GraphLoader()
    loader.connect()
    loader.initialize()
    
    node = {
        "id": "test_node",
        "node_type": "Company",
        "name": "Test Company"
    }
    result = loader.create_node(node)
    assert result == True
    
    stats = loader.get_stats()
    assert stats["nodes_created"] > 0

def test_create_link():
    loader = GraphLoader()
    loader.connect()
    loader.initialize()
    
    # 먼저 노드 생성
    loader.create_node({"id": "from", "node_type": "Company"})
    loader.create_node({"id": "to", "node_type": "Product"})
    
    link = {
        "from": "from",
        "to": "to",
        "relationship_type": "MAKE"
    }
    result = loader.create_link(link)
    assert result == True
    
    stats = loader.get_stats()
    assert stats["links_created"] > 0
```

### 통합 테스트 시나리오
- Static Graph 파일 적재 및 검증
- Dynamic Graph 파일 적재 및 검증
- 중복 노드/링크 적재 시 중복 방지 확인
- 통계 수집 정확성 확인

### 검증 방법
- `verify()` 메서드로 노드/링크 수 확인
- Cypher 쿼리로 직접 확인
- 통계와 실제 데이터 비교

## 📝 History

