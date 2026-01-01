#!/bin/bash
# Data 폴더 전체 재생성 스크립트

set -e

echo "🚀 Data 폴더 전체 재생성 시작..."
echo ""

# 가상환경 활성화
if [ -d "venv" ]; then
    source venv/bin/activate
    echo "✅ 가상환경 활성화"
else
    echo "⚠️ 가상환경이 없습니다. venv를 생성하세요."
    exit 1
fi

# Phase 2: SEC 공시 다운로드
echo ""
echo "=" * 60
echo "Phase 2: SEC 공시 다운로드"
echo "=" * 60
python scripts/01_download_filings.py

# Phase 3: 공시 파싱
echo ""
echo "=" * 60
echo "Phase 3: 공시 파싱"
echo "=" * 60
python scripts/02_parse_filings.py

# Phase 4: 트리플렛 추출
echo ""
echo "=" * 60
echo "Phase 4: 트리플렛 추출"
echo "=" * 60
python scripts/03_extract_triplets.py

# Phase 5: Static Graph 생성
echo ""
echo "=" * 60
echo "Phase 5: Static Graph 생성"
echo "=" * 60
python scripts/04_generate_static_graph.py

# Phase 6: Dynamic Graph 생성
echo ""
echo "=" * 60
echo "Phase 6: Dynamic Graph 생성"
echo "=" * 60
python scripts/06_generate_dynamic_graph.py

echo ""
echo "=" * 60
echo "✅ 모든 데이터 생성 완료!"
echo "=" * 60

