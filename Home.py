import streamlit as st

# --------------------------------------------------------------------------
# [Style] Pro Mode: 잡다한 UI 요소 숨기기 (이제 안전함!)
# --------------------------------------------------------------------------
hide_decoration_bar_style = '''
    <style>
        /* 우측 상단 툴바(점 3개, Fork 버튼) 숨기기 */
        [data-testid="stToolbar"] {visibility: hidden;}
        
        /* 상단 데코레이션(무지개 라인) 숨기기 */
        [data-testid="stDecoration"] {display: none;}

        /* 하단 푸터(Made with Streamlit) 숨기기 */
        footer {visibility: hidden;}
        
        /* 헤더 배경 투명하게 (깔끔함 유지) */
        header {background-color: transparent !important;}
    </style>
'''
st.markdown(hide_decoration_bar_style, unsafe_allow_html=True)

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
