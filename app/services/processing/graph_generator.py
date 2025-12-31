"""
Graph Node/Link Data Generator

Phase 4.5: extracted 데이터를 graph_ontology_design.md 스키마에 맞게
Node와 Link 데이터로 변환하는 서비스
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
    
    Examples:
        >>> normalize_id("iPhone 15 Pro")
        'iphone_15_pro'
        >>> normalize_id("Tim Cook")
        'tim_cook'
        >>> normalize_id("Apple TV+")
        'apple_tv'
    """
    if not text:
        return ""
    
    # 소문자 변환
    text = text.lower()
    # 특수문자 제거 또는 언더스코어로 변환
    text = re.sub(r'[^a-z0-9]+', '_', text)
    # 연속된 언더스코어 제거
    text = re.sub(r'_+', '_', text)
    # 앞뒤 언더스코어 제거
    return text.strip('_')


def normalize_product_name(name: str, ticker: str = None) -> str:
    """제품명을 정규화하여 중복 제거 및 일관성 유지
    
    Args:
        name: 제품명
        ticker: 회사 티커
        
    Returns:
        정규화된 제품명
    """
    name = name.strip()
    name_lower = name.lower()
    
    # 티커별 제품명 정규화 규칙
    if ticker == "TSLA":
        # Tesla 관련 정규화
        normalization_map = {
            # Model 시리즈 - "Tesla Model X" 형태로 통일
            'model 3': 'Tesla Model 3',
            'model s': 'Tesla Model S',
            'model x': 'Tesla Model X',
            'model y': 'Tesla Model Y',
            'tesla model 3': 'Tesla Model 3',
            'tesla model s': 'Tesla Model S',
            'tesla model x': 'Tesla Model X',
            'tesla model y': 'Tesla Model Y',
            # Supercharger
            'supercharger': 'Tesla Supercharger',
            'superchargers': 'Tesla Supercharger',
            'tesla supercharger': 'Tesla Supercharger',
            'tesla superchargers': 'Tesla Supercharger',
            # FSD
            'fsd': 'Full Self-Driving (FSD)',
            'full self-driving': 'Full Self-Driving (FSD)',
            'fsd (supervised)': 'Full Self-Driving (FSD)',
            # NACS
            'nacs': 'NACS',
            'north american charging standard': 'NACS',
            # Tesla 브랜드 자체는 제품이 아님
            'tesla': None,
        }
        
        if name_lower in normalization_map:
            return normalization_map[name_lower]
    
    elif ticker == "AAPL":
        # Apple 관련 정규화 (중복 제거)
        normalization_map = {
            'apple': None,  # 브랜드 자체는 제품이 아님
        }
        if name_lower in normalization_map:
            return normalization_map[name_lower]
    
    elif ticker == "GOOGL":
        normalization_map = {
            'google': None,  # 브랜드/회사명
            'search': 'Google Search',
        }
        if name_lower in normalization_map:
            return normalization_map[name_lower]
    
    elif ticker == "MSFT":
        normalization_map = {
            'microsoft': None,  # 브랜드/회사명
            'copilot': 'Microsoft Copilot',
        }
        if name_lower in normalization_map:
            return normalization_map[name_lower]
    
    return name


