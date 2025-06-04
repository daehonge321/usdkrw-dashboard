import streamlit as st
import requests
import pandas as pd
from datetime import datetime, timedelta
import altair as alt

# 🔑 FRED API 키
FRED_KEY = "53718f3eaba1c258d6c6ae8836cf6911"

# 📈 FRED 시계열 데이터 가져오기 (예외 처리 추가)
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
    try:
        response = requests.get(url)
        response.raise_for_status()
        data = response.json().get("observations", [])
        df = pd.DataFrame(data)
        if df.empty:
            return pd.DataFrame(columns=["date", "value"])
        df["date"] = pd.to_datetime(df["date"])
        df["value"] = pd.to_numeric(df["value"], errors="coerce")
        return df.dropna()
    except requests.exceptions.RequestException as e:
        st.warning(f"📡 데이터 수신 실패: {series_id} — {str(e)}")
        return pd.DataFrame(columns=["date", "value"])

# 📊 Altair 차트 생성 함수
def plot_chart(df, title, y_min=None, y_max=None):
    if df.empty:
        return alt.Chart(pd.DataFrame({"date": [], "value": []})).mark_line().properties(title=title)
    chart = (
        alt.Chart(df)
        .mark_line()
        .encode(
            x="date:T",
            y=alt.Y("value:Q", scale=alt.Scale(domainMin=y_min, domainMax=y_max) if y_min is not None or y_max is not None else alt.Undefined),
            tooltip=["date:T", "value:Q"]
        )
        .properties(title=title, width=500, height=250)
        .interactive()
    )
    return chart

# 📌 최신 수치 불러오기
def fred_latest(series_id):
    url = f"https://api.stlouisfed.org/fred/series/observations?series_id={series_id}&api_key={FRED_KEY}&file_type=json&limit=1&sort_order=desc"
    try:
        response = requests.get(url)
        response.raise_for_status()
        obs = response.json().get("observations", [])
        return float(obs[0]["value"])
    except:
        return None

# 💝 앱 레이아웃 설정
st.set_page_config(page_title="환율 매크로 대시보드", layout="wide")
st.title("📊 환율 관련 실시간 매크로 대시보드")

# 🔘 데이터 생성 버튼
if st.button("🔄 Generate"):
    # 📉 원/달러 관련
    st.subheader("📈 주요 매크로 지표 시계열 (원/달러 관련)")

    col1, col2 = st.columns(2)
    with col1:
        fed_val = fred_latest("DFEDTARU")
        st.markdown(f"#### 🇺🇸 Fed Funds Upper (3년): {fed_val:.2f}%")
        df_fed = fred_timeseries("DFEDTARU", 3)
        st.altair_chart(plot_chart(df_fed, "Fed Funds Target Range"))

        kr3y_val = fred_latest("IR3TIB01KRM156N")
        st.markdown(f"#### 🇰🇷 한국 3Y KTB 수익률 (2년): {kr3y_val:.2f}%")
        df_kr3y = fred_timeseries("IR3TIB01KRM156N", 2)
        st.altair_chart(plot_chart(df_kr3y, "KTB 3Y Yield", y_min=2.0))

        dxy_val = fred_latest("DTWEXBGS")
        st.markdown(f"#### 💱 DXY 달러지수 (1년): {dxy_val:.2f}")
        df_dxy = fred_timeseries("DTWEXBGS", 1)
        st.altair_chart(plot_chart(df_dxy, "DXY Dollar Index", y_min=80))

    with col2:
        us2y_val = fred_latest("DGS2")
        st.markdown(f"#### 🇺🇸 미국 2Y 수익률 (2년): {us2y_val:.2f}%")
        df_us2y = fred_timeseries("DGS2", 2)
        st.altair_chart(plot_chart(df_us2y, "US 2Y Treasury Yield", y_min=2.5))

        vix_val = fred_latest("VIXCLS")
        st.markdown(f"#### 📉 CBOE VIX 지수 (1년): {vix_val:.2f}")
        df_vix = fred_timeseries("VIXCLS", 1)
        st.altair_chart(plot_chart(df_vix, "CBOE VIX Index"))

    # 💶 원/유로 관련
    st.subheader("📈 주요 매크로 지표 시계열 (원/유로 관련)")

    col3, col4 = st.columns(2)
    with col3:
        kr_cpi_val = fred_latest("KRCPHARMQINMEI")
        st.markdown(f"#### 🇰🇷 한국 CPI (% YoY): {kr_cpi_val:.2f}%")
        df_kr_cpi = fred_timeseries("KRCPHARMQINMEI", 3)
        st.altair_chart(plot_chart(df_kr_cpi, "Korea CPI (% YoY)", y_min=0, y_max=10))

    with col4:
        ecb_val = fred_latest("ECBDFR")
        st.markdown(f"#### 🇪🇺 ECB 예치금리: {ecb_val:.2f}%")
        df_ecb = fred_timeseries("ECBDFR", 3)
        st.altair_chart(plot_chart(df_ecb, "ECB Deposit Facility Rate"))

        eu_cpi_val = fred_latest("CP0000EZ19M086NEST")
        st.markdown(f"#### 🇪🇺 유로존 CPI (% YoY): {eu_cpi_val:.2f}%")
        df_eu_cpi = fred_timeseries("CP0000EZ19M086NEST", 3)
        st.altair_chart(plot_chart(df_eu_cpi, "Eurozone CPI (% YoY)", y_min=80, y_max=140))

        m2_val = fred_latest("MABMM201EZM189S")
        st.markdown(f"#### 🇪🇺 유로존 M2 통화량 YoY (%): {m2_val:.2f}%")
        df_m2 = fred_timeseries("MABMM201EZM189S", 3)
        st.altair_chart(plot_chart(df_m2, "Euro Area M2 Growth YoY (%)", y_min=0, y_max=10))
