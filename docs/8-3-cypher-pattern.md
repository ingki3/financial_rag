# Cypher Query Pattern 매칭

Intent 분석 이후 target과 filters의 node type 구성을 보고 기본적인 Cypher query를 결정하는 패턴 매칭 문서입니다.

## 📌 개요

- **target**: Opportunity, Risk, Event (3개)
- **filters**: Company, Person, Technology, Product (4개)
- **조합**: filters는 ontology 구성에 따라 조합 가능한 순서로 생성

## 🔗 Ontology Link 타입

- `HAS_RISKS`: Company → Risk
- `HAS_OPPORTUNITIES`: Company → Opportunity
- `HAS_EVENTS`: Company → Event
- `HAS_TECHNOLOGIES`: Company → Technology
- `MAKE`: Company → Product
- `HAS_RELATION`: Company → Person
- `IS_MENTIONED_IN`: Product/Person/Company → Risk/Opportunity/Event/Technology

## 📋 패턴 구조

각 패턴은 다음 형식으로 구성됩니다:
- **target**: 검색할 노드 타입 (Opportunity, Risk, Event)
- **filters**: 필터 조건 노드들 (Company, Person, Technology, Product의 조합)
- **cypher_query**: 생성된 Cypher 쿼리 템플릿

---

## 패턴 목록

### 1. Target: Opportunity

#### 1.1 Filters: Company만

**패턴:**
```json
{
  "target": {"node_type": "Opportunity"},
  "filters": [{"node_type": "Company", "ticker": "AAPL"}]
}
```

**Cypher Query:**
```cypher
MATCH (c:Company {ticker: $company_ticker})-[r:HAS_OPPORTUNITIES]->(o:Opportunity)
RETURN o.id, o.entity, o.description, o.ticker
```

---

#### 1.2 Filters: Person만

**패턴:**
```json
{
  "target": {"node_type": "Opportunity"},
  "filters": [{"node_type": "Person", "name": "Tim Cook"}]
}
```

**Cypher Query:**
```cypher
MATCH (p:Person {name: $person_name})-[r:IS_MENTIONED_IN]->(o:Opportunity)
RETURN o.id, o.entity, o.description, o.ticker
```

---

#### 1.3 Filters: Technology만

**패턴:**
```json
{
  "target": {"node_type": "Opportunity"},
  "filters": [{"node_type": "Technology", "name": "AI 기술"}]
}
```

**Cypher Query:**
```cypher
MATCH (t:Technology {entity: $technology_name})-[r:IS_MENTIONED_IN]->(o:Opportunity)
RETURN o.id, o.entity, o.description, o.ticker
```

---

#### 1.4 Filters: Product만

**패턴:**
```json
{
  "target": {"node_type": "Opportunity"},
  "filters": [{"node_type": "Product", "name": "iPhone 15"}]
}
```

**Cypher Query:**
```cypher
MATCH (pr:Product {name: $product_name})-[r:IS_MENTIONED_IN]->(o:Opportunity)
RETURN o.id, o.entity, o.description, o.ticker
```

---

#### 1.5 Filters: Company + Person

**패턴:**
```json
{
  "target": {"node_type": "Opportunity"},
  "filters": [
    {"node_type": "Company", "ticker": "AAPL"},
    {"node_type": "Person", "name": "Tim Cook"}
  ]
}
```

**Cypher Query:**
```cypher
MATCH (c:Company {ticker: $company_ticker})-[r1:HAS_RELATION]->(p:Person {name: $person_name})-[r2:IS_MENTIONED_IN]->(o:Opportunity)
WHERE o.ticker = $company_ticker
RETURN o.id, o.entity, o.description, o.ticker
```

---

#### 1.6 Filters: Company + Technology

**패턴:**
```json
{
  "target": {"node_type": "Opportunity"},
  "filters": [
    {"node_type": "Company", "ticker": "AAPL"},
    {"node_type": "Technology", "name": "AI 기술"}
  ]
}
```

