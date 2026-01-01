# Phase 7.3: 저장 스크립트

## 📋 개요

Graph DB 저장을 실행하는 스크립트를 구현합니다.

## 🎯 목표

- Static/Dynamic Graph JSON 파일 로드
- FalkorDB에 적재
- 검증 옵션 지원

## 📝 상세 구현

### 스크립트 구조

```python
#!/usr/bin/env python
"""Graph DB 저장 스크립트"""
import asyncio
from app.services.graph.graph_loader import GraphLoader

async def main():
    loader = GraphLoader()
    await loader.initialize()
    
    # Static Graph 적재
    # Dynamic Graph 적재
    
    if args.verify:
        stats = loader.get_stats()

if __name__ == "__main__":
    asyncio.run(main())
```

### 실행 방법

```bash
python scripts/06_load_graph_to_db.py --ticker AAPL --verify
```

## 📁 파일 위치

**파일**: `scripts/06_load_graph_to_db.py`

## 📝 History

