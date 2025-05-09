import streamlit as st
import requests
import pandas as pd
import datetime as dt

# 🔑 API 키를 여기에 입력하세요
FRED_KEY = "53718f3eaba1c258d6c6ae8836cf6911"
ECOS_KEY = "VYFYLK9K4BF0K8F45B69"

# 📈 FRED에서 최신 데이터 가져오기
@st.cache_data(ttl=300)
def fred_latest(series):
    url = f"https://api.stlouisfed.org/fred/series/observations?series_id={series}&api_key={FRED_KEY}&limit=1&sort_order=desc&file_type=json"
    obs = requests.get(url, timeout=10).json()
    return float(obs["observations"][0]["value"])

# 📊 ECOS에서 최신 데이터 가져오기 + 오류 방지 처리
def ecos_latest(code):
    yyyymm = dt.date.today().strftime("%Y%m")
    url = f"https://ecos.bok.or.kr/api/StatisticSearch/{ECOS_KEY}/json/kr/1/1/{code}/{yyyymm}"
    try:
        resp = requests.get(url, timeout=10).json()
        if 'StatisticSearch' in resp and resp['StatisticSearch']['row']:
            return float(resp['StatisticSearch']['row'][0]['DATA_VALUE'])
        else:
            st.warning("📭 ECOS 데이터가 아직 발표되지 않았거나 오류가 있습니다.")
            return 0.0
    except Exception as e:
        st.error(f"❌ ECOS API 오류: {e}")
        return 0.0

# 🖥️ Streamlit 페이지 설정
st.set_page_config(page_title="USD/KRW 대시보드", layout="wide")
st.title("💵 USD/KRW 실시간 매크로 대시보드")

# 🔘 버튼 클릭 시 데이터 표시
if st.button("🔄 Generate"):
    col1, col2, col3, col4 = st.columns(4)

    col1.metric("🇺🇸 Fed Funds Upper", f"{fred_latest('DFEDTARU'):.2f} %")
    col2.metric("🇺🇸 미국 2년물 금리", f"{fred_latest('DGS2'):.2f} %")
    col3.metric("🇰🇷 BOK 기준금리", f"{ecos_latest('722Y001'):.2f} %")
    col4.metric("💱 달러지수 (DXY)", f"{fred_latest('DTWEXBGS'):.2f}")
