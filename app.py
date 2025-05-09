import streamlit as st
import requests
import pandas as pd
import datetime as dt

# API 키
FRED_KEY = "53718f3eaba1c258d6c6ae8836cf6911"

@st.cache_data(ttl=300)
def fred_latest(series):
    url = (
        f"https://api.stlouisfed.org/fred/series/observations?"
        f"series_id={series}&api_key={FRED_KEY}&limit=1&sort_order=desc&file_type=json"
    )
    obs = requests.get(url, timeout=10).json()
    return float(obs["observations"][0]["value"])

# KRX 외국인 순매수 크롤링 예시 (단순 파싱용, 정식 API가 없을 경우)
@st.cache_data(ttl=300)
def get_foreign_netbuy_dummy():
    # 실제 연동은 한국거래소 CSV or data.krx.co.kr API 필요
    # 여긴 시연용 하드코딩 예시
    return {
        "KOSPI": -2543.0,  # 억 원 단위
        "KOSDAQ": 731.0
    }

# 앱 구성
st.set_page_config(page_title="USD/KRW 매크로 대시보드", layout="wide")
st.title("💵 USD/KRW 실시간 매크로 대시보드")

if st.button("🔄 Generate"):
    col1, col2, col3 = st.columns(3)
    col1.metric("🇺🇸 Fed Funds Upper", f"{fred_latest('DFEDTARU'):.2f} %")
    col2.metric("🇺🇸 미국 2Y 수익률", f"{fred_latest('DGS2'):.2f} %")
    col3.metric("🇰🇷 한국 3Y KTB 수익률", f"{fred_latest('IR3TIB01KRM156N'):.2f} %")

    col4, col5, col6 = st.columns(3)
    col4.metric("💱 DXY 달러지수", f"{fred_latest('DTWEXBGS'):.2f}")
    col5.metric("📉 CBOE VIX 지수", f"{fred_latest('VIXCLS'):.2f}")
    
    # 외국인 순매수
    netbuy = get_foreign_netbuy_dummy()
    col6.metric("🌏 외국인 순매수 (억 원)", f"KOSPI: {netbuy['KOSPI']}, KOSDAQ: {netbuy['KOSDAQ']}")
