# Implementation Plan (구현 계획)

## 📅 프로젝트 타임라인

| 단계 | 작업 내용 | 예상 소요 시간 |
|------|----------|---------------|
| Phase 1 | 환경 설정 | 2시간 |
| Phase 2 | SEC 공시 다운로드 | 3시간 |
| Phase 3 | 공시 파싱 및 텍스트 추출 | 3시간 |
| Phase 4 | Knowledge Triplet 추출 | 4시간 |
| Phase 5 | Static Graph 생성 (Company, Product, Person) | 2시간 |
| Phase 6 | Dynamic Graph 생성 (Document, Section, Risk, Opp, Event, Tech + Links + Embedding) | 3시간 |
| Phase 7 | Graph DB 저장 | 3시간 |
| Phase 8 | 질의 응답 시스템 | 3시간 |
| Phase 9 | 테스트 및 검증 | 2시간 |
| **총계** | | **25시간** |

---

## Phase 1: 환경 설정 (2시간)

### 1.1 FalkorDB 설치 및 실행
```bash
# Docker를 통한 FalkorDB 실행
docker run -d \
  --name falkordb \
  -p 6379:6379 \
  -p 3000:3000 \
  falkordb/falkordb:latest
```

### 1.2 Python 가상환경 및 의존성 설치
```bash
# 가상환경 생성
python -m venv venv
source venv/bin/activate

# 의존성 설치
pip install -r requirements.txt
```

### 1.3 requirements.txt 생성
```
# Core Dependencies
graphiti-core[falkordb]>=0.5.0
sec-edgar-downloader>=5.0.0
beautifulsoup4>=4.12.0
lxml>=5.0.0

# LLM
openai>=1.0.0
anthropic>=0.20.0

# Utilities
python-dotenv>=1.0.0
tqdm>=4.66.0
aiohttp>=3.9.0

# Development
pytest>=8.0.0
pytest-asyncio>=0.23.0
```

### 1.4 환경 변수 설정 (.env.example)
```
# SEC EDGAR API
SEC_USER_AGENT="Your Name your.email@example.com"

# FalkorDB
FALKORDB_HOST=localhost
FALKORDB_PORT=6379

# LLM (선택 - OpenAI 또는 Anthropic)
OPENAI_API_KEY=sk-...
ANTHROPIC_API_KEY=sk-ant-...

# Graphiti
GRAPHITI_MODEL=gpt-4o-mini
```

---

## Phase 2: SEC 공시 다운로드 (3시간)

### 2.1 다운로더 모듈 구현
**파일**: `app/services/sec_downloader.py`

```python
from sec_edgar_downloader import Downloader
from pathlib import Path
import logging
from typing import List

logger = logging.getLogger(__name__)

class SECFilingDownloader:
    """SEC EDGAR에서 10-K, 10-Q, 8-K 공시 자료를 다운로드하는 클래스"""
    
    TICKERS = ["AAPL", "AMZN", "TSLA", "GOOGL", "MSFT", "META", "NVDA"]
    
    # 공시 유형별 다운로드 설정
    FILING_TYPES = {
        "10-K": 3,   # 연간 보고서: 최근 3년
        "10-Q": 12,  # 분기 보고서: 최근 12분기 (3년)
        "8-K": 20,   # 수시 공시: 최근 20건
    }
    
    def __init__(self, data_dir: str = "./data", user_agent: str = None):
        self.data_dir = Path(data_dir)
        self.user_agent = user_agent
        self.downloader = Downloader(
            company_name="FinancialKG",
            email=user_agent.split()[-1] if user_agent else "user@example.com"
        )
    
    def download_filing(self, ticker: str, filing_type: str, limit: int):
        """특정 티커의 특정 유형 공시 다운로드"""
        save_path = self.data_dir / ticker / filing_type
        save_path.mkdir(parents=True, exist_ok=True)
        
        logger.info(f"Downloading {filing_type} for {ticker} (limit: {limit})...")
        
        self.downloader.get(
            filing_type,
            ticker,
            limit=limit,
            download_details=True
        )
    
    def download_all_filings(self, ticker: str):
        """특정 티커의 모든 유형 공시 다운로드"""
        for filing_type, limit in self.FILING_TYPES.items():
            self.download_filing(ticker, filing_type, limit)
        
    def download_all(self):
        """모든 대상 기업의 모든 공시 다운로드"""
        for ticker in self.TICKERS:
            logger.info(f"=== Downloading filings for {ticker} ===")
            self.download_all_filings(ticker)
            
    def get_downloaded_files(self, ticker: str, filing_type: str) -> List[Path]:
        """다운로드된 파일 목록 반환"""
        filing_dir = self.data_dir / ticker / filing_type
        if not filing_dir.exists():
            return []
        return list(filing_dir.glob("**/*.htm")) + list(filing_dir.glob("**/*.html"))
```

