"""
Risk, Opportunity, Event 노드에 year 필드 추가 스크립트

모든 dynamic_graph.json 파일을 읽어서 Risk, Opportunity, Event 노드에 year 필드를 추가합니다.
year는 노드 ID에서 추출하거나 Document 노드의 year를 참조합니다.
"""

import json
import os
import re
from pathlib import Path
from typing import Dict, List, Optional


def extract_year_from_id(node_id: str) -> Optional[int]:
    """노드 ID에서 연도 추출 (예: risk_aapl_xxx_2024 -> 2024)"""
    # ID 끝부분에서 4자리 연도 패턴 찾기
    match = re.search(r'_(\d{4})$', node_id)
    if match:
        return int(match.group(1))
    return None


def get_year_from_document(nodes: Dict, accession_number: str) -> Optional[int]:
    """Document 노드에서 accession_number로 year 찾기"""
    if "Document" not in nodes:
        return None
    
    for doc in nodes["Document"]:
        if doc.get("accession_number") == accession_number:
            return doc.get("year")
    return None


def add_year_to_nodes(file_path: Path) -> bool:
    """동적 그래프 파일에 year 필드 추가"""
    print(f"처리 중: {file_path.name}")
    
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            data = json.load(f)
        
        nodes = data.get("nodes", {})
        modified = False
        
        # Document 노드들의 accession_number -> year 매핑 생성
        doc_year_map = {}
        if "Document" in nodes:
            for doc in nodes["Document"]:
                acc_num = doc.get("accession_number")
                year = doc.get("year")
                if acc_num and year:
                    doc_year_map[acc_num] = year
        
        # Risk, Opportunity, Event 노드에 year 추가
        for node_type in ["Risk", "Opportunity", "Event"]:
            if node_type not in nodes:
                continue
            
            for node in nodes[node_type]:
                # 이미 year 필드가 있으면 스킵
                if "year" in node:
                    continue
                
                year = None
                
                # 방법 1: 노드 ID에서 연도 추출
                node_id = node.get("id", "")
                year = extract_year_from_id(node_id)
                
                # 방법 2: metadata의 accession_number로 Document에서 찾기
                if not year:
                    metadata = node.get("metadata", {})
                    accession_number = metadata.get("accession_number")
                    if accession_number:
                        year = doc_year_map.get(accession_number)
                
                # 방법 3: extracted_at에서 연도 추출 (최후의 수단)
                if not year:
                    extracted_at = node.get("extracted_at", "")
                    if extracted_at:
                        match = re.search(r'(\d{4})', extracted_at)
                        if match:
                            year = int(match.group(1))
                
                if year:
                    node["year"] = year
                    modified = True
        
        if modified:
            # 백업 생성
            backup_path = file_path.with_suffix('.json.bak')
            if not backup_path.exists():
                with open(backup_path, 'w', encoding='utf-8') as f:
                    json.dump(data, f, ensure_ascii=False, indent=2)
                print(f"  백업 생성: {backup_path.name}")
            
            # 수정된 데이터 저장
            with open(file_path, 'w', encoding='utf-8') as f:
                json.dump(data, f, ensure_ascii=False, indent=2)
            print(f"  ✅ year 필드 추가 완료")
            return True
        else:
            print(f"  ⏭️  수정 사항 없음 (이미 year 필드가 있거나 노드 없음)")
            return False
            
    except Exception as e:
        print(f"  ❌ 오류 발생: {e}")
        return False


def main():
    """메인 함수"""
    graph_dir = Path("data/graph")
    
    if not graph_dir.exists():
        print(f"❌ 디렉토리 없음: {graph_dir}")
        return
    
    # 모든 dynamic_graph.json 파일 찾기
    dynamic_files = list(graph_dir.glob("*_dynamic_graph.json"))
    
    if not dynamic_files:
        print("❌ dynamic_graph.json 파일을 찾을 수 없습니다.")
        return
    
    print("=" * 80)
    print("Risk, Opportunity, Event 노드에 year 필드 추가")
    print("=" * 80)
    print(f"처리할 파일 수: {len(dynamic_files)}\n")
    
    success_count = 0
    for file_path in sorted(dynamic_files):
        if add_year_to_nodes(file_path):
            success_count += 1
        print()
    
    print("=" * 80)
    print(f"✅ 완료: {success_count}/{len(dynamic_files)} 파일 수정됨")
    print("=" * 80)


if __name__ == "__main__":
    main()


