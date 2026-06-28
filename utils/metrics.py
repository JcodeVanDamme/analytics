import streamlit as st

def saturation_metrics(release_history_data):
    if len(release_history_data) >= 2:
        last_year = release_history_data.iloc[-1]
        prev_year = release_history_data.iloc[-2]

        if last_year["game_count"] > prev_year["game_count"] and last_year["avg_revenue_per_game"] < prev_year[
            "avg_revenue_per_game"]:
            st.error(
                "**Market Warning:** This genre is currently experiencing rising saturation with declining average returns per game."
            )
        else:
            st.success(
                "**Market Health:** Revenue per game is scaling efficiently alongside new competitor entries. This market segment remains healthy."
            )
    else:
        st.info(
            "**Market Insight:** Insufficient historical volume available to compute a reliable macro baseline trend for this specific selection.")
def pricing_tier_metrics(pricing_df):

    if not pricing_df.empty and pricing_df["game_count"].sum() > 0:
        # 1. Identify key milestones via data slices
        highest_supply_row = pricing_df.loc[pricing_df["game_count"].idxmax()]
        highest_demand_row = pricing_df.loc[pricing_df["avg_owners"].idxmax()]

        # Filter out tiers with zero or negligible games to find the true quality peak
        valid_quality_df = pricing_df[pricing_df["game_count"] >= 3]
        if not valid_quality_df.empty:
            highest_quality_row = valid_quality_df.loc[valid_quality_df["avg_review_score"].idxmax()]
        else:
            highest_quality_row = pricing_df.loc[pricing_df["avg_review_score"].idxmax()]

        # 2. Build the narrative layout using columns
        st.write("")  # Spacing
        metric_col1, metric_col2, metric_col3 = st.columns(3)

        with metric_col1:
            st.markdown(
                f"""
                <div style="background-color: rgba(220, 38, 127, 0.08); padding: 12px; border-left: 4px solid #dc267f; border-radius: 4px;">
                    <b style="color: #dc267f; font-size: 0.9rem; text-transform: uppercase;">Peak Market Supply</b><br>
                    <span style="font-size: 1.3rem; font-weight: bold;">{highest_supply_row['price_tier']}</span><br>
                    <span style="font-size: 0.85rem; color: #808495;">
                        Populated by <b>{highest_supply_row['game_count']:,}</b> active titles. This is the baseline pricing standard for this space.
                    </span>
                </div>
                """,
                unsafe_allow_html=True
            )

        with metric_col2:
            st.markdown(
                f"""
                <div style="background-color: rgba(255, 176, 0, 0.08); padding: 12px; border-left: 4px solid #ffb000; border-radius: 4px;">
                    <b style="color: #ffb000; font-size: 0.9rem; text-transform: uppercase;">Peak Player Acquisition</b><br>
                    <span style="font-size: 1.3rem; font-weight: bold;">{highest_demand_row['price_tier']}</span><br>
                    <span style="font-size: 0.85rem; color: #808495;">
                        Averages <b>{highest_demand_row['avg_owners']:,.0f}</b> estimated owners per title, indicating maximum consumer willingness to convert.
                    </span>
                </div>
                """,
                unsafe_allow_html=True
            )

        with metric_col3:
            st.markdown(
                f"""
                <div style="background-color: rgba(122, 217, 255, 0.08); padding: 12px; border-left: 4px solid #7ad9ff; border-radius: 4px;">
                    <b style="color: #38bdf8; font-size: 0.9rem; text-transform: uppercase;">Peak Player Satisfaction</b><br>
                    <span style="font-size: 1.3rem; font-weight: bold;">{highest_quality_row['price_tier']}</span><br>
                    <span style="font-size: 0.85rem; color: #808495;">
                        Boasts an average review score of <b>{highest_quality_row['avg_review_score']:.1f}%</b>, reflecting optimal perceived value-for-money.
                    </span>
                </div>
                """,
                unsafe_allow_html=True
            )

        st.write("")

        # 3. Structural Context Overlay (The Contextual Wrap-Up)
        if highest_supply_row["price_tier"] != highest_demand_row["price_tier"]:
            st.info(
                f"**Strategic Tension Detected:** While competitor supply is heavily dense in the {highest_supply_row['price_tier']} bracket, "
                f"historical performance indicates player acquisition actually peaks significantly higher in the {highest_demand_row['price_tier']} range. "
                "There may be an under-supplied premium gap in this genre."
            )
        else:
            st.success(
                f"**Market Equilibrium:** The volume of developer supply perfectly aligns with player conversion trends in the {highest_supply_row['price_tier']} tier, "
                "making it the safest—but most highly contested—bracket to enter."
            )
    else:
        st.info(
            "**Not Enough Pricing Information:** There are currently insufficient historical baseline records "
            "within this specific genre configuration to build a reliable macro pricing matrix. Try broadening your metric filters."
        )