# Company 기본 정보 (나중에 외부 파일이나 API로 확장 가능)
COMPANY_INFO = {
    "AAPL": {
        "name": "Apple Inc.",
        "sector": "Technology",
        "description": "Apple Inc.는 스마트폰, 개인용 컴퓨터, 태블릿, 웨어러블 디바이스 등을 설계, 제조 및 판매하는 글로벌 기술 기업입니다. iPhone, iPad, Mac, Apple Watch 등의 하드웨어 제품과 iOS, macOS 등의 소프트웨어, 그리고 iCloud, App Store, Apple Music 등의 서비스를 제공합니다."
    },
    "AMZN": {
        "name": "Amazon.com, Inc.",
        "sector": "Consumer Discretionary",
        "description": "Amazon.com, Inc.는 전자상거래, 클라우드 컴퓨팅(AWS), 디지털 스트리밍, 인공지능 등 다양한 사업을 영위하는 글로벌 기술 기업입니다. 세계 최대 온라인 소매업체이자 클라우드 서비스 제공업체입니다."
    },
    "GOOGL": {
        "name": "Alphabet Inc.",
        "sector": "Communication Services",
        "description": "Alphabet Inc.는 Google의 모회사로서 검색 엔진, 온라인 광고, 클라우드 컴퓨팅, 유튜브, Android OS 등을 운영하는 글로벌 기술 기업입니다. AI 및 자율주행(Waymo) 등 혁신 기술에도 투자하고 있습니다."
    },
    "META": {
        "name": "Meta Platforms, Inc.",
        "sector": "Communication Services",
        "description": "Meta Platforms, Inc.는 Facebook, Instagram, WhatsApp, Messenger 등 소셜 미디어 플랫폼을 운영하며, 메타버스와 VR/AR 기술(Reality Labs)에 집중 투자하는 글로벌 기술 기업입니다."
    },
    "MSFT": {
        "name": "Microsoft Corporation",
        "sector": "Technology",
        "description": "Microsoft Corporation은 Windows, Office, Azure 클라우드, LinkedIn, Xbox 등을 운영하는 글로벌 소프트웨어 및 기술 기업입니다. 기업용 소프트웨어와 클라우드 서비스 분야의 선도 기업입니다."
    },
    "NVDA": {
        "name": "NVIDIA Corporation",
        "sector": "Technology",
        "description": "NVIDIA Corporation은 GPU(Graphics Processing Unit)와 AI 컴퓨팅 플랫폼을 설계 및 제조하는 글로벌 반도체 기업입니다. 게이밍, 데이터센터, 자율주행, AI/ML 분야에서 핵심적인 역할을 하고 있습니다."
    },
    "TSLA": {
        "name": "Tesla, Inc.",
        "sector": "Consumer Discretionary",
        "description": "Tesla, Inc.는 전기차(EV), 에너지 저장 시스템, 태양광 패널 등을 설계, 제조 및 판매하는 글로벌 전기차 및 청정에너지 기업입니다. Model S, Model 3, Model X, Model Y 등의 차량을 생산합니다."
    }
}


def generate_company_node(ticker: str) -> Dict:
    """Company 노드 생성
    
    Args:
        ticker: 티커 심볼 (예: "AAPL")
        
    Returns:
        Company 노드 딕셔너리
    """
    company_info = COMPANY_INFO.get(ticker, {
        "name": f"{ticker} Inc.",
        "sector": "Unknown",
        "description": f"{ticker} 기업 정보"
    })
    
    return {
        "id": ticker,
        "node_type": "Company",
        "ticker": ticker,
        "name": company_info["name"],
        "sector": company_info["sector"],
        "description": company_info["description"],
        "node_style": "static"
    }


def classify_product(product_name: str) -> Dict[str, str]:
    """Product의 product_type과 category를 분류
    
    Args:
        product_name: 제품명
        
    Returns:
        {"product_type": str, "category": str}
    """
    name_lower = product_name.lower()
    
    # Hardware 제품
    if any(keyword in name_lower for keyword in ["iphone", "ipad", "mac", "watch", "airpods", "homepod"]):
        if "iphone" in name_lower:
            return {"product_type": "hardware", "category": "smartphone"}
        elif "ipad" in name_lower:
            return {"product_type": "hardware", "category": "tablet"}
        elif "mac" in name_lower:
            return {"product_type": "hardware", "category": "computer"}
        elif "watch" in name_lower or "airpods" in name_lower or "homepod" in name_lower:
            return {"product_type": "hardware", "category": "wearable"}
        else:
            return {"product_type": "hardware", "category": "other"}
    
    # Service 제품
    elif any(keyword in name_lower for keyword in ["music", "tv+", "arcade", "fitness", "news", "podcasts", "icloud", "app store", "apple pay", "apple card"]):
        if "music" in name_lower or "tv" in name_lower or "arcade" in name_lower or "fitness" in name_lower:
            return {"product_type": "service", "category": "streaming_service"}
        elif "pay" in name_lower or "card" in name_lower:
            return {"product_type": "service", "category": "financial_service"}
        elif "icloud" in name_lower or "app store" in name_lower:
            return {"product_type": "platform", "category": "software_platform"}
        else:
            return {"product_type": "service", "category": "other"}
    
    # Software
    elif any(keyword in name_lower for keyword in ["ios", "macos", "watchos", "ipados"]):
        return {"product_type": "software", "category": "operating_system"}
    
    # 기본값
    else:
        return {"product_type": "other", "category": "other"}