### 2.2 다운로드 스크립트
**파일**: `scripts/01_download_filings.py`

```python
#!/usr/bin/env python
"""SEC 10-K, 10-Q, 8-K 공시 자료 다운로드 스크립트"""
import os
import logging
from dotenv import load_dotenv
from app.services.sec_downloader import SECFilingDownloader

logging.basicConfig(level=logging.INFO)

def main():
    load_dotenv()
    
    downloader = SECFilingDownloader(
        data_dir="./data",
        user_agent=os.getenv("SEC_USER_AGENT")
    )
    
    print("=" * 60)
    print("SEC Filing Downloader")
    print("=" * 60)
    print(f"대상 기업: {', '.join(downloader.TICKERS)}")
    print(f"공시 유형: 10-K (연간), 10-Q (분기), 8-K (수시)")
    print("=" * 60)
    
    downloader.download_all()
    
    print("\n✅ 다운로드 완료!")
    print("저장 위치: ./data/{ticker}/{filing_type}/")

if __name__ == "__main__":
    main()
```

---

## Phase 3: 공시 파싱 및 텍스트 추출 (3시간)

### 3.1 파서 모듈 구현
**파일**: `app/services/filing_parser.py`

```python
from bs4 import BeautifulSoup
from pathlib import Path
from typing import Dict, Optional
import re
import logging

logger = logging.getLogger(__name__)

class FilingParser:
    """10-K, 10-Q, 8-K 파일에서 주요 섹션을 추출하는 클래스"""
    
    # 공시 유형별 섹션 패턴
    SECTION_PATTERNS = {
        "10-K": {
            "business": r"item\s*1[.\s]*business",
            "risk_factors": r"item\s*1a[.\s]*risk\s*factors",
            "mda": r"item\s*7[.\s]*management",
        },
        "10-Q": {
            "mda": r"item\s*2[.\s]*management",
            "risk_factors": r"item\s*1a[.\s]*risk\s*factors",
            "financial_statements": r"item\s*1[.\s]*financial\s*statements",
        },
        "8-K": {
            "results_operations": r"item\s*2\.02",
            "other_events": r"item\s*8\.01",
            "financial_exhibits": r"item\s*9\.01",
        },
    }
    
    def __init__(self, filing_path: str, filing_type: str = "10-K"):
        self.filing_path = Path(filing_path)
        self.filing_type = filing_type
        self.content = None
        self.raw_html = None
        
    def load(self) -> "FilingParser":
        """파일 로드 및 HTML 파싱"""
        with open(self.filing_path, 'r', encoding='utf-8', errors='ignore') as f:
            self.raw_html = f.read()
        soup = BeautifulSoup(self.raw_html, 'lxml')
        self.content = soup.get_text(separator='\n')
        return self
    
    def extract_section(self, section_name: str) -> str:
        """특정 섹션의 텍스트 추출"""
        patterns = self.SECTION_PATTERNS.get(self.filing_type, {})
        pattern = patterns.get(section_name)
        if not pattern or not self.content:
            return ""
        
        # 섹션 시작 찾기
        match = re.search(pattern, self.content, re.IGNORECASE)
        if not match:
            return ""
            
        start_pos = match.start()
        # 다음 섹션까지 추출 (간단한 구현)
        end_pos = min(start_pos + 50000, len(self.content))  # 최대 50k 문자
        
        return self.content[start_pos:end_pos]
        
    def extract_all_sections(self) -> Dict[str, str]:
        """현재 공시 유형의 모든 주요 섹션 추출"""
        patterns = self.SECTION_PATTERNS.get(self.filing_type, {})
        return {
            section: self.extract_section(section)
            for section in patterns.keys()
        }
    
    def get_full_text(self) -> str:
        """전체 텍스트 반환"""
        return self.content or ""
    
    def get_metadata(self) -> Dict[str, str]:
        """공시 메타데이터 추출"""
        return {
            "file_path": str(self.filing_path),
            "filing_type": self.filing_type,
            "text_length": len(self.content) if self.content else 0,
        }
```

### 3.2 파싱 스크립트
**파일**: `scripts/02_parse_filings.py`

