# API 구현 및 리팩토링 계획

## 📋 개요

현재까지 구현된 모듈을 활용하여 다음 3개의 API를 구현하고, app 폴더 구조를 리팩토링합니다.

### 필요한 API
1. **질의 응답 API** (`/answer`) - Stream 형태로 답변 반환
2. **공시 다운로드 API** (`/download`) - ticker 입력 받아 공시 자료 다운로드 및 저장
3. **문서 처리 및 Graph DB 적재 API** (`/process`) - ticker에 대한 문서 처리 및 Graph DB 적재 (중복 방지)

---

## 📁 리팩토링된 app 폴더 구조

```
app/
├── __init__.py
├── api/                          # API 엔드포인트
│   ├── __init__.py
│   ├── routes/                   # 라우터 모듈
│   │   ├── __init__.py
│   │   ├── answer.py             # 질의 응답 API 라우터
│   │   ├── download.py            # 공시 다운로드 API 라우터
│   │   └── process.py            # 문서 처리 API 라우터
│   ├── dependencies.py            # FastAPI 의존성 (DB 연결, 서비스 인스턴스 등)
│   └── main.py                    # FastAPI 앱 진입점
│
├── services/                      # 비즈니스 로직 서비스
│   ├── __init__.py
│   ├── query/                     # 질의 응답 관련 서비스
│   │   ├── __init__.py
│   │   ├── query_engine.py        # QueryEngine (기존)
│   │   ├── intent_extractor.py    # IntentExtractor (기존)
│   │   ├── answer_generator.py    # AnswerGenerator (기존, stream 지원 추가)
│   │   ├── cypher_query_builder.py # CypherQueryBuilder (기존)
│   │   └── vector_search.py       # VectorSearch (기존)
│   │
│   ├── download/                  # 다운로드 관련 서비스
│   │   ├── __init__.py
│   │   └── sec_downloader.py      # SECFilingDownloader (기존)
│   │
│   ├── processing/                # 문서 처리 관련 서비스
│   │   ├── __init__.py
│   │   ├── filing_parser.py       # FilingParser (기존)
│   │   ├── triplet_extractor.py   # TripletExtractor (기존)
│   │   ├── graph_generator.py      # Static/Dynamic Graph 생성 (기존)
│   │   ├── document_processor.py  # 문서 처리 오케스트레이터 (신규)
│   │   └── duplicate_checker.py   # 중복 체크 서비스 (신규)
│   │
│   ├── graph/                     # Graph DB 관련 서비스
│   │   ├── __init__.py
│   │   ├── graph_loader.py        # GraphLoader (기존)
│   │   ├── graphiti_manager.py    # GraphitiManager (기존)
│   │   └── falkor_driver_ext.py   # FalkorDriver 확장 (기존)
│   │
│   └── shared/                    # 공통 서비스
│       ├── __init__.py
│       ├── embedding_generator.py  # EmbeddingGenerator (기존)
│       ├── name_normalizer.py     # NameNormalizer (기존)
│       └── gemini_client_strict.py # GeminiClient 확장 (기존)
│
├── schemas/                       # Pydantic 모델 및 TypedDict
│   ├── __init__.py
│   ├── schemas.py                 # 기존 스키마 (Intent, State 등)
│   └── api_schemas.py             # API 요청/응답 스키마 (신규)
│
├── graph/                         # LangGraph 정의 (기존)
│   ├── __init__.py
│   └── ...
│
├── prompts/                       # 프롬프트 템플릿 (기존)
│   ├── __init__.py
│   └── ...
│
└── utils/                         # 유틸리티 함수 (기존)
    ├── __init__.py
    └── prompt_loader.py
```

---

## 🔧 각 모듈의 역할 및 구현 계획

### 1. API 레이어 (`app/api/`)

#### 1.1 `app/api/main.py`
**역할**: FastAPI 앱 진입점 및 전역 설정

**주요 내용**:
- FastAPI 앱 인스턴스 생성
- CORS 설정
- 라우터 등록
- 미들웨어 설정 (로깅, 에러 핸들링)
- 헬스체크 엔드포인트

**의존성**:
- `app.api.dependencies` - 의존성 주입
- `app.api.routes.*` - 라우터 모듈

---

#### 1.2 `app/api/dependencies.py`
**역할**: FastAPI 의존성 주입 (DB 연결, 서비스 인스턴스)

