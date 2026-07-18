"""
StaySense - Home Page
"""

import streamlit as st

from recommendation_engine import master, similarity_df

st.set_page_config(page_title="StaySense | Home", page_icon="🏠", layout="wide")

# =====================================================
# Theme
# =====================================================

ACCENT = "#FF5A5F"
CARD_BG = "#1A1D24"
CARD_BORDER = "#2A2E38"
TEXT_MUTED = "#9CA3AF"

st.markdown(f"""
<style>

.block-container {{
    padding-top: 2rem;
    max-width: 1100px;
}}

.hero {{
    text-align: center;
    padding: 60px 0 30px 0;
}}

.hero-badge {{
    display: inline-block;
    padding: 8px 18px;
    border-radius: 999px;
    border: 1px solid {CARD_BORDER};
    background: rgba(255,255,255,0.03);
    color: {ACCENT};
    font-size: 0.9rem;
    margin-bottom: 25px;
}}

.hero h1 {{
    font-size: 4rem;
    font-weight: 700;
    margin-bottom: 15px;
}}

.hero p {{
    font-size: 1.25rem;
    color: {TEXT_MUTED};
    max-width: 720px;
    margin: auto;
    line-height: 1.7;
}}

</style>
""", unsafe_allow_html=True)

# =====================================================
# Hero
# =====================================================

st.markdown("""
<div class="hero">

<div class="hero-badge">
Airbnb Intelligence Platform
</div>

<h1>🏠 StaySense</h1>

<p>
Benchmarks listings against genuinely comparable peers and
delivers prioritized recommendations.
</p>

</div>
""", unsafe_allow_html=True)

left, b1, b2, right = st.columns([2,1.3,1.3,2])

with b1:
    if st.button(
        "Explore Listings",
        type="primary",
        use_container_width=True,
    ):
        st.switch_page("pages/1_Listing_Analysis.py")

with b2:
    if st.button(
        "View Market Insights",
        use_container_width=True,
    ):
        st.switch_page("pages/2_Market_Insights.py")
st.write("")
st.write("")
 

# =====================================================
# Dataset Snapshot
# =====================================================

st.header("📈 Dataset Snapshot")

total_listings = len(master)
total_cities = similarity_df["city"].nunique()
avg_stayscore = master["StayScore"].mean()
median_price = similarity_df["price"].median()

m1, m2, m3, m4 = st.columns(4)
m1.metric("Listings", f"{total_listings:,}")
m2.metric("Cities", total_cities)
m3.metric("Median Price", f"${median_price:,.0f}")
m4.metric("Average StayScore", f"{avg_stayscore:.1f}")

st.divider()

# =====================================================
# Project Overview
# =====================================================

st.header("🌍 Project Overview")

left, right = st.columns([1.3, 1])

with left:
    st.markdown("""
### Why StaySense?

Traditional Airbnb analytics compare listings using broad, unfiltered averages —
a studio in central Paris isn't a meaningful comparison for a villa in the
suburbs.

StaySense benchmarks every listing against genuinely comparable peers using
hierarchical filtering and similarity search, then scores performance using
custom KPIs built specifically for this dataset.
""")

with right:
    with st.container(border=True):
        st.subheader("Objective")
        st.markdown("""
- Comparable peer selection
- K-Nearest Neighbors similarity search
- Composite performance KPIs
- Interactive benchmarking dashboard
""")

st.divider()

# =====================================================
# Key Features
# =====================================================

st.header("✨ Key Features")

features = [
    ("📊", "Market Insights", "Executive Power BI analytics across the full dataset."),
    ("🔍", "Listing Analysis", "Benchmark any listing against its top-performing peers."),
    ("⭐", "Custom KPIs", "StayScore, HostTrust, ListingIQ & ExperienceIQ."),
    ("📈", "Recommendations", "Prioritized, actionable improvement guidance."),
]

for col, (icon, title, desc) in zip(st.columns(4), features):
    with col:
        with st.container(border=True):
            st.markdown(f"**{icon} {title}**")
            st.caption(desc)

st.divider()

# =====================================================
# Custom KPIs
# =====================================================

st.header("🏆 Custom KPIs")

kpis = [
    ("StayScore", "Composite overall listing performance."),
    ("HostTrust", "Host reliability and responsiveness."),
    ("ListingIQ", "Listing completeness and quality."),
    ("ExperienceIQ", "Guest experience and satisfaction."),
]

for col, (title, desc) in zip(st.columns(4), kpis):
    with col:
        with st.container(border=True):
            st.markdown(f"**{title}**")
            st.caption(desc)

st.divider()

# =====================================================
# Workflow
# =====================================================

st.header("⚙️ Workflow")
st.markdown(
    "`Dataset` → `Cleaning` → `Feature Engineering` → `Custom KPIs` → "
    " `Similarity Search` → `Power BI` → `Streamlit`"
)

st.divider()

# =====================================================
# Technology Stack
# =====================================================

st.header("💻 Technology Stack")
st.write("🐍 Python  |  🐼 Pandas  |  🔢 NumPy  |  📊 Power BI  |  ⚡ DAX  |  🟠 Streamlit")

st.divider()

# =====================================================
# Explore StaySense
# =====================================================

st.header("🚀 Explore StaySense")

nav_cards = [
    ("📈 Market Insights", "Explore the full Power BI report.", "pages/2_Market_Insights.py"),
    ("📋 Listing Analysis", "Analyze and benchmark individual listings.", "pages/1_Listing_Analysis.py"),
    ("🔬 Methodology", "Understand the analytical approach.", "pages/3_Methodology.py"),
]

for col, (title, desc, target) in zip(st.columns(3), nav_cards):
    with col:
        with st.container(border=True):
            st.markdown(f"**{title}**")
            st.caption(desc)
            st.page_link(target, label="Open →")

st.markdown(
    '<div class="footer">Built using Streamlit, Python & Power BI.</div>',
    unsafe_allow_html=True,
)