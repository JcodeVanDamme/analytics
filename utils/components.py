import streamlit as st


def label(label : str, content : str):
    #l, r = st.columns(2)
    #with l:
    #    st.write(label)
    #with r:
    #    st.write(content)
    with st.container(horizontal=True, gap="xxsmall", width="content"):
        st.write(label)
        st.write(content)