**주요 함수**:
```python
def get_query_engine() -> QueryEngine:
    """QueryEngine 싱글톤 인스턴스 반환"""
    
def get_graph_loader() -> GraphLoader:
    """GraphLoader 싱글톤 인스턴스 반환"""
    
def get_downloader() -> SECFilingDownloader:
    """SECFilingDownloader 인스턴스 반환"""
    
def get_document_processor() -> DocumentProcessor:
    """DocumentProcessor 인스턴스 반환"""
```

**설정 관리**:
- 환경변수에서 DB 연결 정보 로드
- 서비스 인스턴스 라이프사이클 관리

---

#### 1.3 `app/api/routes/answer.py`
**역할**: 질의 응답 API 라우터

**엔드포인트**:
- `POST /answer` - 질의에 대한 답변 생성 (Stream)

**요청 스키마** (`AnswerRequest`):
```python
class AnswerRequest(BaseModel):
    query: str
    use_vector_search: bool = False  # 기본값 False
    top_k: int = 10
```

**응답**: Server-Sent Events (SSE) 스트림
- `text/event-stream` Content-Type
- 청크 단위로 답변 스트리밍

**구현 방식**:
- `AnswerGenerator.generate_answer_stream()` 호출
- `yield`를 사용한 스트리밍 응답

**의존성**:
- `app.services.query.query_engine.QueryEngine`
- `app.services.query.answer_generator.AnswerGenerator` (stream 메서드 추가 필요)

---

#### 1.4 `app/api/routes/download.py`
**역할**: 공시 다운로드 API 라우터

**엔드포인트**:
- `POST /download` - ticker에 대한 공시 자료 다운로드

**요청 스키마** (`DownloadRequest`):
```python
class DownloadRequest(BaseModel):
    ticker: str
    filing_types: Optional[List[str]] = None  # None이면 모든 유형
    limits: Optional[Dict[str, int]] = None    # 유형별 다운로드 제한
```

**응답 스키마** (`DownloadResponse`):
```python
class DownloadResponse(BaseModel):
    ticker: str
    results: Dict[str, int]  # {filing_type: count}
    total_files: int
    message: str
```

**구현 방식**:
- `SECFilingDownloader.download_all_filings(ticker)` 호출
- 비동기 처리 (백그라운드 작업으로 실행 가능)

**의존성**:
- `app.services.download.sec_downloader.SECFilingDownloader`

---

#### 1.5 `app/api/routes/process.py`
**역할**: 문서 처리 및 Graph DB 적재 API 라우터

**엔드포인트**:
- `POST /process` - ticker에 대한 문서 처리 및 Graph DB 적재

**요청 스키마** (`ProcessRequest`):
```python
class ProcessRequest(BaseModel):
    ticker: str
    skip_duplicates: bool = True  # 중복 문서 건너뛰기
    with_embedding: bool = True    # Embedding 생성 여부
    filing_types: Optional[List[str]] = None  # 처리할 공시 유형
```

**응답 스키마** (`ProcessResponse`):
```python
class ProcessResponse(BaseModel):
    ticker: str
    processed_files: int
    skipped_files: int
    graph_stats: Dict  # 노드/링크 통계
    message: str
```

**구현 방식**:
- `DocumentProcessor.process_ticker()` 호출
- 중복 체크: `DuplicateChecker.check_documents()` 사용
- 처리 파이프라인: 파싱 → 추출 → 그래프 생성 → DB 적재

**의존성**:
- `app.services.processing.document_processor.DocumentProcessor`
- `app.services.processing.duplicate_checker.DuplicateChecker`
- `app.services.graph.graph_loader.GraphLoader`

---

### 2. 서비스 레이어 (`app/services/`)

#### 2.1 `app/services/query/answer_generator.py` (수정)
**기존**: `app/services/answer_generator.py`

**추가 기능**:
- `generate_answer_stream()` 메서드 추가
  - Gemini API의 streaming 기능 활용
  - `yield`를 사용한 청크 단위 반환

**수정 사항**:
```python
def generate_answer_stream(
    self,
    query: str,
    results: List[Dict],
    intent: Dict,
    max_results: int = 5
) -> Generator[str, None, None]:
    """스트리밍 답변 생성"""
    # Gemini streaming API 사용
    # yield로 청크 단위 반환
```

---

#### 2.2 `app/services/processing/document_processor.py` (신규)
**역할**: 문서 처리 파이프라인 오케스트레이터

