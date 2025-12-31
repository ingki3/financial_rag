"""SEC 공시 파일에서 주요 섹션을 추출하는 모듈"""
import re
import logging
from pathlib import Path
from typing import Dict, List, Optional, Tuple
from bs4 import BeautifulSoup
from dataclasses import dataclass, asdict

logger = logging.getLogger(__name__)


@dataclass
class FilingMetadata:
    """공시 메타데이터"""
    ticker: str
    filing_type: str
    accession_number: str
    file_path: str
    text_length: int


@dataclass
class ParsedFiling:
    """파싱된 공시 데이터"""
    metadata: FilingMetadata
    sections: Dict[str, str]
    full_text: str
    
    def to_dict(self) -> dict:
        return {
            "metadata": asdict(self.metadata),
            "sections": self.sections,
            "full_text_preview": self.full_text[:1000] + "..." if len(self.full_text) > 1000 else self.full_text
        }


class FilingParser:
    """10-K, 10-Q, 8-K 파일에서 주요 섹션을 추출하는 클래스"""

    # 공시 유형별 섹션 패턴 (시작 패턴, 종료 패턴)
    SECTION_PATTERNS = {
        "10-K": {
            "business": (
                r"item\s*1\.?\s*[-–—]?\s*business",
                r"item\s*1a\.?\s*[-–—]?\s*risk\s*factors"
            ),
            "risk_factors": (
                r"item\s*1a\.?\s*[-–—]?\s*risk\s*factors",
                r"item\s*1b\.?\s*[-–—]?\s*unresolved|item\s*2\.?\s*[-–—]?\s*properties"
            ),
            "mda": (
                r"item\s*7\.?\s*[-–—]?\s*management",
                r"item\s*7a\.?\s*[-–—]?\s*quantitative|item\s*8\.?\s*[-–—]?\s*financial"
            ),
        },
        "10-Q": {
            "financial_statements": (
                r"item\s*1\.?\s*[-–—]?\s*financial\s*statements",
                r"item\s*2\.?\s*[-–—]?\s*management"
            ),
            "mda": (
                r"item\s*2\.?\s*[-–—]?\s*management",
                r"item\s*3\.?\s*[-–—]?\s*quantitative|item\s*4\.?\s*[-–—]?\s*controls"
            ),
            "risk_factors": (
                r"item\s*1a\.?\s*[-–—]?\s*risk\s*factors",
                r"item\s*2\.?\s*[-–—]?\s*unregistered|item\s*6\.?\s*[-–—]?\s*exhibits"
            ),
        },
        "8-K": {
            "results_operations": (
                r"item\s*2\.02",
                r"item\s*[2-9]\.[0-9]|signature"
            ),
            "other_events": (
                r"item\s*8\.01",
                r"item\s*[8-9]\.[0-9]|signature"
            ),
            "financial_exhibits": (
                r"item\s*9\.01",
                r"signature"
            ),
        },
    }

    # 주요 파일 패턴 (primary document)
    PRIMARY_FILE_PATTERNS = [
        r".*-\d{8}\.htm$",  # aapl-20240928.htm
        r".*10k.*\.htm$",
        r".*10q.*\.htm$",
        r".*8k.*\.htm$",
        r"full-submission\.txt$",
    ]

    def __init__(self, filing_dir: Path, filing_type: str, ticker: str):
        """
        Args:
            filing_dir: 공시 폴더 경로 (예: data/AAPL/10-K/0000320193-24-000123/)
            filing_type: 공시 유형 (10-K, 10-Q, 8-K)
            ticker: 종목 티커
        """
        self.filing_dir = Path(filing_dir)
        self.filing_type = filing_type
        self.ticker = ticker
        self.content: Optional[str] = None
        self.raw_html: Optional[str] = None
        self.primary_file: Optional[Path] = None

    def find_primary_file(self) -> Optional[Path]:
        """주요 문서 파일 찾기"""
        if not self.filing_dir.exists():
            return None

        # 모든 htm/html 파일 찾기
        htm_files = list(self.filing_dir.glob("*.htm")) + list(self.filing_dir.glob("*.html"))
        
        if not htm_files:
            # txt 파일 시도
            txt_files = list(self.filing_dir.glob("*.txt"))
            if txt_files:
                return max(txt_files, key=lambda f: f.stat().st_size)
            return None

        # 가장 큰 파일 선택 (보통 주요 문서)
        primary = max(htm_files, key=lambda f: f.stat().st_size)
        return primary

    def load(self) -> "FilingParser":
        """파일 로드 및 HTML 파싱"""
        self.primary_file = self.find_primary_file()
        
        if not self.primary_file:
            logger.warning(f"Primary file not found in {self.filing_dir}")
            self.content = ""
            return self

        try:
            with open(self.primary_file, 'r', encoding='utf-8', errors='ignore') as f:
                self.raw_html = f.read()

            soup = BeautifulSoup(self.raw_html, 'lxml')
            
            # 불필요한 태그 제거
            for tag in soup(["script", "style", "meta", "link"]):
                tag.decompose()

            # 텍스트 추출 및 정리
            self.content = soup.get_text(separator='\n')
            self.content = self._clean_text(self.content)
            
        except Exception as e:
            logger.error(f"Error loading {self.primary_file}: {e}")
            self.content = ""

        return self

    def _clean_text(self, text: str) -> str:
        """텍스트 정리"""
        # 연속된 공백/줄바꿈 정리
        text = re.sub(r'\n\s*\n', '\n\n', text)
        text = re.sub(r' +', ' ', text)
        # 앞뒤 공백 제거
        text = '\n'.join(line.strip() for line in text.split('\n'))
        return text.strip()

    def extract_section(self, section_name: str) -> str:
        """특정 섹션의 텍스트 추출"""
        if not self.content:
            return ""

        patterns = self.SECTION_PATTERNS.get(self.filing_type, {})
        pattern_tuple = patterns.get(section_name)
        
        if not pattern_tuple:
            return ""

        start_pattern, end_pattern = pattern_tuple

        # 섹션 시작 찾기
        start_match = re.search(start_pattern, self.content, re.IGNORECASE)
        if not start_match:
            return ""

        start_pos = start_match.start()

        # 섹션 끝 찾기
        end_match = re.search(end_pattern, self.content[start_pos + 100:], re.IGNORECASE)
        if end_match:
            end_pos = start_pos + 100 + end_match.start()
        else:
            # 끝을 찾지 못하면 최대 100k 문자
            end_pos = min(start_pos + 100000, len(self.content))

        section_text = self.content[start_pos:end_pos]
        
        # 너무 짧으면 빈 문자열 반환 (오탐 방지)
        if len(section_text) < 100:
            return ""

        return section_text

    def extract_all_sections(self) -> Dict[str, str]:
        """현재 공시 유형의 모든 주요 섹션 추출"""
        patterns = self.SECTION_PATTERNS.get(self.filing_type, {})
        sections = {}
        
        for section_name in patterns.keys():
            section_text = self.extract_section(section_name)
            if section_text:
                sections[section_name] = section_text
                logger.debug(f"Extracted {section_name}: {len(section_text)} chars")

        return sections

    def get_accession_number(self) -> str:
        """Accession Number 추출 (폴더명에서)"""
        return self.filing_dir.name

    def parse(self) -> ParsedFiling:
        """전체 파싱 수행"""
        self.load()
        
        sections = self.extract_all_sections()
        
        metadata = FilingMetadata(
            ticker=self.ticker,
            filing_type=self.filing_type,
            accession_number=self.get_accession_number(),
            file_path=str(self.primary_file) if self.primary_file else "",
            text_length=len(self.content) if self.content else 0
        )
        
        return ParsedFiling(
            metadata=metadata,
            sections=sections,
            full_text=self.content or ""
        )


