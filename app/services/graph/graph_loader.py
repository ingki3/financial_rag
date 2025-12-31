"""
Graph Loader Service
FalkorDB에 Static/Dynamic Graph JSON 파일을 적재하는 서비스

Phase 7: Graph DB 저장
"""

import json
import logging
import os
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Optional, Any

from falkordb import FalkorDB

logger = logging.getLogger(__name__)


class GraphLoader:
    """FalkorDB에 노드 및 링크를 적재하는 클래스"""
    
    # 노드 타입별 라벨 매핑
    NODE_LABELS = {
        "Company": "Company",
        "Product": "Product",
        "Person": "Person",
        "Document": "Document",
        "Section": "Section",
        "Risk": "Risk",
        "Opportunity": "Opportunity",
        "Event": "Event",
        "Technology": "Technology"
    }
    
    # Embedding이 있는 노드 타입
    EMBEDDING_NODE_TYPES = {"Risk", "Opportunity", "Event", "Technology"}
    
    def __init__(
        self,
        host: str = None,
        port: int = None,
        graph_name: str = "financial_kg"
    ):
        """FalkorDB 연결 초기화
        
        Args:
            host: FalkorDB 호스트 (기본값: 환경변수 FALKORDB_HOST 또는 localhost)
            port: FalkorDB 포트 (기본값: 환경변수 FALKORDB_PORT 또는 6379)
            graph_name: 그래프 이름 (기본값: financial_kg)
        """
        self.host = host or os.getenv("FALKORDB_HOST", "localhost")
        self.port = port or int(os.getenv("FALKORDB_PORT", "6379"))
        self.graph_name = graph_name
        
        self._client: Optional[FalkorDB] = None
        self._graph = None
        
        # 통계
        self._stats = {
            "nodes_created": 0,
            "nodes_updated": 0,
            "links_created": 0,
            "links_updated": 0,
            "errors": 0,
            "embeddings_stored": 0
        }
    
    def connect(self):
        """FalkorDB에 연결"""
        try:
            self._client = FalkorDB(host=self.host, port=self.port)
            self._graph = self._client.select_graph(self.graph_name)
            logger.info(f"Connected to FalkorDB at {self.host}:{self.port}, graph: {self.graph_name}")
        except Exception as e:
            logger.error(f"Failed to connect to FalkorDB: {e}")
            raise
    
    def close(self):
        """연결 종료"""
        # FalkorDB Python client는 명시적 close 불필요
        logger.info("FalkorDB connection closed")
    
    def initialize(self):
        """인덱스 생성"""
        if not self._graph:
            raise RuntimeError("Not connected to FalkorDB")
        
        # 각 노드 타입별 id 인덱스 생성
        index_queries = [
            "CREATE INDEX FOR (n:Company) ON (n.id)",
            "CREATE INDEX FOR (n:Product) ON (n.id)",
            "CREATE INDEX FOR (n:Person) ON (n.id)",
            "CREATE INDEX FOR (n:Document) ON (n.id)",
            "CREATE INDEX FOR (n:Section) ON (n.id)",
            "CREATE INDEX FOR (n:Risk) ON (n.id)",
            "CREATE INDEX FOR (n:Opportunity) ON (n.id)",
            "CREATE INDEX FOR (n:Event) ON (n.id)",
            "CREATE INDEX FOR (n:Technology) ON (n.id)",
            # ticker 기반 검색용 인덱스
            "CREATE INDEX FOR (n:Company) ON (n.ticker)",
            "CREATE INDEX FOR (n:Risk) ON (n.ticker)",
            "CREATE INDEX FOR (n:Opportunity) ON (n.ticker)",
            "CREATE INDEX FOR (n:Event) ON (n.ticker)",
            "CREATE INDEX FOR (n:Technology) ON (n.ticker)",
        ]
        
        for query in index_queries:
            try:
                self._graph.query(query)
                logger.debug(f"Created index: {query}")
            except Exception as e:
                # 인덱스가 이미 존재하는 경우 무시
                if "already indexed" not in str(e).lower() and "already exists" not in str(e).lower():
                    logger.warning(f"Index creation warning: {e}")
        
        logger.info("Indexes initialized")
    
    def _escape_string(self, value: str) -> str:
        """Cypher 쿼리용 문자열 이스케이프"""
        if value is None:
            return ""
        return value.replace("\\", "\\\\").replace("'", "\\'").replace('"', '\\"')
    
    def _build_node_properties(self, node: Dict) -> str:
        """노드 속성을 Cypher SET 절로 변환"""
        props = []
        
        for key, value in node.items():
            if key == "id" or key == "node_type":
                continue
            
            # metadata는 flat하게 저장
            if key == "metadata" and isinstance(value, dict):
                for meta_key, meta_value in value.items():
                    if meta_value is not None:
                        if isinstance(meta_value, str):
                            props.append(f"n.{meta_key} = '{self._escape_string(meta_value)}'")
                        elif isinstance(meta_value, (int, float)):
                            props.append(f"n.{meta_key} = {meta_value}")
                        elif isinstance(meta_value, bool):
                            props.append(f"n.{meta_key} = {str(value).lower()}")
                continue
            
            # description_embedding은 배열로 저장
            if key == "description_embedding" and isinstance(value, list):
                # 배열을 문자열로 변환하여 저장 (FalkorDB에서 배열 지원)
                embedding_str = "[" + ", ".join(str(v) for v in value) + "]"
                props.append(f"n.{key} = {embedding_str}")
                self._stats["embeddings_stored"] += 1
                continue
            
            if value is None:
                continue
            elif isinstance(value, str):
                props.append(f"n.{key} = '{self._escape_string(value)}'")
            elif isinstance(value, bool):
                props.append(f"n.{key} = {str(value).lower()}")
            elif isinstance(value, (int, float)):
                props.append(f"n.{key} = {value}")
            elif isinstance(value, list):
                # 문자열 배열
                if all(isinstance(v, str) for v in value):
                    items = ", ".join(f"'{self._escape_string(v)}'" for v in value)
                    props.append(f"n.{key} = [{items}]")
                else:
                    items = ", ".join(str(v) for v in value)
                    props.append(f"n.{key} = [{items}]")
        
        return ", ".join(props)
    
    def create_node(self, node: Dict) -> bool:
        """노드 생성 (MERGE 사용하여 중복 방지)
        
        Args:
            node: 노드 데이터 (id, node_type, ... 포함)
            
        Returns:
            성공 여부
        """
        if not self._graph:
            raise RuntimeError("Not connected to FalkorDB")
        
        node_id = node.get("id")
        node_type = node.get("node_type")
        
        if not node_id or not node_type:
            logger.warning(f"Invalid node: missing id or node_type: {node}")
            self._stats["errors"] += 1
            return False
        
        label = self.NODE_LABELS.get(node_type, node_type)
        props = self._build_node_properties(node)
        
        query = f"MERGE (n:{label} {{id: '{self._escape_string(node_id)}'}}) SET {props}"
        
        try:
            self._graph.query(query)
            self._stats["nodes_created"] += 1
            return True
        except Exception as e:
            logger.error(f"Failed to create node {node_id}: {e}")
            self._stats["errors"] += 1
            return False
    
    def create_link(self, link: Dict) -> bool:
        """링크 생성 (MERGE 사용하여 중복 방지)
        
        Args:
            link: 링크 데이터 (from, to, relationship_type, ... 포함)
            
        Returns:
            성공 여부
        """
        if not self._graph:
            raise RuntimeError("Not connected to FalkorDB")
        
        from_id = link.get("from")
        to_id = link.get("to")
        rel_type = link.get("relationship_type")
        
        if not from_id or not to_id or not rel_type:
            logger.warning(f"Invalid link: missing from, to, or relationship_type: {link}")
            self._stats["errors"] += 1
            return False
        
        # 링크 속성
        props = []
        for key, value in link.items():
            if key in ("from", "to", "relationship_type"):
                continue
            if value is None:
                continue
            elif isinstance(value, str):
                props.append(f"r.{key} = '{self._escape_string(value)}'")
            elif isinstance(value, (int, float)):
                props.append(f"r.{key} = {value}")
            elif isinstance(value, bool):
                props.append(f"r.{key} = {str(value).lower()}")
        
        # created_at 추가
        props.append(f"r.created_at = '{datetime.utcnow().isoformat()}Z'")
        
        props_str = ", ".join(props) if props else ""
        
        query = f"""
        MATCH (a {{id: '{self._escape_string(from_id)}'}})
        MATCH (b {{id: '{self._escape_string(to_id)}'}})
        MERGE (a)-[r:{rel_type}]->(b)
        """
        
        if props_str:
            query += f" SET {props_str}"
        
        try:
            self._graph.query(query)
            self._stats["links_created"] += 1
            return True
        except Exception as e:
            logger.error(f"Failed to create link {from_id} -> {to_id}: {e}")
            self._stats["errors"] += 1
            return False
    
    def load_static_graph(self, ticker: str, static_graph: Dict) -> Dict:
        """Static Graph 적재
        
        Args:
            ticker: 티커 심볼
            static_graph: Static Graph JSON 데이터
            
        Returns:
            적재 통계
        """
        logger.info(f"Loading static graph for {ticker}...")
        
        nodes = static_graph.get("nodes", {})
        links = static_graph.get("links", [])
        
        # 노드 적재 (순서: Company → Product → Person)
        for node_type in ["Company", "Product", "Person"]:
            type_nodes = nodes.get(node_type, [])
            logger.info(f"  Loading {len(type_nodes)} {node_type} nodes...")
            for node in type_nodes:
                self.create_node(node)
        
        # 링크 적재
        logger.info(f"  Loading {len(links)} links...")
        for link in links:
            self.create_link(link)
        
        stats = {
            "ticker": ticker,
            "nodes": {
                "Company": len(nodes.get("Company", [])),
                "Product": len(nodes.get("Product", [])),
                "Person": len(nodes.get("Person", []))
            },
            "links": len(links)
        }
        
        logger.info(f"Static graph for {ticker} loaded: {stats}")
        return stats
    
    def load_static_graph_file(self, file_path: Path) -> Dict:
        """Static Graph 파일 적재
        
        Args:
            file_path: Static Graph JSON 파일 경로
            
        Returns:
            적재 통계
        """
        with open(file_path, 'r', encoding='utf-8') as f:
            static_graph = json.load(f)
        
        ticker = static_graph.get("ticker", file_path.stem.replace("_static_graph", "").upper())
        return self.load_static_graph(ticker, static_graph)
    
    def load_dynamic_graph(self, ticker: str, dynamic_graph: Dict) -> Dict:
        """Dynamic Graph 적재
        
        Args:
            ticker: 티커 심볼
            dynamic_graph: Dynamic Graph JSON 데이터
            
        Returns:
            적재 통계
        """
        logger.info(f"Loading dynamic graph for {ticker}...")
        
        nodes = dynamic_graph.get("nodes", {})
        links = dynamic_graph.get("links", [])
        
        # 노드 적재 (순서: Document → Section → Risk/Opp/Event/Tech)
        node_order = ["Document", "Section", "Risk", "Opportunity", "Event", "Technology"]
        
        for node_type in node_order:
            type_nodes = nodes.get(node_type, [])
            logger.info(f"  Loading {len(type_nodes)} {node_type} nodes...")
            for node in type_nodes:
                self.create_node(node)
        
        # 링크 적재
        logger.info(f"  Loading {len(links)} links...")
        for link in links:
            self.create_link(link)
        
        stats = {
            "ticker": ticker,
            "nodes": {nt: len(nodes.get(nt, [])) for nt in node_order},
            "links": len(links)
        }
        
        logger.info(f"Dynamic graph for {ticker} loaded: {stats}")
        return stats
    
    def load_dynamic_graph_file(self, file_path: Path) -> Dict:
        """Dynamic Graph 파일 적재
        
        Args:
            file_path: Dynamic Graph JSON 파일 경로
            
        Returns:
            적재 통계
        """
        with open(file_path, 'r', encoding='utf-8') as f:
            dynamic_graph = json.load(f)
        
        ticker = dynamic_graph.get("ticker", file_path.stem.replace("_dynamic_graph", "").upper())
        return self.load_dynamic_graph(ticker, dynamic_graph)
    
    def get_stats(self) -> Dict:
        """적재 통계 반환"""
        return self._stats.copy()
    
    def reset_stats(self):
        """통계 초기화"""
        self._stats = {
            "nodes_created": 0,
            "nodes_updated": 0,
            "links_created": 0,
            "links_updated": 0,
            "errors": 0,
            "embeddings_stored": 0
        }
    
    def execute_query(self, cypher_query: str, params: Optional[Dict] = None) -> List[Dict]:
        """
        Cypher 쿼리 실행
        
        Args:
            cypher_query: 실행할 Cypher 쿼리
            params: 쿼리 파라미터 (선택적)
            
        Returns:
            쿼리 결과 리스트 (각 행은 딕셔너리)
        """
        if not self._graph:
            raise RuntimeError("Not connected to FalkorDB")
        
        try:
            result = self._graph.query(cypher_query, params or {})
            
            # 결과를 딕셔너리 리스트로 변환
            if not result.result_set:
                return []
            
            # 헤더 추출
            headers = [h[1] for h in result.header] if hasattr(result, 'header') else []
            
            # 결과 변환
            records = []
            for row in result.result_set:
                if headers:
                    record = {headers[i]: row[i] if i < len(row) else None for i in range(len(headers))}
                else:
                    # 헤더가 없는 경우 인덱스 기반
                    record = {f"col_{i}": row[i] if i < len(row) else None for i in range(len(row))}
                records.append(record)
            
            return records
            
        except Exception as e:
            logger.error(f"Failed to execute query: {e}")
            logger.error(f"Query: {cypher_query}")
            logger.error(f"Params: {params}")
            raise
    
    def verify(self) -> Dict:
        """적재 결과 검증
        
        Returns:
            노드/링크 수 통계
        """
        if not self._graph:
            raise RuntimeError("Not connected to FalkorDB")
        
        # 노드 수 확인
        node_query = "MATCH (n) RETURN labels(n)[0] AS label, count(n) AS count ORDER BY label"
        node_result = self._graph.query(node_query)
        
        nodes = {}
        for row in node_result.result_set:
            nodes[row[0]] = row[1]
        
        # 링크 수 확인
        link_query = "MATCH ()-[r]->() RETURN type(r) AS type, count(r) AS count ORDER BY type"
        link_result = self._graph.query(link_query)
        
        links = {}
        for row in link_result.result_set:
            links[row[0]] = row[1]
        
        # Embedding 수 확인
        embedding_query = """
        MATCH (n)
        WHERE n.description_embedding IS NOT NULL
        RETURN labels(n)[0] AS label, count(n) AS count
        ORDER BY label
        """
        embedding_result = self._graph.query(embedding_query)
        
        embeddings = {}
        for row in embedding_result.result_set:
            embeddings[row[0]] = row[1]
        
        return {
            "nodes": nodes,
            "links": links,
            "embeddings": embeddings,
            "total_nodes": sum(nodes.values()),
            "total_links": sum(links.values()),
            "total_embeddings": sum(embeddings.values())
        }


