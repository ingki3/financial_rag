"""
Dynamic Graph Generator

Phase 6: extracted 데이터에서 Dynamic 노드(Document, Section, Risk, Opportunity, Event, Technology)와
링크를 생성하여 {TICKER}_dynamic_graph.json 파일로 저장합니다.
"""

import json
import re
import logging
from pathlib import Path
from typing import Dict, List, Optional
from datetime import datetime

logger = logging.getLogger(__name__)


def normalize_id(text: str) -> str:
    """텍스트를 ID로 사용 가능한 형태로 정규화
    
    Args:
        text: 정규화할 텍스트
        
    Returns:
        정규화된 ID 문자열 (소문자, 언더스코어로 구분)
    """
    if not text:
        return ""
    
    text = text.lower()
    text = re.sub(r'[^a-z0-9]+', '_', text)
    text = re.sub(r'_+', '_', text)
    return text.strip('_')


def normalize_filing_type(filing_type: str) -> str:
    """Filing type을 정규화 (10-K -> 10k)"""
    return filing_type.lower().replace('-', '')


# ============================================================================
# Node Generators
# ============================================================================

def generate_document_node(extracted_data: Dict) -> Dict:
    """Document 노드 생성
    
    Args:
        extracted_data: extracted JSON 데이터
        
    Returns:
        Document 노드 딕셔너리
    """
    ticker = extracted_data.get("ticker", "").upper()
    filing_type = extracted_data.get("filing_type", "")
    accession_number = extracted_data.get("accession_number", "")
    
    filing_type_lower = normalize_filing_type(filing_type)
    doc_id = f"doc_{ticker.lower()}_{filing_type_lower}_{accession_number}"
    
    return {
        "id": doc_id,
        "node_type": "Document",
        "ticker": ticker,
        "filing_type": filing_type,
        "accession_number": accession_number,
        "year": extracted_data.get("year"),
        "quarter": extracted_data.get("quarter"),
        "sections_included": extracted_data.get("sections_included", []),
        "extracted_at": extracted_data.get("extracted_at"),
        "node_style": "dynamic",
        "metadata": {
            "extraction_stats": extracted_data.get("extraction_stats", {})
        }
    }


def generate_section_nodes(extracted_data: Dict) -> List[Dict]:
    """Section 노드 생성
    
    Args:
        extracted_data: extracted JSON 데이터
        
    Returns:
        Section 노드 리스트
    """
    ticker = extracted_data.get("ticker", "").upper()
    filing_type = extracted_data.get("filing_type", "")
    year = extracted_data.get("year")
    accession_number = extracted_data.get("accession_number", "")
    sections_included = extracted_data.get("sections_included", [])
    
    filing_type_lower = normalize_filing_type(filing_type)
    
    section_nodes = []
    for section_name in sections_included:
        section_id = f"section_{ticker.lower()}_{filing_type_lower}_{year}_{normalize_id(section_name)}"
        
        section_node = {
            "id": section_id,
            "node_type": "Section",
            "section_name": section_name,
            "filing_type": filing_type,
            "ticker": ticker,
            "year": year,
            "accession_number": accession_number,
            "node_style": "dynamic"
        }
        section_nodes.append(section_node)
    
    return section_nodes


def generate_entity_nodes(
    extracted_data: Dict,
    category: str,
    node_type: str,
    id_prefix: str
) -> List[Dict]:
    """Risk/Opportunity/Event/Technology 노드 생성 (공통 로직)
    
    Args:
        extracted_data: extracted JSON 데이터
        category: 카테고리 키 (risks, opportunities, events, technologies)
        node_type: 노드 타입 (Risk, Opportunity, Event, Technology)
        id_prefix: ID 접두사 (risk, opp, event, tech)
        
    Returns:
        노드 리스트
    """
    ticker = extracted_data.get("ticker", "").upper()
    year = extracted_data.get("year")
    filing_type = extracted_data.get("filing_type", "")
    accession_number = extracted_data.get("accession_number", "")
    extracted_at = extracted_data.get("extracted_at")
    
    entities = extracted_data.get(category, [])
    nodes = []
    
    for entity in entities:
        entity_name = entity.get("entity", "")
        if not entity_name:
            continue
        
        normalized_entity = normalize_id(entity_name)
        node_id = f"{id_prefix}_{ticker.lower()}_{normalized_entity}_{year}"
        
        node = {
            "id": node_id,
            "node_type": node_type,
            "ticker": ticker,
            "entity": entity_name,
            "description": entity.get("description", ""),
            "node_style": "dynamic",
            "extracted_at": extracted_at,
            "metadata": {
                "source_section": entity.get("source_section", ""),
                "filing_type": filing_type,
                "accession_number": accession_number
            },
            # 원본 데이터 보존 (링크 생성시 필요)
            "_mentioned_products": entity.get("mentioned_products", []),
            "_mentioned_persons": entity.get("mentioned_persons", []),
            "_mentioned_companies": entity.get("mentioned_companies", [])
        }
        nodes.append(node)
    
    return nodes


