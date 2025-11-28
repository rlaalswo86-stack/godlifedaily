import streamlit as st
import requests
from bs4 import BeautifulSoup
import time

# --------------------------------------------------------------------------
# [Page Setup] 페이지 기본 설정
# --------------------------------------------------------------------------
st.set_page_config(page_title="Exchange Rate Monitor", page_icon="💰")

st.title("💰 실시간 환율 대시보드")
st.markdown("네이버 금융(Naver Finance) 데이터를 기반으로 합니다.")

# --------------------------------------------------------------------------
# [Function] 환율 크롤링 (Data Acquisition)
# --------------------------------------------------------------------------
# 반복적인 새로고침 시 속도 저하를 막기 위해 캐시를 사용합니다. (새로고침 버튼 누르면 초기화)
@st.cache_data(ttl=600)  # 10분(600초) 동안은 데이터 유지 (Too many request 방지)
def get_exchange_rate(currency_code):
    """
    currency_code 예시: 
    - 미국 달러: 'FX_USDKRW'
    - 태국 바트: 'FX_THBKRW'
    """
    url = f"https://finance.naver.com/marketindex/exchangeDetail.naver?marketindexCd={currency_code}"
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/58.0.3029.110 Safari/537.36'
    }
    
    try:
        res = requests.get(url, headers=headers)
        if res.status_code == 200:
            soup = BeautifulSoup(res.content, "html.parser")
            
            # [수정] 더 정확한 '매매기준율'을 가져오기 위해 selector를 변경했습니다.
            # div.head_info 안에 있는 span.value가 가장 메인 환율입니다.
            rate_element = soup.select_one('div.head_info > span.value')
            
            # 전일 대비 등락폭 가져오기 (Bonus)
            change_element = soup.select_one('div.head_info > span.change')
            is_up = soup.select_one('div.head_info > span.blind').text == "상승"
            
            if rate_element:
                rate = float(rate_element.text.replace(",", ""))
                change = float(change_element.text.replace(",", ""))
                
                # 하락이면 마이너스 붙이기
                if not is_up:
                    change = -change
                    
                return rate, change
        return None, None
        
    except Exception as e:
        st.error(f"통신 에러: {e}")
        return None, None

# --------------------------------------------------------------------------
# [UI Section] 화면 구성
# --------------------------------------------------------------------------

# 1. 새로고침 버튼 (Manual Trigger)
if st.button("🔄 환율 정보 새로고침"):
    st.cache_data.clear() # 캐시 삭제하여 강제 재요청

# 2. 데이터 가져오기 (Sensing)
with st.spinner('환율 정보를 수신 중입니다...'):
    usd_rate, usd_change = get_exchange_rate("FX_USDKRW") # 달러
    thb_rate, thb_change = get_exchange_rate("FX_THBKRW") # 바트

# 3. 메트릭 표시 (Display)
st.divider()
col1, col2 = st.columns(2)

with col1:
    if usd_rate:
        st.metric(
            label="🇺🇸 미국 달러 (USD)", 
            value=f"{usd_rate:,.2f} 원", 
            delta=f"{usd_change:,.2f} 원"
        )
    else:
        st.error("데이터 수신 실패")

with col2:
    if thb_rate:
        st.metric(
            label="🇹🇭 태국 바트 (THB)", 
            value=f"{thb_rate:,.2f} 원", 
            delta=f"{thb_change:,.2f} 원"
        )
    else:
        st.error("데이터 수신 실패")

st.divider()

# --------------------------------------------------------------------------
# [Feature] 디지털 노마드 계산기 (Calculator)
# --------------------------------------------------------------------------
st.subheader("🧮 치앙마이 한달 살기 계산기")

# 탭으로 기능 분리
calc_tab1, calc_tab2 = st.tabs(["KRW → THB (환전)", "THB → KRW (물가 체감)"])

with calc_tab1:
    krw_input = st.number_input("가져갈 한국 돈 (원)", value=1000000, step=10000)
    if thb_rate:
        thb_result = krw_input / thb_rate
        st.success(f"💰 약 **{thb_result:,.0f} 바트**로 환전됩니다.")
        st.caption(f"(참고: 실제 환전 시 수수료 때문에 이보다 적을 수 있습니다.)")

with calc_tab2:
    thb_input = st.number_input("현지 물건 가격 (바트)", value=100)
    if thb_rate:
        krw_result = thb_input * thb_rate
        st.info(f"🇰🇷 한국 돈으로 약 **{krw_result:,.0f} 원** 입니다.")
        
        # 재미있는 비교 (커피 지수)
        coffee_price = 4500 # 한국 아메리카노 기준
        if krw_result < coffee_price:
             st.write("☕ 한국 커피 한 잔보다 싸네요!")
        else:
             st.write("💸 한국 커피보다 비싸군요!")
