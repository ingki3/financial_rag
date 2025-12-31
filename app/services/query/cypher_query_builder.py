"""
Cypher Query Builder Service

Intent를 기반으로 Cypher 쿼리를 생성하는 서비스
Phase 8: 질의 응답 시스템

패턴 매칭 기반으로 target과 filters 조합에 따라 적절한 Cypher 쿼리를 생성합니다.
"""

import logging
from typing import Dict, List, Optional, Any, Tuple
from app.services.shared.name_normalizer import NameNormalizer

logger = logging.getLogger(__name__)


class CypherQueryBuilder:
    """Intent를 기반으로 Cypher 쿼리 생성"""
    
    # Target 타입별 링크 타입 매핑
    TARGET_LINK_MAP = {
        "Risk": "HAS_RISKS",
        "Opportunity": "HAS_OPPORTUNITIES",
        "Event": "HAS_EVENTS",
        "Technology": "HAS_TECHNOLOGIES"
    }
    
    def __init__(self, name_normalizer: Optional[NameNormalizer] = None):
        """
        Cypher 쿼리 빌더 초기화
        
        Args:
            name_normalizer: 이름 표준화 모듈 (None이면 자동 생성)
        """
        self.name_normalizer = name_normalizer or NameNormalizer()
    
    def build_query(self, intent: Dict) -> Tuple[str, Dict[str, Any]]:
        """
        Intent를 기반으로 Cypher 쿼리 생성
        
        Args:
            intent: Intent 객체 (target, filters 또는 target_entity_type, filters 포함)
            
        Returns:
            (cypher_query, params): 생성된 Cypher 쿼리와 파라미터 딕셔너리
        """
        # 새로운 스키마 (target, filters 리스트) 또는 기존 스키마 (target_entity_type, filters 딕셔너리) 지원
        target = intent.get("target", {})
        filters = intent.get("filters", [])
        query_type = intent.get("query_type", "explain")
        
        # Target 타입 추출
        target_type = None
        if isinstance(target, dict):
            target_type = target.get("node_type")
        
        # 기존 스키마 지원 (target_entity_type)
        if not target_type:
            target_type = intent.get("target_entity_type")
        
        # Filters를 리스트로 변환 (기존 스키마인 경우)
        if not isinstance(filters, list):
            filters = self._convert_filters_to_list(filters, intent)
        
        # 이름 표준화
        ticker = None
        if isinstance(filters, list):
            # Company 필터에서 ticker 추출
            company_filter = next((f for f in filters if isinstance(f, dict) and f.get("node_type") == "Company"), None)
            if company_filter:
                ticker = company_filter.get("ticker")
        
        if ticker and isinstance(filters, list):
            filters = self.name_normalizer.normalize_filters(filters, ticker)
        
        # Target 타입이 없거나 general인 경우
        if not target_type or target_type == "general":
            return self._build_general_query(intent)
        
        # Target이 Opportunity, Risk, Event인 경우 패턴 매칭
        if target_type in ["Opportunity", "Risk", "Event"]:
            return self._build_pattern_query(target_type, filters, intent)
        
        # 기타 타입 (Technology, Product, Person 등)
        return self._build_other_query(target_type, filters, intent)
    
    def _convert_filters_to_list(self, filters: Any, intent: Dict) -> List[Dict]:
        """
        기존 스키마의 filters 딕셔너리를 새로운 스키마의 filters 리스트로 변환
        
        Args:
            filters: 기존 스키마의 filters 딕셔너리
            intent: 전체 Intent 객체
            
        Returns:
            filters 리스트
        """
        if isinstance(filters, list):
            return filters
        
        if not isinstance(filters, dict):
            return []
        
        filter_list = []
        
        # Company 필터
        if filters.get("company"):
            company = filters["company"]
            if isinstance(company, str):
                filter_list.append({"node_type": "Company", "ticker": company})
            elif isinstance(company, list):
                for c in company:
                    filter_list.append({"node_type": "Company", "ticker": c})
        
        # Person 필터
        if filters.get("person"):
            filter_list.append({"node_type": "Person", "name": filters["person"]})
        
        # Product 필터
        if filters.get("product"):
            filter_list.append({"node_type": "Product", "name": filters["product"]})
        
        # Technology 필터 (기존 스키마에는 없지만 확장성 고려)
        if filters.get("technology"):
            filter_list.append({"node_type": "Technology", "name": filters["technology"]})
        
        # Time 필터
        if filters.get("time"):
            time_filter = filters["time"]
            if isinstance(time_filter, dict):
                filter_list.append({"node_type": "Time", **time_filter})
        
        return filter_list
    
    def _build_pattern_query(
        self, 
        target_type: str, 
        filters: List[Dict], 
        intent: Dict
    ) -> Tuple[str, Dict[str, Any]]:
        """
        Opportunity, Risk, Event에 대한 패턴 매칭 쿼리 생성
        
        Args:
            target_type: Target 노드 타입 (Opportunity, Risk, Event)
            filters: 필터 노드 리스트
            intent: 전체 Intent 객체
            
        Returns:
            (cypher_query, params)
        """
        params = {}
        filter_nodes = self._extract_filter_nodes(filters)
        
        # 필터 노드 타입 분류
        company_filter = next((f for f in filter_nodes if f.get("node_type") == "Company"), None)
        person_filter = next((f for f in filter_nodes if f.get("node_type") == "Person"), None)
        technology_filter = next((f for f in filter_nodes if f.get("node_type") == "Technology"), None)
        product_filter = next((f for f in filter_nodes if f.get("node_type") == "Product"), None)
        
        # 패턴 매칭: 필터 조합에 따라 쿼리 생성
        link_type = self.TARGET_LINK_MAP.get(target_type, "HAS_RISKS")
        target_label = target_type
        
        # 쿼리 빌드 시작
        match_clauses = []
        where_parts = []
        
        # 1. Company 필터가 있는 경우
        if company_filter:
            ticker = company_filter.get("ticker")
            if ticker:
                params["company_ticker"] = ticker
                
                # Company에서 Target으로 직접 연결
                base_match = f"(c:Company {{ticker: $company_ticker}})-[r1:{link_type}]->(target:{target_label})"
                
                # Company와 다른 필터 연결
                if person_filter:
                    name = person_filter.get("name")
                    if name:
                        params["person_name"] = name
                        # Company -> Person -> Target 경로
                        match_clauses.append(
                            f"(c:Company {{ticker: $company_ticker}})-[r1:HAS_RELATION]->(p:Person {{name: $person_name}})-[r2:IS_MENTIONED_IN]->(target:{target_label})"
                        )
                        where_parts.append(f"target.ticker = $company_ticker")
                    else:
                        match_clauses.append(base_match)
                elif technology_filter:
                    name = technology_filter.get("name") or technology_filter.get("entity")
                    if name:
                        params["technology_name"] = name
                        # Company -> Technology -> Target 경로
                        match_clauses.append(
                            f"(c:Company {{ticker: $company_ticker}})-[r1:HAS_TECHNOLOGIES]->(t:Technology {{entity: $technology_name}})-[r2:IS_MENTIONED_IN]->(target:{target_label})"
                        )
                        where_parts.append(f"target.ticker = $company_ticker")
                    else:
                        match_clauses.append(base_match)
                elif product_filter:
                    name = product_filter.get("name")
                    if name:
                        params["product_name"] = name
                        # Company -> Product -> Target 경로
                        # Product 이름은 부분 매칭 사용 (CONTAINS)
                        # "iPhone 15" 같은 경우 "iPhone"도 매칭되도록 함
                        match_clauses.append(
                            f"(c:Company {{ticker: $company_ticker}})-[r1:MAKE]->(pr:Product)-[r2:IS_MENTIONED_IN]->(target:{target_label})"
                        )
                        # Product 이름이 여러 단어인 경우, 첫 단어도 검색 (예: "iPhone 15" -> "iPhone"도 매칭)
                        product_name_parts = name.split()
                        if len(product_name_parts) > 1:
                            # 여러 단어인 경우: 정확한 이름 또는 첫 단어로 매칭
                            where_parts.append(f"(pr.name CONTAINS $product_name OR pr.name CONTAINS '{product_name_parts[0]}') AND target.ticker = $company_ticker")
                        else:
                            where_parts.append(f"pr.name CONTAINS $product_name AND target.ticker = $company_ticker")
                    else:
                        match_clauses.append(base_match)
                else:
                    # Company만 있는 경우
                    match_clauses.append(base_match)
        else:
            # Company 필터가 없는 경우
            if person_filter:
                name = person_filter.get("name")
                if name:
                    params["person_name"] = name
                    match_clauses.append(f"(p:Person {{name: $person_name}})-[r1:IS_MENTIONED_IN]->(target:{target_label})")
            
            if technology_filter:
                name = technology_filter.get("name") or technology_filter.get("entity")
                if name:
                    params["technology_name"] = name
                    match_clauses.append(f"(t:Technology {{entity: $technology_name}})-[r1:IS_MENTIONED_IN]->(target:{target_label})")
            
            if product_filter:
                name = product_filter.get("name")
                if name:
                    params["product_name"] = name
                    # Product 이름은 부분 매칭 사용
                    match_clauses.append(f"(pr:Product)-[r1:IS_MENTIONED_IN]->(target:{target_label})")
                    where_parts.append(f"pr.name CONTAINS $product_name")
            
            # 필터가 없는 경우 (단순 Target 검색)
            if not match_clauses:
                match_clauses.append(f"(target:{target_label})")
        
        # 시간 필터 추가
        time_filter = intent.get("filters", {}).get("time") if isinstance(intent.get("filters"), dict) else None
        if not time_filter:
            # filters가 리스트인 경우 time 필터 찾기
            for f in filters:
                if isinstance(f, dict) and f.get("node_type") == "Time":
                    time_filter = f
                    break
        
        if time_filter:
            if isinstance(time_filter, dict):
                year = time_filter.get("year")
                period = time_filter.get("period")
                
                if year:
                    params["year"] = year
                    # year 필드 사용 (Risk, Opportunity, Event 노드에 추가됨)
                    where_parts.append("target.year = $year")
                elif period:
                    if period == "recent":
                        where_parts.append("target.year >= 2023")
                    elif period == "2022-2023":
                        where_parts.append("(target.year = 2022 OR target.year = 2023)")
                    elif period == "2021-2023":
                        where_parts.append("target.year >= 2021 AND target.year <= 2023")
        
        # 쿼리 조합
        if len(match_clauses) == 1:
            query = f"MATCH {match_clauses[0]}"
        else:
            query = "MATCH " + ", ".join(match_clauses)
        
        if where_parts:
            query += " WHERE " + " AND ".join(where_parts)
        
        # RETURN 절
        if target_type == "Event":
            query += " RETURN target.id, target.entity, target.description, target.ticker, target.date, target.year"
        else:
            query += " RETURN target.id, target.entity, target.description, target.ticker, target.year"
        
        # 정렬 및 제한
        query += " ORDER BY target.date DESC" if target_type == "Event" else " ORDER BY target.id"
        query += " LIMIT 20"
        
        return query, params
    
    def _build_other_query(
        self, 
        target_type: str, 
        filters: List[Dict], 
        intent: Dict
    ) -> Tuple[str, Dict[str, Any]]:
        """
        Technology, Product, Person 등 기타 타입에 대한 쿼리 생성
        
        Args:
            target_type: Target 노드 타입
            filters: 필터 노드 리스트
            intent: 전체 Intent 객체
            
        Returns:
            (cypher_query, params)
        """
        params = {}
        filter_nodes = self._extract_filter_nodes(filters)
        
        match_parts = []
        where_parts = []
        
        # Company 필터가 있는 경우
        company_filter = next((f for f in filter_nodes if f.get("node_type") == "Company"), None)
        if company_filter:
            ticker = company_filter.get("ticker")
            if ticker:
                params["company_ticker"] = ticker
                
                if target_type == "Technology":
                    match_parts.append(f"(c:Company {{ticker: $company_ticker}})-[r:HAS_TECHNOLOGIES]->(target:Technology)")
                elif target_type == "Product":
                    match_parts.append(f"(c:Company {{ticker: $company_ticker}})-[r:MAKE]->(target:Product)")
                elif target_type == "Person":
                    match_parts.append(f"(c:Company {{ticker: $company_ticker}})-[r:HAS_RELATION]->(target:Person)")
                else:
                    match_parts.append(f"(target:{target_type})")
        else:
            match_parts.append(f"(target:{target_type})")
        
        # 쿼리 조합
        query = "MATCH " + ", ".join(match_parts)
        
        if where_parts:
            query += " WHERE " + " AND ".join(where_parts)
        
        # Technology 타입은 entity 필드 사용, 나머지는 name 필드 사용
        if target_type == "Technology":
            query += f" RETURN target.id, target.entity, target.description"
        else:
            query += f" RETURN target.id, target.name, target.description"
        query += " LIMIT 20"
        
        return query, params
    
    def _build_general_query(self, intent: Dict) -> Tuple[str, Dict[str, Any]]:
        """
        General 타입에 대한 쿼리 생성 (모든 노드 타입 검색)
        
        Args:
            intent: 전체 Intent 객체
            
        Returns:
            (cypher_query, params)
        """
        query_text = intent.get("query_text", "")
        filters = intent.get("filters", [])
        
        # 간단한 텍스트 검색 쿼리
        query = """
        MATCH (n)
        WHERE n.description CONTAINS $query_text
           OR n.entity CONTAINS $query_text
           OR n.name CONTAINS $query_text
        RETURN n.id, labels(n)[0] AS node_type, n.entity, n.description
        LIMIT 20
        """
        
        params = {"query_text": query_text}
        
        return query, params
    
    def _extract_filter_nodes(self, filters: Any) -> List[Dict]:
        """
        Filters에서 노드 리스트 추출
        
        Args:
            filters: filters 값 (리스트 또는 딕셔너리)
            
        Returns:
            필터 노드 리스트
        """
        if isinstance(filters, list):
            return filters
        elif isinstance(filters, dict):
            # 기존 형식 (filters가 딕셔너리인 경우)을 노드 리스트로 변환
            nodes = []
            
            if filters.get("company"):
                company = filters["company"]
                if isinstance(company, str):
                    nodes.append({"node_type": "Company", "ticker": company})
                elif isinstance(company, list):
                    for c in company:
                        nodes.append({"node_type": "Company", "ticker": c})
            
            if filters.get("person"):
                nodes.append({"node_type": "Person", "name": filters["person"]})
            
            if filters.get("product"):
                nodes.append({"node_type": "Product", "name": filters["product"]})
            
            if filters.get("technology"):
                nodes.append({"node_type": "Technology", "name": filters["technology"]})
            
            if filters.get("time"):
                nodes.append({"node_type": "Time", **filters["time"]})
            
            return nodes
        else:
            return []

