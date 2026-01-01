# Phase 7.3: 저장 스크립트

## 📋 Sub-task 개요

Graph DB 저장을 실행하는 스크립트를 구현합니다. Static/Dynamic Graph JSON 파일을 로드하고, FalkorDB에 적재하며, 검증 옵션을 지원합니다.

### 파일 경로
**파일**: `scripts/06_load_graph_to_db.py`

### Phase 전체 목표 기여
- Graph DB 저장 프로세스 자동화
- 여러 티커에 대한 일괄 처리 지원
- 검증 옵션 제공

### 입력 데이터
- **커맨드라인 인자**: `--ticker` 옵션으로 티커 심볼 지정, `--verify` 옵션
- **Static Graph JSON 파일**: `data/graph/{TICKER}_static_graph.json`
- **Dynamic Graph JSON 파일**: `data/graph/{TICKER}_dynamic_graph.json`
- **환경 변수**: `FALKORDB_HOST`, `FALKORDB_PORT`

### 출력 데이터
- **FalkorDB에 저장된 노드 및 링크**
- **콘솔 출력**: 적재 통계 및 검증 결과

### Class 구조
**해당 없음** (스크립트 파일)

## 🎯 주요 기능

1. **커맨드라인 인자 파싱**
   - `--ticker` 옵션으로 티커 심볼 지정 (하나 이상 가능)
   - `--verify` 옵션으로 검증 수행 여부 지정

2. **GraphLoader 초기화**
   - FalkorDB 연결
   - 인덱스 생성

3. **Graph 파일 로드**
   - Static Graph JSON 파일 로드
   - Dynamic Graph JSON 파일 로드

4. **Graph DB 적재**
   - Static Graph 적재
   - Dynamic Graph 적재

5. **검증 수행**
   - `--verify` 옵션이 있으면 검증 수행
   - 노드/링크 수 통계 출력

## 📊 데이터 구조

### 입력 데이터 구조
- **커맨드라인 인자**:
  ```bash
  --ticker AAPL TSLA NVDA
  --verify  # 선택적
  ```

### 출력 데이터 구조
- **적재 통계**:
  ```python
  {
      "nodes_created": int,
      "links_created": int,
      "errors": int,
      "embeddings_stored": int
  }
  ```

- **검증 결과** (--verify 옵션 사용 시):
  ```python
  {
      "nodes": Dict[str, int],  # 노드 타입별 개수
      "links": Dict[str, int],  # 링크 타입별 개수
      "embeddings": Dict[str, int],  # Embedding이 있는 노드 타입별 개수
      "total_nodes": int,
      "total_links": int,
      "total_embeddings": int
  }
  ```

## 💻 코드 예시 및 전체 코드 구현

