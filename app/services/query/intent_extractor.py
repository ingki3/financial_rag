"""
Intent Extractor Service

Gemini 모델을 활용하여 사용자 질의에서 Intent를 추출합니다.
Phase 8: 질의 응답 시스템

Structured Output을 사용하여 Pydantic 모델 기반으로 Intent를 추출합니다.
참고: https://ai.google.dev/gemini-api/docs/structured-output
"""

import os
import json
import logging
from typing import Dict, Optional, List, Union
from dotenv import load_dotenv
from pydantic import BaseModel, Field
from app.utils.prompt_loader import prompt_loader

# 환경변수 로드
load_dotenv()

logger = logging.getLogger(__name__)

# Gemini API 설정
try:
    from google import genai
    GENAI_AVAILABLE = True
except ImportError:
    GENAI_AVAILABLE = False
    logger.warning("google-genai package is required. Install it with: pip install google-genai")


# Pydantic 모델 정의
class TimeFilter(BaseModel):
    """시간 필터"""
    year: Optional[int] = Field(None, description="특정 연도")
    period: Optional[str] = Field(None, description="기간 (recent, all, 2022-2023 등)", enum=["recent", "all", "2021-2023", "2022-2023", "2021-2022"])


class Filters(BaseModel):
    """필터 조건"""
    company: Optional[Union[str, List[str]]] = Field(None, description="기업 티커 심볼 (단일 또는 다중)")
    context: Optional[List[str]] = Field(None, description="맥락 키워드 배열", enum=["business", "financial", "operational", "regulatory", "competitive", "market"])
    time: Optional[TimeFilter] = Field(None, description="시간 필터")
    section: Optional[str] = Field(None, description="섹션 필터", enum=["risk_factors", "business", "mda", "financial_statements", "other_events", "financial_exhibits"])
    filing_type: Optional[str] = Field(None, description="공시 유형", enum=["10-K", "10-Q", "8-K"])
    product: Optional[str] = Field(None, description="제품명")
    person: Optional[str] = Field(None, description="인물명")


class Expansion(BaseModel):
    """확장 검색 옵션"""
    include_related_products: bool = Field(True, description="관련 제품 포함 여부")
    include_related_persons: bool = Field(False, description="관련 인물 포함 여부")
    include_related_companies: bool = Field(False, description="관련 기업 포함 여부")


class Intent(BaseModel):
    """Intent 모델"""
    target_entity_type: Union[str, List[str]] = Field(
        description="검색할 노드 타입 (단일 또는 다중)",
        enum=["Risk", "Opportunity", "Event", "Technology", "Product", "Person", "general"]
    )
    filters: Filters = Field(description="검색 필터 조건")
    query_type: str = Field(description="질의 유형", enum=["explain", "list", "compare", "analyze"])
    expansion: Expansion = Field(description="확장 검색 옵션")


