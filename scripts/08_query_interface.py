#!/usr/bin/env python
"""
질의 응답 인터페이스

Phase 8.7: CLI 인터페이스 구현

사용법:
    python scripts/08_query_interface.py
    python scripts/08_query_interface.py --debug  # 디버그 모드
    python scripts/08_query_interface.py --no-vector  # Vector 검색 비활성화
"""

import sys
import os
from pathlib import Path
import argparse
import json
from typing import List, Dict, Optional
from datetime import datetime

# 프로젝트 루트를 Python 경로에 추가
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

from dotenv import load_dotenv
load_dotenv()

from app.services.query_engine import QueryEngine
from app.services.cypher_query_builder import CypherQueryBuilder

# ANSI 색상 코드
class Colors:
    HEADER = '\033[95m'
    OKBLUE = '\033[94m'
    OKCYAN = '\033[96m'
    OKGREEN = '\033[92m'
    WARNING = '\033[93m'
    FAIL = '\033[91m'
    ENDC = '\033[0m'
    BOLD = '\033[1m'
    UNDERLINE = '\033[4m'


class QueryInterface:
    """질의 응답 CLI 인터페이스"""
    
    def __init__(self, debug_mode: bool = False, use_vector_search: bool = True):
        """
        초기화
        
        Args:
            debug_mode: 디버그 모드 활성화 여부
            use_vector_search: Vector 검색 사용 여부
        """
        self.debug_mode = debug_mode
        self.use_vector_search = use_vector_search
        self.engine = None
        self.query_builder = None
        self.history: List[Dict] = []
        
    def initialize(self):
        """QueryEngine 초기화"""
        print(f"{Colors.OKCYAN}초기화 중...{Colors.ENDC}")
        try:
            self.engine = QueryEngine(graph_name="financial_kg")
            self.query_builder = CypherQueryBuilder()
            print(f"{Colors.OKGREEN}✅ QueryEngine 초기화 완료{Colors.ENDC}\n")
            return True
        except Exception as e:
            print(f"{Colors.FAIL}❌ 초기화 실패: {e}{Colors.ENDC}")
            return False
    
    def print_header(self):
        """헤더 출력"""
        print(f"\n{Colors.HEADER}{Colors.BOLD}{'=' * 80}{Colors.ENDC}")
        print(f"{Colors.HEADER}{Colors.BOLD}금융 공시 Knowledge Graph 질의 시스템{Colors.ENDC}")
        print(f"{Colors.HEADER}{Colors.BOLD}{'=' * 80}{Colors.ENDC}")
        print(f"\n{Colors.OKCYAN}명령어:{Colors.ENDC}")
        print(f"  {Colors.OKGREEN}help{Colors.ENDC}     - 도움말 표시")
        print(f"  {Colors.OKGREEN}debug{Colors.ENDC}    - 디버그 모드 토글")
        print(f"  {Colors.OKGREEN}history{Colors.ENDC}  - 질의 히스토리 표시")
        print(f"  {Colors.OKGREEN}clear{Colors.ENDC}    - 화면 지우기")
        print(f"  {Colors.OKGREEN}exit{Colors.ENDC} / {Colors.OKGREEN}quit{Colors.ENDC} - 종료")
        print(f"\n{Colors.WARNING}질의를 입력하세요...{Colors.ENDC}\n")
    
    def print_help(self):
        """도움말 출력"""
        print(f"\n{Colors.HEADER}{Colors.BOLD}도움말{Colors.ENDC}")
        print(f"{Colors.HEADER}{'=' * 80}{Colors.ENDC}")
        print(f"\n{Colors.OKCYAN}사용 가능한 명령어:{Colors.ENDC}")
        print(f"  {Colors.OKGREEN}help{Colors.ENDC}        - 이 도움말 표시")
        print(f"  {Colors.OKGREEN}debug{Colors.ENDC}       - 디버그 모드 토글 (Intent, Cypher 쿼리 표시)")
        print(f"  {Colors.OKGREEN}history{Colors.ENDC}     - 질의 히스토리 표시")
        print(f"  {Colors.OKGREEN}clear{Colors.ENDC}       - 화면 지우기")
        print(f"  {Colors.OKGREEN}exit{Colors.ENDC} / {Colors.OKGREEN}quit{Colors.ENDC} - 프로그램 종료")
        print(f"\n{Colors.OKCYAN}질의 예시:{Colors.ENDC}")
        print(f"  - 애플의 기회 요소는?")
        print(f"  - 테슬라의 리스크는?")
        print(f"  - 구글의 AI 기술에 대해 알려줘")
        print(f"  - iPhone과 관련된 기회 요소는?")
        print(f"  - 엔비디아의 GPU 기술은?")
        print(f"\n{Colors.WARNING}현재 설정:{Colors.ENDC}")
        print(f"  디버그 모드: {Colors.OKGREEN if self.debug_mode else Colors.WARNING}{'ON' if self.debug_mode else 'OFF'}{Colors.ENDC}")
        print(f"  Vector 검색: {Colors.OKGREEN if self.use_vector_search else Colors.WARNING}{'ON' if self.use_vector_search else 'OFF'}{Colors.ENDC}\n")
    
    def format_result(self, result: Dict) -> str:
        """결과 포맷팅"""
        output = []
        
        # 답변 출력
        if result.get("answer"):
            output.append(f"\n{Colors.OKGREEN}{Colors.BOLD}답변:{Colors.ENDC}")
            output.append(f"{Colors.OKGREEN}{result['answer']}{Colors.ENDC}\n")
        
        # 통합 결과 출력
        merged_results = result.get("merged_results", [])
        if merged_results:
            output.append(f"{Colors.OKCYAN}{Colors.BOLD}검색 결과 ({len(merged_results)}개):{Colors.ENDC}\n")
            
            for i, res in enumerate(merged_results[:10], 1):
                entity = res.get("entity") or res.get("description", "")[:60]
                description = res.get("description", "")
                
                # 점수 정보
                graph_score = res.get("graph_score", 0.0)
                vector_score = res.get("vector_score", 0.0)
                final_score = res.get("final_score", 0.0)
                
                output.append(f"{Colors.BOLD}{i}. {entity}{Colors.ENDC}")
                if description and len(description) > 0:
                    desc_short = description[:100] + "..." if len(description) > 100 else description
                    output.append(f"   {desc_short}")
                
                if self.debug_mode:
                    score_info = []
                    if graph_score > 0:
                        score_info.append(f"Graph: {graph_score:.4f}")
                    if vector_score > 0:
                        score_info.append(f"Vector: {vector_score:.4f}")
                    if score_info:
                        output.append(f"   점수: {', '.join(score_info)} (최종: {final_score:.4f})")
                output.append("")
        else:
            output.append(f"{Colors.WARNING}검색 결과가 없습니다.{Colors.ENDC}\n")
        
        return "\n".join(output)
    
    def print_debug_info(self, query: str, intent: Dict, cypher_query: Optional[str] = None, params: Optional[Dict] = None):
        """디버그 정보 출력"""
        if not self.debug_mode:
            return
        
        print(f"\n{Colors.HEADER}{Colors.BOLD}디버그 정보{Colors.ENDC}")
        print(f"{Colors.HEADER}{'=' * 80}{Colors.ENDC}")
        
        # Intent 정보
        print(f"\n{Colors.OKCYAN}Intent:{Colors.ENDC}")
        target = intent.get("target", {})
        if isinstance(target, dict):
            target_type = target.get("node_type", "unknown")
        else:
            target_type = intent.get("target_entity_type", "unknown")
        
        print(f"  Target: {Colors.BOLD}{target_type}{Colors.ENDC}")
        print(f"  Query Text: {intent.get('query_text', 'N/A')}")
        print(f"  Query Type: {intent.get('query_type', 'N/A')}")
        
        filters = intent.get("filters", {})
        if filters:
            print(f"  Filters:")
            if isinstance(filters, dict):
                for key, value in filters.items():
                    if value:
                        print(f"    {key}: {value}")
            elif isinstance(filters, list):
                for f in filters:
                    if isinstance(f, dict):
                        node_type = f.get("node_type", "unknown")
                        print(f"    {node_type}: {f.get('ticker') or f.get('name', 'N/A')}")
        
        # Cypher 쿼리
        if cypher_query:
            print(f"\n{Colors.OKCYAN}Cypher Query:{Colors.ENDC}")
            print(f"{Colors.OKBLUE}{cypher_query}{Colors.ENDC}")
            if params:
                print(f"\n{Colors.OKCYAN}Parameters:{Colors.ENDC}")
                print(f"{Colors.OKBLUE}{json.dumps(params, ensure_ascii=False, indent=2)}{Colors.ENDC}")
        
        print(f"{Colors.HEADER}{'=' * 80}{Colors.ENDC}\n")
    
    def process_query(self, query: str) -> Optional[Dict]:
        """질의 처리"""
        if not query.strip():
            return None
        
        print(f"\n{Colors.OKCYAN}처리 중...{Colors.ENDC}")
        
        try:
            # Intent 추출
            intent = self.engine.extract_intent(query)
            
            # Cypher 쿼리 생성 (디버그 모드용)
            cypher_query = None
            params = None
            if self.debug_mode:
                try:
                    cypher_query, params = self.query_builder.build_query(intent)
                except Exception as e:
                    print(f"{Colors.WARNING}Cypher 쿼리 생성 실패: {e}{Colors.ENDC}")
            
            # 디버그 정보 출력
            self.print_debug_info(query, intent, cypher_query, params)
            
            # 질의 실행
            result = self.engine.query(
                user_query=query,
                use_vector_search=self.use_vector_search,
                use_graph_search=True,
                generate_answer=True,
                top_k=10
            )
            
            # 결과 출력
            print(self.format_result(result))
            
            # 히스토리에 추가
            self.history.append({
                "query": query,
                "timestamp": datetime.now().isoformat(),
                "result_count": len(result.get("merged_results", [])),
                "intent": intent
            })
            
            return result
            
        except Exception as e:
            print(f"{Colors.FAIL}❌ 오류 발생: {e}{Colors.ENDC}\n")
            return None
    
    def print_history(self):
        """히스토리 출력"""
        if not self.history:
            print(f"{Colors.WARNING}히스토리가 비어있습니다.{Colors.ENDC}\n")
            return
        
        print(f"\n{Colors.HEADER}{Colors.BOLD}질의 히스토리 ({len(self.history)}개){Colors.ENDC}")
        print(f"{Colors.HEADER}{'=' * 80}{Colors.ENDC}\n")
        
        for i, entry in enumerate(self.history[-10:], 1):  # 최근 10개만 표시
            print(f"{Colors.BOLD}{i}.{Colors.ENDC} {entry['query']}")
            print(f"   시간: {entry['timestamp']}")
            print(f"   결과: {entry['result_count']}개")
            print()
    
    def run(self):
        """메인 루프 실행"""
        if not self.initialize():
            return
        
        self.print_header()
        
        while True:
            try:
                query = input(f"{Colors.OKCYAN}질문: {Colors.ENDC}").strip()
                
                if not query:
                    continue
                
                # 명령어 처리
                if query.lower() in ["exit", "quit", "q"]:
                    print(f"\n{Colors.OKGREEN}프로그램을 종료합니다.{Colors.ENDC}\n")
                    break
                elif query.lower() == "help":
                    self.print_help()
                    continue
                elif query.lower() == "debug":
                    self.debug_mode = not self.debug_mode
                    print(f"\n{Colors.OKGREEN}디버그 모드: {'ON' if self.debug_mode else 'OFF'}{Colors.ENDC}\n")
                    continue
                elif query.lower() == "history":
                    self.print_history()
                    continue
                elif query.lower() == "clear":
                    os.system("clear" if os.name != "nt" else "cls")
                    self.print_header()
                    continue
                
                # 질의 처리
                self.process_query(query)
                
            except KeyboardInterrupt:
                print(f"\n\n{Colors.WARNING}프로그램을 종료합니다.{Colors.ENDC}\n")
                break
            except EOFError:
                print(f"\n\n{Colors.WARNING}프로그램을 종료합니다.{Colors.ENDC}\n")
                break
        
        # 리소스 정리
        if self.engine:
            self.engine.close()


def main():
    """메인 함수"""
    parser = argparse.ArgumentParser(description="금융 공시 Knowledge Graph 질의 시스템")
    parser.add_argument(
        "--debug",
        action="store_true",
        help="디버그 모드 활성화 (Intent, Cypher 쿼리 표시)"
    )
    parser.add_argument(
        "--no-vector",
        action="store_true",
        help="Vector 검색 비활성화"
    )
    
    args = parser.parse_args()
    
    interface = QueryInterface(
        debug_mode=args.debug,
        use_vector_search=not args.no_vector
    )
    
    interface.run()


if __name__ == "__main__":
    main()

