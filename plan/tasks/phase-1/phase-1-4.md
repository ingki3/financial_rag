# Phase 1.4: 환경 변수 설정

## 📋 개요

프로젝트 실행에 필요한 환경 변수를 정의하는 `.env.example` 파일을 생성하고, 실제 사용을 위한 `.env` 파일 생성 방법을 안내합니다.

## 🎯 목표

- `.env.example` 파일 생성
- 필요한 환경 변수 정의
- `.env` 파일 생성 방법 안내

## 📝 상세 구현

### .env.example 파일 내용

```env
# SEC EDGAR API
SEC_USER_AGENT="Your Name your.email@example.com"

# FalkorDB
FALKORDB_HOST=localhost
FALKORDB_PORT=6379

# LLM (Gemini)
GOOGLE_API_KEY=your_google_api_key_here

# LLM (선택 - OpenAI 또는 Anthropic)
OPENAI_API_KEY=sk-...
ANTHROPIC_API_KEY=sk-ant-...

# Graphiti
GRAPHITI_MODEL=gpt-4o-mini
```

### 파일 생성

```bash
# .env.example 파일 생성
cat > .env.example << EOF
# SEC EDGAR API
SEC_USER_AGENT="Your Name your.email@example.com"

# FalkorDB
FALKORDB_HOST=localhost
FALKORDB_PORT=6379

# LLM (Gemini)
GOOGLE_API_KEY=your_google_api_key_here

# LLM (선택 - OpenAI 또는 Anthropic)
OPENAI_API_KEY=sk-...
ANTHROPIC_API_KEY=sk-ant-...

# Graphiti
GRAPHITI_MODEL=gpt-4o-mini
EOF

# .env 파일 생성 (실제 사용)
cp .env.example .env
# .env 파일을 편집하여 실제 API 키 입력
```

### 환경 변수 사용

Python 코드에서 환경 변수 사용:

```python
from dotenv import load_dotenv
import os

load_dotenv()

user_agent = os.getenv("SEC_USER_AGENT")
falkordb_host = os.getenv("FALKORDB_HOST", "localhost")
falkordb_port = int(os.getenv("FALKORDB_PORT", 6379))
google_api_key = os.getenv("GOOGLE_API_KEY")
```

## 🔑 환경 변수 설명

- **SEC_USER_AGENT**: SEC EDGAR API 사용 시 필수 (이름과 이메일)
- **FALKORDB_HOST**: FalkorDB 호스트 주소 (기본값: localhost)
- **FALKORDB_PORT**: FalkorDB 포트 (기본값: 6379)
- **GOOGLE_API_KEY**: Gemini API 키 (필수)
- **OPENAI_API_KEY**: OpenAI API 키 (선택)
- **ANTHROPIC_API_KEY**: Anthropic API 키 (선택)
- **GRAPHITI_MODEL**: Graphiti에서 사용할 LLM 모델

## ⚠️ 주의사항

- `.env` 파일은 Git에 커밋하지 않아야 합니다 (`.gitignore`에 추가)
- `.env.example`은 템플릿으로 Git에 커밋합니다
- API 키는 절대 공개 저장소에 노출되지 않도록 주의합니다
- SEC_USER_AGENT는 SEC 정책에 따라 실제 이름과 이메일을 사용해야 합니다

## 📝 History

