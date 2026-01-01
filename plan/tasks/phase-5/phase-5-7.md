# Phase 5.7: 생성 스크립트

## 📋 Sub-task 개요

Static Graph 생성을 실행하는 스크립트를 구현합니다. 티커별로 Static Graph를 생성하고 JSON 파일로 저장합니다.

### 파일 경로
**파일**: `scripts/04_generate_static_graph.py`

### Phase 전체 목표 기여
- Static Graph 생성 프로세스 자동화
- 여러 티커에 대한 일괄 처리 지원
- JSON 파일로 결과 저장

### 입력 데이터
- **커맨드라인 인자**: `--ticker` 옵션으로 티커 심볼 지정
- **Extracted 데이터**: `data/extracted/{ticker}/` 폴더의 JSON 파일들

### 출력 데이터
- **Static Graph JSON 파일**: `data/graph/{TICKER}_static_graph.json`
- **콘솔 출력**: 생성 결과 요약

### Class 구조
**해당 없음** (스크립트 파일)

## 🎯 주요 기능

1. **커맨드라인 인자 파싱**
   - `--ticker` 옵션으로 티커 심볼 지정 (하나 이상 가능)
   - 기본값: `["AAPL"]`

2. **Static Graph 생성**
   - 각 티커에 대해 `generate_static_graph` 함수 호출
   - Extracted 디렉토리 확인 및 처리

3. **JSON 파일 저장**
   - 생성된 Static Graph를 JSON 파일로 저장
   - `data/graph/{TICKER}_static_graph.json` 경로에 저장

4. **결과 요약 출력**
   - 생성된 노드 및 링크 수 출력
   - 저장된 파일 경로 출력

## 📊 데이터 구조

### 입력 데이터 구조
- **커맨드라인 인자**:
  ```bash
  --ticker AAPL TSLA NVDA
  ```

### 출력 데이터 구조
- **Static Graph JSON 파일**:
  ```json
  {
    "ticker": "AAPL",
    "generated_at": "2024-01-01T00:00:00Z",
    "nodes": {
      "Company": [...],
      "Product": [...],
      "Person": [...],
      "Technology": [...]
    },
    "links": [...]
  }
  ```

## 💻 코드 예시 및 전체 코드 구현

### 스크립트 전체 구현
전체 코드는 `scripts/04_generate_static_graph.py` 파일을 참조하세요.

### 스크립트 구조
```python
#!/usr/bin/env python
"""Static Graph 생성 스크립트"""
import argparse
import json
import logging
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent))

from app.services.processing.graph_generator import generate_static_graph

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

def parse_args() -> argparse.Namespace:
    """커맨드라인 인자 파싱"""
    parser = argparse.ArgumentParser(
        description="Static Graph 생성 스크립트",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
예제:
  # 단일 티커 처리
  python scripts/04_generate_static_graph.py --ticker AAPL
  
  # 여러 티커 처리
  python scripts/04_generate_static_graph.py --ticker AAPL TSLA
        """
    )
    parser.add_argument(
        "--ticker",
        type=str,
        nargs='+',
        required=True,
        help="처리할 티커 심볼 (하나 이상 지정 가능, 예: AAPL 또는 AAPL TSLA)"
    )
    return parser.parse_args()

def main():
    """Static graph 생성 및 저장"""
    args = parse_args()
    tickers = [t.upper() for t in args.ticker]  # 대문자로 변환
    
    for ticker in tickers:
        logger.info(f"🚀 Processing {ticker}...")
        
        extracted_dir = Path(f"data/extracted/{ticker}")
        if not extracted_dir.exists():
            logger.error(f"Extracted directory not found: {extracted_dir}")
            continue
        
        # Static graph 생성
        try:
            static_graph = generate_static_graph(ticker, extracted_dir)
        except Exception as e:
            logger.error(f"Error generating static graph for {ticker}: {e}", exc_info=True)
            continue
        
        # 저장
        output_dir = Path("data/graph")
        output_dir.mkdir(parents=True, exist_ok=True)
        
        output_path = output_dir / f"{ticker}_static_graph.json"
        
        try:
            with open(output_path, 'w', encoding='utf-8') as f:
                json.dump(static_graph, f, indent=2, ensure_ascii=False)
            
            logger.info(f"✅ Saved: {output_path}")
            
            # 요약 출력
            nodes = static_graph["nodes"]
            logger.info(
                f"📊 Summary: "
                f"Company={len(nodes['Company'])}, "
                f"Products={len(nodes['Product'])}, "
                f"Persons={len(nodes['Person'])}, "
                f"Technologies={len(nodes['Technology'])}, "
                f"Links={len(static_graph['links'])}"
            )
            
        except Exception as e:
            logger.error(f"Error saving static graph for {ticker}: {e}", exc_info=True)
            continue
    
    logger.info("✅ Static graph generation completed!")

if __name__ == "__main__":
    main()
```

### 실행 방법
```bash
# 단일 티커 처리
python scripts/04_generate_static_graph.py --ticker AAPL

# 여러 티커 처리
python scripts/04_generate_static_graph.py --ticker AAPL TSLA NVDA
```

### 에러 핸들링
- Extracted 디렉토리 없음: 에러 로그 및 다음 티커로 진행
- Static Graph 생성 실패: 에러 로그 및 다음 티커로 진행
- 파일 저장 실패: 에러 로그 및 다음 티커로 진행

## 🔄 상세 알고리즘/프로세스

### 실행 프로세스
1. **커맨드라인 인자 파싱**
   - `argparse`를 사용하여 `--ticker` 옵션 파싱
   - 티커 심볼을 대문자로 변환

2. **각 티커 처리**
   - Extracted 디렉토리 존재 확인
   - `generate_static_graph` 함수 호출
   - 생성된 Static Graph를 JSON 파일로 저장
   - 결과 요약 출력

3. **완료 메시지 출력**
   - 모든 티커 처리 완료 후 메시지 출력

### 예외 처리
- Extracted 디렉토리 없음: 에러 로그 및 다음 티커로 진행
- Static Graph 생성 실패: 에러 로그 및 다음 티커로 진행
- 파일 저장 실패: 에러 로그 및 다음 티커로 진행

## ⚙️ 설정 및 의존성

### 필요한 환경 변수
- `GOOGLE_API_KEY`: Gemini API 키 (정규화 단계에서 LLM 사용 시 필요)

### 외부 라이브러리 의존성
- 없음 (표준 라이브러리만 사용)

### 설정 파일
- 없음

## 🧪 테스트 케이스

### 단위 테스트 예시
```python
def test_parse_args():
    # argparse 테스트
    # ...

def test_main():
    # 메인 함수 테스트
    # ...
```

### 통합 테스트 시나리오
- 실제 티커로 스크립트 실행 테스트
- 생성된 JSON 파일 확인
- 여러 티커 일괄 처리 테스트

### 검증 방법
- 생성된 JSON 파일 존재 확인
- JSON 파일 구조 확인
- 노드 및 링크 수 확인

## ⚠️ 주의사항

- Extracted 데이터가 있어야 Static Graph 생성 가능
- 정규화 단계에서 LLM API 비용 발생 가능
- 대량의 티커 처리 시 시간이 오래 걸릴 수 있음

## 📝 History
