import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from plotly.subplots import make_subplots

colors = [
    "#dc267f",
    "#ffb000",
    "#7ad9ff",
    "#fe6100",
    "#785ef0"
]

backgroundColor = "#2A475E"
secondaryBackgroundColor = "#171A21"

highlight_color = "#ffffff"

font_family = "monospace, bold"
font_size = 15
annotation_font_size = 28
font_color = "#ffffff"
grid_color_0 = "rgba(200,200,200,0.05)"
grid_color_1 = "rgba(200,200,200,0.1)"
grid_color_2 = "rgba(200,200,200,0.2)"
grid_color_3 = "rgba(200,200,200,1.0)"

legend_color = "#2A475E"
hover_style = dict(
        bgcolor=backgroundColor,
        bordercolor=grid_color_3,
        align="left",
        namelength=-1,
        font=dict(
            family=font_family,
            size=font_size,
            color=font_color,
            weight="bold"
        )
)

def genre_distribution_chart(df):
    pdf = df.copy()
    pdf = pdf[pdf["name"] != "All"].copy()

    # 2. Ensure numeric values for proportional sizing
    pdf["count"] = pd.to_numeric(pdf["count"], errors="coerce").fillna(0)

    # 3. Sort before computing threshold slices
    pdf = pdf.sort_values("count", ascending=False).reset_index(drop=True)

    total = pdf["count"].sum()
    pdf["share"] = pdf["count"] / total
    pdf["cum_share"] = pdf["share"].cumsum()

    # Calculate individual exact percentage strings for EVERY genre before grouping
    pdf["percentage_str"] = (pdf["count"] / total * 100).round(1).astype(str) + "%"

    # 4. Truncate at 90% threshold and group everything else into "Others"
    cutoff = (pdf["cum_share"] <= 0.90).sum()
    top = pdf.iloc[:cutoff]
    others = pdf.iloc[cutoff:]

    frames = [top]
    if len(others) > 0:
        frames.append(pd.DataFrame({
            "name": ["Others"],
            "count": [others["count"].sum()]
        }))

    pdf_final = pd.concat(frames, ignore_index=True)

    # Combined macro percentages for the chart slices
    total_final = pdf_final["count"].sum()
    pdf_final["percentage_str"] = (pdf_final["count"] / total_final * 100).round(1).astype(str) + "%"

    selected = str(st.session_state.selected_genre).strip().lower()
    names = [str(n).strip().lower() for n in pdf_final["name"]]
    selected_in_top = selected in names

    # 6. Build trace configurations dynamically
    pull = []
    text_templates = []
    border_colors = []
    border_widths = []

    # Track metrics for the center annotation hole
    center_label_text = str(st.session_state.selected_genre).upper()
    center_percentage_text = ""

    if selected == "all":
        center_percentage_text = "100%"
    elif not selected_in_top and selected != "all":
        # Pull the specific sub-genre percentage metrics for the center hole display
        matched_rows = pdf[pdf["name"].str.strip().str.lower() == selected]
        if not matched_rows.empty:
            center_label_text = matched_rows.iloc[0]["name"].upper()
            center_percentage_text = matched_rows.iloc[0]["percentage_str"]
        else:
            center_label_text = "OTHERS"
            center_percentage_text = ""

    for idx, n in enumerate(names):
        # ✨ UPDATED CONDITIONAL:
        # True if it's a direct top match, OR if we selected a sub-genre and this is the "Others" slice
        is_active_selection = (selected == n) or (not selected_in_top and n == "others" and selected != "all")

        if selected == "all":
            pull.append(0)
            text_templates.append("%{label}<br>%{percent}")
            border_colors.append(highlight_color)
            border_widths.append(0)
        elif is_active_selection:
            pull.append(0.12)  # Kept pulled out!

            # ✨ UPDATED: Keep the outer label visible even when pulled if it's the "Others" category
            if n == "others":
                text_templates.append("%{label}<br>%{percent}")
            else:
                text_templates.append("")  # Hide it for normal top slices since it matches center text

            border_colors.append(highlight_color)
            border_widths.append(3)

            # Only override the slice calculation variables if it's a true top-level choice
            if selected == n:
                center_label_text = pdf_final.iloc[idx]["name"].upper()
                center_percentage_text = pdf_final.iloc[idx]["percentage_str"]
        else:
            pull.append(0)
            text_templates.append("%{label}<br>%{percent}")
            border_colors.append("rgba(0,0,0,0)")
            border_widths.append(0)

    unique_genres = [name for name in pdf_final["name"] if name != "Others"]
    custom_color_discrete_map = {}

    # 1. Choose your color scale (e.g., 'Agsunset', 'Plasma', or 'Blugrn')
    # Fetching the hex colors array from Plotly's built-in libraries
    scale_colors = px.colors.sequential.Plasma_r

    # 2. Map colors evenly based on the sorted rank of unique genres
    num_genres = len(unique_genres)
    for i, genre in enumerate(unique_genres):
        if num_genres > 1:
            # Calculate a percentage position (0.0 to 1.0) along the color scale
            scale_position = i / (num_genres - 1)
            # Sample the exact color from that position on the scale
            color = px.colors.sample_colorscale(scale_colors, scale_position)[0]
        else:
            color = scale_colors[0]

        custom_color_discrete_map[genre] = color

    fig = px.pie(
        pdf_final,
        names="name",
        values="count",
        color="name",
        hole=0.8,
        color_discrete_map=custom_color_discrete_map
    )

    fig.update_traces(
        texttemplate=text_templates,
        textposition="outside",
        pull=pull,
        hoverinfo="skip",
        hovertemplate=None,
        textfont=dict(
            size=font_size,
            family=font_family,
            color=font_color
        ),
        domain=dict(x=[0, 1], y=[0, 1]),
        automargin=False,
        marker=dict(
            line=dict(
                color=border_colors,
                width=border_widths
            )
        )
    )

    raw_chunks = center_label_text.split()
    processed_chunks = []

    for chunk in raw_chunks:
        if len(chunk) <= 3 and processed_chunks:
            processed_chunks[-1] = f"{processed_chunks[-1]} {chunk}"
        else:
            processed_chunks.append(chunk)
    center_label_text = "<br>".join(processed_chunks)

    display_string = (
        f"<span>{center_label_text}</span><br>"
        f"<span>{center_percentage_text}</span>"
    )

    fig.update_layout(
        showlegend=False,
        margin=dict(l=60, r=60, t=60, b=60),
        clickmode="event+select",

        annotations=[dict(
            text=display_string,
            x=0.5, y=0.5,
            font_size=annotation_font_size,
            font_family=font_family,
            font_color=font_color,
            showarrow=False,
            align="center"
        )],
        paper_bgcolor="rgba(0,0,0,0)"
    )

    return fig, top["name"], others["name"]