**Cypher Query:**
```cypher
MATCH (c:Company {ticker: $company_ticker})-[r1:HAS_TECHNOLOGIES]->(t:Technology {entity: $technology_name})-[r2:IS_MENTIONED_IN]->(o:Opportunity)
WHERE o.ticker = $company_ticker
RETURN o.id, o.entity, o.description, o.ticker
```

---

#### 1.7 Filters: Company + Product

**패턴:**
```json
{
  "target": {"node_type": "Opportunity"},
  "filters": [
    {"node_type": "Company", "ticker": "AAPL"},
    {"node_type": "Product", "name": "iPhone 15"}
  ]
}
```

**Cypher Query:**
```cypher
MATCH (c:Company {ticker: $company_ticker})-[r1:MAKE]->(pr:Product {name: $product_name})-[r2:IS_MENTIONED_IN]->(o:Opportunity)
WHERE o.ticker = $company_ticker
RETURN o.id, o.entity, o.description, o.ticker
```

---

#### 1.8 Filters: Person + Technology

**패턴:**
```json
{
  "target": {"node_type": "Opportunity"},
  "filters": [
    {"node_type": "Person", "name": "Tim Cook"},
    {"node_type": "Technology", "name": "AI 기술"}
  ]
}
```

**Cypher Query:**
```cypher
MATCH (p:Person {name: $person_name})-[r1:IS_MENTIONED_IN]->(t:Technology {entity: $technology_name})-[r2:IS_MENTIONED_IN]->(o:Opportunity)
RETURN o.id, o.entity, o.description, o.ticker
```

---

#### 1.9 Filters: Person + Product

**패턴:**
```json
{
  "target": {"node_type": "Opportunity"},
  "filters": [
    {"node_type": "Person", "name": "Tim Cook"},
    {"node_type": "Product", "name": "iPhone 15"}
  ]
}
```

**Cypher Query:**
```cypher
MATCH (p:Person {name: $person_name})-[r1:IS_MENTIONED_IN]->(pr:Product {name: $product_name})-[r2:IS_MENTIONED_IN]->(o:Opportunity)
RETURN o.id, o.entity, o.description, o.ticker
```

---

#### 1.10 Filters: Technology + Product

**패턴:**
```json
{
  "target": {"node_type": "Opportunity"},
  "filters": [
    {"node_type": "Technology", "name": "AI 기술"},
    {"node_type": "Product", "name": "iPhone 15"}
  ]
}
```

**Cypher Query:**
```cypher
MATCH (t:Technology {entity: $technology_name})-[r1:IS_MENTIONED_IN]->(pr:Product {name: $product_name})-[r2:IS_MENTIONED_IN]->(o:Opportunity)
RETURN o.id, o.entity, o.description, o.ticker
```

---

#### 1.11 Filters: Company + Person + Technology

**패턴:**
```json
{
  "target": {"node_type": "Opportunity"},
  "filters": [
    {"node_type": "Company", "ticker": "AAPL"},
    {"node_type": "Person", "name": "Tim Cook"},
    {"node_type": "Technology", "name": "AI 기술"}
  ]
}
```

**Cypher Query:**
```cypher
MATCH (c:Company {ticker: $company_ticker})-[r1:HAS_RELATION]->(p:Person {name: $person_name})-[r2:IS_MENTIONED_IN]->(t:Technology {entity: $technology_name})-[r3:IS_MENTIONED_IN]->(o:Opportunity)
WHERE o.ticker = $company_ticker
RETURN o.id, o.entity, o.description, o.ticker
```

---

#### 1.12 Filters: Company + Person + Product

**패턴:**
```json
{
  "target": {"node_type": "Opportunity"},
  "filters": [
    {"node_type": "Company", "ticker": "AAPL"},
    {"node_type": "Person", "name": "Tim Cook"},
    {"node_type": "Product", "name": "iPhone 15"}
  ]
}
```