def is_non_product(name: str, ticker: str = None) -> bool:
    """제품이 아닌 항목인지 확인 (금융 상품, 주식, 암호화폐, 타사 제품 등)
    
    Args:
        name: 제품명
        ticker: 회사 티커 (타사 제품 필터링용)
        
    Returns:
        제품이 아니면 True
    """
    name_lower = name.lower()
    
    # 금융 상품 패턴
    financial_patterns = [
        # 채권/노트 패턴 (2028 Notes, 2030 Notes 등)
        r'\d{4}\s*notes?',
        r'\d{4}\s*bonds?',
        r'\d{4}\s*debentures?',
        # Senior Notes 패턴 (3.400% Senior Notes due 2026)
        r'\d+\.\d+%\s*senior\s*notes',
        r'senior\s*notes\s*due\s*\d{4}',
        # 일반 금융 용어
        r'^notes?$',
        r'^bonds?$',
        r'^commercial paper$',
        r'^term debt$',
        r'^credit facility',
        r'^revolving credit',
        # "XXX Notes" 패턴
        r'\bnotes$',
        r'^new\s+.*\s+notes$',
        r'^existing\s+.*\s+notes$',
        r'^u\.s\.\s*notes$',
        r'^euro\s*notes$',
    ]
    
    for pattern in financial_patterns:
        if re.search(pattern, name_lower):
            return True
    
    # 주식 클래스 패턴
    stock_patterns = [
        r'^class\s+[a-z]\s+(common\s+)?stock$',
        r'^common\s+stock$',
        r'^preferred\s+stock$',
    ]
    
    for pattern in stock_patterns:
        if re.search(pattern, name_lower):
            return True
    
    # 암호화폐 (회사 제품이 아님)
    crypto_list = ['bitcoin', 'ethereum', 'dogecoin', 'cryptocurrency', 'crypto']
    if name_lower in crypto_list:
        return True
    
    # 타사 제품 필터링 (해당 회사 제품이 아닌 경우)
    # 티커별 자사 제품 매핑
    company_products = {
        'AAPL': ['ios', 'ipados', 'macos', 'watchos', 'tvos', 'iphone', 'ipad', 'mac', 'apple'],
        'GOOGL': ['android', 'chrome', 'chromeos', 'google', 'pixel', 'youtube'],
        'MSFT': ['windows', 'xbox', 'azure', 'office', 'microsoft', 'surface'],
        'META': ['facebook', 'instagram', 'whatsapp', 'messenger', 'meta', 'oculus'],
        'AMZN': ['alexa', 'kindle', 'fire', 'echo', 'aws', 'amazon', 'prime'],
        'NVDA': ['nvidia', 'geforce', 'cuda', 'tegra', 'shield'],
        'TSLA': ['tesla', 'autopilot', 'supercharger', 'powerwall', 'megapack'],
    }
    
    # 다른 회사의 독점 제품 목록
    exclusive_products = {
        'ios': 'AAPL',
        'ipados': 'AAPL',
        'macos': 'AAPL',
        'iphone': 'AAPL',
        'ipad': 'AAPL',
        'android': 'GOOGL',
        'chrome': 'GOOGL',
        'windows': 'MSFT',
        'xbox': 'MSFT',
    }
    
    # 현재 티커가 제공된 경우, 타사 독점 제품 필터링
    if ticker:
        ticker_upper = ticker.upper()
        for product, owner in exclusive_products.items():
            if name_lower == product and ticker_upper != owner:
                return True
    
    return False