def plot_pricing_distribution_responsive(df: pd.DataFrame):
    if df.empty or "avg_review_score" not in df.columns:
        return None

    # Create 2 stacked rows sharing the same X-axis
    fig = make_subplots(
        rows=2, cols=1,
        shared_xaxes=True,
        vertical_spacing=0.08,  # Spacing between the two plots
        row_heights=[0.7, 0.3],  # Main metrics get more space
        specs=[[{"secondary_y": True}], [{"secondary_y": False}]]  # Keep dual axes only on top row
    )

    # 1. Supply (Row 1, Left Axis - y1)
    fig.add_trace(
        go.Bar(
            x=df["price_tier"],
            y=df["game_count"],
            name="Number of Games (Supply)",
            marker_color=colors[0],
            hovertemplate="<b>Tier:</b> %{x}<br><b>Total Games:</b> %{y:,}<extra></extra>"
        ),
        row=1, col=1, secondary_y=False
    )

    # 2. Demand (Row 1, Right Axis - y2)
    fig.add_trace(
        go.Scatter(
            x=df["price_tier"],
            y=df["avg_owners"],
            name="Avg Owners (Demand)",
            mode="lines+markers",
            line=dict(color=colors[1], width=3),
            marker=dict(size=8),
            hovertemplate="<b>Tier:</b> %{x}<br><b>Avg Owners:</b> %{y:,.0f}<extra></extra>"
        ),
        row=1, col=1, secondary_y=True
    )

    # 3. Quality (Row 2, Left Axis - y3)
    fig.add_trace(
        go.Scatter(
            x=df["price_tier"],
            y=df["avg_review_score"],
            name="Avg Review Score (%)",
            mode="lines+markers",
            line=dict(color=colors[2], width=3, dash="dash"),
            marker=dict(size=8, symbol="diamond"),
            hovertemplate="<b>Tier:</b> %{x}<br><b>Avg Score:</b> %{y:.1f}%<extra></extra>"
        ),
        row=2, col=1
    )

    # Configure Layout with all your explicit styles applied cleanly
    fig.update_layout(
        # X-Axis Styling (Applied to the shared bottom axis)
        xaxis2=dict(
            title=dict(text="Pricing Buckets"),
            tickfont=dict(
                size=font_size,
                family=font_family,
                color=font_color
            ),
            tickmode="linear",
            dtick=1 if len(df) < 15 else 2
        ),

        # Row 1 Left Y-Axis (Supply)
        yaxis=dict(
            title=None,
            tickfont=dict(
                size=font_size,
                family=font_family,
                color=colors[0]
            ),
            gridcolor=grid_color_1,
        ),

        # Row 1 Right Y-Axis (Demand)
        yaxis2=dict(
            title=None,
            showgrid=False,
            tickfont=dict(
                size=font_size,
                family=font_family,
                color=colors[1]
            )
        ),

        # Row 2 Left Y-Axis (Quality Score %)
        yaxis3=dict(
            title=None,
            showgrid=True,
            gridcolor=grid_color_1,
            range=[0, 100],
            tickfont=dict(
                size=font_size,
                family=font_family,
                color=colors[2]
            ),
            ticksuffix="%"
        ),

        # Top-centered Horizontal Legend
        legend=dict(
            orientation="h",
            yanchor="bottom",
            y=1.12,  # Floating safely over the subplots
            xanchor="center",
            x=0.47,
        ),

        # Universal Styling Parameters
        hoverlabel=hover_style,
        plot_bgcolor="rgba(0,0,0,0)",
        paper_bgcolor="rgba(0,0,0,0)",
        margin=dict(l=50, r=50, t=60, b=50)  # Safe container margins for mobile
    )

    return fig

