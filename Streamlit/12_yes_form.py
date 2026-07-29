# ========================================================================
# ~/bigdata2026/fastapi/Streamlit/12_yes_form.py
#   
#   왜 폼이 필요할까? - 문제 상황 살펴보기(폼이 있는 경우)
# ========================================================================
import streamlit as st

st.title("회원가입 (문제 상황)")

name = st.text_input("이름")
email = st.text_input("이메일")
age = st.number_input("나이", min_value=0, max_value=120)

st.write("---")
st.write(f"입력한 이름:{name}")