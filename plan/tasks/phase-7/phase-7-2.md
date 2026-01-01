# Phase 7.2: Cypher 쿼리 패턴

## 📋 Sub-task 개요

FalkorDB에 노드 및 링크를 생성하기 위한 Cypher 쿼리 패턴을 정의합니다. MERGE를 사용하여 중복을 방지하고, 인덱스를 생성하여 검색 성능을 최적화합니다.

### 파일 경로
**해당 없음** (쿼리 패턴 정의)

### Phase 전체 목표 기여
- Graph DB 저장을 위한 쿼리 패턴 표준화
- 중복 방지 메커니즘 제공
- 검색 성능 최적화를 위한 인덱스 패턴

### 입력 데이터
- **노드 데이터** (Dict): 노드 딕셔너리
- **링크 데이터** (Dict): 링크 딕셔너리

### 출력 데이터
- **Cypher 쿼리 문자열**: 실행 가능한 Cypher 쿼리

### Class 구조
**해당 없음** (쿼리 패턴 정의)

## 🎯 주요 기능

1. **노드 생성 쿼리 패턴**
   - MERGE를 사용한 중복 방지
   - 속성 설정 (SET 절)

2. **링크 생성 쿼리 패턴**
   - 시작/종료 노드 매칭
   - MERGE를 사용한 중복 방지
   - 링크 속성 설정

3. **인덱스 생성 쿼리 패턴**
   - 노드 타입별 id 인덱스
   - ticker 기반 검색용 인덱스

## 📊 데이터 구조

### 노드 생성 쿼리 패턴
```cypher
MERGE (n:Company {id: $id})
SET n.ticker = $ticker, n.name = $name, n.sector = $sector
```

### 링크 생성 쿼리 패턴
```cypher
MATCH (a:Company {id: $from_id})
MATCH (b:Risk {id: $to_id})
MERGE (a)-[r:HAS_RISKS]->(b)
SET r.created_at = $created_at
```

### 인덱스 생성 쿼리 패턴
```cypher
CREATE INDEX FOR (n:Company) ON (n.id)
CREATE INDEX FOR (n:Company) ON (n.ticker)
```

## 💻 코드 예시 및 전체 코드 구현

### 노드 생성 (MERGE)
```cypher
MERGE (n:Company {id: 'AAPL'})
SET n.ticker = 'AAPL', n.name = 'Apple Inc.', n.sector = 'Technology'
```

### 링크 생성 (MERGE)
```cypher
MATCH (a:Company {id: 'AAPL'})
MATCH (b:Risk {id: 'risk_aapl_intense_competition_2024'})
MERGE (a)-[r:HAS_RISKS]->(b)
SET r.created_at = '2024-01-01T00:00:00Z'
```

### 인덱스 생성
```cypher
CREATE INDEX FOR (n:Company) ON (n.id)
CREATE INDEX FOR (n:Product) ON (n.id)
CREATE INDEX FOR (n:Person) ON (n.id)
CREATE INDEX FOR (n:Technology) ON (n.id)
CREATE INDEX FOR (n:Document) ON (n.id)
CREATE INDEX FOR (n:Section) ON (n.id)
CREATE INDEX FOR (n:Risk) ON (n.id)
CREATE INDEX FOR (n:Opportunity) ON (n.id)
CREATE INDEX FOR (n:Event) ON (n.id)
```

### 인덱스 생성 (ticker 기반)
```cypher
CREATE INDEX FOR (n:Company) ON (n.ticker)
CREATE INDEX FOR (n:Risk) ON (n.ticker)
CREATE INDEX FOR (n:Opportunity) ON (n.ticker)
CREATE INDEX FOR (n:Event) ON (n.ticker)
CREATE INDEX FOR (n:Technology) ON (n.ticker)
```

## 🔄 상세 알고리즘/프로세스

### 노드 생성 프로세스
1. **MERGE 절**
   - 노드 라벨과 id로 노드 존재 확인
   - 없으면 생성, 있으면 기존 노드 사용

2. **SET 절**
   - 노드 속성 설정
   - 문자열 이스케이프 처리

### 링크 생성 프로세스
1. **MATCH 절**
   - 시작 노드와 종료 노드 매칭

2. **MERGE 절**
   - 관계 타입으로 관계 존재 확인
   - 없으면 생성, 있으면 기존 관계 사용

3. **SET 절**
   - 관계 속성 설정
   - created_at 자동 추가

### 인덱스 생성 프로세스
1. **CREATE INDEX 절**
   - 노드 라벨과 속성으로 인덱스 생성
   - 중복 인덱스 생성 시도 시 무시

## ⚙️ 설정 및 의존성

### 필요한 환경 변수
- 없음

### 외부 라이브러리 의존성
- `falkordb`: FalkorDB Python 클라이언트

### 설정 파일
- 없음

## 🧪 테스트 케이스

### 단위 테스트 예시
```cypher
-- 노드 생성 테스트
MERGE (n:Company {id: 'TEST'})
SET n.name = 'Test Company'
RETURN n

-- 링크 생성 테스트
MATCH (a:Company {id: 'TEST'})
MATCH (b:Product {id: 'test_product'})
MERGE (a)-[r:MAKE]->(b)
RETURN r
```

### 통합 테스트 시나리오
- 실제 노드/링크로 쿼리 실행 테스트
- 중복 방지 확인
- 인덱스 생성 확인

### 검증 방법
- 쿼리 실행 성공 확인
- 중복 노드/링크 생성 방지 확인
- 인덱스 존재 확인

## ⚠️ 주의사항

- MERGE를 사용하여 중복 방지
- 문자열 이스케이프 처리 필요
- 인덱스가 이미 존재하는 경우 무시
- 대량 데이터 적재 시 배치 처리 고려

## 📝 History
