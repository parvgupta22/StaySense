"""
StaySense Recommendation Engine

This module provides the complete recommendation engine
used by the StaySense dashboard.

Author: Parv Gupta
"""
# Imports
import pandas as pd
import numpy as np

from sklearn.neighbors import NearestNeighbors
from pathlib import Path


PROJECT_ROOT = Path(__file__).resolve().parent.parent
DATA_DIR = PROJECT_ROOT / "Data" / "processed"
DATA_DIR_2=PROJECT_ROOT / "Data" / "cleaned"


# Load Processed Data
master = pd.read_csv(DATA_DIR/"master.csv")
listings_clean = pd.read_csv(DATA_DIR_2/"Listings_Clean.csv")
similarity_df = pd.read_csv(DATA_DIR/"similarity_df.csv")

# Constants
LEVEL_1_FILTERS = [
    "city",
    "neighbourhood",
    "property_type"
]

LEVEL_2_FILTERS = [
    "city",
    "neighbourhood"
]

LEVEL_3_FILTERS = [
    "city"
]

SIMILARITY_FEATURES = [
    "accommodates",
    "bedrooms",
    "amenities_count"
]

COMPARISON_METRICS = [
    "StayScore",
    "HostTrust",
    "ListingIQ",
    "ExperienceIQ",
    "price",
    "amenities_count"
]

MIN_CANDIDATES = 100
TOP_SIMILAR = 100
BENCHMARK_PERCENTILE = 0.20

LEVEL_FILTERS = {
    1: ["city", "neighbourhood", "property_type"],
    2: ["city", "neighbourhood"],
    3: ["city"]
}

# Candidate Retrieval
def get_candidate_pool(listing_id):

    # Retrieve the selected listing
    target = similarity_df.loc[
        similarity_df["listing_id"] == listing_id
    ]

    if target.empty:
        raise ValueError(f"Listing ID {listing_id} not found.")

    target = target.iloc[0]

    # Determine hierarchy level
    hierarchy_level = target["Hierarchy_Level"]

    # Get the required filters
    filters = LEVEL_FILTERS[hierarchy_level]

    # Start with all listings
    candidate_pool = similarity_df.copy()

    # Apply each filter dynamically
    for column in filters:
        candidate_pool = candidate_pool[
            candidate_pool[column] == target[column]
        ]

    # Remove the listing itself
    candidate_pool = candidate_pool[
        candidate_pool["listing_id"] != listing_id
    ]

    return candidate_pool


# Similarity Ranking Function
def get_similar_listings(listing_id, top_similar=100):

    # Retrieve candidate pool
    candidate_pool = get_candidate_pool(listing_id).copy()

    # Retrieve target listing
    target = similarity_df.loc[
        similarity_df["listing_id"] == listing_id,
        SIMILARITY_FEATURES
    ]

    # Candidate features
    X_candidates = candidate_pool[SIMILARITY_FEATURES]

    # Number of neighbours to retrieve
    n_neighbors = min(top_similar, len(candidate_pool))

    # Fit KNN
    knn = NearestNeighbors(
        n_neighbors=n_neighbors,
        metric="euclidean"
    )

    knn.fit(X_candidates)

    # Find neighbours
    distances, indices = knn.kneighbors(target)

    # Retrieve similar listings
    similar_listings = candidate_pool.iloc[indices[0]].copy()

    # Add ranking information
    similar_listings["Distance"] = distances[0]
    similar_listings["Similarity_Rank"] = range(1, len(similar_listings) + 1)

    return similar_listings


# Benchmarking
def build_benchmark(listing_id):

    # Retrieve similar listings
    similar_listings = get_similar_listings(listing_id)
    
    # Step 2: Attach KPI scores
    similar_listings = similar_listings.merge(
        master[
            [
                "listing_id",
                "StayScore",
                "HostTrust",
                "ListingIQ",
                "ExperienceIQ"
            ]
        ],
        on="listing_id",
        how="left"
    )
  
    
    # Sort by StayScore (Highest first)
    similar_listings = similar_listings.sort_values(
        by="StayScore",
        ascending=False
    )

    
    # Number of benchmark listings
    benchmark_size = max(
        1,
        int(len(similar_listings) * BENCHMARK_PERCENTILE)
    )

    # Select benchmark
    benchmark = similar_listings.head(benchmark_size).copy()

    benchmark = benchmark.reset_index(drop=True)

    benchmark["Benchmark_Rank"] = benchmark.index + 1

    return benchmark


# Benchmark Summary
def get_benchmark_summary(benchmark):

    benchmark_summary = (
        benchmark[COMPARISON_METRICS]
        .mean()
        .to_frame(name="Benchmark")
        .reset_index()
        .rename(columns={"index": "Metric"})
    )

    return benchmark_summary

def compare_to_benchmark(listing_id, benchmark_summary):

    # Retrieve target KPIs
    target = master.loc[
        master["listing_id"] == listing_id,
        [
            "listing_id",
            "StayScore",
            "HostTrust",
            "ListingIQ",
            "ExperienceIQ"
        ]
    ].copy()

    # Retrieve target business metrics
    target = target.merge(
        similarity_df[
            [
                "listing_id",
                "price",
                "amenities_count"
            ]
        ],
        on="listing_id",
        how="left"
    )

    target = target.iloc[0]

    # Build comparison table
    comparison = benchmark_summary.copy()

    target_values = []

    for metric in comparison["Metric"]:
        target_values.append(target[metric])

    comparison["Target"] = target_values

    comparison["Difference"] = (
        comparison["Target"] - comparison["Benchmark"]
    )

    comparison["Gap (%)"] = (
        comparison["Difference"] /
        comparison["Benchmark"] * 100
    ).round(2)

    return comparison


