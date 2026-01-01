# Phase 2: SEC 공시 다운로드

## 📋 개요

Phase 2는 SEC EDGAR API를 통해 7개 테크 기업의 공시 자료(10-K, 10-Q, 8-K)를 다운로드하는 단계입니다.

## 🎯 목표

- 7개 기업의 최근 3년간 공시 자료 다운로드
- 10-K (연간 보고서): 최근 3년
- 10-Q (분기 보고서): 최근 12분기 (3년)
- 8-K (수시 공시): 최근 20건
- 체계적인 폴더 구조로 저장

## 📥 입력

- SEC EDGAR API 접근
- 환경 변수: `SEC_USER_AGENT`

## 📤 출력

- `data/raw/{ticker}/{filing_type}/` 폴더 구조
- 다운로드된 HTML/SGML 파일

## 🔗 관련 문서

- `phase-2-1.md`: 다운로더 모듈 구현 상세
- `phase-2-2.md`: 다운로드 스크립트 상세

## 📝 History

