"""Graphiti를 활용한 FalkorDB Knowledge Graph 관리 모듈"""
import os
import json
import logging
import asyncio
from pathlib import Path
from datetime import datetime
from typing import Dict, List, Optional
from dataclasses import dataclass

from graphiti_core import Graphiti
from graphiti_core.llm_client.gemini_client import GeminiClient, LLMConfig
from graphiti_core.embedder.gemini import GeminiEmbedder, GeminiEmbedderConfig
from graphiti_core.cross_encoder.gemini_reranker_client import GeminiRerankerClient
from graphiti_core.utils.bulk_utils import RawEpisode
from graphiti_core.nodes import EpisodeType

from app.services.graph.falkor_driver_ext import FalkorDriverWithTimeout
from app.services.shared.gemini_client_strict import GeminiClientStrict

logger = logging.getLogger(__name__)


@dataclass
class EpisodeData:
    """Episode 저장용 데이터"""
    name: str
    body: str
    source: str
    reference_time: datetime
    group_id: str


class GraphitiManager:
    """Graphiti + FalkorDB 기반 Knowledge Graph 관리 클래스"""

    def __init__(
        self,
        host: str = "localhost",
        port: int = 6379,  # FalkorDB Redis 포트
        database: str = "default_db",
        gemini_api_key: Optional[str] = None,
        model: str = "gemini-3-flash-preview",
        max_coroutines: int = 1,  # "Max pending queries exceeded" 에러를 줄이기 위해 최소값으로 설정
        falkordb_query_timeout_ms: int = 120_000,
    ):
        """
        Args:
            host: FalkorDB 호스트
            port: FalkorDB 포트
            database: FalkorDB Graph(=database) 이름 (multi-tenant)
            gemini_api_key: Gemini API 키
            model: Gemini 모델명
        """
        self.host = host
        self.port = port
        self.database = database
        self.api_key = gemini_api_key or os.getenv("GEMINI_API_KEY")
        self.model = model
        self.max_coroutines = max_coroutines
        self.falkordb_query_timeout_ms = falkordb_query_timeout_ms
        self.graphiti: Optional[Graphiti] = None

    async def initialize(self):
        """Graphiti 초기화 및 인덱스 생성"""
        logger.info(
            f"Initializing Graphiti with FalkorDB at {self.host}:{self.port} (db={self.database})"
        )
        
        # Gemini "thought" 출력 방지: structured output 파싱 실패를 크게 줄임
        from google.genai import types
        thinking_config = types.ThinkingConfig(includeThoughts=False, thinkingBudget=0)

        # Gemini 클라이언트 설정
        llm_config = LLMConfig(
            api_key=self.api_key,
            model=self.model
        )
        
        embedder_config = GeminiEmbedderConfig(
            api_key=self.api_key,
            # graphiti_core 기본값(예: embedding-001)을 그대로 쓰고 싶으면 이 줄을 제거해도 됩니다.
            embedding_model="embedding-001"
        )
        
        # Graphiti 초기화 (FalkorDB 연결)
        # 핵심: Neo4j(Bolt URI) 대신 FalkorDriver를 graph_driver로 전달
        driver = FalkorDriverWithTimeout(
            host=self.host,
            port=self.port,
            database=self.database,
            query_timeout_ms=self.falkordb_query_timeout_ms,
        )
        self.graphiti = Graphiti(
            graph_driver=driver,
            llm_client=GeminiClientStrict(config=llm_config, thinking_config=thinking_config),
            embedder=GeminiEmbedder(config=embedder_config),
            cross_encoder=GeminiRerankerClient(config=llm_config),
            max_coroutines=self.max_coroutines,
        )
        
        # 인덱스 및 제약조건 생성
        await self.graphiti.build_indices_and_constraints()
        logger.info("✅ Graphiti initialized successfully")

    async def close(self):
        """연결 종료"""
        if self.graphiti:
            await self.graphiti.close()
            logger.info("Graphiti connection closed")

    async def add_episode(self, episode: EpisodeData) -> bool:
        """단일 Episode 추가
        
        Returns:
            성공 여부
        """
        if not self.graphiti:
            raise RuntimeError("Graphiti not initialized. Call initialize() first.")
        
        # Failover: transient DB/backpressure issues can happen during Graphiti's internal queries
        # (e.g., fulltext lookups). We retry with exponential backoff on transient errors.
        # "Max pending queries exceeded" 에러를 줄이기 위해 기본 대기 시간 대폭 증가
        max_attempts = int(os.getenv("GRAPHITI_EPISODE_MAX_ATTEMPTS", "5"))
        base_sleep = float(os.getenv("GRAPHITI_EPISODE_RETRY_BASE_SLEEP", "10.0"))  # 5.0 → 10.0으로 증가

        last_err: Exception | None = None
        for attempt in range(1, max_attempts + 1):
            try:
                await self.graphiti.add_episode(
                    name=episode.name,
                    episode_body=episode.body,
                    source_description=episode.source,
                    reference_time=episode.reference_time,
                    group_id=episode.group_id,
                )
                return True
            except Exception as e:
                last_err = e
                msg = str(e)
                msg_l = msg.lower()
                is_transient = (
                    "timed out" in msg_l
                    or "timeout" in msg_l
                    or "max pending queries exceeded" in msg_l
                    or "too many pending" in msg_l
                    or "resource exhausted" in msg_l
                    or "temporarily unavailable" in msg_l
                )
                logger.error(f"Failed to add episode '{episode.name}' (attempt {attempt}/{max_attempts}): {e}")
                if attempt >= max_attempts or not is_transient:
                    break
                sleep_s = base_sleep * (2 ** (attempt - 1))
                if "max pending queries exceeded" in msg_l:
                    sleep_s *= 3.0  # Max pending 에러 시 추가 200% 대기 시간
                    logger.warning(f"Max pending queries exceeded - waiting {sleep_s:.1f}s before retry")
                await asyncio.sleep(sleep_s)

        # final failure
        return False

    async def add_extracted_triplets(
        self,
        triplets_file: Path,
        delay: float = 0.0  # delay는 더 이상 사용하지 않지만 호환성을 위해 유지
    ) -> Dict[str, int]:
        """추출된 Triplets JSON 파일을 Episode로 저장 (Bulk API 사용)
        
        Args:
            triplets_file: 추출된 triplets JSON 파일 경로
            delay: 사용하지 않음 (호환성을 위해 유지)
            
        Returns:
            카테고리별 저장된 Episode 수
        """
        if not self.graphiti:
            raise RuntimeError("Graphiti not initialized. Call initialize() first.")
        
        with open(triplets_file, 'r', encoding='utf-8') as f:
            data = json.load(f)
        
        ticker = data.get("ticker", "")
        filing_type = data.get("filing_type", "")
        accession = data.get("accession_number", "")
        section = data.get("section", "")
        
        # 연도 추출 (accession number에서)
        year = self._extract_year_from_accession(accession)
        ref_time = datetime(year, 12, 31) if year else datetime.now()
        
        source_base = f"SEC {filing_type} - {ticker} ({year}), Section: {section}"
        
        stats = {
            "opportunities": 0,
            "risks": 0,
            "events": 0,
            "strategies": 0,
            "financials": 0
        }

        failures: list[dict] = []
        
        # 모든 episode를 RawEpisode 리스트로 변환
        bulk_episodes: list[RawEpisode] = []
        episode_categories: list[str] = []  # 각 episode의 카테고리 추적
        
        # Opportunities
        for item in data.get("opportunities", []):
            bulk_episodes.append(
                RawEpisode(
                    name=f"{ticker} Opportunity: {item['entity']}",
                    content=f"{item['entity']}: {item['description']}",
                    source_description=source_base,
                    source=EpisodeType.message,
                    reference_time=ref_time
                )
            )
            episode_categories.append("opportunities")
        
        # Risks
        for item in data.get("risks", []):
            bulk_episodes.append(
                RawEpisode(
                    name=f"{ticker} Risk: {item['entity']}",
                    content=f"{item['entity']}: {item['description']}",
                    source_description=source_base,
                    source=EpisodeType.message,
                    reference_time=ref_time
                )
            )
            episode_categories.append("risks")
        
        # Events
        for item in data.get("events", []):
            event_date = item.get("date", "")
            event_time = self._parse_date(event_date) or ref_time
            
            bulk_episodes.append(
                RawEpisode(
                    name=f"{ticker} Event: {item['entity']}",
                    content=f"{item['entity']} ({event_date}): {item['description']}",
                    source_description=source_base,
                    source=EpisodeType.message,
                    reference_time=event_time
                )
            )
            episode_categories.append("events")
        
        # Strategies
        for item in data.get("strategies", []):
            bulk_episodes.append(
                RawEpisode(
                    name=f"{ticker} Strategy: {item['entity']}",
                    content=f"{item['entity']}: {item['description']}",
                    source_description=source_base,
                    source=EpisodeType.message,
                    reference_time=ref_time
                )
            )
            episode_categories.append("strategies")
        
        # Financials
        for item in data.get("financials", []):
            period = item.get("period", "")
            bulk_episodes.append(
                RawEpisode(
                    name=f"{ticker} Financial: {item['metric']}",
                    content=f"{item['metric']}: {item['value']} ({period})",
                    source_description=source_base,
                    source=EpisodeType.message,
                    reference_time=ref_time
                )
            )
            episode_categories.append("financials")
        
        # "Max pending queries exceeded" 에러를 줄이기 위해 bulk 대신 개별 episode로 처리
        # 각 episode 사이에 delay를 두어 DB 부하를 분산
        if bulk_episodes:
            episode_delay = float(os.getenv("GRAPHITI_EPISODE_DELAY", "0.5"))  # 각 episode 사이 delay (초)
            total_episodes = len(bulk_episodes)
            
            logger.info(f"Processing {total_episodes} episodes individually (with {episode_delay}s delay between each)")
            
            for i, raw_episode in enumerate(bulk_episodes):
                category = episode_categories[i]
                episode = EpisodeData(
                    name=raw_episode.name,
                    body=raw_episode.content,
                    source=raw_episode.source_description,
                    reference_time=raw_episode.reference_time,
                    group_id=ticker
                )
                
                if await self.add_episode(episode):
                    stats[category] += 1
                    if (i + 1) % 10 == 0:
                        logger.info(f"Progress: {i + 1}/{total_episodes} episodes processed")
                else:
                    failures.append({"category": category, "name": episode.name})
                
                # 각 episode 사이에 delay (마지막 episode는 제외)
                if i < total_episodes - 1 and episode_delay > 0:
                    await asyncio.sleep(episode_delay)
            
            logger.info(f"Completed processing {total_episodes} episodes: {sum(stats.values())} succeeded, {len(failures)} failed")

        # Failover 기록: 나중에 재실행/재처리할 수 있도록 파일 단위 실패 목록을 저장
        if failures:
            fail_dir = Path("./test_result/failures")
            fail_dir.mkdir(parents=True, exist_ok=True)
            fail_path = fail_dir / f"{ticker}_{filing_type}_{accession}_{section}.json"
            with open(fail_path, "w", encoding="utf-8") as f:
                json.dump(
                    {
                        "source_file": str(triplets_file),
                        "ticker": ticker,
                        "filing_type": filing_type,
                        "accession_number": accession,
                        "section": section,
                        "failures": failures,
                    },
                    f,
                    ensure_ascii=False,
                    indent=2,
                )
            logger.warning(f"Saved failure report: {fail_path} ({len(failures)} failures)")

        return stats

    def _extract_year_from_accession(self, accession: str) -> Optional[int]:
        """Accession number에서 연도 추출"""
        # 형식: 0000320193-24-000123 → 2024
        if "-" in accession:
            parts = accession.split("-")
            if len(parts) >= 2:
                year_part = parts[1]
                if len(year_part) == 2:
                    year = int(year_part)
                    return 2000 + year if year < 50 else 1900 + year
        return None

    def _parse_date(self, date_str: str) -> Optional[datetime]:
        """날짜 문자열 파싱"""
        if not date_str:
            return None
        
        formats = [
            "%Y-%m-%d",
            "%Y-%m",
            "%Y"
        ]
        
        for fmt in formats:
            try:
                return datetime.strptime(date_str[:len(fmt.replace("%", ""))], fmt)
            except ValueError:
                continue
        
        # 연도만 있는 경우
        try:
            year = int(date_str[:4])
            return datetime(year, 12, 31)
        except:
            return None

    async def search(
        self,
        query: str,
        group_ids: Optional[List[str]] = None,
        num_results: int = 10
    ) -> List[Dict]:
        """그래프 검색
        
        Args:
            query: 검색 질의
            group_ids: 필터링할 group_id 목록 (예: ["AAPL", "TSLA"])
            num_results: 반환할 결과 수
            
        Returns:
            검색 결과 목록
        """
        if not self.graphiti:
            raise RuntimeError("Graphiti not initialized")
        
        results = await self.graphiti.search(
            query=query,
            group_ids=group_ids,
            num_results=num_results
        )
        
        return results


