import streamlit as st
import pandas as pd

from utils.charts import genre_distribution_chart, plot_tag_synergies, plot_combined_release_analytics, plot_pricing_distribution_responsive
from utils.data import get_genres, get_tags_by_genre, get_metrics_by_order, get_pricing_tiers_by_genre, get_tag_synergies_by_genre, get_release_history_analysis, get_tags_for_game, get_all_time_genre_leaders
from utils.style import apply_global, heading, subheading, write, style_containers, suss_heading
from utils.texts import texts, tooltips
from utils.metrics import pricing_tier_metrics, saturation_metrics, synergie_metrics, title_metrics
st.set_page_config(
    page_title="Steam Analytics",
    layout="wide"
)

container_id = 0
apply_global()

# SESSION STATE
if "selected_genre" not in st.session_state:
    st.session_state.selected_genre = "All"

if "top_page" not in st.session_state:
    st.session_state.top_page = 1

if "synergy_max_tags" not in st.session_state:
    st.session_state.synergy_max_tags = 10

page_size = 10

def next_page():
    st.session_state.top_page += 1

def prev_page():
    if st.session_state.top_page > 1:
        st.session_state.top_page -= 1


if "top_order" not in st.session_state:
    st.session_state.top_order = "metacritic_score"

genre_df = get_genres()
genre_fig, top_genres, other_genres = genre_distribution_chart(genre_df)

heading("steam analytics",)
st.markdown("<a id='start' style='scroll-margin-top: 300px;'></a>", unsafe_allow_html=True)

write("Welcome to Steam Analytics. This dashboard parses industry data to uncover crossover trends, competitive baselines, and commercial gaps across desired market ranges.")
write("**How to use this tool:** Use the sidebar filters to isolate specific genre profiles.")
write("The evaluation metrics below will dynamically calculate market saturation, consumer acquisition ceilings, optimal retail pricing brackets and other KPIs.")

st.divider()

st.write("")
st.write("")

with st.sidebar:

    with st.expander("Navigation", expanded=False):
        def jump_to(target_id):
            """Executes JS to smoothly scroll the parent window to the target ID."""
            js = f"""
            <script>
                var el = window.parent.document.getElementById("{target_id}");
                if (el) {{
                    el.scrollIntoView({{behavior: "auto", block: "start"}});
                }}
            </script>
            """
            # Inserting this tiny component instantly triggers the JS execution
            st.components.v1.html(js, height=0, width=0)

        st.button(
            "Market Distribution",
            on_click=jump_to,
            args=("start",),
            use_container_width=True
        )
        st.button(
            "Market Trends",
            on_click=jump_to,
            args=("mid",),
            use_container_width=True
        )
        st.button(
            "Top Titles",
            on_click=jump_to,
            args=("end",),
            use_container_width=True
        )

    heading("Genre filter")


    def select_genre_callback(genre_target):
        st.session_state.selected_genre = genre_target
        st.session_state.top_page = 1


    # Current normalized selection state
    current_selection = str(st.session_state.selected_genre).strip().lower()

    # 1. Master "Select All" Button (styled exactly like the others)
    is_all_active = (current_selection == "all")
    st.button(
        "Select All",
        key="btn_select_all_genres",
        type="primary" if is_all_active else "secondary",
        use_container_width=True,
        on_click=select_genre_callback,
        args=("All",)
    )

    st.write("")  # Micro spacer line

    # 2. Expander 1: Top Core Performers
    with st.expander("Top Genres", expanded=True):
        for genre_name in top_genres:
            # Recalculate precisely for each distinct item row iteration
            is_active = (current_selection == str(genre_name).strip().lower())

            st.button(
                f"{genre_name}",
                key=f"list_top_{genre_name}",
                type="primary" if is_active else "secondary",
                width='stretch',
                on_click=select_genre_callback,
                args=(genre_name,)
            )

    # 3. Expander 2: Long-Tail Categories
    with st.expander("Other Genres", expanded=True):
        for genre_name in other_genres:
            # 🛠️ FIX: Explicitly recalculate is_active here so it doesn't leak from the top loop!
            is_active = (current_selection == str(genre_name).strip().lower())

            st.button(
                f"{genre_name}",
                key=f"list_other_{genre_name}",
                type="primary" if is_active else "secondary",
                width='stretch',
                on_click=select_genre_callback,
                args=(genre_name,)
            )

# Pull active row variables below it safely
genre = genre_df[genre_df["name"] == st.session_state.selected_genre].iloc[0].to_dict()


# GENRE SELECTION

genre = genre_df[genre_df["name"] == st.session_state.selected_genre].iloc[0].to_dict()

# PIE CHART *************************************************************************************

with st.container(border=True, key=f"game_card_{container_id}"):
    container_id += 1
    subheading("Genre Distribution")
    write(texts["pie_description"])
    st.plotly_chart(genre_fig, width='stretch', key="distribution")

