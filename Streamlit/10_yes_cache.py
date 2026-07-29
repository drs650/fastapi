# ========================================================================
# ~/bigdata2026/fastapi/Streamlit/10_yes_cache.py
#   
#   캐시가 있을 때의 경우
# ========================================================================
import streamlit as st
import pandas as pd
import time

@st.cache_data  # 이 한 줄이 핵심
def load_subway_data():
    time.sleep(2)
    return pd.read_csv("subway_long.csv", index_col=False)

st.title("캐싱 적용해보기")

station = st.selectbox("역을 선택하세요", ["동대구역", "반월당역", "범어역"])

df = load_subway_data()
st.write(f"{station} 데이터 로딩 완료")
st.dataframe(df.head())