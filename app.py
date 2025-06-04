import streamlit as st
import requests
import pandas as pd
from datetime import datetime, timedelta
import altair as alt

# 🔑 FRED API 키
FRED_KEY = "53718f3eaba1c258d6c6ae8836cf6911"

# 📈 FRED 시계열 데이터 가져오기 (예외 처리 포함)
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

# 📊 Altair 차트 생성 함수 (스케일 조건 분기)
def plot_chart(df, title, y_min=None, y_max=None):
    if df.empty:
        return alt.Chart(pd.DataFrame({"date": [], "value": []})).mark_line().properties(title=title)

    scale_args = {}
    if y_min is not None:
        scale_args["domainMin"] = y_min
    if y_max is not None:
        scale_args["domainMax"] = y_max
    y_scale = alt.Scale(**scale_args) if scale_args else alt.Undefined

    chart = (
        alt.Chart(df)
        .mark_line()
        .encode(
            x="date:T",
            y=alt.Y("value:Q", scale=y_scale),
            tooltip=["date:T", "value:Q"]
        )
        .properties(title=title, width=500, height=250)
        .interactive()
    )
    return chart

# 💝 앱 레이아웃 설정
st.set_page_config(page_title="환율 매크로 데시보드", layout="wide")
st.title("📊 환율 관련 실시간 매크로 데시보드")

# 🔘 데이터 생성 버튼
if st.button("🔄 Generate"):
    # 📉 원/달러 관련
    st.subheader("📈 주요 매크로 지표 시계열 (원/달러 관련)")

    col1, col2 = st.columns(2)
    with col1:
        df_fed = fred_timeseries("DFEDTARU", 3)
        latest = df_fed["value"].iloc[-1] if not df_fed.empty else None
        st.markdown(f"#### 🇺🇸 Fed Funds Upper (3년): {latest:.2f}%" if latest else "#### 🇺🇸 Fed Funds Upper (3년)")
        st.altair_chart(plot_chart(df_fed, "Fed Funds Target Range"))

        df_kr3y = fred_timeseries("IR3TIB01KRM156N", 2)
        latest = df_kr3y["value"].iloc[-1] if not df_kr3y.empty else None
        st.markdown(f"#### 🇰🇷 한국 3Y KTB 수익률 (2년): {latest:.2f}%" if latest else "#### 🇰🇷 한국 3Y KTB 수익률 (2년)")
        st.altair_chart(plot_chart(df_kr3y, "KTB 3Y Yield", y_min=2.0))

        df_dxy = fred_timeseries("DTWEXBGS", 1)
        latest = df_dxy["value"].iloc[-1] if not df_dxy.empty else None
        st.markdown(f"#### 💱 DXY 달러지수 (1년): {latest:.2f}" if latest else "#### 💱 DXY 달러지수 (1년)")
        st.altair_chart(plot_chart(df_dxy, "DXY Dollar Index", y_min=80))

    with col2:
        df_us2y = fred_timeseries("DGS2", 2)
        latest = df_us2y["value"].iloc[-1] if not df_us2y.empty else None
        st.markdown(f"#### 🇺🇸 미국 2Y 수익률 (2년): {latest:.2f}%" if latest else "#### 🇺🇸 미국 2Y 수익률 (2년)")
        st.altair_chart(plot_chart(df_us2y, "US 2Y Treasury Yield", y_min=2.5))

        df_vix = fred_timeseries("VIXCLS", 1)
        latest = df_vix["value"].iloc[-1] if not df_vix.empty else None
        st.markdown(f"#### 📉 CBOE VIX 지수 (1년): {latest:.2f}" if latest else "#### 📉 CBOE VIX 지수 (1년)")
        st.altair_chart(plot_chart(df_vix, "CBOE VIX Index"))

    # 💶 원/유로 관련
    st.subheader("📈 주요 매크로 지표 시계열 (원/유로 관련)")

    col3, col4 = st.columns(2)
    with col3:
        # 한국 CPI를 YoY 비율로 대체 (IRCPBKRQINMEI)
        df_kr_cpi = fred_timeseries("IRCPBKRQINMEI", 3)
        latest = df_kr_cpi["value"].iloc[-1] if not df_kr_cpi.empty else None
        st.markdown(f"#### 🇰🇷 한국 CPI (% YoY): {latest:.1f}%" if latest else "#### 🇰🇷 한국 CPI (% YoY)")
        st.altair_chart(plot_chart(df_kr_cpi, "Korea CPI YoY", y_min=0, y_max=10))

    with col4:
        df_ecb = fred_timeseries("ECBDFR", 3)
        latest = df_ecb["value"].iloc[-1] if not df_ecb.empty else None
        st.markdown(f"#### 🇪🇺 ECB 예치금리: {latest:.2f}%" if latest else "#### 🇪🇺 ECB 예치금리")
        st.altair_chart(plot_chart(df_ecb, "ECB Deposit Facility Rate"))

        df_eu_cpi = fred_timeseries("CP0000EZ19M086NEST", 3)
        latest = df_eu_cpi["value"].iloc[-1] if not df_eu_cpi.empty else None
        st.markdown(f"#### 🇪🇺 유로존 CPI (% YoY): {latest:.1f}" if latest else "#### 🇪🇺 유로존 CPI (% YoY)")
        st.altair_chart(plot_chart(df_eu_cpi, "Eurozone CPI YoY", y_min=80, y_max=140))

        df_m2 = fred_timeseries("MYAGM2EZM196N", 3)
        latest = df_m2["value"].iloc[-1] if not df_m2.empty else None
        st.markdown(f"#### 💶 유로존 M2 통화량 증가율 YoY: {latest:.2f}%" if latest else "#### 💶 유로존 M2 통화량 증가율 YoY")
        st.altair_chart(plot_chart(df_m2, "Eurozone M2 Money Supply YoY"))
