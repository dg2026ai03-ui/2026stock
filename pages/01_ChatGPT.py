# streamlit_app.py
import streamlit as st
import yfinance as yf
import pandas as pd
import matplotlib.pyplot as plt

st.set_page_config(page_title="주식 비교 분석 앱", layout="wide")

st.title("📈 한국 vs 미국 주식 비교 분석")

# 기본 종목 리스트
korea_stocks = {
    "삼성전자": "005930.KS",
    "SK하이닉스": "000660.KS",
    "네이버": "035420.KS",
    "카카오": "035720.KS"
}

us_stocks = {
    "애플": "AAPL",
    "마이크로소프트": "MSFT",
    "엔비디아": "NVDA",
    "테슬라": "TSLA"
}

# 사용자 선택
st.sidebar.header("📊 종목 선택")
selected_korea = st.sidebar.multiselect("한국 주식 선택", list(korea_stocks.keys()))
selected_us = st.sidebar.multiselect("미국 주식 선택", list(us_stocks.keys()))

period = st.sidebar.selectbox("기간 선택", ["1mo", "3mo", "6mo", "1y", "3y", "5y"])

# 티커 변환
selected_tickers = []
for k in selected_korea:
    selected_tickers.append(korea_stocks[k])
for u in selected_us:
    selected_tickers.append(us_stocks[u])

if len(selected_tickers) == 0:
    st.warning("종목을 하나 이상 선택하세요!")
    st.stop()

# 데이터 다운로드
@st.cache_data
def load_data(tickers, period):
    data = yf.download(tickers, period=period)["Adj Close"]
    return data

data = load_data(selected_tickers, period)

# 수익률 계산
returns = (data / data.iloc[0] - 1) * 100

# 차트
st.subheader("📊 주가 비교 차트")
fig, ax = plt.subplots()
returns.plot(ax=ax)
ax.set_ylabel("수익률 (%)")
ax.set_xlabel("날짜")
ax.legend(loc="upper left")
st.pyplot(fig)

# 테이블
st.subheader("📋 수익률 요약")
summary = returns.iloc[-1].sort_values(ascending=False)
st.dataframe(summary.rename("수익률 (%)"))

# 개별 종목 상세 보기
st.subheader("🔍 개별 종목 상세")
selected_detail = st.selectbox("종목 선택", selected_tickers)

stock = yf.Ticker(selected_detail)
info = stock.info

st.write(f"### {selected_detail} 정보")
st.write(f"- 현재가: {info.get('currentPrice', 'N/A')}")
st.write(f"- 시가총액: {info.get('marketCap', 'N/A')}")
st.write(f"- PER: {info.get('trailingPE', 'N/A')}")

hist = stock.history(period=period)

fig2, ax2 = plt.subplots()
hist['Close'].plot(ax=ax2)
ax2.set_title(f"{selected_detail} 가격 차트")
st.pyplot(fig2)

st.success("✅ 데이터는 Yahoo Finance 기반입니다.")

# requirements.txt
# 아래 내용을 requirements.txt 파일로 저장하세요
requirements_txt = """
streamlit
yfinance
pandas
matplotlib
"""

st.download_button("📥 requirements.txt 다운로드", requirements_txt, file_name="requirements.txt")
