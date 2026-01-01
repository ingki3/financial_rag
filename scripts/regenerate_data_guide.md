# Data 폴더 재생성 가이드

## 현재 상황
- data 폴더가 비어있음
- 데이터를 다시 생성해야 함

## 데이터 생성 프로세스

### 1. 환경 설정 확인
```bash
# 가상환경 확인
ls -la venv/

# 의존성 확인
pip list | grep sec-edgar
```

### 2. Phase 2: SEC 공시 다운로드
```bash
# 가상환경 활성화
source venv/bin/activate

# SEC 공시 다운로드 (30분 ~ 1시간 소요)
python scripts/01_download_filings.py
```
**저장 위치**: `./data/raw/{ticker}/{filing_type}/`

### 3. Phase 3: 공시 파싱
```bash
python scripts/02_parse_filings.py
```
**저장 위치**: `./data/parsed/{ticker}/{filing_type}/`

### 4. Phase 4: 트리플렛 추출
```bash
python scripts/03_extract_triplets.py
```
**저장 위치**: `./data/extracted/{ticker}/{filing_type}/`
**주의**: LLM API 사용으로 시간과 비용 소요

### 5. Phase 5: Static Graph 생성
```bash
python scripts/04_generate_static_graph.py
```
**저장 위치**: `./data/graph/{TICKER}_static_graph.json`

### 6. Phase 6: Dynamic Graph 생성
```bash
python scripts/06_generate_dynamic_graph.py
```
**저장 위치**: `./data/graph/{TICKER}_dynamic_graph.json`

## 빠른 시작 (전체 자동화)
```bash
# 전체 프로세스 자동 실행
./scripts/00_regenerate_all_data.sh
```

## 필요한 환경 변수
`.env` 파일에 다음이 설정되어 있어야 합니다:
- `SEC_USER_AGENT`: SEC EDGAR API용 User-Agent
- `GEMINI_API_KEY`: Gemini API 키 (트리플렛 추출용)

## 예상 소요 시간
- Phase 2 (다운로드): 30분 ~ 1시간
- Phase 3 (파싱): 10분 ~ 30분
- Phase 4 (추출): 1시간 ~ 3시간 (LLM API 사용)
- Phase 5 (Static Graph): 5분 ~ 10분
- Phase 6 (Dynamic Graph): 10분 ~ 30분

**총 예상 시간**: 2시간 ~ 5시간

