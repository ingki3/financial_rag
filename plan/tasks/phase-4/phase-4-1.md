# Phase 4.1: 추출기 모듈 구현

## 📋 개요

LLM을 활용하여 텍스트에서 Knowledge Triplet을 추출하는 모듈을 구현합니다.

## 🎯 목표

- Gemini LLM API 연동
- 구조화된 Triplet 추출
- 프롬프트 YAML 관리
- 배치 처리 지원

## 📝 상세 구현

### 클래스 구조

```python
class TripletExtractor:
    """LLM을 활용한 Knowledge Triplet 추출 클래스"""
    
    def extract(
        self,
        text: str,
        ticker: str,
        filing_type: str,
        section: str,
        accession_number: str
    ) -> ExtractedTriplets:
        """텍스트에서 트리플렛 추출"""
```

### 추출 대상

- Opportunities: 기회 요소
- Risks: 리스크 요소
- Events: 주요 이벤트 (날짜 포함)
- Technologies: 기술 관련 정보
- mentioned_products: 언급된 제품
- mentioned_persons: 언급된 인물
- mentioned_companies: 언급된 기업

### 프롬프트 관리

- YAML 파일: `app/prompts/triplet_extractor.yaml`
- 버전 관리 및 업데이트 용이

## 📁 파일 위치

**파일**: `app/services/processing/triplet_extractor.py`

## ⚠️ 주의사항

- LLM API 비용 발생
- API 속도 제한 준수
- 배치 처리로 효율성 향상

## 📝 History

