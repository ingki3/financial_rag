# Phase 1.2: Python 가상환경 및 의존성 설치

## 📋 개요

Python 가상환경을 생성하고 프로젝트에 필요한 의존성을 설치합니다.

## 🎯 목표

- Python 가상환경 생성
- 가상환경 활성화
- 의존성 설치

## 📝 상세 구현

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

## ⚠️ 주의사항

- Python 3.11 이상이 필요합니다
- 가상환경을 활성화한 상태에서 작업해야 합니다
- `requirements.txt`는 Phase 1.3에서 생성됩니다

## 📝 History

