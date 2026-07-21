import streamlit as st

# 다중 선택 박스
st.title('나만의 자기소개 카드')

name = st.text_input(
    '이름을 입력하세요',
    placeholder='예) 홍길동'
)

years = st.slider(
    '경력 연차를 선택하세요',
    min_value= 0,
    max_value= 20,
    value=0
)

skills = st.multiselect(
    '관심 있는 기술을 모두 선택하세요',
    ['Python','SQL', 'Streamlit', 'FastAPI', '머신러닝']
)

st.divider()

if name:
    col1, col2 = st.columns([1, 3])
    
    with col1:
        st.markdown(f'''
        <div style="width:60px;height:60px;border-radius:50%'
                    background-color:#e6f1fb;
                    display:flex;
                    justify-content:center;
                    align-items:center;
                    font-weight:bold;">{name[0]}</div>
                    ''',            
                    unsafe_allow_html=True)

    with col2:
        st.write(f'**이름:** {name}')
        st.write(f'**경력 연차:** {years}년')

        if skills:
            st.write(f'**관심 기술:**', ', ' .join(skills))
        else:
            st.write('**관심 기술:** 선택된 항목 없음')

else:
    st.info('이름을 입력하면 카드가 생성됩니다.')