**Cypher Query:**
```cypher
MATCH (c:Company {ticker: $company_ticker})-[r1:HAS_RELATION]->(p:Person {name: $person_name})-[r2:IS_MENTIONED_IN]->(pr:Product {name: $product_name})-[r3:IS_MENTIONED_IN]->(o:Opportunity)
WHERE o.ticker = $company_ticker
RETURN o.id, o.entity, o.description, o.ticker
```

---

#### 1.13 Filters: Company + Technology + Product

**패턴:**
```json
{
  "target": {"node_type": "Opportunity"},
  "filters": [
    {"node_type": "Company", "ticker": "AAPL"},
    {"node_type": "Technology", "name": "AI 기술"},
    {"node_type": "Product", "name": "iPhone 15"}
  ]
}
```

**Cypher Query:**
```cypher
MATCH (c:Company {ticker: $company_ticker})-[r1:HAS_TECHNOLOGIES]->(t:Technology {entity: $technology_name})-[r2:IS_MENTIONED_IN]->(pr:Product {name: $product_name})-[r3:IS_MENTIONED_IN]->(o:Opportunity)
WHERE o.ticker = $company_ticker
RETURN o.id, o.entity, o.description, o.ticker
```

---

#### 1.14 Filters: Person + Technology + Product

**패턴:**
```json
{
  "target": {"node_type": "Opportunity"},
  "filters": [
    {"node_type": "Person", "name": "Tim Cook"},
    {"node_type": "Technology", "name": "AI 기술"},
    {"node_type": "Product", "name": "iPhone 15"}
  ]
}
```

**Cypher Query:**
```cypher
MATCH (p:Person {name: $person_name})-[r1:IS_MENTIONED_IN]->(t:Technology {entity: $technology_name})-[r2:IS_MENTIONED_IN]->(pr:Product {name: $product_name})-[r3:IS_MENTIONED_IN]->(o:Opportunity)
RETURN o.id, o.entity, o.description, o.ticker
```

---

#### 1.15 Filters: Company + Person + Technology + Product

**패턴:**
```json
{
  "target": {"node_type": "Opportunity"},
  "filters": [
    {"node_type": "Company", "ticker": "AAPL"},
    {"node_type": "Person", "name": "Tim Cook"},
    {"node_type": "Technology", "name": "AI 기술"},
    {"node_type": "Product", "name": "iPhone 15"}
  ]
}
```

**Cypher Query:**
```cypher
MATCH (c:Company {ticker: $company_ticker})-[r1:HAS_RELATION]->(p:Person {name: $person_name})-[r2:IS_MENTIONED_IN]->(t:Technology {entity: $technology_name})-[r3:IS_MENTIONED_IN]->(pr:Product {name: $product_name})-[r4:IS_MENTIONED_IN]->(o:Opportunity)
WHERE o.ticker = $company_ticker
RETURN o.id, o.entity, o.description, o.ticker
```

---

### 2. Target: Risk

#### 2.1 Filters: Company만

**패턴:**
```json
{
  "target": {"node_type": "Risk"},
  "filters": [{"node_type": "Company", "ticker": "AAPL"}]
}
```

**Cypher Query:**
```cypher
MATCH (c:Company {ticker: $company_ticker})-[r:HAS_RISKS]->(risk:Risk)
RETURN risk.id, risk.entity, risk.description, risk.ticker
```

---

#### 2.2 Filters: Person만

**패턴:**
```json
{
  "target": {"node_type": "Risk"},
  "filters": [{"node_type": "Person", "name": "Tim Cook"}]
}
```

**Cypher Query:**
```cypher
MATCH (p:Person {name: $person_name})-[r:IS_MENTIONED_IN]->(risk:Risk)
RETURN risk.id, risk.entity, risk.description, risk.ticker
```

---

#### 2.3 Filters: Technology만