class IntentExtractor:
    """Gemini를 활용한 Intent 추출 클래스 (Structured Output 사용)"""
    
    def __init__(
        self,
        model: str = "gemini-2.5-flash-lite",
        api_key: Optional[str] = None
    ):
        """
        Args:
            model: Gemini 모델명
            api_key: Gemini API 키 (없으면 환경변수에서 로드)
        """
        if not GENAI_AVAILABLE:
            raise ImportError("google-genai package is required. Install it with: pip install google-genai")
        
        self.model = model
        api_key = api_key or os.getenv("GEMINI_API_KEY") or os.getenv("GOOGLE_API_KEY")
        
        if not api_key:
            raise ValueError("GEMINI_API_KEY or GOOGLE_API_KEY must be provided")
        
        # google.genai Client 초기화
        self.client = genai.Client(api_key=api_key)
        
        self._original_query = None
    
    def _build_intent_prompt(self, query: str) -> str:
        """Intent 추출을 위한 Prompt 생성"""
        # YAML 파일에서 프롬프트 로드
        prompt = prompt_loader.load_prompt("intent_extractor")
        template = prompt.get("template", "")
        
        # 변수 치환
        return template.format(query=query)
    
    async def extract_intent(self, query: str) -> Dict:
        """질의에서 Intent 추출 (비동기, Structured Output 사용)"""
        self._original_query = query
        
        try:
            prompt = self._build_intent_prompt(query)
            
            # Structured Output을 사용하여 Intent 추출
            response = await self.client.aio.models.generate_content(
                model=self.model,
                contents=prompt,
                config={
                    "response_mime_type": "application/json",
                    "response_json_schema": Intent.model_json_schema(),
                    "temperature": 0.1,  # 일관성을 위해 낮은 temperature
                }
            )
            
            # JSON 파싱 후 Pydantic 모델로 검증
            import json
            response_text = response.text.strip()
            logger.debug(f"Raw response text: {response_text[:500]}")
            
            # JSON 추출 (마크다운 코드 블록 제거)
            if response_text.startswith("```json"):
                response_text = response_text[7:]
            if response_text.startswith("```"):
                response_text = response_text[3:]
            if response_text.endswith("```"):
                response_text = response_text[:-3]
            response_text = response_text.strip()
            
            try:
                intent_dict = json.loads(response_text)
            except json.JSONDecodeError as json_err:
                logger.error(f"JSON decode error: {json_err}")
                logger.error(f"Response text (first 500 chars): {response_text[:500]}")
                raise
            
            intent_obj = Intent(**intent_dict)
            intent_dict = intent_obj.model_dump()
            
            # 검증 및 정규화
            intent_dict = self._validate_and_normalize(intent_dict)
            
            logger.debug(f"Intent extracted: {intent_dict}")
            return intent_dict
            
        except json.JSONDecodeError as json_err:
            logger.error(f"JSON decode error: {json_err}")
            if 'response_text' in locals():
                logger.error(f"Response text (first 500 chars): {response_text[:500]}")
            return self._get_default_intent(query)
        except Exception as e:
            logger.error(f"Failed to extract intent: {type(e).__name__}: {e}")
            import traceback
            logger.error(f"Traceback: {traceback.format_exc()}")
            if 'response' in locals():
                if hasattr(response, 'text'):
                    logger.error(f"Response text: {response.text[:500] if response.text else 'None'}")
                logger.error(f"Response type: {type(response)}")
            return self._get_default_intent(query)
    
    def extract_intent_sync(self, query: str) -> Dict:
        """질의에서 Intent 추출 (동기, Structured Output 사용)"""
        self._original_query = query
        
        try:
            prompt = self._build_intent_prompt(query)
            
            # Structured Output을 사용하여 Intent 추출
            response = self.client.models.generate_content(
                model=self.model,
                contents=prompt,
                config={
                    "response_mime_type": "application/json",
                    "response_json_schema": Intent.model_json_schema(),
                    "temperature": 0.1,  # 일관성을 위해 낮은 temperature
                }
            )
            
            # JSON 파싱 후 Pydantic 모델로 검증
            import json
            response_text = response.text.strip()
            logger.debug(f"Raw response text: {response_text[:200]}")
            
            # JSON 추출 (마크다운 코드 블록 제거)
            if response_text.startswith("```json"):
                response_text = response_text[7:]
            if response_text.startswith("```"):
                response_text = response_text[3:]
            if response_text.endswith("```"):
                response_text = response_text[:-3]
            response_text = response_text.strip()
            
            intent_dict = json.loads(response_text)
            intent_obj = Intent(**intent_dict)
            intent_dict = intent_obj.model_dump()
            
            # 검증 및 정규화
            intent_dict = self._validate_and_normalize(intent_dict)
            
            logger.debug(f"Intent extracted: {intent_dict}")
            return intent_dict
            
        except json.JSONDecodeError as json_err:
            logger.error(f"JSON decode error: {json_err}")
            if 'response_text' in locals():
                logger.error(f"Response text (first 500 chars): {response_text[:500]}")
            return self._get_default_intent(query)
        except Exception as e:
            logger.error(f"Failed to extract intent: {type(e).__name__}: {e}")
            import traceback
            logger.error(f"Traceback: {traceback.format_exc()}")
            if 'response' in locals():
                if hasattr(response, 'text'):
                    logger.error(f"Response text: {response.text[:500] if response.text else 'None'}")
                logger.error(f"Response type: {type(response)}")
            return self._get_default_intent(query)
    
    def _validate_and_normalize(self, intent: Dict) -> Dict:
        """Intent 검증 및 정규화"""
        # 필수 필드 확인
        if "target_entity_type" not in intent:
            intent["target_entity_type"] = "general"
        
        # filters 기본값 설정
        if "filters" not in intent:
            intent["filters"] = {}
        
        # company 티커 정규화
        if "company" in intent["filters"] and intent["filters"]["company"]:
            company = intent["filters"]["company"]
            if isinstance(company, str):
                intent["filters"]["company"] = self._normalize_company(company)
            elif isinstance(company, list):
                intent["filters"]["company"] = [self._normalize_company(c) for c in company]
        
        # query_type 기본값
        if "query_type" not in intent:
            intent["query_type"] = "explain"
        
        # expansion 기본값
        if "expansion" not in intent:
            intent["expansion"] = {
                "include_related_products": True,
                "include_related_persons": False,
                "include_related_companies": False
            }
        
        return intent
    
    def _normalize_company(self, company: str) -> str:
        """한국어 기업명을 티커로 변환"""
        company_map = {
            "애플": "AAPL", "apple": "AAPL",
            "아마존": "AMZN", "amazon": "AMZN",
            "테슬라": "TSLA", "tesla": "TSLA",
            "구글": "GOOGL", "google": "GOOGL", "알파벳": "GOOGL",
            "마이크로소프트": "MSFT", "microsoft": "MSFT", "ms": "MSFT",
            "메타": "META", "meta": "META", "페이스북": "META", "facebook": "META",
            "엔비디아": "NVDA", "nvidia": "NVDA"
        }
        return company_map.get(company.lower(), company.upper())
    
    def _get_default_intent(self, query: str) -> Dict:
        """기본 Intent 반환 (폴백)"""
        return {
            "target_entity_type": "general",
            "filters": {},
            "query_type": "explain",
            "expansion": {
                "include_related_products": True,
                "include_related_persons": False,
                "include_related_companies": False
            }
        }