def load_graph_file(file_path: Path) -> Dict:
    """JSON 파일 로드
    
    Args:
        file_path: JSON 파일 경로
        
    Returns:
        JSON 데이터
    """
    with open(file_path, 'r', encoding='utf-8') as f:
        return json.load(f)


def main():
    """테스트용 메인 함수"""
    import argparse
    
    parser = argparse.ArgumentParser(description="Load graph data to FalkorDB")
    parser.add_argument("--ticker", type=str, required=True, help="Ticker symbol")
    parser.add_argument("--graph-dir", type=str, default="data/graph", help="Graph data directory")
    
    args = parser.parse_args()
    
    # 로깅 설정
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    )
    
    loader = GraphLoader()
    loader.connect()
    loader.initialize()
    
    ticker = args.ticker.upper()
    graph_dir = Path(args.graph_dir)
    
    # Static Graph 로드
    static_file = graph_dir / f"{ticker}_static_graph.json"
    if static_file.exists():
        static_graph = load_graph_file(static_file)
        loader.load_static_graph(ticker, static_graph)
    
    # Dynamic Graph 로드
    dynamic_file = graph_dir / f"{ticker}_dynamic_graph.json"
    if dynamic_file.exists():
        dynamic_graph = load_graph_file(dynamic_file)
        loader.load_dynamic_graph(ticker, dynamic_graph)
    
    # 통계 출력
    print("\n=== Load Statistics ===")
    stats = loader.get_stats()
    for key, value in stats.items():
        print(f"  {key}: {value}")
    
    # 검증
    print("\n=== Verification ===")
    verify = loader.verify()
    print(f"  Total Nodes: {verify['total_nodes']}")
    print(f"  Total Links: {verify['total_links']}")
    print(f"  Total Embeddings: {verify['total_embeddings']}")
    
    loader.close()


if __name__ == "__main__":
    main()

