"""
Duplicate Checker Service

Graph DB에 이미 적재된 문서인지 확인하는 서비스
"""

import logging
from pathlib import Path
from typing import Dict, List, Set, Optional
from app.services.graph.graph_loader import GraphLoader

logger = logging.getLogger(__name__)


class DuplicateChecker:
    """Graph DB에 이미 적재된 문서인지 확인하는 클래스"""
    
    def __init__(self, graph_loader: GraphLoader):
        """
        DuplicateChecker 초기화
        
        Args:
            graph_loader: GraphLoader 인스턴스
        """
        self.graph_loader = graph_loader
    
    def check_document(
        self,
        ticker: str,
        filing_type: str,
        accession_number: str
    ) -> bool:
        """
        문서가 이미 Graph DB에 적재되었는지 확인
        
        Document 노드의 id는 다음과 같은 형식:
        f"{ticker}_{filing_type}_{accession_number}"
        
        Args:
            ticker: 티커 심볼
            filing_type: 공시 유형 (10-K, 10-Q, 8-K)
            accession_number: Accession Number
        
        Returns:
            True: 이미 적재됨, False: 적재되지 않음
        """
        doc_id = f"{ticker}_{filing_type}_{accession_number}"
        
        try:
            cypher_query = """
            MATCH (d:Document {id: $doc_id})
            RETURN d LIMIT 1
            """
            
            result = self.graph_loader.execute_query(cypher_query, {"doc_id": doc_id})
            
            return len(result) > 0
            
        except Exception as e:
            logger.error(f"Error checking document {doc_id}: {e}")
            return False
    
    def check_documents(
        self,
        ticker: str,
        filing_dirs: List[Path]
    ) -> Dict[Path, bool]:
        """
        여러 문서의 중복 여부 일괄 확인
        
        Args:
            ticker: 티커 심볼
            filing_dirs: 공시 폴더 경로 리스트
        
        Returns:
            {file_path: is_duplicate} 딕셔너리
        """
        results = {}
        
        # 먼저 이미 처리된 문서 ID 목록을 한 번에 조회
        processed_ids = self.get_processed_documents(ticker)
        
        for filing_dir in filing_dirs:
            # 폴더명에서 filing_type과 accession_number 추출
            # 예: data/raw/AAPL/10-K/0000320193-24-000123/
            parts = filing_dir.parts
            if len(parts) >= 2:
                filing_type = parts[-2]  # 10-K, 10-Q, 8-K
                accession_number = parts[-1]  # 0000320193-24-000123
                
                doc_id = f"{ticker}_{filing_type}_{accession_number}"
                results[filing_dir] = doc_id in processed_ids
            else:
                logger.warning(f"Invalid filing directory structure: {filing_dir}")
                results[filing_dir] = False
        
        return results
    
    def get_processed_documents(
        self,
        ticker: str
    ) -> Set[str]:
        """
        티커에 대해 이미 처리된 문서 ID 목록 반환
        
        Args:
            ticker: 티커 심볼
        
        Returns:
            처리된 문서 ID 집합
        """
        try:
            cypher_query = """
            MATCH (d:Document)
            WHERE d.ticker = $ticker
            RETURN d.id
            """
            
            result = self.graph_loader.execute_query(cypher_query, {"ticker": ticker})
            
            doc_ids = {row.get("d.id") for row in result if row.get("d.id")}
            
            logger.info(f"Found {len(doc_ids)} processed documents for {ticker}")
            return doc_ids
            
        except Exception as e:
            logger.error(f"Error getting processed documents for {ticker}: {e}")
            return set()

