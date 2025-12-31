#!/usr/bin/env python
"""
질문-답변을 마크다운 파일로 정리하는 스크립트
"""

import sys
from pathlib import Path
import json
from datetime import datetime

# 프로젝트 루트를 Python 경로에 추가
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

def format_qa_to_markdown(input_file: str, output_file: str):
    """질문-답변을 마크다운 형식으로 변환"""
    
    # JSON 파일 읽기
    with open(input_file, 'r', encoding='utf-8') as f:
        data = json.load(f)
    
    successful = [r for r in data['results'] if 'error' not in r]
    
    # 마크다운 생성
    md_content = []
    
    # 헤더
    md_content.append("# 자연어 질의 테스트 - 질문과 답변")
    md_content.append("")
    md_content.append(f"**테스트 일시**: {data.get('timestamp', datetime.now().isoformat())}")
    md_content.append(f"**총 질의 수**: {data['total_queries']}개")
    md_content.append("")
    md_content.append("---")
    md_content.append("")
    
    # 각 질의-답변 쌍
    for i, result in enumerate(successful, 1):
        query = result.get('query', '')
        answer = result.get('answer', '')
        intent = result.get('intent', {})
        merged_results = result.get('merged_results', [])
        timing = result.get('timing', {})
        time_ms = result.get('time_ms', 0)
        
        # Intent 정보
        target = intent.get('target', {})
        if isinstance(target, dict):
            target_type = target.get('node_type', 'unknown')
        else:
            target_type = intent.get('target_entity_type', 'unknown')
        
        query_type = intent.get('query_type', 'unknown')
        query_text = intent.get('query_text', '')
        
        # 질문 섹션
        md_content.append(f"## {i}. {query}")
        md_content.append("")
        
        # 답변
        if answer:
            md_content.append(answer)
            md_content.append("")
        else:
            md_content.append("*답변이 생성되지 않았습니다.*")
            md_content.append("")
        
        md_content.append("---")
        md_content.append("")
    
    # 파일 저장
    output_path = Path(output_file)
    output_path.parent.mkdir(parents=True, exist_ok=True)
    
    with open(output_path, 'w', encoding='utf-8') as f:
        f.write('\n'.join(md_content))
    
    print(f"✅ 마크다운 파일 생성 완료: {output_file}")
    print(f"   총 {len(successful)}개의 질의-답변 쌍이 포함되었습니다.")


if __name__ == "__main__":
    input_file = "test_result/natural_language_query_test.json"
    output_file = "test_result/natural_language_qa.md"
    
    if len(sys.argv) > 1:
        input_file = sys.argv[1]
    if len(sys.argv) > 2:
        output_file = sys.argv[2]
    
    format_qa_to_markdown(input_file, output_file)

