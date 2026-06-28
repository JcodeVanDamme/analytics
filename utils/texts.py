texts = dict(
    pie_description=("This chart displays Steam market distribution by genre. "
                    "The top <b>90%</b> are shown individually, while smaller long-tail genres are grouped into <b>'Others'</b>."
    ),
    saturation_vs_payout=(
            "This dual-axis visualization contrasts market saturation against historical monetization standards "
            "by year. The bars track <b>Competitor Releases</b> (left axis) to demonstrate the volume velocity of "
            "competing titles over time. The overlay line tracks the <b>Average Revenue per Game</b> (right axis), "
            "calculated by multiplying list prices by baseline ownership bounds. This combination reveals whether "
            "surging genre saturation is actively cannibalizing individual game payout performance or if the market "
            "segment is scaling sustainably."
    ),
    pricing_tiers=(
        "This split-panel chart analyzes market dynamics across structural pricing buckets. "
        "The top panel contrasts market supply and demand: the bars show <b>Number of Games (Supply)</b> "
        "(left axis), while the solid line maps <b>Avg Owners (Demand)</b> (right axis) to identify where "
        "player acquisition peaks. The bottom panel isolates quality, tracking the <b>Avg Review Score (%)</b> "
        "on its own dedicated baseline to showcase how player satisfaction aligns with financial investment."
    ),
    tag_synergies=(
            "This quadrant profile maps sub-tag performance synergies within the selected genre. "
            "Each bubble represents a secondary tag: its horizontal position tracks player satisfaction via the "
            "<b>Average Review Score (%)</b>, while its vertical position represents commercial demand via "
            "<b>Average Estimated Owners</b>. The bubble scale reflects total market supply (Game Count). "
            "The dashed baseline axes intersect at the dataset's current medians, dividing the market into four distinct "
            "quadrants to instantly isolate high-demand, high-satisfaction niche opportunities."
        )
)


tooltips = {
    "titles": (
        "The total volume of unique game listings cataloged within this specific market segment. "
        "The trend indicator tracks Year-Over-Year volume changes, showing the growth or decline "
        "in new titles released this year compared directly against the previous year's baseline."
    ),
    "price": (
        "The historical average list price (USD) for titles in this market segment. "
        "The trend indicator tracks pricing velocity, measuring shifts in monetization by "
        "comparing the average launch price of new titles this year versus last year."
    ),
    "positive_ratio": (
        "The baseline user sentiment index, tracking the average percentage of positive reviews "
        "The trend indicator reveals the "
        "sentiment trajectory, showing if recent releases are seeing better or worse player reception."
    ),
    "peak_ccu": (
        "The average player popularity ceiling, measuring the mean all-time maximum concurrent "
        "player peak in this segment. The trend indicator highlights engagement momentum by "
        "comparing current-year launch peaks against last year's performance."
    ),
    "score": (
            "Damped Bayesian average: <i>Positives / (Positives + Negatives + 50)</i>. "
            "The +50 baseline stabilizes scores for low-volume titles to prevent early review skewing."
        ),
    "metacritic": (
        "Aggregated critical score from journalists and media publications. "
        "Displays empty if the title has no official expert review ranking."
    ),
    "playtime": (
        "The mean lifetime gameplay hours logged per user account. "
        "Serves as a proxy for product depth and retention."
    ),
    "owners": (
        "The upper bound of calculated ownership. "
        "Extracted directly from the maximum value of the platform tier brackets."
    ),
    "recommendations": (
        "Total count of positive platform recommendations "
        "submitted by players. Indicates organic viral momentum."
    )
}