def synergie_metrics(tags_df):
    if not tags_df.empty and len(tags_df) >= 4:
        median_score = tags_df["avg_review_score"].median()
        median_owners = tags_df["avg_owners"].median()

        high_owners_high_score = tags_df[
            (tags_df["avg_review_score"] >= median_score) &
            (tags_df["avg_owners"] >= median_owners)
            ]
        low_owners_high_score = tags_df[
            (tags_df["avg_review_score"] >= median_score) &
            (tags_df["avg_owners"] < median_owners)
            ]

        # 🌟 NEW PILLAR: Find the absolute largest bubble across the entire dataset
        largest_bubble = tags_df.loc[tags_df["game_count"].idxmax()]

        st.write("")  # Spacing

        # Render three distinct responsive layout columns for the badges
        badge_col1, badge_col2, badge_col3 = st.columns(3)

        # 🌟 1. Industry Standard Card -> PINK Theme (#dc267f)
        with badge_col1:
            st.markdown(
                f"""
                <div style="background-color: rgba(220, 38, 127, 0.08); padding: 16px; border-left: 4px solid #dc267f; border-radius: 6px; height: 100%;">
                    <b style="color: #dc267f; font-size: 0.95rem; text-transform: uppercase; letter-spacing: 0.05em;">📊 Industry Standard</b><br>
                    <div style="margin-top: 8px; font-size: 0.95rem; line-height: 1.5; color: #e2e8f0;">
                        The mechanic <code style="color: #dc267f; background: rgba(220, 38, 127, 0.12); padding: 2px 6px; border-radius: 4px;"><b>{largest_bubble['secondary_tag'].upper()}</b></code> 
                        defines this space, appearing in <code style="font-family: monospace;"><b>{largest_bubble['game_count']:,}</b></code> active titles. 
                        It represents the baseline cost-of-entry expected by the player base.
                    </div>
                </div>
                """,
                unsafe_allow_html=True
            )

        # 🌟 2. Core Market Catalyst Card -> BLUE Theme in the middle (#7ad9ff / #38bdf8)
        with badge_col2:
            if not high_owners_high_score.empty:
                prime_catalyst = high_owners_high_score.loc[high_owners_high_score["avg_owners"].idxmax()]
                st.markdown(
                    f"""
                    <div style="background-color: rgba(122, 217, 255, 0.08); padding: 16px; border-left: 4px solid #7ad9ff; border-radius: 6px; height: 100%;">
                        <b style="color: #38bdf8; font-size: 0.95rem; text-transform: uppercase; letter-spacing: 0.05em;">🚀 Core Market Catalyst</b><br>
                        <div style="margin-top: 8px; font-size: 0.95rem; line-height: 1.5; color: #e2e8f0;">
                            Integrating <code style="color: #38bdf8; background: rgba(122, 217, 255, 0.15); padding: 2px 6px; border-radius: 4px;"><b>{prime_catalyst['secondary_tag'].upper()}</b></code> 
                            yields the strongest crossover footprint. Titles with this trait average 
                            <code style="font-family: monospace;"><b>{prime_catalyst['avg_owners']:,.0f}</b></code> owners with 
                            <code style="font-family: monospace;"><b>{prime_catalyst['avg_review_score']:.1f}%</b></code> approval.
                        </div>
                    </div>
                    """,
                    unsafe_allow_html=True
                )
            else:
                st.markdown(
                    """
                    <div style="background-color: rgba(15, 23, 42, 0.4); padding: 16px; border-left: 4px solid #64748b; border-radius: 6px; height: 100%;">
                        <b style="color: #94a3b8; font-size: 0.95rem; text-transform: uppercase;">🚀 Core Market Catalyst</b><br>
                        <div style="margin-top: 8px; font-size: 0.95rem; color: #64748b; font-style: italic;">
                            No high-volume baseline mechanics cleared the upper performance thresholds.
                        </div>
                    </div>
                    """,
                    unsafe_allow_html=True
                )

        # 🌟 3. Under-Exploited Niche Card -> GOLD/YELLOW Theme (#ffb000)
        with badge_col3:
            if not low_owners_high_score.empty:
                hidden_niche = low_owners_high_score.loc[low_owners_high_score["avg_review_score"].idxmax()]
                st.markdown(
                    f"""
                    <div style="background-color: rgba(255, 176, 0, 0.08); padding: 16px; border-left: 4px solid #ffb000; border-radius: 6px; height: 100%;">
                        <b style="color: #ffb000; font-size: 0.95rem; text-transform: uppercase; letter-spacing: 0.05em;">💡 Under-Exploited Niche</b><br>
                        <div style="margin-top: 8px; font-size: 0.95rem; line-height: 1.5; color: #e2e8f0;">
                            The tag <code style="color: #ffb000; background: rgba(255, 176, 0, 0.12); padding: 2px 6px; border-radius: 4px;"><b>{hidden_niche['secondary_tag'].upper()}</b></code> 
                            shows clear signs of unmet demand, driving an incredible satisfaction rating of 
                            <code style="font-family: monospace;"><b>{hidden_niche['avg_review_score']:.1f}%</b></code> on lower volume scales.
                        </div>
                    </div>
                    """,
                    unsafe_allow_html=True
                )
            else:
                st.markdown(
                    """
                    <div style="background-color: rgba(15, 23, 42, 0.4); padding: 16px; border-left: 4px solid #64748b; border-radius: 6px; height: 100%;">
                        <b style="color: #94a3b8; font-size: 0.95rem; text-transform: uppercase;">💡 Under-Exploited Niche</b><br>
                        <div style="margin-top: 8px; font-size: 0.95rem; color: #64748b; font-style: italic;">
                            No hidden under-saturated high-satisfaction features detected in this profile.
                        </div>
                    </div>
                    """,
                    unsafe_allow_html=True
                )

        st.write("")
        st.write("")