def generate_product_nodes(ticker: str, extracted_files: List[Path]) -> List[Dict]:
    """Product 노드 생성
    
    Args:
        ticker: 티커 심볼
        extracted_files: extracted JSON 파일 경로 리스트
        
    Returns:
        Product 노드 리스트
    """
    # 모든 extracted 파일에서 mentioned_products_global 수집
    all_products = {}
    filtered_count = 0
    
    for extracted_file in extracted_files:
        try:
            with open(extracted_file, 'r', encoding='utf-8') as f:
                data = json.load(f)
            
            products_global = data.get("mentioned_products_global", [])
            for product in products_global:
                product_name = product.get("name", "").strip()
                if not product_name:
                    continue
                
                # 제품이 아닌 항목 필터링 (금융 상품, 주식, 암호화폐, 타사 제품 등)
                if is_non_product(product_name, ticker):
                    filtered_count += 1
                    continue
                
                # 제품명 정규화 (중복 제거 및 일관성 유지)
                normalized_name = normalize_product_name(product_name, ticker)
                if normalized_name is None:
                    # 브랜드명 등 제품이 아닌 항목
                    filtered_count += 1
                    continue
                
                # 중복 제거 (정규화된 이름 기준, 대소문자 무시)
                name_key = normalized_name.lower()
                if name_key not in all_products:
                    # 정규화된 이름으로 업데이트
                    product_copy = product.copy()
                    product_copy["name"] = normalized_name
                    all_products[name_key] = product_copy
        except Exception as e:
            logger.warning(f"Error reading {extracted_file}: {e}")
    
    if filtered_count > 0:
        logger.info(f"Filtered {filtered_count} non-product items (financial instruments, stocks, etc.)")
    
    # Product 노드 생성
    product_nodes = []
    for product_name, product_data in all_products.items():
        normalized_name = normalize_id(product_name)
        product_id = f"product_{ticker.lower()}_{normalized_name}"
        
        # 분류 정보 가져오기
        classification = classify_product(product_name)
        
        # description 생성 (간단한 설명)
        description = f"{product_name}은(는) {ticker}의 {classification['category']} 제품입니다."
        
        product_node = {
            "id": product_id,
            "node_type": "Product",
            "name": product_data.get("name", product_name),
            "product_type": classification["product_type"],
            "category": classification["category"],
            "description": description,
            "node_style": "static"
        }
        
        product_nodes.append(product_node)
    
    logger.info(f"Generated {len(product_nodes)} Product nodes for {ticker}")
    return product_nodes


def generate_person_nodes(ticker: str, extracted_files: List[Path]) -> List[Dict]:
    """Person 노드 생성
    
    Args:
        ticker: 티커 심볼
        extracted_files: extracted JSON 파일 경로 리스트
        
    Returns:
        Person 노드 리스트
    """
    # 모든 extracted 파일에서 mentioned_persons_global 수집
    all_persons = {}
    
    for extracted_file in extracted_files:
        try:
            with open(extracted_file, 'r', encoding='utf-8') as f:
                data = json.load(f)
            
            persons_global = data.get("mentioned_persons_global", [])
            for person in persons_global:
                person_name = person.get("name", "").strip()
                if not person_name:
                    continue
                
                # 중복 제거 (이름 기준)
                name_key = person_name.lower()
                if name_key not in all_persons:
                    all_persons[name_key] = person
        except Exception as e:
            logger.warning(f"Error reading {extracted_file}: {e}")
            continue
    
    # Person 노드 생성
    person_nodes = []
    for person_name, person_data in all_persons.items():
        normalized_name = normalize_id(person_name)
        person_id = f"person_{ticker.lower()}_{normalized_name}"
        
        role = person_data.get("role", "")
        role_text = f" {role}" if role else ""
        
        # description 생성
        description = f"{person_data.get('name', person_name)}은(는){role_text}로서 {ticker}와 관련이 있습니다."
        
        person_node = {
            "id": person_id,
            "node_type": "Person",
            "name": person_data.get("name", person_name),
            "description": description,
            "node_style": "static"
        }
        
        person_nodes.append(person_node)
    
    logger.info(f"Generated {len(person_nodes)} Person nodes for {ticker}")
    return person_nodes


