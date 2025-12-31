# Financial Knowledge Graph System

SEC 공시 자료 기반 Knowledge Graph 질의 응답 시스템

## 📌 프로젝트 개요

본 프로젝트는 주요 테크 기업들의 SEC 공시 자료(10-K, 10-Q, 8-K)를 수집하고, **Graph DB와 Vector DB로 적재**하여 사용자의 질의에 대한 심도 깊은 답변을 제공하는 시스템입니다.

**핵심 기능**:
- ✅ SEC 공시 자료 자동 다운로드 및 파싱
- ✅ LLM 기반 Knowledge Triplet 추출
- ✅ Graph DB (FalkorDB) 및 Vector DB 구축
- ✅ 자연어 질의 응답 시스템 (Graph + Vector 하이브리드 검색)
- ✅ REST API 및 Streamlit 클라이언트

## 🚀 빠른 시작

### 1. 환경 설정

```bash
# 가상환경 생성 및 활성화
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate

# 의존성 설치
pip install -r requirements.txt

# 환경 변수 설정
cp .env.example .env
# .env 파일을 열어 API 키 설정
```

### 2. FalkorDB 실행

```bash
docker run -d \
  --name falkordb \
  -p 6379:6379 \
  -p 3000:3000 \
  falkordb/falkordb:latest
```

### 3. API 서버 실행

```bash
# API 서버 시작 (포트 8001)
uvicorn app.api.main:app --host 0.0.0.0 --port 8001
```

API 문서: http://localhost:8001/docs

### 4. Streamlit 클라이언트 실행

```bash
# 새 터미널에서
streamlit run streamlit_app.py --server.port 8501
```

클라이언트: http://localhost:8501

## 📋 주요 기능

### 1. 공시 다운로드 (`/download`)

```bash
curl -X POST "http://localhost:8001/download" \
  -H "Content-Type: application/json" \
  -d '{
    "ticker": "AAPL",
    "filing_types": ["10-K", "10-Q"],
    "limits": {"10-K": 3, "10-Q": 12}
  }'
```

### 2. 문서 처리 및 Graph DB 적재 (`/process`)

```bash
curl -X POST "http://localhost:8001/process" \
  -H "Content-Type: application/json" \
  -d '{
    "ticker": "AAPL",
    "filing_types": ["10-K", "10-Q"],
    "skip_duplicates": true,
    "with_embedding": true
  }'
```

### 3. 질의 응답 (`/answer`)

```bash
curl -X POST "http://localhost:8001/answer" \
  -H "Content-Type: application/json" \
  -d '{
    "query": "애플의 기회 요소를 알려줘",
    "use_vector_search": false,
    "top_k": 5
  }' \
  --no-buffer
```

## 🏗 프로젝트 구조

```
graphiti_test/
├── app/
│   ├── api/              # FastAPI 엔드포인트
│   │   ├── routes/       # 라우터 모듈
│   │   ├── dependencies.py
│   │   └── main.py
│   ├── services/         # 비즈니스 로직 서비스
│   │   ├── query/       # 질의 응답 관련
│   │   ├── download/     # 다운로드 관련
│   │   ├── processing/   # 문서 처리 관련
│   │   ├── graph/        # Graph DB 관련
│   │   └── shared/       # 공유 유틸리티
│   ├── schemas/          # Pydantic 모델
│   ├── prompts/          # YAML 프롬프트 파일
│   └── utils/            # 유틸리티 함수
├── plan/                  # 프로젝트 계획 문서
│   ├── prd.md
│   └── plan.md
├── docs/                  # 구현 문서
├── scripts/               # 실행 스크립트
├── data/                  # 데이터 저장소
│   ├── raw/              # 원본 다운로드 파일
│   ├── parsed/           # 파싱된 섹션 데이터
│   ├── extracted/        # 추출된 엔티티 데이터
│   └── graph/            # Graph 데이터
├── streamlit_app.py       # Streamlit 클라이언트
├── requirements.txt
└── README.md
```

