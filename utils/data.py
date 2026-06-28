import pyarrow.parquet as pq
import duckdb
import streamlit as st
import pandas as pd
from functools import wraps

DATA_PATH = "data/games.parquet"


def custom_loader(message="Processing data..."):
    def decorator(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            placeholder = st.empty()

            # An elegant, hardware-accelerated inline SVG spinner
            spinner_html = f"""
            <div style="display: flex; align-items: center; gap: 12px; padding: 10px 0;">
                <svg width="24" height="24" viewBox="0 0 24 24" xmlns="http://www.w3.org/2000/svg" style="animation: spin 0.8s linear infinite;">
                    <style>
                        @keyframes spin {{ 100% {{ transform: rotate(360deg); }} }}
                    </style>
                    <circle cx="12" cy="12" r="9" stroke="#66C0F4" stroke-width="3" fill="none" stroke-dasharray="36 12" stroke-linecap="round"/>
                </svg>
                <span style="font-family: monospace; font-size: 1.1rem; font-weight: 600;">
                    {message}
                </span>
            </div>
            """

            with placeholder.container():
                st.markdown(spinner_html, unsafe_allow_html=True)
            try:
                return func(*args, **kwargs)
            finally:
                placeholder.empty()

        return wrapper

    return decorator

@st.cache_data(show_spinner=False)
@custom_loader("Fetching Genres...")
def get_genres():
    table = pq.read_table(DATA_PATH)

    con = duckdb.connect()
    con.register("data", table)

    query = """
    WITH parsed_base AS (
        SELECT
            *,
            YEAR(strptime(TRIM(release_date), '%b %d, %Y')) AS r_year,
            (positive::DOUBLE / (positive + negative + 1)) AS positive_ratio,
            (average_playtime_forever / 60.0) AS avg_playtime_hours
        FROM data
    ),

    max_year_cte AS (
        -- ✨ FIXED: Force the maximum evaluation timeline to cap at 2025
        SELECT MAX(r_year) AS max_year FROM parsed_base WHERE r_year < 2026
    ),

    base AS (
        SELECT 
            p.*,
            m.max_year
        FROM parsed_base p, max_year_cte m
        WHERE p.r_year < 2026 -- ✨ FIXED: Filter out any incomplete 2026 raw records
    ),

    exploded AS (
        SELECT
            TRIM(genre) AS genre,
            *
        FROM base,
        UNNEST(genres) AS t(genre)
    ),

    filtered AS (
        SELECT *
        FROM exploded
        WHERE genre IS NOT NULL
          AND genre <> ''
    ),

    genre_stats AS (
        SELECT
            genre AS name,
            COUNT(*) AS count,
            AVG(price) AS avg_price,
            quantile_cont(price, 0.5) AS median_price,
            AVG(positive_ratio) AS avg_positive_ratio,
            AVG(peak_ccu) AS avg_peak_ccu,
            AVG(avg_playtime_hours) AS avg_playtime_hours,
            AVG(recommendations) AS avg_recommendations,

            COUNT(CASE WHEN r_year = max_year THEN 1 END) AS count_cy,
            AVG(CASE WHEN r_year = max_year THEN price END) AS avg_price_cy,
            AVG(CASE WHEN r_year = max_year THEN positive_ratio END) AS avg_positive_ratio_cy,
            AVG(CASE WHEN r_year = max_year THEN peak_ccu END) AS avg_peak_ccu_cy,

            COUNT(CASE WHEN r_year = max_year - 1 THEN 1 END) AS count_ly,
            AVG(CASE WHEN r_year = max_year - 1 THEN price END) AS avg_price_ly,
            AVG(CASE WHEN r_year = max_year - 1 THEN positive_ratio END) AS avg_positive_ratio_ly,
            AVG(CASE WHEN r_year = max_year - 1 THEN peak_ccu END) AS avg_peak_ccu_ly,

            1 AS sort_key
        FROM filtered
        GROUP BY genre
    ),

    all_stats AS (
        SELECT
            'All' AS name,
            COUNT(*) AS count,
            AVG(price) AS avg_price,
            quantile_cont(price, 0.5) AS median_price,
            AVG(positive_ratio) AS avg_positive_ratio,
            AVG(peak_ccu) AS avg_peak_ccu,
            AVG(avg_playtime_hours) AS avg_playtime_hours,
            AVG(recommendations) AS avg_recommendations,

            COUNT(CASE WHEN r_year = max_year THEN 1 END) AS count_cy,
            AVG(CASE WHEN r_year = max_year THEN price END) AS avg_price_cy,
            AVG(CASE WHEN r_year = max_year THEN positive_ratio END) AS avg_positive_ratio_cy,
            AVG(CASE WHEN r_year = max_year THEN peak_ccu END) AS avg_peak_ccu_cy,

            COUNT(CASE WHEN r_year = max_year - 1 THEN 1 END) AS count_ly,
            AVG(CASE WHEN r_year = max_year - 1 THEN price END) AS avg_price_ly,
            AVG(CASE WHEN r_year = max_year - 1 THEN positive_ratio END) AS avg_positive_ratio_ly,
            AVG(CASE WHEN r_year = max_year - 1 THEN peak_ccu END) AS avg_peak_ccu_ly,

            0 AS sort_key
        FROM base
    )

    SELECT
        name,
        count,
        avg_price,
        median_price,
        avg_positive_ratio,
        avg_peak_ccu,
        avg_playtime_hours,
        avg_recommendations,

        (COALESCE(count_cy, 0) - COALESCE(count_ly, 0)) AS delta_titles,
        (COALESCE(avg_price_cy, 0.0) - COALESCE(avg_price_ly, 0.0)) AS delta_price,
        (COALESCE(avg_positive_ratio_cy, 0.0) - COALESCE(avg_positive_ratio_ly, 0.0)) AS delta_ratio,
        (COALESCE(avg_peak_ccu_cy, 0.0) - COALESCE(avg_peak_ccu_ly, 0.0)) AS delta_ccu,

        sort_key
    FROM (
        SELECT * FROM genre_stats
        UNION ALL
        SELECT * FROM all_stats
    )
    ORDER BY sort_key, name
    """

    return con.execute(query).df()


@st.cache_data(show_spinner=False)
@custom_loader("Fetching Genre Tags...")
def get_tags_by_genre(selected_genre: str, min_genre_games: int = 5):
    table = pq.read_table(DATA_PATH)
    con = duckdb.connect()
    con.register("data", table)

    query = """
    -- Step 1: Calculate global baseline frequencies for every tag (using non-reserved alias)
    WITH g_tag_counts AS (
        SELECT 
            TRIM(t.tag) AS tag,
            COUNT(*) AS global_count
        FROM data,
        UNNEST(tags) AS t(tag)
        WHERE tag IS NOT NULL AND tag <> ''
        GROUP BY TRIM(t.tag)
    ),

    -- Step 2: Total number of games on Steam (changed alias to avoid reserved 'global')
    gt_total AS (
        SELECT COUNT(*) AS total_games FROM data
    ),

    -- Step 3: Filter down to the selected genre population
    filtered_genre_games AS (
        SELECT game_id, tags
        FROM data,
        UNNEST(genres) AS g(genre)
        WHERE (? = 'All' OR TRIM(genre) = ?)
    ),

    -- Step 4: Total size of this specific genre
    genre_total AS (
        SELECT COUNT(*) AS total_genre_games FROM filtered_genre_games
    ),

    -- Step 5: Count tags inside this genre slice
    genre_tag_counts AS (
        SELECT 
            TRIM(t.tag) AS tag,
            COUNT(*) AS genre_count
        FROM filtered_genre_games,
        UNNEST(tags) AS t(tag)
        WHERE tag IS NOT NULL AND tag <> ''
        GROUP BY TRIM(t.tag)
    )

    -- Step 6: Combine metrics to find the "Lift Factor"
    SELECT 
        g.tag,
        g.genre_count,
        -- Lift = (% of games with this tag in genre) / (% of games with this tag globally)
        ( (CAST(g.genre_count AS FLOAT) / gen_t.total_genre_games) / 
          (CAST(gl.global_count AS FLOAT) / glob_t.total_games) ) AS lift_factor
    FROM genre_tag_counts g
    JOIN g_tag_counts gl ON g.tag = gl.tag
    CROSS JOIN genre_total gen_t
    CROSS JOIN gt_total glob_t -- <-- FIXED: Uses the updated, safe table names
    WHERE LOWER(g.tag) != LOWER(?)  
      AND g.genre_count >= ?        
    ORDER BY lift_factor DESC, g.genre_count DESC
    LIMIT 30
    """

    df = con.execute(query, [selected_genre, selected_genre, selected_genre, min_genre_games]).df()

    return df["tag"].tolist()

@st.cache_data(show_spinner=False)
@custom_loader("Fetching Number of Titles...")
def get_entries_by_genre(selected_genre: str, num: int = 50):
    table = pq.read_table(DATA_PATH)

    con = duckdb.connect()
    con.register("data", table)

    query = """
    WITH base AS (
        SELECT *
        FROM data
    ),

    all_rows AS (
        SELECT *
        FROM base
        WHERE ? = 'All'
    ),

    genre_rows AS (
        SELECT b.*
        FROM base b,
        UNNEST(b.genres) AS g(genre)
        WHERE ? != 'All'
          AND TRIM(genre) = ?
    ),

    filtered AS (
        SELECT * FROM all_rows
        UNION ALL
        SELECT * FROM genre_rows
    ),

    dedup AS (
        SELECT DISTINCT *
        FROM filtered
    )

    SELECT *
    FROM dedup
    ORDER BY recommendations DESC
    LIMIT ?
    """

    return con.execute(query, [
        selected_genre,
        selected_genre,
        selected_genre,
        num
    ]).df()

def parse_estimated_owners(owner_str: str) -> int:
    """Parses a string range like '100000000 - 200000000' into a single numeric midpoint."""
    if pd.isna(owner_str) or not isinstance(owner_str, str) or '-' not in owner_str:
        return 0
    try:
        # Split by the hyphen, strip whitespace, and convert to integers
        low, high = map(lambda x: int(x.replace(',', '').strip()), owner_str.split('-'))
        return int((low + high) / 2)
    except (ValueError, AttributeError):
        return 0


@st.cache_data(show_spinner=False)
@custom_loader("Fetching Title Metrics...")
def get_metrics_by_order(
    order_by_column: str,
    page,
    page_size,
    ascending,
    genre_filter
) -> list:
    column_mapping = {
        "score": "calculated_score",
        "calculated_score": "calculated_score",
        "name": "name",
        "metacritic_score": "clean_metacritic",
        "average_playtime_hours": "average_playtime_hours",
        "recommendations": "clean_recommendations"
    }

    target_column = column_mapping.get(order_by_column, "calculated_score")

    table = pq.read_table(DATA_PATH)
    con = duckdb.connect()
    con.register("data", table)

    offset = max(0, (page - 1) * page_size)
    direction = "ASC" if ascending else "DESC"

    where_clauses = ["(positive IS NOT NULL OR negative IS NOT NULL)"]
    query_params = []

    # Safe verification to ensure genre_filter is handled cleanly as a string token
    genre_str = str(genre_filter).strip() if genre_filter else "All"

    if genre_str.lower() != "all":
        #  FIXED LINE: Uses array transformation lambda mapping instead of lower() on a VARCHAR[]
        where_clauses.append("list_contains(list_transform(genres, x -> lower(x)), lower(?))")
        query_params.append(genre_str)

    where_sql = " AND ".join(where_clauses)

    query = f"""
    SELECT * FROM (
        SELECT 
            game_id,
            name,
            COALESCE(metacritic_score, 0) AS clean_metacritic,
            publishers,     
            COALESCE(positive, 0) AS pos,
            COALESCE(negative, 0) AS neg,
            COALESCE(recommendations, 0) AS clean_recommendations,
            ((COALESCE(positive, 0)::DOUBLE) / (COALESCE(positive, 0) + COALESCE(negative, 0) + 50)) AS calculated_score,
            (COALESCE(average_playtime_forever, 0)::DOUBLE / 60.0) AS average_playtime_hours,
            estimated_owners
        FROM data
        WHERE {where_sql}
    ) AS evaluated_data
    ORDER BY {target_column} {direction}
    LIMIT {page_size} OFFSET {offset}
    """

    df = con.execute(query, query_params).df()

    if df.empty:
        return []

    results = []
    for _, row in df.iterrows():
        owners_str = str(row["estimated_owners"]) if not pd.isna(row["estimated_owners"]) else "0 - 0"
        try:
            parts = owners_str.split("-")
            max_owners = int(parts[1].strip().replace(",", "")) if len(parts) > 1 else int(parts[0].strip().replace(",", ""))
        except (ValueError, IndexError):
            max_owners = 0

        raw_publishers = row["publishers"]
        if hasattr(raw_publishers, "__len__") and not isinstance(raw_publishers, (str, bytes)):
            publishers_list = list(raw_publishers)
        elif isinstance(raw_publishers, (float, int)) and pd.isna(raw_publishers):
            publishers_list = []
        else:
            val_str = str(raw_publishers).strip()
            publishers_list = [val_str] if val_str and val_str.lower() not in ("none", "nan", "") else []

        results.append({
            "title_name": row["name"],
            "metrics": {
                "game_id": int(row["game_id"]),
                "metacritic_score": int(row["clean_metacritic"]) if row["clean_metacritic"] > 0 else None,
                "publishers": publishers_list,
                "score": round(float(row["calculated_score"]), 4),
                "average_playtime_hours": round(float(row["average_playtime_hours"]), 2),
                "max_owners": max_owners,
                "recommendations": int(row["clean_recommendations"])
            }
        })

    return results


@st.cache_data(show_spinner=False)
@custom_loader("Fetching Release Data...")
def get_titles_by_genre_year_range(selected_genre: str) -> dict:
    # 1. Load the parquet table
    table = pq.read_table(DATA_PATH)

    # 2. Connect to DuckDB and register the table
    con = duckdb.connect()
    con.register("data", table)

    query = """
    WITH base AS (
        SELECT 
            *,
            -- Centralize date parsing logic using fixed %d format
            YEAR(strptime(TRIM(release_date), '%b %d, %Y')) AS release_year
        FROM data
        WHERE release_date IS NOT NULL AND release_date <> ''
    ),

    -- 1. FLATTEN GENRES AND APPLY THE FILTER (Uses the 2 '?' placeholders)
    filtered_genre AS (
        SELECT release_year
        FROM base,
        UNNEST(genres) AS g(genre)
        WHERE (? = 'All' OR TRIM(genre) = ?)
    ),

    -- 2. Calculate the min and max year for that specific genre
    bounds AS (
        SELECT 
            MIN(release_year) AS min_year, 
            MAX(release_year) AS max_year 
        FROM filtered_genre
    ),

    -- 3. Filter the dataset to include titles within that range
    names_in_range AS (
        SELECT 
            b.release_year,
            TRIM(b.name) AS name
        FROM base b
        CROSS JOIN bounds o
        WHERE b.release_year BETWEEN o.min_year AND o.max_year
          AND b.name IS NOT NULL 
          AND b.name <> ''
    )

    -- 4. Group by year, count total rows per year, and aggregate titles into a list
    SELECT 
        release_year,
        COUNT(*) AS total_count,
        LIST(name) AS titles
    FROM names_in_range
    GROUP BY release_year
    ORDER BY release_year DESC
    """

    # 3. Execute query
    df = con.execute(query, [selected_genre, selected_genre]).df()

    # 4. Construct the dictionary with nested metadata: { year: {"count": X, "titles": [...] } }
    output = {}
    for _, row in df.iterrows():
        output[int(row["release_year"])] = {
            "count": int(row["total_count"]),
            "titles": row["titles"]
        }

    return output


@st.cache_data(show_spinner=False)
@custom_loader("Fetching Title Margins...")
def get_pricing_tiers_by_genre(selected_genre: str) -> pd.DataFrame:
    table = pq.read_table(DATA_PATH)
    con = duckdb.connect()
    con.register("data", table)

    query = """
    WITH base AS (
        SELECT 
            *,
            CAST(price AS FLOAT) AS clean_price,
            CAST(positive AS FLOAT) AS pos,
            CAST(negative AS FLOAT) AS neg
        FROM data
        WHERE price IS NOT NULL
          AND positive IS NOT NULL 
          AND negative IS NOT NULL
    ),

    filtered_genre AS (
        SELECT clean_price, estimated_owners, pos, neg
        FROM base,
        UNNEST(genres) AS g(genre)
        WHERE (? = 'All' OR TRIM(genre) = ?)
    ),

    binned_data AS (
        SELECT 
            CAST(TRIM(SPLIT_PART(estimated_owners, '-', 1)) AS BIGINT) AS clean_owners,
            -- Calculate score ratio inline, handle zero division safety
        CASE 
            WHEN (pos + neg) > 0 THEN (pos * 100.0) / (pos + neg)
            ELSE NULL 
        END AS clean_score,

            CASE 
                WHEN clean_price = 0 THEN 'Free'
                WHEN clean_price > 0 AND clean_price <= 4.99 THEN '$0.01 - $4.99'
                WHEN clean_price >= 5.00 AND clean_price <= 9.99 THEN '$5.00 - $9.99'
                WHEN clean_price >= 10.00 AND clean_price <= 14.99 THEN '$10.00 - $14.99'
                WHEN clean_price >= 15.00 AND clean_price <= 19.99 THEN '$15.00 - $19.99'
                WHEN clean_price >= 20.00 AND clean_price <= 29.99 THEN '$20.00 - $29.99'
                WHEN clean_price >= 30.00 AND clean_price <= 39.99 THEN '$30.00 - $39.99'
                WHEN clean_price >= 40.00 AND clean_price <= 59.99 THEN '$40.00 - $59.99'
                ELSE '$60.00+' 
            END AS price_tier,
            CASE 
                WHEN clean_price = 0 THEN 0
                WHEN clean_price > 0 AND clean_price <= 4.99 THEN 1
                WHEN clean_price >= 5.00 AND clean_price <= 9.99 THEN 2
                WHEN clean_price >= 10.00 AND clean_price <= 14.99 THEN 3
                WHEN clean_price >= 15.00 AND clean_price <= 19.99 THEN 4
                WHEN clean_price >= 20.00 AND clean_price <= 29.99 THEN 5
                WHEN clean_price >= 30.00 AND clean_price <= 39.99 THEN 6
                WHEN clean_price >= 40.00 AND clean_price <= 59.99 THEN 7
                ELSE 8 
            END AS sort_order
        FROM filtered_genre
        WHERE estimated_owners IS NOT NULL AND estimated_owners LIKE '%-%'
    )

    SELECT 
        price_tier,
        COUNT(*) AS game_count,
        AVG(clean_owners) AS avg_owners,
        -- Average the clean deduced percentages, ignoring NULL entries
        AVG(clean_score) AS avg_review_score,
        sort_order
    FROM binned_data
    GROUP BY price_tier, sort_order
    ORDER BY sort_order ASC
    """

    return con.execute(query, [selected_genre, selected_genre]).df()

@st.cache_data(show_spinner=False)
@custom_loader("Fetching Tag Synergies...")
def get_tag_synergies_by_genre(
    selected_genre: str,
    min_games_threshold: int = 5,
    max_tags: int = 20  # 👈 1. Added parameter with a default fallback of 20
) -> pd.DataFrame:
    table = pq.read_table(DATA_PATH)
    con = duckdb.connect()
    con.register("data", table)

    query = """
    WITH base AS (
        SELECT 
            game_id,               
            genres,
            tags,
            CAST(positive AS FLOAT) AS pos,
            CAST(negative AS FLOAT) AS neg,
            CAST(TRIM(SPLIT_PART(estimated_owners, '-', 1)) AS BIGINT) AS clean_owners
        FROM data
        WHERE estimated_owners IS NOT NULL 
          AND estimated_owners LIKE '%-%'
          AND positive IS NOT NULL
          AND negative IS NOT NULL
    ),

    genre_filtered_games AS (
        SELECT game_id, tags, clean_owners, pos, neg 
        FROM base,
        UNNEST(genres) AS g(genre)
        WHERE (? = 'All' OR TRIM(genre) = ?)
    ),

    unnested_tags AS (
        SELECT 
            game_id,              
            TRIM(t.tag) AS secondary_tag,
            clean_owners,
            CASE 
                WHEN (pos + neg) > 0 THEN (pos * 100.0) / (pos + neg)
                ELSE NULL
            END AS review_score
        FROM genre_filtered_games,
        UNNEST(tags) AS t(tag)
    )

    SELECT 
        secondary_tag,
        COUNT(DISTINCT game_id) AS game_count, 
        AVG(clean_owners) AS avg_owners,
        AVG(review_score) AS avg_review_score
    FROM unnested_tags
    WHERE LOWER(secondary_tag) != LOWER(?) 
      AND secondary_tag != ''
    GROUP BY secondary_tag
    HAVING COUNT(DISTINCT game_id) >= ? 
    ORDER BY avg_owners DESC
    LIMIT ?  -- 👈 2. Swapped out the hardcoded limit string for a parameter placeholder
    """

    # 3. Appended max_tags safely to the parameters array passed down to DuckDB
    params = [selected_genre, selected_genre, selected_genre, min_games_threshold, max_tags]
    return con.execute(query, params).df()

@st.cache_data(show_spinner=False)
@custom_loader("Fetching Release History...")
def get_release_history_analysis(selected_genre: str) -> pd.DataFrame:
    table = pq.read_table(DATA_PATH)
    con = duckdb.connect()
    con.register("data", table)

    query = """
    WITH base AS (
        SELECT 
            YEAR(STRPTIME(release_date, '%b %d, %Y')) AS release_year,
            CAST(price AS FLOAT) AS clean_price,
            CAST(TRIM(SPLIT_PART(estimated_owners, '-', 1)) AS BIGINT) AS clean_owners,
            genres 
        FROM data
        WHERE release_date IS NOT NULL 
          AND price IS NOT NULL
          AND estimated_owners IS NOT NULL 
          AND estimated_owners LIKE '%-%'
    ),

    filtered_genre AS (
        SELECT release_year, clean_price, clean_owners,
               (clean_price * clean_owners) AS estimated_game_revenue
        FROM base,
        UNNEST(genres) AS g(genre) 
        WHERE (? = 'All' OR TRIM(genre) = ?)
          -- ✨ FIXED: Terminate the line series boundary at 2025 to strip out incomplete data
          AND release_year BETWEEN 2010 AND 2025 
    )

    SELECT 
        release_year,
        COUNT(*) AS game_count,
        AVG(estimated_game_revenue) AS avg_revenue_per_game,
        MEDIAN(estimated_game_revenue) AS median_revenue_per_game
    FROM filtered_genre
    GROUP BY release_year
    ORDER BY release_year ASC
    """

    return con.execute(query, [selected_genre, selected_genre]).df()


@st.cache_data(show_spinner=False)
@custom_loader("Fetching Game Tags...")
def get_tags_for_game(title_id: int) -> list:
    """
    Reads the dataset and returns a clean list of all tags associated with a specific game_id.
    Safely avoids array-element truth value check exceptions.
    """
    table = pq.read_table(DATA_PATH)
    con = duckdb.connect()
    con.register("data", table)

    query = """
    SELECT tags 
    FROM data 
    WHERE game_id = ?::BIGINT
    LIMIT 1
    """

    df = con.execute(query, [title_id]).df()

    # 1. First, check if the query returned absolutely nothing
    if df.empty:
        return []

    raw_tags = df.iloc[0]["tags"]

    # 2. Check if the cell is completely empty/None (Handles base None/Null types safely)
    if raw_tags is None:
        return []

    # 3. --- Robust Parsing Block ---
    # Handle case where DuckDB/PyArrow reads it directly as an array or iterable sequence
    if hasattr(raw_tags, "__len__") and not isinstance(raw_tags, (str, bytes)):
        return [str(tag).strip() for tag in raw_tags if str(tag).strip()]

    # Handle case where it is a standalone float/int NaN (Scalar value check only)
    elif isinstance(raw_tags, (float, int)):
        return []

    # Handle case where tags are stored as a string or stringified JSON array
    elif isinstance(raw_tags, str):
        clean_str = raw_tags.strip("[]'\" ")
        if not clean_str:
            return []
        return [tag.strip() for tag in clean_str.split(",") if tag.strip()]

    return []


@st.cache_data(show_spinner=False)
@custom_loader("Fetching All-Time-Hits...")
def get_all_time_genre_leaders(genre_filter: str) -> dict:
    """Fetches the absolute highest-ranking single games across the entire genre."""
    table = pq.read_table(DATA_PATH)
    con = duckdb.connect()
    con.register("data", table)

    genre_str = str(genre_filter).strip() if genre_filter else "All"
    where_clauses = ["(positive IS NOT NULL OR negative IS NOT NULL)"]
    query_params = []

    if genre_str.lower() != "all":
        where_clauses.append("list_contains(list_transform(genres, x -> lower(x)), lower(?))")
        query_params.append(genre_str)

    where_sql = " AND ".join(where_clauses)

    # Subquery pre-calculates uniform metrics across the whole table slice
    base_query = f"""
    WITH processed_data AS (
        SELECT 
            name,
            ((COALESCE(positive, 0)::DOUBLE) / (COALESCE(positive, 0) + COALESCE(negative, 0) + 50)) AS calculated_score,
            (COALESCE(average_playtime_forever, 0)::DOUBLE / 60.0) AS average_playtime_hours,
            estimated_owners
        FROM data
        WHERE {where_sql}
    )
    """

    # 1. Fetch highest calculated score title
    fav_df = con.execute(
        f"{base_query} SELECT name, calculated_score FROM processed_data ORDER BY calculated_score DESC LIMIT 1",
        query_params).df()

    # 2. Fetch highest playtime title
    play_df = con.execute(
        f"{base_query} SELECT name, average_playtime_hours FROM processed_data ORDER BY average_playtime_hours DESC LIMIT 1",
        query_params).df()

    # 3. Fetch highest owner title (midpoint parsed directly in SQL)
    owner_query = f"""
    {base_query}
    SELECT name, estimated_owners,
           CAST(TRIM(SPLIT_PART(estimated_owners, '-', 1)) AS BIGINT) AS low_owners,
           CAST(TRIM(SPLIT_PART(estimated_owners, '-', 2)) AS BIGINT) AS high_owners
    FROM processed_data
    WHERE estimated_owners LIKE '%-%'
    ORDER BY (low_owners + high_owners) / 2 DESC
    LIMIT 1
    """
    titan_df = con.execute(owner_query, query_params).df()

    # Parse max_owners out of the raw tier bracket text string safely
    if not titan_df.empty:
        owners_str = str(titan_df.iloc[0]["estimated_owners"])
        try:
            max_owners = int(owners_str.split("-")[1].strip().replace(",", ""))
        except:
            max_owners = 0
    else:
        max_owners = 0

    return {
        "titan_name": titan_df.iloc[0]["name"] if not titan_df.empty else "N/A",
        "max_owners": max_owners,
        "favorite_name": fav_df.iloc[0]["name"] if not fav_df.empty else "N/A",
        "top_score": float(fav_df.iloc[0]["calculated_score"]) if not fav_df.empty else 0.0,
        "retention_name": play_df.iloc[0]["name"] if not play_df.empty else "N/A",
        "top_playtime": float(play_df.iloc[0]["average_playtime_hours"]) if not play_df.empty else 0.0
    }
