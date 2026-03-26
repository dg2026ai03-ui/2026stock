import streamlit as st
import yfinance as yf
import pandas as pd
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import numpy as np
from datetime import datetime

# ══════════════════════════════════════════════════════
#  PAGE CONFIG
# ══════════════════════════════════════════════════════
st.set_page_config(
    page_title="STOCKPULSE — 글로벌 주식 비교",
    page_icon="▸",
    layout="wide",
    initial_sidebar_state="expanded",
)

# ══════════════════════════════════════════════════════
#  GLOBAL CSS  — Bloomberg Terminal meets editorial print
# ══════════════════════════════════════════════════════
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Syne:wght@400;700;800&family=IBM+Plex+Mono:wght@300;400;500&family=Noto+Sans+KR:wght@300;400;700&display=swap');

/* ── Tokens ── */
:root {
  --ink:        #0b0c0e;
  --surface:    #111318;
  --panel:      #181c23;
  --raise:      #1e2330;
  --border:     #252b38;
  --amber:      #f5a623;
  --amber-dim:  #7a5112;
  --green:      #00d084;
  --red:        #ff4d4d;
  --blue:       #4d9eff;
  --muted:      #4a5568;
  --sub:        #718096;
  --text:       #dde1ea;
  --text-bright:#f0f2f7;
}

/* ── Base ── */
html, body, [class*="css"] {
  font-family: 'Noto Sans KR', 'IBM Plex Mono', sans-serif;
  background-color: var(--ink) !important;
  color: var(--text);
}
.stApp { background-color: var(--ink) !important; }

/* ── Sidebar ── */
section[data-testid="stSidebar"] {
  background: var(--surface) !important;
  border-right: 1px solid var(--border) !important;
}
section[data-testid="stSidebar"] > div { padding-top: 1.5rem; }
section[data-testid="stSidebar"] label { color: var(--sub) !important; font-size: 0.72rem !important; letter-spacing: 0.1em; text-transform: uppercase; }
section[data-testid="stSidebar"] .stSelectbox > div > div,
section[data-testid="stSidebar"] .stMultiSelect > div > div { background: var(--raise) !important; border-color: var(--border) !important; }

/* ── Header ── */
.sp-header {
  display: flex; align-items: baseline; gap: 1rem;
  border-bottom: 1px solid var(--border);
  padding-bottom: 1rem; margin-bottom: 1.8rem;
}
.sp-logo {
  font-family: 'Syne', sans-serif;
  font-size: 2rem; font-weight: 800;
  color: var(--amber);
  letter-spacing: -0.03em;
  line-height: 1;
}
.sp-logo span { color: var(--text-bright); }
.sp-tagline {
  font-family: 'IBM Plex Mono', monospace;
  font-size: 0.65rem; color: var(--muted);
  letter-spacing: 0.18em; text-transform: uppercase;
  border-left: 2px solid var(--amber-dim);
  padding-left: 0.7rem;
}
.sp-time {
  margin-left: auto;
  font-family: 'IBM Plex Mono', monospace;
  font-size: 0.68rem; color: var(--muted);
}

/* ── Ticker Cards ── */
.ticker-grid { display: flex; flex-wrap: wrap; gap: 0.6rem; margin-bottom: 1.5rem; }
.ticker-card {
  background: var(--panel);
  border: 1px solid var(--border);
  border-radius: 6px;
  padding: 0.7rem 1rem;
  min-width: 140px;
  flex: 1;
  position: relative;
  overflow: hidden;
  transition: border-color 0.2s, transform 0.15s;
}
.ticker-card::before {
  content: '';
  position: absolute; top: 0; left: 0; right: 0; height: 2px;
}
.ticker-card.kr::before { background: var(--blue); }
.ticker-card.us::before { background: var(--amber); }
.ticker-card:hover { border-color: var(--amber); transform: translateY(-1px); }
.tc-flag { font-size: 0.65rem; color: var(--muted); font-family: 'IBM Plex Mono',monospace; letter-spacing: 0.1em; margin-bottom: 0.2rem; }
.tc-name { font-size: 0.82rem; font-weight: 700; color: var(--text-bright); margin-bottom: 0.4rem; white-space: nowrap; overflow: hidden; text-overflow: ellipsis; }
.tc-price { font-family: 'IBM Plex Mono', monospace; font-size: 1.1rem; color: var(--text-bright); }
.tc-change { font-family: 'IBM Plex Mono', monospace; font-size: 0.75rem; margin-left: 0.4rem; }
.tc-up   { color: var(--green); }
.tc-down { color: var(--red); }
.tc-ret  { font-family: 'IBM Plex Mono', monospace; font-size: 0.7rem; margin-top: 0.25rem; color: var(--sub); }

