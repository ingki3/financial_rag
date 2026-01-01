# Phase 3: 공시 파싱 및 텍스트 추출

## 📋 개요

Phase 3는 다운로드된 HTML/SGML 형식의 공시 파일에서 주요 섹션을 추출하고 텍스트로 변환하는 단계입니다.

## 🎯 목표

- HTML/SGML 파일 파싱
- 공시 유형별 주요 섹션 추출
- 텍스트 변환 및 JSON 형식으로 저장

## 📥 입력

- `data/raw/{ticker}/{filing_type}/` 폴더의 HTML/SGML 파일

## 📤 출력

- `data/parsed/{ticker}/{filing_type}/` 폴더의 JSON 파일
- 각 JSON 파일: `metadata`, `sections` 포함

## 🔗 관련 문서

- `phase-3-1.md`: 파서 모듈 구현 상세
- `phase-3-2.md`: 파싱 스크립트 상세

## 📝 History

