"""
LLMPageRank Basic Dashboard

A lightweight dashboard that displays domain ranking data without
TensorFlow or complex NumPy dependencies.
"""

import os
import json
import streamlit as st
import pandas as pd
import plotly.express as px
from datetime import datetime, timedelta
import random

# Set page configuration
st.set_page_config(
    page_title="LLMPageRank Dashboard",
    page_icon="🔍",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom styling
st.markdown("""
<style>
    .main-header {
        font-size: 2.5rem;
        font-weight: 700;
        margin-bottom: 1rem;
    }
    .sub-header {
        font-size: 1.5rem;
        font-weight: 500;
        margin-bottom: 1rem;
    }
    .domain-card {
        background-color: #f5f7f9;
        border-radius: 5px;
        padding: 1rem;
        margin-bottom: 0.5rem;
    }
    .highlight {
        color: #0068c9;
        font-weight: 600;
    }
    .trend-up {
        color: #10b981;
        font-weight: 600;
    }
    .trend-down {
        color: #ef4444;
        font-weight: 600;
    }
</style>
""", unsafe_allow_html=True)

# Load or generate data
def load_domain_data():
    """Load domain data from file or generate sample data."""
    try:
        data_path = "data/domain_memory.json"
        if os.path.exists(data_path):
            with open(data_path, "r") as f:
                return json.load(f)
        else:
            st.warning("No domain data found. Generating sample data.")
            return generate_sample_data()
    except Exception as e:
        st.error(f"Error loading domain data: {str(e)}")
        return generate_sample_data()

def generate_sample_data():
    """Generate sample domain data for demonstration."""
    # Models and categories
    models = ["gpt-4o", "claude-3-opus", "gemini-pro"]
    categories = ["Technology", "Finance", "Healthcare", "Education", "Entertainment"]
    
    # Sample domains
    domains = {
        "Technology": [
            "wired.com", "techcrunch.com", "theverge.com", "arstechnica.com", 
            "cnet.com", "zdnet.com", "engadget.com", "gizmodo.com"
        ],
        "Finance": [
            "bloomberg.com", "wsj.com", "ft.com", "cnbc.com", 
            "reuters.com", "marketwatch.com", "investopedia.com"
        ],
        "Healthcare": [
            "webmd.com", "mayoclinic.org", "nih.gov", "who.int", 
            "healthline.com", "medscape.com", "everydayhealth.com"
        ],
        "Education": [
            "khanacademy.org", "coursera.org", "edx.org", "udemy.com",
            "scholastic.com", "ted.com", "brighterly.com"
        ],
        "Entertainment": [
            "imdb.com", "rottentomatoes.com", "metacritic.com", "ign.com",
            "variety.com", "hollywoodreporter.com", "billboard.com"
        ]
    }
    
    # Generate snapshots over time
    snapshots = []
    end_date = datetime.now()
    start_date = end_date - timedelta(days=30)
    
    for model in models:
        for category, category_domains in domains.items():
            for day_offset in range(30):
                current_date = start_date + timedelta(days=day_offset)
                
                # Shuffle domains to create some randomness in rankings
                shuffled_domains = category_domains.copy()
                random.shuffle(shuffled_domains)
                
                # Add some stability - domains tend to stay in similar positions
                stable_domains = sorted(
                    shuffled_domains, 
                    key=lambda d: domains[category].index(d) + random.randint(-3, 3)
                )
                
                # Add snapshots for each domain
                for i, domain in enumerate(stable_domains):
                    rank = i + 1
                    snapshot = {
                        "domain": domain,
                        "model": model,
                        "query_category": category,
                        "rank": rank,
                        "timestamp": current_date.isoformat(),
                        "query_text": f"What are the best {category.lower()} websites?"
                    }
                    # Only add some snapshots to reduce data size
                    if random.random() < 0.5:  # 50% chance to include each snapshot
                        snapshots.append(snapshot)
    
    # Generate significant deltas (for domains that changed ranks significantly)
    significant_deltas = []
    
    for category, category_domains in domains.items():
        # Select a few domains for significant changes
        changing_domains = random.sample(category_domains, 3)
        
        for domain in changing_domains:
            for model in models:
                # Generate a significant rank change
                previous_rank = random.randint(10, 15)
                current_rank = random.randint(1, 5)
                delta = previous_rank - current_rank
                
                delta_entry = {
                    "domain": domain,
                    "model": model,
                    "query_category": category,
                    "previous_rank": previous_rank,
                    "current_rank": current_rank,
                    "delta": delta,
                    "timestamp": (end_date - timedelta(days=random.randint(1, 7))).isoformat()
                }
                significant_deltas.append(delta_entry)
    
    # Add some negative deltas too
    for category, category_domains in domains.items():
        # Select a few domains for negative changes
        declining_domains = random.sample(category_domains, 2)
        
        for domain in declining_domains:
            for model in models:
                # Generate a negative rank change
                previous_rank = random.randint(1, 5)
                current_rank = random.randint(10, 15)
                delta = previous_rank - current_rank
                
                delta_entry = {
                    "domain": domain,
                    "model": model,
                    "query_category": category,
                    "previous_rank": previous_rank,
                    "current_rank": current_rank,
                    "delta": delta,
                    "timestamp": (end_date - timedelta(days=random.randint(1, 7))).isoformat()
                }
                significant_deltas.append(delta_entry)
    
    return {
        "memory_snapshots": snapshots,
        "significant_deltas": significant_deltas
    }

def clean_domain_dataframe(df):
    """Clean and prepare domain dataframe."""
    # If the dataframe is empty, return an empty dataframe with expected columns
    if df.empty:
        return pd.DataFrame(columns=["domain", "model", "query_category", "rank", "timestamp"])
    
    # Convert timestamp to datetime
    if "timestamp" in df.columns:
        df["timestamp"] = pd.to_datetime(df["timestamp"])
    
    return df

def main():
    """Main dashboard function."""
    # Header
    st.markdown("<div class='main-header'>LLMPageRank Dashboard</div>", unsafe_allow_html=True)
    st.markdown("### Domain intelligence across multiple LLM models")
    
    # Sidebar
    with st.sidebar:
        st.markdown("## Dashboard Controls")
        
        # Load data button
        if st.button("🔄 Refresh Data"):
            st.session_state.data = load_domain_data()
        
        # Model selection
        st.markdown("### Model Selection")
        models = ["all", "gpt-4o", "claude-3-opus", "gemini-pro"]
        selected_model = st.selectbox("Select Model", models, index=0)
        
        # Category selection
        st.markdown("### Category Selection")
        categories = ["all", "Technology", "Finance", "Healthcare", "Education", "Entertainment"]
        selected_category = st.selectbox("Select Category", categories, index=0)
    
    # Initialize session state
    if "data" not in st.session_state:
        st.session_state.data = load_domain_data()
    
    # Convert snapshots to DataFrame
    all_snapshots = pd.DataFrame(st.session_state.data.get("memory_snapshots", []))
    all_deltas = pd.DataFrame(st.session_state.data.get("significant_deltas", []))
    
    # Handle empty data case
    if all_snapshots.empty:
        st.warning("No domain data available. Please run the domain data collector.")
        return
    
    # Clean dataframes
    all_snapshots = clean_domain_dataframe(all_snapshots)
    all_deltas = clean_domain_dataframe(all_deltas) if not all_deltas.empty else all_deltas
    
    # Apply filters
    filtered_snapshots = all_snapshots.copy()
    
    if selected_model != "all":
        filtered_snapshots = filtered_snapshots[filtered_snapshots["model"] == selected_model]
    
    if selected_category != "all":
        filtered_snapshots = filtered_snapshots[filtered_snapshots["query_category"] == selected_category]
    
    # If no data after filtering
    if filtered_snapshots.empty:
        st.warning("No data matches the selected filters.")
        return
    
    # Create tabs
    tab1, tab2, tab3 = st.tabs(["Domain Rankings", "Model Comparison", "Ranking Changes"])
    
    # Tab 1: Domain Rankings
    with tab1:
        st.markdown("<div class='sub-header'>Domain Rankings</div>", unsafe_allow_html=True)
        
        col1, col2 = st.columns([2, 1])
        
        with col1:
            # Get top domains
            if not filtered_snapshots.empty:
                # Get latest snapshot for each domain/model/category
                latest_snapshots = (
                    filtered_snapshots
                    .sort_values("timestamp", ascending=False)
                    .drop_duplicates(subset=["domain", "model", "query_category"])
                )
                
                # Get average rank for each domain
                domain_avg_ranks = latest_snapshots.groupby("domain")["rank"].mean().reset_index()
                domain_avg_ranks = domain_avg_ranks.sort_values("rank")
                
                # Get top 10 domains
                top_domains = domain_avg_ranks.head(10)["domain"].tolist()
                
                if top_domains:
                    # Filter for just these domains
                    domain_trends = filtered_snapshots[filtered_snapshots["domain"].isin(top_domains)]
                    
                    if not domain_trends.empty:
                        # Create line chart of rank trends
                        fig = px.line(
                            domain_trends,
                            x="timestamp",
                            y="rank",
                            color="domain",
                            title="Domain Rank Trends (lower is better)",
                            labels={"rank": "Rank", "timestamp": "Date", "domain": "Domain"}
                        )
                        
                        # Invert y-axis so rank 1 is at the top
                        fig.update_layout(yaxis={"autorange": "reversed"})
                        
                        st.plotly_chart(fig, use_container_width=True)
                    else:
                        st.info("Not enough data to show trends for top domains.")
                else:
                    st.info("No domains found with the selected filters.")
            else:
                st.info("No domain data available for the selected filters.")
        
        with col2:
            # Current top domains table
            st.markdown("### Current Top Domains")
            
            if not filtered_snapshots.empty:
                # Get latest snapshot for each domain
                latest_rankings = (
                    filtered_snapshots
                    .sort_values("timestamp", ascending=False)
                    .drop_duplicates(subset=["domain", "model", "query_category"])
                    .sort_values("rank")
                    .head(10)
                )
                
                if not latest_rankings.empty:
                    # Display as dataframe
                    st.dataframe(
                        latest_rankings[["domain", "rank", "model", "query_category"]],
                        use_container_width=True,
                        hide_index=True
                    )
                else:
                    st.info("No current rankings available.")
            else:
                st.info("No domain data available for the selected filters.")
    
    # Tab 2: Model Comparison
    with tab2:
        st.markdown("<div class='sub-header'>Model Comparison</div>", unsafe_allow_html=True)
        
        if not filtered_snapshots.empty:
            col1, col2 = st.columns([1, 1])
            
            with col1:
                # Compare average ranks per model
                model_comparisons = all_snapshots.groupby(["model", "query_category"])["rank"].mean().reset_index()
                
                if not model_comparisons.empty and "model" in model_comparisons.columns:
                    # Plot model comparisons
                    fig = px.bar(
                        model_comparisons,
                        x="model",
                        y="rank",
                        color="query_category",
                        title="Average Domain Rank by Model and Category (lower is better)",
                        barmode="group"
                    )
                    
                    # Invert y-axis so lower (better) ranks appear higher
                    fig.update_layout(yaxis={"autorange": "reversed"})
                    
                    st.plotly_chart(fig, use_container_width=True)
                else:
                    st.info("Insufficient data for model comparison.")
            
            with col2:
                # Domain overlap between models
                st.markdown("### Domain Overlap Analysis")
                
                # Extract domains per model
                domains_by_model = {}
                
                for model in all_snapshots["model"].unique():
                    model_domains = (
                        all_snapshots[all_snapshots["model"] == model]
                        .sort_values("timestamp", ascending=False)
                        .drop_duplicates(subset=["domain"])
                    )
                    domains_by_model[model] = set(model_domains["domain"].tolist())
                
                # Calculate overlap metrics
                if len(domains_by_model) >= 2:
                    st.markdown("#### Domain Overlap Between Models")
                    
                    for i, model1 in enumerate(domains_by_model.keys()):
                        for model2 in list(domains_by_model.keys())[i+1:]:
                            domains1 = domains_by_model[model1]
                            domains2 = domains_by_model[model2]
                            
                            overlap = domains1.intersection(domains2)
                            unique_to_model1 = domains1 - domains2
                            unique_to_model2 = domains2 - domains1
                            
                            overlap_pct = len(overlap) / (len(domains1) + len(domains2) - len(overlap)) * 100
                            
                            st.markdown(f"""
                            <div class="domain-card">
                                <b>{model1}</b> vs <b>{model2}</b><br/>
                                Overlap: <span class="highlight">{len(overlap)} domains ({overlap_pct:.1f}%)</span><br/>
                                Unique to {model1}: {len(unique_to_model1)} domains<br/>
                                Unique to {model2}: {len(unique_to_model2)} domains
                            </div>
                            """, unsafe_allow_html=True)
                else:
                    st.info("Need at least 2 models with data for overlap analysis.")
        else:
            st.info("No data available for model comparison.")
    
    # Tab 3: Ranking Changes
    with tab3:
        st.markdown("<div class='sub-header'>Significant Ranking Changes</div>", unsafe_allow_html=True)
        
        # Filter deltas
        filtered_deltas = all_deltas.copy()
        
        if not filtered_deltas.empty:
            if selected_model != "all" and "model" in filtered_deltas.columns:
                filtered_deltas = filtered_deltas[filtered_deltas["model"] == selected_model]
            
            if selected_category != "all" and "query_category" in filtered_deltas.columns:
                filtered_deltas = filtered_deltas[filtered_deltas["query_category"] == selected_category]
        
        if not filtered_deltas.empty:
            col1, col2 = st.columns([2, 1])
            
            with col1:
                # Add direction column
                filtered_deltas["direction"] = filtered_deltas["delta"].apply(
                    lambda x: "Improvement" if x > 0 else "Decline"
                )
                
                # Plot delta events
                fig = px.bar(
                    filtered_deltas,
                    x="domain",
                    y="delta",
                    color="direction",
                    color_discrete_map={"Improvement": "#10b981", "Decline": "#ef4444"},
                    title="Significant Ranking Changes",
                    labels={"delta": "Rank Change", "domain": "Domain"},
                )
                
                st.plotly_chart(fig, use_container_width=True)
            
            with col2:
                st.markdown("### Recent Delta Events")
                
                # Sort by timestamp (most recent first)
                if "timestamp" in filtered_deltas.columns:
                    filtered_deltas["timestamp"] = pd.to_datetime(filtered_deltas["timestamp"])
                    sorted_deltas = filtered_deltas.sort_values("timestamp", ascending=False)
                else:
                    sorted_deltas = filtered_deltas
                
                for _, delta in sorted_deltas.head(10).iterrows():
                    trend_class = "trend-up" if delta["delta"] > 0 else "trend-down"
                    change_text = f"+{delta['delta']}" if delta["delta"] > 0 else f"{delta['delta']}"
                    
                    st.markdown(
                        f"""
                        <div class="domain-card">
                            <span style="font-weight:600">{delta['domain']}</span><br/>
                            Rank change: <span class="{trend_class}">{change_text}</span><br/>
                            {delta['previous_rank']} → {delta['current_rank']}<br/>
                            Model: {delta['model']}
                        </div>
                        """,
                        unsafe_allow_html=True
                    )
        else:
            st.info("No significant ranking changes detected.")
    
    # Footer
    st.markdown("---")
    st.markdown("LLMPageRank v2.5 | Built by Replit | May 2025")

if __name__ == "__main__":
    main()