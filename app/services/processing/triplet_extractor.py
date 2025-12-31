"""Gemini를 활용한 Knowledge Triplet 추출 모듈"""
import json
import logging
import time
from pathlib import Path
from typing import Dict, List, Optional
from dataclasses import dataclass, asdict
from google import genai

from app.utils.prompt_loader import prompt_loader

logger = logging.getLogger(__name__)


@dataclass
class Opportunity:
    """기회 요소"""
    entity: str
    description: str


@dataclass
class Risk:
    """리스크 요소"""
    entity: str
    description: str


@dataclass
class Event:
    """주요 이벤트"""
    entity: str
    date: str
    description: str


@dataclass
class Strategy:
    """전략"""
    entity: str
    description: str


@dataclass
class Financial:
    """재무 지표"""
    metric: str
    value: str
    period: str


@dataclass
class ExtractedTriplets:
    """추출된 Knowledge Triplets"""
    ticker: str
    filing_type: str
    accession_number: str
    section: str
    opportunities: List[Dict]
    risks: List[Dict]
    events: List[Dict]
    technologies: List[Dict]  # 새로 추가
    strategies: List[Dict]
    financials: List[Dict]
    
    def to_dict(self) -> dict:
        return asdict(self)
    
    def total_count(self) -> int:
        return (
            len(self.opportunities) + 
            len(self.risks) + 
            len(self.events) + 
            len(self.technologies) +  # 새로 추가
            len(self.strategies) + 
            len(self.financials)
        )


