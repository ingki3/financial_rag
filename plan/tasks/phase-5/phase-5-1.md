# Phase 5.1: Company Node 생성

## 📋 Sub-task 개요

각 티커에 대해 Company 노드를 생성합니다. Company 노드는 Static Graph의 핵심 노드로, 다른 모든 노드와 링크의 기준점이 됩니다.

### 파일 경로
**파일**: `app/services/processing/graph_generator.py`

### Phase 전체 목표 기여
- Static Graph의 중심 노드 역할
- Product, Person, Technology 노드와의 링크 생성 시 기준점 제공
- 티커별 고유 식별자로 그래프 구조의 루트 역할

### 입력 데이터
- **티커 심볼** (str): 회사 티커 (예: "AAPL")
- **COMPANY_INFO 딕셔너리**: 티커별 회사 정보 (이름, 섹터, 설명)

### 출력 데이터
- **Company 노드 딕셔너리**:
  ```python
  {
      "id": str,  # 티커 심볼
      "node_type": "Company",
      "ticker": str,
      "name": str,
      "sector": str,
      "description": str,
      "node_style": "static"
  }
  ```

### Class 구조
이 Sub-task는 함수 기반 구현으로, 별도의 Class 구조는 없습니다.

#### 함수: `generate_company_node(ticker: str) -> Dict`
- **목적**: 티커 심볼을 입력받아 Company 노드를 생성
- **Input 구조 및 내용**:
  - `ticker` (str): 회사 티커 심볼 (예: "AAPL")
- **Output 형식 및 내용**:
  - `Dict`: Company 노드 딕셔너리
    - `id`: 티커 심볼
    - `node_type`: "Company"
    - `ticker`: 티커 심볼
    - `name`: 회사명
    - `sector`: 산업 섹터
    - `description`: 회사 설명
    - `node_style`: "static"
- **함수 내부 동작 방식**:
  1. `COMPANY_INFO` 딕셔너리에서 티커에 해당하는 회사 정보 조회
  2. 정보가 없으면 기본값 사용 (`{ticker} Inc.`, "Unknown" 섹터)
  3. 노드 딕셔너리 생성 및 반환

## 🎯 주요 기능

1. **티커 기반 노드 생성**
   - 티커 심볼을 ID로 사용하여 고유성 보장
   - 티커당 1개의 Company 노드만 생성

2. **회사 정보 매핑**
   - `COMPANY_INFO` 딕셔너리에서 회사명, 섹터, 설명 조회
   - 정보가 없는 경우 기본값으로 대체

3. **Static Node 속성 설정**
   - `node_type`: "Company"
   - `node_style`: "static"
   - 필수 필드 모두 포함

## 📊 데이터 구조

### 입력 데이터 구조
```python
ticker: str  # 예: "AAPL"
```

### COMPANY_INFO 딕셔너리 구조
```python
COMPANY_INFO = {
    "AAPL": {
        "name": "Apple Inc.",
        "sector": "Technology",
        "description": "Apple Inc.는 스마트폰, 개인용 컴퓨터..."
    },
    # ... 기타 티커
}
```

### 출력 데이터 구조
```python
{
    "id": str,  # 티커 심볼 (예: "AAPL")
    "node_type": "Company",
    "ticker": str,  # 티커 심볼
    "name": str,  # 회사명
    "sector": str,  # 산업 섹터
    "description": str,  # 회사 설명
    "node_style": "static"
}
```

### ID 생성 규칙
- **ID 형식**: `{ticker}` (예: `AAPL`)
- **고유성**: 티커당 1개만 생성
- **대소문자**: 티커 심볼 그대로 사용

## 💻 코드 예시 및 전체 코드 구현

### 함수 구현 코드
```python
def generate_company_node(ticker: str) -> Dict:
    """Company 노드 생성
    
    Args:
        ticker: 티커 심볼 (예: "AAPL")
        
    Returns:
        Company 노드 딕셔너리
    """
    company_info = COMPANY_INFO.get(ticker, {
        "name": f"{ticker} Inc.",
        "sector": "Unknown",
        "description": f"{ticker} 기업 정보"
    })
    
    return {
        "id": ticker,
        "node_type": "Company",
        "ticker": ticker,
        "name": company_info["name"],
        "sector": company_info["sector"],
        "description": company_info["description"],
        "node_style": "static"
    }
```

### 사용 예시
```python
from app.services.processing.graph_generator import generate_company_node

# Company 노드 생성
company_node = generate_company_node("AAPL")
print(company_node)
# 출력:
# {
#     "id": "AAPL",
#     "node_type": "Company",
#     "ticker": "AAPL",
#     "name": "Apple Inc.",
#     "sector": "Technology",
#     "description": "Apple Inc.는 스마트폰...",
#     "node_style": "static"
# }
```

### 에러 핸들링
- 티커 정보가 없는 경우: 기본값으로 대체하여 노드 생성 계속 진행
- 티커가 빈 문자열인 경우: 기본값 사용

## 🔄 상세 알고리즘/프로세스

### 처리 흐름
1. **티커 입력 검증**
   - 티커 심볼이 제공되었는지 확인

2. **회사 정보 조회**
   - `COMPANY_INFO` 딕셔너리에서 티커로 조회
   - 정보가 있으면 해당 정보 사용
   - 정보가 없으면 기본값 생성

3. **노드 딕셔너리 생성**
   - 필수 필드 설정:
     - `id`: 티커 심볼
     - `node_type`: "Company"
     - `ticker`: 티커 심볼
     - `name`: 회사명
     - `sector`: 섹터
     - `description`: 설명
     - `node_style`: "static"

4. **노드 반환**
   - 생성된 노드 딕셔너리 반환

### 예외 처리
- 티커 정보 부재: 기본값으로 대체
- 빈 티커: 기본값 사용

## ⚙️ 설정 및 의존성

### 필요한 환경 변수
- 없음

### 외부 라이브러리 의존성
- 없음 (표준 라이브러리만 사용)

### 설정 파일
- `COMPANY_INFO` 딕셔너리: `app/services/processing/graph_generator.py` 파일 내 상수로 정의
  - 향후 외부 파일이나 API로 확장 가능

## 🧪 테스트 케이스

### 단위 테스트 예시
```python
def test_generate_company_node():
    # 정상 케이스: 알려진 티커
    node = generate_company_node("AAPL")
    assert node["id"] == "AAPL"
    assert node["node_type"] == "Company"
    assert node["name"] == "Apple Inc."
    assert node["sector"] == "Technology"
    assert node["node_style"] == "static"
    
    # 정상 케이스: 알려지지 않은 티커
    node = generate_company_node("UNKNOWN")
    assert node["id"] == "UNKNOWN"
    assert node["name"] == "UNKNOWN Inc."
    assert node["sector"] == "Unknown"
    
    # 정상 케이스: 빈 문자열
    node = generate_company_node("")
    assert node["id"] == ""
    assert node["name"] == " Inc."
```

### 통합 테스트 시나리오
- `generate_static_graph` 함수에서 Company 노드 생성 확인
- 생성된 노드가 Static Graph의 `nodes["Company"]` 리스트에 포함되는지 확인

### 검증 방법
- 노드 ID가 티커와 일치하는지 확인
- 필수 필드가 모두 포함되어 있는지 확인
- `node_type`과 `node_style`이 올바른지 확인

## 📝 History