def plot_combined_release_analytics(df: pd.DataFrame):
    fig = go.Figure()

    fig.add_trace(go.Bar(
        x=df["release_year"],
        y=df["game_count"],
        name="Titles Released",
        marker_color=colors[0],
        opacity=0.75,
        yaxis="y1",
        hovertemplate="<b>Year:</b> %{x}<br><b>Games Launched:</b> %{y:,}<extra></extra>",

    ))
    fig.add_trace(go.Scatter(
        x=df["release_year"],
        y=df["avg_revenue_per_game"],
        name="Avg Revenue per Game ($)",
        mode="lines+markers",
        line=dict(color=colors[1], width=3),  # Tied to the right axis color
        marker=dict(size=8, color=colors[1]), # Optional: explicitly color markers to match
        yaxis="y2",
        hovertemplate="<b>Year:</b> %{x}<br><b>Avg Revenue/Game:</b> $%{y:,.0f}<extra></extra>"
    ))

    # Single layout configuration handling both axes simultaneously
    fig.update_layout(
        xaxis=dict(title=dict(text="Release Year"), tickmode="linear", dtick=1 if len(df) < 15 else 2),

        # Left Axis Styling
        yaxis=dict(
            title=None,
            gridcolor=grid_color_1,
            tickfont=dict(
                size=font_size,
                family=font_family,
                color=colors[0]
            )
        ),

        # Right Axis Styling (Completely distinct scale for monetary metrics)
        yaxis2=dict(
            title=None,
            overlaying="y",
            side="right",
            showgrid=False,
            tickfont=dict(
                size=font_size,
                family=font_family,
                color=colors[1]
            )
        ),
        hoverlabel=hover_style,
        plot_bgcolor="rgba(0,0,0,0)",
        paper_bgcolor="rgba(0,0,0,0)",
        legend=dict(
            orientation="h",  # Horizontal span
            yanchor="bottom",
            y=1.12,  # Pushes the legend safely above the plot into the top margin
            xanchor="center",
            x=0.47,
        )
    )

    return fig