```python
#!/usr/bin/env python
"""SEC 공시 파싱 스크립트"""
import os
import json
from pathlib import Path
from dotenv import load_dotenv
from app.services.filing_parser import FilingParser

def main():
    load_dotenv()
    
    data_dir = Path("./data")
    output_dir = Path("./data/parsed")
    output_dir.mkdir(parents=True, exist_ok=True)
    
    tickers = ["AAPL", "AMZN", "TSLA", "GOOGL", "MSFT", "META", "NVDA"]
    filing_types = ["10-K", "10-Q", "8-K"]
    
    for ticker in tickers:
        for filing_type in filing_types:
            filing_dir = data_dir / ticker / filing_type
            if not filing_dir.exists():
                continue
                
            for filing_file in filing_dir.glob("**/*.htm*"):
                print(f"Parsing: {filing_file}")
                
                parser = FilingParser(filing_file, filing_type)
                parser.load()
                
                sections = parser.extract_all_sections()
                metadata = parser.get_metadata()
                
                # 결과 저장
                output_file = output_dir / ticker / f"{filing_file.stem}.json"
                output_file.parent.mkdir(parents=True, exist_ok=True)
                
                with open(output_file, 'w', encoding='utf-8') as f:
                    json.dump({
                        "metadata": metadata,
                        "sections": sections
                    }, f, ensure_ascii=False, indent=2)
    
    print("✅ 파싱 완료!")

if __name__ == "__main__":
    main()
```

---

## Phase 4: Knowledge Triplet 추출 (4시간)

### 4.1 추출기 모듈 구현
**파일**: `src/extractor/triplet_extractor.py`

```python
from openai import OpenAI
import json

class TripletExtractor:
    """LLM을 활용한 Knowledge Triplet 추출 클래스"""
    
    EXTRACTION_PROMPT = """
    다음 텍스트에서 지식 트리플렛을 추출하세요.
    
    추출 대상:
    1. 기회 요소 (Opportunities)
    2. 리스크 요소 (Risks)
    3. 주요 이벤트 (Key Events)
    4. 전략 (Strategies)
    5. 재무 지표 (Financial Metrics)
    
    JSON 형식으로 반환하세요:
    {
        "opportunities": [{"entity": "...", "description": "..."}],
        "risks": [{"entity": "...", "description": "..."}],
        "events": [{"entity": "...", "date": "...", "description": "..."}],
        "strategies": [{"entity": "...", "description": "..."}],
        "financials": [{"metric": "...", "value": "...", "period": "..."}]
    }
    
    텍스트:
    {text}
    """
    
    def __init__(self, model: str = "gpt-4o-mini"):
        self.client = OpenAI()
        self.model = model
        
    def extract(self, text: str) -> dict:
        """텍스트에서 트리플렛 추출"""
        response = self.client.chat.completions.create(
            model=self.model,
            messages=[
                {"role": "system", "content": "당신은 금융 문서 분석 전문가입니다."},
                {"role": "user", "content": self.EXTRACTION_PROMPT.format(text=text)}
            ],
            response_format={"type": "json_object"}
        )
        return json.loads(response.choices[0].message.content)
```

### 4.2 추출 스크립트
**파일**: `scripts/03_extract_triplets.py`

---

## Phase 5: Static Graph 생성 (2시간)

### 5.1 데이터 파이프라인 구조

```
Extracted Data
    ↓
1. Static Node 생성 (Company, Product, Person)
    → {TICKER}_static_graph.json
    ↓
2. Dynamic Node 생성 (Risk, Opportunity, Event, Technology, Section, Document)
    → {TICKER}_dynamic_graph.json
    ↓
3. Link 생성 (Static ↔ Static, Dynamic ↔ Dynamic, Static ↔ Dynamic)
    → 각 JSON 파일에 links 배열로 저장
    ↓
4. Graph DB 적재 (Cypher 쿼리 변환)
```

### 5.2 Static Graph 생성 모듈 구현
**파일**: `app/services/graph_generator.py`

**주요 기능**:
1. **Company Node 생성**
   - 티커당 1개의 Company 노드 생성
   - ID: `{ticker}` (예: `AAPL`)
   - 필수 필드: id, node_type, ticker, name, sector, description, node_style

2. **Product Node 생성**
   - `mentioned_products_global`에서 중복 제거하여 생성
   - ID: `product_{ticker}_{normalized_name}` (예: `product_aapl_iphone_15_pro`)
   - **중요**: Product name은 고유명사 (예: "iPhone 15 Pro", "Tesla Model 3")
   - 필수 필드: id, node_type, name, product_type, category, description, node_style

3. **Person Node 생성**
   - `mentioned_persons_global`에서 중복 제거하여 생성
   - ID: `person_{ticker}_{normalized_name}` (예: `person_aapl_tim_cook`)
   - 필수 필드: id, node_type, name, description, node_style

4. **Static Link 생성**
   - MAKE: Company → Product
   - HAS_RELATION: Company → Person (role 속성 포함)

### 5.3 생성 스크립트
**파일**: `scripts/05_generate_static_graph.py`

```python
#!/usr/bin/env python
"""Static Graph 생성 스크립트"""
import argparse
from app.services.graph_generator import generate_static_graph

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--ticker", nargs="+", default=["AAPL"])
    args = parser.parse_args()
    
    for ticker in args.ticker:
        static_graph = generate_static_graph(ticker.upper())
        # 저장: data/graph/{TICKER}_static_graph.json

if __name__ == "__main__":
    main()
```

---