# KPIS *****************************************************************************************

# --- RENDER THE BORDERED 2X2 GRID ---
row1_col1, row1_col2 = st.columns(2)
row2_col1, row2_col2 = st.columns(2)

# --- ROW 1 ---
with row1_col1:
    with st.container(border=True, horizontal=True, key=f"game_card_{container_id}"):
        container_id += 1
        st.metric(
            label="Titles",
            value=f"{int(genre['count']):,}",
            delta=f"{int(genre['delta_titles']):+,} vs last year" if genre['delta_titles'] != 0 else None,
            help=tooltips["titles"]
        )

with row1_col2:
    with st.container(border=True, horizontal=True, key=f"game_card_{container_id}"):
        container_id += 1
        st.metric(
            label="Avg Price",
            value=f"{genre['avg_price']:.2f} €",
            delta=f"{genre['delta_price']:+.2f} € vs last year" if genre['delta_price'] != 0 else None,
            help=tooltips["price"]
        )

# --- ROW 2 ---
with row2_col1:
    with st.container(border=True, horizontal=True, key=f"game_card_{container_id}"):
        container_id += 1
        st.metric(
            label="Positive Ratio",
            value=f"{genre['avg_positive_ratio']:.2%}",
            delta=f"{genre['delta_ratio']:+.2%} vs last year" if genre['delta_ratio'] != 0 else None,
            help=tooltips["positive_ratio"]
        )

with row2_col2:
    with st.container(border=True, horizontal=True, key=f"game_card_{container_id}"):
        container_id += 1
        st.metric(
            label="Avg CCU",
            value=f"{genre['avg_peak_ccu']:.0f}",
            delta=f"{int(genre['delta_ccu']):+,} vs last year" if genre['delta_ccu'] != 0 else None,
            help=tooltips["peak_ccu"]
        )


# TAGS *************************************************************************************
top_n_tags = 10

tags = get_tags_by_genre(genre["name"])
top_tags = tags[:top_n_tags]

with st.container(border=True, key=f"game_card_{container_id}"):
    container_id += 1

    st.markdown(
        "<p style='text-transform: uppercase; letter-spacing:  0.08em;'>Top Tags</p>",
        unsafe_allow_html=True)

    with st.container(horizontal=True):
        for tag in (top_tags):
            st.badge(tag)

# Trend *************************************************************************************

st.write("")
heading("Market Trends")
st.markdown("<a id='mid' style='scroll-margin-top: 300px;'></a>", unsafe_allow_html=True)

with st.container(border=True, key=f"game_card_{container_id}"):
    container_id += 1

    subheading("Satuation vs Payout")
    write(texts["saturation_vs_payout"])

    release_history_data = get_release_history_analysis(genre["name"])
    st.plotly_chart(plot_combined_release_analytics(release_history_data),  key="market")

    saturation_metrics(release_history_data)

    st.divider()

    subheading("Pricing Tiers")
    write(texts["pricing_tiers"])

    pricing_df = get_pricing_tiers_by_genre(genre["name"])
    st.plotly_chart(plot_pricing_distribution_responsive(pricing_df))

    pricing_tier_metrics(pricing_df)

    st.divider()

    subheading("Tag Synergy")
    write(texts["tag_synergies"])

    st.write("")

    config_col, spacer_col = st.columns([2.0, 3.0])
    with config_col:
        st.slider(
            "Max Tags to Display",
            min_value=5,
            max_value=40,
            step=5,
            key="synergy_max_tags"
        )

    synergy_df = get_tag_synergies_by_genre(
        genre["name"],
        min_games_threshold=8,
        max_tags=st.session_state.synergy_max_tags
    )

    fig = plot_tag_synergies(synergy_df, genre["name"])
    if fig is not None:
        st.plotly_chart(fig, width='stretch')
    else:
        st.info("Not enough tag synergy data matches your current filtering criteria.")

    synergie_metrics(synergy_df)


st.write("")
heading(f"Top Games in {genre["name"]}")
st.markdown("<a id='end' style='scroll-margin-top: 300px;'></a>", unsafe_allow_html=True)

with st.container(border=True, key=f"game_card_{container_id}"):
    container_id += 1
    title_metrics(get_all_time_genre_leaders(genre["name"]))

st.write("")
st.write("")

display_mapping = {
    "Metacritic Score": "metacritic_score",
    "User Score": "score",
    "Average Playtime": "average_playtime_hours",
    "Max Owners": "max_owners",
    "Recommendations": "recommendations"  # 👈 Added recommendations here too!
}

# Find the index of the currently saved session state so the selectbox doesn't reset on refresh
current_index = 0
if "top_order" in st.session_state:
    # Get the display name corresponding to the current state value
    current_display = [k for k, v in display_mapping.items() if v == st.session_state.top_order]
    if current_display:
        current_index = list(display_mapping.keys()).index(current_display[0])

