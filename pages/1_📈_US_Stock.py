import streamlit as st
import yfinance as yf
import pandas as pd

# 페이지 설정
st.set_page_config(page_title="US Stock Analysis", page_icon="📈")

# --------------------------------------------------------------------------
# [Internal Function] S&P 500 리스트 가져오기 (Dual Source)
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
# [TAB 1] 개별 종목 상세 조회
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
                prev_price = hist['Close'].iloc[-2]
                delta = current_price - prev_price
                
                hist['RSI'] = calculate_rsi(hist)
                curr_rsi = hist['RSI'].iloc[-1]

                col1.metric("현재 주가", f"${current_price:.2f}", f"{delta:.2f}")
                col2.metric("PER", info.get('trailingPE', 'N/A'))
                col3.metric("RSI (14일)", f"{curr_rsi:.2f}")

                st.line_chart(hist['Close'])
                
                with st.expander("기업 개요"):
                    st.write(info.get('longBusinessSummary', '정보 없음')[:200] + "...")

        except Exception as e:
            st.error(f"에러 발생: {e}")

# ==========================================================================
# [TAB 2] S&P 500 전수 조사
# ==========================================================================
with tab2:
    st.markdown("### 🏹 조건에 맞는 '저평가 우량주'를 발굴합니다.")
    
    # [Option] 테스트용 단축 모드 (이건 유용하니 남겨둡니다)
    quick_mode = st.checkbox("빠른 테스트 모드 (상위 50개만 스캔)", value=False)
    
    col_p1, col_p2, col_p3 = st.columns(3)
    target_rsi = col_p1.number_input("RSI 기준 (이하)", value=35)
    target_per = col_p2.number_input("PER 기준 (이하)", value=30)
    target_roe = col_p3.number_input("ROE 기준 (이상 %)", value=15.0)

    if st.button("전수 조사 시작", key="btn_scan"):
        st.cache_data.clear()
        tickers, error_msg = get_sp500_tickers()
        
        if error_msg: st.warning(error_msg)
        
        # 모드 알림
        if quick_mode:
            tickers = tickers[:50]
            st.info(f"⚡ 빠른 모드: 상위 50개 종목을 스캔합니다.")
        else:
            st.info(f"🐢 전체 모드: S&P 500 전 종목({len(tickers)}개)을 스캔합니다. (약 3~5분 소요)")

        results = []
        progress_text = "시장 스캔 중..."
        my_bar = st.progress(0, text=progress_text)
        status_msg = st.empty()
        
        total = len(tickers)
        
        for i, ticker in enumerate(tickers):
            # 진행률 바 업데이트 (5개마다)
            if i % 5 == 0: 
                my_bar.progress((i / total), text=f"{progress_text} ({i}/{total})")
                status_msg.caption(f"현재 분석 중: **{ticker}**")

            try:
                stock = yf.Ticker(ticker)
                hist = stock.history(period="3mo")
                if hist.empty: continue

                # 지표 계산
                current_price = hist['Close'].iloc[-1]
                hist['RSI'] = calculate_rsi(hist)
                current_rsi = hist['RSI'].iloc[-1]

                # 1차 필터
                if current_rsi > target_rsi: continue

                # 2차 필터
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
        
        # 완료 처리
        my_bar.empty()
        status_msg.empty()
        
        if results:
            st.success(f"🎉 총 {len(results)}개의 유망 종목을 발굴했습니다!")
            df = pd.DataFrame(results).sort_values(by="RSI")
            
            # 깔끔한 결과 테이블
            st.dataframe(
                df,
                column_config={
                    "Ticker": "티커",
                    "Name": "기업명",
                    "Price": st.column_config.NumberColumn("주가($)", format="$%.2f"),
                    "RSI": st.column_config.NumberColumn("RSI", format="%.2f"),
                    "PER": st.column_config.NumberColumn("PER", format="%.2f"),
                    "ROE": st.column_config.NumberColumn("ROE(%)", format="%.2f%%"),
                },
                hide_index=True,
                use_container_width=True
            )
        else:
            st.warning("조건에 맞는 종목이 없습니다. 기준을 조금 완화해 보세요.")