## Phase 6: Dynamic Graph 생성 (3시간)

### 6.1 실행 단계 개요

| 단계 | 작업 내용 | 생성되는 노드/링크 |
|------|----------|------------------|
| **5.1** | Dynamic Node 생성 | Document, Section, Risk, Opportunity, Event, Technology |
| **5.2** | IS_INCLUDED Link 생성 | Section → Document |
| **5.3** | IS_EXTRACTED_FROM Link 생성 | Risk/Opp/Event/Tech → Section |
| **5.4** | HAS_* Link 생성 | Company → Risk/Opp/Event/Tech |
| **5.5** | IS_MENTIONED_IN Link 생성 | Product/Person/Company → Dynamic Node |
| **5.6** | Embedding 생성 | 노드에 `description_embedding` 추가 (768차원) |

### 6.2 Dynamic Node 생성
**파일**: `app/services/dynamic_graph_generator.py`

**주요 기능**:
1. **Document Node 생성**
   - ID: `doc_{ticker}_{filing_type_lower}_{accession_number}`
   - 필수 필드: id, node_type, ticker, filing_type, accession_number, year, sections_included

2. **Section Node 생성**
   - ID: `section_{ticker}_{filing_type_lower}_{year}_{section_name}`
   - 필수 필드: id, node_type, section_name, filing_type, ticker, year, accession_number

3. **Risk/Opportunity/Event/Technology Node 생성**
   - Risk ID: `risk_{ticker}_{normalized_entity}_{year}`
   - Opportunity ID: `opp_{ticker}_{normalized_entity}_{year}`
   - Event ID: `event_{ticker}_{normalized_entity}_{year}`
   - Technology ID: `tech_{ticker}_{normalized_entity}_{year}`
   - 필수 필드: id, node_type, ticker, entity, description, metadata (source_section, filing_type, accession_number)

### 6.3 Dynamic Link 생성

#### 6.3.1 IS_INCLUDED Link (Section → Document)
```python
def generate_is_included_links(section_nodes, doc_node) -> List[Dict]:
    # Section이 어떤 Document에 포함되는지 연결
    # section_order: sections_included 배열에서의 인덱스 + 1 (1-base)
```

#### 6.3.2 IS_EXTRACTED_FROM Link (Risk/Opp/Event/Tech → Section)
```python
def generate_is_extracted_from_links(dynamic_nodes, section_nodes, extracted_data, doc_node) -> List[Dict]:
    # 추출된 엔티티가 어떤 Section에서 추출되었는지 추적
    # 매칭 키: ticker, filing_type, year, source_section, accession_number
```

#### 6.3.3 HAS_* Link (Company → Risk/Opp/Event/Tech)
```python
def generate_has_risks_links(ticker, risk_nodes, extracted_data) -> List[Dict]
def generate_has_opportunities_links(ticker, opp_nodes, extracted_data) -> List[Dict]
def generate_has_events_links(ticker, event_nodes, extracted_data) -> List[Dict]
def generate_has_technologies_links(ticker, tech_nodes, extracted_data) -> List[Dict]
```

### 6.4 Embedding 생성
**파일**: `app/services/embedding_generator.py`

**개요**: Risk, Opportunity, Event, Technology 노드에 `description_embedding` 필드를 추가하여 의미 기반 검색을 지원합니다.

**설정**:
- 모델: Gemini `text-embedding-004` (768차원)
- API: `google.generativeai.embed_content()`
- 환경변수: `GOOGLE_API_KEY` 필요

**벡터화 대상 텍스트**:
| 노드 타입 | 텍스트 형식 |
|----------|-----------|
| Risk | `{entity}: {description}` |
| Opportunity | `{entity}: {description}` |
| Event | `{entity} ({date}): {description}` |
| Technology | `{entity}: {description}` |

```python
def get_embedding_text(node: Dict) -> str:
    """노드에서 embedding 대상 텍스트 추출"""

async def generate_embedding(text: str) -> List[float]:
    """단일 텍스트 embedding 생성"""

async def generate_embeddings_batch(texts: List[str], batch_size: int = 100) -> List[List[float]]:
    """배치 단위 embedding 생성 (API 호출 최적화)"""

async def add_embeddings_to_nodes(nodes: List[Dict]) -> List[Dict]:
    """노드 리스트에 embedding 추가"""
```

**예상 API 호출량**: 전체 ~1,569 노드 → ~19회 배치 호출 (100개/배치)

### 6.5 통합 함수
```python
def generate_dynamic_links(ticker, doc_node, section_nodes, risk_nodes, opp_nodes, event_nodes, tech_nodes, extracted_data) -> List[Dict]:
    all_links = []
    all_links.extend(generate_is_included_links(section_nodes, doc_node))
    all_links.extend(generate_is_extracted_from_links(dynamic_nodes, section_nodes, extracted_data, doc_node))
    all_links.extend(generate_has_risks_links(ticker, risk_nodes, extracted_data))
    all_links.extend(generate_has_opportunities_links(ticker, opp_nodes, extracted_data))
    all_links.extend(generate_has_events_links(ticker, event_nodes, extracted_data))
    all_links.extend(generate_has_technologies_links(ticker, tech_nodes, extracted_data))
    return all_links
```

