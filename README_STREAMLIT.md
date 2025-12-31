# Streamlit API 클라이언트

Financial Knowledge Graph API를 테스트할 수 있는 웹 인터페이스입니다.

## 실행 방법

### 1. API 서버 실행

```bash
cd /home/ingki3/Dev/graphiti_test
source venv/bin/activate
uvicorn app.api.main:app --host 0.0.0.0 --port 8001
```

### 2. Streamlit 앱 실행

다른 터미널에서:

```bash
cd /home/ingki3/Dev/graphiti_test
source venv/bin/activate
streamlit run streamlit_app.py
```

브라우저에서 `http://localhost:8501`로 접속하면 됩니다.

## 기능

### 1. 질의 응답 API 테스트
- 사용자 질의 입력
- Vector 검색 옵션 설정
- 스트리밍 답변 실시간 표시

### 2. 공시 다운로드 API 테스트
- 티커 심볼 입력
- 공시 유형 선택 (10-K, 10-Q, 8-K)
- 다운로드 제한 설정
- 다운로드 결과 표시

### 3. 문서 처리 API 테스트
- 티커 심볼 입력
- 공시 유형 선택
- 중복 건너뛰기 옵션
- Embedding 생성 옵션
- 처리 결과 및 Graph DB 통계 표시

## 설정

- API 서버 URL은 사이드바에서 변경할 수 있습니다.
- 기본값: `http://localhost:8001`


