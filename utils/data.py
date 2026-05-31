import streamlit as st
import pyarrow.parquet as pq
import duckdb
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

def search_games(query: str, limit: int = 100):
    if not query:
        return duckdb.query(f"""
            SELECT *
            FROM read_parquet('{DATA_FILE_PATH}')
            LIMIT {limit}
        """).df()

    return duckdb.query(f"""
        SELECT *
        FROM read_parquet('{DATA_FILE_PATH}')
        WHERE lower(name) LIKE lower('%{query}%')
        LIMIT {limit}
    """).df()