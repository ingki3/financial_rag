# Phase 4: Knowledge Triplet 추출

## 📋 개요

Phase 4는 LLM을 활용하여 파싱된 텍스트에서 Knowledge Triplet을 추출하는 단계입니다.

## 🎯 목표

- 기회 요소 (Opportunities) 추출
- 리스크 요소 (Risks) 추출
- 주요 이벤트 (Key Events) 추출
- 전략 (Strategies) 추출
- 재무 지표 (Financial Metrics) 추출
- 제품/인물/기업 언급 추출

## 📥 입력

- `data/parsed/{ticker}/{filing_type}/` 폴더의 JSON 파일

## 📤 출력

- `data/extracted/{ticker}/{filing_type}/` 폴더의 JSON 파일
- 각 JSON 파일: 추출된 triplets 및 메타데이터

## 🔗 관련 문서

- `phase-4-1.md`: 추출기 모듈 구현 상세
- `phase-4-2.md`: 추출 스크립트 상세

## 📝 History

