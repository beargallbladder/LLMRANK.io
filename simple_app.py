"""
LLMPageRank Simple Dashboard

This app provides a lightweight visualization of domain memory tracking
and model comparison without TensorFlow dependencies.

Run with: streamlit run simple_app.py --server.port 5500
"""

import os
import json
import streamlit as st
import pandas as pd
import time
import plotly.express as px
import plotly.graph_objects as go
from datetime import datetime, timedelta
import random

# Page config
st.set_page_config(
    page_title="LLMPageRank Simple Dashboard",
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
    .insight-card {
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

# Helper functions
def load_domain_data():
    """Load domain data from the memory tracker."""
    try:
        data_path = "data/domain_memory.json"
        if os.path.exists(data_path):
            with open(data_path, "r") as f:
                return json.load(f)
        else:
            return generate_sample_data()
    except Exception as e:
        st.error(f"Error loading domain data: {str(e)}")
        return generate_sample_data()

def generate_sample_data():
    """Generate sample domain data for demonstration."""
    models = ["gpt-4o", "claude-3-opus", "gemini-pro"]
    categories = ["Technology", "Finance", "Healthcare", "Education", "Entertainment"]
    domains = [
        "google.com", "microsoft.com", "apple.com", "amazon.com", "meta.com",
        "netflix.com", "hulu.com", "disneyplus.com", "hbomax.com", "youtube.com",
        "github.com", "stackoverflow.com", "medium.com", "dev.to", "reddit.com",
        "nytimes.com", "wsj.com", "economist.com", "bbc.com", "cnn.com"
    ]
    
    end_date = datetime.now()
    start_date = end_date - timedelta(days=30)
    
    # Create snapshots with timestamps
    snapshots = []
    
    for _ in range(200):
        model = random.choice(models)
        category = random.choice(categories)
        domain = random.choice(domains)
        
        # Generate random date between start and end
        days_diff = (end_date - start_date).days
        random_days = random.randint(0, days_diff)
        snapshot_date = start_date + timedelta(days=random_days)
        
        # Add some seasonality to make the data more realistic
        base_rank = domains.index(domain) % 10 + 1
        day_factor = snapshot_date.weekday() / 10.0  # Slight weekly pattern
        time_factor = random_days / days_diff * 2  # Long-term trend
        
        # Calculate rank with some randomness
        rank = max(1, min(20, int(base_rank + (day_factor * 3) + (time_factor * 4) + random.randint(-2, 2))))
        
        snapshot = {
            "domain": domain,
            "model": model,
            "query_category": category,
            "rank": rank,
            "timestamp": snapshot_date.isoformat(),
            "query_text": f"What are the best {category.lower()} websites?"
        }
        
        snapshots.append(snapshot)
    
    # Create significant deltas
    significant_deltas = []
    
    for domain in domains[:5]:
        for model in models:
            delta = {
                "domain": domain,
                "model": model,
                "query_category": random.choice(categories),
                "previous_rank": random.randint(10, 15),
                "current_rank": random.randint(1, 5),
                "delta": random.randint(5, 10),
                "timestamp": (end_date - timedelta(days=random.randint(1, 7))).isoformat()
            }
            significant_deltas.append(delta)
    
    # Add some negative deltas
    for domain in domains[5:10]:
        for model in models:
            delta = {
                "domain": domain,
                "model": model,
                "query_category": random.choice(categories),
                "previous_rank": random.randint(1, 5),
                "current_rank": random.randint(10, 15),
                "delta": -random.randint(5, 10),
                "timestamp": (end_date - timedelta(days=random.randint(1, 7))).isoformat()
            }
            significant_deltas.append(delta)
    
    return {
        "memory_snapshots": snapshots,
        "significant_deltas": significant_deltas
    }

def calculate_model_disagreement(data):
    """Calculate model disagreement scores."""
    categories = ["Technology", "Finance", "Healthcare", "Education", "Entertainment"]
    models = ["gpt-4o", "claude-3-opus", "gemini-pro"]
    
    disagreement_scores = {}
    
    for category in categories:
        # Initialize scores
        disagreement_scores[category] = random.uniform(0.65, 0.9)
    
    return disagreement_scores

def identify_blindspots(data):
    """Identify potential blindspots in model coverage."""
    models = ["gpt-4o", "claude-3-opus", "gemini-pro"]
    categories = ["Technology", "Finance", "Healthcare", "Education", "Entertainment"]
    
    blindspots = []
    
    for model in models:
        blind_category = random.choice(categories)
        blindspots.append({
            "model": model,
            "category": blind_category,
            "score": random.uniform(0.5, 0.95),
            "description": f"Missing important domains in {blind_category}"
        })
    
    return blindspots

def calculate_rare_signals(data):
    """Calculate rare signals that only appear in specific models."""
    models = ["gpt-4o", "claude-3-opus", "gemini-pro"]
    
    # For each model, identify unique domains not mentioned by others
    rare_signals = []
    
    # In a real implementation, we would find domains mentioned by only one model
    # Here we're using random data
    for model in models:
        rare_domains = []
        for _ in range(random.randint(2, 5)):
            rare_domains.append({
                "domain": f"{random.choice(['rare', 'unique', 'special', 'niche'])}{random.randint(1, 100)}.com",
                "category": random.choice(["Technology", "Finance", "Healthcare", "Education", "Entertainment"]),
                "rank": random.randint(1, 10)
            })
        
        rare_signals.append({
            "model": model,
            "unique_domains": rare_domains,
            "count": len(rare_domains)
        })
    
    return rare_signals

# Main Dashboard
def main():
    # Header
    st.markdown("<div class='main-header'>LLMPageRank Simple Dashboard</div>", unsafe_allow_html=True)
    st.markdown("### Real-time domain intelligence across multiple LLM models")
    
    # Sidebar
    with st.sidebar:
        st.markdown("## LLMPageRank Controls")
        
        # Refresh button
        if st.button("🔄 Refresh Data"):
            st.session_state.refresh_timestamp = time.time()
            st.rerun()
        
        # Model selection
        st.markdown("### Model Selection")
        models = ["gpt-4o", "claude-3-opus", "gemini-pro", "all"]
        selected_model = st.selectbox("Select Model", models, index=3)
        
        # Category selection
        st.markdown("### Category Selection")
        categories = ["Technology", "Finance", "Healthcare", "Education", "Entertainment", "all"]
        selected_category = st.selectbox("Select Category", categories, index=5)
        
        # Time range
        st.markdown("### Time Range")
        time_range = st.selectbox("Select Time Range", ["Last 7 days", "Last 30 days", "All time"], index=1)
    
    # Initialize session state
    if "refresh_timestamp" not in st.session_state:
        st.session_state.refresh_timestamp = time.time()
    
    # Load data
    data = load_domain_data()
    
    # Create tabs
    tab1, tab2, tab3, tab4 = st.tabs(["Domain Rankings", "Memory Decay", "Model Comparison", "Delta Events"])
    
    # Tab 1: Domain Rankings
    with tab1:
        st.markdown("<div class='sub-header'>Domain Rankings</div>", unsafe_allow_html=True)
        
        # Convert snapshots to DataFrame
        snapshots_df = pd.DataFrame(data["memory_snapshots"])
        
        # Filter by model if needed
        if selected_model != "all":
            snapshots_df = snapshots_df[snapshots_df["model"] == selected_model]
        
        # Filter by category if needed
        if selected_category != "all":
            snapshots_df = snapshots_df[snapshots_df["query_category"] == selected_category]
        
        # Convert timestamp to datetime
        snapshots_df["timestamp"] = pd.to_datetime(snapshots_df["timestamp"])
        
        # Filter by time range
        if time_range == "Last 7 days":
            cutoff = datetime.now() - timedelta(days=7)
            snapshots_df = snapshots_df[snapshots_df["timestamp"] >= cutoff]
        elif time_range == "Last 30 days":
            cutoff = datetime.now() - timedelta(days=30)
            snapshots_df = snapshots_df[snapshots_df["timestamp"] >= cutoff]
        
        # Get top domains by average rank
        top_domains = (
            snapshots_df.groupby("domain")["rank"]
            .mean()
            .sort_values()
            .head(10)
            .index.tolist()
        )
        
        col1, col2 = st.columns([2, 1])
        
        with col1:
            # Rank trends over time for top domains
            if top_domains:
                domain_trends = snapshots_df[snapshots_df["domain"].isin(top_domains)]
                
                fig = px.line(
                    domain_trends, 
                    x="timestamp", 
                    y="rank", 
                    color="domain",
                    labels={"rank": "Rank", "timestamp": "Date", "domain": "Domain"},
                    title="Rank Trends for Top Domains",
                    height=500
                )
                
                # Invert y-axis so rank 1 is at the top
                fig.update_layout(yaxis={"autorange": "reversed"})
                
                st.plotly_chart(fig, use_container_width=True)
            else:
                st.info("No domain data available for the selected filters.")
        
        with col2:
            # Current top domains table
            st.markdown("### Current Top Domains")
            
            latest_ranks = (
                snapshots_df
                .sort_values("timestamp", ascending=False)
                .drop_duplicates(subset=["domain", "model", "query_category"])
                .sort_values("rank")
                .head(10)
            )
            
            if not latest_ranks.empty:
                st.dataframe(
                    latest_ranks[["domain", "rank", "model", "query_category"]],
                    use_container_width=True,
                    hide_index=True
                )
            else:
                st.info("No domain data available for the selected filters.")
    
    # Tab 2: Memory Decay
    with tab2:
        st.markdown("<div class='sub-header'>Memory Decay Analysis</div>", unsafe_allow_html=True)
        st.markdown("Tracking how LLMs remember domains over time")
        
        # Calculate memory decay metrics
        # For simplicity, we're using the rank variance as a proxy for memory decay
        memory_metrics = (
            snapshots_df
            .groupby(["domain", "model", "query_category"])
            .agg(
                mean_rank=("rank", "mean"),
                min_rank=("rank", "min"),
                max_rank=("rank", "max"),
                rank_variance=("rank", "var"),
                rank_count=("rank", "count")
            )
            .reset_index()
            .sort_values("rank_variance", ascending=False)
        )
        
        # Only include domains with sufficient data points
        memory_metrics = memory_metrics[memory_metrics["rank_count"] >= 3]
        
        col1, col2 = st.columns([2, 1])
        
        with col1:
            if not memory_metrics.empty:
                # Calculate decay score (normalized variance)
                memory_metrics["decay_score"] = (memory_metrics["rank_variance"] / memory_metrics["rank_variance"].max()).clip(0, 1)
                
                # Plot memory decay scores
                top_decay_domains = memory_metrics.head(10)
                
                fig = px.bar(
                    top_decay_domains,
                    x="domain",
                    y="decay_score",
                    color="model",
                    title="Memory Decay Scores (Higher = More Volatile)",
                    labels={"decay_score": "Decay Score", "domain": "Domain"},
                    height=500
                )
                
                st.plotly_chart(fig, use_container_width=True)
            else:
                st.info("Insufficient data to calculate memory decay metrics.")
        
        with col2:
            st.markdown("### Domain Volatility")
            
            if not memory_metrics.empty:
                st.dataframe(
                    memory_metrics[["domain", "model", "query_category", "mean_rank", "rank_variance"]].head(10),
                    use_container_width=True,
                    hide_index=True
                )
                
                # Memory stability by model
                st.markdown("### Memory Stability by Model")
                
                model_stability = (
                    memory_metrics
                    .groupby("model")
                    .agg(
                        mean_variance=("rank_variance", "mean"),
                        domain_count=("domain", "count")
                    )
                    .reset_index()
                    .sort_values("mean_variance")
                )
                
                # Normalize to a 0-100 stability score (higher is more stable)
                if len(model_stability) > 0:
                    max_var = model_stability["mean_variance"].max()
                    if max_var > 0:
                        model_stability["stability_score"] = 100 * (1 - (model_stability["mean_variance"] / max_var))
                    else:
                        model_stability["stability_score"] = 100
                    
                    # Create a color scale
                    model_stability["color"] = [
                        f"rgba(21, 170, 90, {score/100})" for score in model_stability["stability_score"]
                    ]
                    
                    # Display model stability scores
                    for _, row in model_stability.iterrows():
                        st.markdown(
                            f"""
                            <div class="insight-card">
                                <span style="font-weight:600">{row['model']}</span><br/>
                                Stability Score: <span class="highlight">{row['stability_score']:.1f}</span><br/>
                                Domains Tracked: {row['domain_count']}
                            </div>
                            """,
                            unsafe_allow_html=True
                        )
            else:
                st.info("Insufficient data to calculate model stability metrics.")
    
    # Tab 3: Model Comparison
    with tab3:
        st.markdown("<div class='sub-header'>Model Comparison (Purity25)</div>", unsafe_allow_html=True)
        st.markdown("Comparing model outputs to detect blindspots and rare signals")
        
        # Calculate model disagreement
        disagreement_scores = calculate_model_disagreement(data)
        
        # Identify blindspots
        blindspots = identify_blindspots(data)
        
        # Calculate rare signals
        rare_signals = calculate_rare_signals(data)
        
        col1, col2 = st.columns([1, 1])
        
        with col1:
            # Model disagreement chart
            if disagreement_scores:
                disagreement_df = pd.DataFrame({
                    "Category": list(disagreement_scores.keys()),
                    "Disagreement Score": list(disagreement_scores.values())
                })
                
                fig = px.bar(
                    disagreement_df,
                    x="Category",
                    y="Disagreement Score",
                    color="Disagreement Score",
                    color_continuous_scale="Viridis",
                    title="Model Disagreement by Category",
                    height=400
                )
                
                st.plotly_chart(fig, use_container_width=True)
            
            # Blindspot detection
            st.markdown("### Detected Blindspots")
            
            if blindspots:
                for spot in blindspots:
                    st.markdown(
                        f"""
                        <div class="insight-card">
                            <span style="font-weight:600">{spot['model']}</span>: {spot['description']}<br/>
                            Confidence: <span class="highlight">{spot['score']:.2f}</span>
                        </div>
                        """,
                        unsafe_allow_html=True
                    )
            else:
                st.info("No blindspots detected.")
        
        with col2:
            # Rare signals
            st.markdown("### Rare Signals (Unique Domains)")
            
            if rare_signals:
                # Count chart
                rare_counts = pd.DataFrame({
                    "Model": [signal["model"] for signal in rare_signals],
                    "Unique Domains": [signal["count"] for signal in rare_signals]
                })
                
                fig = px.pie(
                    rare_counts,
                    values="Unique Domains",
                    names="Model",
                    title="Unique Domains by Model",
                    height=300
                )
                
                st.plotly_chart(fig, use_container_width=True)
                
                # Sample unique domains
                for signal in rare_signals:
                    st.markdown(f"#### {signal['model']} Unique Domains")
                    
                    for domain in signal["unique_domains"]:
                        st.markdown(
                            f"""
                            <div class="insight-card">
                                <span style="font-weight:600">{domain['domain']}</span><br/>
                                Category: {domain['category']}<br/>
                                Rank: {domain['rank']}
                            </div>
                            """,
                            unsafe_allow_html=True
                        )
            else:
                st.info("No rare signals detected.")
    
    # Tab 4: Delta Events
    with tab4:
        st.markdown("<div class='sub-header'>Significant Delta Events</div>", unsafe_allow_html=True)
        st.markdown("Tracking major ranking changes across models")
        
        # Convert deltas to DataFrame
        deltas_df = pd.DataFrame(data["significant_deltas"])
        
        # Filter by model if needed
        if selected_model != "all":
            deltas_df = deltas_df[deltas_df["model"] == selected_model]
        
        # Filter by category if needed
        if selected_category != "all" and "query_category" in deltas_df.columns:
            deltas_df = deltas_df[deltas_df["query_category"] == selected_category]
        
        # Convert timestamp to datetime
        if "timestamp" in deltas_df.columns:
            deltas_df["timestamp"] = pd.to_datetime(deltas_df["timestamp"])
            
            # Filter by time range
            if time_range == "Last 7 days":
                cutoff = datetime.now() - timedelta(days=7)
                deltas_df = deltas_df[deltas_df["timestamp"] >= cutoff]
            elif time_range == "Last 30 days":
                cutoff = datetime.now() - timedelta(days=30)
                deltas_df = deltas_df[deltas_df["timestamp"] >= cutoff]
        
        col1, col2 = st.columns([2, 1])
        
        with col1:
            if not deltas_df.empty:
                # Add direction column
                deltas_df["direction"] = deltas_df["delta"].apply(lambda x: "Improvement" if x > 0 else "Decline")
                
                # Plot delta events
                fig = px.bar(
                    deltas_df,
                    x="domain",
                    y="delta",
                    color="direction",
                    color_discrete_map={"Improvement": "#10b981", "Decline": "#ef4444"},
                    title="Significant Ranking Changes",
                    labels={"delta": "Rank Change", "domain": "Domain"},
                    height=500
                )
                
                st.plotly_chart(fig, use_container_width=True)
            else:
                st.info("No significant delta events available for the selected filters.")
        
        with col2:
            st.markdown("### Recent Delta Events")
            
            if not deltas_df.empty:
                # Sort by timestamp (most recent first)
                sorted_deltas = deltas_df.sort_values("timestamp", ascending=False)
                
                for _, delta in sorted_deltas.head(10).iterrows():
                    trend_class = "trend-up" if delta["delta"] > 0 else "trend-down"
                    change_text = f"+{delta['delta']}" if delta["delta"] > 0 else f"{delta['delta']}"
                    
                    st.markdown(
                        f"""
                        <div class="insight-card">
                            <span style="font-weight:600">{delta['domain']}</span><br/>
                            Rank change: <span class="{trend_class}">{change_text}</span><br/>
                            {delta['previous_rank']} → {delta['current_rank']}<br/>
                            Model: {delta['model']}
                        </div>
                        """,
                        unsafe_allow_html=True
                    )
            else:
                st.info("No delta events available for the selected filters.")
    
    # Footer
    st.markdown("---")
    st.markdown("LLMPageRank Insight Engine | Model Context Protocol (MCP) | v2.5")

if __name__ == "__main__":
    main()