"""
Streamlit API 클라이언트

Financial Knowledge Graph API를 테스트할 수 있는 웹 인터페이스
"""

import streamlit as st
import requests
import json
from typing import Dict, Any
import time

# 페이지 설정
st.set_page_config(
    page_title="Financial KG API 테스트",
    page_icon="📊",
    layout="wide"
)

# API 기본 URL
API_BASE_URL = st.sidebar.text_input(
    "API 서버 URL",
    value="http://localhost:8001",
    help="API 서버의 기본 URL을 입력하세요"
)

# 사이드바
st.sidebar.title("📊 Financial KG API")
st.sidebar.markdown("---")
st.sidebar.markdown("### API 엔드포인트")
st.sidebar.markdown("""
- **질의 응답** (`/answer`)
- **공시 다운로드** (`/download`)
- **문서 처리** (`/process`)
""")

# 메인 타이틀
st.title("📊 Financial Knowledge Graph API 테스트 클라이언트")

# 탭 생성
tab1, tab2, tab3 = st.tabs(["🔍 질의 응답", "📥 공시 다운로드", "⚙️ 문서 처리"])

# ============================================================================
# 탭 1: 질의 응답 API
# ============================================================================
with tab1:
    st.header("🔍 질의 응답 API 테스트")
    st.markdown("사용자 질의에 대한 답변을 스트리밍으로 받습니다.")
    
    col1, col2 = st.columns([2, 1])
    
    with col1:
        query = st.text_area(
            "질의 입력",
            value="애플의 기회 요소를 알려줘",
            height=100,
            help="질의를 입력하세요"
        )
    
    with col2:
        use_vector_search = st.checkbox(
            "Vector 검색 사용",
            value=False,
            help="Vector 검색을 활성화합니다"
        )
        top_k = st.number_input(
            "최대 결과 수",
            min_value=1,
            max_value=50,
            value=5,
            help="반환할 최대 결과 수"
        )
    
    if st.button("질의 전송", type="primary", use_container_width=True):
        if not query:
            st.error("질의를 입력해주세요.")
        else:
            with st.spinner("답변 생성 중..."):
                try:
                    request_data = {
                        "query": query,
                        "use_vector_search": use_vector_search,
                        "top_k": top_k
                    }
                    
                    # 스트리밍 요청
                    response = requests.post(
                        f"{API_BASE_URL}/answer",
                        json=request_data,
                        stream=True,
                        timeout=60
                    )
                    
                    if response.status_code == 200:
                        st.success("✅ 답변 생성 완료")
                        st.markdown("---")
                        
                        # 스트리밍 응답 표시
                        answer_placeholder = st.empty()
                        full_text = ""
                        
                        for line in response.iter_lines():
                            if line:
                                line_str = line.decode('utf-8')
                                if line_str.startswith('data: '):
                                    chunk = line_str[6:]  # 'data: ' 제거
                                    if chunk == '[DONE]':
                                        break
                                    full_text += chunk
                                    answer_placeholder.markdown(full_text)
                        
                        st.markdown("---")
                        st.caption(f"전체 응답 길이: {len(full_text)} 문자")
                    else:
                        st.error(f"❌ 에러: {response.status_code}")
                        st.json(response.json())
                        
                except requests.exceptions.RequestException as e:
                    st.error(f"❌ 요청 실패: {str(e)}")
                except Exception as e:
                    st.error(f"❌ 에러: {str(e)}")