def generate_make_links(company_id: str, product_nodes: List[Dict]) -> List[Dict]:
    """MAKE 링크 생성 (Company → Product)
    
    Args:
        company_id: Company 노드 ID
        product_nodes: Product 노드 리스트
        
    Returns:
        MAKE 링크 리스트
    """
    links = []
    created_at = datetime.utcnow().isoformat() + "Z"
    
    for product_node in product_nodes:
        link = {
            "from": company_id,
            "to": product_node["id"],
            "relationship_type": "MAKE",
            "created_at": created_at,
            "metadata": {
                "launch_date": None,
                "status": "active"
            }
        }
        links.append(link)
    
    logger.info(f"Generated {len(links)} MAKE links")
    return links


def generate_has_relation_links(
    company_id: str,
    person_nodes: List[Dict],
    extracted_files: List[Path]
) -> List[Dict]:
    """HAS_RELATION 링크 생성 (Company → Person)
    
    Args:
        company_id: Company 노드 ID
        person_nodes: Person 노드 리스트
        extracted_files: extracted JSON 파일 경로 리스트 (role 정보 추출용)
        
    Returns:
        HAS_RELATION 링크 리스트
    """
    # Person 이름 -> role 매핑 생성
    person_roles = {}
    for extracted_file in extracted_files:
        try:
            with open(extracted_file, 'r', encoding='utf-8') as f:
                data = json.load(f)
            
            persons_global = data.get("mentioned_persons_global", [])
            for person in persons_global:
                person_name = person.get("name", "").strip()
                role = person.get("role", "")
                if person_name and role:
                    name_key = person_name.lower()
                    if name_key not in person_roles:
                        person_roles[name_key] = role
        except Exception as e:
            logger.warning(f"Error reading {extracted_file}: {e}")
            continue
    
    links = []
    created_at = datetime.utcnow().isoformat() + "Z"
    
    for person_node in person_nodes:
        person_name_key = person_node["name"].lower()
        role = person_roles.get(person_name_key, "Unknown")
        
        link = {
            "from": company_id,
            "to": person_node["id"],
            "relationship_type": "HAS_RELATION",
            "role": role,
            "created_at": created_at,
            "metadata": {
                "start_date": None,
                "end_date": None
            }
        }
        links.append(link)
    
    logger.info(f"Generated {len(links)} HAS_RELATION links")
    return links


def generate_static_graph(ticker: str, extracted_dir: Path) -> Dict:
    """Static 노드와 링크를 생성하여 반환
    
    Args:
        ticker: 티커 심볼
        extracted_dir: extracted 데이터 디렉토리 경로
        
    Returns:
        {
            "ticker": str,
            "generated_at": str,
            "nodes": {
                "Company": List[Dict],
                "Product": List[Dict],
                "Person": List[Dict]
            },
            "links": List[Dict]
        }
    """
    logger.info(f"Generating static graph for {ticker}")
    
    # 1. Company 노드 생성
    company_node = generate_company_node(ticker)
    
    # 2. Product 노드 생성
    extracted_files = list(extracted_dir.rglob("*.json"))
    if not extracted_files:
        logger.warning(f"No extracted files found in {extracted_dir}")
        product_nodes = []
    else:
        product_nodes = generate_product_nodes(ticker, extracted_files)
    
    # 3. Person 노드 생성
    if not extracted_files:
        person_nodes = []
    else:
        person_nodes = generate_person_nodes(ticker, extracted_files)
    
    # 4. 링크 생성
    make_links = generate_make_links(company_node["id"], product_nodes)
    has_relation_links = generate_has_relation_links(
        company_node["id"], person_nodes, extracted_files
    )
    
    result = {
        "ticker": ticker,
        "generated_at": datetime.utcnow().isoformat() + "Z",
        "nodes": {
            "Company": [company_node],
            "Product": product_nodes,
            "Person": person_nodes
        },
        "links": make_links + has_relation_links
    }
    
    logger.info(
        f"Static graph generated: "
        f"Company=1, Products={len(product_nodes)}, "
        f"Persons={len(person_nodes)}, Links={len(result['links'])}"
    )
    
    return result


