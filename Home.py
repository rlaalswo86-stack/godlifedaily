import streamlit as st

# ... import 문들 ...
# --------------------------------------------------------------------------
# [Style] 모바일 메뉴 버튼 강제 노출 (Ultimate Fix)
# --------------------------------------------------------------------------
mobile_style_fix = '''
    <style>
        /* 1. 햄버거 메뉴 버튼(사이드바 열기)을 강제로 최상단에 띄움 */
        [data-testid="stSidebarCollapsedControl"] {
            display: block !important;
            visibility: visible !important;
            z-index: 100000 !important; /* 다른 요소보다 무조건 위에 배치 */
            color: white !important;    /* 아이콘 색상을 흰색으로 고정 (배경이 어두울 경우 대비) */
            left: 1rem !important;      /* 위치 강제 지정 */
            top: 1rem !important;
        }
        
        /* 2. 우측 상단 툴바(이상한 글씨 원인) 아예 없애기 */
        [data-testid="stToolbar"] {
            display: none !important;
        }

        /* 3. 상단 헤더 배경 투명하게 (버튼 가림 방지) */
        [data-testid="stHeader"] {
            background-color: transparent !important;
        }

        /* 4. 푸터 숨기기 */
        footer {
            display: none !important;
        }
    </style>
'''
st.markdown(mobile_style_fix, unsafe_allow_html=True)

# ... 기존 st.set_page_config ...

st.set_page_config(
    page_title="God-Life Daily",
    page_icon="👋",
)

st.write("# Welcome to God-Life Daily! 👋")

st.markdown(
    """
    ### 디지털 노마드를 위한 통합 대시보드입니다.
    
    왼쪽 사이드바에서 원하는 메뉴를 선택하세요.
    
    - **📈 US Stock:** 미국 주식 전수 조사 및 분석
    - **💰 Exchange Rate:** 실시간 환율 조회 (태국 바트/달러)
    - **✈️ Travel:** (준비 중) 최저가 항공권 검색
    
    ---
    *Built by HW Engineer & Silicon Valley Mentor*
    """
)
