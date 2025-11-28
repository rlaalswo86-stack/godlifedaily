import streamlit as st
import yfinance as yf
import pandas as pd

# --------------------------------------------------------------------------
# [Style] 지저분한 UI 요소 숨기기 (Pro Mode)
# --------------------------------------------------------------------------
hide_decoration_bar_style = '''
    <style>
        /* 우측 상단 'Fork' 버튼 등 헤더 장식 숨기기 */
        header {visibility: hidden;}
        /* 하단 'Made with Streamlit' 푸터 숨기기 */
        footer {visibility: hidden;}
        /* 뷰어 모드 버튼 숨기기 */
        .stDeployButton {display:none;}
    </style>
'''
st.markdown(hide_decoration_bar_style, unsafe_allow_html=True)

# ... 기존 st.set_page_config ...

# 페이지 설정
st.set_page_config(page_title="US Stock Analysis", page_icon="📈")

# --------------------------------------------------------------------------
# [Internal Function] S&P 500 리스트 가져오기 (Dual Source)
# --------------------------------------------------------------------------
@st.cache_data
def get_sp500_tickers():
    # 1. 위키피디아 시도 (Primary Source)
    try:
        url = 'https://en.wikipedia.org/wiki/List_of_S%26P_500_companies'
        headers = {'User-Agent': 'Mozilla/5.0'}
        tables = pd.read_html(url, storage_options=headers)
        df = tables[0]
        tickers = df['Symbol'].apply(lambda x: x.replace('.', '-')).tolist()
        return tickers, None
    except Exception as e_wiki:
        # 2. 실패 시 GitHub CSV 시도 (Secondary Source)
        try:
            print(f"위키피디아 접속 실패 ({e_wiki}), CSV 데이터로 전환합니다.")
            csv_url = "https://raw.githubusercontent.com/datasets/s-and-p-500-companies/master/data/constituents.csv"
            df = pd.read_csv(csv_url)
            tickers = df['Symbol'].apply(lambda x: x.replace('.', '-')).tolist()
            return tickers, None
        except Exception as e_csv:
            # 3. 전부 실패 시 비상용 리스트 (Fail-safe)
            default_tickers = ['AAPL', 'MSFT', 'GOOGL', 'NVDA', 'TSLA', 'AMZN', 'META', 'AMD', 'INTC', 'KO']
            error_msg = f"데이터 확보 실패. 비상용 리스트로 동작합니다. (에러: {e_wiki} / {e_csv})"
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
    st.caption("※ 시간이 오래 걸릴 수 있어 상위 50개만 테스트하려면 아래 체크박스를 켜세요.")
    
    # [Debug Option] 테스트용 단축 모드
    quick_mode = st.checkbox("빠른 테스트 모드 (상위 50개만 스캔)", value=False)
    
    col_p1, col_p2, col_p3 = st.columns(3)
    target_rsi = col_p1.number_input("RSI 기준 (이하)", value=70)
    target_per = col_p2.number_input("PER 기준 (이하)", value=40)
    target_roe = col_p3.number_input("ROE 기준 (이상 %)", value=10.0)

    if st.button("전수 조사 시작", key="btn_scan"):
        tickers, error_msg = get_sp500_tickers()
        
        if error_msg:
            st.error(error_msg)
        
        # 빠른 테스트 모드일 경우 종목 수 제한
        if quick_mode:
            tickers = tickers[:50]
            st.info(f"⚡ 빠른 모드: {len(tickers)}개 종목만 스캔합니다.")
        else:
            st.info(f"🐢 전체 모드: {len(tickers)}개 종목을 모두 스캔합니다. (잠시만 기다려주세요)")

        results = []
        progress_text = "시장 스캔 중..."
        my_bar = st.progress(0, text=progress_text)
        status_msg = st.empty()
        
        total = len(tickers)
        
        for i, ticker in enumerate(tickers):
            # 진행률 바 업데이트
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

                # 1차 필터 (RSI)
                if current_rsi > target_rsi: continue

                # 2차 필터 (재무)
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
            st.dataframe(
                df,
                column_config={
                    "Price": st.column_config.NumberColumn("주가($)", format="$%.2f"),
                    "RSI": st.column_config.NumberColumn("RSI", format="%.2f"),
                    "PER": st.column_config.NumberColumn("PER", format="%.2f"),
                    "ROE": st.column_config.NumberColumn("ROE(%)", format="%.2f%%"),
                },
                hide_index=True
            )
        else:
            st.warning("조건에 맞는 종목이 없습니다.")