class GraphitiPopulator:
    """Graphiti에 추출된 데이터를 일괄 저장하는 클래스"""

    TICKERS = ["AAPL", "AMZN", "TSLA", "GOOGL", "MSFT", "META", "NVDA"]

    def __init__(
        self,
        extracted_dir: str = "./data/extracted",
        host: str = "localhost",
        port: int = 6379,
        database: str = "default_db",
    ):
        self.extracted_dir = Path(extracted_dir)
        # DB(그래프)는 하나로 유지하고, 저장만 티커 단위로 순차 처리
        self.manager = GraphitiManager(host=host, port=port, database=database)

    def get_ticker_files(self, ticker: str) -> List[Path]:
        """특정 티커의 모든 추출 파일 반환"""
        ticker_dir = self.extracted_dir / ticker
        if not ticker_dir.exists():
            return []
        
        files = []
        for filing_type in ["10-K", "10-Q", "8-K"]:
            type_dir = ticker_dir / filing_type
            if type_dir.exists():
                files.extend(sorted(type_dir.glob("*.json")))
        
        return files

    async def populate_ticker(self, ticker: str) -> Dict[str, int]:
        """특정 티커의 모든 데이터 저장
        
        Returns:
            저장 통계
        """
        await self.manager.initialize()
        
        files = self.get_ticker_files(ticker)
        total_stats = {
            "files_processed": 0,
            "opportunities": 0,
            "risks": 0,
            "events": 0,
            "strategies": 0,
            "financials": 0,
            "total_episodes": 0
        }
        
        logger.info(f"Processing {len(files)} files for {ticker}")
        
        for file_path in files:
            try:
                logger.info(f"  Processing: {file_path.name}")
                stats = await self.manager.add_extracted_triplets(file_path, delay=0.0)
                
                total_stats["files_processed"] += 1
                for key in ["opportunities", "risks", "events", "strategies", "financials"]:
                    total_stats[key] += stats.get(key, 0)
                total_stats["total_episodes"] += sum(stats.values())
                
                logger.info(f"    → Saved {sum(stats.values())} episodes")
                
            except Exception as e:
                logger.error(f"  Error processing {file_path}: {e}")
        
        await self.manager.close()
        return total_stats

    async def populate_all(self) -> Dict[str, Dict[str, int]]:
        """모든 티커 데이터 저장"""
        all_stats = {}
        
        for ticker in self.TICKERS:
            logger.info(f"\n{'='*50}")
            logger.info(f"Populating {ticker}")
            logger.info(f"{'='*50}")
            
            stats = await self.populate_ticker(ticker)
            all_stats[ticker] = stats
        
        return all_stats

