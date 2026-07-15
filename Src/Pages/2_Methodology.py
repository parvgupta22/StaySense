"""
StaySense - Methodology Page

The "show your work" page. Walks through the actual analytical pipeline
behind StaySense in the order it actually runs: KPI definitions, StayScore
calculation, candidate pool construction, similarity search, benchmark
construction, and finally comparison.

Author: Parv Gupta
"""

import streamlit as st

from recommendation_engine import master, LEVEL_FILTERS, SIMILARITY_FEATURES, BENCHMARK_PERCENTILE

# =====================================================
# Page Configuration
# =====================================================

st.set_page_config(
    page_title="StaySense | Methodology",
    page_icon="🔬",
    layout="wide"
)



# =====================================================
# Header
# =====================================================

st.title("🔬 Methodology")
st.caption(
    "How StaySense scores listings, finds genuinely comparable peers, and "
    "builds a benchmark — the full analytical pipeline, in order."
)

st.markdown("")

# =====================================================
# Pipeline Overview Strip
# =====================================================

pipeline_steps = [
    ("1", "🧮", "KPI Definitions"),
    ("2", "⭐", "StayScore"),
    ("3", "🗺️", "Candidate Pool"),
    ("4", "🎯", "Similarity Search"),
    ("5", "🏆", "Benchmark"),
    ("6", "📊", "Comparison"),
]

step_cols = st.columns(len(pipeline_steps))
for col, (num, icon, label) in zip(step_cols, pipeline_steps):
    with col:
        st.markdown(
            f"<div style='text-align:center; padding:8px 4px;'>"
            f"<div style='font-size:1.8em;'>{icon}</div>"
            f"<div style='font-weight:700; font-size:0.85em;'>{num}. {label}</div>"
            f"</div>",
            unsafe_allow_html=True,
        )

st.markdown("---")

# =====================================================
# 1. KPI Definitions
# =====================================================

st.header("1️⃣ 🧮 KPI Definitions")

st.markdown(
    "Every listing is scored across three independent pillars, each "
    "capturing a different dimension of performance:"
)

k1, k2, k3 = st.columns(3)

with k1:
    with st.container(border=True):
        st.markdown("#### HostTrust")
        st.caption(
            "Host reliability: experience, superhost status, response rate, "
            "acceptance rate, identity verification, response time."
        )

with k2:
    with st.container(border=True):
        st.markdown("#### ListingIQ")
        st.caption(
            "Property quality: amenities, accommodates, bedrooms, property "
            "type, room type."
        )

with k3:
    with st.container(border=True):
        st.markdown("#### ExperienceIQ")
        st.caption(
            "Guest experience: cleanliness, check-in, and communication "
            "review sub-scores."
        )

with st.container(border=True):
    st.markdown("**Handling Missing Data**")
    st.markdown(
        "Each KPI uses **proportional weight redistribution**: when a "
        "component is missing for a listing, its weight is redistributed "
        "across the components that are present, rather than losing the "
        "score entirely. A transparency column tracks how many components "
        "were actually used for each listing, and listings with fewer than "
        "3 components present are excluded rather than scored on too "
        "little information. ExperienceIQ's missingness — largely from "
        "listings without enough reviews yet — is handled the same way, "
        "one level up, when StayScore is calculated."
    )

st.markdown("")

# =====================================================
# 2. StayScore Calculation
# =====================================================

st.header("2️⃣ ⭐ StayScore Calculation")

st.markdown(
    "StayScore combines the three KPI pillars into a single composite "
    "performance number. Several weighting approaches were evaluated before "
    "arriving at the current method:"
)

with st.container(border=True):

    st.markdown(
        "**Chosen approach: equal-thirds weighting** — HostTrust, "
        "ListingIQ, and ExperienceIQ each contribute one third "
        "(33.33% / 33.33% / 33.34%) to the final StayScore. This is a "
        "deliberate, documented default: the most defensible option in the "
        "absence of a ground-truth outcome variable or business-defined "
        "priority between the three pillars."
    )

st.markdown("")

# =====================================================
# 3. Candidate Pool Construction
# =====================================================

st.header("3️⃣ 🗺️ Candidate Pool Construction")

st.markdown(
    "Before any similarity scoring happens, StaySense narrows the field to "
    "listings that are structurally comparable, using a hierarchical filter:"
)

filter_cols = st.columns(len(LEVEL_FILTERS))
for col, (level, filters) in zip(filter_cols, LEVEL_FILTERS.items()):
    with col:
        with st.container(border=True):
            st.markdown(f"**Level {level}**")
            st.caption(" → ".join(filters))

st.markdown(
    "Each listing is assigned a hierarchy level, and only listings sharing "
    "all of that level's attributes enter its candidate pool — trading off "
    "pool size against comparability. Level 1 gives the tightest match "
    "(same city, neighbourhood, and property type); broader levels fall "
    "back to city-wide comparison when finer-grained peers aren't available."
)

st.markdown("")

# =====================================================
# 4. Similarity Search
# =====================================================

st.header("4️⃣ 🎯 Similarity Search")

st.markdown(
    "Within a listing's candidate pool, StaySense uses a **K-Nearest "
    "Neighbors** search (Euclidean distance) to find the listings most "
    "similar in scale and capacity:"
)

feature_cols = st.columns(len(SIMILARITY_FEATURES))
for col, feature in zip(feature_cols, SIMILARITY_FEATURES):
    with col:
        with st.container(border=True):
            st.markdown(f"**{feature}**")

st.markdown(
    "These features describe what a listing *is* — its size and capacity "
    "— rather than how it performs, keeping similarity selection "
    "independent from the KPI scores being benchmarked. This avoids "
    "circularity between 'who is similar' and 'who is a top performer.'"
)

st.markdown("")

# =====================================================
# 5. Benchmark Construction
# =====================================================

st.header("5️⃣ 🏆 Benchmark Construction")

with st.container(border=True):
    st.markdown(
        f"From the similar listings retrieved above, StaySense selects the "
        f"top **{int(BENCHMARK_PERCENTILE * 100)}%** by StayScore to form "
        "the benchmark group — the average of the highest-*performing* "
        "similar listings, not just any similar listing."
    )
    st.markdown(
        "This reflects the product's purpose: hosts aren't shown 'what's "
        "typical' among their peers, they're shown 'what's achievable' "
        "among listings that are genuinely comparable to their own."
    )

st.markdown("")

# =====================================================
# 6. Comparison
# =====================================================

st.header("6️⃣ 📊 Comparison")

with st.container(border=True):
    st.markdown(
        "Finally, the listing's own KPI and business metrics are compared "
        "against the benchmark average, producing a **gap percentage** for "
        "each metric. That gap drives two things:"
    )
    st.markdown(
        "- **Priority ranking** — larger negative gaps are surfaced as "
        "higher-priority opportunities\n"
        "- **Recommendation text** — tailored guidance for each metric, "
        "based on the size and direction of the gap"
    )
    st.markdown(
        "This is the step a host actually sees first on the Listing "
        "Analysis page — everything above it is the analytical foundation "
        "that makes that comparison meaningful."
    )