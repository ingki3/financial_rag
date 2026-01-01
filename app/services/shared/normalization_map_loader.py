"""
Normalization Map Loader

Normalization Map JSON 파일을 로드하고 관리하는 클래스
"""

import json
import logging
import re
import fcntl
from pathlib import Path
from typing import Dict, List, Optional, Any
from datetime import datetime

logger = logging.getLogger(__name__)


class NormalizationMapLoader:
    """Normalization Map을 로드하고 관리하는 클래스"""
    
    def __init__(self, maps_dir: Path = Path("data/normalization_maps")):
        """
        Args:
            maps_dir: Normalization Map 파일 디렉토리 경로
        """
        self.maps_dir = Path(maps_dir)
        self.maps_dir.mkdir(parents=True, exist_ok=True)
        self._maps: Dict[str, Dict] = {}
        self._dirty_flags: Dict[str, bool] = {}
    
    def load(self, ticker: str) -> Dict:
        """티커별 Normalization Map 로드
        
        Args:
            ticker: 티커 심볼
            
        Returns:
            Normalization Map 딕셔너리 (없으면 빈 구조 반환)
        """
        ticker = ticker.upper()
        
        # 이미 메모리에 로드되어 있고 변경사항이 없으면 캐시 반환
        if ticker in self._maps and not self._dirty_flags.get(ticker, False):
            return self._maps[ticker]
        
        map_file = self.maps_dir / f"{ticker}_normalization_map.json"
        
        if not map_file.exists():
            # 파일이 없으면 기본 구조 생성
            default_map = self._create_default_map(ticker)
            self._maps[ticker] = default_map
            self._dirty_flags[ticker] = True
            return default_map
        
        try:
            with open(map_file, 'r', encoding='utf-8') as f:
                # 파일 잠금 (읽기)
                fcntl.flock(f.fileno(), fcntl.LOCK_SH)
                try:
                    data = json.load(f)
                finally:
                    fcntl.flock(f.fileno(), fcntl.LOCK_UN)
            
            self._maps[ticker] = data
            self._dirty_flags[ticker] = False
            logger.info(f"Loaded normalization map for {ticker}")
            return data
            
        except Exception as e:
            logger.error(f"Failed to load normalization map for {ticker}: {e}")
            default_map = self._create_default_map(ticker)
            self._maps[ticker] = default_map
            self._dirty_flags[ticker] = True
            return default_map
    
    def save(self, ticker: str, force: bool = False) -> bool:
        """Normalization Map 저장
        
        Args:
            ticker: 티커 심볼
            force: 변경사항 없어도 강제 저장
            
        Returns:
            저장 성공 여부
        """
        ticker = ticker.upper()
        
        if ticker not in self._maps:
            logger.warning(f"No map loaded for {ticker}")
            return False
        
        if not force and not self._dirty_flags.get(ticker, False):
            logger.debug(f"No changes to save for {ticker}")
            return True
        
        map_file = self.maps_dir / f"{ticker}_normalization_map.json"
        backup_file = self.maps_dir / f"{ticker}_normalization_map.json.backup"
        
        try:
            # 백업 생성
            if map_file.exists():
                import shutil
                shutil.copy2(map_file, backup_file)
            
            # 메타데이터 업데이트
            data = self._maps[ticker]
            if "metadata" in data:
                data["metadata"]["last_updated"] = datetime.utcnow().isoformat() + "Z"
            
            # 파일 저장 (쓰기 잠금)
            with open(map_file, 'w', encoding='utf-8') as f:
                fcntl.flock(f.fileno(), fcntl.LOCK_EX)
                try:
                    json.dump(data, f, indent=2, ensure_ascii=False)
                    f.flush()
                finally:
                    fcntl.flock(f.fileno(), fcntl.LOCK_UN)
            
            self._dirty_flags[ticker] = False
            logger.info(f"Saved normalization map for {ticker}")
            return True
            
        except Exception as e:
            logger.error(f"Failed to save normalization map for {ticker}: {e}")
            return False
    
    def get_category(self, ticker: str, node_type: str) -> Optional[Dict]:
        """카테고리 정보 가져오기
        
        Args:
            ticker: 티커 심볼
            node_type: 노드 타입 ("Product", "Person", "Technology")
            
        Returns:
            카테고리 딕셔너리 또는 None
        """
        data = self.load(ticker)
        categories = data.get("categories", [])
        
        for category in categories:
            if category.get("category") == node_type:
                return category
        
        return None
    
    def mark_dirty(self, ticker: str):
        """변경사항 표시
        
        Args:
            ticker: 티커 심볼
        """
        ticker = ticker.upper()
        self._dirty_flags[ticker] = True
    
    def _create_default_map(self, ticker: str) -> Dict:
        """기본 Normalization Map 구조 생성
        
        Args:
            ticker: 티커 심볼
            
        Returns:
            기본 구조 딕셔너리
        """
        now = datetime.utcnow().isoformat() + "Z"
        return {
            "metadata": {
                "ticker": ticker,
                "version": "1.0.0",
                "created_at": now,
                "last_updated": now,
                "total_mappings": 0,
                "llm_generated_count": 0,
                "auto_added_count": 0
            },
            "categories": [],
            "filtered_terms": [],
            "normalization_rules": []
        }
    
    def add_variant(
        self,
        ticker: str,
        node_type: str,
        standard_item: str,
        variant: str,
        source: str = "manual",
        llm_confidence: Optional[float] = None
    ) -> bool:
        """Variant 추가
        
        Args:
            ticker: 티커 심볼
            node_type: 노드 타입
            standard_item: 표준명
            variant: 변형명 (소문자로 저장됨)
            source: 출처 ("manual", "llm", "auto_added")
            llm_confidence: LLM 신뢰도 (LLM 생성 시)
            
        Returns:
            성공 여부
        """
        ticker = ticker.upper()
        data = self.load(ticker)
        variant_lower = variant.lower().strip()
        
        # 카테고리 찾기 또는 생성
        category = self.get_category(ticker, node_type)
        if not category:
            category = {
                "category": node_type,
                "standard_items": [],
                "normalized_map": []
            }
            data["categories"].append(category)
        
        # standard_item이 standard_items에 없으면 추가
        if standard_item not in category["standard_items"]:
            category["standard_items"].append(standard_item)
            category["standard_items"].sort()
        
        # normalized_map에서 해당 standard_item 찾기
        normalized_item = None
        for item in category["normalized_map"]:
            if item["standard_item"] == standard_item:
                normalized_item = item
                break
        
        if not normalized_item:
            # 새 항목 생성
            normalized_item = {
                "standard_item": standard_item,
                "variants": [],
                "metadata": {
                    "added_at": datetime.utcnow().isoformat() + "Z",
                    "total_usage_count": 0,
                    "source": source
                }
            }
            if llm_confidence is not None:
                normalized_item["metadata"]["llm_confidence"] = llm_confidence
            category["normalized_map"].append(normalized_item)
        
        # variant 추가 (중복 체크)
        if variant_lower not in normalized_item["variants"]:
            normalized_item["variants"].append(variant_lower)
            normalized_item["variants"].sort()
        
        # 메타데이터 업데이트
        if llm_confidence is not None and "llm_confidence" not in normalized_item["metadata"]:
            normalized_item["metadata"]["llm_confidence"] = llm_confidence
        
        self.mark_dirty(ticker)
        return True
    
    def add_rule(
        self,
        ticker: str,
        node_type: str,
        rule_type: str,
        pattern: str,
        target_standard: str,
        description: str,
        source: str = "llm",
        llm_confidence: Optional[float] = None,
        examples: Optional[List[Dict]] = None
    ) -> str:
        """정규화 규칙 추가
        
        Args:
            ticker: 티커 심볼
            node_type: 노드 타입
            rule_type: 규칙 타입 ("pattern", "suffix", "prefix", "abbreviation")
            pattern: 정규식 패턴
            target_standard: 매칭 시 반환할 표준명
            description: 규칙 설명
            source: 출처 ("llm", "manual")
            llm_confidence: LLM 신뢰도
            examples: 예시 배열 [{"input": "...", "output": "..."}]
            
        Returns:
            생성된 rule_id
        """
        ticker = ticker.upper()
        data = self.load(ticker)
        
        # rule_id 생성
        existing_rules = []
        for rule_group in data.get("normalization_rules", []):
            if rule_group.get("category") == node_type:
                existing_rules = rule_group.get("rules", [])
                break
        
        rule_id = f"rule_{len(existing_rules) + 1:03d}"
        
        # 규칙 생성
        rule = {
            "rule_id": rule_id,
            "rule_type": rule_type,
            "pattern": pattern,
            "target_standard": target_standard,
            "description": description,
            "source": source,
            "discovered_at": datetime.utcnow().isoformat() + "Z",
            "usage_count": 0,
            "examples": examples or [],
            "active": True
        }
        
        if llm_confidence is not None:
            rule["llm_confidence"] = llm_confidence
        
        # normalization_rules에 추가
        rule_group = None
        for rg in data.get("normalization_rules", []):
            if rg.get("category") == node_type:
                rule_group = rg
                break
        
        if not rule_group:
            rule_group = {
                "category": node_type,
                "rules": []
            }
            if "normalization_rules" not in data:
                data["normalization_rules"] = []
            data["normalization_rules"].append(rule_group)
        
        rule_group["rules"].append(rule)
        self.mark_dirty(ticker)
        
        return rule_id

