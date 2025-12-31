#!/usr/bin/env python
"""FalkorDB 상태 확인 스크립트"""
import os
import sys
import asyncio
import time
from pathlib import Path
from dotenv import load_dotenv

load_dotenv()

sys.path.insert(0, str(Path(__file__).parent.parent))

from falkordb import FalkorDB

def check_db_status(host: str = "localhost", port: int = 6379, database: str = "default_db"):
    """FalkorDB 상태 확인"""
    print("=" * 60)
    print("🔍 FalkorDB 상태 확인")
    print("=" * 60)
    print(f"호스트: {host}:{port}")
    print(f"데이터베이스: {database}")
    print("=" * 60)
    
    try:
        # 1. 기본 연결 확인
        print("\n1️⃣ 기본 연결 확인...")
        db = FalkorDB(host=host, port=port)
        graph = db.select_graph(database)
        print("✅ 연결 성공")
        
        # 2. 간단한 쿼리로 응답 시간 확인
        print("\n2️⃣ 쿼리 응답 시간 확인...")
        start_time = time.time()
        result = graph.query("MATCH (n) RETURN count(n) AS total LIMIT 1")
        elapsed = (time.time() - start_time) * 1000
        total_nodes = result.result_set[0][0] if result.result_set else 0
        print(f"✅ 쿼리 응답 시간: {elapsed:.2f}ms")
        print(f"   총 노드 수: {total_nodes}")
        
        # 3. 엣지 수 확인
        print("\n3️⃣ 엣지 수 확인...")
        start_time = time.time()
        result = graph.query("MATCH ()-[e]->() RETURN count(e) AS total LIMIT 1")
        elapsed = (time.time() - start_time) * 1000
        total_edges = result.result_set[0][0] if result.result_set else 0
        print(f"✅ 쿼리 응답 시간: {elapsed:.2f}ms")
        print(f"   총 엣지 수: {total_edges}")
        
        # 4. 티커별 데이터 확인
        print("\n4️⃣ 티커별 데이터 확인...")
        tickers = ["AAPL", "TSLA", "AMZN", "GOOGL", "MSFT", "META", "NVDA"]
        for ticker in tickers:
            result = graph.query(
                "MATCH (n) WHERE n.group_id = $group_id RETURN count(n) AS total LIMIT 1",
                {"group_id": ticker}
            )
            count = result.result_set[0][0] if result.result_set else 0
            if count > 0:
                print(f"   {ticker}: {count}개 노드")
        
        # 5. 최근 에러 가능성 확인 (pending queries 관련)
        print("\n5️⃣ DB 부하 상태 확인...")
        if elapsed > 1000:
            print("⚠️  쿼리 응답 시간이 느립니다 (>1초)")
            print("   → 'Max pending queries exceeded' 에러 가능성 높음")
        elif elapsed > 500:
            print("⚠️  쿼리 응답 시간이 다소 느립니다 (>500ms)")
            print("   → 주의 필요")
        else:
            print("✅ 쿼리 응답 시간 정상")
        
        print("\n" + "=" * 60)
        print("📊 종합 평가")
        print("=" * 60)
        
        if elapsed < 500:
            print("✅ 업로드 가능 상태")
            print("   - DB 응답 시간 정상")
            print("   - 연결 상태 양호")
        elif elapsed < 1000:
            print("⚠️  업로드 가능하나 주의 필요")
            print("   - DB 응답 시간이 다소 느림")
            print("   - 낮은 설정(SEMAPHORE_LIMIT=3)으로 진행 권장")
        else:
            print("❌ 업로드 비권장")
            print("   - DB 응답 시간이 매우 느림")
            print("   - 'Max pending queries exceeded' 에러 가능성 높음")
            print("   - DB 부하 감소 후 재시도 권장")
        
        print("=" * 60)
        
    except Exception as e:
        print(f"\n❌ 오류 발생: {e}")
        print("=" * 60)
        return False
    
    return True

if __name__ == "__main__":
    host = os.getenv("FALKORDB_HOST", "localhost")
    port = int(os.getenv("FALKORDB_PORT", "6379"))
    database = "default_db"
    
    check_db_status(host=host, port=port, database=database)

