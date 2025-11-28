import streamlit as st

# --------------------------------------------------------------------------
# [Style] Pro Mode + 모바일 메뉴 위치 보정
# --------------------------------------------------------------------------
style_fix = '''
    <style>
        /* 1. 우측 상단 툴바 (점 3개, Fork 버튼) 숨기기 */
        [data-testid="stToolbar"] {
            display: none;
        }
        
        /* 2. 상단 데코레이션 (무지개 라인) 숨기기 */
        [data-testid="stDecoration"] {
            display: none;
        }

        /* 3. 하단 푸터 숨기기 */
        footer {
            display: none;
        }

        /* 4. [핵심] 햄버거 메뉴 버튼 위치 강제 조정 */
        /* 무지개 라인이 사라져서 위로 밀린 버튼을 안전한 곳으로 내립니다 */
        [data-testid="stSidebarCollapsedControl"] {
            top: 15px !important;    /* 위에서 15px 떨어트림 (잘림 방지) */
            left: 10px !important;   /* 왼쪽 여백 */
            display: block !important;
            z-index: 99999 !important; /* 무조건 맨 위에 그리기 */
        }
    </style>
'''
st.markdown(style_fix, unsafe_allow_html=True)

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
