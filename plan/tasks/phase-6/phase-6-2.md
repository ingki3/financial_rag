# Phase 6.2: Dynamic Link 생성

## 📋 개요

Dynamic Node 간의 관계를 나타내는 링크를 생성합니다.

## 🎯 목표

- IS_INCLUDED Link (Section → Document)
- IS_EXTRACTED_FROM Link (Risk/Opp/Event/Tech → Section)
- HAS_* Link (Company → Risk/Opp/Event/Tech)
- IS_MENTIONED_IN Link (Product/Person/Company → Dynamic Node)

## 📝 상세 구현

### IS_INCLUDED Link

```python
{
    "from": "section_aapl_10-k_2024_business",
    "to": "doc_aapl_10-k_0000320193-24-000077",
    "relationship_type": "IS_INCLUDED",
    "section_order": 1
}
```

### IS_EXTRACTED_FROM Link

```python
{
    "from": "risk_aapl_intense_competition_2024",
    "to": "section_aapl_10-k_2024_risk_factors",
    "relationship_type": "IS_EXTRACTED_FROM"
}
```

### HAS_RISKS Link

```python
{
    "from": "AAPL",
    "to": "risk_aapl_intense_competition_2024",
    "relationship_type": "HAS_RISKS"
}
```

### IS_MENTIONED_IN Link

```python
{
    "from": "product_aapl_iphone_15_pro",
    "to": "risk_aapl_intense_competition_2024",
    "relationship_type": "IS_MENTIONED_IN",
    "mention_context": "..."
}
```

## 📁 파일 위치

**파일**: `app/services/processing/dynamic_graph_generator.py`

## 📝 History

