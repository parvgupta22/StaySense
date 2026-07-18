"""
StaySense - Market Insights Page

The macro view: market-wide Airbnb data exploration, built in Power BI
and embedded here as three tabs, one per report page:

1. Dataset Overview   - property characteristics, pricing, geography
2. Performance        - KPI distributions and relationships
3. Price & Performance - how price and performance interact

Each tab embeds a distinct "Publish to Web" URL for that specific
Power BI report page. See the setup instructions below for how to
generate those URLs.

Author: Parv Gupta
"""

import streamlit as st
import streamlit.components.v1 as components

# =====================================================
# Page Configuration
# =====================================================

st.set_page_config(
    page_title="StaySense | Market Insights",
    page_icon="📈",
    layout="wide"
)

# =====================================================
# Embed URLs
# =====================================================
# Paste each page's "Publish to Web" link below. In Power BI Service:
# open the report -> switch to the page you want -> File > Embed report
# > Publish to web (public) > Create embed code > copy the "Link you
# can send in email" URL (not the full <iframe> HTML, just the link).
# Repeat once per page, switching pages before each Create embed code.

PAGE_1_URL = "https://app.powerbi.com/view?r=eyJrIjoiYzU4ZDZlNWEtZjY0Ny00NGY0LWEyMmYtNDI0ZGVhOWFiMmE1IiwidCI6ImVjOGQ3NTA2LTg3NDAtNDYzZi1iMmFkLTJkNjAxNGQxZGU3MiJ9&pageName=ca8262cf66b2f5eaf634"  # Dataset Overview
PAGE_2_URL = "https://app.powerbi.com/view?r=eyJrIjoiYzU4ZDZlNWEtZjY0Ny00NGY0LWEyMmYtNDI0ZGVhOWFiMmE1IiwidCI6ImVjOGQ3NTA2LTg3NDAtNDYzZi1iMmFkLTJkNjAxNGQxZGU3MiJ9&pageName=0e7262bf313e824e8db3"  # Performance Distributions
PAGE_3_URL = "https://app.powerbi.com/view?r=eyJrIjoiYzU4ZDZlNWEtZjY0Ny00NGY0LWEyMmYtNDI0ZGVhOWFiMmE1IiwidCI6ImVjOGQ3NTA2LTg3NDAtNDYzZi1iMmFkLTJkNjAxNGQxZGU3MiJ9&pageName=90dbcfd29705833651cb"  # Price & Performance

EMBED_HEIGHT = 700

# =====================================================
# Header
# =====================================================

st.title("📈 Market Insights")
st.caption(
    "A market-wide view of the Airbnb dataset — property characteristics, "
    "performance distributions, and how price relates to performance. "
    "Built in Power BI."
)

st.markdown("---")

# =====================================================
# Embedded Report Tabs
# =====================================================
# Each tab's embed URL is generated with every OTHER page hidden in Power
# BI Desktop before publishing (right-click page tab -> Hide page), so
# the page-tab navigator bar doesn't appear at all - no cropping needed.

tab1, tab2, tab3 = st.tabs([
    "🗺️ Dataset Overview",
    "⭐ Performance Distributions",
    "💰 Price & Performance",
])


def render_tab(url, tab_name):
    if url:
        components.iframe(url, height=EMBED_HEIGHT, scrolling=True)
    else:
        with st.container(border=True):
            st.markdown(f"### 📊 {tab_name} — Not Yet Connected")
            st.markdown(
                "Once this page's embed URL is generated in Power BI, paste it "
                "into the corresponding variable near the top of this file, and "
                "it will render directly here."
            )


with tab1:
    render_tab(PAGE_1_URL, "Dataset Overview")

with tab2:
    render_tab(PAGE_2_URL, "Performance Distributions")

with tab3:
    render_tab(PAGE_3_URL, "Price & Performance")

# =====================================================
# Setup Instructions (only shown if any URL is still missing)
# =====================================================

if not (PAGE_1_URL and PAGE_2_URL and PAGE_3_URL):
    st.markdown("---")
    with st.expander("🔧 How to connect the Power BI report"):
        st.markdown(
            "1. Open your published report at **app.powerbi.com**\n"
            "2. Switch to the specific page you want to embed (its tab at the "
            "bottom of the report)\n"
            "3. Go to **File → Embed report → Publish to web (public)**\n"
            "4. Click **Create embed code**\n"
            "5. Copy the URL under **\"Link you can send in email\"** — it looks "
            "like `https://app.powerbi.com/view?r=...`\n"
            "6. Paste it into `PAGE_1_URL`, `PAGE_2_URL`, or `PAGE_3_URL` "
            "(matching the page you just embedded) near the top of this file\n"
            "7. Repeat for each of the other two pages, switching the active "
            "page in Power BI *before* clicking Create embed code each time\n"
            "8. Save this file and refresh — the matching tab will now show "
            "the live report"
        )
        st.caption(
            "Publish to Web makes each report page publicly accessible to "
            "anyone with the link — fine for this project since the Airbnb "
            "dataset is public."
        )