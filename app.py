import streamlit as st
import requests
import pandas as pd

# 🔑 FRED API Key
FRED_KEY = "53718f3eaba1c258d6c6ae8836cf6911"

# 📈 FRED 최신 수치 불러오기
@st.cache_data(ttl=300)
def fred_latest(series):
    url = (
        f"https://api.stlouisfed.org/fred/series/observations?"
        f"series_id={series}&api_key={FRED_KEY}&limit=1&sort_order=desc&file_type=json"
    )
    obs = requests.get(url, timeout=10).json()
    return float(obs["observations"][0]["value"])

# 📉 시계열 데이터 가져오기
@st.cache_data(ttl=300)
def fred_timeseries(series_id, start="2020-01-01"):
    url = (
        f"https://api.stlouisfed.org/fred/series/observations?"
        f"series_id={series_id}&api_key={FRED_KEY}&file_type=json"
        f"&sort_order=asc&observation_start={start}"
    )
    obs = requests.get(url, timeout=10).json()
    df = pd.DataFrame(obs["observations"])
    df["date"] = pd.to_datetime(df["date"])
    df["value"] = pd.to_numeric(df["value"], errors="coerce")
    df = df.set_index("date").dropna()
    return df

# 외국인 순매수 더미
@st.cache_data(ttl=300)
def get_foreign_netbuy_dummy():
    return {"KOSPI": -2543.0, "KOSDAQ": 731.0}

# 뉴스 불러오기
@st.cache_data(ttl=600)
def load_news():
    SHEET_CSV_URL = "https://docs.google.com/spreadsheets/d/1U751_0j_6D35wTY_Tj8roCppRCne2ubmo1jM1bmWE6Y/export?format=csv"
    df = pd.read_csv(SHEET_CSV_URL, usecols=[0, 4, 6], nrows=10)
    df.columns = ["제목", "요약", "본문"]
    return df

# 📊 Streamlit 설정
st.set_page_config(page_title="환율 매크로 대시보드", layout="wide")
st.title("📊 환율 관련 실시간 매크로 대시보드")

if st.button("🔄 Generate"):
    # ▶ 기존 USD 관련 지표
    col1, col2, col3 = st.columns(3)
    col1.metric("🇺🇸 Fed Funds Upper", f"{fred_latest('DFEDTARU'):.2f} %")
    col2.metric("🇺🇸 미국 2Y 수익률", f"{fred_latest('DGS2'):.2f} %")
    col3.metric("🇰🇷 한국 3Y KTB 수익률", f"{fred_latest('IR3TIB01KRM156N'):.2f} %")

    col4, col5, col6 = st.columns(3)
    col4.metric("💱 DXY 달러지수", f"{fred_latest('DTWEXBGS'):.2f}")
    col5.metric("📉 CBOE VIX 지수", f"{fred_latest('VIXCLS'):.2f}")

    netbuy = get_foreign_netbuy_dummy()
    col6.markdown("### 🌏 외국인 순매수 (억 원)")
    col6.markdown(f"- **KOSPI**: `{netbuy['KOSPI']}`  \n- **KOSDAQ**: `{netbuy['KOSDAQ']}`")

    # ▶ 원/유로 주요 지표 (최신 수치)
    st.markdown("---")
    st.markdown("## 💶 원/유로 환율 판단 지표")

    kr_eu_data = {
        "한국 기준금리 (%)": fred_latest("IRKRBRT01STM156N"),
        "ECB 예치금리 (%)": fred_latest("ECBDFR"),
        "한국 CPI (%)": fred_latest("KORCPIALLMINMEI"),  # ✅ 수정된 코드
        "유로존 CPI (%)": fred_latest("CP0000EZ19M086NEST"),
    }

    col_kr1, col_eu1 = st.columns(2)
    col_kr1.metric("🇰🇷 한국 기준금리", f"{kr_eu_data['한국 기준금리 (%)']:.2f} %")
    col_eu1.metric("🇪🇺 ECB 예치금리", f"{kr_eu_data['ECB 예치금리 (%)']:.2f} %")

    col_kr2, col_eu2 = st.columns(2)
    col_kr2.metric("🇰🇷 한국 CPI", f"{kr_eu_data['한국 CPI (%)']:.2f} %")
    col_eu2.metric("🇪🇺 유로존 CPI", f"{kr_eu_data['유로존 CPI (%)']:.2f} %")

    # ▶ 시계열 그래프 섹션
    st.markdown("---")
    st.markdown("## 📈 주요 지표 시계열 그래프")

    tab1, tab2, tab3, tab4 = st.tabs(["한국 기준금리", "ECB 예치금리", "한국 CPI", "유로존 CPI"])
    with tab1:
        df = fred_timeseries("IRKRBRT01STM156N")
        st.line_chart(df["value"], height=250)
    with tab2:
        df = fred_timeseries("ECBDFR")
        st.line_chart(df["value"], height=250)
    with tab3:
        df = fred_timeseries("KORCPIALLMINMEI")  # ✅ 수정된 코드
        st.line_chart(df["value"], height=250)
    with tab4:
        df = fred_timeseries("CP0000EZ19M086NEST")
        st.line_chart(df["value"], height=250)

    # ▶ 뉴스 섹션
    st.markdown("---")
    st.markdown("## 📰 최신 환율 관련 뉴스")
    news_df = load_news()
    for idx, row in news_df.iterrows():
        st.markdown(f"""
        ### {row['제목']}
        - {row['요약']}

        <details>
        <summary>본문 열기</summary>
        {row['본문']}
        </details>
        """)
