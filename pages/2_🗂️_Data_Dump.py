import streamlit as st
import pandas as pd
import math

from utils.data import get_total_rows, load_page

# ---------------------------------------------------
# Page Config
# ---------------------------------------------------
st.set_page_config(
    page_title="Data Dump",
    page_icon="🗂️",
    layout="wide"
)

st.title("🗂️ Steam Data Dump")

# ---------------------------------------------------
# Constants
# ---------------------------------------------------
PAGE_SIZE = 250
FILTER_PREFIX = "filter_"

# ---------------------------------------------------
# Session State (Pagination)
# ---------------------------------------------------
if "page_number_dump" not in st.session_state:
    st.session_state.page_number_dump = 1

page_number_dump = st.session_state.page_number_dump

# ---------------------------------------------------
# Data Loading (lightweight page-based load)
# ---------------------------------------------------
try:
    total_rows = get_total_rows()
    total_pages = math.ceil(total_rows / PAGE_SIZE)

    # clamp page number
    page_number_dump = max(1, min(page_number_dump, total_pages))
    st.session_state.page_number_dump = page_number_dump

    start_idx = (page_number_dump - 1) * PAGE_SIZE
    end_idx = min(start_idx + PAGE_SIZE, total_rows)

    df = load_page(start_idx, end_idx)

    # ---------------------------------------------------
    # Metadata
    # ---------------------------------------------------
    col1, col2 = st.columns(2)

    with col1:
        st.metric("Datasets", total_rows)

    with col2:
        st.metric("Columns", len(df.columns))

    # ---------------------------------------------------
    # Column Filter
    # ---------------------------------------------------
    with st.expander("Filter Columns", expanded=False):

        # init checkboxes once
        for column in df.columns:
            key = f"{FILTER_PREFIX}{column}"
            if key not in st.session_state:
                st.session_state[key] = True

        # bulk actions
        b1, b2 = st.columns(2)

        if b1.button("✅ Select All", use_container_width=True):
            for column in df.columns:
                st.session_state[f"{FILTER_PREFIX}{column}"] = True

        if b2.button("❌ Select None", use_container_width=True):
            for column in df.columns:
                st.session_state[f"{FILTER_PREFIX}{column}"] = False

        # checkboxes
        cols = st.columns(3)

        for idx, column in enumerate(df.columns):
            with cols[idx % 3]:
                st.checkbox(column, key=f"{FILTER_PREFIX}{column}")

        selected_columns = [
            col for col in df.columns
            if st.session_state.get(f"{FILTER_PREFIX}{col}", True)
        ]

    # ---------------------------------------------------
    # Navigation
    # ---------------------------------------------------
    st.subheader(f"Page {page_number_dump:,} / {total_pages:,}")

    col1, col2 = st.columns(2)

    with col1:
        if st.button("⬅ Previous", use_container_width=True):
            st.session_state.page_number_dump -= 1
            st.rerun()

    with col2:
        if st.button("Next ➡", use_container_width=True):
            st.session_state.page_number_dump += 1
            st.rerun()

    # ---------------------------------------------------
    # Render Table
    # ---------------------------------------------------
    st.dataframe(
        df[selected_columns],
        use_container_width=True,
        height=600
    )

except FileNotFoundError:
    st.error("Data file not found")

except Exception as e:
    st.exception(e)