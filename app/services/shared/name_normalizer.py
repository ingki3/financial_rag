"""
이름 표준화 서비스

Product, Person, Technology 이름을 표준 사전에 맞게 정규화합니다.
LLM을 사용하여 사용자 입력을 표준 이름으로 변환합니다.
"""

import os
import json
import logging
from pathlib import Path
from typing import Dict, List, Optional, Set
from dotenv import load_dotenv

load_dotenv()

logger = logging.getLogger(__name__)

# Gemini API 설정
try:
    from google import genai
    GENAI_AVAILABLE = True
except ImportError:
    GENAI_AVAILABLE = False
    logger.warning("google-genai package is required. Install it with: pip install google-genai")


class NameNormalizer:
    """이름 표준화 클래스"""
    
    def __init__(self, standard_dicts_dir: Path = Path("data/standard_dicts")):
        """
        NameNormalizer 초기화
        
        Args:
            standard_dicts_dir: 표준 사전 디렉토리 경로
        """
        self.standard_dicts_dir = Path(standard_dicts_dir)
        self._standard_dicts: Dict[str, Dict[str, List[str]]] = {}
        self._load_standard_dicts()
        
        # Gemini API 초기화
        if GENAI_AVAILABLE:
            api_key = os.getenv("GEMINI_API_KEY") or os.getenv("GOOGLE_API_KEY")
            if api_key:
                self.client = genai.Client(api_key=api_key)
                self.model = "gemini-2.5-flash-lite"
            else:
                logger.warning("GEMINI_API_KEY not found. Name normalization will use fuzzy matching only.")
                self.client = None
        else:
            self.client = None
    
    def _load_standard_dicts(self):
        """표준 사전 로드"""
        if not self.standard_dicts_dir.exists():
            logger.warning(f"Standard dicts directory not found: {self.standard_dicts_dir}")
            return
        
        for dict_file in self.standard_dicts_dir.glob("*_standard_dict.json"):
            ticker = dict_file.stem.replace("_standard_dict", "").upper()
            try:
                with open(dict_file, 'r', encoding='utf-8') as f:
                    self._standard_dicts[ticker] = json.load(f)
                logger.info(f"Loaded standard dict for {ticker}")
            except Exception as e:
                logger.error(f"Failed to load standard dict for {ticker}: {e}")
    
    def normalize(
        self,
        name: str,
        node_type: str,
        ticker: str,
        use_llm: bool = True
    ) -> Optional[str]:
        """
        이름을 표준 이름으로 정규화
        
        Args:
            name: 정규화할 이름
            node_type: 노드 타입 ("Product", "Person", "Technology")
            ticker: 티커 심볼
            use_llm: LLM 사용 여부 (False면 fuzzy matching만 사용)
            
        Returns:
            표준 이름 또는 None (매칭 실패)
        """
        if not name:
            return None
        
        ticker = ticker.upper()
        
        # 표준 사전 확인
        if ticker not in self._standard_dicts:
            logger.warning(f"No standard dict for ticker: {ticker}")
            return name  # 원본 반환
        
        standard_names = self._standard_dicts[ticker].get(node_type, [])
        if not standard_names:
            logger.warning(f"No standard names for {ticker}/{node_type}")
            return name  # 원본 반환
        
        # 정확한 매칭 확인
        name_lower = name.lower().strip()
        for std_name in standard_names:
            if std_name.lower().strip() == name_lower:
                return std_name
        
        # 부분 매칭 확인 (포함 관계)
        for std_name in standard_names:
            std_lower = std_name.lower().strip()
            if name_lower in std_lower or std_lower in name_lower:
                return std_name
        
        # LLM을 사용한 매칭
        if use_llm and self.client:
            return self._normalize_with_llm(name, node_type, ticker, standard_names)
        
        # 매칭 실패 시 원본 반환
        return name
    
    def _normalize_with_llm(
        self,
        name: str,
        node_type: str,
        ticker: str,
        standard_names: List[str]
    ) -> Optional[str]:
        """
        LLM을 사용하여 이름 정규화
        
        Args:
            name: 정규화할 이름
            node_type: 노드 타입
            ticker: 티커 심볼
            standard_names: 표준 이름 리스트
            
        Returns:
            표준 이름 또는 None
        """
        if not self.client:
            return None
        
        try:
            # YAML 파일에서 프롬프트 로드
            prompt_data = prompt_loader.load_prompt("name_normalizer")
            template = prompt_data.get("template", "")
            
            # 변수 치환
            prompt = template.format(
                ticker=ticker,
                node_type=node_type,
                name=name,
                standard_names_json=json.dumps(standard_names, ensure_ascii=False, indent=2)
            )

            response = self.client.models.generate_content(
                model=self.model,
                contents=prompt,
                config={
                    "temperature": 0.1,
                }
            )
            
            normalized = response.text.strip().strip('"').strip("'")
            
            # "NONE"이거나 표준 이름 목록에 없으면 None 반환
            if normalized.upper() == "NONE" or normalized not in standard_names:
                logger.debug(f"LLM normalization failed for '{name}': '{normalized}'")
                return None
            
            logger.debug(f"LLM normalized '{name}' -> '{normalized}'")
            return normalized
            
        except Exception as e:
            logger.error(f"LLM normalization failed: {e}")
            return None
    
    def normalize_filters(
        self,
        filters: List[Dict],
        ticker: Optional[str] = None
    ) -> List[Dict]:
        """
        Filters 리스트의 이름들을 표준화
        
        Args:
            filters: 필터 노드 리스트
            ticker: 티커 심볼 (filters에서 추출 가능하면 생략 가능)
            
        Returns:
            표준화된 필터 리스트
        """
        normalized_filters = []
        
        for filter_node in filters:
            node_type = filter_node.get("node_type")
            
            # Company 노드는 ticker만 있으므로 그대로 유지
            if node_type == "Company":
                normalized_filters.append(filter_node)
                if not ticker:
                    ticker = filter_node.get("ticker")
                continue
            
            # Product, Person, Technology 노드의 이름 표준화
            if node_type in ["Product", "Person", "Technology"]:
                normalized_node = filter_node.copy()
                
                # ticker 추출
                node_ticker = ticker or filter_node.get("ticker")
                if not node_ticker:
                    # filters에서 Company 노드 찾기
                    company_filter = next(
                        (f for f in filters if f.get("node_type") == "Company"),
                        None
                    )
                    if company_filter:
                        node_ticker = company_filter.get("ticker")
                
                if node_ticker:
                    # name 또는 entity 필드 표준화
                    if node_type == "Technology":
                        entity = filter_node.get("entity") or filter_node.get("name")
                        if entity:
                            normalized_entity = self.normalize(
                                entity, node_type, node_ticker
                            )
                            if normalized_entity:
                                normalized_node["entity"] = normalized_entity
                                if "name" in normalized_node:
                                    del normalized_node["name"]
                    else:
                        name = filter_node.get("name")
                        if name:
                            normalized_name = self.normalize(
                                name, node_type, node_ticker
                            )
                            if normalized_name:
                                normalized_node["name"] = normalized_name
                
                normalized_filters.append(normalized_node)
            else:
                # 기타 노드 타입은 그대로 유지
                normalized_filters.append(filter_node)
        
        return normalized_filters


