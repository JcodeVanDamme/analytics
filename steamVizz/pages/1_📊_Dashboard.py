import streamlit as st

st.set_page_config(
    page_title="Dashboard",
    page_icon="📊",
    layout="wide"
)

st.title("📊 Dashboard")

st.markdown("## Overview")

col1, col2, col3 = st.columns(3)

with col1:
    st.metric("Games", "122,611")

with col2:
    st.metric("Platforms", "3")

with col3:
    st.metric("Avg Price", "$12.49")

st.divider()

st.subheader("Placeholder Dashboard")

st.write(
    """
    This page can later contain:

    - Charts
    - KPIs
    - Filters
    - Aggregations
    - Search
    - Recommendation systems
    - Genre statistics
    - CCU analytics
    - Price distributions
    """
)