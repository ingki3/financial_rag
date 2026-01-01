# Phase 8.2: Cypher 쿼리 빌더 구현

## 📋 Sub-task 개요

Intent를 기반으로 동적 Cypher 쿼리를 생성하는 모듈을 구현합니다. 다양한 질의 유형을 지원하고, 최적화된 쿼리를 생성합니다.

### 파일 경로
**파일**: `app/services/query/cypher_query_builder.py`

### Phase 전체 목표 기여
- Intent 기반 동적 쿼리 생성
- 다양한 질의 유형 지원
- 최적화된 Cypher 쿼리 생성

### 입력 데이터
- **Intent 딕셔너리** (Dict): Intent 추출 결과
  ```python
  {
    "target_entity_type": "Risk",
    "filters": {
      "ticker": "AAPL"
    },
    "query_type": "list"
  }
  ```

### 출력 데이터
- **Cypher 쿼리 문자열** (str): 실행 가능한 Cypher 쿼리
- **파라미터 딕셔너리** (Dict): 쿼리 파라미터

### Class 구조

#### Class: `CypherQueryBuilder`
Intent를 기반으로 Cypher 쿼리를 생성하는 클래스

##### 속성 (Attributes)
- `name_normalizer` (NameNormalizer): 이름 표준화 모듈
- `TARGET_LINK_MAP` (Dict): Target 타입별 링크 타입 매핑 (클래스 변수)

##### 함수 (Methods)

###### `__init__(self, name_normalizer: Optional[NameNormalizer] = None)`
- **목적**: CypherQueryBuilder 인스턴스 초기화
- **Input 구조 및 내용**:
  - `name_normalizer` (NameNormalizer, optional): 이름 표준화 모듈
- **Output 형식 및 내용**: 없음 (생성자)
- **함수 내부 동작 방식**:
  1. NameNormalizer 인스턴스 생성 또는 전달받은 인스턴스 사용

###### `build_query(self, intent: Dict) -> Tuple[str, Dict[str, Any]]`
- **목적**: Intent를 기반으로 Cypher 쿼리 생성
- **Input 구조 및 내용**:
  - `intent` (Dict): Intent 객체 (target, filters 또는 target_entity_type, filters 포함)
- **Output 형식 및 내용**:
  - `Tuple[str, Dict[str, Any]]`: 생성된 Cypher 쿼리와 파라미터 딕셔너리
- **함수 내부 동작 방식**:
  1. Target 타입 추출
  2. Filters를 리스트로 변환
  3. 이름 표준화 (필터의 이름 정규화)
  4. Target 타입에 따라 적절한 쿼리 빌더 메서드 호출

##### 상속 관계
- 없음 (독립 클래스)

## 🎯 주요 기능

1. **Intent 기반 쿼리 생성**
   - Target 타입에 따른 쿼리 패턴 선택
   - Filters를 쿼리 조건으로 변환

2. **다양한 질의 유형 지원**
   - explain: 설명 요청
   - list: 목록 요청
   - compare: 비교 요청
   - analyze: 분석 요청

3. **최적화된 쿼리 생성**
   - 인덱스 활용
   - 효율적인 패턴 매칭

## 📊 데이터 구조

### 입력 데이터 구조
- **Intent 딕셔너리**:
  ```python
  {
    "target_entity_type": str,  # Risk, Opportunity, Event, Technology, Product, Person, general
    "filters": Dict,  # 필터 조건
    "query_type": str  # explain, list, compare, analyze
  }
  ```

### 출력 데이터 구조
- **Cypher 쿼리**:
  ```cypher
  MATCH (c:Company {ticker: $ticker})-[:HAS_RISKS]->(r:Risk)
  RETURN r
  ```

- **파라미터 딕셔너리**:
  ```python
  {
    "ticker": "AAPL"
  }
  ```

### 쿼리 패턴 예시
```cypher
// 기회 요소 질의
MATCH (c:Company {ticker: $ticker})-[:HAS_OPPORTUNITIES]->(o:Opportunity)
RETURN o

// 제품 관련 리스크
MATCH (p:Product {name: $product_name})-[:IS_MENTIONED_IN]->(r:Risk)
RETURN r
```

## 💻 코드 예시 및 전체 코드 구현

### 클래스 전체 구현
전체 코드는 `app/services/query/cypher_query_builder.py` 파일을 참조하세요.

### 사용 예시
```python
from app.services.query.cypher_query_builder import CypherQueryBuilder

builder = CypherQueryBuilder()

intent = {
    "target_entity_type": "Risk",
    "filters": {
        "ticker": "AAPL"
    },
    "query_type": "list"
}

cypher_query, params = builder.build_query(intent)
print(cypher_query)
print(params)
```

### 에러 핸들링
- Intent 형식 오류: 기본 쿼리 반환
- 필터 매칭 실패: 경고 로그 및 계속 진행

## 🔄 상세 알고리즘/프로세스

### 쿼리 생성 프로세스
1. **Target 타입 추출**
   - Intent에서 target_entity_type 또는 target.node_type 추출

2. **Filters 변환**
   - Filters를 리스트로 변환
   - 이름 표준화 (NameNormalizer 사용)

3. **쿼리 패턴 선택**
   - Target 타입이 general이면 일반 쿼리
   - Target 타입이 Opportunity, Risk, Event이면 패턴 매칭 쿼리
   - 기타 타입이면 다른 쿼리 패턴

4. **쿼리 생성**
   - 선택된 패턴에 따라 Cypher 쿼리 생성
   - 파라미터 딕셔너리 생성

### 예외 처리
- Intent 형식 오류: 기본 쿼리 반환
- 필터 매칭 실패: 경고 로그 및 계속 진행

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
def test_build_query():
    builder = CypherQueryBuilder()
    intent = {
        "target_entity_type": "Risk",
        "filters": {"ticker": "AAPL"}
    }
    query, params = builder.build_query(intent)
    
    assert "MATCH" in query
    assert "ticker" in params
```

### 통합 테스트 시나리오
- 다양한 Intent로 쿼리 생성 테스트
- 쿼리 실행 테스트
- 결과 검증

### 검증 방법
- 생성된 쿼리 구문 확인
- 파라미터 정확성 확인
- 쿼리 실행 결과 확인

## ⚠️ 주의사항

- Intent 형식이 올바르지 않으면 기본 쿼리 반환
- 이름 표준화가 중요 (정규화된 이름 사용)
- 쿼리 최적화를 위해 인덱스 활용

## 📝 History
