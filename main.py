import streamlit as st

st.set_page_config(
    page_title="Steam Analytics",
    page_icon="🎮",
    layout="wide"
)

st.title("🎮 Steam Analytics Platform")

st.markdown(
    """
    Welcome to the Steam Analytics dashboard.

    Use the navigation sidebar to switch between:

    - 📊 Dashboard
    - 🗂️ Data Dump
    """
)

st.info("Select a page from the sidebar.")