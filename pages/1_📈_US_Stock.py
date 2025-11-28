import streamlit as st
import yfinance as yf
import pandas as pd

# 페이지 설정
st.set_page_config(page_title="US Stock Analysis", page_icon="📈")

# --------------------------------------------------------------------------
# [Internal Function] S&P 500 리스트 가져오기
# --------------------------------------------------------------------------
@st.cache_data
def get_sp500_tickers():
    # 1. GitHub CSV 시도 (Primary)
    try:
        csv_url = "https://raw.githubusercontent.com/datasets/s-and-p-500-companies/master/data/constituents.csv"
        df = pd.read_csv(csv_url)
        tickers = df['Symbol'].apply(lambda x: x.replace('.', '-')).tolist()
        return tickers, None
    except Exception as e_csv:
        # 2. 위키피디아 시도 (Secondary)
        try:
            url = 'https://en.wikipedia.org/wiki/List_of_S%26P_500_companies'
            headers = {'User-Agent': 'Mozilla/5.0'}
            tables = pd.read_html(url, storage_options=headers)
            df = None
            for table in tables:
                if 'Symbol' in table.columns and len(table) > 100:
                    df = table
                    break
            if df is None: raise Exception("Table not found")
            tickers = df['Symbol'].apply(lambda x: x.replace('.', '-')).tolist()
            return tickers, None
        except Exception as e_wiki:
            # 3. 비상용 (Fail-safe)
            default_tickers = ['AAPL', 'MSFT', 'GOOGL', 'NVDA', 'TSLA', 'AMZN', 'META', 'AMD', 'INTC', 'KO']
            error_msg = f"데이터 확보 실패. 비상용 리스트로 동작합니다. ({e_csv} / {e_wiki})"
            return default_tickers, error_msg

# --------------------------------------------------------------------------
# [Internal Function] RSI 계산
# --------------------------------------------------------------------------
def calculate_rsi(data, window=14):
    delta = data['Close'].diff()
    gain = (delta.where(delta > 0, 0)).rolling(window=window).mean()
    loss = (-delta.where(delta < 0, 0)).rolling(window=window).mean()
    rs = gain / loss
    return 100 - (100 / (1 + rs))

# --------------------------------------------------------------------------
# [UI Section]
# --------------------------------------------------------------------------
st.title("📈 미국 주식 분석기")

tab1, tab2 = st.tabs(["🔍 종목 상세 분석", "🚀 S&P 500 꿀주식 찾기"])

# ==========================================================================
# [TAB 1] 개별 종목
# ==========================================================================
with tab1:
    st.markdown("### 특정 종목의 차트와 지표를 확인합니다.")
    ticker_input = st.text_input("티커 입력 (예: AAPL, TSLA)", value="AAPL").upper()
    period = st.selectbox("조회 기간", ["1mo", "3mo", "6mo", "1y", "5y"], index=2)

    if st.button("분석 시작", key="btn_single"):
        try:
            with st.spinner('데이터 수신 중...'):
                stock = yf.Ticker(ticker_input)
                hist = stock.history(period=period)
                info = stock.info

            if hist.empty:
                st.error("데이터가 없습니다.")
            else:
                col1, col2, col3 = st.columns(3)
                current_price = hist['Close'].iloc[-1]
                hist['RSI'] = calculate_rsi(hist)
                curr_rsi = hist['RSI'].iloc[-1]

                col1.metric("현재 주가", f"${current_price:.2f}")
                col2.metric("PER", info.get('trailingPE', 'N/A'))
                col3.metric("RSI (14일)", f"{curr_rsi:.2f}")
                st.line_chart(hist['Close'])

        except Exception as e:
            st.error(f"에러 발생: {e}")

# ==========================================================================
# [TAB 2] S&P 500 전수 조사 (검증 기능 추가됨)
# ==========================================================================
with tab2:
    st.markdown("### 🏹 조건에 맞는 '저평가 우량주'를 발굴합니다.")
    
    # [Debug Option] 테스트용 단축 모드
    quick_mode = st.checkbox("빠른 테스트 모드 (상위 50개만 스캔)", value=False)
    
    col_p1, col_p2, col_p3 = st.columns(3)
    target_rsi = col_p1.number_input("RSI 기준 (이하)", value=70)
    target_per = col_p2.number_input("PER 기준 (이하)", value=40)
    target_roe = col_p3.number_input("ROE 기준 (이상 %)", value=10.0)

    if st.button("전수 조사 시작", key="btn_scan"):
        st.cache_data.clear()
        tickers, error_msg = get_sp500_tickers()
        
        if error_msg: st.warning(error_msg)
        
        # ------------------------------------------------------------------
        # 🕵️‍♂️ [검증 포인트] 엔지니어 확인용 로그 (Probe)
        # ------------------------------------------------------------------
        raw_count = len(tickers)
        st.write(f"---")
        st.write(f"**🛠️ [System Log] 데이터 무결성 점검**")
        st.write(f"- 원본 데이터 개수: **{raw_count}개** (500~505개면 정상)")
        
        if quick_mode:
            tickers = tickers[:50]
            st.warning(f"⚡ [Mode] 빠른 테스트 모드 ON: 상위 50개만 스캔합니다.")
        else:
            st.success(f"🐢 [Mode] 전체 모드 ON: **{len(tickers)}개** 전수 조사를 수행합니다.")

        # 눈으로 직접 확인하는 Raw Data 열람 기능
        with st.expander("📋 스캔 대상 리스트 전체 보기 (클릭)"):
            st.write(tickers)
        st.write(f"---")
        # ------------------------------------------------------------------

        results = []
        progress_text = "시장 스캔 중..."
        my_bar = st.progress(0, text=progress_text)
        status_msg = st.empty()
        
        total = len(tickers)
        
        for i, ticker in enumerate(tickers):
            if i % 5 == 0: 
                my_bar.progress((i / total), text=f"{progress_text} ({i}/{total})")
                status_msg.caption(f"현재 분석 중: **{ticker}** ({i+1}/{total})")

            try:
                stock = yf.Ticker(ticker)
                hist = stock.history(period="3mo")
                if hist.empty: continue

                current_price = hist['Close'].iloc[-1]
                hist['RSI'] = calculate_rsi(hist)
                current_rsi = hist['RSI'].iloc[-1]

                if current_rsi > target_rsi: continue

                info = stock.info
                per = info.get('trailingPE', 999)
                roe = info.get('returnOnEquity', 0)

                cond_per = (per < target_per) and (per > 0)
                cond_roe = (roe * 100) > target_roe

                if cond_per and cond_roe:
                    results.append({
                        "Ticker": ticker,
                        "Price": current_price,
                        "RSI": current_rsi,
                        "PER": per,
                        "ROE": roe * 100,
                        "Name": info.get('shortName', ticker)
                    })
            except:
                continue
        
        my_bar.empty()
        status_msg.empty()
        
        if results:
            st.success(f"🎉 {len(results)}개 종목 발견!")
            df = pd.DataFrame(results).sort_values(by="RSI")
            st.dataframe(df, hide_index=True)
        else:
            st.warning("조건에 맞는 종목이 없습니다.")
