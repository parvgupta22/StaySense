"""
StaySense - Listing Analysis Page

The core interactive tool. A host selects their listing and sees a
step-by-step breakdown answering three questions:

1. How is my listing performing?
2. How does it compare with successful competitors?
3. What should I improve first?

Author: Parv Gupta
"""

import pandas as pd
import plotly.graph_objects as go
import streamlit as st

from recommendation_engine import master, similarity_df, generate_listing_report

# =====================================================
# Page Configuration
# =====================================================

st.set_page_config(
    page_title="StaySense | Listing Analysis",
    page_icon="📋",
    layout="wide"
)
st.markdown("""
<style>

/* Dropdown box */
div[data-baseweb="select"] {
    cursor: pointer !important;
}

/* Every element inside the select */
div[data-baseweb="select"] * {
    cursor: pointer !important;
}

</style>
""", unsafe_allow_html=True)
st.markdown("""
<style>
.block-container {
    padding-top: 1.5rem;
}
</style>
""", unsafe_allow_html=True)





PRIORITY_ICON = {
    "High": "🔴",
    "Medium": "🟠",
    "Low": "🟡",
    "Strength": "🟢",
    "Unavailable": "⚪",
}

KPI_METRICS = ["StayScore", "HostTrust", "ListingIQ", "ExperienceIQ"]

# Display labels for every metric that can appear in the comparison /
# recommendations tables, so capitalization is consistent everywhere
# (price -> Price, amenities_count -> Amenities Count, etc.)
METRIC_LABELS = {
    "StayScore": "StayScore",
    "HostTrust": "HostTrust",
    "ListingIQ": "ListingIQ",
    "ExperienceIQ": "ExperienceIQ",
    "price": "Price",
    "amenities_count": "Amenities Count",
}


def display_label(metric):
    return METRIC_LABELS.get(metric, metric)


def safe_generate_report(listing_id):
    try:
        return generate_listing_report(listing_id), None
    except ValueError as e:
        return None, str(e)
    except Exception as e:
        return None, f"Something went wrong while building this report: {e}"


def percentile_rank(series, value):
    """Percentile standing of `value` against the full distribution in `series`.

    Used for the radar chart since HostTrust, ListingIQ, ExperienceIQ, and
    StayScore all sit on different raw scales (e.g. HostTrust tops out
    around 96, ListingIQ around 79) - plotting raw values on one 0-100
    axis distorts the shape. Percentile rank puts every KPI on a fair,
    directly comparable 0-100 scale.
    """
    valid = series.dropna()
    if valid.empty or pd.isna(value):
        return None
    return float((valid <= value).mean() * 100)




# =====================================================
# Sidebar - Listing Selector
# =====================================================
# Search and dropdown are two separate, independent widgets: the search
# box narrows the list, the dropdown picks from it. Typing in the search
# box is optional - you can always just browse the full dropdown.

st.sidebar.header("📋 Select a Listing")

listing_ids = sorted(similarity_df["listing_id"].unique())

search_term = st.sidebar.text_input(
    "Search by Listing ID",
    placeholder="e.g. 123456",
)

if search_term:
    filtered_ids = [lid for lid in listing_ids if search_term in str(lid)]
else:
    filtered_ids = listing_ids

st.sidebar.caption(f"{len(filtered_ids)} listing(s) available")

selected_listing_id = st.sidebar.selectbox(
    "Choose a listing",
    options=filtered_ids,
    index=None,
    placeholder="Select from the list...",
)

# =====================================================
# Header
# =====================================================

st.title("📋 Listing Analysis")
st.write(
    "Analyze how a listing performs against comparable high-performing Airbnb listings and discover the highest-impact improvements."
)

if selected_listing_id is None:
    st.info("👈 Search or select a Listing ID from the sidebar to begin.")
    st.stop()

with st.spinner("Building your report..."):
    report, error = safe_generate_report(selected_listing_id)

