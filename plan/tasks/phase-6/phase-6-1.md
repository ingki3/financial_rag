# Phase 6.1: Dynamic Node 생성

## 📋 개요

Document, Section, Risk, Opportunity, Event, Technology 노드를 생성합니다.

## 🎯 목표

- 각 노드 타입별 고유 ID 생성
- 필수 필드 설정
- 메타데이터 포함

## 📝 상세 구현

### Document Node

```python
{
    "id": "doc_aapl_10-k_0000320193-24-000077",
    "node_type": "Document",
    "ticker": "AAPL",
    "filing_type": "10-K",
    "accession_number": "0000320193-24-000077",
    "year": 2024,
    "sections_included": [...]
}
```

### Section Node

```python
{
    "id": "section_aapl_10-k_2024_business",
    "node_type": "Section",
    "section_name": "business",
    "filing_type": "10-K",
    "ticker": "AAPL",
    "year": 2024
}
```

### Risk/Opportunity/Event/Technology Node

```python
{
    "id": "risk_aapl_intense_competition_2024",
    "node_type": "Risk",
    "ticker": "AAPL",
    "entity": "Intense Competition",
    "description": "...",
    "metadata": {
        "source_section": "risk_factors",
        "filing_type": "10-K",
        "accession_number": "..."
    }
}
```

## 📁 파일 위치

**파일**: `app/services/processing/dynamic_graph_generator.py`

## 📝 History