**패턴:**
```json
{
  "target": {"node_type": "Risk"},
  "filters": [{"node_type": "Technology", "name": "AI 기술"}]
}
```

**Cypher Query:**
```cypher
MATCH (t:Technology {entity: $technology_name})-[r:IS_MENTIONED_IN]->(risk:Risk)
RETURN risk.id, risk.entity, risk.description, risk.ticker
```

---

#### 2.4 Filters: Product만

**패턴:**
```json
{
  "target": {"node_type": "Risk"},
  "filters": [{"node_type": "Product", "name": "iPhone 15"}]
}
```

**Cypher Query:**
```cypher
MATCH (pr:Product {name: $product_name})-[r:IS_MENTIONED_IN]->(risk:Risk)
RETURN risk.id, risk.entity, risk.description, risk.ticker
```

---

#### 2.5 Filters: Company + Person

**패턴:**
```json
{
  "target": {"node_type": "Risk"},
  "filters": [
    {"node_type": "Company", "ticker": "AAPL"},
    {"node_type": "Person", "name": "Tim Cook"}
  ]
}
```

**Cypher Query:**
```cypher
MATCH (c:Company {ticker: $company_ticker})-[r1:HAS_RELATION]->(p:Person {name: $person_name})-[r2:IS_MENTIONED_IN]->(risk:Risk)
WHERE risk.ticker = $company_ticker
RETURN risk.id, risk.entity, risk.description, risk.ticker
```

---

#### 2.6 Filters: Company + Technology

**패턴:**
```json
{
  "target": {"node_type": "Risk"},
  "filters": [
    {"node_type": "Company", "ticker": "AAPL"},
    {"node_type": "Technology", "name": "AI 기술"}
  ]
}
```

**Cypher Query:**
```cypher
MATCH (c:Company {ticker: $company_ticker})-[r1:HAS_TECHNOLOGIES]->(t:Technology {entity: $technology_name})-[r2:IS_MENTIONED_IN]->(risk:Risk)
WHERE risk.ticker = $company_ticker
RETURN risk.id, risk.entity, risk.description, risk.ticker
```

---

#### 2.7 Filters: Company + Product

**패턴:**
```json
{
  "target": {"node_type": "Risk"},
  "filters": [
    {"node_type": "Company", "ticker": "AAPL"},
    {"node_type": "Product", "name": "iPhone 15"}
  ]
}
```

**Cypher Query:**
```cypher
MATCH (c:Company {ticker: $company_ticker})-[r1:MAKE]->(pr:Product {name: $product_name})-[r2:IS_MENTIONED_IN]->(risk:Risk)
WHERE risk.ticker = $company_ticker
RETURN risk.id, risk.entity, risk.description, risk.ticker
```

---

#### 2.8 Filters: Person + Technology

**패턴:**
```json
{
  "target": {"node_type": "Risk"},
  "filters": [
    {"node_type": "Person", "name": "Tim Cook"},
    {"node_type": "Technology", "name": "AI 기술"}
  ]
}
```

**Cypher Query:**
```cypher
MATCH (p:Person {name: $person_name})-[r1:IS_MENTIONED_IN]->(t:Technology {entity: $technology_name})-[r2:IS_MENTIONED_IN]->(risk:Risk)
RETURN risk.id, risk.entity, risk.description, risk.ticker
```

---

#### 2.9 Filters: Person + Product

**패턴:**
```json
{
  "target": {"node_type": "Risk"},
  "filters": [
    {"node_type": "Person", "name": "Tim Cook"},
    {"node_type": "Product", "name": "iPhone 15"}
  ]
}
```

**Cypher Query:**
```cypher
MATCH (p:Person {name: $person_name})-[r1:IS_MENTIONED_IN]->(pr:Product {name: $product_name})-[r2:IS_MENTIONED_IN]->(risk:Risk)
RETURN risk.id, risk.entity, risk.description, risk.ticker
```

---

#### 2.10 Filters: Technology + Product

