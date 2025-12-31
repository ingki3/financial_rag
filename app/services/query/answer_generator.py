"""
Answer Generator Service

검색 결과를 바탕으로 자연어 답변을 생성하는 서비스
Phase 8: 질의 응답 시스템
"""

import logging
import os
from typing import Dict, List, Optional, Generator
from dotenv import load_dotenv
from app.utils.prompt_loader import prompt_loader

load_dotenv()

logger = logging.getLogger(__name__)

# Gemini API 설정
try:
    from google import genai
    GENAI_AVAILABLE = True
except ImportError:
    GENAI_AVAILABLE = False
    logger.warning("google-genai package is required. Install it with: pip install google-genai")


class AnswerGenerator:
    """검색 결과를 바탕으로 답변 생성"""
    
    def __init__(self, model: str = "gemini-3-flash-preview", api_key: Optional[str] = None):
        """
        AnswerGenerator 초기화
        
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
        
        self.client = genai.Client(api_key=api_key)
    
    def generate_answer(
        self,
        query: str,
        results: List[Dict],
        intent: Optional[Dict] = None,
        max_results: int = 5
    ) -> str:
        """
        검색 결과를 바탕으로 답변 생성
        
        Args:
            query: 사용자 질의
            results: 검색 결과 리스트
            intent: Intent 객체 (선택적)
            max_results: 답변 생성에 사용할 최대 결과 수
            
        Returns:
            생성된 답변 텍스트
        """
        if not results:
            return "죄송합니다. 검색 결과를 찾을 수 없습니다."
        
        # 상위 N개 결과만 사용
        top_results = results[:max_results]
        
        # 컨텍스트 구성
        context = self._build_context(top_results, intent)
        
        # Prompt 생성
        prompt = self._build_prompt(query, context, intent)
        
        try:
            # Gemini를 사용하여 답변 생성
            response = self.client.models.generate_content(
                model=self.model,
                contents=prompt,
                config={
                    "temperature": 0.7,
                }
            )
            
            answer = response.text.strip()
            logger.info(f"Generated answer (length: {len(answer)})")
            return answer
            
        except Exception as e:
            logger.error(f"Failed to generate answer: {e}")
            # 폴백: 간단한 요약 반환
            return self._generate_fallback_answer(query, top_results)
    
    def _build_context(self, results: List[Dict], intent: Optional[Dict] = None) -> str:
        """
        검색 결과를 컨텍스트 텍스트로 변환
        
        Args:
            results: 검색 결과 리스트
            intent: Intent 객체 (선택적)
            
        Returns:
            컨텍스트 텍스트
        """
        context_parts = []
        
        for i, result in enumerate(results, 1):
            node_type = result.get("node_type") or result.get("labels", [None])[0] if isinstance(result.get("labels"), list) else None
            entity = result.get("entity") or result.get("name")
            description = result.get("description")
            ticker = result.get("ticker")
            
            context_part = f"[결과 {i}]"
            if node_type:
                context_part += f"\n타입: {node_type}"
            if entity:
                context_part += f"\n제목: {entity}"
            if description:
                context_part += f"\n설명: {description}"
            if ticker:
                context_part += f"\n기업: {ticker}"
            
            context_parts.append(context_part)
        
        return "\n\n".join(context_parts)
    
    def _build_prompt(
        self, 
        query: str, 
        context: str, 
        intent: Optional[Dict] = None
    ) -> str:
        """
        답변 생성을 위한 Prompt 생성
        
        Args:
            query: 사용자 질의
            context: 검색 결과 컨텍스트
            intent: Intent 객체 (선택적)
            
        Returns:
            Prompt 텍스트
        """
        query_type = intent.get("query_type", "explain") if intent else "explain"
        
        # YAML 파일에서 프롬프트 로드
        prompt = prompt_loader.load_prompt("answer_generator")
        template = prompt.get("template", "")
        
        # 변수 치환
        return template.format(
            query=query,
            context=context,
            query_type=query_type
        )
    
    def _generate_fallback_answer(self, query: str, results: List[Dict]) -> str:
        """
        폴백 답변 생성 (LLM 실패 시)
        
        Args:
            query: 사용자 질의
            results: 검색 결과 리스트
            
        Returns:
            간단한 요약 답변
        """
        answer_parts = [f"'{query}'에 대한 검색 결과를 찾았습니다:\n"]
        
        for i, result in enumerate(results, 1):
            entity = result.get("entity") or result.get("name", "알 수 없음")
            description = result.get("description", "")
            
            if description:
                # 설명이 길면 앞부분만
                desc_preview = description[:200] + "..." if len(description) > 200 else description
                answer_parts.append(f"{i}. {entity}: {desc_preview}")
            else:
                answer_parts.append(f"{i}. {entity}")
        
        return "\n".join(answer_parts)
    
    def generate_answer_stream(
        self,
        query: str,
        results: List[Dict],
        intent: Optional[Dict] = None,
        max_results: int = 5
    ) -> Generator[str, None, None]:
        """
        검색 결과를 바탕으로 스트리밍 답변 생성
        
        Args:
            query: 사용자 질의
            results: 검색 결과 리스트
            intent: Intent 객체 (선택적)
            max_results: 답변 생성에 사용할 최대 결과 수
        
        Yields:
            답변 텍스트 청크 (str)
        """
        if not results:
            yield "죄송합니다. 검색 결과를 찾을 수 없습니다."
            return
        
        # 상위 N개 결과만 사용
        top_results = results[:max_results]
        
        # 컨텍스트 구성
        context = self._build_context(top_results, intent)
        
        # Prompt 생성
        prompt = self._build_prompt(query, context, intent)
        
        try:
            # generate_content_stream 사용
            response_stream = self.client.models.generate_content_stream(
                model=self.model,
                contents=prompt,
                config={
                    "temperature": 0.7,
                }
            )
            
            # 각 chunk에서 텍스트 추출하여 yield
            for chunk in response_stream:
                text = None
                
                # 방법 1: chunk.text 속성 확인
                if hasattr(chunk, 'text') and chunk.text:
                    text = chunk.text
                # 방법 2: candidates 구조에서 추출
                elif hasattr(chunk, 'candidates') and chunk.candidates:
                    for candidate in chunk.candidates:
                        if hasattr(candidate, 'content'):
                            if hasattr(candidate.content, 'parts'):
                                for part in candidate.content.parts:
                                    if hasattr(part, 'text') and part.text:
                                        text = part.text
                                        break
                            elif hasattr(candidate.content, 'text') and candidate.content.text:
                                text = candidate.content.text
                                break
                        if text:
                            break
                
                if text:
                    yield text
                    
        except Exception as e:
            logger.error(f"Failed to generate streaming answer: {e}")
            # 폴백: 간단한 요약 반환
            fallback = self._generate_fallback_answer(query, top_results)
            yield fallback