def title_metrics(leaders):
    if leaders["titan_name"] != "N/A" or leaders["favorite_name"] != "N/A":

        # Generate the three-column layout for the performance metric highlights
        leader_col1, leader_col2, leader_col3 = st.columns(3)

        # 1. Card: Market Share Leader (All-time Max Owners)
        with leader_col1:
            st.markdown(
                f"""
                <div style="background-color: rgba(15, 23, 42, 0.4); padding: 16px; border-left: 4px solid #f59e0b; border-radius: 6px; height: 100%;">
                    <b style="color: #fbbf24; font-size: 0.95rem; text-transform: uppercase; letter-spacing: 0.05em;">All-Time Market Titan</b><br>
                    <div style="margin-top: 8px; font-size: 0.95rem; line-height: 1.5; color: #e2e8f0;">
                        <code style="color: #fbbf24; background: rgba(251,191,36,0.1); padding: 2px 6px; border-radius: 4px;"><b>{leaders['titan_name'].upper()}</b></code> 
                        holds the undisputed ceiling record for scale in this category, reaching an estimated 
                        <code style="font-family: monospace;"><b>{leaders['max_owners']:,}</b></code> max owners.
                    </div>
                </div>
                """,
                unsafe_allow_html=True
            )

        # 2. Card: Highest Quality Score (All-time Damped Bayesian Average Peak)
        with leader_col2:
            st.markdown(
                f"""
                <div style="background-color: rgba(15, 23, 42, 0.4); padding: 16px; border-left: 4px solid #10b981; border-radius: 6px; height: 100%;">
                    <b style="color: #34d399; font-size: 0.95rem; text-transform: uppercase; letter-spacing: 0.05em;">All-Time Community Favorite</b><br>
                    <div style="margin-top: 8px; font-size: 0.95rem; line-height: 1.5; color: #e2e8f0;">
                        <code style="color: #34d399; background: rgba(52,211,153,0.1); padding: 2px 6px; border-radius: 4px;"><b>{leaders['favorite_name'].upper()}</b></code> 
                        holds the absolute highest player sentiment record with a custom Bayesian-damped score of 
                        <code style="font-family: monospace;"><b>{leaders['top_score'] * 100:.2f}%</b></code>.
                    </div>
                </div>
                """,
                unsafe_allow_html=True
            )

        # 3. Card: Retention King (All-time Max Average Playtime Hours)
        with leader_col3:
            st.markdown(
                f"""
                <div style="background-color: rgba(15, 23, 42, 0.4); padding: 16px; border-left: 4px solid #3b82f6; border-radius: 6px; height: 100%;">
                    <b style="color: #60a5fa; font-size: 0.95rem; text-transform: uppercase; letter-spacing: 0.05em;">All-Time Retention King</b><br>
                    <div style="margin-top: 8px; font-size: 0.95rem; line-height: 1.5; color: #e2e8f0;">
                        <code style="color: #60a5fa; background: rgba(96,165,250,0.1); padding: 2px 6px; border-radius: 4px;"><b>{leaders['retention_name'].upper()}</b></code> 
                        leads historical engagement density, maintaining an unparalleled mean duration of 
                        <code style="font-family: monospace;"><b>{leaders['top_playtime']:,}h</b></code> logged per user.
                    </div>
                </div>
                """,
                unsafe_allow_html=True
            )

        st.write("")

    else:
        st.write("")
        st.info("**No Genre Information Found:** No baseline records could be fetched for this category configurations.")