**패턴:**
```json
{
  "target": {"node_type": "Risk"},
  "filters": [
    {"node_type": "Technology", "name": "AI 기술"},
    {"node_type": "Product", "name": "iPhone 15"}
  ]
}
```

**Cypher Query:**
```cypher
MATCH (t:Technology {entity: $technology_name})-[r1:IS_MENTIONED_IN]->(pr:Product {name: $product_name})-[r2:IS_MENTIONED_IN]->(risk:Risk)
RETURN risk.id, risk.entity, risk.description, risk.ticker
```

---

#### 2.11 Filters: Company + Person + Technology

**패턴:**
```json
{
  "target": {"node_type": "Risk"},
  "filters": [
    {"node_type": "Company", "ticker": "AAPL"},
    {"node_type": "Person", "name": "Tim Cook"},
    {"node_type": "Technology", "name": "AI 기술"}
  ]
}
```

**Cypher Query:**
```cypher
MATCH (c:Company {ticker: $company_ticker})-[r1:HAS_RELATION]->(p:Person {name: $person_name})-[r2:IS_MENTIONED_IN]->(t:Technology {entity: $technology_name})-[r3:IS_MENTIONED_IN]->(risk:Risk)
WHERE risk.ticker = $company_ticker
RETURN risk.id, risk.entity, risk.description, risk.ticker
```

---

#### 2.12 Filters: Company + Person + Product

**패턴:**
```json
{
  "target": {"node_type": "Risk"},
  "filters": [
    {"node_type": "Company", "ticker": "AAPL"},
    {"node_type": "Person", "name": "Tim Cook"},
    {"node_type": "Product", "name": "iPhone 15"}
  ]
}
```

**Cypher Query:**
```cypher
MATCH (c:Company {ticker: $company_ticker})-[r1:HAS_RELATION]->(p:Person {name: $person_name})-[r2:IS_MENTIONED_IN]->(pr:Product {name: $product_name})-[r3:IS_MENTIONED_IN]->(risk:Risk)
WHERE risk.ticker = $company_ticker
RETURN risk.id, risk.entity, risk.description, risk.ticker
```

---

#### 2.13 Filters: Company + Technology + Product

**패턴:**
```json
{
  "target": {"node_type": "Risk"},
  "filters": [
    {"node_type": "Company", "ticker": "AAPL"},
    {"node_type": "Technology", "name": "AI 기술"},
    {"node_type": "Product", "name": "iPhone 15"}
  ]
}
```

**Cypher Query:**
```cypher
MATCH (c:Company {ticker: $company_ticker})-[r1:HAS_TECHNOLOGIES]->(t:Technology {entity: $technology_name})-[r2:IS_MENTIONED_IN]->(pr:Product {name: $product_name})-[r3:IS_MENTIONED_IN]->(risk:Risk)
WHERE risk.ticker = $company_ticker
RETURN risk.id, risk.entity, risk.description, risk.ticker
```

---

#### 2.14 Filters: Person + Technology + Product

**패턴:**
```json
{
  "target": {"node_type": "Risk"},
  "filters": [
    {"node_type": "Person", "name": "Tim Cook"},
    {"node_type": "Technology", "name": "AI 기술"},
    {"node_type": "Product", "name": "iPhone 15"}
  ]
}
```

**Cypher Query:**
```cypher
MATCH (p:Person {name: $person_name})-[r1:IS_MENTIONED_IN]->(t:Technology {entity: $technology_name})-[r2:IS_MENTIONED_IN]->(pr:Product {name: $product_name})-[r3:IS_MENTIONED_IN]->(risk:Risk)
RETURN risk.id, risk.entity, risk.description, risk.ticker
```

---

#### 2.15 Filters: Company + Person + Technology + Product