/* ── Section heading ── */
.sp-section {
  font-family: 'IBM Plex Mono', monospace;
  font-size: 0.62rem; color: var(--amber);
  letter-spacing: 0.22em; text-transform: uppercase;
  margin: 1.6rem 0 0.7rem;
  display: flex; align-items: center; gap: 0.6rem;
}
.sp-section::after { content: ''; flex: 1; height: 1px; background: var(--border); }

/* ── Chart wrapper ── */
.chart-wrap {
  background: var(--panel);
  border: 1px solid var(--border);
  border-radius: 8px;
  padding: 0.4rem 0.4rem 0;
  margin-bottom: 1rem;
}

/* ── Tabs ── */
.stTabs [data-baseweb="tab-list"] { background: var(--surface); border-bottom: 1px solid var(--border); gap: 0; }
.stTabs [data-baseweb="tab"] {
  font-family: 'IBM Plex Mono', monospace; font-size: 0.7rem;
  letter-spacing: 0.12em; text-transform: uppercase; color: var(--muted);
  padding: 0.6rem 1.2rem; border-radius: 0;
}
.stTabs [aria-selected="true"] { color: var(--amber) !important; background: var(--panel) !important; }
.stTabs [data-baseweb="tab-highlight"] { background-color: var(--amber) !important; height: 2px; }
.stTabs [data-baseweb="tab-border"] { display: none; }

/* ── Multiselect tag ── */
.stMultiSelect [data-baseweb="tag"] { background-color: var(--amber-dim) !important; border-color: var(--amber) !important; color: var(--amber) !important; }

/* ── Data table ── */
.dataframe { font-family: 'IBM Plex Mono', monospace !important; font-size: 0.78rem !important; }
.dataframe thead tr th { background: var(--raise) !important; color: var(--amber) !important; border-color: var(--border) !important; font-size: 0.68rem !important; letter-spacing: 0.1em; }
.dataframe tbody tr td { border-color: var(--border) !important; background: var(--panel) !important; }
.dataframe tbody tr:hover td { background: var(--raise) !important; }

/* ── Sidebar logo ── */
.sb-logo {
  font-family: 'Syne', sans-serif; font-weight: 800;
  font-size: 1.1rem; color: var(--amber);
  letter-spacing: -0.02em; padding: 0 0 1.2rem 0;
  border-bottom: 1px solid var(--border); margin-bottom: 1rem;
}
.sb-logo span { color: var(--text-bright); }

/* ── Download button ── */
.stDownloadButton button {
  background: transparent !important;
  border: 1px solid var(--amber) !important;
  color: var(--amber) !important;
  font-family: 'IBM Plex Mono', monospace !important;
  font-size: 0.72rem !important; letter-spacing: 0.1em;
  border-radius: 4px !important;
}
.stDownloadButton button:hover { background: var(--amber-dim) !important; }

