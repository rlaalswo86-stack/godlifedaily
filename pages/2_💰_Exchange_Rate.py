import streamlit as st
import yfinance as yf
import pandas as pd
import time

# --------------------------------------------------------------------------
# [Page Setup] 페이지 기본 설정
# --------------------------------------------------------------------------
st.set_page_config(page_title="Exchange Rate Monitor", page_icon="💰")

st.title("💰 실시간 환율 대시보드")
st.markdown("Yahoo Finance 데이터를 기반으로 합니다. (안정성 강화 버전)")

# --------------------------------------------------------------------------
# [Function] 환율 데이터 가져오기 (yfinance 사용)
# --------------------------------------------------------------------------
@st.cache_data(ttl=600)  # 10분 캐싱
def get_exchange_rate_data():
    """
    yfinance를 통해 환율 정보를 가져옵니다.
    - KRW=X: USD/KRW (달러 원화 환율)
    - THBKRW=X: THB/KRW (바트 원화 환율)
    """
    tickers = ['KRW=X', 'THBKRW=X']
    
    try:
        # 두 개의 환율 정보를 한 번에 요청 (Batch Request)
        data = yf.download(tickers, period="5d", interval="1d", progress=False)['Close']
        
        # 최신 데이터 추출 (오늘 종가 or 현재가)
        # 데이터프레임 구조가 티커별로 컬럼이 생기므로 각각 추출
        if not data.empty:
            # 1. 달러 (USD)
            usd_price = data['KRW=X'].iloc[-1]
            usd_prev = data['KRW=X'].iloc[-2]
            usd_change = usd_price - usd_prev
            
            # 2. 바트 (THB)
            thb_price = data['THBKRW=X'].iloc[-1]
            thb_prev = data['THBKRW=X'].iloc[-2]
            thb_change = thb_price - thb_prev
            
            return {
                'USD': {'price': usd_price, 'change': usd_change},
                'THB': {'price': thb_price, 'change': thb_change}
            }
            
        return None
    except Exception as e:
        st.error(f"데이터 수신 실패: {e}")
        return None

# --------------------------------------------------------------------------
# [UI Section] 화면 구성
# --------------------------------------------------------------------------

# 1. 새로고침 버튼
if st.button("🔄 환율 정보 새로고침"):
    st.cache_data.clear()

# 2. 데이터 수신 (Sensing)
with st.spinner('환율 정보를 수신 중입니다...'):
    rates = get_exchange_rate_data()

# 3. 메트릭 표시 (Display)
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
    
    # 데이터 소스 정보 (Timestamp)
    st.caption("※ Yahoo Finance 제공 데이터이며, 실제 은행 고시 환율과 약간의 차이가 있을 수 있습니다.")

else:
    st.error("환율 서버 연결에 실패했습니다. 잠시 후 다시 시도해주세요.")

st.divider()

# --------------------------------------------------------------------------
# [Feature] 디지털 노마드 계산기
# --------------------------------------------------------------------------
st.subheader("🧮 치앙마이 한달 살기 계산기")

if rates:
    thb_rate = rates['THB']['price']
    
    calc_tab1, calc_tab2 = st.tabs(["KRW → THB (환전)", "THB → KRW (물가 체감)"])

    with calc_tab1:
        krw_input = st.number_input("가져갈 한국 돈 (원)", value=1000000, step=10000)
        thb_result = krw_input / thb_rate
        st.success(f"💰 약 **{thb_result:,.0f} 바트**로 환전됩니다.")

    with calc_tab2:
        thb_input = st.number_input("현지 물건 가격 (바트)", value=100)
        krw_result = thb_input * thb_rate
        st.info(f"🇰🇷 한국 돈으로 약 **{krw_result:,.0f} 원** 입니다.")
        
        coffee_price = 4500
        if krw_result < coffee_price:
             st.write("☕ 한국 커피 한 잔보다 싸네요!")
        else:
             st.write("💸 한국 커피보다 비싸군요!")