# ============================================================================
# 탭 2: 공시 다운로드 API
# ============================================================================
with tab2:
    st.header("📥 공시 다운로드 API 테스트")
    st.markdown("SEC EDGAR에서 공시 자료를 다운로드합니다.")
    
    col1, col2 = st.columns(2)
    
    with col1:
        ticker = st.text_input(
            "티커 심볼",
            value="AAPL",
            help="다운로드할 기업의 티커 심볼 (예: AAPL, TSLA)"
        ).upper()
    
    with col2:
        filing_types = st.multiselect(
            "공시 유형",
            options=["10-K", "10-Q", "8-K"],
            default=["10-K"],
            help="다운로드할 공시 유형을 선택하세요"
        )
    
    st.markdown("### 다운로드 제한 설정")
    col1, col2, col3 = st.columns(3)
    
    limits = {}
    with col1:
        limit_10k = st.number_input("10-K 제한", min_value=1, max_value=10, value=3)
        if "10-K" in filing_types:
            limits["10-K"] = limit_10k
    with col2:
        limit_10q = st.number_input("10-Q 제한", min_value=1, max_value=20, value=12)
        if "10-Q" in filing_types:
            limits["10-Q"] = limit_10q
    with col3:
        limit_8k = st.number_input("8-K 제한", min_value=1, max_value=50, value=20)
        if "8-K" in filing_types:
            limits["8-K"] = limit_8k
    
    if st.button("다운로드 시작", type="primary", use_container_width=True):
        if not ticker:
            st.error("티커 심볼을 입력해주세요.")
        elif not filing_types:
            st.error("공시 유형을 선택해주세요.")
        else:
            with st.spinner("다운로드 중... (시간이 걸릴 수 있습니다)"):
                try:
                    request_data = {
                        "ticker": ticker,
                        "filing_types": filing_types,
                        "limits": limits if limits else None
                    }
                    
                    st.json(request_data)
                    
                    # 진행 상황 표시를 위한 progress bar
                    progress_bar = st.progress(0)
                    status_text = st.empty()
                    
                    response = requests.post(
                        f"{API_BASE_URL}/download",
                        json=request_data,
                        timeout=600  # 10분 타임아웃
                    )
                    
                    progress_bar.progress(100)
                    
                    if response.status_code == 200:
                        result = response.json()
                        st.success("✅ 다운로드 완료")
                        st.json(result)
                        
                        # 결과 요약
                        st.markdown("### 다운로드 결과 요약")
                        col1, col2, col3 = st.columns(3)
                        with col1:
                            st.metric("티커", result.get("ticker", ""))
                        with col2:
                            st.metric("총 파일 수", result.get("total_files", 0))
                        with col3:
                            st.metric("공시 유형 수", len(result.get("results", {})))
                        
                        # 공시 유형별 결과
                        if result.get("results"):
                            st.markdown("#### 공시 유형별 다운로드 수")
                            for filing_type, count in result["results"].items():
                                st.write(f"- **{filing_type}**: {count}건")
                    else:
                        st.error(f"❌ 에러: {response.status_code}")
                        try:
                            st.json(response.json())
                        except:
                            st.text(response.text)
                            
                except requests.exceptions.Timeout:
                    st.error("❌ 요청 시간 초과 (10분)")
                except requests.exceptions.RequestException as e:
                    st.error(f"❌ 요청 실패: {str(e)}")
                except Exception as e:
                    st.error(f"❌ 에러: {str(e)}")

