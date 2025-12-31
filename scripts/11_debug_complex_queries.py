"""
복합 쿼리 디버깅 스크립트

Product, Person 필터가 포함된 복합 쿼리의 문제점을 파악합니다.
"""

import sys
import os
from pathlib import Path

# 프로젝트 루트를 Python 경로에 추가
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

from dotenv import load_dotenv
load_dotenv()

import logging
import json
from app.services.graph_loader import GraphLoader
from app.services.query_engine import QueryEngine
from app.services.cypher_query_builder import CypherQueryBuilder

# 로깅 설정
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)

logger = logging.getLogger(__name__)


def debug_complex_queries():
    """복합 쿼리 디버깅"""
    
    print("=" * 80)
    print("복합 쿼리 디버깅")
    print("=" * 80)
    
    try:
        graph_loader = GraphLoader()
        graph_loader.connect()
        
        print("\n✅ GraphLoader 연결 완료\n")
        
        # 1. 데이터베이스 상태 확인
        print("=" * 80)
        print("1. 데이터베이스 상태 확인")
        print("=" * 80)
        
        # Product 노드 확인
        product_query = "MATCH (p:Product) RETURN count(p) AS count, collect(p.name)[0..5] AS sample_names"
        product_result = graph_loader.execute_query(product_query)
        print(f"\n📦 Product 노드 수: {product_result[0]['count'] if product_result else 0}")
        if product_result and product_result[0].get('sample_names'):
            print(f"   샘플 이름: {product_result[0]['sample_names']}")
        
        # Person 노드 확인
        person_query = "MATCH (p:Person) RETURN count(p) AS count, collect(p.name)[0..5] AS sample_names"
        person_result = graph_loader.execute_query(person_query)
        print(f"\n👤 Person 노드 수: {person_result[0]['count'] if person_result else 0}")
        if person_result and person_result[0].get('sample_names'):
            print(f"   샘플 이름: {person_result[0]['sample_names']}")
        
        # IS_MENTIONED_IN 링크 확인
        mention_query = """
        MATCH (a)-[r:IS_MENTIONED_IN]->(b)
        RETURN count(r) AS count, labels(a)[0] AS from_type, labels(b)[0] AS to_type
        LIMIT 10
        """
        mention_result = graph_loader.execute_query(mention_query)
        print(f"\n🔗 IS_MENTIONED_IN 링크 수: {mention_result[0]['count'] if mention_result else 0}")
        if mention_result:
            for row in mention_result[:5]:
                print(f"   {row.get('from_type')} -> {row.get('to_type')}")
        
        # 2. iPhone 15 관련 데이터 확인
        print("\n" + "=" * 80)
        print("2. iPhone 15 관련 데이터 확인")
        print("=" * 80)
        
        # iPhone 15 Product 노드 확인
        iphone_query = "MATCH (p:Product) WHERE p.name CONTAINS 'iPhone' RETURN p.id, p.name, p.description LIMIT 10"
        iphone_result = graph_loader.execute_query(iphone_query)
        print(f"\n📱 iPhone 관련 Product 노드: {len(iphone_result)}개")
        for row in iphone_result:
            print(f"   - {row.get('p.name')} (id: {row.get('p.id')})")
        
        # iPhone 15와 Opportunity 연결 확인
        iphone_opp_query = """
        MATCH (p:Product)-[r:IS_MENTIONED_IN]->(o:Opportunity)
        WHERE p.name CONTAINS 'iPhone'
        RETURN p.name AS product_name, o.id AS opp_id, o.entity AS opp_entity, o.ticker
        LIMIT 10
        """
        iphone_opp_result = graph_loader.execute_query(iphone_opp_query)
        print(f"\n🔗 iPhone -> Opportunity 연결: {len(iphone_opp_result)}개")
        for row in iphone_opp_result:
            print(f"   {row.get('product_name')} -> {row.get('opp_entity')} ({row.get('o.ticker')})")
        
        # 3. Tim Cook 관련 데이터 확인
        print("\n" + "=" * 80)
        print("3. Tim Cook 관련 데이터 확인")
        print("=" * 80)
        
        # Tim Cook Person 노드 확인
        tim_cook_query = "MATCH (p:Person) WHERE p.name CONTAINS 'Tim' OR p.name CONTAINS 'Cook' RETURN p.id, p.name, p.description LIMIT 10"
        tim_cook_result = graph_loader.execute_query(tim_cook_query)
        print(f"\n👤 Tim Cook 관련 Person 노드: {len(tim_cook_result)}개")
        for row in tim_cook_result:
            print(f"   - {row.get('p.name')} (id: {row.get('p.id')})")
        
        # Tim Cook과 Opportunity 연결 확인
        tim_cook_opp_query = """
        MATCH (p:Person)-[r:IS_MENTIONED_IN]->(o:Opportunity)
        WHERE p.name CONTAINS 'Tim' OR p.name CONTAINS 'Cook'
        RETURN p.name AS person_name, o.id AS opp_id, o.entity AS opp_entity, o.ticker
        LIMIT 10
        """
        tim_cook_opp_result = graph_loader.execute_query(tim_cook_opp_query)
        print(f"\n🔗 Person -> Opportunity 연결: {len(tim_cook_opp_result)}개")
        for row in tim_cook_opp_result:
            print(f"   {row.get('person_name')} -> {row.get('opp_entity')} ({row.get('o.ticker')})")
        
        # 4. 복합 쿼리 단계별 디버깅
        print("\n" + "=" * 80)
        print("4. 복합 쿼리 단계별 디버깅")
        print("=" * 80)
        
        # 케이스 1: iPhone 15와 Opportunity
        print("\n📱 케이스 1: iPhone 15와 Opportunity")
        print("-" * 80)
        
        # Step 1: Company -> Product 확인
        step1_query = """
        MATCH (c:Company {ticker: 'AAPL'})-[r:MAKE]->(p:Product)
        WHERE p.name CONTAINS 'iPhone 15'
        RETURN p.id, p.name
        LIMIT 5
        """
        step1_result = graph_loader.execute_query(step1_query)
        print(f"Step 1 - Company -> Product: {len(step1_result)}개")
        for row in step1_result:
            print(f"   Product: {row.get('p.name')} (id: {row.get('p.id')})")
        
        # Step 2: Product -> Opportunity 확인
        if step1_result:
            product_id = step1_result[0].get('p.id')
            step2_query = f"""
            MATCH (p:Product {{id: '{product_id}'}})-[r:IS_MENTIONED_IN]->(o:Opportunity)
            RETURN o.id, o.entity, o.ticker
            LIMIT 5
            """
            step2_result = graph_loader.execute_query(step2_query)
            print(f"\nStep 2 - Product -> Opportunity: {len(step2_result)}개")
            for row in step2_result:
                print(f"   Opportunity: {row.get('o.entity')} (ticker: {row.get('o.ticker')})")
        
        # Step 3: 전체 경로 확인
        step3_query = """
        MATCH (c:Company {ticker: 'AAPL'})-[r1:MAKE]->(p:Product)-[r2:IS_MENTIONED_IN]->(o:Opportunity)
        WHERE p.name CONTAINS 'iPhone 15' AND o.ticker = 'AAPL'
        RETURN p.name AS product_name, o.id AS opp_id, o.entity AS opp_entity
        LIMIT 10
        """
        step3_result = graph_loader.execute_query(step3_query)
        print(f"\nStep 3 - 전체 경로: {len(step3_result)}개")
        for row in step3_result:
            print(f"   {row.get('product_name')} -> {row.get('opp_entity')}")
        
        # 케이스 2: Tim Cook과 Opportunity
        print("\n👤 케이스 2: Tim Cook과 Opportunity")
        print("-" * 80)
        
        # Step 1: Company -> Person 확인
        step1_person_query = """
        MATCH (c:Company {ticker: 'GOOGL'})-[r:HAS_RELATION]->(p:Person)
        WHERE p.name CONTAINS 'Tim Cook'
        RETURN p.id, p.name
        LIMIT 5
        """
        step1_person_result = graph_loader.execute_query(step1_person_query)
        print(f"Step 1 - Company -> Person: {len(step1_person_result)}개")
        for row in step1_person_result:
            print(f"   Person: {row.get('p.name')} (id: {row.get('p.id')})")
        
        # Step 2: Person -> Opportunity 확인
        if step1_person_result:
            person_id = step1_person_result[0].get('p.id')
            step2_person_query = f"""
            MATCH (p:Person {{id: '{person_id}'}})-[r:IS_MENTIONED_IN]->(o:Opportunity)
            RETURN o.id, o.entity, o.ticker
            LIMIT 5
            """
            step2_person_result = graph_loader.execute_query(step2_person_query)
            print(f"\nStep 2 - Person -> Opportunity: {len(step2_person_result)}개")
            for row in step2_person_result:
                print(f"   Opportunity: {row.get('o.entity')} (ticker: {row.get('o.ticker')})")
        
        # Step 3: 전체 경로 확인
        step3_person_query = """
        MATCH (c:Company {ticker: 'GOOGL'})-[r1:HAS_RELATION]->(p:Person)-[r2:IS_MENTIONED_IN]->(o:Opportunity)
        WHERE p.name CONTAINS 'Tim Cook' AND o.ticker = 'GOOGL'
        RETURN p.name AS person_name, o.id AS opp_id, o.entity AS opp_entity
        LIMIT 10
        """
        step3_person_result = graph_loader.execute_query(step3_person_query)
        print(f"\nStep 3 - 전체 경로: {len(step3_person_result)}개")
        for row in step3_person_result:
            print(f"   {row.get('person_name')} -> {row.get('opp_entity')}")
        
        # 5. 생성된 쿼리와 실제 데이터 비교
        print("\n" + "=" * 80)
        print("5. 생성된 쿼리 검증")
        print("=" * 80)
        
        engine = QueryEngine(graph_loader=graph_loader)
        query_builder = CypherQueryBuilder()
        
        # 테스트 질의
        test_queries = [
            "애플의 iPhone 15와 관련된 기회 요소는?",
            "구글의 Tim Cook이 언급된 기회 요소는?",
        ]
        
        for query in test_queries:
            print(f"\n📝 질의: {query}")
            print("-" * 80)
            
            intent = engine.extract_intent(query)
            cypher_query, params = query_builder.build_query(intent)
            
            print(f"생성된 쿼리:")
            print(cypher_query)
            print(f"\n파라미터: {json.dumps(params, ensure_ascii=False, indent=2)}")
            
            # 쿼리 실행
            try:
                result = graph_loader.execute_query(cypher_query, params)
                print(f"\n실행 결과: {len(result)}개")
                if result:
                    for i, row in enumerate(result[:3], 1):
                        print(f"  {i}. {json.dumps(row, ensure_ascii=False)}")
                else:
                    print("  결과 없음")
            except Exception as e:
                print(f"\n❌ 쿼리 실행 오류: {e}")
        
        # 리소스 정리
        graph_loader.close()
        print("\n" + "=" * 80)
        print("✅ 디버깅 완료")
        print("=" * 80)
        
    except Exception as e:
        logger.error(f"디버깅 실패: {e}", exc_info=True)
        print(f"\n❌ 오류 발생: {e}\n")


if __name__ == "__main__":
    debug_complex_queries()

