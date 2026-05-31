import streamlit as st
import pandas as pd
import math
from utils.data import load_data
from utils.data import stringify

st.set_page_config(
    page_title="Data Dump",
    page_icon="🗂️",
    layout="wide"
)

st.title("🗂️ Steam Data Dump")

PAGE_SIZE = 250
FILTER_PREFIX = "filter_"

try:

    df = load_data()
    df = stringify(df)

    # ---------------------------------------------------
    # Metadata
    # ---------------------------------------------------

    col1, col2 = st.columns(2)

    with col1:
        st.metric("Datasets", len(df))

    with col2:
        st.metric("Columns", len(df.columns))

    # ---------------------------------------------------
    # Column Filter
    # ---------------------------------------------------
    with st.expander("Filter Columns", expanded=False):

        # Init
        for column in df.columns:
            key = f"{FILTER_PREFIX}{column}"
            if key not in st.session_state:
                st.session_state[key] = True

        b1, b2 = st.columns(2)

        if b1.button("✅ Select All"):
            for column in df.columns:
                st.session_state[f"{FILTER_PREFIX}{column}"] = True

        if b2.button("❌ Select None"):
            for column in df.columns:
                st.session_state[f"{FILTER_PREFIX}{column}"] = False

        cols = st.columns(3)

        for idx, column in enumerate(df.columns):
            with cols[idx % 3]:
                st.checkbox(column, key=f"{FILTER_PREFIX}{column}")

        selected_columns = [
            col for col in df.columns
            if st.session_state[f"{FILTER_PREFIX}{col}"]
        ]

    # ---------------------------------------------------
    # Pagination State
    # ---------------------------------------------------
    if "page_number" not in st.session_state:
        st.session_state.page_number = 1

    page_number = st.session_state.page_number

    total_pages = math.ceil(len(df) / PAGE_SIZE)

    # ---------------------------------------------------
    # Navigation
    # ---------------------------------------------------
    st.subheader(f"Page {page_number:,} / {total_pages:,}")

    col1, col2 = st.columns(2)

    with col1:
        if st.button("⬅ Previous", width="stretch"):
            st.session_state.page_number = max(
                1,
                st.session_state.page_number - 1
            )
            st.rerun()

    with col2:
        if st.button("Next ➡", width="stretch"):
            st.session_state.page_number = min(
                total_pages,
                st.session_state.page_number + 1
            )
            st.rerun()

    # ---------------------------------------------------
    # Calculate Page Indices
    # ---------------------------------------------------
    start_idx = (page_number - 1) * PAGE_SIZE
    end_idx = start_idx + PAGE_SIZE

    page_df = df.iloc[start_idx:end_idx]

    # ---------------------------------------------------
    # Render
    # ---------------------------------------------------

    st.dataframe(
        page_df[selected_columns],
        use_container_width=True,
        height=600
    )


except FileNotFoundError:
    st.error(f"Data file not found")

except Exception as e:
    st.exception(e)