# ============================================================================
# 탭 3: 문서 처리 API
# ============================================================================
with tab3:
    st.header("⚙️ 문서 처리 및 Graph DB 적재 API 테스트")
    st.markdown("다운로드된 공시 문서를 처리하고 Graph DB에 적재합니다.")
    
    col1, col2 = st.columns(2)
    
    with col1:
        ticker = st.text_input(
            "티커 심볼",
            value="AAPL",
            help="처리할 기업의 티커 심볼",
            key="process_ticker"
        ).upper()
    
    with col2:
        filing_types = st.multiselect(
            "공시 유형",
            options=["10-K", "10-Q", "8-K"],
            default=["10-K"],
            help="처리할 공시 유형을 선택하세요",
            key="process_filing_types"
        )
    
    col1, col2 = st.columns(2)
    
    with col1:
        skip_duplicates = st.checkbox(
            "중복 문서 건너뛰기",
            value=True,
            help="이미 처리된 문서는 건너뜁니다"
        )
    
    with col2:
        with_embedding = st.checkbox(
            "Embedding 생성",
            value=True,
            help="노드에 embedding을 생성합니다 (시간이 더 걸립니다)"
        )
    
    if st.button("문서 처리 시작", type="primary", use_container_width=True):
        if not ticker:
            st.error("티커 심볼을 입력해주세요.")
        elif not filing_types:
            st.error("공시 유형을 선택해주세요.")
        else:
            with st.spinner("문서 처리 중... (시간이 오래 걸릴 수 있습니다)"):
                try:
                    request_data = {
                        "ticker": ticker,
                        "skip_duplicates": skip_duplicates,
                        "with_embedding": with_embedding,
                        "filing_types": filing_types if filing_types else None
                    }
                    
                    st.json(request_data)
                    
                    # 진행 상황 표시
                    progress_bar = st.progress(0)
                    status_text = st.empty()
                    status_text.info("처리 중...")
                    
                    response = requests.post(
                        f"{API_BASE_URL}/process",
                        json=request_data,
                        timeout=1800  # 30분 타임아웃
                    )
                    
                    progress_bar.progress(100)
                    status_text.empty()
                    
                    if response.status_code == 200:
                        result = response.json()
                        st.success("✅ 문서 처리 완료")
                        st.json(result)
                        
                        # 결과 요약
                        st.markdown("### 처리 결과 요약")
                        col1, col2, col3, col4 = st.columns(4)
                        with col1:
                            st.metric("티커", result.get("ticker", ""))
                        with col2:
                            st.metric("처리된 파일", result.get("processed_files", 0))
                        with col3:
                            st.metric("건너뛴 파일", result.get("skipped_files", 0))
                        with col4:
                            graph_stats = result.get("graph_stats", {})
                            total_nodes = sum(graph_stats.get("nodes", {}).values()) if isinstance(graph_stats.get("nodes"), dict) else 0
                            st.metric("총 노드 수", total_nodes)
                        
                        # Graph 통계 상세
                        if graph_stats:
                            st.markdown("#### Graph DB 통계")
                            if isinstance(graph_stats.get("nodes"), dict):
                                st.write("**노드 타입별 수:**")
                                for node_type, count in graph_stats["nodes"].items():
                                    st.write(f"- **{node_type}**: {count}개")
                            
                            if graph_stats.get("links"):
                                st.write(f"**총 링크 수**: {graph_stats['links']}개")
                    else:
                        st.error(f"❌ 에러: {response.status_code}")
                        try:
                            st.json(response.json())
                        except:
                            st.text(response.text)
                            
                except requests.exceptions.Timeout:
                    st.error("❌ 요청 시간 초과 (30분)")
                except requests.exceptions.RequestException as e:
                    st.error(f"❌ 요청 실패: {str(e)}")
                except Exception as e:
                    st.error(f"❌ 에러: {str(e)}")

# ============================================================================
# 사이드바: 서버 상태 확인
# ============================================================================
st.sidebar.markdown("---")
st.sidebar.markdown("### 서버 상태")

if st.sidebar.button("서버 연결 확인"):
    try:
        response = requests.get(f"{API_BASE_URL}/health", timeout=5)
        if response.status_code == 200:
            st.sidebar.success("✅ 서버 연결 성공")
            st.sidebar.json(response.json())
        else:
            st.sidebar.error(f"❌ 서버 응답 오류: {response.status_code}")
    except requests.exceptions.RequestException as e:
        st.sidebar.error(f"❌ 서버 연결 실패: {str(e)}")

# 푸터
st.sidebar.markdown("---")
st.sidebar.markdown("### 📚 API 문서")
st.sidebar.markdown(f"[Swagger UI]({API_BASE_URL}/docs)")
st.sidebar.markdown(f"[ReDoc]({API_BASE_URL}/redoc)")