/* ── Hide Streamlit chrome ── */
#MainMenu, footer, header { visibility: hidden; }
.stDeployButton { display: none !important; }
div[data-testid="stToolbar"] { display: none; }
</style>
""", unsafe_allow_html=True)


# ══════════════════════════════════════════════════════
#  STOCK UNIVERSE
# ══════════════════════════════════════════════════════
KR_STOCKS = {
    "삼성전자":       "005930.KS",
    "SK하이닉스":     "000660.KS",
    "LG에너지솔루션": "373220.KS",
    "삼성바이오로직스":"207940.KS",
    "현대차":         "005380.KS",
    "기아":           "000270.KS",
    "POSCO홀딩스":    "005490.KS",
    "NAVER":          "035420.KS",
    "카카오":         "035720.KS",
    "셀트리온":       "068270.KS",
    "KB금융":         "105560.KS",
    "신한지주":       "055550.KS",
    "LG화학":         "051910.KS",
    "삼성SDI":        "006400.KS",
    "한국전력":       "015760.KS",
}

US_STOCKS = {
    "Apple":            "AAPL",
    "Microsoft":        "MSFT",
    "NVIDIA":           "NVDA",
    "Alphabet":         "GOOGL",
    "Amazon":           "AMZN",
    "Meta":             "META",
    "Tesla":            "TSLA",
    "Berkshire B":      "BRK-B",
    "JPMorgan":         "JPM",
    "Visa":             "V",
    "J&J":              "JNJ",
    "ExxonMobil":       "XOM",
    "UnitedHealth":     "UNH",
    "Walmart":          "WMT",
    "Netflix":          "NFLX",
}

PERIOD_OPTIONS = {
    "1개월":  "1mo",
    "3개월":  "3mo",
    "6개월":  "6mo",
    "1년":    "1y",
    "2년":    "2y",
    "5년":    "5y",
}

COLORS = [
    "#f5a623","#4d9eff","#00d084","#ff4d4d","#c77dff",
    "#ff9f43","#48dbfb","#1dd1a1","#ff6b81","#a29bfe",
    "#fd79a8","#55efc4","#fdcb6e","#74b9ff","#e17055",
]

# ══════════════════════════════════════════════════════
#  PLOTLY BASE THEME
# ══════════════════════════════════════════════════════
def base_layout(**kwargs):
    return dict(
        paper_bgcolor="rgba(0,0,0,0)",
        plot_bgcolor="rgba(0,0,0,0)",
        font=dict(family="IBM Plex Mono, monospace", color="#4a5568", size=10),
        xaxis=dict(gridcolor="#1e2330", linecolor="#252b38", tickfont_size=9, showgrid=True, zeroline=False),
        yaxis=dict(gridcolor="#1e2330", linecolor="#252b38", tickfont_size=9, showgrid=True, zeroline=False),
        legend=dict(bgcolor="rgba(24,28,35,0.9)", bordercolor="#252b38", borderwidth=1, font_size=9),
        margin=dict(l=8, r=8, t=36, b=8),
        hoverlabel=dict(bgcolor="#1e2330", bordercolor="#f5a623", font_color="#f0f2f7", font_size=11),
        **kwargs,
    )


# ══════════════════════════════════════════════════════
#  DATA HELPERS
# ══════════════════════════════════════════════════════
@st.cache_data(ttl=300, show_spinner=False)
def load_history(tickers: tuple, period: str) -> dict:
    out = {}
    for tk in tickers:
        try:
            hist = yf.Ticker(tk).history(period=period)
            if not hist.empty:
                out[tk] = hist
        except Exception:
            pass
    return out


def pct_return(hist):
    if hist is None or len(hist) < 2:
        return float("nan")
    return (hist["Close"].iloc[-1] / hist["Close"].iloc[0] - 1) * 100


def normalized(hist):
    s = hist["Close"]
    return (s / s.iloc[0] - 1) * 100


def last_price_chg(hist):
    if hist is None or len(hist) < 2:
        return None, None
    return hist["Close"].iloc[-1], (hist["Close"].iloc[-1] / hist["Close"].iloc[-2] - 1) * 100


def annualized_vol(hist):
    dr = hist["Close"].pct_change().dropna()
    return dr.std() * np.sqrt(252) * 100 if len(dr) > 1 else float("nan")


# ══════════════════════════════════════════════════════
#  SIDEBAR
# ══════════════════════════════════════════════════════
with st.sidebar:
    st.markdown('<div class="sb-logo">STOCK<span>PULSE</span></div>', unsafe_allow_html=True)

    period_label = st.selectbox("⏱ 분석 기간", list(PERIOD_OPTIONS.keys()), index=3)
    period = PERIOD_OPTIONS[period_label]

    st.markdown("---")
    st.markdown("**🇰🇷 한국 주식**")
    kr_names = st.multiselect(
        "종목 선택 (KRX)",
        list(KR_STOCKS.keys()),
        default=["삼성전자", "SK하이닉스", "NAVER", "현대차", "카카오"],
    )

    st.markdown("**🇺🇸 미국 주식**")
    us_names = st.multiselect(
        "종목 선택 (NYSE/NASDAQ)",
        list(US_STOCKS.keys()),
        default=["Apple", "NVIDIA", "Tesla", "Microsoft", "Meta"],
    )

    st.markdown("---")
    chart_mode = st.radio("📊 가격 차트", ["라인", "캔들스틱"], horizontal=True)
    show_volume = st.checkbox("거래량 표시", value=False)

    st.markdown(
        '<div style="font-family:IBM Plex Mono;font-size:0.6rem;color:#2d3748;margin-top:2rem;">'
        'DATA · Yahoo Finance<br>CACHE · 5 min<br>BUILD · Streamlit + Plotly</div>',
        unsafe_allow_html=True,
    )


# ══════════════════════════════════════════════════════
#  COLLECT & FETCH
# ══════════════════════════════════════════════════════
kr_tickers = [KR_STOCKS[n] for n in kr_names]
us_tickers = [US_STOCKS[n] for n in us_names]
all_tickers = kr_tickers + us_tickers
sym2name = {**{v: k for k, v in KR_STOCKS.items()}, **{v: k for k, v in US_STOCKS.items()}}

# ── Header ─────────────────────────────────────────────
now_str = datetime.now().strftime("%Y.%m.%d  %H:%M")
st.markdown(
    f'<div class="sp-header">'
    f'  <div class="sp-logo">STOCK<span>PULSE</span></div>'
    f'  <div class="sp-tagline">글로벌 주식 비교 애널리틱스</div>'
    f'  <div class="sp-time">🕐 {now_str} KST</div>'
    f'</div>',
    unsafe_allow_html=True,
)

if not all_tickers:
    st.info("👈 사이드바에서 종목을 선택하면 분석이 시작됩니다.")
    st.stop()

with st.spinner("시세 데이터 수신 중..."):
    data = load_history(tuple(all_tickers), period)

if not data:
    st.error("데이터를 가져오지 못했습니다. 잠시 후 다시 시도해 주세요.")
    st.stop()


# ══════════════════════════════════════════════════════
#  TICKER CARDS
# ══════════════════════════════════════════════════════
def render_cards(tickers, market_cls, currency):
    if not tickers:
        return
    cards_html = '<div class="ticker-grid">'
    for tk in tickers:
        if tk not in data:
            continue
        name   = sym2name.get(tk, tk)
        price, chg = last_price_chg(data[tk])
        ret = pct_return(data[tk])
        if price is None:
            continue
        flag  = "🇰🇷 KRX" if market_cls == "kr" else "🇺🇸 NYSE/NASDAQ"
        arrow = "▲" if chg >= 0 else "▼"
        cc    = "tc-up" if chg >= 0 else "tc-down"
        rc    = "tc-up" if ret >= 0 else "tc-down"
        ps    = f"₩{price:,.0f}" if currency == "KRW" else f"${price:,.2f}"
        rs    = f"+{ret:.1f}%" if ret >= 0 else f"{ret:.1f}%"
        cards_html += (
            f'<div class="ticker-card {market_cls}">'
            f'  <div class="tc-flag">{flag} · {tk}</div>'
            f'  <div class="tc-name">{name}</div>'
            f'  <div>'
            f'    <span class="tc-price">{ps}</span>'
            f'    <span class="tc-change {cc}">{arrow}{abs(chg):.2f}%</span>'
            f'  </div>'
            f'  <div class="tc-ret {rc}">{period_label} 누적수익 {rs}</div>'
            f'</div>'
        )
    cards_html += '</div>'
    st.markdown(cards_html, unsafe_allow_html=True)

st.markdown('<div class="sp-section">🇰🇷 한국 주요 종목</div>', unsafe_allow_html=True)
render_cards(kr_tickers, "kr", "KRW")

st.markdown('<div class="sp-section">🇺🇸 미국 주요 종목</div>', unsafe_allow_html=True)
render_cards(us_tickers, "us", "USD")


# ══════════════════════════════════════════════════════
#  TABS
# ══════════════════════════════════════════════════════
tab1, tab2, tab3, tab4 = st.tabs([
    "01 · 수익률 비교",
    "02 · 가격 차트",
    "03 · 상관관계",
    "04 · 요약 테이블",
])


# ─────────────────────────────────────────────────────
# TAB 1 — 수익률 비교
# ─────────────────────────────────────────────────────
with tab1:
    tickers_ok = [t for t in all_tickers if t in data]

    # Normalized line chart ───────────────────────────
    st.markdown('<div class="sp-section">정규화 수익률 추이</div>', unsafe_allow_html=True)

    fig_norm = go.Figure()
    for idx, tk in enumerate(tickers_ok):
        norm = normalized(data[tk])
        name = sym2name.get(tk, tk)
        flag = "🇰🇷" if tk in kr_tickers else "🇺🇸"
        dash = "solid" if tk in kr_tickers else "dot"
        col  = COLORS[idx % len(COLORS)]
        fig_norm.add_trace(go.Scatter(
            x=norm.index, y=norm.values,
            name=f"{flag} {name}",
            mode="lines",
            line=dict(color=col, width=1.8, dash=dash),
            hovertemplate=f"<b>{name}</b><br>%{{x|%Y-%m-%d}}<br>수익률 %{{y:+.2f}}%<extra></extra>",
        ))
    fig_norm.add_hline(y=0, line_color="#252b38", line_width=1)
    fig_norm.update_layout(**base_layout(height=400, title_text=f"누적 수익률 비교 ({period_label})", title_font_size=11, title_font_color="#718096"), yaxis_ticksuffix="%", hovermode="x unified")

    st.markdown('<div class="chart-wrap">', unsafe_allow_html=True)
    st.plotly_chart(fig_norm, use_container_width=True)
    st.markdown("</div>", unsafe_allow_html=True)

    # Bar chart — ranked returns ─────────────────────
    st.markdown('<div class="sp-section">기간 수익률 순위</div>', unsafe_allow_html=True)

    bar_rows = []
    for tk in tickers_ok:
        ret  = pct_return(data[tk])
        name = sym2name.get(tk, tk)
        mkt  = "KR" if tk in kr_tickers else "US"
        bar_rows.append({"name": name, "ret": ret, "mkt": mkt, "tk": tk})
    df_bar = pd.DataFrame(bar_rows).dropna().sort_values("ret", ascending=True)

    bar_colors = []
    for _, row in df_bar.iterrows():
        if row["ret"] >= 0:
            bar_colors.append("#00d084" if row["mkt"] == "KR" else "#f5a623")
        else:
            bar_colors.append("#ff4d4d")

    text_vals = [f"+{r:.1f}%" if r >= 0 else f"{r:.1f}%" for r in df_bar["ret"]]

    fig_bar = go.Figure(go.Bar(
        x=df_bar["ret"], y=df_bar["name"],
        orientation="h",
        marker_color=bar_colors,
        text=text_vals,
        textposition="outside",
        textfont=dict(size=9, family="IBM Plex Mono"),
        hovertemplate="<b>%{y}</b><br>수익률: %{x:.2f}%<extra></extra>",
    ))
    fig_bar.update_layout(
        **base_layout(height=max(300, len(df_bar) * 34), title_text="기간 수익률", title_font_size=11, title_font_color="#718096"),
        xaxis_ticksuffix="%", bargap=0.35,
    )
    st.markdown('<div class="chart-wrap">', unsafe_allow_html=True)
    st.plotly_chart(fig_bar, use_container_width=True)
    st.markdown("</div>", unsafe_allow_html=True)

    # KR vs US average comparison ────────────────────
    if kr_tickers and us_tickers:
        st.markdown('<div class="sp-section">한국 vs 미국 평균 수익률</div>', unsafe_allow_html=True)
        kr_avg = np.nanmean([pct_return(data[t]) for t in kr_tickers if t in data])
        us_avg = np.nanmean([pct_return(data[t]) for t in us_tickers if t in data])
        fig_avg = go.Figure()
        for label, val, col in [("🇰🇷 한국 평균", kr_avg, "#4d9eff"), ("🇺🇸 미국 평균", us_avg, "#f5a623")]:
            fig_avg.add_trace(go.Indicator(
                mode="number+delta",
                value=val,
                number=dict(suffix="%", font=dict(size=36, color=col, family="IBM Plex Mono")),
                title=dict(text=label, font=dict(size=11, color="#718096")),
                delta=dict(reference=0, valueformat=".2f", suffix="%"),
                domain=dict(x=[0, 0.5] if label.startswith("🇰🇷") else [0.5, 1], y=[0, 1]),
            ))
        fig_avg.update_layout(**base_layout(height=160))
        st.markdown('<div class="chart-wrap">', unsafe_allow_html=True)
        st.plotly_chart(fig_avg, use_container_width=True)
        st.markdown("</div>", unsafe_allow_html=True)


# ─────────────────────────────────────────────────────
# TAB 2 — 가격 차트 (2-column grid, with optional volume)
# ─────────────────────────────────────────────────────
with tab2:
    st.markdown(f'<div class="sp-section">{chart_mode} 차트</div>', unsafe_allow_html=True)

    tickers_chart = [t for t in all_tickers if t in data]
    if not tickers_chart:
        st.info("선택된 종목 데이터가 없습니다.")
    else:
        for row_start in range(0, len(tickers_chart), 2):
            cols = st.columns(2)
            for ci, tk in enumerate(tickers_chart[row_start:row_start + 2]):
                hist  = data[tk]
                name  = sym2name.get(tk, tk)
                flag  = "🇰🇷" if tk in kr_tickers else "🇺🇸"
                ret   = pct_return(hist)
                ret_s = f"+{ret:.1f}%" if ret >= 0 else f"{ret:.1f}%"
                col   = "#4d9eff" if tk in kr_tickers else "#f5a623"
                rc    = "#00d084" if ret >= 0 else "#ff4d4d"

                rows_subplot = 2 if show_volume else 1
                row_heights  = [0.72, 0.28] if show_volume else [1]

                fig_p = make_subplots(
                    rows=rows_subplot, cols=1,
                    shared_xaxes=True,
                    row_heights=row_heights,
                    vertical_spacing=0.03,
                )

                if chart_mode == "캔들스틱":
                    fig_p.add_trace(go.Candlestick(
                        x=hist.index,
                        open=hist["Open"], high=hist["High"],
                        low=hist["Low"], close=hist["Close"],
                        increasing=dict(line_color="#00d084", fillcolor="rgba(0,208,132,0.25)"),
                        decreasing=dict(line_color="#ff4d4d", fillcolor="rgba(255,77,77,0.25)"),
                        name=name, showlegend=False,
                    ), row=1, col=1)
                else:
                    fig_p.add_trace(go.Scatter(
                        x=hist.index, y=hist["Close"],
                        mode="lines",
                        line=dict(color=col, width=2),
                        fill="tozeroy",
                        fillcolor=f"rgba({int(col[1:3],16)},{int(col[3:5],16)},{int(col[5:7],16)},0.07)",
                        name=name, showlegend=False,
                        hovertemplate="%{x|%Y-%m-%d}<br>종가 %{y:,.2f}<extra></extra>",
                    ), row=1, col=1)

                if show_volume and "Volume" in hist.columns:
                    vol_colors = ["#00d084" if c >= o else "#ff4d4d"
                                  for c, o in zip(hist["Close"], hist["Open"])]
                    fig_p.add_trace(go.Bar(
                        x=hist.index, y=hist["Volume"],
                        marker_color=vol_colors,
                        opacity=0.5,
                        name="거래량", showlegend=False,
                        hovertemplate="%{x|%Y-%m-%d}<br>거래량 %{y:,.0f}<extra></extra>",
                    ), row=2, col=1)

                title_html = f"{flag} {name}  <span style='color:{rc};font-size:0.85em;'>{ret_s}</span>"
                fig_p.update_layout(
                    **base_layout(height=280 if not show_volume else 340),
                    title_text=title_html, title_font_size=11, title_font_color="#9ca3af",
                    xaxis_rangeslider_visible=False,
                )
                with cols[ci]:
                    st.markdown('<div class="chart-wrap">', unsafe_allow_html=True)
                    st.plotly_chart(fig_p, use_container_width=True)
                    st.markdown("</div>", unsafe_allow_html=True)


# ─────────────────────────────────────────────────────
# TAB 3 — 상관관계
# ─────────────────────────────────────────────────────
with tab3:
    tickers_corr = [t for t in all_tickers if t in data and len(data[t]) > 5]
    if len(tickers_corr) < 2:
        st.info("상관관계 분석을 위해 2개 이상의 종목을 선택해 주세요.")
    else:
        st.markdown('<div class="sp-section">일간 수익률 상관관계 히트맵</div>', unsafe_allow_html=True)

        ret_df = pd.DataFrame({
            sym2name.get(t, t): data[t]["Close"].pct_change().dropna()
            for t in tickers_corr
        })
        corr = ret_df.corr()

        # Custom diverging colorscale — dark navy midpoint
        cs = [
            [0.0, "#ff4d4d"],
            [0.25, "#7a2020"],
            [0.5, "#1e2330"],
            [0.75, "#1a4a2e"],
            [1.0, "#00d084"],
        ]
        fig_heat = go.Figure(go.Heatmap(
            z=corr.values,
            x=corr.columns.tolist(),
            y=corr.index.tolist(),
            colorscale=cs, zmin=-1, zmax=1,
            text=corr.round(2).values,
            texttemplate="%{text:.2f}",
            textfont=dict(size=9, family="IBM Plex Mono"),
            hovertemplate="%{y} × %{x}<br>상관계수: %{z:.3f}<extra></extra>",
            colorbar=dict(
                tickfont=dict(size=9, family="IBM Plex Mono"),
                tickcolor="#4a5568",
                outlinecolor="#252b38",
            ),
        ))
        fig_heat.update_layout(
            **base_layout(height=520),
            title_text=f"일간 수익률 상관관계 ({period_label})",
            title_font_size=11, title_font_color="#718096",
            xaxis_tickangle=-30,
        )
        st.markdown('<div class="chart-wrap">', unsafe_allow_html=True)
        st.plotly_chart(fig_heat, use_container_width=True)
        st.markdown("</div>", unsafe_allow_html=True)

        # Scatter — most correlated pair ──────────────
        upper = corr.where(np.triu(np.ones(corr.shape), k=1).astype(bool)).stack()
        if not upper.empty:
            st.markdown('<div class="sp-section">최고 상관 종목 산점도</div>', unsafe_allow_html=True)
            top_pair = upper.abs().idxmax()
            a, b     = top_pair
            rx = ret_df[a] * 100
            ry = ret_df[b] * 100

            fig_sc = go.Figure()
            fig_sc.add_trace(go.Scatter(
                x=rx, y=ry, mode="markers",
                marker=dict(
                    color=rx.values,
                    colorscale=[[0,"#ff4d4d"],[0.5,"#f5a623"],[1,"#00d084"]],
                    size=4, opacity=0.75,
                    colorbar=dict(title="", tickfont_size=8),
                ),
                hovertemplate=f"{a}: %{{x:.2f}}%<br>{b}: %{{y:.2f}}%<extra></extra>",
            ))
            # Trend line
            z = np.polyfit(rx.dropna(), ry[rx.dropna().index], 1)
            x_line = np.linspace(rx.min(), rx.max(), 100)
            fig_sc.add_trace(go.Scatter(
                x=x_line, y=np.polyval(z, x_line),
                mode="lines", line=dict(color="#f5a623", width=1.2, dash="dash"),
                name="추세선", showlegend=False,
            ))
            fig_sc.update_layout(
                **base_layout(height=380),
                title_text=f'"{a}" vs "{b}"  — 상관계수 {corr.loc[a,b]:.3f}',
                title_font_size=11, title_font_color="#718096",
                xaxis_title=a, yaxis_title=b,
                xaxis_ticksuffix="%", yaxis_ticksuffix="%",
            )
            st.markdown('<div class="chart-wrap">', unsafe_allow_html=True)
            st.plotly_chart(fig_sc, use_container_width=True)
            st.markdown("</div>", unsafe_allow_html=True)


# ─────────────────────────────────────────────────────
# TAB 4 — 요약 테이블
# ─────────────────────────────────────────────────────
with tab4:
    st.markdown('<div class="sp-section">종목별 지표 요약</div>', unsafe_allow_html=True)

    rows = []
    for tk in all_tickers:
        if tk not in data:
            continue
        hist = data[tk]
        name = sym2name.get(tk, tk)
        mkt  = "🇰🇷 KRX" if tk in kr_tickers else "🇺🇸 NYSE/NASDAQ"
        cur  = "KRW" if tk in kr_tickers else "USD"
        sym  = "₩" if cur == "KRW" else "$"
        fmt  = ",.0f" if cur == "KRW" else ",.2f"

        price, chg = last_price_chg(hist)
        ret  = pct_return(hist)
        vol  = annualized_vol(hist)
        high = hist["High"].max()
        low  = hist["Low"].min()
        dd   = (hist["Close"].min() / hist["Close"].cummax().shift(1).max() - 1) * 100

        rows.append({
            "시장":        mkt,
            "종목명":      name,
            "티커":        tk,
            "현재가":      f"{sym}{price:{fmt}}" if price else "N/A",
            "전일비(%)":   f"{'▲' if chg>=0 else '▼'}{abs(chg):.2f}%" if chg else "N/A",
            f"{period_label} 수익률": f"{'+'if ret>=0 else ''}{ret:.2f}%" if not np.isnan(ret) else "N/A",
            "연환산 변동성": f"{vol:.1f}%" if not np.isnan(vol) else "N/A",
            "기간 최고가":  f"{sym}{high:{fmt}}",
            "기간 최저가":  f"{sym}{low:{fmt}}",
        })

    if rows:
        df_sum = pd.DataFrame(rows)

        def _color(val):
            s = str(val)
            if "%" not in s:
                return ""
            try:
                raw = s.replace("+","").replace("▲","").replace("▼","").replace("%","")
                num = float(raw)
                if "▼" in s:
                    num = -abs(num)
                return "color: #00d084; font-weight:500" if num > 0 else ("color: #ff4d4d; font-weight:500" if num < 0 else "")
            except:
                return ""

        styled = df_sum.style.applymap(_color, subset=[f"{period_label} 수익률", "전일비(%)"])
        st.dataframe(styled, use_container_width=True, hide_index=True)

        csv = df_sum.to_csv(index=False).encode("utf-8-sig")
        st.download_button(
            "⬇  CSV 내보내기",
            data=csv,
            file_name=f"stockpulse_{datetime.today().strftime('%Y%m%d')}.csv",
            mime="text/csv",
        )

        # Rolling volatility sparklines ────────────────
        st.markdown('<div class="sp-section">30일 롤링 변동성 추이</div>', unsafe_allow_html=True)
        fig_rv = go.Figure()
        for idx, tk in enumerate([t for t in all_tickers if t in data]):
            hist = data[tk]
            dr   = hist["Close"].pct_change()
            rv30 = dr.rolling(30).std() * np.sqrt(252) * 100
            name = sym2name.get(tk, tk)
            flag = "🇰🇷" if tk in kr_tickers else "🇺🇸"
            fig_rv.add_trace(go.Scatter(
                x=rv30.index, y=rv30.values,
                name=f"{flag} {name}",
                mode="lines",
                line=dict(color=COLORS[idx % len(COLORS)], width=1.5),
                hovertemplate=f"<b>{name}</b><br>%{{x|%Y-%m-%d}}<br>변동성 %{{y:.1f}}%<extra></extra>",
            ))
        fig_rv.update_layout(
            **base_layout(height=320, title_text="30일 롤링 연환산 변동성", title_font_size=11, title_font_color="#718096"),
            yaxis_ticksuffix="%", hovermode="x unified",
        )
        st.markdown('<div class="chart-wrap">', unsafe_allow_html=True)
        st.plotly_chart(fig_rv, use_container_width=True)
        st.markdown("</div>", unsafe_allow_html=True)
