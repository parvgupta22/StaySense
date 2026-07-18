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
# Theme (matches Home / Listing Analysis)
# =====================================================

ACCENT = "#FF5A5F"
CARD_BG = "#1A1D24"
CARD_BORDER = "#2A2E38"
TEXT_MUTED = "#9CA3AF"

st.markdown(f"""
<style>
.step-strip {{ display: flex; align-items: center; gap: 4px; margin-bottom: 12px; }}
.step-card {{
    background: {CARD_BG};
    border: 1px solid {CARD_BORDER};
    border-radius: 10px;
    padding: 10px 6px;
    text-align: center;
    flex: 1;
}}
.step-card .icon {{ font-size: 1.5em; }}
.step-card .label {{ font-size: 0.78em; font-weight: 600; color: #E5E5E5; margin-top: 2px; }}
.step-arrow {{ color: {TEXT_MUTED}; font-size: 1.2em; padding: 0 2px; }}

.section-header {{
    border-left: 3px solid {ACCENT};
    padding-left: 12px;
    margin: 4px 0 14px 0;
}}
.section-header h2 {{ margin: 0; }}

.approach-chosen {{
    background: {CARD_BG};
    border: 1px solid {ACCENT};
    border-radius: 10px;
    padding: 14px 16px;
    color: #E5E5E5;
}}
</style>
""", unsafe_allow_html=True)

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

strip_html = "<div class='step-strip'>"
for i, (num, icon, label) in enumerate(pipeline_steps):
    strip_html += (
        f"<div class='step-card'>"
        f"<div class='icon'>{icon}</div>"
        f"<div class='label'>{num}. {label}</div>"
        f"</div>"
    )
    if i < len(pipeline_steps) - 1:
        strip_html += "<div class='step-arrow'>→</div>"
strip_html += "</div>"

st.markdown(strip_html, unsafe_allow_html=True)
st.markdown("---")

# =====================================================
# 1. KPI Definitions
# =====================================================

st.markdown('<div class="section-header"><h2>1️⃣ 🧮 KPI Definitions</h2></div>', unsafe_allow_html=True)

st.markdown(
    "Every listing is scored across three independent pillars, each "
    "capturing a different dimension of performance:"
)

k1, k2, k3 = st.columns(3)

with k1:
    with st.container(border=True):
        st.markdown("#### HostTrust")
        st.caption(
            "Host reliability: experience, response rate, "
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
        "little information."
    )

st.markdown("")

# =====================================================
# 2. StayScore Calculation
# =====================================================

st.markdown('<div class="section-header"><h2>2️⃣ ⭐ StayScore Calculation</h2></div>', unsafe_allow_html=True)

st.markdown(
    "StayScore combines the three KPI pillars into a single composite "
    "performance number."
)

st.markdown(
    """<div class='approach-chosen'>
    <strong>Equal-thirds weighting</strong><br>
    HostTrust, ListingIQ, and ExperienceIQ each contribute one third
    (33.33% / 33.33% / 33.34%) to the final StayScore. This is a deliberate,
    documented default: the most defensible option in the absence of a
    ground-truth outcome variable or business-defined priority between the
    three pillars. As soon as either becomes available — a real conversion
    metric or explicit business priorities — the weighting can move to a
    supervised or AHP-based approach instead.
    </div>""",
    unsafe_allow_html=True,
)


st.markdown("")

# =====================================================
# 3. Candidate Pool Construction
# =====================================================

st.markdown('<div class="section-header"><h2>3️⃣ 🗺️ Candidate Pool Construction</h2></div>', unsafe_allow_html=True)

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

st.markdown('<div class="section-header"><h2>4️⃣ 🎯 Similarity Search</h2></div>', unsafe_allow_html=True)

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

st.markdown('<div class="section-header"><h2>5️⃣ 🏆 Benchmark Construction</h2></div>', unsafe_allow_html=True)

with st.container(border=True):
    st.markdown(
        f"From the similar listings retrieved above, StaySense selects the "
        f"top **{int(BENCHMARK_PERCENTILE * 100)}%** by StayScore to form "
        "the benchmark group — the average of the highest-*performing* "
        "similar listings, not just any similar listing."
    )
    st.markdown(
        "This reflects the product's purpose: it doesn't show 'what's "
        "typical' among comparable listings — it shows 'what's achievable' "
        "among listings that are genuinely comparable."
    )

st.markdown("")

# =====================================================
# 6. Comparison
# =====================================================

st.markdown('<div class="section-header"><h2>6️⃣ 📊 Comparison</h2></div>', unsafe_allow_html=True)

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
        "This is the step a viewer actually sees first on the Listing "
        "Analysis page — everything above it is the analytical foundation "
        "that makes that comparison meaningful."
    )