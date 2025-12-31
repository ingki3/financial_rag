"""
FastAPI Dependencies

의존성 주입을 위한 서비스 인스턴스 관리
"""

import os
import logging
from functools import lru_cache
from typing import Optional
from dotenv import load_dotenv

from app.services.query.query_engine import QueryEngine
from app.services.graph.graph_loader import GraphLoader
from app.services.download.sec_downloader import SECFilingDownloader
from app.services.processing.document_processor import DocumentProcessor
from app.services.processing.duplicate_checker import DuplicateChecker

load_dotenv()

logger = logging.getLogger(__name__)


@lru_cache()
def get_query_engine() -> QueryEngine:
    """
    QueryEngine 싱글톤 인스턴스 반환
    
    Returns:
        QueryEngine 인스턴스
    """
    logger.info("Initializing QueryEngine...")
    return QueryEngine()


@lru_cache()
def get_graph_loader() -> GraphLoader:
    """
    GraphLoader 싱글톤 인스턴스 반환
    
    Returns:
        GraphLoader 인스턴스
    """
    logger.info("Initializing GraphLoader...")
    graph_name = os.getenv("FALKORDB_GRAPH_NAME", "financial_kg")
    loader = GraphLoader(graph_name=graph_name)
    loader.connect()
    loader.initialize()
    return loader


def get_downloader() -> SECFilingDownloader:
    """
    SECFilingDownloader 인스턴스 반환
    
    Returns:
        SECFilingDownloader 인스턴스
    """
    user_agent = os.getenv("SEC_USER_AGENT", "FinancialKG user@example.com")
    data_dir = os.getenv("DATA_DIR", "./data/raw")
    return SECFilingDownloader(data_dir=data_dir, user_agent=user_agent)


def get_document_processor() -> DocumentProcessor:
    """
    DocumentProcessor 인스턴스 반환
    
    Returns:
        DocumentProcessor 인스턴스
    """
    graph_loader = get_graph_loader()
    duplicate_checker = DuplicateChecker(graph_loader)
    data_dir = os.getenv("DATA_DIR", "./data")
    
    return DocumentProcessor(
        graph_loader=graph_loader,
        duplicate_checker=duplicate_checker,
        data_dir=data_dir
    )

