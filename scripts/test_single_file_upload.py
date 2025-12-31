#!/usr/bin/env python
"""단일 파일 업로드 테스트 스크립트"""
import os
import sys
import asyncio
import logging
from pathlib import Path
from datetime import datetime
from dotenv import load_dotenv

load_dotenv()

# 프로젝트 루트 추가
sys.path.insert(0, str(Path(__file__).parent.parent))

from app.services.graphiti_manager import GraphitiManager

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


async def test_single_file_upload(file_path: str):
    """단일 파일 업로드 테스트"""
    file_path_obj = Path(file_path)
    
    if not file_path_obj.exists():
        print(f"❌ 파일을 찾을 수 없습니다: {file_path}")
        return False
    
    print("=" * 60)
    print("🧪 단일 파일 업로드 테스트")
    print("=" * 60)
    print(f"📄 파일: {file_path_obj.name}")
    print(f"📁 경로: {file_path_obj}")
    print(f"🗄️ FalkorDB: {os.getenv('FALKORDB_HOST', 'localhost')}:{os.getenv('FALKORDB_PORT', '6379')}")
    print("=" * 60)
    
    # GraphitiManager 초기화
    manager = GraphitiManager(
        host=os.getenv("FALKORDB_HOST", "localhost"),
        port=int(os.getenv("FALKORDB_PORT", "6379")),
        database="default_db"
    )
    
    try:
        # 초기화
        print("\n1️⃣ Graphiti 초기화 중...")
        await manager.initialize()
        print("✅ 초기화 완료")
        
        # 파일 업로드
        print(f"\n2️⃣ 파일 업로드 시작: {file_path_obj.name}")
        start_time = datetime.now()
        
        stats = await manager.add_extracted_triplets(file_path_obj)
        
        elapsed = (datetime.now() - start_time).total_seconds()
        
        print(f"\n{'=' * 60}")
        print("📊 업로드 결과")
        print(f"{'=' * 60}")
        print(f"소요 시간: {elapsed:.2f}초")
        print(f"\n카테고리별 저장된 Episodes:")
        print(f"   🔵 Opportunities: {stats.get('opportunities', 0)}개")
        print(f"   🔴 Risks: {stats.get('risks', 0)}개")
        print(f"   📅 Events: {stats.get('events', 0)}개")
        print(f"   📈 Strategies: {stats.get('strategies', 0)}개")
        print(f"   💰 Financials: {stats.get('financials', 0)}개")
        
        total = sum(stats.values())
        print(f"\n   총 Episodes: {total}개")
        print(f"{'=' * 60}")
        
        if total > 0:
            print("✅ 업로드 성공!")
            return True
        else:
            print("⚠️  업로드되었지만 episodes가 0개입니다.")
            return False
            
    except Exception as e:
        print(f"\n❌ 업로드 실패: {e}")
        import traceback
        traceback.print_exc()
        return False
        
    finally:
        await manager.close()
        print("\n🔌 연결 종료")


def main():
    import argparse
    
    parser = argparse.ArgumentParser(description="단일 파일 업로드 테스트")
    parser.add_argument(
        "--file",
        type=str,
        required=True,
        help="업로드할 파일 경로"
    )
    
    args = parser.parse_args()
    
    result = asyncio.run(test_single_file_upload(args.file))
    
    sys.exit(0 if result else 1)


if __name__ == "__main__":
    main()

