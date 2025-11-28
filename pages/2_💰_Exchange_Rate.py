import streamlit as st
import yfinance as yf
import pandas as pd
import time

# --------------------------------------------------------------------------
# [Page Setup] 페이지 기본 설정
# --------------------------------------------------------------------------
st.set_page_config(page_title="Exchange Rate Monitor", page_icon="💰")

# [Style] 모바일 최적화 및 잡다한 UI 숨기기
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
st.markdown("Yahoo Finance 데이터를 기반으로 합니다. (안정성 강화 버전)")

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
# [Helper Function] 쉼표 처리기 (String -> Float 변환)
# --------------------------------------------------------------------------
def clean_currency_input(value_str):
    """
    사용자가 '1,000,000' 처럼 쉼표를 넣어서 입력해도
    알아서 쉼표를 떼고 숫자로 바꿔줍니다.
    """
    try:
        # 문자열로 들어온 값에서 쉼표(,)를 제거하고 실수형(float)으로 변환
        return float(str(value_str).replace(',', ''))
    except ValueError:
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
        st.metric(
            label="🇺🇸 미국 달러 (USD)", 
            value=f"{rates['USD']['price']:,.2f} 원", 
            delta=f"{rates['USD']['change']:,.2f} 원"
        )
    with col2:
        st.metric(
            label="🇹🇭 태국 바트 (THB)", 
            value=f"{rates['THB']['price']:,.2f} 원", 
            delta=f"{rates['THB']['change']:,.2f} 원"
        )
    st.caption("※ Yahoo Finance 제공 데이터이며, 실제 은행 고시 환율과 약간의 차이가 있을 수 있습니다.")
else:
    st.error("환율 서버 연결에 실패했습니다. 잠시 후 다시 시도해주세요.")

st.divider()

# --------------------------------------------------------------------------
# [Feature] 디지털 노마드 계산기 (쉼표 기능 적용)
# --------------------------------------------------------------------------
st.subheader("🧮 치앙마이 한달 살기 계산기")

if rates:
    thb_rate = rates['THB']['price']
    
    calc_tab1, calc_tab2 = st.tabs(["KRW → THB (환전)", "THB → KRW (물가 체감)"])

    with calc_tab1:
        st.caption("가져갈 한국 돈을 입력하세요 (쉼표 사용 가능)")
        # [수정 포인트] number_input 대신 text_input 사용
        krw_input_str = st.text_input("한국 돈 (원)", value="1,000,000")
        
        # 입력값 전처리 (Parsing)
        krw_val = clean_currency_input(krw_input_str)
        
        if krw_val > 0:
            thb_result = krw_val / thb_rate
            st.success(f"💰 **{krw_input_str} 원**은 약 **{thb_result:,.0f} 바트**입니다.")
        else:
            st.warning("올바른 숫자를 입력해주세요.")

    with calc_tab2:
        st.caption("현지 물건 가격을 입력하세요 (쉼표 사용 가능)")
        # [수정 포인트] number_input 대신 text_input 사용
        thb_input_str = st.text_input("현지 가격 (바트)", value="100")
        
        # 입력값 전처리 (Parsing)
        thb_val = clean_currency_input(thb_input_str)
        
        if thb_val > 0:
            krw_result = thb_val * thb_rate
            st.info(f"🇹🇭 **{thb_input_str} 바트**는 한국 돈으로 약 **{krw_result:,.0f} 원**입니다.")
            
            coffee_price = 4500
            if krw_result < coffee_price:
                 st.write("☕ 오! 한국 커피 한 잔보다 싸네요!")
            else:
                 st.write("💸 흠... 한국 커피보다 비싸군요!")
        else:
            st.warning("올바른 숫자를 입력해주세요.")
