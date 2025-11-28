import streamlit as st

# ... import 문들 ...

# --------------------------------------------------------------------------
# [Style] 메뉴 버튼은 살리고, 잡다한 텍스트만 숨기기 (Mobile Fix)
# --------------------------------------------------------------------------
hide_decoration_bar_style = '''
    <style>
        /* 1. 우측 상단 툴바(점 3개, Fork 버튼 등) 숨기기 */
        /* 여기서 글자 깨짐 현상이 발생하므로 숨깁니다 */
        [data-testid="stToolbar"] {
            visibility: hidden;
            right: 2rem;
        }
        
        /* 2. 상단 데코레이션(무지개 라인) 숨기기 */
        [data-testid="stDecoration"] {
            display: none;
        }

        /* 3. 하단 푸터 숨기기 */
        footer {
            visibility: hidden;
        }

        /* [핵심] 헤더 컨테이너는 강제로 보이게 설정! */
        /* 이걸 해야 왼쪽 햄버거 메뉴(☰)가 살아납니다 */
        header {
            visibility: visible !important;
            background-color: transparent !important;
        }
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
