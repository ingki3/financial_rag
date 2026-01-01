# Phase 5.2: Product Node 생성

## 📋 개요

추출된 데이터에서 언급된 제품을 수집하여 Product 노드를 생성합니다.

## 🎯 목표

- `mentioned_products` 수집
- 이름 정규화 (NormalizationService 사용)
- 중복 제거
- Product Node 생성

## 📝 상세 구현

### Node 구조

```python
{
    "id": "product_aapl_iphone_15_pro",
    "node_type": "Product",
    "name": "iPhone 15 Pro",
    "product_type": "...",
    "category": "...",
    "description": "...",
    "node_style": "static"
}
```

### ID 생성 규칙

- ID: `product_{ticker}_{normalized_name}`
- 정규화: NormalizationService 사용

### 정규화 프로세스

1. NormalizationService.normalize() 호출
2. normalization_map에서 표준명 찾기
3. 없으면 LLM으로 표준명 추천
4. 새로운 표준명이면 normalization_map에 추가

## 📁 파일 위치

**파일**: `app/services/processing/graph_generator.py`

## 📝 History

