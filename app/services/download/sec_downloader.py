"""SEC EDGAR에서 10-K, 10-Q, 8-K 공시 자료를 다운로드하는 모듈"""
import logging
import time
import shutil
from pathlib import Path
from typing import List, Dict
from sec_edgar_downloader import Downloader

logger = logging.getLogger(__name__)


class SECFilingDownloader:
    """SEC EDGAR에서 10-K, 10-Q, 8-K 공시 자료를 다운로드하는 클래스"""

    TICKERS = ["AAPL", "AMZN", "TSLA", "GOOGL", "MSFT", "META", "NVDA"]

    # 공시 유형별 다운로드 설정
    FILING_TYPES: Dict[str, int] = {
        "10-K": 3,   # 연간 보고서: 최근 3년
        "10-Q": 12,  # 분기 보고서: 최근 12분기 (3년)
        "8-K": 20,   # 수시 공시: 최근 20건
    }

    def __init__(self, data_dir: str = "./data/raw", user_agent: str = None):
        self.data_dir = Path(data_dir)
        self.user_agent = user_agent or "FinancialKG user@example.com"
        
        # 이메일 추출
        email_parts = self.user_agent.split()
        email = email_parts[-1] if email_parts else "user@example.com"
        company = " ".join(email_parts[:-1]) if len(email_parts) > 1 else "FinancialKG"
        
        self.downloader = Downloader(
            company_name=company,
            email_address=email
        )

    def download_filing(self, ticker: str, filing_type: str, limit: int) -> int:
        """특정 티커의 특정 유형 공시 다운로드
        
        Returns:
            다운로드된 파일 수
        """
        logger.info(f"Downloading {filing_type} for {ticker} (limit: {limit})...")

        try:
            # sec-edgar-downloader는 자체 디렉토리 구조를 사용
            # 기본적으로 sec-edgar-filings/{ticker}/{filing_type}/ 에 저장됨
            self.downloader.get(
                filing_type,
                ticker,
                limit=limit,
                download_details=True
            )
            
            # 다운로드된 파일을 우리의 디렉토리 구조로 이동
            src_dir = Path("sec-edgar-filings") / ticker / filing_type
            dst_dir = self.data_dir / ticker / filing_type
            
            if src_dir.exists():
                dst_dir.mkdir(parents=True, exist_ok=True)
                
                # 각 filing 폴더 이동
                count = 0
                for item in src_dir.iterdir():
                    if item.is_dir():
                        dst_path = dst_dir / item.name
                        if dst_path.exists():
                            shutil.rmtree(dst_path)
                        shutil.move(str(item), str(dst_path))
                        count += 1
                
                logger.info(f"✅ {ticker} {filing_type}: {count}건 다운로드 완료")
                return count
            else:
                logger.warning(f"⚠️ {ticker} {filing_type}: 다운로드된 파일 없음")
                return 0
                
        except Exception as e:
            logger.error(f"❌ {ticker} {filing_type} 다운로드 실패: {e}")
            return 0

    def download_all_filings(self, ticker: str) -> Dict[str, int]:
        """특정 티커의 모든 유형 공시 다운로드
        
        Returns:
            공시 유형별 다운로드 수
        """
        results = {}
        for filing_type, limit in self.FILING_TYPES.items():
            count = self.download_filing(ticker, filing_type, limit)
            results[filing_type] = count
            # API 속도 제한 준수 (초당 10건 이하)
            time.sleep(1)
        return results

    def download_all(self) -> Dict[str, Dict[str, int]]:
        """모든 대상 기업의 모든 공시 다운로드
        
        Returns:
            기업별, 공시 유형별 다운로드 수
        """
        all_results = {}
        for ticker in self.TICKERS:
            logger.info(f"\n{'='*60}")
            logger.info(f"=== Downloading filings for {ticker} ===")
            logger.info(f"{'='*60}")
            results = self.download_all_filings(ticker)
            all_results[ticker] = results
            # 기업 간 간격
            time.sleep(2)
        
        return all_results

    def get_downloaded_files(self, ticker: str, filing_type: str) -> List[Path]:
        """다운로드된 파일 목록 반환"""
        filing_dir = self.data_dir / ticker / filing_type
        if not filing_dir.exists():
            return []
        
        files = []
        for ext in ["*.htm", "*.html", "*.txt"]:
            files.extend(filing_dir.glob(f"**/{ext}"))
        return files

    def get_summary(self) -> Dict[str, Dict[str, int]]:
        """다운로드된 파일 요약"""
        summary = {}
        for ticker in self.TICKERS:
            summary[ticker] = {}
            for filing_type in self.FILING_TYPES.keys():
                files = self.get_downloaded_files(ticker, filing_type)
                summary[ticker][filing_type] = len(files)
        return summary

    def cleanup_temp_dir(self):
        """임시 다운로드 디렉토리 정리"""
        temp_dir = Path("sec-edgar-filings")
        if temp_dir.exists():
            shutil.rmtree(temp_dir)
            logger.info("임시 디렉토리 정리 완료")

