import streamlit as st
import requests
import pandas as pd

# 🔑 API 키
FRED_KEY = "53718f3eaba1c258d6c6ae8836cf6911"

# 📈 FRED 실시간 지표 조회 함수
@st.cache_data(ttl=300)
def fred_latest(series):
    url = (
        f"https://api.stlouisfed.org/fred/series/observations?"
        f"series_id={series}&api_key={FRED_KEY}&limit=1&sort_order=desc&file_type=json"
    )
    obs = requests.get(url, timeout=10).json()
    return float(obs["observations"][0]["value"])

# 🌏 외국인 순매수 더미 함수 (실제 연동은 data.krx.co.kr 필요)
@st.cache_data(ttl=300)
def get_foreign_netbuy_dummy():
    return {
        "KOSPI": -2543.0,   # 단위: 억 원
        "KOSDAQ": 731.0
    }

# 📰 Google 스프레드시트 뉴스 불러오기
@st.cache_data(ttl=600)
def load_news():
    SHEET_CSV_URL = "https://docs.google.com/spreadsheets/d/1U751_0j_6D35wTY_Tj8roCppRCne2ubmo1jM1bmWE6Y/export?format=csv"
    df = pd.read_csv(SHEET_CSV_URL, usecols=[0, 4, 6], nrows=10)
    df.columns = ["제목", "요약", "본문"]
    return df

# 🖥️ 앱 레이아웃 설정
st.set_page_config(page_title="환율 매크로 대시보드", layout="wide")
st.title("📊 환율 관련 실시간 매크로 대시보드")

# 🔘 유저 버튼
if st.button("🔄 Generate"):
    col1, col2, col3 = st.columns(3)
    col1.metric("🇺🇸 Fed Funds Upper", f"{fred_latest('DFEDTARU'):.2f} %")
    col2.metric("🇺🇸 미국 2Y 수익률", f"{fred_latest('DGS2'):.2f} %")
    col3.metric("🇰🇷 한국 3Y KTB 수익률", f"{fred_latest('IR3TIB01KRM156N'):.2f} %")

    col4, col5, col6 = st.columns(3)
    col4.metric("💱 DXY 달러지수", f"{fred_latest('DTWEXBGS'):.2f}")
    col5.metric("📉 CBOE VIX 지수", f"{fred_latest('VIXCLS'):.2f}")

    netbuy = get_foreign_netbuy_dummy()
    col6.markdown("### 🌏 외국인 순매수 (억 원)")
    col6.markdown(f"""
- **KOSPI**: `{netbuy['KOSPI']}`  
- **KOSDAQ**: `{netbuy['KOSDAQ']}`
""")

    # 📰 뉴스 섹션
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
