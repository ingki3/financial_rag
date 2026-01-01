# Phase 1: 환경 설정

## 📋 개요

Phase 1은 프로젝트 개발 및 실행을 위한 기본 환경을 설정하는 단계입니다. Docker를 통한 FalkorDB 설치, Python 가상환경 구축, 의존성 관리, 환경 변수 설정을 포함합니다.

## 🎯 목표

- FalkorDB Docker 컨테이너 실행
- Python 가상환경 생성 및 의존성 설치
- 프로젝트 설정 파일 생성

## 📥 입력 데이터 상세

### 데이터 소스
- **없음** (초기 설정 단계)

## 📤 출력 데이터 상세

### 출력 형식
- **Docker 컨테이너**: 실행 중인 FalkorDB 컨테이너
- **파일 시스템**: 
  - `venv/`: Python 가상환경 디렉토리
  - `requirements.txt`: Python 패키지 의존성 파일
  - `.env.example`: 환경 변수 예시 파일

### 데이터 구조
- **requirements.txt**: Python 패키지 목록 (텍스트 파일)
- **.env.example**: 환경 변수 키-값 쌍 (텍스트 파일)

## 🔄 주요 작업 단계

1. **FalkorDB Docker 컨테이너 실행** (Phase 1.1)
   - Docker 이미지 다운로드
   - 컨테이너 실행 및 포트 매핑

2. **Python 가상환경 생성** (Phase 1.2)
   - 가상환경 생성
   - pip 업그레이드

3. **의존성 설치** (Phase 1.3)
   - requirements.txt 생성
   - 패키지 설치

4. **환경 변수 설정** (Phase 1.4)
   - .env.example 파일 생성
   - 환경 변수 템플릿 제공

## 📊 사용하는 데이터 구조 및 스키마

- **Docker 컨테이너**: FalkorDB 서비스
- **Python 가상환경**: Python 패키지 격리 환경
- **환경 변수**: 프로젝트 설정 값

## 🔗 Phase 간 의존성

### 이전 Phase 의존성
- **없음** (최초 Phase)

### 다음 Phase로의 데이터 전달
- **Phase 2 (SEC 공시 다운로드)**:
  - 환경 변수 설정 완료 필요
  - Python 환경 준비 완료 필요

## 🔗 관련 문서

- `phase-1-1.md`: FalkorDB 설치 및 실행 상세
- `phase-1-2.md`: Python 가상환경 및 의존성 설치 상세
- `phase-1-3.md`: requirements.txt 생성 상세
- `phase-1-4.md`: 환경 변수 설정 상세

## 📝 History

