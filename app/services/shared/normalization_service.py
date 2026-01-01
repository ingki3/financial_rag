"""
Normalization Service

정규화 로직을 통합 관리하는 서비스
Normalization Map을 사용하여 이름을 정규화합니다.
"""

import re
import logging
from typing import Optional, Dict, Any
from pathlib import Path

from app.services.shared.normalization_map_loader import NormalizationMapLoader

logger = logging.getLogger(__name__)


class NormalizationService:
    """정규화 서비스 클래스"""
    
    def __init__(self, maps_dir: Path = Path("data/normalization_maps")):
        """
        Args:
            maps_dir: Normalization Map 디렉토리 경로
        """
        self.loader = NormalizationMapLoader(maps_dir)
        self._llm_service = None  # Lazy import
    
    def normalize(
        self,
        name: str,
        node_type: str,
        ticker: str,
        use_llm: bool = True,
        auto_save: bool = True
    ) -> Optional[str]:
        """이름 정규화
        
        Args:
            name: 정규화할 이름
            node_type: 노드 타입 ("Product", "Person", "Technology")
            ticker: 티커 심볼
            use_llm: LLM 사용 여부
            auto_save: 자동 저장 여부
            
        Returns:
            표준명 또는 None
        """
        if not name or not name.strip():
            return None
        
        ticker = ticker.upper()
        name_lower = name.lower().strip()
        
        # [1] Normalization Map 로드
        data = self.loader.load(ticker)
        
        # [2] 카테고리 찾기
        category = self.loader.get_category(ticker, node_type)
        if not category:
            # 카테고리가 없으면 원본 반환
            return name
        
        # [3] normalized_map에서 variants 검색
        normalized_map = category.get("normalized_map", [])
        for item in normalized_map:
            variants = item.get("variants", [])
            if name_lower in variants:
                # 매칭 성공
                standard_item = item["standard_item"]
                # usage_count 증가
                item["metadata"]["total_usage_count"] = item["metadata"].get("total_usage_count", 0) + 1
                self.loader.mark_dirty(ticker)
                if auto_save:
                    self.loader.save(ticker)
                return standard_item
        
        # [4] standard_items에서 직접 매칭
        standard_items = category.get("standard_items", [])
        matched_standard = None
        
        # Exact Match
        for std_item in standard_items:
            if std_item.lower().strip() == name_lower:
                matched_standard = std_item
                break
        
        # Partial Match
        if not matched_standard:
            for std_item in standard_items:
                std_lower = std_item.lower().strip()
                if name_lower in std_lower or std_lower in name_lower:
                    matched_standard = std_item
                    break
        
        if matched_standard:
            # 매칭 성공 - variant 추가
            self.loader.add_variant(
                ticker, node_type, matched_standard, name_lower,
                source="manual"
            )
            if auto_save:
                self.loader.save(ticker)
            return matched_standard
        
        # [5] normalization_rules에서 패턴 매칭
        matched_standard = self._match_rules(ticker, node_type, name_lower, data)
        if matched_standard:
            if auto_save:
                self.loader.save(ticker)
            return matched_standard
        
        # [6] LLM 호출
        if use_llm:
            result = self._normalize_with_llm(name, node_type, ticker, standard_items, data)
            if result:
                # LLM이 새로운 표준명을 제안한 경우 standard_items에 추가
                if result not in standard_items:
                    category["standard_items"].append(result)
                    category["standard_items"].sort()
                    # normalized_map에 새 항목 추가
                    name_lower = name.lower().strip()
                    self.loader.add_variant(
                        ticker, node_type, result, name_lower,
                        source="auto_added",
                        llm_confidence=0.9
                    )
                    # pending_review 플래그 설정
                    normalized_map = category.get("normalized_map", [])
                    for item in normalized_map:
                        if item["standard_item"] == result:
                            item["metadata"]["pending_review"] = True
                            break
                
                if auto_save:
                    self.loader.save(ticker)
                return result
        
        # 매칭 실패 - 원본 반환
        return name
    
    def _match_rules(
        self,
        ticker: str,
        node_type: str,
        name_lower: str,
        data: Dict
    ) -> Optional[str]:
        """규칙 기반 매칭
        
        Args:
            ticker: 티커 심볼
            node_type: 노드 타입
            name_lower: 소문자로 변환된 이름
            data: Normalization Map 데이터
            
        Returns:
            매칭된 표준명 또는 None
        """
        rules_groups = data.get("normalization_rules", [])
        
        for rule_group in rules_groups:
            if rule_group.get("category") != node_type:
                continue
            
            rules = rule_group.get("rules", [])
            for rule in rules:
                if not rule.get("active", True):
                    continue
                
                pattern = rule.get("pattern", "")
                if not pattern:
                    continue
                
                try:
                    # 정규식 매칭
                    if re.match(pattern, name_lower):
                        target_standard = rule.get("target_standard")
                        if target_standard:
                            # usage_count 증가
                            rule["usage_count"] = rule.get("usage_count", 0) + 1
                            self.loader.mark_dirty(ticker)
                            return target_standard
                except re.error as e:
                    logger.warning(f"Invalid regex pattern '{pattern}': {e}")
                    continue
        
        return None
    
    def _normalize_with_llm(
        self,
        name: str,
        node_type: str,
        ticker: str,
        standard_items: list,
        data: Dict
    ) -> Optional[str]:
        """LLM을 사용한 정규화 (규칙 발견 기능 포함)
        
        Args:
            name: 정규화할 이름
            node_type: 노드 타입
            ticker: 티커 심볼
            standard_items: 표준명 목록
            data: Normalization Map 데이터
            
        Returns:
            표준명 또는 None
        """
        # Lazy import
        if self._llm_service is None:
            try:
                from app.services.shared.name_normalizer import NameNormalizer
                self._llm_service = NameNormalizer()
            except Exception as e:
                logger.warning(f"Failed to initialize LLM service: {e}")
                return None
        
        if not hasattr(self._llm_service, 'client') or not self._llm_service.client:
            return None
        
        try:
            # Phase 3: 개선된 LLM 호출 (규칙 발견 기능 포함)
            result = self._normalize_with_llm_enhanced(
                name, node_type, ticker, standard_items
            )
            
            if result:
                standard_name = result.get("standard_name")
                discovered_rule = result.get("discovered_rule")
                confidence = result.get("confidence", 0.9)
                
                if standard_name:
                    # variant 추가
                    name_lower = name.lower().strip()
                    self.loader.add_variant(
                        ticker, node_type, standard_name, name_lower,
                        source="llm",
                        llm_confidence=confidence
                    )
                    
                    # 규칙 발견 시 normalization_rules에 추가
                    if discovered_rule:
                        rule_id = self.loader.add_rule(
                            ticker=ticker,
                            node_type=node_type,
                            rule_type=discovered_rule.get("rule_type", "pattern"),
                            pattern=discovered_rule.get("pattern", ""),
                            target_standard=discovered_rule.get("target_standard", standard_name),
                            description=discovered_rule.get("description", ""),
                            source="llm",
                            llm_confidence=discovered_rule.get("confidence", confidence),
                            examples=[{"input": name_lower, "output": standard_name}]
                        )
                        logger.info(f"Discovered new normalization rule: {rule_id}")
                    
                    return standard_name
        except Exception as e:
            logger.error(f"LLM normalization failed: {e}")
        
        return None
    
    def _normalize_with_llm_enhanced(
        self,
        name: str,
        node_type: str,
        ticker: str,
        standard_items: list
    ) -> Optional[Dict]:
        """개선된 LLM 정규화 (규칙 발견 기능 포함)
        
        Args:
            name: 정규화할 이름
            node_type: 노드 타입
            ticker: 티커 심볼
            standard_items: 표준명 목록
            
        Returns:
            {
                "standard_name": str,
                "discovered_rule": dict | None,
                "confidence": float
            } 또는 None
        """
        import json
        from app.utils.prompt_loader import prompt_loader
        
        try:
            # 프롬프트 로드
            prompt_data = prompt_loader.load_prompt("name_normalizer")
            template = prompt_data.get("template", "")
            
            # 변수 치환
            prompt = template.format(
                ticker=ticker,
                node_type=node_type,
                name=name,
                standard_names_json=json.dumps(standard_items, ensure_ascii=False, indent=2)
            )
            
            # LLM 호출 (Structured Output 사용)
            response = self._llm_service.client.models.generate_content(
                model=self._llm_service.model,
                contents=prompt,
                config={
                    "response_mime_type": "application/json",
                    "temperature": 0.1,
                }
            )
            
            # JSON 파싱
            response_text = response.text.strip()
            
            # 마크다운 코드 블록 제거
            if response_text.startswith("```json"):
                response_text = response_text[7:]
            if response_text.startswith("```"):
                response_text = response_text[3:]
            if response_text.endswith("```"):
                response_text = response_text[:-3]
            response_text = response_text.strip()
            
            result = json.loads(response_text)
            
            # 결과 처리
            matched_standard = result.get("matched_standard")
            suggested_standard = result.get("suggested_standard")
            discovered_rule = result.get("discovered_rule")
            confidence = result.get("confidence", 0.9)
            
            standard_name = matched_standard or suggested_standard
            
            if not standard_name or standard_name.upper() == "NONE":
                return None
            
            return {
                "standard_name": standard_name,
                "discovered_rule": discovered_rule,
                "confidence": confidence
            }
            
        except json.JSONDecodeError as e:
            logger.warning(f"Failed to parse LLM response as JSON: {e}")
            # Fallback: 기존 방식으로 시도
            try:
                standard_name = self._llm_service._normalize_with_llm(
                    name, node_type, ticker, standard_items
                )
                if standard_name:
                    return {
                        "standard_name": standard_name,
                        "discovered_rule": None,
                        "confidence": 0.8
                    }
            except Exception as e2:
                logger.error(f"Fallback LLM normalization also failed: {e2}")
        except Exception as e:
            logger.error(f"LLM enhanced normalization failed: {e}")
        
        return None

