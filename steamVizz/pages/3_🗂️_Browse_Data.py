import streamlit as st
import pandas as pd
import utils.components as comp
from utils.data import load_data
from utils.data import mockData

st.set_page_config(
    page_title="Browse Data",
    page_icon="🗂️",
    layout="wide"
)

st.title("🗂️ Browse Data")

def show_details(row):
    @st.dialog(row['name'])
    def dialog():

        comp.label("Released:", row.release_date)

        st.image(f"{row.header_image}", use_container_width=True)

        st.write(f"{row.short_description}")

        st.write("Tags:")

        with st.container(horizontal=True, gap="xxsmall"):
            for tag in row.tags:
                st.badge(tag)

        st.divider()

        # Retention Score

        # Genre Ranking

        # Publisher Ranking

    dialog()


try:

    # Load cached Data
    df = load_data()

    search = st.text_input(
        "Search...",
        placeholder="Type a name..."
    )
    matches = df[
        df["name"].str.contains(search, case=False, na=False)
    ] if search else df.head()

    event = st.dataframe(
        matches[["name"]],
        use_container_width=True,
        hide_index=True,
        on_select="rerun",
        selection_mode="single-cell"
    )

    cells = event.selection["cells"]

    if cells:
        row_in_matches = cells[0][0]
        original_idx = matches.index[row_in_matches]
        selected_row = df.loc[original_idx]

        show_details(selected_row)


except FileNotFoundError:
    st.error(f"Data file not found")

except Exception as e:
    st.exception(e)