### 스크립트 구조
```python
#!/usr/bin/env python
"""Graph DB 저장 스크립트"""
import argparse
import json
import logging
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent))

from app.services.graph.graph_loader import GraphLoader

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

def parse_args() -> argparse.Namespace:
    """커맨드라인 인자 파싱"""
    parser = argparse.ArgumentParser(
        description="Graph DB 저장 스크립트",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
예제:
  # 단일 티커 저장
  python scripts/06_load_graph_to_db.py --ticker AAPL
  
  # 검증 포함 저장
  python scripts/06_load_graph_to_db.py --ticker AAPL --verify
        """
    )
    parser.add_argument(
        "--ticker",
        type=str,
        nargs='+',
        required=True,
        help="처리할 티커 심볼 (하나 이상 지정 가능)"
    )
    parser.add_argument(
        "--verify",
        action="store_true",
        help="적재 후 검증 수행"
    )
    return parser.parse_args()

def main():
    """Graph DB 저장 및 검증"""
    args = parse_args()
    tickers = [t.upper() for t in args.ticker]
    
    # GraphLoader 초기화
    loader = GraphLoader()
    loader.connect()
    loader.initialize()
    
    try:
        for ticker in tickers:
            logger.info(f"🚀 Loading graph for {ticker}...")
            
            graph_dir = Path("data/graph")
            
            # Static Graph 로드
            static_file = graph_dir / f"{ticker}_static_graph.json"
            if static_file.exists():
                with open(static_file, 'r', encoding='utf-8') as f:
                    static_graph = json.load(f)
                loader.load_static_graph(ticker, static_graph)
                logger.info(f"✅ Static graph loaded for {ticker}")
            else:
                logger.warning(f"Static graph not found: {static_file}")
            
            # Dynamic Graph 로드
            dynamic_file = graph_dir / f"{ticker}_dynamic_graph.json"
            if dynamic_file.exists():
                with open(dynamic_file, 'r', encoding='utf-8') as f:
                    dynamic_graph = json.load(f)
                loader.load_dynamic_graph(ticker, dynamic_graph)
                logger.info(f"✅ Dynamic graph loaded for {ticker}")
            else:
                logger.warning(f"Dynamic graph not found: {dynamic_file}")
            
            # 통계 출력
            stats = loader.get_stats()
            logger.info(f"📊 Statistics for {ticker}: {stats}")
        
        # 검증 수행
        if args.verify:
            logger.info("🔍 Verifying loaded data...")
            verify_result = loader.verify()
            logger.info(f"✅ Verification: {verify_result}")
        
    finally:
        loader.close()
    
    logger.info("✅ Graph DB loading completed!")

if __name__ == "__main__":
    main()
```

### 실행 방법
```bash
# 단일 티커 저장
python scripts/06_load_graph_to_db.py --ticker AAPL

# 검증 포함 저장
python scripts/06_load_graph_to_db.py --ticker AAPL --verify

# 여러 티커 저장
python scripts/06_load_graph_to_db.py --ticker AAPL TSLA NVDA --verify
```

### 에러 핸들링
- Graph 파일 없음: 경고 로그 및 다음 티커로 진행
- FalkorDB 연결 실패: 에러 로그 및 종료
- 적재 실패: 에러 로그 및 계속 진행

## 🔄 상세 알고리즘/프로세스

### 실행 프로세스
1. **커맨드라인 인자 파싱**
   - `argparse`를 사용하여 `--ticker` 및 `--verify` 옵션 파싱
   - 티커 심볼을 대문자로 변환

2. **GraphLoader 초기화**
   - FalkorDB 연결
   - 인덱스 생성

3. **각 티커 처리**
   - Static Graph 파일 확인 및 로드
   - Dynamic Graph 파일 확인 및 로드
   - GraphLoader를 통한 적재
   - 통계 출력

4. **검증 수행**
   - `--verify` 옵션이 있으면 검증 수행
   - 노드/링크 수 통계 출력

5. **연결 종료**
   - GraphLoader 연결 종료

### 예외 처리
- Graph 파일 없음: 경고 로그 및 다음 티커로 진행
- FalkorDB 연결 실패: 에러 로그 및 종료
- 적재 실패: 에러 로그 및 계속 진행

## ⚙️ 설정 및 의존성

### 필요한 환경 변수
- `FALKORDB_HOST`: FalkorDB 호스트 (기본값: localhost)
- `FALKORDB_PORT`: FalkorDB 포트 (기본값: 6379)

### 외부 라이브러리 의존성
- `falkordb`: FalkorDB Python 클라이언트

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
- 실제 Graph 파일로 적재 테스트
- 검증 결과 확인
- 여러 티커 일괄 처리 테스트

### 검증 방법
- FalkorDB에 저장된 노드/링크 수 확인
- 검증 결과 확인
- 통계 정확성 확인

## ⚠️ 주의사항

- FalkorDB가 실행 중이어야 함
- Graph 파일이 있어야 적재 가능
- 대량의 데이터 적재 시 시간이 오래 걸릴 수 있음
- MERGE를 사용하여 중복 방지

## 📝 History