def generate_risk_nodes(extracted_data: Dict) -> List[Dict]:
    """Risk 노드 생성"""
    return generate_entity_nodes(extracted_data, "risks", "Risk", "risk")


def generate_opportunity_nodes(extracted_data: Dict) -> List[Dict]:
    """Opportunity 노드 생성"""
    return generate_entity_nodes(extracted_data, "opportunities", "Opportunity", "opp")


def generate_event_nodes(extracted_data: Dict) -> List[Dict]:
    """Event 노드 생성"""
    return generate_entity_nodes(extracted_data, "events", "Event", "event")


def generate_technology_nodes(extracted_data: Dict) -> List[Dict]:
    """Technology 노드 생성"""
    return generate_entity_nodes(extracted_data, "technologies", "Technology", "tech")


# ============================================================================
# Link Generators
# ============================================================================

def generate_is_included_links(section_nodes: List[Dict], doc_node: Dict) -> List[Dict]:
    """IS_INCLUDED 링크 생성 (Section → Document)
    
    Args:
        section_nodes: Section 노드 리스트
        doc_node: Document 노드
        
    Returns:
        IS_INCLUDED 링크 리스트
    """
    links = []
    created_at = datetime.utcnow().isoformat() + "Z"
    
    for idx, section_node in enumerate(section_nodes):
        link = {
            "from": section_node["id"],
            "to": doc_node["id"],
            "relationship_type": "IS_INCLUDED",
            "created_at": created_at,
            "metadata": {
                "section_order": idx + 1  # 1-based
            }
        }
        links.append(link)
    
    return links


def generate_is_extracted_from_links(
    dynamic_nodes: List[Dict],
    section_nodes: List[Dict],
    extracted_data: Dict
) -> List[Dict]:
    """IS_EXTRACTED_FROM 링크 생성 (Risk/Opp/Event/Tech → Section)
    
    Args:
        dynamic_nodes: Dynamic 노드 리스트 (Risk, Opportunity, Event, Technology)
        section_nodes: Section 노드 리스트
        extracted_data: extracted JSON 데이터 (year 추출용)
        
    Returns:
        IS_EXTRACTED_FROM 링크 리스트
    """
    links = []
    created_at = datetime.utcnow().isoformat() + "Z"
    
    # Section 노드 매핑 생성 (section_name -> section_id)
    ticker = extracted_data.get("ticker", "").upper()
    filing_type = extracted_data.get("filing_type", "")
    year = extracted_data.get("year")
    filing_type_lower = normalize_filing_type(filing_type)
    
    section_map = {}
    for section_node in section_nodes:
        section_name = section_node.get("section_name", "")
        section_map[section_name] = section_node["id"]
    
    for node in dynamic_nodes:
        source_section = node.get("metadata", {}).get("source_section", "")
        
        # Section ID 찾기
        section_id = section_map.get(source_section)
        if not section_id:
            # fallback: 직접 생성
            section_id = f"section_{ticker.lower()}_{filing_type_lower}_{year}_{normalize_id(source_section)}"
        
        link = {
            "from": node["id"],
            "to": section_id,
            "relationship_type": "IS_EXTRACTED_FROM",
            "created_at": created_at,
            "metadata": {
                "extraction_method": "llm_extraction"
            }
        }
        links.append(link)
    
    return links