### 6.6 생성 스크립트
**파일**: `scripts/06_generate_dynamic_graph.py`

```python
#!/usr/bin/env python
"""Dynamic Graph 생성 스크립트"""
import argparse
from app.services.dynamic_graph_generator import generate_dynamic_graph

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--ticker", nargs="+", default=["AAPL"])
    parser.add_argument("--with-embedding", action="store_true", help="Generate embeddings for nodes")
    args = parser.parse_args()
    
    for ticker in args.ticker:
        static_graph = load_static_graph(ticker)
        dynamic_graph = generate_dynamic_graph(ticker.upper(), static_graph, with_embedding=args.with_embedding)
        # 저장: data/graph/{TICKER}_dynamic_graph.json

if __name__ == "__main__":
    main()
```

---

## Phase 7: Graph DB 저장 (3시간)

### 7.1 개요
Phase 5~6에서 생성된 Static/Dynamic Graph JSON 파일을 FalkorDB에 적재합니다.

**입력 파일**:
- `data/graph/{TICKER}_static_graph.json` - Company, Product, Person 노드 및 MAKE, HAS_RELATION 링크
- `data/graph/{TICKER}_dynamic_graph.json` - Document, Section, Risk, Opportunity, Event, Technology 노드 및 모든 Dynamic 링크

**FalkorDB 설정**:
```
Host: localhost (또는 환경변수 FALKORDB_HOST)
Port: 6379 (또는 환경변수 FALKORDB_PORT)
Graph Name: financial_kg
```

### 7.2 Graph Loader 모듈
**파일**: `app/services/graph_loader.py`

```python
from falkordb import FalkorDB
from typing import Dict, List
import logging

class GraphLoader:
    """FalkorDB에 노드 및 링크를 적재하는 클래스"""
    
    def __init__(self, host: str = "localhost", port: int = 6379, graph_name: str = "financial_kg"):
        self.db = FalkorDB(host=host, port=port)
        self.graph = self.db.select_graph(graph_name)
        
    async def initialize(self):
        """인덱스 및 제약조건 생성"""
        node_types = ["Company", "Product", "Person", "Document", "Section", 
                      "Risk", "Opportunity", "Event", "Technology"]
        for node_type in node_types:
            self.graph.query(f"CREATE INDEX FOR (n:{node_type}) ON (n.id)")
            self.graph.query(f"CREATE INDEX FOR (n:{node_type}) ON (n.ticker)")
        logging.info("Indices created")
        
    async def create_node(self, node: Dict):
        """노드 생성 (MERGE 사용하여 중복 방지)"""
        node_type = node.get("node_type")
        node_id = node.get("id")
        props = {k: v for k, v in node.items() if k != "node_type" and v is not None}
        
        query = f"""
        MERGE (n:{node_type} {{id: $id}})
        SET n += $props
        """
        self.graph.query(query, {"id": node_id, "props": props})
        
    async def create_link(self, link: Dict):
        """링크 생성 (MERGE 사용하여 중복 방지)"""
        from_id = link.get("from")
        to_id = link.get("to")
        rel_type = link.get("relationship_type")
        props = {k: v for k, v in link.items() 
                 if k not in ["from", "to", "relationship_type"] and v is not None}
        
        query = f"""
        MATCH (a {{id: $from_id}})
        MATCH (b {{id: $to_id}})
        MERGE (a)-[r:{rel_type}]->(b)
        SET r += $props
        """
        self.graph.query(query, {"from_id": from_id, "to_id": to_id, "props": props})
    
    async def load_static_graph(self, ticker: str, static_graph: Dict):
        """Static Graph 적재"""
        for node_type, nodes in static_graph.get("nodes", {}).items():
            for node in nodes:
                await self.create_node(node)
        for link in static_graph.get("links", []):
            await self.create_link(link)
    
    async def load_dynamic_graph(self, ticker: str, dynamic_graph: Dict):
        """Dynamic Graph 적재"""
        for node_type, nodes in dynamic_graph.get("nodes", {}).items():
            for node in nodes:
                await self.create_node(node)
        for link in dynamic_graph.get("links", []):
            await self.create_link(link)
    
    def get_stats(self) -> Dict:
        """적재 통계 반환"""
        node_stats = self.graph.query("MATCH (n) RETURN labels(n)[0] AS label, count(n) AS count")
        link_stats = self.graph.query("MATCH ()-[r]->() RETURN type(r) AS type, count(r) AS count")
        return {"nodes": node_stats.result_set, "links": link_stats.result_set}
```

