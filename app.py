import streamlit as st
import requests
import pandas as pd
import datetime as dt

# 🔑 API 키 입력
FRED_KEY = "53718f3eaba1c258d6c6ae8836cf6911"
ECOS_KEY = "VYFYLK9K4BF0K8F45B69"

# 📈 FRED 지표 가져오기 함수
@st.cache_data(ttl=300)
def fred_latest(series):
    url = (
        f"https://api.stlouisfed.org/fred/series/observations?"
        f"series_id={series}&api_key={FRED_KEY}&limit=1&sort_order=desc&file_type=json"
    )
    obs = requests.get(url, timeout=10).json()
    return float(obs["observations"][0]["value"])

# 📊 ECOS 지표 가져오기 + 월별 fallback 처리
def ecos_latest(code):
    def query_ecos(yyyymm):
        url = (
            f"https://ecos.bok.or.kr/api/StatisticSearch/"
            f"{ECOS_KEY}/json/kr/1/1/{code}/{yyyymm}"
        )
        resp = requests.get(url, timeout=10).json()
        if 'StatisticSearch' in resp and resp['StatisticSearch']['row']:
            return float(resp['StatisticSearch']['row'][0]['DATA_VALUE'])
        return None

    # 1️⃣ 이번 달 기준 조회
    this_month = dt.date.today().strftime("%Y%m")
    val = query_ecos(this_month)
    if val is not None:
        return val

    # 2️⃣ 없다면 전달 기준 fallback
    last_month_date = dt.date.today().replace(day=1) - dt.timedelta(days=1)
    last_month = last_month_date.strftime("%Y%m")
    val = query_ecos(last_month)
    if val is not None:
        st.info(f"📅 최신 데이터가 없어 전달({last_month}) 기준금리를 표시합니다.")
        return val

    # 3️⃣ 둘 다 실패
    st.warning("📭 ECOS 데이터가 없습니다. API 키, 통계코드 또는 발표 일정을 확인하세요.")
    return 0.0

# 🖥️ Streamlit 앱 구성
st.set_page_config(page_title="USD/KRW 대시보드", layout="wide")
st.title("💵 USD/KRW 실시간 매크로 대시보드")

# 🔘 유저 인터랙션
if st.button("🔄 Generate"):
    col1, col2, col3, col4 = st.columns(4)

    col1.metric("🇺🇸 Fed Funds Upper", f"{fred_latest('DFEDTARU'):.2f} %")
    col2.metric("🇺🇸 미국 2년물 금리", f"{fred_latest('DGS2'):.2f} %")
    col3.metric("🇰🇷 BOK 기준금리", f"{ecos_latest('722Y001'):.2f} %")
    col4.metric("💱 달러지수 (DXY)", f"{fred_latest('DTWEXBGS'):.2f}")