def plot_tag_synergies(df: pd.DataFrame, selected_genre: str):
    if df.empty:
        return None

    # Construct clean text fields for rich hover interaction boxes
    df["hover_text"] = (
        "<b>Tag:</b> " + df["secondary_tag"] + "<br>" +
        "<b>Avg Owners:</b> " + df["avg_owners"].map(lambda x: f"{x:,.0f}") + "<br>" +
        "<b>Avg Review Score:</b> " + df["avg_review_score"].map(lambda x: f"{x:.1f}%") + "<br>" +
        "<b>Games:</b> " + df["game_count"].map(lambda x: f"{x:,}")
    )

    fig = go.Figure()

    # Create the bubble matrix profile
    fig.add_trace(go.Scatter(
        x=df["avg_review_score"],
        y=df["avg_owners"],
        mode="markers+text",
        text=df["secondary_tag"],
        textposition="top center",
        textfont=dict(
                size=font_size,
                family=font_family,
                color=font_color
            ),
        marker=dict(
            size=df["game_count"],
            sizemode="area",
            sizeref=2.0 * max(df["game_count"]) / (40.0**2) if max(df["game_count"]) > 0 else 1,
            sizemin=8,
            color=df["game_count"],
            colorscale="Plasma",
            line=dict(color="rgba(255, 255, 255, 0.8)", width=1),
            showscale=True,
            colorbar=dict(
                thickness=15,
                len=1.0,
                ypad=0,
                x=1.05,
                yanchor="middle",
                xanchor="left",
                tickfont=dict(
                    size=font_size,
                    family=font_family,
                    color=font_color
                ),
                tickformat="~s",
                outlinewidth=0,
            ),
        ),
        # FIXED: Pass your formatted array to customdata, then read it via %{customdata}
        customdata=df["hover_text"].tolist(),
        hovertemplate="%{customdata}<extra></extra>"
    ))

    # Add dynamic quadrant target dividing lines based on data slice medians
    median_x = df["avg_review_score"].median()
    median_y = df["avg_owners"].median()

    fig.add_shape(type="line", x0=median_x, y0=0, x1=median_x, y1=max(df["avg_owners"])*1.1,
                  line=dict(color=grid_color_1, width=1, dash="dash"))
    fig.add_shape(type="line", x0=min(df["avg_review_score"])*0.95, y0=median_y, x1=100, y1=median_y,
                  line=dict(color=grid_color_1, width=1, dash="dash"))

    # 1. Calculate symmetrical boundaries for X (Review Score)
    max_dist_x = max(abs(df["avg_review_score"].max() - median_x), abs(median_x - df["avg_review_score"].min()))
    x_range = [median_x - max_dist_x * 1.05, median_x + max_dist_x * 1.2]

    # 2. Calculate symmetrical boundaries for Y (Owners)
    max_dist_y = max(abs(df["avg_owners"].max() - median_y), abs(median_y - df["avg_owners"].min()))
    y_range = [max(0, median_y - max_dist_y * 1.05),
               median_y + max_dist_y * 1.2]  # max(0,...) prevents negative owners scale

    # Polish overall frame design
    fig.update_layout(
        xaxis=dict(
            title=dict(text="Average Review Score (%)"),
            gridcolor=grid_color_0,
            range=x_range
        ),
        yaxis=dict(
            title=dict(text="Average Estimated Owners"),
            gridcolor=grid_color_0,
            range=y_range
        ),
        hoverlabel=hover_style,
        plot_bgcolor="rgba(0,0,0,0)",
        paper_bgcolor="rgba(0,0,0,0)",
        margin=dict(l=40, r=40, t=5, b=40)
    )

    return fig
