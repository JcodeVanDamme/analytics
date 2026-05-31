import streamlit as st

st.set_page_config(
    page_title="Steam Analytics",
    page_icon="🎮",
    layout="wide"
)

st.title("🎮 Steam Analytics Platform")

st.markdown(
    """
    Use the navigation sidebar to switch between:

    - 🗂️ Data Dump
    - 🗂️ Browse Titles
    """
)

st.info("Select a page from the sidebar.")