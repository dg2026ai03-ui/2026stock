import streamlit as st
import yfinance as yf
import pandas as pd
import plotly.express as px
from datetime import datetime, timedelta

# 페이지 설정
st.set_page_config(page_title="한-미 주식 비교 대시보드", layout="wide")

st.title("📈 한-미 주요 주식 수익률 비교")
st.markdown("한국과 미국 주요 종목의 수익률을 한눈에 비교해보세요.")

# 사이드바: 종목 선택 및 기간 설정
st.sidebar.header("설정")

# 주요 종목 리스트 (딕셔너리 형태: 이름 -> 티커)
stock_dict = {
    "삼성전자": "005930.KS",
    "SK하이닉스": "000660.KS",
    "NAVER": "035420.KS",
    "애플(Apple)": "AAPL",
    "테슬라(Tesla)": "TSLA",
    "엔비디아(NVIDIA)": "NVDA",
    "마이크로소프트(MSFT)": "MSFT",
    "S&P 500 ETF(SPY)": "SPY",
    "나스닥 100 ETF(QQQ)": "QQQ"
}

selected_stocks = st.sidebar.multiselect(
    "비교할 종목을 선택하세요", 
    options=list(stock_dict.keys()),
    default=["삼성전자", "애플(Apple)", "엔비디아(NVIDIA)"]
)

# 날짜 선택
start_date = st.sidebar.date_input("시작 날짜", datetime.now() - timedelta(days=365))
end_date = st.sidebar.date_input("종료 날짜", datetime.now())

if selected_stocks:
    # 데이터 불러오기
    tickers = [stock_dict[name] for name in selected_stocks]
    data = yf.download(tickers, start=start_date, end=end_date)['Close']
    
    # 데이터가 1개일 경우 Series로 반환되므로 DataFrame으로 변환
    if len(selected_stocks) == 1:
        data = data.to_frame()
        data.columns = selected_stocks
    else:
        # 컬럼명을 티커에서 한글 이름으로 변경
        inv_dict = {v: k for k, v in stock_dict.items()}
        data.columns = [inv_dict[t] for t in data.columns]

    # 수익률 계산 (시작점 100으로 정규화)
    # 수식: (현재가 / 시작가) * 100
    norm_data = (data / data.iloc[0]) * 100

    # 레이아웃 구성
    col1, col2 = st.columns([3, 1])

    with col1:
        st.subheader("수익률 비교 차트 (시작일 = 100)")
        fig = px.line(norm_data, labels={"value": "수익률 (Index)", "Date": "날짜"})
        st.plotly_chart(fig, use_container_width=True)

    with col2:
        st.subheader("최종 수익률 (%)")
        last_return = ((data.iloc[-1] / data.iloc[0]) - 1) * 100
        st.dataframe(last_return.sort_values(ascending=False).rename("수익률(%)"))

    # 상세 데이터 표
    with st.expander("상세 종가 데이터 보기"):
        st.write(data)
else:
    st.warning("비교할 종목을 하나 이상 선택해주세요.")
