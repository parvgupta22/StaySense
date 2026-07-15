"""
StaySense - Overview Page

Entry point of the app. Sets up the narrative: the problem StaySense
solves, how it solves it, and a snapshot of the underlying dataset.

Author: Parv Gupta
"""

import streamlit as st
import pandas as pd

from recommendation_engine import master, similarity_df

# =====================================================
# Page Configuration
# =====================================================

st.set_page_config(
    page_title="StaySense | Overview",
    page_icon="🏠",
    layout="wide"
)

st.markdown("""
<style>
.block-container {
    padding-top: 1.5rem;
}
</style>
""", unsafe_allow_html=True)




# =====================================================
# Header
# =====================================================

st.title("🏠 StaySense")
st.subheader("Airbnb Listing Intelligence — Decision Support, Not Prediction")

st.markdown(
    "StaySense helps Airbnb hosts understand how their listing performs "
    "against genuinely comparable, high-performing listings — and what to "
    "improve first. It does not predict prices or occupancy; it is an "
    "analytical benchmarking tool."
)

st.markdown("")

# =====================================================
# The Problem
# =====================================================

with st.container(border=True):
    st.markdown("### 🧩 The Problem")
    st.markdown(
        "Every Airbnb listing is unique. A studio in central Paris and a "
        "villa in the suburbs are not meaningful comparisons, yet most "
        "host-facing analytics tools compare listings against broad, "
        "unfiltered averages. A host with a below-average listing in an "
        "expensive, high-standard neighbourhood can look artificially "
        "strong — and a genuinely high-performing listing in a modest "
        "area can look artificially weak."
    )

st.markdown("")

# =====================================================
# The Solution
# =====================================================

st.markdown("### 🛠️ The Solution")

col1, col2, col3 = st.columns(3)

with col1:
    with st.container(border=True):
        st.markdown("#### 🗺️ Comparable Peers")
        st.markdown(
            "Hierarchical filtering (city → neighbourhood → property type) "
            "narrows the field to listings that are actually comparable, "
            "falling back to broader geography only when needed."
        )

with col2:
    with st.container(border=True):
        st.markdown("#### 🎯 Similarity Search")
        st.markdown(
            "Within that pool, a K-Nearest Neighbors search finds listings "
            "most similar in size and capacity — accommodates, bedrooms, "
            "and amenity count."
        )

with col3:
    with st.container(border=True):
        st.markdown("#### 📊 Composite KPIs")
        st.markdown(
            "Each listing is scored across three pillars — HostTrust, "
            "ListingIQ, and ExperienceIQ — which combine into a single "
            "StayScore for benchmarking."
        )

st.markdown("")

# =====================================================
# Dataset Overview
# =====================================================

st.markdown("### 📁 Dataset Overview")

total_listings = len(master)
total_cities = similarity_df["city"].nunique()
avg_stayscore = master["StayScore"].mean()
scored_listings = master["StayScore"].notna().sum()

m1, m2, m3, m4 = st.columns(4)
m1.metric("Total Listings", f"{total_listings:,}")
m2.metric("Cities Covered", f"{total_cities:,}")
m3.metric("Listings with a StayScore", f"{scored_listings:,}")
m4.metric("Average StayScore", f"{avg_stayscore:.1f}")

chart_col1, chart_col2 = st.columns(2)

with chart_col1:
    with st.container(border=True):
        st.markdown("**StayScore Distribution**")
        st.caption("How overall performance scores are spread across all scored listings.")

        stayscore_chart_data = master["StayScore"].dropna()
        binned_counts = pd.cut(stayscore_chart_data, bins=20).value_counts().sort_index()
        binned_counts.index = binned_counts.index.astype(str)  # Interval objects aren't chart-serializable

        st.bar_chart(binned_counts, use_container_width=True)

with chart_col2:
    with st.container(border=True):
        st.markdown("**Listings by City (Top 10)**")
        st.caption("Where the dataset's listings are concentrated.")

        top_cities = similarity_df["city"].value_counts().head(10)
        st.bar_chart(top_cities, use_container_width=True)

st.markdown("")

# =====================================================
# What's Next
# =====================================================

with st.container(border=True):
    st.markdown("### 🚀 Explore StaySense")

    nav_col1, nav_col2 = st.columns(2)

    with nav_col1:
        st.markdown("**📋 Listing Analysis**")
        st.markdown(
            "Look up a specific listing and see its full performance "
            "breakdown against its benchmark peers."
        )

    with nav_col2:
        st.markdown("**🔬 Methodology**")
        st.markdown(
            "A detailed walkthrough of the KPI construction, candidate "
            "selection logic, and benchmarking approach behind StaySense."
        )

    st.info("Use the sidebar to navigate between pages.")