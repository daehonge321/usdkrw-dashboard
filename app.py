%%writefile app.py
import streamlit as st, requests, pandas as pd, datetime as dt

FRED_KEY = "53718f3eaba1c258d6c6ae8836cf6911"
ECOS_KEY = "VYFYLK9K4BF0K8F45B69"

@st.cache_data(ttl=300)
def fred_latest(series):
    url = f"https://api.stlouisfed.org/fred/series/observations?series_id={series}&api_key={FRED_KEY}&limit=1&sort_order=desc&file_type=json"
    obs = requests.get(url).json()["observations"][0]
    return float(obs["value"])

def ecos_latest(code):
    yyyymm = dt.date.today().strftime("%Y%m")
    url = f"https://ecos.bok.or.kr/api/StatisticSearch/{ECOS_KEY}/json/kr/1/1/{code}/{yyyymm}"
    return float(requests.get(url).json()['StatisticSearch']['row'][0]['DATA_VALUE'])

st.set_page_config(page_title="USD/KRW 대시보드", layout="wide")
st.title("USD/KRW 실시간 매크로 대시보드")

if st.button("Generate"):
    col1, col2, col3, col4 = st.columns(4)
    col1.metric("Fed Funds Upper", f"{fred_latest('DFEDTARU'):.2f} %")
    col2.metric("미국 2년물 금리", f"{fred_latest('DGS2'):.2f} %")
    col3.metric("BOK 기준금리", f"{ecos_latest('722Y001'):.2f} %")
    col4.metric("달러지수 (DXY)", f"{fred_latest('DTWEXBGS'):.2f}")