class FilingParserBatch:
    """여러 공시를 일괄 파싱하는 클래스"""

    TICKERS = ["AAPL", "AMZN", "TSLA", "GOOGL", "MSFT", "META", "NVDA"]
    FILING_TYPES = ["10-K", "10-Q", "8-K"]

    def __init__(self, data_dir: str = "./data/raw"):
        self.data_dir = Path(data_dir)

    def get_filing_dirs(self, ticker: str, filing_type: str) -> List[Path]:
        """특정 티커와 공시 유형의 모든 공시 폴더 반환"""
        base_dir = self.data_dir / ticker / filing_type
        if not base_dir.exists():
            return []
        
        # accession number 폴더들
        dirs = [d for d in base_dir.iterdir() if d.is_dir()]
        return sorted(dirs)

    def parse_all(self) -> List[ParsedFiling]:
        """모든 공시 파싱"""
        results = []
        
        for ticker in self.TICKERS:
            for filing_type in self.FILING_TYPES:
                filing_dirs = self.get_filing_dirs(ticker, filing_type)
                
                for filing_dir in filing_dirs:
                    try:
                        parser = FilingParser(filing_dir, filing_type, ticker)
                        parsed = parser.parse()
                        
                        if parsed.metadata.text_length > 0:
                            results.append(parsed)
                            logger.info(
                                f"✅ {ticker}/{filing_type}/{parsed.metadata.accession_number}: "
                                f"{len(parsed.sections)} sections, {parsed.metadata.text_length:,} chars"
                            )
                        else:
                            logger.warning(
                                f"⚠️ {ticker}/{filing_type}/{filing_dir.name}: No content found"
                            )
                    except Exception as e:
                        logger.error(f"❌ Error parsing {filing_dir}: {e}")

        return results

    def get_summary(self, results: List[ParsedFiling]) -> Dict:
        """파싱 결과 요약"""
        summary = {
            "total_filings": len(results),
            "by_ticker": {},
            "by_type": {},
            "sections_extracted": 0,
            "total_text_length": 0
        }
        
        for parsed in results:
            ticker = parsed.metadata.ticker
            ftype = parsed.metadata.filing_type
            
            summary["by_ticker"][ticker] = summary["by_ticker"].get(ticker, 0) + 1
            summary["by_type"][ftype] = summary["by_type"].get(ftype, 0) + 1
            summary["sections_extracted"] += len(parsed.sections)
            summary["total_text_length"] += parsed.metadata.text_length

        return summary

