# Phase 4.2: 추출 스크립트

## 📋 개요

추출기 모듈을 실행하여 모든 파싱된 파일에서 Triplet을 추출하는 스크립트를 구현합니다.

## 🎯 목표

- 파싱된 파일 순회
- LLM을 통한 Triplet 추출
- JSON 형식으로 저장

## 📝 상세 구현

### 스크립트 구조

```python
#!/usr/bin/env python
"""Knowledge Triplet 추출 스크립트"""
from app.services.processing.triplet_extractor import TripletExtractorBatch

def main():
    extractor_batch = TripletExtractorBatch()
    extractor_batch.extract_all()
    
    print("✅ 추출 완료!")

if __name__ == "__main__":
    main()
```

### 실행 방법

```bash
# 전체 추출
python scripts/03_extract_triplets.py

# 특정 모드 (section/filing)
python scripts/03_extract_triplets.py --mode section
```

## 📁 파일 위치

**파일**: `scripts/03_extract_triplets.py`

## ⚠️ 주의사항

- 추출 시간: 파일당 약 1-2분 소요
- LLM API 비용 발생
- 백그라운드 실행 권장

## 📝 History

