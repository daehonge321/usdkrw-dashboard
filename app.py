import streamlit as st
import requests
import pandas as pd
from datetime import datetime, timedelta

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
    return df.set_index("date")["value"]

# 🖥️ 앱 레이아웃 설정
st.set_page_config(page_title="환율 매크로 대시보드", layout="wide")
st.title("📊 환율 관련 실시간 매크로 대시보드")

# 🔘 유저 버튼
if st.button("🔄 Generate"):
    # 📉 시계열 차트 섹션
    st.subheader("📈 주요 매크로 지표 시계열")

    col1, col2 = st.columns(2)
    with col1:
        st.markdown("#### 🇺🇸 Fed Funds Upper (3년)")
        st.line_chart(fred_timeseries("DFEDTARU", 3))

        st.markdown("#### 🇰🇷 한국 3Y KTB 수익률 (2년)")
        st.line_chart(fred_timeseries("IR3TIB01KRM156N", 2))

        st.markdown("#### 💱 DXY 달러지수 (1년)")
        st.line_chart(fred_timeseries("DTWEXBGS", 1))

    with col2:
        st.markdown("#### 🇺🇸 미국 2Y 수익률 (2년)")
        st.line_chart(fred_timeseries("DGS2", 2))

        st.markdown("#### 📉 CBOE VIX 지수 (1년)")
        st.line_chart(fred_timeseries("VIXCLS", 1))
