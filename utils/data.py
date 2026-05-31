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

@st.cache_data
def get_publisher_rank(row):

    publisher = str(row["publishers"])
    game_id = int(row["game_id"])

    query = """
    WITH ranked AS (

        SELECT
            game_id,

            ROW_NUMBER() OVER (
                ORDER BY
                    positive * 1.0 /
                    NULLIF(positive + negative, 0)
                    DESC
            ) AS rank

        FROM read_parquet('data/games.parquet')
        WHERE publishers = ?
    )

    SELECT
        rank,
        (SELECT COUNT(*)
         FROM read_parquet('data/games.parquet')
         WHERE publishers = ?) AS total
    FROM ranked
    WHERE game_id = ?
    """

    result = duckdb.execute(
        query,
        [publisher, publisher, game_id]
    ).fetchone()

    return result


@st.cache_data
def get_genre_rank(row):

    genre = str(row["genres"][0])
    game_id = int(row["game_id"])


    query = """
    WITH ranked AS (

        SELECT
            game_id,

            ROW_NUMBER() OVER (
                ORDER BY
                    positive * 1.0 /
                    NULLIF(positive + negative, 0)
                    DESC
            ) AS rank

        FROM read_parquet('data/games.parquet')
        WHERE list_contains(genres, ?)

    )

    SELECT
        rank,
        (SELECT COUNT(*)
         FROM read_parquet('data/games.parquet')
         WHERE list_contains(genres, ?)) AS total
    FROM ranked
    WHERE game_id = ?
    """

    result = duckdb.execute(
        query,
        [genre, genre, game_id]
    ).fetchone()

    return result