selector_col, spacer_col = st.columns([5.0, 3.5])
with selector_col:
    # Create two internal columns inside the selector column
    # Adjust the ratios [1, 1] if you want the text or dropdown to take up more relative space
    inner_text_col, inner_dropdown_col = st.columns([1, 1])

    with inner_text_col:
        # Markdown spacing adjustment to align the text vertically with the dropdown input
        st.write("<div style='margin-top: 28px;'></div>", unsafe_allow_html=True)

        # Calculate dynamic page ranks cleanly
        start_range = ((st.session_state.top_page * page_size) - page_size) + 1
        end_range = (start_range + page_size) - 1

        subheading(f"Showing Titles {start_range} - {end_range}")

    def reset_pagination():
        st.session_state.top_page = 1

    with inner_dropdown_col:
        selected_display = st.selectbox(
            "Order By",
            options=list(display_mapping.keys()),
            index=current_index,
            key="titles",
            on_change=reset_pagination
        )

# Update the session state with the internal database key name
st.session_state.top_order = display_mapping[selected_display]

# 2. Fetch the data using the session state variables
games_data = get_metrics_by_order(
    order_by_column=st.session_state.top_order,
    page=st.session_state.top_page,
    page_size=page_size,
    ascending=False,
    genre_filter=genre["name"]
)

start_rank = ((st.session_state.top_page - 1) * page_size) + 1

for idx, game in enumerate(games_data, start=start_rank):
    metrics = game["metrics"]

    # Unique card key using state configurations to prevent rendering clashes
    card_key = f"game_card_{st.session_state.top_order}_{st.session_state.top_page}_{container_id}"

    with st.container(border=True, key=f"game_card_{container_id}", gap="xxsmall"):
        container_id += 1

        col1, col2 = st.columns([1.5, 3.5], gap="medium")

        with col1:
            # Header Row
            subheading(f"#{idx} {game['title_name']}")

            # Sub-header meta line for publishers
            if metrics["publishers"]:
                pub_text = ", ".join(metrics["publishers"])
                suss_heading(f"Publishers: {pub_text}")

        with col2:
            # Responsive Metric Grid
            # On desktop, this yields 4 elegant columns. On mobile, Streamlit auto-stacks these vertically.
            m1, m2, m3, m4, m5 = st.columns(5)


            def get_score_badge(score_out_of_100, is_meta=False):
                # 1. Safely catch missing or zero data
                if score_out_of_100 is None or pd.isna(score_out_of_100) or score_out_of_100 == 0:
                    return

                # 2. Treat both scales identically as numbers from 0 to 100
                if score_out_of_100 >= 75.0:
                    st.badge("Positive", color="green")
                elif score_out_of_100 >= 50.0:
                    st.badge("Mixed", color="orange")
                else:
                    st.badge("Bad", color="red")

            with m1:
                score_pct = metrics["score"] * 100
                st.metric(
                    label="User Score",
                    value=f"{score_pct:.1f}%",
                    help=tooltips["score"]
                )
                get_score_badge(score_pct, False)

            with m2:
                meta = metrics["metacritic_score"]
                st.metric(
                    label="Metacritic Score",
                    value=str(meta) if meta else "N/A",
                    help=tooltips["metacritic"]
                )
                get_score_badge(meta, True)

            with m3:
                hours_int = int(metrics['average_playtime_hours'])

                st.metric(
                    label="Avg Playtime",
                    value=f"{hours_int:,} hrs",
                    help=tooltips["playtime"]
                )

            def format_abbreviated_number(val) -> str:
                if not val or pd.isna(val):
                    return "0"

                val = float(val)
                if val >= 1_000_000:
                    return f"{val / 1_000_000:.1f}M".replace(".0M", "M")
                elif val >= 1_000:
                    return f"{val / 1_000:.0f}K"
                return str(int(val))

            with m4:
                st.metric(
                    label="Est. Max Owners",
                    value=format_abbreviated_number(metrics['max_owners']),
                    help=tooltips["owners"]
                )
            with m5:
                st.metric(
                    label="Recommendations",
                    value=format_abbreviated_number(metrics['recommendations']),
                    help=tooltips["recommendations"]
                )

        st.divider()  # Light structural separator inside the card

        title_tags = get_tags_for_game(metrics['game_id'])
        with st.container(horizontal=True):
            for tag in (title_tags):
                st.badge(tag)

col_prev, col_next = st.columns([0.5, 0.5])
with col_prev:
    is_first_page = (st.session_state.top_page <= 1)
    st.button("Previous Titles", on_click=prev_page, disabled=is_first_page, width='stretch', key="Prev")

with col_next:
    st.button("Next Titles", on_click=next_page, width='stretch', key="Next")

st.caption(f"Showing page **{st.session_state.top_page}**")

style_containers(container_id)