**주요 메서드**:
```python
class DocumentProcessor:
    def __init__(
        self,
        parser: FilingParser,
        extractor: TripletExtractor,
        graph_generator: GraphGenerator,
        graph_loader: GraphLoader,
        duplicate_checker: DuplicateChecker
    ):
        """의존성 주입"""
    
    def process_ticker(
        self,
        ticker: str,
        skip_duplicates: bool = True,
        with_embedding: bool = True,
        filing_types: Optional[List[str]] = None
    ) -> Dict:
        """
        티커의 모든 문서 처리 및 Graph DB 적재
        
        프로세스:
        1. 다운로드된 파일 목록 조회
        2. 중복 체크 (skip_duplicates=True인 경우)
        3. 각 파일에 대해:
           - 파싱 (FilingParser)
           - 트리플렛 추출 (TripletExtractor)
           - Static/Dynamic Graph 생성 (GraphGenerator)
           - Graph DB 적재 (GraphLoader)
        4. 통계 반환
        """
    
    def process_single_file(
        self,
        file_path: Path,
        ticker: str,
        with_embedding: bool = True
    ) -> Dict:
        """단일 파일 처리"""
```

**의존성**:
- `app.services.processing.filing_parser.FilingParser`
- `app.services.processing.triplet_extractor.TripletExtractor`
- `app.services.processing.graph_generator.*` (Static/Dynamic Graph 생성)
- `app.services.processing.duplicate_checker.DuplicateChecker`
- `app.services.graph.graph_loader.GraphLoader`

---

#### 2.3 `app/services/processing/duplicate_checker.py` (신규)
**역할**: Graph DB에 이미 적재된 문서인지 확인

**주요 메서드**:
```python
class DuplicateChecker:
    def __init__(self, graph_loader: GraphLoader):
        """GraphLoader 주입"""
    
    def check_document(
        self,
        ticker: str,
        filing_type: str,
        accession_number: str
    ) -> bool:
        """
        문서가 이미 Graph DB에 적재되었는지 확인
        
        Document 노드의 id는 다음과 같은 형식:
        f"{ticker}_{filing_type}_{accession_number}"
        
        Cypher 쿼리:
        MATCH (d:Document {id: $doc_id})
        RETURN d LIMIT 1
        """
    
    def check_documents(
        self,
        ticker: str,
        filing_dirs: List[Path]
    ) -> Dict[Path, bool]:
        """
        여러 문서의 중복 여부 일괄 확인
        
        Returns:
            {file_path: is_duplicate}
        """
    
    def get_processed_documents(
        self,
        ticker: str
    ) -> Set[str]:
        """
        티커에 대해 이미 처리된 문서 ID 목록 반환
        
        Cypher 쿼리:
        MATCH (d:Document)
        WHERE d.ticker = $ticker
        RETURN d.id
        """
```

**의존성**:
- `app.services.graph.graph_loader.GraphLoader`

---

### 3. 스키마 레이어 (`app/schemas/`)

#### 3.1 `app/schemas/api_schemas.py` (신규)
**역할**: API 요청/응답 스키마 정의

**주요 스키마**:
```python
# Answer API
class AnswerRequest(BaseModel):
    query: str
    use_vector_search: bool = False
    top_k: int = 10

class AnswerStreamChunk(BaseModel):
    chunk: str
    done: bool = False

# Download API
class DownloadRequest(BaseModel):
    ticker: str
    filing_types: Optional[List[str]] = None
    limits: Optional[Dict[str, int]] = None

class DownloadResponse(BaseModel):
    ticker: str
    results: Dict[str, int]
    total_files: int
    message: str

# Process API
class ProcessRequest(BaseModel):
    ticker: str
    skip_duplicates: bool = True
    with_embedding: bool = True
    filing_types: Optional[List[str]] = None

class ProcessResponse(BaseModel):
    ticker: str
    processed_files: int
    skipped_files: int
    graph_stats: Dict
    message: str
```

---

## 🔄 기존 모듈 적용 계획

### 기존 모듈 → 새 위치 매핑