class TripletExtractor:
    """Gemini를 활용한 Knowledge Triplet 추출 클래스"""
    def _render_prompt(self, prompt_name: str, **kwargs: object) -> str:
        """
        Renders a YAML prompt template using a simple {{var}} replacement.
        This avoids escaping JSON braces inside YAML (unlike str.format()).
        """
        prompt_data = prompt_loader.load_prompt(prompt_name)
        template = prompt_data.get("template")
        if not isinstance(template, str) or not template.strip():
            raise ValueError(f"Prompt '{prompt_name}' missing a non-empty 'template' field.")

        rendered = template
        for k, v in kwargs.items():
            rendered = rendered.replace(f"{{{{{k}}}}}", str(v))
        return rendered

    def __init__(
        self,
        model: str = "gemini-3-flash-preview",
        api_key: Optional[str] = None,
        max_chunk_size: int = 30000
    ):
        """
        Args:
            model: Gemini 모델명 (기본: gemini-3-flash-preview)
            api_key: Gemini API 키 (없으면 환경변수에서 로드)
            max_chunk_size: 최대 청크 크기 (문자 수)
        """
        self.model = model
        self.max_chunk_size = max_chunk_size
        
        # Gemini 클라이언트 초기화
        if api_key:
            self.client = genai.Client(api_key=api_key)
        else:
            self.client = genai.Client()

    def _chunk_text(self, text: str) -> List[str]:
        """긴 텍스트를 청크로 분할"""
        if len(text) <= self.max_chunk_size:
            return [text]
        
        chunks = []
        # 문단 단위로 분할 시도
        paragraphs = text.split('\n\n')
        current_chunk = ""
        
        for para in paragraphs:
            if len(current_chunk) + len(para) + 2 <= self.max_chunk_size:
                current_chunk += para + "\n\n"
            else:
                if current_chunk:
                    chunks.append(current_chunk.strip())
                current_chunk = para + "\n\n"
        
        if current_chunk:
            chunks.append(current_chunk.strip())
        
        return chunks

    def extract(
        self,
        text: str,
        ticker: str,
        filing_type: str,
        section: str,
        accession_number: str = ""
    ) -> ExtractedTriplets:
        """텍스트에서 Knowledge Triplets 추출
        
        Args:
            text: 추출 대상 텍스트
            ticker: 기업 티커
            filing_type: 공시 유형 (10-K, 10-Q, 8-K)
            section: 섹션명 (business, risk_factors, mda 등)
            accession_number: SEC Accession Number
            
        Returns:
            ExtractedTriplets 객체
        """
        if not text or len(text) < 100:
            logger.warning(f"Text too short for extraction: {len(text)} chars")
            return ExtractedTriplets(
                ticker=ticker,
                filing_type=filing_type,
                accession_number=accession_number,
                section=section,
                opportunities=[],
                risks=[],
                events=[],
                technologies=[],
                strategies=[],
                financials=[]
            )

        # 텍스트 청킹
        chunks = self._chunk_text(text)
        logger.info(f"Processing {len(chunks)} chunk(s) for {ticker}/{filing_type}/{section}")

        all_results = {
            "opportunities": [],
            "risks": [],
            "events": [],
            "technologies": [],
            "strategies": [],
            "financials": [],
            "mentioned_products_global": [],
            "mentioned_persons_global": []
        }

        for i, chunk in enumerate(chunks):
            try:
                chunk_result = self._extract_from_chunk(
                    chunk, ticker, filing_type, section
                )
                
                # 결과 병합
                for key in all_results:
                    if key in chunk_result:
                        if key in ["mentioned_products_global", "mentioned_persons_global"]:
                            all_results[key].extend(chunk_result.get(key, []))
                        else:
                            all_results[key].extend(chunk_result.get(key, []))
                
                # Rate limiting
                if i < len(chunks) - 1:
                    time.sleep(1)
                    
            except Exception as e:
                logger.error(f"Error extracting from chunk {i+1}: {e}")
                continue

        # 중복 제거 (entity 기준)
        for key in ["opportunities", "risks", "events", "technologies", "strategies", "financials"]:
            seen = set()
            unique = []
            for item in all_results[key]:
                entity = item.get("entity", item.get("metric", ""))
                if entity and entity not in seen:
                    seen.add(entity)
                    unique.append(item)
            all_results[key] = unique[:10]  # 최대 10개
        
        # Global 목록 중복 제거는 _combine_sections에서 처리
        # ExtractedTriplets에는 global 필드를 제외하고 전달
        triplets_data = {
            k: v for k, v in all_results.items() 
            if k not in ["mentioned_products_global", "mentioned_persons_global"]
        }

        return ExtractedTriplets(
            ticker=ticker,
            filing_type=filing_type,
            accession_number=accession_number,
            section=section,
            **triplets_data
        )

    def _extract_from_chunk(
        self,
        text: str,
        ticker: str,
        filing_type: str,
        section: str
    ) -> Dict:
        """단일 청크에서 추출"""
        prompt = self._render_prompt(
            "triplet_extractor",
            ticker=ticker,
            filing_type=filing_type,
            section=section,
            text=text[: self.max_chunk_size],
        )

        try:
            response = self.client.models.generate_content(
                model=self.model,
                contents=prompt,
                config={
                    "response_mime_type": "application/json"
                }
            )
            
            result_text = response.text.strip()
            
            # JSON 파싱
            result = json.loads(result_text)
            return result
            
        except json.JSONDecodeError as e:
            logger.error(f"JSON parsing error: {e}")
            logger.debug(f"Response text: {response.text[:500]}")
            return {}
        except Exception as e:
            logger.error(f"Gemini API error: {e}")
            return {}