**패턴:**
```json
{
  "target": {"node_type": "Risk"},
  "filters": [
    {"node_type": "Company", "ticker": "AAPL"},
    {"node_type": "Person", "name": "Tim Cook"},
    {"node_type": "Technology", "name": "AI 기술"},
    {"node_type": "Product", "name": "iPhone 15"}
  ]
}
```

**Cypher Query:**
```cypher
MATCH (c:Company {ticker: $company_ticker})-[r1:HAS_RELATION]->(p:Person {name: $person_name})-[r2:IS_MENTIONED_IN]->(t:Technology {entity: $technology_name})-[r3:IS_MENTIONED_IN]->(pr:Product {name: $product_name})-[r4:IS_MENTIONED_IN]->(risk:Risk)
WHERE risk.ticker = $company_ticker
RETURN risk.id, risk.entity, risk.description, risk.ticker
```

---

### 3. Target: Event

#### 3.1 Filters: Company만

**패턴:**
```json
{
  "target": {"node_type": "Event"},
  "filters": [{"node_type": "Company", "ticker": "AAPL"}]
}
```

**Cypher Query:**
```cypher
MATCH (c:Company {ticker: $company_ticker})-[r:HAS_EVENTS]->(e:Event)
RETURN e.id, e.entity, e.description, e.ticker, e.date
```

---

#### 3.2 Filters: Person만

**패턴:**
```json
{
  "target": {"node_type": "Event"},
  "filters": [{"node_type": "Person", "name": "Tim Cook"}]
}
```

**Cypher Query:**
```cypher
MATCH (p:Person {name: $person_name})-[r:IS_MENTIONED_IN]->(e:Event)
RETURN e.id, e.entity, e.description, e.ticker, e.date
```

---

#### 3.3 Filters: Technology만

**패턴:**
```json
{
  "target": {"node_type": "Event"},
  "filters": [{"node_type": "Technology", "name": "AI 기술"}]
}
```

**Cypher Query:**
```cypher
MATCH (t:Technology {entity: $technology_name})-[r:IS_MENTIONED_IN]->(e:Event)
RETURN e.id, e.entity, e.description, e.ticker, e.date
```

---

#### 3.4 Filters: Product만

**패턴:**
```json
{
  "target": {"node_type": "Event"},
  "filters": [{"node_type": "Product", "name": "iPhone 15"}]
}
```

**Cypher Query:**
```cypher
MATCH (pr:Product {name: $product_name})-[r:IS_MENTIONED_IN]->(e:Event)
RETURN e.id, e.entity, e.description, e.ticker, e.date
```

---

#### 3.5 Filters: Company + Person

**패턴:**
```json
{
  "target": {"node_type": "Event"},
  "filters": [
    {"node_type": "Company", "ticker": "AAPL"},
    {"node_type": "Person", "name": "Tim Cook"}
  ]
}
```

**Cypher Query:**
```cypher
MATCH (c:Company {ticker: $company_ticker})-[r1:HAS_RELATION]->(p:Person {name: $person_name})-[r2:IS_MENTIONED_IN]->(e:Event)
WHERE e.ticker = $company_ticker
RETURN e.id, e.entity, e.description, e.ticker, e.date
```

---

#### 3.6 Filters: Company + Technology

**패턴:**
```json
{
  "target": {"node_type": "Event"},
  "filters": [
    {"node_type": "Company", "ticker": "AAPL"},
    {"node_type": "Technology", "name": "AI 기술"}
  ]
}
```

**Cypher Query:**
```cypher
MATCH (c:Company {ticker: $company_ticker})-[r1:HAS_TECHNOLOGIES]->(t:Technology {entity: $technology_name})-[r2:IS_MENTIONED_IN]->(e:Event)
WHERE e.ticker = $company_ticker
RETURN e.id, e.entity, e.description, e.ticker, e.date
```

---

#### 3.7 Filters: Company + Product

**패턴:**
```json
{
  "target": {"node_type": "Event"},
  "filters": [
    {"node_type": "Company", "ticker": "AAPL"},
    {"node_type": "Product", "name": "iPhone 15"}
  ]
}
```

