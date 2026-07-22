# ========================================================================
# ~/bigdata2026/fastapi/Streamlit/practice3.py
#   
#   Streamlit 연습문제 3 - 간단 설문 & 만족도 조사
# ========================================================================
import streamlit as st

st.title('간단 설문 & 만족도 조사')

name = st.text_input('이름을 입력하세요')

interests = st.multiselect('관심있는 분야를 선택하세요.',
                           ['AI', '빅데이터', '웹개발', '클라우드', '보안'])

satisfaction = st.slider('이번 수업 만족도를 선택하세요. (0~10)',
                         min_value=0, max_value=10, value=5)

st.divider()

submitted = st.button('제출하기')

if submitted:
    if name and interests:
        st.success('제출이 완료되었습니다. 참여해주셔서 감사합니다.')

        st.write(f'**응답자:** {name}')
        st.write(f'**관심 분야:** {interests}')
        st.write(f'**만족도:** {satisfaction} / 10')
    
    else:
        st.write(f'')
else:
    st.divider()