# Phase 6.4: 생성 스크립트

## 📋 개요

Dynamic Graph 생성을 실행하는 스크립트를 구현합니다.

## 🎯 목표

- 티커별 Dynamic Graph 생성
- Embedding 생성 옵션 지원
- JSON 파일로 저장

## 📝 상세 구현

### 스크립트 구조

```python
#!/usr/bin/env python
"""Dynamic Graph 생성 스크립트"""
import argparse
from app.services.processing.dynamic_graph_generator import generate_dynamic_graph

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--ticker", nargs="+", default=["AAPL"])
    parser.add_argument("--with-embedding", action="store_true")
    args = parser.parse_args()
    
    for ticker in args.ticker:
        dynamic_graph = generate_dynamic_graph(
            ticker.upper(),
            with_embedding=args.with_embedding
        )
        # 저장: data/graph/{TICKER}_dynamic_graph.json

if __name__ == "__main__":
    main()
```

### 실행 방법

```bash
# Embedding 없이 생성
python scripts/05_generate_dynamic_graph.py --ticker AAPL

# Embedding 포함 생성
python scripts/05_generate_dynamic_graph.py --ticker AAPL --with-embedding
```

## 📁 파일 위치

**파일**: `scripts/05_generate_dynamic_graph.py`

## 📝 History