# Generate Recommendations
def generate_recommendations(comparison):

    recommendations = comparison.copy()

    priorities = []
    recommendation_text = []

    for _, row in recommendations.iterrows():

        metric = row["Metric"]
        benchmark = row["Benchmark"]
        target = row["Target"]
        gap = row["Gap (%)"]

        # -----------------------------------------
        # Missing KPI Check
        # -----------------------------------------

        if pd.isna(target) or pd.isna(benchmark) or pd.isna(gap):

            priorities.append("Unavailable")

            recommendation_text.append(
                f"{metric} could not be evaluated because insufficient review data was available to calculate this performance metric."
            )

            continue

        # -----------------------------------------
        # Priority Assignment
        # -----------------------------------------

        if gap >= 0:
            priority = "Strength"

        elif gap <= -20:
            priority = "High"

        elif gap <= -10:
            priority = "Medium"

        else:
            priority = "Low"

        priorities.append(priority)

        # -----------------------------------------
        # Dynamic Recommendation
        # -----------------------------------------

        if metric == "StayScore":

            if gap < 0:
                text = (
                    f"Your StayScore is {target:.2f} compared to the benchmark "
                    f"of {benchmark:.2f} ({abs(gap):.2f}% lower). "
                    "Improving your overall listing performance will help you compete "
                    "with similar high-performing listings."
                )
            else:
                text = (
                    f"Your StayScore is {gap:.2f}% above the benchmark. "
                    "Continue maintaining your overall listing quality."
                )

        elif metric == "HostTrust":

            if gap < 0:
                text = (
                    f"Your HostTrust is {target:.2f} compared to the benchmark "
                    f"of {benchmark:.2f}. "
                    "Improving responsiveness, profile completeness and guest confidence "
                    "can further strengthen your performance."
                )
            else:
                text = (
                    f"Your HostTrust exceeds the benchmark by {gap:.2f}%. "
                    "Continue maintaining excellent host standards."
                )

        elif metric == "ListingIQ":

            if gap < 0:
                text = (
                    f"Your ListingIQ is {target:.2f} compared to the benchmark "
                    f"of {benchmark:.2f}. "
                    "Enhancing your listing description, photos and amenities can "
                    "improve your competitiveness."
                )
            else:
                text = (
                    f"Your ListingIQ is {gap:.2f}% above the benchmark. "
                    "Maintain the quality and completeness of your listing."
                )

        elif metric == "ExperienceIQ":

            if gap < 0:
                text = (
                    f"Your ExperienceIQ is {target:.2f} compared to the benchmark "
                    f"of {benchmark:.2f}. "
                    "Focus on maintaining excellent guest reviews and service quality."
                )
            else:
                text = (
                    f"Your ExperienceIQ exceeds comparable listings by {gap:.2f}%. "
                    "Keep delivering an outstanding guest experience."
                )

        elif metric == "price":

            if gap < 0:
                text = (
                    f"Your average nightly price is {target:.2f}, while similar "
                    f"high-performing listings average {benchmark:.2f}. "
                    "After improving your listing quality, consider reviewing your pricing strategy."
                )
            else:
                text = (
                    f"Your average nightly price is {target:.2f}, approximately "
                    f"{gap:.2f}% above comparable listings. Ensure the premium is supported "
                    "by superior listing quality and guest experience."
                )

        elif metric == "amenities_count":

            if gap < 0:
                text = (
                    f"Benchmark listings provide an average of {benchmark:.0f} amenities, "
                    f"while your listing offers {target:.0f}. "
                    "Adding more amenities could improve your competitiveness."
                )
            else:
                text = (
                    f"Your listing offers {target:.0f} amenities, which is above the "
                    "benchmark. Continue maintaining this advantage."
                )

        recommendation_text.append(text)

    recommendations["Priority"] = priorities
    recommendations["Recommendation"] = recommendation_text

    # -----------------------------------------
    # Sort by Priority
    # -----------------------------------------

    priority_order = {
        "High": 1,
        "Medium": 2,
        "Low": 3,
        "Strength": 4,
        "Unavailable": 5
    }

    recommendations["Priority_Order"] = (
        recommendations["Priority"].map(priority_order)
    )

    recommendations = recommendations.sort_values(
        by="Priority_Order"
    )

    recommendations = recommendations.drop(
        columns="Priority_Order"
    )

    recommendations = recommendations.reset_index(drop=True)

    return recommendations





# =====================================================
# Generate Complete Listing Report
# =====================================================

def generate_listing_report(listing_id):

    # Step 0: Retrieve Listing Information
    listing_info = (
        listings_clean.loc[
            listings_clean["listing_id"] == listing_id
        ]
        .iloc[0]
        .to_dict()
    )

    # Step 1: Build Benchmark
    benchmark = build_benchmark(listing_id)

    # Step 2: Generate Benchmark Summary
    benchmark_summary = get_benchmark_summary(benchmark)

    # Step 3: Compare Listing to Benchmark
    comparison = compare_to_benchmark(
        listing_id,
        benchmark_summary
    )

    # Step 4: Generate Recommendations
    recommendations = generate_recommendations(comparison)

    # Step 5: Return Complete Report
    return {
        "listing_info": listing_info,
        "benchmark": benchmark,
        "benchmark_summary": benchmark_summary,
        "comparison": comparison,
        "recommendations": recommendations
    }