### 7.3 Cypher 쿼리 패턴

**노드 생성 (MERGE)**:
```cypher
// Company 노드
MERGE (n:Company {id: $id})
SET n.ticker = $ticker, n.name = $name, n.sector = $sector

// Risk/Opportunity/Event/Technology 노드
MERGE (n:Risk {id: $id})
SET n.ticker = $ticker, n.entity = $entity, n.description = $description
```

**링크 생성 (MERGE)**:
```cypher
// HAS_RISKS 링크
MATCH (a:Company {id: $from_id})
MATCH (b:Risk {id: $to_id})
MERGE (a)-[r:HAS_RISKS]->(b)

// IS_MENTIONED_IN 링크
MATCH (a {id: $from_id})
MATCH (b {id: $to_id})
MERGE (a)-[r:IS_MENTIONED_IN]->(b)
SET r.mention_context = $mention_context
```

### 7.4 저장 스크립트
**파일**: `scripts/07_load_graph_to_db.py`

```python
#!/usr/bin/env python
"""Phase 7: Graph DB 저장 스크립트"""
import asyncio
import json
import os
import argparse
from pathlib import Path
from dotenv import load_dotenv
from app.services.graph_loader import GraphLoader

async def main():
    load_dotenv()
    
    parser = argparse.ArgumentParser(description="Load graph data into FalkorDB")
    parser.add_argument("--ticker", nargs="+", default=["AAPL"])
    parser.add_argument("--verify", action="store_true", help="Verify loaded data")
    args = parser.parse_args()
    
    loader = GraphLoader(
        host=os.getenv("FALKORDB_HOST", "localhost"),
        port=int(os.getenv("FALKORDB_PORT", 6379))
    )
    await loader.initialize()
    
    graph_dir = Path("./data/graph")
    
    for ticker in args.ticker:
        ticker = ticker.upper()
        print(f"\n{'='*60}")
        print(f"Loading graph data for {ticker}")
        print(f"{'='*60}")
        
        # 1. Static Graph 로드
        static_file = graph_dir / f"{ticker}_static_graph.json"
        if static_file.exists():
            with open(static_file, 'r', encoding='utf-8') as f:
                static_graph = json.load(f)
            await loader.load_static_graph(ticker, static_graph)
            print(f"  ✅ Static Graph loaded")
        
        # 2. Dynamic Graph 로드
        dynamic_file = graph_dir / f"{ticker}_dynamic_graph.json"
        if dynamic_file.exists():
            with open(dynamic_file, 'r', encoding='utf-8') as f:
                dynamic_graph = json.load(f)
            await loader.load_dynamic_graph(ticker, dynamic_graph)
            print(f"  ✅ Dynamic Graph loaded")
    
    if args.verify:
        stats = loader.get_stats()
        print(f"\n📊 Statistics: {stats}")
    
    print(f"\n✅ Graph population completed!")

if __name__ == "__main__":
    asyncio.run(main())
```

### 7.5 검증 쿼리

```cypher
-- 노드 수 확인
MATCH (n) RETURN labels(n)[0] AS label, count(n) AS count ORDER BY label

-- 링크 수 확인
MATCH ()-[r]->() RETURN type(r) AS type, count(r) AS count ORDER BY type

-- 티커별 노드 수 확인
MATCH (n) WHERE n.ticker IS NOT NULL
RETURN n.ticker AS ticker, labels(n)[0] AS label, count(n) AS count
ORDER BY ticker, label

-- 샘플 데이터 확인 (AAPL의 Risk와 연결된 Product)
MATCH (p:Product)-[r:IS_MENTIONED_IN]->(risk:Risk)
WHERE risk.ticker = 'AAPL'
RETURN p.name, risk.entity, r.mention_context
LIMIT 10
```

### 7.6 예상 적재량

| 노드 타입 | 예상 수 |
|----------|--------|
| Company | 7 |
| Product | ~210 |
| Person | ~27 |
| Document | ~134 |
| Section | ~90 |
| Risk | ~375 |
| Opportunity | ~348 |
| Event | ~464 |
| Technology | ~382 |
| **총 노드** | **~2,037** |

| 링크 타입 | 예상 수 |
|----------|--------|
| MAKE | ~210 |
| HAS_RELATION | ~27 |
| IS_INCLUDED | ~186 |
| IS_EXTRACTED_FROM | ~1,650 |
| HAS_RISKS | ~395 |
| HAS_OPPORTUNITIES | ~356 |
| HAS_EVENTS | ~471 |
| HAS_TECHNOLOGIES | ~428 |
| IS_MENTIONED_IN | ~1,552 |
| **총 링크** | **~5,275** |

---

## Phase 8: 질의 응답 시스템 (3시간)

