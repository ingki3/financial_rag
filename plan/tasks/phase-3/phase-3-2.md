# Phase 3.2: 파싱 스크립트

## 📋 개요

파서 모듈을 실행하여 모든 다운로드된 공시 파일을 파싱하는 스크립트를 구현합니다.

## 🎯 목표

- 다운로드된 파일 순회
- 파서를 통한 섹션 추출
- JSON 형식으로 저장

## 📝 상세 구현

### 스크립트 구조

```python
#!/usr/bin/env python
"""SEC 공시 파싱 스크립트"""
from pathlib import Path
from app.services.processing.filing_parser import FilingParserBatch

def main():
    parser_batch = FilingParserBatch(data_dir="./data/raw")
    results = parser_batch.parse_all()
    
    # 결과 저장
    output_dir = Path("./data/parsed")
    for parsed in results:
        # JSON 파일로 저장
        ...
    
    print("✅ 파싱 완료!")

if __name__ == "__main__":
    main()
```

### 실행 방법

```bash
python scripts/02_parse_filings.py
```

## 📁 파일 위치

**파일**: `scripts/02_parse_filings.py`

## 📝 History