**Cypher Query:**
```cypher
MATCH (c:Company {ticker: $company_ticker})-[r1:MAKE]->(pr:Product {name: $product_name})-[r2:IS_MENTIONED_IN]->(e:Event)
WHERE e.ticker = $company_ticker
RETURN e.id, e.entity, e.description, e.ticker, e.date
```

---

#### 3.8 Filters: Person + Technology

**패턴:**
```json
{
  "target": {"node_type": "Event"},
  "filters": [
    {"node_type": "Person", "name": "Tim Cook"},
    {"node_type": "Technology", "name": "AI 기술"}
  ]
}
```

**Cypher Query:**
```cypher
MATCH (p:Person {name: $person_name})-[r1:IS_MENTIONED_IN]->(t:Technology {entity: $technology_name})-[r2:IS_MENTIONED_IN]->(e:Event)
RETURN e.id, e.entity, e.description, e.ticker, e.date
```

---

#### 3.9 Filters: Person + Product

**패턴:**
```json
{
  "target": {"node_type": "Event"},
  "filters": [
    {"node_type": "Person", "name": "Tim Cook"},
    {"node_type": "Product", "name": "iPhone 15"}
  ]
}
```

**Cypher Query:**
```cypher
MATCH (p:Person {name: $person_name})-[r1:IS_MENTIONED_IN]->(pr:Product {name: $product_name})-[r2:IS_MENTIONED_IN]->(e:Event)
RETURN e.id, e.entity, e.description, e.ticker, e.date
```

---

#### 3.10 Filters: Technology + Product

**패턴:**
```json
{
  "target": {"node_type": "Event"},
  "filters": [
    {"node_type": "Technology", "name": "AI 기술"},
    {"node_type": "Product", "name": "iPhone 15"}
  ]
}
```

**Cypher Query:**
```cypher
MATCH (t:Technology {entity: $technology_name})-[r1:IS_MENTIONED_IN]->(pr:Product {name: $product_name})-[r2:IS_MENTIONED_IN]->(e:Event)
RETURN e.id, e.entity, e.description, e.ticker, e.date
```

---

#### 3.11 Filters: Company + Person + Technology

**패턴:**
```json
{
  "target": {"node_type": "Event"},
  "filters": [
    {"node_type": "Company", "ticker": "AAPL"},
    {"node_type": "Person", "name": "Tim Cook"},
    {"node_type": "Technology", "name": "AI 기술"}
  ]
}
```

**Cypher Query:**
```cypher
MATCH (c:Company {ticker: $company_ticker})-[r1:HAS_RELATION]->(p:Person {name: $person_name})-[r2:IS_MENTIONED_IN]->(t:Technology {entity: $technology_name})-[r3:IS_MENTIONED_IN]->(e:Event)
WHERE e.ticker = $company_ticker
RETURN e.id, e.entity, e.description, e.ticker, e.date
```

---

#### 3.12 Filters: Company + Person + Product

**패턴:**
```json
{
  "target": {"node_type": "Event"},
  "filters": [
    {"node_type": "Company", "ticker": "AAPL"},
    {"node_type": "Person", "name": "Tim Cook"},
    {"node_type": "Product", "name": "iPhone 15"}
  ]
}
```

**Cypher Query:**
```cypher
MATCH (c:Company {ticker: $company_ticker})-[r1:HAS_RELATION]->(p:Person {name: $person_name})-[r2:IS_MENTIONED_IN]->(pr:Product {name: $product_name})-[r3:IS_MENTIONED_IN]->(e:Event)
WHERE e.ticker = $company_ticker
RETURN e.id, e.entity, e.description, e.ticker, e.date
```

---

#### 3.13 Filters: Company + Technology + Product

