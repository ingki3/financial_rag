"""
Document Processor Service

문서 처리 파이프라인 오케스트레이터
다운로드된 공시 문서를 파싱, 추출, 그래프 생성, DB 적재까지 처리
"""

import logging
import json
from pathlib import Path
from typing import Dict, List, Optional
from datetime import datetime

from app.services.processing.filing_parser import FilingParser, FilingParserBatch
from app.services.processing.triplet_extractor import TripletExtractor
from app.services.processing.graph_generator import generate_static_graph
from app.services.processing.dynamic_graph_generator import generate_dynamic_graph
from app.services.processing.duplicate_checker import DuplicateChecker
from app.services.graph.graph_loader import GraphLoader

logger = logging.getLogger(__name__)


class DocumentProcessor:
    """문서 처리 파이프라인 오케스트레이터"""
    
    def __init__(
        self,
        parser_batch: Optional[FilingParserBatch] = None,
        extractor: Optional[TripletExtractor] = None,
        graph_loader: Optional[GraphLoader] = None,
        duplicate_checker: Optional[DuplicateChecker] = None,
        data_dir: str = "./data"
    ):
        """
        DocumentProcessor 초기화
        
        Args:
            parser_batch: FilingParserBatch 인스턴스
            extractor: TripletExtractor 인스턴스
            graph_loader: GraphLoader 인스턴스
            duplicate_checker: DuplicateChecker 인스턴스
            data_dir: 데이터 디렉토리 경로
        """
        self.data_dir = Path(data_dir)
        self.raw_dir = self.data_dir / "raw"
        self.extracted_dir = self.data_dir / "extracted"
        self.graph_dir = self.data_dir / "graph"
        
        # 서비스 인스턴스
        self.parser_batch = parser_batch or FilingParserBatch(data_dir=str(self.raw_dir))
        self.extractor = extractor or TripletExtractor()
        
        if graph_loader:
            self.graph_loader = graph_loader
            self.duplicate_checker = duplicate_checker or DuplicateChecker(graph_loader)
        else:
            self.graph_loader = None
            self.duplicate_checker = None
    
    def process_ticker(
        self,
        ticker: str,
        skip_duplicates: bool = True,
        with_embedding: bool = True,
        filing_types: Optional[List[str]] = None
    ) -> Dict:
        """
        티커의 모든 문서 처리 및 Graph DB 적재
        
        프로세스:
        1. 다운로드된 파일 목록 조회
        2. 중복 체크 (skip_duplicates=True인 경우)
        3. 각 파일에 대해:
           - 파싱 (FilingParser)
           - 트리플렛 추출 (TripletExtractor)
           - Static/Dynamic Graph 생성 (GraphGenerator)
           - Graph DB 적재 (GraphLoader)
        4. 통계 반환
        
        Args:
            ticker: 티커 심볼
            skip_duplicates: 중복 문서 건너뛰기 여부
            with_embedding: Embedding 생성 여부
            filing_types: 처리할 공시 유형 리스트 (None이면 모든 유형)
        
        Returns:
            처리 통계 딕셔너리
        """
        ticker = ticker.upper()
        logger.info(f"Processing documents for {ticker}...")
        
        stats = {
            "ticker": ticker,
            "processed_files": 0,
            "skipped_files": 0,
            "errors": 0,
            "graph_stats": {}
        }
        
        # 처리할 공시 유형
        if filing_types is None:
            filing_types = ["10-K", "10-Q", "8-K"]
        
        # 1. 다운로드된 파일 목록 조회
        filing_dirs = []
        for filing_type in filing_types:
            dirs = self.parser_batch.get_filing_dirs(ticker, filing_type)
            filing_dirs.extend(dirs)
        
        if not filing_dirs:
            logger.warning(f"No filing directories found for {ticker}")
            return stats
        
        logger.info(f"Found {len(filing_dirs)} filing directories for {ticker}")
        
        # 2. 중복 체크
        if skip_duplicates and self.duplicate_checker:
            duplicate_map = self.duplicate_checker.check_documents(ticker, filing_dirs)
            logger.info(f"Duplicate check: {sum(duplicate_map.values())} duplicates found")
        else:
            duplicate_map = {filing_dir: False for filing_dir in filing_dirs}
        
        # 3. 각 파일 처리
        processed_extracted_files = []
        
        for filing_dir in filing_dirs:
            if duplicate_map.get(filing_dir, False):
                logger.info(f"Skipping duplicate: {filing_dir}")
                stats["skipped_files"] += 1
                continue
            
            try:
                # 파싱
                filing_type = filing_dir.parent.name
                parser = FilingParser(filing_dir, filing_type, ticker)
                parsed = parser.parse()
                
                if parsed.metadata.text_length == 0:
                    logger.warning(f"No content in {filing_dir}")
                    continue
                
                # 트리플렛 추출
                extracted_file = self._extract_triplets(parsed, ticker, filing_type)
                if extracted_file:
                    processed_extracted_files.append(extracted_file)
                    stats["processed_files"] += 1
                else:
                    stats["errors"] += 1
                    
            except Exception as e:
                logger.error(f"Error processing {filing_dir}: {e}")
                stats["errors"] += 1
        
        # 4. Static Graph 생성 및 적재
        if processed_extracted_files:
            try:
                static_graph = generate_static_graph(ticker, processed_extracted_files)
                static_graph_file = self.graph_dir / f"{ticker}_static_graph.json"
                static_graph_file.parent.mkdir(parents=True, exist_ok=True)
                
                with open(static_graph_file, 'w', encoding='utf-8') as f:
                    json.dump(static_graph, f, ensure_ascii=False, indent=2)
                
                logger.info(f"Static graph saved: {static_graph_file}")
                
                # Graph DB 적재
                if self.graph_loader:
                    self.graph_loader.load_static_graph(ticker, static_graph)
                    logger.info(f"Static graph loaded to DB for {ticker}")
                
            except Exception as e:
                logger.error(f"Error generating static graph for {ticker}: {e}")
                stats["errors"] += 1
        
        # 5. Dynamic Graph 생성 및 적재
        if processed_extracted_files:
            try:
                dynamic_graph = generate_dynamic_graph(
                    ticker,
                    processed_extracted_files,
                    static_graph,
                    with_embedding=with_embedding
                )
                dynamic_graph_file = self.graph_dir / f"{ticker}_dynamic_graph.json"
                
                with open(dynamic_graph_file, 'w', encoding='utf-8') as f:
                    json.dump(dynamic_graph, f, ensure_ascii=False, indent=2)
                
                logger.info(f"Dynamic graph saved: {dynamic_graph_file}")
                
                # Graph DB 적재
                if self.graph_loader:
                    db_stats = self.graph_loader.load_dynamic_graph(ticker, dynamic_graph)
                    stats["graph_stats"] = db_stats
                    logger.info(f"Dynamic graph loaded to DB for {ticker}")
                
            except Exception as e:
                logger.error(f"Error generating dynamic graph for {ticker}: {e}")
                stats["errors"] += 1
        
        logger.info(f"Processing complete for {ticker}: {stats}")
        return stats
    
    def _extract_triplets(
        self,
        parsed,
        ticker: str,
        filing_type: str
    ) -> Optional[Path]:
        """
        단일 파일에서 트리플렛 추출
        
        Args:
            parsed: 파싱된 공시 데이터
            ticker: 티커 심볼
            filing_type: 공시 유형
        
        Returns:
            추출된 파일 경로 (실패 시 None)
        """
        try:
            # 추출 디렉토리 생성
            extract_dir = self.extracted_dir / ticker / filing_type
            extract_dir.mkdir(parents=True, exist_ok=True)
            
            # 파일명 생성 (accession_number 기반)
            filename = f"{parsed.metadata.accession_number}.json"
            extract_file = extract_dir / filename
            
            # 이미 추출된 파일이 있으면 건너뛰기
            if extract_file.exists():
                logger.info(f"Extracted file already exists: {extract_file}")
                return extract_file
            
            # 섹션별로 추출
            extracted_data = {
                "ticker": ticker,
                "filing_type": filing_type,
                "accession_number": parsed.metadata.accession_number,
                "file_path": parsed.metadata.file_path,
                "sections": {}
            }
            
            for section_name, section_text in parsed.sections.items():
                if not section_text or len(section_text) < 100:
                    continue
                
                try:
                    triplets = self.extractor.extract_triplets_sync(section_text)
                    extracted_data["sections"][section_name] = triplets
                    logger.debug(f"Extracted triplets from {section_name}: {len(triplets.opportunities)} opps, {len(triplets.risks)} risks")
                except Exception as e:
                    logger.error(f"Error extracting triplets from {section_name}: {e}")
                    continue
            
            # JSON 저장
            with open(extract_file, 'w', encoding='utf-8') as f:
                json.dump(extracted_data, f, ensure_ascii=False, indent=2, default=str)
            
            logger.info(f"Triplets extracted: {extract_file}")
            return extract_file
            
        except Exception as e:
            logger.error(f"Error extracting triplets: {e}")
            return None
    
    def process_single_file(
        self,
        file_path: Path,
        ticker: str,
        with_embedding: bool = True
    ) -> Dict:
        """
        단일 파일 처리 (테스트용)
        
        Args:
            file_path: 공시 폴더 경로
            ticker: 티커 심볼
            with_embedding: Embedding 생성 여부
        
        Returns:
            처리 결과 딕셔너리
        """
        # 파일 경로에서 filing_type 추출
        filing_type = file_path.parent.name
        
        # 파싱
        parser = FilingParser(file_path, filing_type, ticker)
        parsed = parser.parse()
        
        if parsed.metadata.text_length == 0:
            return {"error": "No content found"}
        
        # 트리플렛 추출
        extracted_file = self._extract_triplets(parsed, ticker, filing_type)
        
        if not extracted_file:
            return {"error": "Extraction failed"}
        
        # Graph 생성은 전체 티커 단위로 처리하는 것이 효율적
        return {
            "success": True,
            "extracted_file": str(extracted_file),
            "message": "File processed. Use process_ticker() to generate graphs."
        }

