import streamlit as st

# 다중 선택 박스
st.title('나만의 자기소개 카드')

string1 = st.text_input(
    '이름을 입력하세요',
    placeholder='예) 홍길동',
    max_chars=32
)

st.divider()
st.write('경력 연차를 선택하세요')
score = st.slider('', 0, 100, 0) 


st.divider()
sub = st.multiselect(
    '관심 있는 기술을 모두 선택하세요',
    ['Python','SQL', 'Streamlit', 'FastAPI', '머신러닝']
)

st.write('---')

if not string1:
    st.info('이름을 입력하면 카드가 생성됩니다.')
else:
    col1, col2 = st.columns([1, 4])
    
    with col2:
        st.write('')

