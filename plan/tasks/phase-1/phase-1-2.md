# Phase 1.2: Python 가상환경 및 의존성 설치

## 📋 Sub-task 개요

Python 가상환경을 생성하고 프로젝트에 필요한 의존성을 설치합니다. 가상환경을 통해 프로젝트별 패키지 격리를 제공합니다.

### 파일 경로
**해당 없음** (명령어 실행)

### Phase 전체 목표 기여
- 프로젝트 개발을 위한 Python 환경 구축
- Phase 1.3의 requirements.txt 파일을 통한 의존성 관리 준비

### 입력 데이터
- **Python**: Python 3.11 이상 설치 필요
- **pip**: Python 패키지 관리자

### 출력 데이터
- **가상환경 디렉토리**: `venv/` 폴더
- **설치된 패키지**: requirements.txt에 정의된 패키지들

### Class 구조
**해당 없음** (명령어 실행)

## 🎯 주요 기능

1. **가상환경 생성**
   - `python -m venv venv` 명령어로 가상환경 생성
   - 프로젝트별 패키지 격리

2. **가상환경 활성화**
   - Linux/Mac: `source venv/bin/activate`
   - Windows: `venv\Scripts\activate`

3. **의존성 설치**
   - `pip install -r requirements.txt`로 일괄 설치
   - 또는 개별 패키지 설치

## 📊 데이터 구조

### 가상환경 구조
```
venv/
  bin/          # 실행 파일 (Linux/Mac)
  Scripts/      # 실행 파일 (Windows)
  lib/          # 설치된 패키지
  include/      # 헤더 파일
  pyvenv.cfg    # 가상환경 설정
```

### 의존성 패키지 목록
- `graphiti-core[falkordb]`: Graphiti와 FalkorDB 통합
- `sec-edgar-downloader`: SEC EDGAR 공시 다운로드
- `beautifulsoup4`: HTML 파싱
- `lxml`: XML/HTML 파서
- `python-dotenv`: 환경 변수 관리
- `tqdm`: 진행 표시줄
- `aiohttp`: 비동기 HTTP 클라이언트
- `pytest`: 테스트 프레임워크
- `pytest-asyncio`: 비동기 테스트 지원

## 💻 코드 예시 및 전체 코드 구현

### 가상환경 생성

```bash
# 가상환경 생성
python -m venv venv

# 가상환경 활성화 (Linux/Mac)
source venv/bin/activate

# 가상환경 활성화 (Windows)
venv\Scripts\activate
```

### 의존성 설치

```bash
# requirements.txt가 있는 경우
pip install -r requirements.txt

# 또는 개별 설치
pip install graphiti-core[falkordb]
pip install sec-edgar-downloader
pip install beautifulsoup4
pip install lxml
pip install python-dotenv
pip install tqdm
pip install aiohttp
pip install pytest
pip install pytest-asyncio
```

### 가상환경 비활성화

```bash
deactivate
```

### pip 업그레이드

```bash
# pip 업그레이드
pip install --upgrade pip
```

## 🔄 상세 알고리즘/프로세스

### 가상환경 생성 프로세스
1. **Python 버전 확인**
   - `python --version`으로 Python 3.11 이상 확인

2. **가상환경 생성**
   - `python -m venv venv` 명령어 실행
   - `venv/` 폴더 생성 확인

3. **가상환경 활성화**
   - 터미널 프롬프트에 `(venv)` 표시 확인

4. **pip 업그레이드**
   - `pip install --upgrade pip` 실행

5. **의존성 설치**
   - `pip install -r requirements.txt` 실행
   - 또는 개별 패키지 설치

### 예외 처리
- Python 버전 부족: Python 3.11 이상 설치 필요
- 가상환경 생성 실패: 디스크 공간 및 권한 확인
- 패키지 설치 실패: 네트워크 연결 및 pip 업그레이드 확인

## ⚙️ 설정 및 의존성

### 필요한 환경 변수
- 없음

### 외부 라이브러리 의존성
- **Python**: Python 3.11 이상
- **pip**: Python 패키지 관리자

### 설정 파일
- `requirements.txt`: 패키지 의존성 목록 (Phase 1.3에서 생성)

## 🧪 테스트 케이스

### 단위 테스트 예시
```bash
# 가상환경 활성화 확인
which python  # Linux/Mac
where python  # Windows

# Python 버전 확인
python --version

# 설치된 패키지 확인
pip list

# 특정 패키지 확인
pip show graphiti-core
```

### 통합 테스트 시나리오
- 가상환경 생성 후 패키지 설치 확인
- 가상환경 비활성화 후 재활성화 테스트
- requirements.txt로 의존성 재설치 테스트

### 검증 방법
- `pip list`로 설치된 패키지 확인
- `python -c "import graphiti_core"`로 패키지 import 테스트
- `python -c "import sec_edgar_downloader"`로 패키지 import 테스트

## ⚠️ 주의사항

- Python 3.11 이상이 필요합니다
- 가상환경을 활성화한 상태에서 작업해야 합니다
- `requirements.txt`는 Phase 1.3에서 생성됩니다
- 가상환경을 Git에 커밋하지 않아야 합니다 (`.gitignore`에 추가)

## 📝 History

