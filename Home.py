import streamlit as st

# ... import 문들 ...
# --------------------------------------------------------------------------
# [Style] 메뉴(☰)는 100% 살리고, 오른쪽 잡동사니만 제거
# --------------------------------------------------------------------------
hide_decoration_bar_style = '''
    <style>
        /* 1. 우측 상단 툴바 (점 3개, Fork 버튼, 에러난 아이콘 텍스트 등) */
        /* visibility 대신 display:none을 써서 아예 공간을 없애버립니다 */
        [data-testid="stToolbar"] {
            display: none !important;
        }

        /* 2. 상단 데코레이션 (무지개 라인) */
        [data-testid="stDecoration"] {
            display: none !important;
        }

        /* 3. 하단 푸터 (Made with Streamlit) */
        footer {
            display: none !important;
        }

        /* [핵심] header 태그에 대한 스타일은 아예 뺐습니다. */
        /* 건드리지 않아야 햄버거 버튼이 자연스럽게 살아납니다. */
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
