# Phase 1.3: requirements.txt 생성

## 📋 개요

프로젝트에 필요한 Python 패키지 의존성을 정의하는 `requirements.txt` 파일을 생성합니다.

## 🎯 목표

- 프로젝트 의존성 목록 정의
- 버전 명시
- `requirements.txt` 파일 생성

## 📝 상세 구현

### requirements.txt 내용

```txt
# Core Dependencies
graphiti-core[falkordb]>=0.5.0
sec-edgar-downloader>=5.0.0
beautifulsoup4>=4.12.0
lxml>=5.0.0

# LLM
openai>=1.0.0
anthropic>=0.20.0
google-genai>=0.3.0

# Utilities
python-dotenv>=1.0.0
tqdm>=4.66.0
aiohttp>=3.9.0

# Development
pytest>=8.0.0
pytest-asyncio>=0.23.0
```

### 파일 생성

```bash
# requirements.txt 파일 생성
cat > requirements.txt << EOF
# Core Dependencies
graphiti-core[falkordb]>=0.5.0
sec-edgar-downloader>=5.0.0
beautifulsoup4>=4.12.0
lxml>=5.0.0

# LLM
openai>=1.0.0
anthropic>=0.20.0
google-genai>=0.3.0

# Utilities
python-dotenv>=1.0.0
tqdm>=4.66.0
aiohttp>=3.9.0

# Development
pytest>=8.0.0
pytest-asyncio>=0.23.0
EOF
```

### 의존성 설치 확인

```bash
# requirements.txt로 설치
pip install -r requirements.txt

# 설치된 패키지 확인
pip list
```

## 📦 주요 패키지 설명

- **graphiti-core[falkordb]**: Graphiti와 FalkorDB 통합
- **sec-edgar-downloader**: SEC EDGAR 공시 다운로드
- **beautifulsoup4**: HTML 파싱
- **lxml**: XML/HTML 파서
- **google-genai**: Gemini LLM API
- **python-dotenv**: 환경 변수 관리
- **pytest**: 테스트 프레임워크

## ⚠️ 주의사항

- 버전은 최소 버전을 명시합니다 (>=)
- 새로운 패키지 추가 시 이 파일을 업데이트해야 합니다
- `google-genai`는 Gemini API 사용을 위해 필요합니다

## 📝 History

