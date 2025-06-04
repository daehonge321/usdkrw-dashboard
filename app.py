import streamlit as st
import requests
import pandas as pd
from datetime import datetime, timedelta
import altair as alt

# 🔑 API 키
FRED_KEY = "53718f3eaba1c258d6c6ae8836cf6911"

# 📈 FRED 시계열 데이터 가져오기
@st.cache_data(ttl=3600)
def fred_timeseries(series_id, years):
    end_date = datetime.today()
    start_date = end_date - timedelta(days=365 * years)
    url = (
        f"https://api.stlouisfed.org/fred/series/observations?"
        f"series_id={series_id}&api_key={FRED_KEY}&file_type=json"
        f"&observation_start={start_date.strftime('%Y-%m-%d')}"
        f"&observation_end={end_date.strftime('%Y-%m-%d')}"
    )
    data = requests.get(url).json()["observations"]
    df = pd.DataFrame(data)
    df["date"] = pd.to_datetime(df["date"])
    df["value"] = pd.to_numeric(df["value"], errors="coerce")
    return df

# 📊 Altair 차트 생성 함수
def plot_chart(df, title, y_min=None):
    chart = (
        alt.Chart(df)
        .mark_line()
        .encode(
            x="date:T",
            y=alt.Y("value:Q", scale=alt.Scale(domainMin=y_min) if y_min else alt.Undefined),
            tooltip=["date:T", "value:Q"]
        )
        .properties(title=title, width=500, height=250)
        .interactive()
    )
    return chart

# 🖥️ 앱 레이아웃 설정
st.set_page_config(page_title="환율 매크로 대시보드", layout="wide")
st.title("📊 환율 관련 실시간 매크로 대시보드")

# 🔘 유저 버튼
if st.button("🔄 Generate"):
    # 📉 시계열 차트 섹션
    st.subheader("📈 주요 매크로 지표 시계열 (원/달러 관련)")

    col1, col2 = st.columns(2)
    with col1:
        st.markdown("#### 🇺🇸 Fed Funds Upper (3년)")
        df_fed = fred_timeseries("DFEDTARU", 3)
        st.altair_chart(plot_chart(df_fed, "Fed Funds Target Range"))

        st.markdown("#### 🇰🇷 한국 3Y KTB 수익률 (2년)")
        df_kr3y = fred_timeseries("IR3TIB01KRM156N", 2)
        st.altair_chart(plot_chart(df_kr3y, "KTB 3Y Yield", y_min=2.0))

        st.markdown("#### 💱 DXY 달러지수 (1년)")
        df_dxy = fred_timeseries("DTWEXBGS", 1)
        st.altair_chart(plot_chart(df_dxy, "DXY Dollar Index", y_min=80))

    with col2:
        st.markdown("#### 🇺🇸 미국 2Y 수익률 (2년)")
        df_us2y = fred_timeseries("DGS2", 2)
        st.altair_chart(plot_chart(df_us2y, "US 2Y Treasury Yield", y_min=2.5))

        st.markdown("#### 📉 CBOE VIX 지수 (1년)")
        df_vix = fred_timeseries("VIXCLS", 1)
        st.altair_chart(plot_chart(df_vix, "CBOE VIX Index"))

    # 💶 원/유로 관련 시계열 추가
    st.subheader("📈 주요 매크로 지표 시계열 (원/유로 관련)")

    col3, col4 = st.columns(2)
    with col3:
        st.markdown("#### 🇰🇷 한국 기준금리")
        df_kr_base = fred_timeseries("IRKRBRT01STM156N", 3)
        st.altair_chart(plot_chart(df_kr_base, "Korea Base Rate"))

        st.markdown("#### 🇰🇷 한국 CPI")
        df_kr_cpi = fred_timeseries("IRKRCPICQINMEI", 3)
        st.altair_chart(plot_chart(df_kr_cpi, "Korea CPI"))

    with col4:
        st.markdown("#### 🇪🇺 ECB 예치금리")
        df_ecb = fred_timeseries("ECBDFR", 3)
        st.altair_chart(plot_chart(df_ecb, "ECB Deposit Facility Rate"))

        st.markdown("#### 🇪🇺 유로존 CPI")
        df_eu_cpi = fred_timeseries("CP0000EZ19M086NEST", 3)
        st.altair_chart(plot_chart(df_eu_cpi, "Eurozone CPI"))
