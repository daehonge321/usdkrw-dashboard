import streamlit as st
import requests
import pandas as pd
import datetime as dt

# 🔑 API 키 입력
FRED_KEY = "53718f3eaba1c258d6c6ae8836cf6911"
ECOS_KEY = "VYFYLK9K4BF0K8F45B69"

# 📈 FRED에서 최신 데이터 가져오기
@st.cache_data(ttl=300)
def fred_latest(series):
    url = (
        f"https://api.stlouisfed.org/fred/series/observations?"
        f"series_id={series}&api_key={FRED_KEY}&limit=1&sort_order=desc&file_type=json"
    )
    obs = requests.get(url, timeout=10).json()
    return float(obs["observations"][0]["value"])

# 📊 ECOS 기준금리 - 가장 최근 날짜부터 자동 탐색 (최대 10일)
def ecos_latest_dynamic():
    base_date = dt.date.today()
    for i in range(10):
        try_date = (base_date - dt.timedelta(days=i)).strftime("%Y%m%d")
        url = (
            f"https://ecos.bok.or.kr/api/StatisticSearch/"
            f"{ECOS_KEY}/json/kr/1/1/722Y001/{try_date}"
        )
        try:
            resp = requests.get(url, timeout=10).json()
            if 'StatisticSearch' in resp and resp['StatisticSearch']['row']:
                value = float(resp['StatisticSearch']['row'][0]['DATA_VALUE'])
                st.info(f"📅 {try_date} 기준 기준금리를 표시합니다.")
                return value
        except Exception as e:
            st.error(f"❌ ECOS 오류: {e}")
    st.warning("📭 최근 10일 내 ECOS 기준금리 데이터가 없습니다.")
    return 0.0

# 🖥️ Streamlit 앱 구성
st.set_page_config(page_title="USD/KRW 대시보드", layout="wide")
st.title("💵 USD/KRW 실시간 매크로 대시보드")

# 🔘 유저 인터랙션
if st.button("🔄 Generate"):
    col1, col2, col3, col4 = st.columns(4)

    col1.metric("🇺🇸 Fed Funds Upper", f"{fred_latest('DFEDTARU'):.2f} %")
    col2.metric("🇺🇸 미국 2년물 금리", f"{fred_latest('DGS2'):.2f} %")
    col3.metric("🇰🇷 BOK 기준금리", f"{ecos_latest_dynamic():.2f} %")
    col4.metric("💱 달러지수 (DXY)", f"{fred_latest('DTWEXBGS'):.2f}")