def generate_has_links(ticker: str, nodes: List[Dict], link_type: str) -> List[Dict]:
    """HAS_* 링크 생성 (Company → Dynamic Node)
    
    Args:
        ticker: 티커 심볼
        nodes: Dynamic 노드 리스트
        link_type: 링크 타입 (HAS_RISKS, HAS_OPPORTUNITIES, HAS_EVENTS, HAS_TECHNOLOGIES)
        
    Returns:
        HAS_* 링크 리스트
    """
    links = []
    created_at = datetime.utcnow().isoformat() + "Z"
    
    for node in nodes:
        link = {
            "from": ticker.upper(),
            "to": node["id"],
            "relationship_type": link_type,
            "created_at": created_at
        }
        links.append(link)
    
    return links


def generate_is_mentioned_in_links(
    dynamic_nodes: List[Dict],
    static_nodes: Dict,
    extracted_data: Dict
) -> List[Dict]:
    """IS_MENTIONED_IN 링크 생성 (Product/Person/Company → Dynamic Node)
    
    Args:
        dynamic_nodes: Dynamic 노드 리스트
        static_nodes: Static Graph의 nodes 딕셔너리
        extracted_data: extracted JSON 데이터
        
    Returns:
        IS_MENTIONED_IN 링크 리스트
    """
    links = []
    created_at = datetime.utcnow().isoformat() + "Z"
    ticker = extracted_data.get("ticker", "").upper()
    
    # Static 노드 매핑 생성 (name_lower -> id)
    product_map = {}
    for product in static_nodes.get("Product", []):
        name_lower = product.get("name", "").lower()
        product_map[name_lower] = product["id"]
    
    person_map = {}
    for person in static_nodes.get("Person", []):
        name_lower = person.get("name", "").lower()
        person_map[name_lower] = person["id"]
    
    for node in dynamic_nodes:
        node_type = node.get("node_type", "").lower()
        
        # mentioned_products 처리
        for product in node.get("_mentioned_products", []):
            product_name = product.get("name", "").lower()
            product_id = product_map.get(product_name)
            
            if product_id:
                link = {
                    "from": product_id,
                    "to": node["id"],
                    "relationship_type": "IS_MENTIONED_IN",
                    "mention_context": product.get("mention_context", ""),
                    "created_at": created_at,
                    "metadata": {
                        "mention_type": node_type
                    }
                }
                links.append(link)
        
        # mentioned_persons 처리
        for person in node.get("_mentioned_persons", []):
            person_name = person.get("name", "").lower()
            person_id = person_map.get(person_name)
            
            if person_id:
                link = {
                    "from": person_id,
                    "to": node["id"],
                    "relationship_type": "IS_MENTIONED_IN",
                    "mention_context": person.get("mention_context", ""),
                    "created_at": created_at,
                    "metadata": {
                        "mention_type": node_type
                    }
                }
                links.append(link)
        
        # mentioned_companies 처리
        for company in node.get("_mentioned_companies", []):
            company_ticker = company.get("ticker") or company.get("name", "")
            if company_ticker:
                company_ticker = company_ticker.upper()
                link = {
                    "from": company_ticker,
                    "to": node["id"],
                    "relationship_type": "IS_MENTIONED_IN",
                    "mention_context": company.get("mention_context", ""),
                    "created_at": created_at,
                    "metadata": {
                        "mention_type": node_type
                    }
                }
                links.append(link)
    
    return links


# ============================================================================
# Main Generator
# ============================================================================

