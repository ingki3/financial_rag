# Phase 1.4: 환경 변수 설정

## 📋 Sub-task 개요

프로젝트 실행에 필요한 환경 변수를 정의하는 `.env.example` 파일을 생성하고, 실제 사용을 위한 `.env` 파일 생성 방법을 안내합니다. 환경 변수를 통해 API 키, 데이터베이스 설정 등을 관리합니다.

### 파일 경로
**파일**: `.env.example` (프로젝트 루트), `.env` (프로젝트 루트, Git 제외)

### Phase 전체 목표 기여
- 프로젝트 설정 관리
- API 키 및 민감한 정보 보호
- Phase 2-8의 각 단계에서 필요한 환경 변수 제공

### 입력 데이터
- **환경 변수 목록**: 프로젝트에서 사용하는 환경 변수 목록
- **기본값**: 각 환경 변수의 기본값

### 출력 데이터
- **.env.example 파일**: 환경 변수 템플릿 파일
- **.env 파일**: 실제 환경 변수 값이 포함된 파일 (Git 제외)

### Class 구조
**해당 없음** (설정 파일)

## 🎯 주요 기능

1. **환경 변수 템플릿 생성**
   - `.env.example` 파일 생성
   - 모든 필요한 환경 변수 정의

2. **환경 변수 파일 생성**
   - `.env` 파일 생성 (`.env.example` 복사)
   - 실제 API 키 및 설정 값 입력

3. **환경 변수 로드**
   - `python-dotenv`를 통한 환경 변수 로드
   - Python 코드에서 환경 변수 사용

## 📊 데이터 구조

### .env.example 파일 구조
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

### 환경 변수 설명
- **SEC_USER_AGENT**: SEC EDGAR API 사용 시 필수 (이름과 이메일)
- **FALKORDB_HOST**: FalkorDB 호스트 주소 (기본값: localhost)
- **FALKORDB_PORT**: FalkorDB 포트 (기본값: 6379)
- **GOOGLE_API_KEY**: Gemini API 키 (필수)
- **OPENAI_API_KEY**: OpenAI API 키 (선택)
- **ANTHROPIC_API_KEY**: Anthropic API 키 (선택)
- **GRAPHITI_MODEL**: Graphiti에서 사용할 LLM 모델

## 💻 코드 예시 및 전체 코드 구현

### .env.example 파일 생성

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
```

### .env 파일 생성

```bash
# .env 파일 생성 (실제 사용)
cp .env.example .env

# .env 파일 편집하여 실제 API 키 입력
# nano .env
# 또는
# vim .env
```

### 환경 변수 사용 (Python)

```python
from dotenv import load_dotenv
import os

# .env 파일 로드
load_dotenv()

# 환경 변수 읽기
user_agent = os.getenv("SEC_USER_AGENT")
falkordb_host = os.getenv("FALKORDB_HOST", "localhost")
falkordb_port = int(os.getenv("FALKORDB_PORT", 6379))
google_api_key = os.getenv("GOOGLE_API_KEY")

# 필수 환경 변수 확인
if not google_api_key:
    raise ValueError("GOOGLE_API_KEY is required")
```

## 🔄 상세 알고리즘/프로세스

### 환경 변수 설정 프로세스
1. **.env.example 파일 생성**
   - 프로젝트 루트에 `.env.example` 파일 생성
   - 모든 필요한 환경 변수 정의 (값은 예시로)

2. **.env 파일 생성**
   - `.env.example`을 복사하여 `.env` 파일 생성
   - 실제 API 키 및 설정 값 입력

3. **.gitignore 설정**
   - `.env` 파일을 `.gitignore`에 추가
   - `.env.example`은 Git에 커밋

4. **환경 변수 로드**
   - `python-dotenv`의 `load_dotenv()` 함수 사용
   - Python 코드에서 `os.getenv()`로 환경 변수 읽기

### 예외 처리
- 환경 변수 누락: 기본값 사용 또는 에러 발생
- API 키 누락: 필수 환경 변수 확인 후 에러 발생

## ⚙️ 설정 및 의존성

### 필요한 환경 변수
- `SEC_USER_AGENT`: SEC EDGAR API 접근을 위한 User-Agent
- `GOOGLE_API_KEY`: Gemini API 키 (필수)
- `FALKORDB_HOST`: FalkorDB 호스트 (기본값: localhost)
- `FALKORDB_PORT`: FalkorDB 포트 (기본값: 6379)

### 외부 라이브러리 의존성
- **python-dotenv**: 환경 변수 로드 (`pip install python-dotenv`)

### 설정 파일
- `.env.example`: 환경 변수 템플릿
- `.env`: 실제 환경 변수 값 (Git 제외)
- `.gitignore`: `.env` 파일 제외 설정

## 🧪 테스트 케이스

### 단위 테스트 예시
```bash
# .env.example 파일 존재 확인
test -f .env.example && echo "File exists" || echo "File not found"

# .env 파일이 .gitignore에 포함되어 있는지 확인
grep -q "^\.env$" .gitignore && echo "In .gitignore" || echo "Not in .gitignore"
```

### 통합 테스트 시나리오
- `.env` 파일 생성 후 환경 변수 로드 테스트
- 필수 환경 변수 누락 시 에러 처리 테스트
- 기본값이 있는 환경 변수 테스트

### 검증 방법
- Python 코드에서 `os.getenv()`로 환경 변수 읽기 테스트
- 필수 환경 변수 확인 로직 테스트
- 기본값 동작 확인

## ⚠️ 주의사항

- `.env` 파일은 Git에 커밋하지 않아야 합니다 (`.gitignore`에 추가)
- `.env.example`은 템플릿으로 Git에 커밋합니다
- API 키는 절대 공개 저장소에 노출되지 않도록 주의합니다
- SEC_USER_AGENT는 SEC 정책에 따라 실제 이름과 이메일을 사용해야 합니다
- 환경 변수 값에 공백이 있으면 따옴표로 감싸야 합니다

## 📝 History

