# ========================================================================
# ~/bigdata2026/fastapi/Streamlit/07_layout.py
#   
#   Streamlit 라이브러리 기초 실습
#
#       - 입력 위젯 (텍스트 입력, 파일 업로더 등)
# ========================================================================

# 1. 라이브러리 불러오기
import streamlit as st
import pandas as pd
import seaborn as sns
import matplotlib.pyplot as plt
from PIL import Image

# main page
st.title('This is main page')

# sidebar
with st.sidebar:
    st.title('This is sidebar')
    side_option = st.multiselect(
        label='your selection is',
        options=['Car', 'Airplane', 'Train', 'Ship', 'Bicycle'],
        placeholder='select transportation'
    )

img1 = Image.open('ex5.png')
img2 = Image.open('ex2.png')

st.header('포켓몬')
st.image(img1, width=400, caption='메타몽, 피카츄, 꼬부기, 이상해씨, 잠만보')

st.header('피카츄')
st.image(img2, width=400, caption='귀여운 피카츄')

# 컬럼레이아웃 (세로 단이 2개)
col1, col2 = st.columns(2) # 똑같은 비율로 나눠진다. 2개
with col1:
    st.header('포켓몬')
    st.image(img1, width=400, caption='메타몽, 피카츄, 꼬부기, 이상해씨, 잠만보')

with col2:
    st.header('피카츄')
    st.image(img2, width=400, caption='귀여운 피카츄')

st.divider()

# 웹 레이아웃
tab1, tab2 = st.tabs(['실습1', '실습2'])

# 판다스로 csv불러와서 데이터프레임 생성
df = pd.read_csv('2026-07-16T07-15_export.csv')

with tab1:
    st.table(df.head())

with tab2:
    fig, ax = plt.subplots()
    sns.countplot(data=df, ax=ax)
    st.pyplot(fig)