| 기존 경로 | 새 경로 | 변경 사항 |
|----------|---------|----------|
| `app/services/query_engine.py` | `app/services/query/query_engine.py` | 이동 |
| `app/services/intent_extractor.py` | `app/services/query/intent_extractor.py` | 이동 |
| `app/services/answer_generator.py` | `app/services/query/answer_generator.py` | 이동 + stream 메서드 추가 |
| `app/services/cypher_query_builder.py` | `app/services/query/cypher_query_builder.py` | 이동 |
| `app/services/vector_search.py` | `app/services/query/vector_search.py` | 이동 |
| `app/services/sec_downloader.py` | `app/services/download/sec_downloader.py` | 이동 |
| `app/services/filing_parser.py` | `app/services/processing/filing_parser.py` | 이동 |
| `app/services/triplet_extractor.py` | `app/services/processing/triplet_extractor.py` | 이동 |
| `app/services/graph_generator.py` | `app/services/processing/graph_generator.py` | 이동 (또는 분리) |
| `app/services/dynamic_graph_generator.py` | `app/services/processing/dynamic_graph_generator.py` | 이동 |
| `app/services/graph_loader.py` | `app/services/graph/graph_loader.py` | 이동 |
| `app/services/graphiti_manager.py` | `app/services/graph/graphiti_manager.py` | 이동 |
| `app/services/falkor_driver_ext.py` | `app/services/graph/falkor_driver_ext.py` | 이동 |
| `app/services/embedding_generator.py` | `app/services/shared/embedding_generator.py` | 이동 |
| `app/services/name_normalizer.py` | `app/services/shared/name_normalizer.py` | 이동 |
| `app/services/gemini_client_strict.py` | `app/services/shared/gemini_client_strict.py` | 이동 |

### Import 경로 수정

모든 기존 스크립트와 모듈에서 import 경로를 업데이트해야 합니다:
- `from app.services.query_engine import QueryEngine` → `from app.services.query.query_engine import QueryEngine`
- 기타 모든 import 경로도 동일하게 수정

---

## 🚀 구현 단계

### Phase 1: 폴더 구조 생성 및 모듈 이동
1. 새 폴더 구조 생성
2. 기존 파일들을 새 위치로 이동
3. `__init__.py` 파일 생성
4. Import 경로 수정 (전체 프로젝트)

### Phase 2: 신규 서비스 구현
1. `DuplicateChecker` 구현
2. `DocumentProcessor` 구현
3. `AnswerGenerator.generate_answer_stream()` 구현

### Phase 3: API 레이어 구현
1. `app/api/main.py` 구현
2. `app/api/dependencies.py` 구현
3. `app/api/routes/answer.py` 구현
4. `app/api/routes/download.py` 구현
5. `app/api/routes/process.py` 구현

### Phase 4: 스키마 정의
1. `app/schemas/api_schemas.py` 구현

### Phase 5: 테스트 및 검증
1. 각 API 엔드포인트 단위 테스트
2. 통합 테스트
3. 기존 스크립트 동작 확인

---

## 📝 중복 방지 전략

### Document ID 형식
```
{ticker}_{filing_type}_{accession_number}
```
예: `AAPL_10-K_0000320193-24-000123`

### 중복 체크 방법
1. **Graph DB 쿼리**:
   ```cypher
   MATCH (d:Document {id: $doc_id})
   RETURN d LIMIT 1
   ```
   - 결과가 있으면 중복

2. **일괄 체크 최적화**:
   - 티커별로 이미 처리된 문서 ID 목록을 한 번에 조회
   - 메모리에서 Set으로 관리하여 빠른 체크

3. **처리 전 체크**:
   - `DocumentProcessor.process_ticker()`에서 `skip_duplicates=True`인 경우
   - 모든 파일에 대해 사전 중복 체크 수행
   - 중복 파일은 건너뛰기

---

## 🔍 추가 고려사항

### 1. 에러 핸들링
- 각 API에서 적절한 HTTP 상태 코드 반환
- 에러 메시지 구조화
- 로깅 강화

### 2. 비동기 처리
- `/download`와 `/process` API는 시간이 오래 걸릴 수 있음
- 백그라운드 작업으로 처리하고 작업 ID 반환
- 작업 상태 조회 API 추가 고려

### 3. 인증/인가
- 현재는 구현하지 않지만, 향후 확장 가능하도록 구조 설계

### 4. 문서화
- FastAPI 자동 문서화 (`/docs`, `/redoc`) 활용
- 각 엔드포인트에 docstring 추가

---

## ✅ 체크리스트

### Phase 1: 구조 리팩토링
- [ ] 새 폴더 구조 생성
- [ ] 기존 파일 이동
- [ ] Import 경로 수정
- [ ] 기존 스크립트 동작 확인

### Phase 2: 신규 서비스
- [ ] `DuplicateChecker` 구현
- [ ] `DocumentProcessor` 구현
- [ ] `AnswerGenerator.generate_answer_stream()` 구현

### Phase 3: API 구현
- [ ] `main.py` 구현
- [ ] `dependencies.py` 구현
- [ ] `answer.py` 구현
- [ ] `download.py` 구현
- [ ] `process.py` 구현

### Phase 4: 스키마
- [ ] `api_schemas.py` 구현

### Phase 5: 테스트
- [ ] 단위 테스트
- [ ] 통합 테스트
- [ ] API 문서 확인

