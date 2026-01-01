# Phase 5: Static Graph 생성

## 📋 개요

Phase 5는 추출된 데이터에서 Static Graph를 생성하는 단계입니다. Static Graph는 Company, Product, Person, Technology 노드와 이들 간의 관계를 포함합니다. 모든 노드 생성 후 정규화 단계를 거쳐 표준 키워드로 통일합니다.

## 🎯 목표

- Company Node 생성
- Product Node 생성
- Person Node 생성
- Technology Node 생성
- 정규화 단계 (모든 Static Node 정규화)
- Static Link 생성 (MAKE, HAS_RELATION, USES)

## 📥 입력 데이터 상세

### 데이터 소스
- **파일 경로**: `data/extracted/{ticker}/{filing_type}/` 폴더의 JSON 파일
- **데이터 형식**: JSON
- **데이터 구조**:
  ```json
  {
    "ticker": "AAPL",
    "filing_type": "10-K",
    "company_name": "Apple Inc.",
    "sector": "Technology",
    "mentioned_products": ["iPhone", "Mac", "iPad"],
    "mentioned_persons": ["Tim Cook", "Steve Jobs"],
    "mentioned_technologies": ["AI", "Machine Learning"],
    "technologies": ["Artificial Intelligence", "Machine Learning"]
  }
  ```
- **필수 필드**:
  - `ticker`: 회사 티커 심볼
  - `company_name`: 회사명
  - `sector`: 산업 섹터
  - `mentioned_products`: 제품 목록 (선택)
  - `mentioned_persons`: 인물 목록 (선택)
  - `mentioned_technologies` 또는 `technologies`: 기술 목록 (선택)

## 📤 출력 데이터 상세

### 출력 형식
- **파일 경로**: `data/graph/{TICKER}_static_graph.json`
- **데이터 형식**: JSON
- **데이터 구조**:
  ```json
  {
    "nodes": {
      "AAPL": {
        "id": "AAPL",
        "node_type": "Company",
        "ticker": "AAPL",
        "name": "Apple Inc.",
        "sector": "Technology",
        "node_style": "static"
      },
      "product_aapl_iphone_15": {
        "id": "product_aapl_iphone_15",
        "node_type": "Product",
        "name": "iPhone 15",
        "normalized_name": "iPhone 15",
        "node_style": "static"
      }
    },
    "links": [
      {
        "from": "AAPL",
        "to": "product_aapl_iphone_15",
        "link_type": "MAKE",
        "link_style": "static"
      }
    ]
  }
  ```
- **노드 타입**: Company, Product, Person, Technology
- **링크 타입**: MAKE (Company → Product), HAS_RELATION (Company → Person), USES (Company → Technology)

## 🔄 주요 작업 단계

1. **Company Node 생성** (Phase 5.1)
   - 티커당 1개의 Company 노드 생성
   - ID: `{ticker}` 형식

2. **Product Node 생성** (Phase 5.2)
   - `mentioned_products`에서 제품 수집
   - 중복 제거
   - ID: `product_{ticker}_{normalized_name}` 형식

3. **Person Node 생성** (Phase 5.3)
   - `mentioned_persons`에서 인물 수집
   - 중복 제거
   - ID: `person_{ticker}_{normalized_name}` 형식

4. **Technology Node 생성** (Phase 5.4)
   - `mentioned_technologies` 또는 `technologies`에서 기술 수집
   - 중복 제거
   - ID: `tech_{ticker}_{normalized_name}` 형식

5. **정규화 단계** (Phase 5.5)
   - 모든 Static Node (Product, Person, Technology)의 이름 정규화
   - `normalization_map` 파일 활용
   - LLM을 통한 새로운 매핑 결정
   - 새로운 매핑 등록

6. **Static Link 생성** (Phase 5.6)
   - Company → Product: MAKE 링크
   - Company → Person: HAS_RELATION 링크
   - Company → Technology: USES 링크

7. **JSON 파일 저장** (Phase 5.7)
   - `data/graph/{TICKER}_static_graph.json` 파일로 저장

## 📊 사용하는 데이터 구조 및 스키마

### Node 구조
- **Company Node**:
  ```python
  {
    "id": str,  # 티커 심볼
    "node_type": "Company",
    "ticker": str,
    "name": str,
    "sector": str,
    "description": Optional[str],
    "node_style": "static"
  }
  ```

- **Product Node**:
  ```python
  {
    "id": str,  # product_{ticker}_{normalized_name}
    "node_type": "Product",
    "name": str,  # 정규화된 이름
    "normalized_name": str,
    "product_type": Optional[str],
    "category": Optional[str],
    "description": Optional[str],
    "node_style": "static"
  }
  ```

- **Person Node**:
  ```python
  {
    "id": str,  # person_{ticker}_{normalized_name}
    "node_type": "Person",
    "name": str,  # 정규화된 이름
    "normalized_name": str,
    "role": Optional[str],
    "title": Optional[str],
    "description": Optional[str],
    "node_style": "static"
  }
  ```

- **Technology Node**:
  ```python
  {
    "id": str,  # tech_{ticker}_{normalized_name}
    "node_type": "Technology",
    "name": str,  # 정규화된 이름
    "normalized_name": str,
    "category": Optional[str],
    "description": Optional[str],
    "node_style": "static"
  }
  ```

### Link 구조
```python
{
  "from": str,  # 시작 노드 ID
  "to": str,  # 종료 노드 ID
  "link_type": str,  # "MAKE" | "HAS_RELATION" | "USES"
  "link_style": "static"
}
```

### Normalization Map 구조
- **파일 경로**: `data/normalization_maps/{TICKER}_normalization_map.json`
- **구조**: `tasks.mdc` 참조 또는 `phase-5-5.md` 참조

## 🔗 Phase 간 의존성

### 이전 Phase 의존성
- **Phase 4**: 데이터 추출 완료 필요
  - `data/extracted/{ticker}/{filing_type}/` 폴더에 JSON 파일이 존재해야 함
  - 추출된 데이터에 `mentioned_products`, `mentioned_persons`, `mentioned_technologies` 필드 포함

### 다음 Phase로의 데이터 전달
- **Phase 6 (Dynamic Graph 생성)**:
  - `data/graph/{TICKER}_static_graph.json` 파일을 입력으로 사용
  - Static Graph의 Company 노드를 참조하여 Dynamic Node와 연결

## 🔗 관련 문서

- `phase-5-1.md`: Company Node 생성 상세
- `phase-5-2.md`: Product Node 생성 상세
- `phase-5-3.md`: Person Node 생성 상세
- `phase-5-4.md`: Technology Node 생성 상세
- `phase-5-5.md`: 정규화 단계 상세
- `phase-5-6.md`: Static Link 생성 상세
- `phase-5-7.md`: 생성 스크립트 상세

## 📝 History

