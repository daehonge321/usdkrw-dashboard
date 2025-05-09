import streamlit as st
import requests
import pandas as pd
import datetime as dt

# 🔑 API 키
FRED_KEY = "53718f3eaba1c258d6c6ae8836cf6911"
ECOS_KEY = "VYFYLK9K4BF0K8F45B69"

# 📈 FRED 지표
@st.cache_data(ttl=300)
def fred_latest(series):
    url = (
        f"https://api.stlouisfed.org/fred/series/observations?"
        f"series_id={series}&api_key={FRED_KEY}&limit=1&sort_order=desc&file_type=json"
    )
    obs = requests.get(url, timeout=10).json()
    return float(obs["observations"][0]["value"])

# 📊 ECOS 기준금리: 기준일자별 탐색 → 없으면 월평균 fallback
def ecos_latest_combined():
    # 1️⃣ 기준일자별 코드(722Y001)로 최근 30일 탐색
    base_date = dt.date.today()
    for i in range(30):
        try_date = (base_date - dt.timedelta(days=i)).strftime("%Y%m%d")
        url = (
            f"https://ecos.bok.or.kr/api/StatisticSearch/"
            f"{ECOS_KEY}/json/kr/1/1/722Y001/{try_date}"
        )
        try:
            resp = requests.get(url, timeout=10).json()
            if 'StatisticSearch' in resp and resp['StatisticSearch']['row']:
                val = float(resp['StatisticSearch']['row'][0]['DATA_VALUE'])
                st.info(f"📅 {try_date} 기준 기준금리를 표시합니다.")
                return val
        except:
            pass  # 네트워크 오류 무시

    # 2️⃣ 없으면 월평균 기준금리(722Y002)로 fallback
    last_month = (base_date.replace(day=1) - dt.timedelta(days=1)).strftime("%Y")
    url_monthly = (
        f"https://ecos.bok.or.kr/api/StatisticSearch/"
        f"{ECOS_KEY}/json/kr/1/1/722Y002/M/{last_month}/{last_month}/010101000"
    )
    try:
        resp = requests.get(url_monthly, timeout=10).json()
        if 'StatisticSearch' in resp and resp['StatisticSearch']['row']:
            val = float(resp['StatisticSearch']['row'][0]['DATA_VALUE'])
            st.info(f"📅 월평균 기준금리({last_month})로 대체되었습니다.")
            return val
    except:
        pass

    st.warning("📭 ECOS 기준금리 데이터가 없습니다.")
    return 0.0

# 🖥️ Streamlit 앱 구성
st.set_page_config(page_title="USD/KRW 대시보드", layout="wide")
st.title("💵 USD/KRW 실시간 매크로 대시보드")

# 🔘 사용자 버튼 인터랙션
if st.button("🔄 Generate"):
    col1, col2, col3, col4 = st.columns(4)

    col1.metric("🇺🇸 Fed Funds Upper", f"{fred_latest('DFEDTARU'):.2f} %")
    col2.metric("🇺🇸 미국 2년물 금리", f"{fred_latest('DGS2'):.2f} %")
    col3.metric("🇰🇷 BOK 기준금리", f"{ecos_latest_combined():.2f} %")
    col4.metric("💱 달러지수 (DXY)", f"{fred_latest('DTWEXBGS'):.2f}")
