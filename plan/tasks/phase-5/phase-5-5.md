# Phase 5.5: 생성 스크립트

## 📋 개요

Static Graph 생성을 실행하는 스크립트를 구현합니다.

## 🎯 목표

- 티커별 Static Graph 생성
- JSON 파일로 저장

## 📝 상세 구현

### 스크립트 구조

```python
#!/usr/bin/env python
"""Static Graph 생성 스크립트"""
import argparse
from app.services.processing.graph_generator import generate_static_graph

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--ticker", nargs="+", default=["AAPL"])
    args = parser.parse_args()
    
    for ticker in args.ticker:
        static_graph = generate_static_graph(ticker.upper())
        # 저장: data/graph/{TICKER}_static_graph.json

if __name__ == "__main__":
    main()
```

### 실행 방법

```bash
python scripts/04_generate_static_graph.py --ticker AAPL TSLA NVDA
```

## 📁 파일 위치

**파일**: `scripts/04_generate_static_graph.py`

## 📝 History