class TripletExtractorBatch:
    """여러 공시에서 Triplets를 일괄 추출하는 클래스"""

    TICKERS = ["AAPL", "AMZN", "TSLA", "GOOGL", "MSFT", "META", "NVDA"]
    FILING_TYPES = ["10-K", "10-Q", "8-K"]
    
    # 추출 대상 섹션 (파싱된 섹션 중)
    TARGET_SECTIONS = {
        "10-K": ["business", "risk_factors", "mda"],
        "10-Q": ["mda", "risk_factors", "financial_statements"],
        "8-K": ["results_operations", "other_events"]
    }

    def __init__(
        self,
        parsed_dir: str = "./data/parsed",
        output_dir: str = "./data/extracted",
        model: str = "gemini-3-flash-preview",
        combine_sections_per_filing: bool = False,
        combined_max_per_category: int = 10,
    ):
        self.parsed_dir = Path(parsed_dir)
        self.output_dir = Path(output_dir)
        self.extractor = TripletExtractor(model=model)
        self.combine_sections_per_filing = combine_sections_per_filing
        self.combined_max_per_category = combined_max_per_category

    def _combine_sections(
        self,
        per_section: List[ExtractedTriplets],
        *,
        ticker: str,
        filing_type: str,
        accession_number: str,
        parsed_metadata: dict = None,
    ) -> dict:
        """섹션별 결과를 공시(=accession) 1건 단위로 합쳐서 반환.

        - 각 아이템에 source_section, extracted_at 추가
        - 각 엔티티의 mentioned_products/persons/companies 필드 보존
        - category별로 entity/metric 기준 중복 제거 후 상한 적용
        """
        from datetime import datetime
        
        extracted_at = datetime.now().isoformat() + "Z"
        
        combined: dict = {
            "ticker": ticker,
            "filing_type": filing_type,
            "accession_number": accession_number,
            "sections_included": [t.section for t in per_section],
            "year": self._extract_year(accession_number, parsed_metadata),
            "quarter": self._extract_quarter(filing_type, parsed_metadata),
            "extracted_at": extracted_at,
            "opportunities": [],
            "risks": [],
            "events": [],
            "technologies": [],
            "strategies": [],
            "financials": [],
            "mentioned_products_global": [],
            "mentioned_persons_global": [],
        }

        # 각 섹션의 결과 병합
        for t in per_section:
            # Opportunities 병합 (각 엔티티에 mentioned_products/persons/companies 포함)
            for opp in t.opportunities:
                opp_with_meta = dict(opp)
                opp_with_meta["source_section"] = t.section
                opp_with_meta["extracted_at"] = extracted_at
                # mentioned_products, mentioned_persons, mentioned_companies는 이미 LLM이 추출
                # 필드가 없으면 빈 배열로 초기화
                if "mentioned_products" not in opp_with_meta:
                    opp_with_meta["mentioned_products"] = []
                if "mentioned_persons" not in opp_with_meta:
                    opp_with_meta["mentioned_persons"] = []
                if "mentioned_companies" not in opp_with_meta:
                    opp_with_meta["mentioned_companies"] = []
                combined["opportunities"].append(opp_with_meta)
            
            # Risks 병합
            for risk in t.risks:
                risk_with_meta = dict(risk)
                risk_with_meta["source_section"] = t.section
                risk_with_meta["extracted_at"] = extracted_at
                if "mentioned_products" not in risk_with_meta:
                    risk_with_meta["mentioned_products"] = []
                if "mentioned_persons" not in risk_with_meta:
                    risk_with_meta["mentioned_persons"] = []
                if "mentioned_companies" not in risk_with_meta:
                    risk_with_meta["mentioned_companies"] = []
                combined["risks"].append(risk_with_meta)
            
            # Events 병합
            for event in t.events:
                event_with_meta = dict(event)
                event_with_meta["source_section"] = t.section
                event_with_meta["extracted_at"] = extracted_at
                event_with_meta["date_parsed"] = self._parse_event_date(event.get("date", ""))
                event_with_meta["event_type"] = self._classify_event_type(
                    event.get("entity", ""),
                    event.get("description", "")
                )
                if "mentioned_products" not in event_with_meta:
                    event_with_meta["mentioned_products"] = []
                if "mentioned_persons" not in event_with_meta:
                    event_with_meta["mentioned_persons"] = []
                if "mentioned_companies" not in event_with_meta:
                    event_with_meta["mentioned_companies"] = []
                combined["events"].append(event_with_meta)
            
            # Technologies 병합
            for tech in getattr(t, "technologies", []):
                tech_with_meta = dict(tech)
                tech_with_meta["source_section"] = t.section
                tech_with_meta["extracted_at"] = extracted_at
                if "mentioned_products" not in tech_with_meta:
                    tech_with_meta["mentioned_products"] = []
                if "mentioned_persons" not in tech_with_meta:
                    tech_with_meta["mentioned_persons"] = []
                if "mentioned_companies" not in tech_with_meta:
                    tech_with_meta["mentioned_companies"] = []
                combined["technologies"].append(tech_with_meta)
            
            # Strategies, Financials 병합 (기존 방식 유지)
            for strategy in t.strategies:
                strategy_with_meta = dict(strategy)
                strategy_with_meta["source_section"] = t.section
                combined["strategies"].append(strategy_with_meta)
            
            for financial in t.financials:
                financial_with_meta = dict(financial)
                financial_with_meta["source_section"] = t.section
                combined["financials"].append(financial_with_meta)
            
            # 전역 Product/Person 목록 수집 (중복 제거용)
            for category in ["opportunities", "risks", "events"]:
                for item in getattr(t, category, []):
                    combined["mentioned_products_global"].extend(
                        item.get("mentioned_products", [])
                    )
                    combined["mentioned_persons_global"].extend(
                        item.get("mentioned_persons", [])
                    )
            

        # de-dup & cap per category
        for cat in ["opportunities", "risks", "events", "strategies", "financials"]:
            seen = set()
            uniq = []
            for it in combined[cat]:
                key = it.get("entity") or it.get("metric") or it.get("name") or ""
                if not key:
                    continue
                if key in seen:
                    continue
                seen.add(key)
                uniq.append(it)
            combined[cat] = uniq[: self.combined_max_per_category]
        
        # 전역 목록 중복 제거 및 통합
        combined["mentioned_products_global"] = self._deduplicate_products(
            combined["mentioned_products_global"]
        )
        combined["mentioned_persons_global"] = self._deduplicate_persons(
            combined["mentioned_persons_global"]
        )
        
        # extraction_stats 추가
        combined["extraction_stats"] = {
            "opportunities_count": len(combined["opportunities"]),
            "risks_count": len(combined["risks"]),
            "events_count": len(combined["events"]),
            "technologies_count": len(combined["technologies"]),
            "strategies_count": len(combined["strategies"]),
            "financials_count": len(combined["financials"]),
            "mentioned_products_count": len(combined["mentioned_products_global"]),
            "mentioned_persons_count": len(combined["mentioned_persons_global"]),
        }

        return combined

    def get_parsed_files(self, ticker: str, filing_type: str) -> List[Path]:
        """파싱된 JSON 파일 목록 반환"""
        dir_path = self.parsed_dir / ticker / filing_type
        if not dir_path.exists():
            return []
        return sorted(dir_path.glob("*.json"))

    def extract_from_file(self, file_path: Path) -> tuple[List[ExtractedTriplets], dict]:
        """단일 파싱 파일에서 Triplets 추출
        
        Returns:
            (results, metadata) 튜플
        """
        with open(file_path, 'r', encoding='utf-8') as f:
            data = json.load(f)
        
        metadata = data.get("metadata", {})
        sections = data.get("sections", {})
        
        ticker = metadata.get("ticker", "")
        filing_type = metadata.get("filing_type", "")
        accession = metadata.get("accession_number", "")
        
        results = []
        target_sections = self.TARGET_SECTIONS.get(filing_type, [])
        
        for section_name in target_sections:
            section_text = sections.get(section_name, "")
            
            if not section_text or len(section_text) < 200:
                continue
            
            logger.info(f"Extracting from {ticker}/{filing_type}/{accession}/{section_name}")
            
            triplets = self.extractor.extract(
                text=section_text,
                ticker=ticker,
                filing_type=filing_type,
                section=section_name,
                accession_number=accession
            )
            
            if triplets.total_count() > 0:
                results.append(triplets)
                logger.info(f"  → Extracted {triplets.total_count()} triplets")
            
            # Rate limiting between sections
            time.sleep(0.5)
        
        return results, metadata

    def _save_results_combined(self, combined: dict):
        """공시(=accession) 1건 단위로 합쳐진 결과를 파일로 저장"""
        output_path = (
            self.output_dir
            / combined["ticker"]
            / combined["filing_type"]
            / f"{combined['accession_number']}.json"
        )
        output_path.parent.mkdir(parents=True, exist_ok=True)
        with open(output_path, "w", encoding="utf-8") as f:
            json.dump(combined, f, ensure_ascii=False, indent=2)

    def extract_all(self) -> List[ExtractedTriplets]:
        """모든 파싱 파일에서 Triplets 추출"""
        all_results = []
        
        for ticker in self.TICKERS:
            for filing_type in self.FILING_TYPES:
                files = self.get_parsed_files(ticker, filing_type)
                
                for file_path in files:
                    try:
                        results, metadata = self.extract_from_file(file_path)

                        if self.combine_sections_per_filing:
                            # file 단위(=accession) 1개 결과로 저장
                            if results:
                                ticker = metadata.get("ticker", "")
                                filing_type = metadata.get("filing_type", "")
                                accession = metadata.get("accession_number", "")
                                combined = self._combine_sections(
                                    results,
                                    ticker=ticker,
                                    filing_type=filing_type,
                                    accession_number=accession,
                                    parsed_metadata=metadata,
                                )
                                self._save_results_combined(combined)
                            # summary 계산을 위해서는 section별 ExtractedTriplets를 그대로 유지
                            all_results.extend(results)
                        else:
                            all_results.extend(results)
                            # 기존 방식: 섹션별 파일 저장
                            self._save_results(results)
                        
                        # Rate limiting between files
                        time.sleep(1)
                        
                    except Exception as e:
                        logger.error(f"Error processing {file_path}: {e}")
                        continue
        
        return all_results

    def _save_results(self, results: List[ExtractedTriplets]):
        """추출 결과를 파일로 저장"""
        for triplets in results:
            output_path = (
                self.output_dir / 
                triplets.ticker / 
                triplets.filing_type / 
                f"{triplets.accession_number}_{triplets.section}.json"
            )
            output_path.parent.mkdir(parents=True, exist_ok=True)
            
            with open(output_path, 'w', encoding='utf-8') as f:
                json.dump(triplets.to_dict(), f, ensure_ascii=False, indent=2)

    def _extract_year(self, accession_number: str, parsed_metadata: dict = None) -> Optional[int]:
        """Accession number나 metadata에서 연도 추출"""
        if parsed_metadata and "year" in parsed_metadata:
            return parsed_metadata["year"]
        # Accession number에서 추출 시도: 0000320193-23-000106 -> 2023
        try:
            parts = accession_number.split("-")
            if len(parts) >= 2:
                year_str = parts[1]
                if len(year_str) == 2:
                    return 2000 + int(year_str)
        except:
            pass
        return None

    def _extract_quarter(self, filing_type: str, parsed_metadata: dict = None) -> Optional[int]:
        """10-Q의 경우 분기 추출"""
        if filing_type != "10-Q":
            return None
        if parsed_metadata and "quarter" in parsed_metadata:
            return parsed_metadata["quarter"]
        return None

    def _parse_event_date(self, date_str: str) -> Optional[str]:
        """Event 날짜를 ISO 8601 형식으로 파싱"""
        if not date_str or date_str.strip() == "":
            return None
        
        date_str = date_str.strip()
        
        # "2023" -> "2023-01-01"
        if len(date_str) == 4 and date_str.isdigit():
            return f"{date_str}-01-01"
        
        # "2023-09-01" 형식은 그대로
        if len(date_str) == 10 and date_str.count("-") == 2:
            return date_str
        
        # 다른 형식은 dateutil.parser 사용
        try:
            from dateutil import parser
            parsed = parser.parse(date_str)
            return parsed.strftime("%Y-%m-%d")
        except:
            return None

    def _classify_event_type(self, entity: str, description: str) -> str:
        """Event 타입 분류 (규칙 기반 또는 LLM)"""
        text = (entity + " " + description).lower()
        
        # 규칙 기반 분류
        if any(keyword in text for keyword in ["launch", "release", "introduce", "product"]):
            return "product_launch"
        elif any(keyword in text for keyword in ["acquisition", "merger", "m&a", "acquire"]):
            return "m&a"
        elif any(keyword in text for keyword in ["regulation", "regulatory", "compliance"]):
            return "regulatory_change"
        elif any(keyword in text for keyword in ["earnings", "revenue", "financial", "guidance"]):
            return "financial_announcement"
        else:
            return "other"

    def _deduplicate_products(self, products: List[Dict]) -> List[Dict]:
        """제품명 기준 중복 제거 및 통합"""
        seen = {}
        for p in products:
            name = p.get("name", "").lower().strip()
            if name and name not in seen:
                seen[name] = dict(p)
                seen[name]["mention_count"] = 1
            elif name in seen:
                # 언급 횟수 증가, 컨텍스트 병합
                seen[name]["mention_count"] = seen[name].get("mention_count", 1) + 1
        return list(seen.values())

    def _deduplicate_persons(self, persons: List[Dict]) -> List[Dict]:
        """인물명 기준 중복 제거 및 통합"""
        seen = {}
        for p in persons:
            name = p.get("name", "").lower().strip()
            if name and name not in seen:
                seen[name] = dict(p)
                seen[name]["mention_count"] = 1
            elif name in seen:
                # 역할 정보 업데이트, 컨텍스트 병합
                if p.get("role") and not seen[name].get("role"):
                    seen[name]["role"] = p["role"]
                seen[name]["mention_count"] = seen[name].get("mention_count", 1) + 1
        return list(seen.values())

    def get_summary(self, results: List[ExtractedTriplets]) -> Dict:
        """추출 결과 요약"""
        summary = {
            "total_extractions": len(results),
            "total_triplets": sum(r.total_count() for r in results),
            "by_category": {
                "opportunities": sum(len(r.opportunities) for r in results),
                "risks": sum(len(r.risks) for r in results),
                "events": sum(len(r.events) for r in results),
                "technologies": sum(len(r.technologies) for r in results),
                "strategies": sum(len(r.strategies) for r in results),
                "financials": sum(len(r.financials) for r in results),
            },
            "by_ticker": {},
            "by_filing_type": {}
        }
        
        # Product/Person 통계 계산
        all_products = []
        all_persons = []
        for r in results:
            # 각 엔티티에서 products/persons 수집
            for opp in r.opportunities:
                all_products.extend(opp.get("mentioned_products", []))
                all_persons.extend(opp.get("mentioned_persons", []))
            for risk in r.risks:
                all_products.extend(risk.get("mentioned_products", []))
                all_persons.extend(risk.get("mentioned_persons", []))
            for event in r.events:
                all_products.extend(event.get("mentioned_products", []))
                all_persons.extend(event.get("mentioned_persons", []))
            for tech in r.technologies:
                all_products.extend(tech.get("mentioned_products", []))
                all_persons.extend(tech.get("mentioned_persons", []))
        
        summary["by_category"]["mentioned_products"] = len(self._deduplicate_products(all_products))
        summary["by_category"]["mentioned_persons"] = len(self._deduplicate_persons(all_persons))
        
        for r in results:
            summary["by_ticker"][r.ticker] = summary["by_ticker"].get(r.ticker, 0) + r.total_count()
            summary["by_filing_type"][r.filing_type] = summary["by_filing_type"].get(r.filing_type, 0) + r.total_count()
        
        return summary

