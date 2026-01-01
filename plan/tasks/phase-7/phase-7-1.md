# Phase 7.1: Graph Loader 모듈 구현

## 📋 개요

FalkorDB에 노드 및 링크를 적재하는 모듈을 구현합니다.

## 🎯 목표

- FalkorDB 연결
- 인덱스 생성
- 노드 생성 (MERGE 사용)
- 링크 생성 (MERGE 사용)
- 중복 방지

## 📝 상세 구현

### 클래스 구조

```python
class GraphLoader:
    """FalkorDB에 노드 및 링크를 적재하는 클래스"""
    
    async def initialize(self):
        """인덱스 및 제약조건 생성"""
    
    async def create_node(self, node: Dict):
        """노드 생성 (MERGE 사용)"""
    
    async def create_link(self, link: Dict):
        """링크 생성 (MERGE 사용)"""
    
    async def load_static_graph(self, ticker: str, static_graph: Dict):
        """Static Graph 적재"""
    
    async def load_dynamic_graph(self, ticker: str, dynamic_graph: Dict):
        """Dynamic Graph 적재"""
```

### 인덱스 생성

- Node 타입별 id 인덱스
- Node 타입별 ticker 인덱스

## 📁 파일 위치

**파일**: `app/services/graph/graph_loader.py`

## ⚠️ 주의사항

- MERGE를 사용하여 중복 방지
- 트랜잭션 처리 고려
- 대량 데이터 적재 시 배치 처리

## 📝 History