**패턴:**
```json
{
  "target": {"node_type": "Event"},
  "filters": [
    {"node_type": "Company", "ticker": "AAPL"},
    {"node_type": "Technology", "name": "AI 기술"},
    {"node_type": "Product", "name": "iPhone 15"}
  ]
}
```

**Cypher Query:**
```cypher
MATCH (c:Company {ticker: $company_ticker})-[r1:HAS_TECHNOLOGIES]->(t:Technology {entity: $technology_name})-[r2:IS_MENTIONED_IN]->(pr:Product {name: $product_name})-[r3:IS_MENTIONED_IN]->(e:Event)
WHERE e.ticker = $company_ticker
RETURN e.id, e.entity, e.description, e.ticker, e.date
```

---

#### 3.14 Filters: Person + Technology + Product

**패턴:**
```json
{
  "target": {"node_type": "Event"},
  "filters": [
    {"node_type": "Person", "name": "Tim Cook"},
    {"node_type": "Technology", "name": "AI 기술"},
    {"node_type": "Product", "name": "iPhone 15"}
  ]
}
```

**Cypher Query:**
```cypher
MATCH (p:Person {name: $person_name})-[r1:IS_MENTIONED_IN]->(t:Technology {entity: $technology_name})-[r2:IS_MENTIONED_IN]->(pr:Product {name: $product_name})-[r3:IS_MENTIONED_IN]->(e:Event)
RETURN e.id, e.entity, e.description, e.ticker, e.date
```

---

#### 3.15 Filters: Company + Person + Technology + Product

**패턴:**
```json
{
  "target": {"node_type": "Event"},
  "filters": [
    {"node_type": "Company", "ticker": "AAPL"},
    {"node_type": "Person", "name": "Tim Cook"},
    {"node_type": "Technology", "name": "AI 기술"},
    {"node_type": "Product", "name": "iPhone 15"}
  ]
}
```

**Cypher Query:**
```cypher
MATCH (c:Company {ticker: $company_ticker})-[r1:HAS_RELATION]->(p:Person {name: $person_name})-[r2:IS_MENTIONED_IN]->(t:Technology {entity: $technology_name})-[r3:IS_MENTIONED_IN]->(pr:Product {name: $product_name})-[r4:IS_MENTIONED_IN]->(e:Event)
WHERE e.ticker = $company_ticker
RETURN e.id, e.entity, e.description, e.ticker, e.date
```

---

## 📊 패턴 요약

### 총 패턴 수
- **Target**: 3개 (Opportunity, Risk, Event)
- **Filter 조합**: 15개 (단일 4개 + 2개 조합 6개 + 3개 조합 4개 + 4개 조합 1개)
- **총 패턴**: 3 × 15 = **45개**

### Filter 조합 목록
1. Company만
2. Person만
3. Technology만
4. Product만
5. Company + Person
6. Company + Technology
7. Company + Product
8. Person + Technology
9. Person + Product
10. Technology + Product
11. Company + Person + Technology
12. Company + Person + Product
13. Company + Technology + Product
14. Person + Technology + Product
15. Company + Person + Technology + Product

## 🔧 사용 방법

1. Intent 분석 결과에서 `target`과 `filters` 추출
2. `target.node_type`과 `filters`의 조합으로 패턴 매칭
3. 매칭된 패턴의 Cypher 쿼리 템플릿 사용
4. `filters`의 실제 값(ticker, name)을 쿼리 파라미터로 바인딩
5. 쿼리 실행 및 결과 반환

## ⚠️ 주의사항

1. **Company 필터가 있는 경우**: target 노드의 `ticker`와 일치하는지 WHERE 절로 검증
2. **IS_MENTIONED_IN 링크**: Product, Person, Technology는 모두 IS_MENTIONED_IN으로 target에 연결
3. **HAS_RELATION 링크**: Company와 Person 사이에만 사용
4. **MAKE 링크**: Company와 Product 사이에만 사용
5. **HAS_TECHNOLOGIES 링크**: Company와 Technology 사이에만 사용

