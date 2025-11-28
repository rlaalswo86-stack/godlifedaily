import streamlit as st

# ... import 문들 ...

# --------------------------------------------------------------------------
# [Style] 메뉴 버튼은 살리고, 잡다한 버튼만 숨기기
# --------------------------------------------------------------------------
hide_decoration_bar_style = '''
    <style>
        /* 1. 우측 상단 'Deploy/Fork' 버튼 숨기기 */
        .stDeployButton {visibility: hidden;}
        
        /* 2. 우측 상단 툴바(점 3개 메뉴) 숨기기 */
        /* 이 부분에서 아이콘 로딩 에러로 글자가 깨지는 경우가 많습니다 */
        [data-testid="stToolbar"] {visibility: hidden;}
        
        /* 3. 상단 데코레이션(무지개 라인) 숨기기 */
        [data-testid="stDecoration"] {visibility: hidden;}

        /* 4. 하단 푸터 숨기기 */
        footer {visibility: hidden;}
        
        /* [중요] 헤더 전체는 건드리지 않습니다! 그래야 메뉴(☰)가 눌립니다 */
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