if error:
    st.error(error)
    st.stop()

benchmark = report["benchmark"]
comparison = report["comparison"]
recommendations = report["recommendations"]

info = report["listing_info"]




# =====================================================
# Listing Overview
# =====================================================

st.header("📋 Listing Overview")

col1, col2 = st.columns(2)

# -----------------------------
# Location
# -----------------------------
with col1:

    with st.container(border=True):

        st.subheader("📍 Location")

        if pd.notna(info["listing_id"]):
            st.write(f" Listing ID: {int(info['listing_id'])}")

        if pd.notna(info["city"]):
            st.write(f" City: {info['city']}")

        if pd.notna(info["neighbourhood"]):
            st.write(f" Neighbourhood: {info['neighbourhood']}")

        st.write(f" Benchmark Listings: {len(benchmark)}")


# -----------------------------
# Property
# -----------------------------
with col2:

    with st.container(border=True):

        st.subheader("🏠 Property")

        if pd.notna(info["property_type"]):
            st.write(f" Property Type: {info['property_type']}")

        if pd.notna(info["room_type"]):
            st.write(f" Room Type: {info['room_type']}")

        if pd.notna(info["price"]):
            st.write(f" Price: €{info['price']:.0f} / Night")

        if pd.notna(info["accommodates"]):
            guests = int(info["accommodates"])
            st.write(
                f" Accommodates: {guests} Guest{'s' if guests != 1 else ''}"
            )

        if pd.notna(info["bedrooms"]):
            bedrooms = int(info["bedrooms"])
            st.write(
                f" Bedrooms: {bedrooms} Bedroom{'s' if bedrooms != 1 else ''}"
            )

        if "amenities_count" in info and pd.notna(info["amenities_count"]):
            st.write(f" Amenities: {int(info['amenities_count'])}")

st.markdown("")

# =====================================================
# Question 1: How is my listing performing?
# =====================================================

st.header("1️⃣ How is my listing performing?")

kpi_rows = comparison[comparison["Metric"].isin(KPI_METRICS)]

kpi_cols = st.columns(len(kpi_rows))

for col, (_, row) in zip(kpi_cols, kpi_rows.iterrows()):
    target = row["Target"]
    gap = row["Gap (%)"]

    if pd.isna(target) or pd.isna(gap):
        col.metric(display_label(row["Metric"]), "N/A")
    else:
        col.metric(
            display_label(row["Metric"]),
            f"{target:.1f}",
            delta=f"{gap:.1f}% vs benchmark",
        )

# --- KPI Radar Chart -------------------------------------------------
# Each KPI is converted to a percentile rank against the full dataset,
# so all four axes are on a fair, comparable 0-100 scale regardless of
# their raw ranges. Benchmark peers are overlaid for context.

radar_metrics = []
target_percentiles = []
benchmark_percentiles = []

for _, row in kpi_rows.iterrows():
    metric = row["Metric"]
    if metric not in master.columns:
        continue

    t_pct = percentile_rank(master[metric], row["Target"])
    b_pct = percentile_rank(master[metric], row["Benchmark"])

    if t_pct is None:
        continue

    radar_metrics.append(display_label(metric))
    target_percentiles.append(t_pct)
    benchmark_percentiles.append(b_pct if b_pct is not None else 0)

