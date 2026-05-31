import streamlit as st
import pyarrow.parquet as pq
import pandas as pd
from pathlib import Path

DATA_FILE_PATH = Path("data/games.parquet")


@st.cache_data(show_spinner=True)
def get_total_rows():
    parquet_file = pq.ParquetFile(DATA_FILE_PATH)
    return parquet_file.metadata.num_rows


@st.cache_data(show_spinner=True)
def load_page(start: int, end: int):
    table = pq.read_table(
        DATA_FILE_PATH,
        columns=None,
        use_threads=True,
        memory_map=True
    )

    df = table.slice(start, end - start).to_pandas()

    if "game_id" not in df.columns:
        df = df.reset_index().rename(columns={"index": "game_id"})

    return df