# Streamlit이 설치되어 있지 않은 경우 설치
try:
    import streamlit
except ImportError:
    !pip install streamlit

import streamlit as st
import yfinance as yf
import pandas as pd

# 페이지 설정
st.set_page_config(page_title="US Stock Analysis", page_icon="📈")

# --------------------------------------------------------------------------
# [Internal Function] S&P 500 리스트 가져오기 (캐싱 사용으로 속도 향상)
# --------------------------------------------------------------------------
@st.cache_data
def get_sp500_tickers():
    url = 'https://en.wikipedia.org/wiki/List_of_S%26P_500_companies'
    try:
        tables = pd.read_html(url)
        df = tables[0]
        tickers = df['Symbol'].apply(lambda x: x.replace('.', '-')).tolist()
        return tickers, None # Return tickers and no error
    except Exception as e:
        default_tickers = ['AAPL', 'MSFT', 'GOOGL', 'NVDA', 'TSLA'] # 비상용
        error_msg = f"S&P 500 리스트를 가져오는 데 실패했습니다: {e}. 기본 종목으로 진행합니다."
        return default_tickers, error_msg # Return default tickers and error message

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
# [UI Section] 탭 구분 (개별 검색 vs 전수 조사)
# --------------------------------------------------------------------------
st.title("📈 미국 주식 분석기")

tab1, tab2 = st.tabs(["🔍 종목 상세 분석", "🚀 S&P 500 꿀주식 찾기"])

# ==========================================================================
# [TAB 1] 기존 기능: 개별 종목 상세 조회
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
                # 메트릭 표시
                col1, col2, col3 = st.columns(3)
                current_price = hist['Close'].iloc[-1]
                prev_price = hist['Close'].iloc[-2]
                delta = current_price - prev_price

                # RSI 계산
                hist['RSI'] = calculate_rsi(hist)
                curr_rsi = hist['RSI'].iloc[-1]

                col1.metric("현재 주가", f"${current_price:.2f}", f"{delta:.2f}")
                col2.metric("PER", info.get('trailingPE', 'N/A'))
                col3.metric("RSI (14일)", f"{curr_rsi:.2f}")

                # 차트
                st.line_chart(hist['Close'])

                # 재무 정보 일부
                with st.expander("기업 개요 및 재무 정보"):
                    st.write(f"**산업:** {info.get('industry', 'N/A')}")
                    st.write(f"**설명:** {info.get('longBusinessSummary', 'N/A')[:200]}...")

        except Exception as e:
            st.error(f"에러 발생: {e}")

# ==========================================================================
# [TAB 2] 신규 기능: S&P 500 전수 조사 (스캐너)
# ==========================================================================
with tab2:
    st.markdown("### 🏹 조건에 맞는 '저평가 우량주'를 발굴합니다.")
    st.info("S&P 500 전 종목을 스캔하므로 시간이 조금 걸립니다. (약 3~5분)")

    # 사용자 입력 파라미터 (Threshold 설정) - 기본값을 완화하여 결과를 더 잘 찾도록 수정
    col_p1, col_p2, col_p3 = st.columns(3)
    target_rsi = col_p1.number_input("RSI 기준 (이하)", value=70) # 35 -> 70으로 완화
    target_per = col_p2.number_input("PER 기준 (이하)", value=40) # 30 -> 40으로 완화
    target_roe = col_p3.number_input("ROE 기준 (이상 %)", value=10.0) # 15.0 -> 10.0으로 완화

    if st.button("전수 조사 시작 (Start Scan)", key="btn_scan"):
        tickers, error_fetching_tickers = get_sp500_tickers()
        if error_fetching_tickers:
            st.warning(error_fetching_tickers) # Display the warning on the UI

        results = []

        # 프로그레스 바 설정
        progress_text = "미국 주식 시장을 스캔하는 중입니다..."
        my_bar = st.progress(0, text=progress_text)
        status_message = st.empty() # 실시간 상태 메시지를 위한 placeholder

        # 스캔 시작
        total = len(tickers)
        for i, ticker in enumerate(tickers):
            # 진행률 업데이트 (너무 자주는 아니고 10개마다)
            if i % 10 == 0:
                my_bar.progress((i / total), text=f"{progress_text} ({i}/{total}) - {ticker}")

            try:
                stock = yf.Ticker(ticker)
                hist = stock.history(period="3mo")

                if hist.empty:
                    print(f"[SKIP] {ticker}: 데이터 없음")
                    status_message.text(f"스캔 중... {ticker}: 데이터 없음")
                    continue

                # 지표 계산
                current_price = hist['Close'].iloc[-1]
                hist['RSI'] = calculate_rsi(hist)
                current_rsi = hist['RSI'].iloc[-1]

                # 1차 필터 (RSI가 기준보다 높으면 바로 Skip -> 속도 향상)
                if current_rsi > target_rsi:
                    print(f"[SKIP] {ticker}: RSI({current_rsi:.1f}) > {target_rsi} (기준 미달)")
                    status_message.text(f"스캔 중... {ticker}: RSI 기준 미달")
                    continue

                # 2차 필터 (재무제표 호출 - 느림)
                # RSI 통과한 녀석만 info를 부릅니다 (Lazy Loading)
                info = stock.info
                per = info.get('trailingPE', 999)
                roe = info.get('returnOnEquity', 0)

                # 최종 조건 검사
                cond_per = (per < target_per) and (per > 0)
                cond_roe = (roe * 100) > target_roe

                if cond_per and cond_roe:
                    results.append({
                        "Ticker": ticker,
                        "Price": round(current_price, 2),
                        "RSI": round(current_rsi, 2),
                        "PER": round(per, 2),
                        "ROE(%)": round(roe * 100, 2),
                        "Company": info.get('shortName', ticker)
                    })
                    print(f"[PASS] {ticker}: 조건 만족! (RSI:{current_rsi:.1f}, PER:{per:.1f}, ROE:{roe*100:.1f}%) -- 총 {len(results)}개")
                    status_message.text(f"스캔 중... {ticker}: 조건 만족!")
                else:
                    print(f"[FAIL] {ticker}: 조건 미달 (PER:{per:.1f} > {target_per} or ROE:{roe*100:.1f}% < {target_roe}%)")
                    status_message.text(f"스캔 중... {ticker}: PER/ROE 기준 미달")

            except Exception as e:
                print(f"[ERROR] {ticker}: 데이터 처리 중 오류 발생 - {e}")
                status_message.text(f"스캔 중... {ticker}: 오류 발생")
                continue

        my_bar.empty() # 프로그레스 바 제거
        status_message.empty() # 상태 메시지 제거

        # 결과 출력
        if results:
            st.success(f"🎉 총 {len(results)}개의 보물을 발견했습니다!")
            df_res = pd.DataFrame(results)
            # 보기 좋게 정렬 (RSI 낮은 순)
            df_res = df_res.sort_values(by="RSI", ascending=True)

            # 인터랙티브 테이블 표시
            st.dataframe(
                df_res,
                column_config={
                    "RSI": st.column_config.NumberColumn("RSI (과매도)", format="%.2f"),
                    "ROE(%)": st.column_config.NumberColumn("ROE (수익성)", format="%.2f%%"),
                },
                hide_index=True
            )
        else:
            st.warning("조건에 맞는 종목이 없습니다. 기준을 조금 완화해 보세요.")
