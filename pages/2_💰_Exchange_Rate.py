import streamlit as st
import yfinance as yf
import pandas as pd
import time

# --------------------------------------------------------------------------
# [Page Setup] 페이지 기본 설정
# --------------------------------------------------------------------------
st.set_page_config(page_title="Exchange Rate Monitor", page_icon="💰")

# [Style] 모바일 메뉴 살리기 & 잡다한 UI 숨기기
hide_decoration_bar_style = '''
    <style>
        [data-testid="stToolbar"] {display: none;}
        [data-testid="stDecoration"] {display: none;}
        footer {display: none;}
        [data-testid="stSidebarCollapsedControl"] {
            top: 15px !important; left: 10px !important;
            display: block !important; z-index: 99999 !important;
        }
    </style>
'''
st.markdown(hide_decoration_bar_style, unsafe_allow_html=True)

st.title("💰 실시간 환율 대시보드")
st.markdown("Yahoo Finance 데이터를 기반으로 합니다.")

# --------------------------------------------------------------------------
# [Function] 환율 데이터 가져오기
# --------------------------------------------------------------------------
@st.cache_data(ttl=600)
def get_exchange_rate_data():
    tickers = ['KRW=X', 'THBKRW=X']
    try:
        data = yf.download(tickers, period="5d", interval="1d", progress=False)['Close']
        if not data.empty:
            usd_price = data['KRW=X'].iloc[-1]
            usd_change = usd_price - data['KRW=X'].iloc[-2]
            
            thb_price = data['THBKRW=X'].iloc[-1]
            thb_change = thb_price - data['THBKRW=X'].iloc[-2]
            
            return {
                'USD': {'price': usd_price, 'change': usd_change},
                'THB': {'price': thb_price, 'change': thb_change}
            }
        return None
    except Exception as e:
        return None

# --------------------------------------------------------------------------
# [Callback Logic] 입력값 자동 포맷팅 (Interrupt Service Routine)
# --------------------------------------------------------------------------
# 사용자가 엔터를 치면 이 함수가 실행되어 값을 '성형수술' 합니다.
def format_krw_input():
    # 현재 입력된 값 가져오기
    val = st.session_state.krw_input_key
    try:
        # 쉼표 제거 후 숫자로 변환
        num = float(val.replace(',', ''))
        # 다시 쉼표가 있는 문자열로 변환하여 저장
        st.session_state.krw_input_key = f"{num:,.0f}"
    except:
        # 숫자가 아니면 0으로 초기화
        st.session_state.krw_input_key = "0"

def format_thb_input():
    val = st.session_state.thb_input_key
    try:
        num = float(val.replace(',', ''))
        st.session_state.thb_input_key = f"{num:,.0f}"
    except:
        st.session_state.thb_input_key = "0"

# --------------------------------------------------------------------------
# [Helper] 계산용 숫자 변환기
# --------------------------------------------------------------------------
def parse_currency(val_str):
    try:
        return float(val_str.replace(',', ''))
    except:
        return 0.0

# --------------------------------------------------------------------------
# [UI Section]
# --------------------------------------------------------------------------
if st.button("🔄 환율 정보 새로고침"):
    st.cache_data.clear()

with st.spinner('환율 정보를 수신 중입니다...'):
    rates = get_exchange_rate_data()

st.divider()

if rates:
    col1, col2 = st.columns(2)
    with col1:
        st.metric(label="🇺🇸 미국 달러 (USD)", value=f"{rates['USD']['price']:,.2f} 원", delta=f"{rates['USD']['change']:,.2f} 원")
    with col2:
        st.metric(label="🇹🇭 태국 바트 (THB)", value=f"{rates['THB']['price']:,.2f} 원", delta=f"{rates['THB']['change']:,.2f} 원")
    st.caption("※ Yahoo Finance 제공 데이터")
else:
    st.error("환율 서버 연결 실패")

st.divider()

# --------------------------------------------------------------------------
# [Feature] 디지털 노마드 계산기 (Auto-Format 적용)
# --------------------------------------------------------------------------
st.subheader("🧮 치앙마이 한달 살기 계산기")

if rates:
    thb_rate = rates['THB']['price']
    
    calc_tab1, calc_tab2 = st.tabs(["KRW → THB (환전)", "THB → KRW (물가 체감)"])

    with calc_tab1:
        st.caption("가져갈 한국 돈을 입력하고 엔터(Enter)를 누르세요.")
        
        # [핵심] on_change=format_krw_input : 엔터 칠 때 포맷팅 함수 실행
        # key="krw_input_key" : 이 입력창의 고유 주소 (Address)
        krw_input_str = st.text_input(
            "한국 돈 (원)", 
            value="1,000,000", 
            key="krw_input_key", 
            on_change=format_krw_input
        )
        
        krw_val = parse_currency(krw_input_str)
        if krw_val > 0:
            thb_result = krw_val / thb_rate
            st.success(f"💰 **{krw_input_str} 원**은 약 **{thb_result:,.0f} 바트**입니다.")

    with calc_tab2:
        st.caption("현지 가격을 입력하고 엔터(Enter)를 누르세요.")
        
        # [핵심] 바트 입력창도 동일하게 처리
        thb_input_str = st.text_input(
            "현지 가격 (바트)", 
            value="100", 
            key="thb_input_key", 
            on_change=format_thb_input
        )
        
        thb_val = parse_currency(thb_input_str)
        if thb_val > 0:
            krw_result = thb_val * thb_rate
            st.info(f"🇹🇭 **{thb_input_str} 바트**는 한국 돈으로 약 **{krw_result:,.0f} 원**입니다.")
            
            if krw_result < 4500:
                 st.write("☕ 오! 한국 커피 한 잔보다 싸네요!")
            else:
                 st.write("💸 흠... 한국 커피보다 비싸군요!")