if len(radar_metrics)==4:
    with st.container(border=True):
        st.markdown("**KPI Profile — Percentile vs. All Listings**")
        st.caption(
            "Each axis shows this listing's percentile rank across the full dataset, "
            "so all four KPIs are directly comparable despite having different raw scales."
        )

        # Close the loop so each shape connects back to its starting point
        categories_closed = radar_metrics + [radar_metrics[0]]
        target_closed = target_percentiles + [target_percentiles[0]]
        benchmark_closed = benchmark_percentiles + [benchmark_percentiles[0]]

        fig = go.Figure()

        fig.add_trace(go.Scatterpolar(
            r=benchmark_closed,
            theta=categories_closed,
            fill="toself",
            name="Benchmark Peers",
            line=dict(color="#9CA3AF", width=1.5, dash="dot"),
            fillcolor="rgba(156, 163, 175, 0.15)",
        ))

        fig.add_trace(go.Scatterpolar(
            r=target_closed,
            theta=categories_closed,
            fill="toself",
            name="This Listing",
            line=dict(color="#FF5A5F", width=2.5),
            fillcolor="rgba(255, 90, 95, 0.25)",
        ))

        fig.update_layout(
            polar=dict(
                radialaxis=dict(
                    visible=True,
                    range=[0, 100],
                    ticksuffix="%",
                    tickfont=dict(size=10),
                ),
                angularaxis=dict(
                    tickfont=dict(size=13),
                ),
            ),
            showlegend=True,
            legend=dict(orientation="h", yanchor="bottom", y=-0.15, xanchor="center", x=0.5),
            height=420,
            margin=dict(l=70, r=70, t=30, b=30),
        )

        st.plotly_chart(fig, use_container_width=True)
else:

    unavailable_kpis = []

    for _, row in kpi_rows.iterrows():

        metric = row["Metric"]

        if metric not in master.columns:
            unavailable_kpis.append(display_label(metric))
            continue

        if percentile_rank(master[metric], row["Target"]) is None:
            unavailable_kpis.append(display_label(metric))

    with st.container(border=True):

        st.markdown("**📊 KPI Profile**")

        st.info(
            "The radar chart cannot be displayed because one or more KPIs could not be computed for this listing."
        )

        st.markdown("**Unavailable KPIs:**")

        for metric in unavailable_kpis:
            st.write(f"• {metric}")

st.markdown("")

# =====================================================
# Question 2: How does it compare with competitors?
# =====================================================

st.header("2️⃣ How does it compare with successful competitors?")

chart_col, table_col = st.columns([3, 2])

with chart_col:
    with st.container(border=True):

        st.markdown("**Target vs. Benchmark**")
        st.caption("Your listing's KPI scores next to the average of your top benchmark peers.")

        # Create chart dataframe
        chart_data = kpi_rows.copy()

        chart_data["Metric"] = chart_data["Metric"].apply(display_label)

        # Order metrics
        order = [
            "StayScore",
            "HostTrust",
            "ListingIQ",
            "ExperienceIQ"
        ]

        chart_data["Metric"] = pd.Categorical(
            chart_data["Metric"],
            categories=order,
            ordered=True
        )

        chart_data = chart_data.sort_values("Metric")

        # Create grouped bar chart
        fig = go.Figure()

        fig.add_trace(
            go.Bar(
                name="Target",
                x=chart_data["Metric"],
                y=chart_data["Target"],
                marker_color='#3B82F6',
                text=chart_data["Target"].round(1),
                textposition="outside"
            )
        )

        fig.add_trace(
            go.Bar(
                name="Benchmark",
                x=chart_data["Metric"],
                y=chart_data["Benchmark"],
                marker_color='#6B7280',
                text=chart_data["Benchmark"].round(1),
                textposition="outside"
            )
        )

        fig.update_layout(
            barmode="group",
            template="plotly_dark",
            height=400,
            xaxis_title="",
            yaxis_title="Score",
            legend_title="",
            margin=dict(l=20, r=20, t=20, b=20)
        )
        legend=dict(
            orientation="h",
            yanchor="bottom",
            y=1.02,
            xanchor="right",
            x=1
)   
        st.plotly_chart(fig, use_container_width=True)

with table_col:
    with st.container(border=True):
        st.markdown("**Full Comparison**")
        display_comparison = comparison.copy()
        display_comparison["Metric"] = display_comparison["Metric"].apply(display_label)
        display_comparison = display_comparison.rename(columns={"Gap (%)": "Gap vs Benchmark (%)"})
        st.dataframe(
            display_comparison[["Metric", "Target", "Benchmark", "Gap vs Benchmark (%)"]],
            use_container_width=True,
            hide_index=True,
        )

