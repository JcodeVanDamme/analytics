import streamlit as st
import utils.components as comp
from utils.data import get_total_rows, load_page, search_games
from utils.tag_parser import parse_tags

st.set_page_config(
    page_title="Browse Titles",
    page_icon="🗂️",
    layout="wide"
)

st.title("🗂️ Browse Titles")

PAGE_SIZE = 250

# ---------------------------------------------------
# Dialog
# ---------------------------------------------------
def show_details(row):

    @st.dialog(" ")
    def dialog():

        with st.container(gap="xxsmall"):

            st.title(row["name"])

            st.markdown(
                f"**RELEASED:** **{row.get('release_date', '').upper()}**",
            )
            genres = row.get("genres")

            if len(genres) > 0:
                chips = "".join(
                    f"""
                    <span style="
                        display:inline-block;
                        padding:2px 8px;
                        margin:1px;
                        font-size:14px;
                        font-weight:600;
                        border-radius:3px;
                        background:#1f6feb;
                        color:white;
                        white-space:nowrap;
                        line-height:1;
                    ">{g.upper()}</span>
                    """
                    for g in genres
                )
                st.markdown(
                    f"""
                    <div style="
                        display:flex;
                        flex-wrap:wrap;
                        gap:2px 4px;
                        line-height:1;
                    ">
                        {chips}
                    </div>
                    """,
                    unsafe_allow_html=True
                )

        st.image(row.get("header_image"), use_container_width=True)

        st.write(row.get("short_description"))

        parsed_tags = parse_tags(row.get("tags"))

        if parsed_tags:
            with st.container(gap="xxsmall"):
                st.markdown("**TAGS:**")
                with st.container(horizontal=True, gap="xxsmall"):
                    for tag in parsed_tags[:12]:
                        st.markdown(
                            f"""
                            <span style="
                                display:inline-block;
                                padding:2px 8px;
                                margin:1px;
                                font-size:14px;
                                font-weight:600;
                                border-radius:3px;
                                background:#1f6feb;
                                color:white;
                                white-space:nowrap;
                                line-height:1;
                            ">{tag}</span>
                            """,
                            unsafe_allow_html=True
                        )
    dialog()


# ---------------------------------------------------
# Pagination state
# ---------------------------------------------------
if "page_number_browse" not in st.session_state:
    st.session_state.page_number_browse = 1


# ---------------------------------------------------
# Search state (cleared on page change)
# ---------------------------------------------------
if "search_query" not in st.session_state:
    st.session_state.search_query = ""

def clear_search():
    st.session_state.search_query = ""


# ---------------------------------------------------
# Total data
# ---------------------------------------------------
total_rows = get_total_rows()
total_pages = max(1, (total_rows // PAGE_SIZE) + 1)

page_number_browse = st.session_state.page_number_browse

page_number_browse = max(
    1,
    min(page_number_browse, total_pages)
)

st.session_state.page_number_browse = page_number_browse


# ---------------------------------------------------
# SEARCH INPUT (state-controlled)
# ---------------------------------------------------
st.session_state.search_query = st.text_input(
    "Search...",
    placeholder="Type a name...",
    value=st.session_state.search_query
)

search = st.session_state.search_query


# ---------------------------------------------------
# LOAD DATA (browse page always loaded)
# ---------------------------------------------------
start_idx = (page_number_browse - 1) * PAGE_SIZE
end_idx = min(start_idx + PAGE_SIZE, total_rows)

page_df = load_page(start_idx, end_idx)


# ---------------------------------------------------
# SEARCH RESULTS (shown in addition, NOT replacement)
# ---------------------------------------------------
if search:
    search_df = search_games(search, limit=200)

    st.subheader(f"🔎 Search results for '{search}'")

    if not search_df.empty:
        event_search = st.dataframe(
            search_df[["name"]],
            use_container_width=True,
            hide_index=True,
            on_select="rerun",
            selection_mode="single-cell",
            key="search_table"
        )

        search_cells = event_search.selection["cells"]

        if search_cells:
            row_idx = search_cells[0][0]
            selected_row = search_df.iloc[row_idx]
            show_details(selected_row)
    else:
        st.info("No search results found.")


# ---------------------------------------------------
# PAGE NAVIGATION (clears search)
# ---------------------------------------------------
st.subheader(f"Page {page_number_browse:,} / {total_pages:,}")

col1, col2 = st.columns(2)

with col1:
    if st.button("⬅ Previous", use_container_width=True):
        st.session_state.page_number_browse -= 1
        clear_search()
        st.rerun()

with col2:
    if st.button("Next ➡", use_container_width=True):
        st.session_state.page_number_browse += 1
        clear_search()
        st.rerun()


# ---------------------------------------------------
# MAIN TABLE (always visible)
# ---------------------------------------------------
st.subheader("📄 Browse Results")

event = st.dataframe(
    page_df[["name"]],
    use_container_width=True,
    hide_index=True,
    on_select="rerun",
    selection_mode="single-cell",
    key="browse_table"
)

cells = event.selection["cells"]

if cells:
    row_idx = cells[0][0]
    selected_row = page_df.iloc[row_idx]
    show_details(selected_row)