### 8.1 질의 엔진 구현
**파일**: `src/query/query_engine.py`

```python
from src.graph.graphiti_manager import GraphitiManager
from openai import OpenAI

class QueryEngine:
    """자연어 질의 처리 엔진"""
    
    TICKER_MAP = {
        "애플": "AAPL",
        "아마존": "AMZN", 
        "테슬라": "TSLA",
        "구글": "GOOGL",
        "마이크로소프트": "MSFT",
        "메타": "META",
        "엔비디아": "NVDA"
    }
    
    def __init__(self, graphiti_manager: GraphitiManager):
        self.manager = graphiti_manager
        self.llm = OpenAI()
        
    def extract_intent(self, query: str) -> dict:
        """질의에서 의도 추출"""
        # 기업명 추출
        company = None
        for kr_name, ticker in self.TICKER_MAP.items():
            if kr_name in query:
                company = ticker
                break
                
        # 질의 유형 분류
        query_type = "general"
        if "기회" in query or "opportunity" in query.lower():
            query_type = "opportunities"
        elif "리스크" in query or "위험" in query:
            query_type = "risks"
        elif "전략" in query:
            query_type = "strategies"
            
        return {"company": company, "query_type": query_type}
        
    async def query(self, user_query: str) -> str:
        """사용자 질의 처리"""
        intent = self.extract_intent(user_query)
        
        # 그래프 검색
        results = await self.manager.search(
            query=user_query,
            group_ids=[intent["company"]] if intent["company"] else None
        )
        
        # LLM을 통한 답변 생성
        context = "\n".join([r.content for r in results[:10]])
        
        response = self.llm.chat.completions.create(
            model="gpt-4o-mini",
            messages=[
                {"role": "system", "content": "당신은 금융 분석 전문가입니다. 주어진 정보를 바탕으로 질문에 답변하세요."},
                {"role": "user", "content": f"컨텍스트:\n{context}\n\n질문: {user_query}"}
            ]
        )
        
        return response.choices[0].message.content
```

### 8.2 CLI 인터페이스
**파일**: `scripts/08_query_interface.py`

```python
#!/usr/bin/env python
"""질의 응답 인터페이스"""
import asyncio
from src.graph.graphiti_manager import GraphitiManager
from src.query.query_engine import QueryEngine

async def main():
    manager = GraphitiManager()
    engine = QueryEngine(manager)
    
    print("=== 금융 공시 Knowledge Graph 질의 시스템 ===")
    print("종료하려면 'exit' 또는 'quit'을 입력하세요.\n")
    
    while True:
        query = input("질문: ").strip()
        if query.lower() in ["exit", "quit"]:
            break
            
        if not query:
            continue
            
        answer = await engine.query(query)
        print(f"\n답변: {answer}\n")

if __name__ == "__main__":
    asyncio.run(main())
```

---

## Phase 9: 테스트 및 검증 (2시간)

### 9.1 단위 테스트
**파일**: `tests/test_downloader.py`
**파일**: `tests/test_parser.py`
**파일**: `tests/test_extractor.py`

### 9.2 통합 테스트
**파일**: `tests/test_integration.py`

### 9.3 검증 시나리오

| 테스트 케이스 | 입력 | 기대 결과 |
|--------------|------|----------|
| TC-01 | "애플의 기회 요소를 알려줘" | Apple 관련 기회 요소 목록 |
| TC-02 | "테슬라의 리스크는?" | Tesla 관련 리스크 요소 |
| TC-03 | "구글의 AI 전략" | Alphabet AI 관련 전략 |
| TC-04 | "엔비디아 vs AMD 비교" | 두 기업 비교 분석 |

---

## 🚀 실행 순서

```bash
# 1. 환경 설정
cp .env.example .env
# .env 파일 수정 (API 키 설정)

# 2. FalkorDB 시작
docker run -d --name falkordb -p 6379:6379 -p 3000:3000 falkordb/falkordb:latest

# 3. 의존성 설치
pip install -r requirements.txt

# 4. 공시 다운로드 (10-K, 10-Q, 8-K)
python scripts/01_download_filings.py
# 예상 소요 시간: 30분 ~ 1시간 (API 제한으로 인해)
# 저장 위치: ./data/raw/{ticker}/{filing_type}/

# 5. 파싱
python scripts/02_parse_filings.py
# 저장 위치: ./data/parsed/{ticker}/{filing_type}/

# 6. 트리플렛 추출
python scripts/03_extract_triplets.py
# 저장 위치: ./data/extracted/{ticker}/{filing_type}/

# 7. Static Graph 생성 (Company, Product, Person 노드)
python scripts/05_generate_static_graph.py --ticker AAPL TSLA NVDA
# 저장 위치: ./data/graph/{TICKER}_static_graph.json

# 8. Dynamic Graph 생성 (Document, Section, Risk, Opp, Event, Tech 노드 + 링크)
python scripts/06_generate_dynamic_graph.py --ticker AAPL TSLA NVDA
# 옵션: --with-embedding (Embedding 생성 포함)
# 저장 위치: ./data/graph/{TICKER}_dynamic_graph.json

# 9. Graph DB 적재
python scripts/07_populate_graph.py
# FalkorDB에 노드 및 링크 적재

# 10. 질의 시스템 실행
python scripts/08_query_interface.py
```