with st.expander("View the benchmark peer listings used for this comparison"):
    display_cols = [
        c for c in [
            "listing_id",
            "Benchmark_Rank",
            "StayScore",
            "HostTrust",
            "ListingIQ",
            "ExperienceIQ",
            "price",
            "amenities_count",
        ]
        if c in benchmark.columns
    ]
    st.dataframe(benchmark[display_cols], use_container_width=True, hide_index=True)

st.markdown("")

# =====================================================
# Question 3: What should I improve first?
# =====================================================

st.header("🎯 Performance Insights & Recommendations")
st.caption(
    "Recommendations are prioritized by the size of the gap to your benchmark peers."
)

# -----------------------------
# Split Recommendations
# -----------------------------
improvements = recommendations[
    recommendations["Priority"] != "Strength"
]

strengths = recommendations[
    recommendations["Priority"] == "Strength"
]

priority_colors = {
    "High": "#EF4444",
    "Medium": "#F59E0B",
    "Low": "#3B82F6",
    "Strength": "#10B981"
}


# -----------------------------
# Recommendation Card
# -----------------------------
def recommendation_card(row):

    icon = PRIORITY_ICON.get(row["Priority"], "⚪")
    color = priority_colors.get(row["Priority"], "#6B7280")

    st.markdown(
        f"""
<div style="
background:#1f1f1f;
border-left:6px solid {color};
border-radius:12px;
padding:16px;
margin-bottom:16px;
">

<div style="
display:inline-block;
background:{color};
color:white;
padding:5px 12px;
border-radius:20px;
font-size:11px;
font-weight:bold;
">
{icon} {row["Priority"].upper()}
</div>

<h3 style="
margin-top:18px;
margin-bottom:18px;
color:white;
">
{display_label(row["Metric"])}
</h3>

<div style="
display:grid;
grid-template-columns:repeat(3,1fr);
gap:10px;
margin-bottom:18px;
">

<div style="
background:#2a2a2a;
padding:10px;
border-radius:8px;
text-align:center;
">
<div style="font-size:11px;color:#9CA3AF;">CURRENT</div>
<div style="font-size:20px;font-weight:bold;color:white;">
{row["Target"]:.1f}
</div>
</div>

<div style="
background:#2a2a2a;
padding:10px;
border-radius:8px;
text-align:center;
">
<div style="font-size:11px;color:#9CA3AF;">BENCHMARK</div>
<div style="font-size:20px;font-weight:bold;color:white;">
{row["Benchmark"]:.1f}
</div>
</div>

<div style="
background:#2a2a2a;
padding:10px;
border-radius:8px;
text-align:center;
">
<div style="font-size:11px;color:#9CA3AF;">GAP</div>
<div style="font-size:20px;font-weight:bold;color:{color};">
{row["Gap (%)"]:.1f}%
</div>
</div>

</div>

<div style="
font-size:13px;
font-weight:bold;
color:#9CA3AF;
margin-bottom:8px;
">
💡 Recommended Action
</div>

<div style="
font-size:15px;
line-height:1.6;
color:white;
">
{row["Recommendation"]}
</div>

</div>
""",
        unsafe_allow_html=True,
    )

# -----------------------------
# Improvement Priorities
# -----------------------------
st.subheader("🔴 Improvement Priorities")
NUM_COLS=3
cols = st.columns(NUM_COLS)

for i, (_, row) in enumerate(improvements.iterrows()):

    with cols[i % NUM_COLS]:
        recommendation_card(row)


# -----------------------------
# Strengths
# -----------------------------
st.subheader("🟢 Strengths to Maintain")

cols = st.columns(NUM_COLS)

for i, (_, row) in enumerate(strengths.iterrows()):

    with cols[i % NUM_COLS]:
        recommendation_card(row)