def generate_dynamic_graph(
    ticker: str,
    extracted_files: List[Path],
    static_graph: Dict,
    with_embedding: bool = True
) -> Dict:
    """전체 Dynamic Graph 생성
    
    Args:
        ticker: 티커 심볼
        extracted_files: extracted JSON 파일 경로 리스트
        static_graph: Static Graph 데이터
        with_embedding: embedding 생성 여부 (기본 True)
        
    Returns:
        Dynamic Graph 딕셔너리
    """
    logger.info(f"Generating dynamic graph for {ticker}")
    
    all_nodes = {
        "Document": [],
        "Section": [],
        "Risk": [],
        "Opportunity": [],
        "Event": [],
        "Technology": []
    }
    all_links = []
    
    # 중복 체크용 set
    seen_node_ids = {
        "Document": set(),
        "Section": set(),
        "Risk": set(),
        "Opportunity": set(),
        "Event": set(),
        "Technology": set()
    }
    
    for extracted_file in extracted_files:
        try:
            with open(extracted_file, 'r', encoding='utf-8') as f:
                extracted_data = json.load(f)
        except Exception as e:
            logger.warning(f"Error reading {extracted_file}: {e}")
            continue
        
        # 1. Document 노드 생성
        doc_node = generate_document_node(extracted_data)
        if doc_node["id"] not in seen_node_ids["Document"]:
            all_nodes["Document"].append(doc_node)
            seen_node_ids["Document"].add(doc_node["id"])
        
        # 2. Section 노드 생성
        section_nodes = generate_section_nodes(extracted_data)
        for node in section_nodes:
            if node["id"] not in seen_node_ids["Section"]:
                all_nodes["Section"].append(node)
                seen_node_ids["Section"].add(node["id"])
        
        # 3. Risk/Opportunity/Event/Technology 노드 생성
        risk_nodes = generate_risk_nodes(extracted_data)
        opp_nodes = generate_opportunity_nodes(extracted_data)
        event_nodes = generate_event_nodes(extracted_data)
        tech_nodes = generate_technology_nodes(extracted_data)
        
        for node in risk_nodes:
            if node["id"] not in seen_node_ids["Risk"]:
                all_nodes["Risk"].append(node)
                seen_node_ids["Risk"].add(node["id"])
        
        for node in opp_nodes:
            if node["id"] not in seen_node_ids["Opportunity"]:
                all_nodes["Opportunity"].append(node)
                seen_node_ids["Opportunity"].add(node["id"])
        
        for node in event_nodes:
            if node["id"] not in seen_node_ids["Event"]:
                all_nodes["Event"].append(node)
                seen_node_ids["Event"].add(node["id"])
        
        for node in tech_nodes:
            if node["id"] not in seen_node_ids["Technology"]:
                all_nodes["Technology"].append(node)
                seen_node_ids["Technology"].add(node["id"])
        
        # 4. 링크 생성
        dynamic_nodes = risk_nodes + opp_nodes + event_nodes + tech_nodes
        
        # IS_INCLUDED
        all_links.extend(generate_is_included_links(section_nodes, doc_node))
        
        # IS_EXTRACTED_FROM
        all_links.extend(generate_is_extracted_from_links(
            dynamic_nodes, section_nodes, extracted_data
        ))
        
        # HAS_* 링크
        all_links.extend(generate_has_links(ticker, risk_nodes, "HAS_RISKS"))
        all_links.extend(generate_has_links(ticker, opp_nodes, "HAS_OPPORTUNITIES"))
        all_links.extend(generate_has_links(ticker, event_nodes, "HAS_EVENTS"))
        all_links.extend(generate_has_links(ticker, tech_nodes, "HAS_TECHNOLOGIES"))
        
        # IS_MENTIONED_IN
        all_links.extend(generate_is_mentioned_in_links(
            dynamic_nodes, static_graph.get("nodes", {}), extracted_data
        ))
    
    # 노드에서 임시 필드 제거
    for node_type in ["Risk", "Opportunity", "Event", "Technology"]:
        for node in all_nodes[node_type]:
            node.pop("_mentioned_products", None)
            node.pop("_mentioned_persons", None)
            node.pop("_mentioned_companies", None)
    
    # Embedding 생성
    if with_embedding:
        try:
            from app.services.shared.embedding_generator import add_embeddings_to_nodes_sync
            
            for node_type in ["Risk", "Opportunity", "Event", "Technology"]:
                if all_nodes[node_type]:
                    logger.info(f"Generating embeddings for {len(all_nodes[node_type])} {node_type} nodes...")
                    all_nodes[node_type] = add_embeddings_to_nodes_sync(all_nodes[node_type])
        except ImportError:
            logger.warning("embedding_generator not available. Skipping embedding generation.")
        except Exception as e:
            logger.error(f"Error generating embeddings: {e}")
    
    result = {
        "ticker": ticker,
        "generated_at": datetime.utcnow().isoformat() + "Z",
        "nodes": all_nodes,
        "links": all_links
    }
    
    # 통계 로그
    total_nodes = sum(len(nodes) for nodes in all_nodes.values())
    logger.info(
        f"Dynamic graph generated: "
        f"Documents={len(all_nodes['Document'])}, "
        f"Sections={len(all_nodes['Section'])}, "
        f"Risks={len(all_nodes['Risk'])}, "
        f"Opportunities={len(all_nodes['Opportunity'])}, "
        f"Events={len(all_nodes['Event'])}, "
        f"Technologies={len(all_nodes['Technology'])}, "
        f"Links={len(all_links)}"
    )
    
    return result