---

## 📊 마일스톤 체크리스트

- [x] Phase 1: 환경 설정 완료 ✅
  - [x] FalkorDB Docker 컨테이너 실행
  - [x] Python 환경 및 의존성 설치
  - [x] 환경 변수 설정
  
- [x] Phase 2: 공시 다운로드 완료 ✅
  - [x] 7개 기업 10-K, 10-Q, 8-K 다운로드
  - [x] 폴더 구조 확인 (data/raw/{ticker}/{filing_type}/)
  - [x] API 엔드포인트 구현 (`/download`)
  
- [x] Phase 3: 파싱 완료 ✅
  - [x] HTML → 텍스트 변환
  - [x] 섹션별 추출
  - [x] 저장 확인 (data/parsed/{ticker}/{filing_type}/)
  
- [x] Phase 4: 트리플렛 추출 완료 ✅
  - [x] LLM 연동 (Gemini)
  - [x] Risk/Opportunity/Event/Technology 추출
  - [x] mentioned_products/persons/companies 추출
  - [x] Extracted Data 저장 확인 (data/extracted/{ticker}/{filing_type}/)
  - [x] 프롬프트 YAML 분리 (`app/prompts/triplet_extractor.yaml`)
  
- [x] Phase 5: Static Graph 생성 완료 ✅
  - [x] Company Node 생성
  - [x] Product Node 생성 (고유명사, 중복 제거)
  - [x] Person Node 생성 (중복 제거)
  - [x] MAKE Link 생성 (Company → Product)
  - [x] HAS_RELATION Link 생성 (Company → Person)
  - [x] 저장 확인 ({TICKER}_static_graph.json)
  
- [x] Phase 6: Dynamic Graph 생성 완료 ✅
  - [x] Document Node 생성
  - [x] Section Node 생성
  - [x] Risk/Opportunity/Event/Technology Node 생성
  - [x] IS_INCLUDED Link 생성 (Section → Document)
  - [x] IS_EXTRACTED_FROM Link 생성 (Dynamic → Section)
  - [x] HAS_RISKS/HAS_OPPORTUNITIES/HAS_EVENTS/HAS_TECHNOLOGIES Link 생성
  - [x] IS_MENTIONED_IN Link 생성 (Static → Dynamic)
  - [x] Embedding 생성 (Gemini text-embedding-004)
  - [x] 저장 확인 ({TICKER}_dynamic_graph.json)
  
- [x] Phase 7: Graph DB 저장 완료 ✅
  - [x] FalkorDB 연동
  - [x] Node/Link Data 로드 및 Cypher 쿼리 생성
  - [x] 데이터 저장 확인
  - [x] 중복 방지 메커니즘 구현 (`DuplicateChecker`)
  
- [x] Phase 8: 질의 시스템 완료 ✅
  - [x] Graph 검색 기능 구현
  - [x] Vector 검색 기능 구현 (하이브리드)
  - [x] 답변 생성 구현
  - [x] Intent 추출 구현 (Gemini Structured Output)
  - [x] Cypher 쿼리 빌더 구현
  - [x] 이름 표준화 시스템 구현
  - [x] 프롬프트 YAML 분리 (`app/prompts/answer_generator.yaml`, `app/prompts/intent_extractor.yaml`)
  
- [x] Phase 9: API 구현 완료 ✅
  - [x] FastAPI 기반 REST API 구현
  - [x] `/answer` 엔드포인트 (스트리밍 답변)
  - [x] `/download` 엔드포인트 (공시 다운로드)
  - [x] `/process` 엔드포인트 (문서 처리 및 Graph DB 적재)
  - [x] Streamlit 클라이언트 구현
  - [x] 의존성 관리 (FastAPI Dependency Injection)
  - [x] API 스키마 정의 (`app/schemas/api_schemas.py`)

---

## ⚠️ 주의사항

1. **SEC API 제한**: 초당 10건 이하 요청 유지
2. **LLM 비용**: GPT-4 사용 시 토큰 비용 발생 (예상: $50-100, 공시 수 증가로 인해)
3. **저장 공간**: 
   - 10-K: 7 × 3 = 21건, 약 210MB
   - 10-Q: 7 × 12 = 84건, 약 420MB
   - 8-K: 7 × 20 = 140건, 약 280MB
   - 총 예상: ~1GB
4. **메모리**: Graphiti 처리 시 최소 8GB RAM 권장