## 🛠 기술 스택

| 구분 | 기술 |
|------|------|
| 프로그래밍 언어 | Python 3.11+ |
| Graph DB | FalkorDB |
| Knowledge Graph | Graphiti |
| Vector DB | FalkorDB (Vector Search) |
| LLM | Gemini 3 Flash / Gemini 2.5 Flash Lite |
| Embedding | Gemini Embedding (text-embedding-004) |
| API Framework | FastAPI |
| Web Framework | Streamlit |

## 📚 문서

- **프로젝트 계획**: `plan/` 폴더
  - `prd.md`: 제품 요구사항 문서
  - `plan.md`: 구현 계획
- **구현 문서**: `docs/` 폴더
  - Phase별 구현 문서 (예: `8-1-query-system-plan.md`)

## 🎯 사용 예시

### 질의 예시

1. **기회 요소 질의**: "애플의 기회 요소를 알려줘"
2. **리스크 비교**: "테슬라와 엔비디아의 공통 리스크는?"
3. **제품 관련**: "iPhone 15와 관련된 리스크는?"
4. **전략 분석**: "구글의 AI 전략은 어떻게 되어있어?"

### API 사용 예시

#### Python 클라이언트

```python
import requests

# 질의 응답
response = requests.post(
    "http://localhost:8001/answer",
    json={
        "query": "애플의 기회 요소를 알려줘",
        "use_vector_search": False,
        "top_k": 5
    },
    stream=True
)

for chunk in response.iter_content(chunk_size=None):
    if chunk:
        print(chunk.decode('utf-8'), end='')
```

## 🔧 환경 변수

`.env` 파일에 다음 변수를 설정하세요:

```env
# Gemini API
GEMINI_API_KEY=your_gemini_api_key

# FalkorDB
FALKORDB_HOST=localhost
FALKORDB_PORT=6379
FALKORDB_GRAPH_NAME=financial_kg

# SEC EDGAR
SEC_USER_AGENT="Your Name your.email@example.com"

# 데이터 디렉토리
DATA_DIR=./data
RAW_DATA_DIR=./data/raw

# 모델 설정 (선택)
INTENT_MODEL=gemini-2.5-flash-lite
ANSWER_MODEL=gemini-3-flash-preview
TRIPLET_EXTRACTOR_MODEL=gemini-3-flash-preview
```

## 📊 Knowledge Graph Ontology

### Node 타입
- **Static**: Company, Product, Person
- **Dynamic**: Risk, Opportunity, Event, Technology, Section, Document

### Link 타입
- `HAS_RISKS`, `HAS_OPPORTUNITIES`, `HAS_EVENTS`, `HAS_TECHNOLOGIES`
- `IS_EXTRACTED_FROM`, `IS_INCLUDED`
- `MAKE`, `HAS_RELATION`, `IS_MENTIONED_IN`

상세 스키마: `docs/5-2-graph-ontology-design.md` 참조

## 🏢 대상 기업

| 회사명 | 티커 |
|--------|------|
| Apple | AAPL |
| Amazon | AMZN |
| Tesla | TSLA |
| Alphabet (Google) | GOOGL |
| Microsoft | MSFT |
| Meta Platforms | META |
| NVIDIA | NVDA |

## ⚠️ 주의사항

1. **SEC API 제한**: 초당 10건 이하 요청 유지
2. **LLM 비용**: 토큰 기반 과금 발생
3. **FalkorDB**: Docker 컨테이너 필요
4. **저장 공간**: 예상 1GB 이상

## 📝 라이선스

이 프로젝트는 MIT 라이선스를 따릅니다.

## 🤝 기여

이슈 및 풀 리퀘스트를 환영합니다!

## 📞 문의

프로젝트 관련 문의사항이 있으시면 이슈를 등록해주세요.

