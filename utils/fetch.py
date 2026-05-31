import streamlit as st
import requests
@st.cache_data
def fetch_live_review_score(appid):

    url = (
        f"https://store.steampowered.com/appreviews/"
        f"{appid}?json=1"
    )

    r = requests.get(url, timeout=10)
    r.raise_for_status()

    summary = r.json()["query_summary"]

    positive = summary["total_positive"]
    negative = summary["total_negative"]

    return (
        positive /
        (positive + negative)
    ) * 100