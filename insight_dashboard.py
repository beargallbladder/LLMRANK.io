"""
Insight Dashboard

This Streamlit application provides the free tier dashboard for the LLMRank Insight Engine.
It displays the top 100 domains per category and model, with memory decay metrics and
weekly change indicators.
"""

import os
import json
import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from datetime import datetime, timedelta

import domain_memory_tracker
import notification_agent

# Set page config
st.set_page_config(
    page_title="LLMPageRank Insight Dashboard",
    page_icon="📊",
    layout="wide"
)

# Constants
CATEGORIES = [
    "Technology", "Finance", "Healthcare", "Education", "Entertainment",
    "Travel", "Food", "Sports", "News", "Shopping", "Social Media"
]

MODELS = [
    "gpt-4o", "claude-3-opus", "gemini-pro", "llama-3", "mixtral"
]

# Helper functions
def generate_test_data():
    """Generate test data for demonstration purposes."""
    # Add test domains for each category and model
    domains = [
        "example.com", "google.com", "microsoft.com", "apple.com", "amazon.com",
        "facebook.com", "twitter.com", "linkedin.com", "github.com", "netflix.com",
        "spotify.com", "airbnb.com", "uber.com", "lyft.com", "doordash.com",
        "grubhub.com", "walmart.com", "target.com", "bestbuy.com", "ebay.com"
    ]
    
    for category in CATEGORIES[:5]:  # Limit to first 5 categories for test data
        for model in MODELS:
            for i, domain in enumerate(domains[:20]):  # Top 20 domains
                # Generate a random rank based on position in the list
                rank = i + 1
                
                # Add some variance between models
                if model == "gpt-4o":
                    rank = max(1, rank - 2)  # GPT-4o tends to rank slightly higher
                elif model == "claude-3-opus":
                    rank = max(1, rank - 1)  # Claude ranks slightly higher
                elif model == "llama-3":
                    rank = rank + 2  # Llama ranks slightly lower
                
                # Add test data from one week ago
                week_ago = datetime.now() - timedelta(days=7)
                with st.spinner(f"Adding test data for {domain} in {model}/{category}..."):
                    # Add historical data point
                    domain_memory_tracker.update_domain_rank(
                        domain=domain,
                        model=model,
                        query_category=category,
                        rank=rank + 3,  # Higher rank (worse) in the past
                        query_text=f"best {category.lower()} sites"
                    )
                    
                    # Add current data point
                    domain_memory_tracker.update_domain_rank(
                        domain=domain,
                        model=model,
                        query_category=category,
                        rank=rank,
                        query_text=f"best {category.lower()} sites"
                    )
    
    st.success("Test data generated successfully!")

def display_header():
    """Display the dashboard header."""
    st.title("🧠 LLMPageRank Insight Dashboard")
    st.markdown("""
    This dashboard shows how domains are remembered across different LLM models. 
    Monitor memory decay and track ranking changes over time.
    """)
    
    # Display filters in the sidebar
    st.sidebar.header("Filters")
    
    selected_category = st.sidebar.selectbox("Select Category", CATEGORIES)
    selected_model = st.sidebar.selectbox("Select Model", MODELS)
    
    return selected_category, selected_model

def display_top_domains(category, model):
    """Display the top domains for a category and model."""
    st.header(f"Top Domains: {category} / {model}")
    
    # Get top domains
    domains = domain_memory_tracker.get_top_domains(model, category)
    
    if not domains:
        st.info(f"No domains found for {category} in {model}. Please generate test data or add real domains.")
        return
    
    # Create DataFrame
    df = pd.DataFrame(domains)
    
    # Calculate weekly change
    for i, row in df.iterrows():
        domain = row["domain"]
        history = domain_memory_tracker.get_rank_history(
            domain=domain,
            model=model,
            query_category=category,
            days=7
        )
        
        # Calculate weekly change if we have enough history
        if len(history) >= 2:
            oldest = history[0]
            newest = history[-1]
            weekly_change = oldest["rank"] - newest["rank"]
            df.at[i, "weekly_change"] = weekly_change
        else:
            df.at[i, "weekly_change"] = 0
    
    # Format for display
    df["rank_display"] = df["rank"].astype(int)
    
    # Create change indicators
    def format_change(val):
        if val > 0:
            return f"⬆️ +{val}"
        elif val < 0:
            return f"⬇️ {val}"
        else:
            return "↔️ 0"
    
    df["change_display"] = df["weekly_change"].apply(format_change)
    
    # Display table
    st.dataframe(
        df[["rank_display", "domain", "change_display"]].rename(
            columns={
                "rank_display": "Rank",
                "domain": "Domain",
                "change_display": "Weekly Change"
            }
        ),
        use_container_width=True
    )
    
    # Plot top 10 as a horizontal bar chart
    top_10 = df.head(10).copy()
    top_10["domain"] = top_10["domain"].apply(lambda x: x.replace(".com", ""))  # Simplify domain names
    
    fig = px.bar(
        top_10,
        y="domain",
        x="rank",
        orientation="h",
        title=f"Top 10 Domains in {category} / {model}",
        labels={"domain": "Domain", "rank": "Rank"},
        color="weekly_change",
        color_continuous_scale="RdYlGn_r"  # Red for negative change, green for positive
    )
    
    fig.update_layout(
        yaxis=dict(autorange="reversed"),
        xaxis=dict(range=[0, 15])
    )
    
    st.plotly_chart(fig, use_container_width=True)

def display_memory_decay(category, model):
    """Display memory decay metrics for domains."""
    st.header(f"Memory Decay Analysis: {category} / {model}")
    
    # Get top domains
    domains = domain_memory_tracker.get_top_domains(model, category, limit=20)
    
    if not domains:
        st.info(f"No domains found for {category} in {model}.")
        return
    
    # Get memory decay for each domain
    decay_data = []
    
    for domain_data in domains[:10]:  # Limit to top 10 for decay analysis
        domain = domain_data["domain"]
        
        decay_metrics = domain_memory_tracker.get_memory_decay(
            domain=domain,
            model=model,
            query_category=category
        )
        
        if decay_metrics and "models" in decay_metrics and model in decay_metrics["models"]:
            model_metrics = decay_metrics["models"][model]
            
            if category in model_metrics:
                cat_metrics = model_metrics[category]
                
                decay_data.append({
                    "domain": domain,
                    "decay_score": cat_metrics["decay_score"],
                    "trend": cat_metrics["trend"],
                    "rank": domain_data["rank"]
                })
    
    if not decay_data:
        st.info("Not enough historical data to calculate memory decay metrics.")
        return
    
    # Create DataFrame
    df = pd.DataFrame(decay_data)
    
    # Display memory decay
    col1, col2 = st.columns([2, 1])
    
    with col1:
        # Plot decay scores
        fig = px.bar(
            df,
            x="domain",
            y="decay_score",
            color="trend",
            color_discrete_map={
                "improving": "green",
                "declining": "red",
                "stable": "blue"
            },
            title="Memory Decay Scores (Higher = Better Retention)",
            labels={"domain": "Domain", "decay_score": "Decay Score"}
        )
        
        fig.update_layout(
            xaxis_tickangle=-45,
            yaxis=dict(range=[0, 1])
        )
        
        st.plotly_chart(fig, use_container_width=True)
    
    with col2:
        # Display trend counts
        trend_counts = df["trend"].value_counts().reset_index()
        trend_counts.columns = ["Trend", "Count"]
        
        fig = px.pie(
            trend_counts,
            values="Count",
            names="Trend",
            title="Trend Distribution",
            color="Trend",
            color_discrete_map={
                "improving": "green",
                "declining": "red",
                "stable": "blue"
            }
        )
        
        st.plotly_chart(fig, use_container_width=True)
    
    # Display table
    st.dataframe(
        df[["domain", "decay_score", "trend", "rank"]].rename(
            columns={
                "domain": "Domain",
                "decay_score": "Memory Score",
                "trend": "Trend",
                "rank": "Current Rank"
            }
        ),
        use_container_width=True
    )

def display_significant_changes(category=None, model=None):
    """Display significant ranking changes."""
    st.header("⚠️ Significant Ranking Changes")
    
    # Get recent significant deltas
    deltas = domain_memory_tracker.get_significant_deltas(days=7)
    
    if not deltas:
        st.info("No significant ranking changes detected in the past week.")
        return
    
    # Filter by category and model if provided
    filtered_deltas = []
    
    for delta in deltas:
        if category and delta["query_category"] != category:
            continue
            
        if model and delta["model"] != model:
            continue
            
        filtered_deltas.append(delta)
    
    if not filtered_deltas:
        st.info(f"No significant ranking changes for the selected filters.")
        return
    
    # Convert to DataFrame
    df = pd.DataFrame(filtered_deltas)
    
    # Format timestamps
    df["timestamp"] = pd.to_datetime(df["timestamp"])
    df["date"] = df["timestamp"].dt.strftime("%Y-%m-%d")
    
    # Format deltas with emojis
    def format_delta(row):
        delta = row["delta"]
        if delta > 0:
            return f"⬆️ +{delta}"
        else:
            return f"⬇️ {delta}"
    
    df["delta_display"] = df.apply(format_delta, axis=1)
    
    # Format table
    display_df = df[["date", "domain", "model", "query_category", "delta_display", "previous_rank", "current_rank"]].rename(
        columns={
            "date": "Date",
            "domain": "Domain",
            "model": "Model",
            "query_category": "Category",
            "delta_display": "Change",
            "previous_rank": "Previous",
            "current_rank": "Current"
        }
    )
    
    st.dataframe(display_df, use_container_width=True)
    
    # Plot changes over time
    st.subheader("Ranking Changes Over Time")
    
    # Group by date and count changes
    date_counts = df.groupby("date").size().reset_index(name="count")
    date_counts["date"] = pd.to_datetime(date_counts["date"])
    
    # Plot
    fig = px.line(
        date_counts,
        x="date",
        y="count",
        title="Significant Ranking Changes by Date",
        labels={"date": "Date", "count": "Number of Changes"}
    )
    
    st.plotly_chart(fig, use_container_width=True)

def display_model_comparison():
    """Display comparison of domains across different models."""
    st.header("🔄 Model Comparison")
    
    # Let user select a category and domain
    category = st.selectbox("Select Category for Comparison", CATEGORIES, key="compare_category")
    
    # Get top domains for this category across models
    all_domains = set()
    
    for model in MODELS:
        domains = domain_memory_tracker.get_top_domains(model, category, limit=20)
        for domain_data in domains:
            all_domains.add(domain_data["domain"])
    
    if not all_domains:
        st.info(f"No domains found for {category} across models.")
        return
    
    # Let user select a domain
    domain = st.selectbox("Select Domain", sorted(list(all_domains)), key="compare_domain")
    
    # Get rank data for this domain across models
    model_ranks = {}
    
    for model in MODELS:
        history = domain_memory_tracker.get_rank_history(
            domain=domain,
            model=model,
            query_category=category,
            days=30
        )
        
        if history:
            # Get rank over time
            timestamps = [datetime.fromisoformat(entry["timestamp"]) for entry in history]
            ranks = [entry["rank"] for entry in history]
            
            model_ranks[model] = {
                "timestamps": timestamps,
                "ranks": ranks,
                "current_rank": ranks[-1] if ranks else None
            }
    
    if not model_ranks:
        st.info(f"No ranking data found for {domain} in {category}.")
        return
    
    # Display current ranks
    st.subheader(f"Current Rankings for {domain} in {category}")
    
    current_ranks = []
    
    for model, data in model_ranks.items():
        if data["current_rank"] is not None:
            current_ranks.append({
                "Model": model,
                "Rank": data["current_rank"]
            })
    
    if current_ranks:
        current_df = pd.DataFrame(current_ranks)
        
        # Plot current ranks
        fig = px.bar(
            current_df,
            x="Model",
            y="Rank",
            title=f"Current Rankings for {domain} in {category}",
            labels={"Model": "Model", "Rank": "Rank"},
            color="Model"
        )
        
        fig.update_layout(
            yaxis=dict(autorange="reversed")  # Reverse y-axis so lower (better) ranks are higher
        )
        
        st.plotly_chart(fig, use_container_width=True)
    
    # Plot rank over time
    st.subheader(f"Ranking Trends for {domain} in {category}")
    
    fig = go.Figure()
    
    for model, data in model_ranks.items():
        fig.add_trace(go.Scatter(
            x=data["timestamps"],
            y=data["ranks"],
            mode="lines+markers",
            name=model
        ))
    
    fig.update_layout(
        title=f"Ranking Trends for {domain} in {category}",
        xaxis_title="Date",
        yaxis_title="Rank",
        yaxis=dict(autorange="reversed")  # Reverse y-axis so lower (better) ranks are higher
    )
    
    st.plotly_chart(fig, use_container_width=True)
    
    # Memory decay across models
    st.subheader(f"Memory Decay Analysis for {domain}")
    
    decay_metrics = domain_memory_tracker.get_memory_decay(domain=domain)
    
    if not decay_metrics or "models" not in decay_metrics:
        st.info(f"No memory decay metrics available for {domain}.")
        return
    
    # Collect decay scores
    decay_scores = []
    
    for model, model_data in decay_metrics["models"].items():
        if category in model_data:
            cat_data = model_data[category]
            decay_scores.append({
                "Model": model,
                "Decay Score": cat_data["decay_score"],
                "Trend": cat_data["trend"]
            })
    
    if decay_scores:
        decay_df = pd.DataFrame(decay_scores)
        
        # Plot decay scores
        fig = px.bar(
            decay_df,
            x="Model",
            y="Decay Score",
            color="Trend",
            color_discrete_map={
                "improving": "green",
                "declining": "red",
                "stable": "blue"
            },
            title=f"Memory Decay Scores for {domain} (Higher = Better Retention)",
            labels={"Model": "Model", "Decay Score": "Memory Score"}
        )
        
        st.plotly_chart(fig, use_container_width=True)

def display_free_tier_info():
    """Display information about the free tier and upgrade options."""
    st.sidebar.markdown("---")
    st.sidebar.header("✨ Free Tier")
    st.sidebar.info(
        "You're using the free tier of LLMPageRank. "
        "Upgrade to access:\n"
        "- Real-time alerts via Slack\n"
        "- Email notifications\n"
        "- API access\n"
        "- Custom domain tracking\n"
        "- Historical data beyond 30 days"
    )
    st.sidebar.button("Upgrade Now")
    
    # Admin controls (hidden in production)
    st.sidebar.markdown("---")
    st.sidebar.header("⚙️ Admin Controls")
    
    if st.sidebar.button("Generate Test Data"):
        generate_test_data()

def main():
    """Main dashboard function."""
    selected_category, selected_model = display_header()
    
    # Create tabs
    tab1, tab2, tab3, tab4 = st.tabs([
        "Top Domains", 
        "Memory Decay", 
        "Significant Changes",
        "Model Comparison"
    ])
    
    with tab1:
        display_top_domains(selected_category, selected_model)
    
    with tab2:
        display_memory_decay(selected_category, selected_model)
    
    with tab3:
        display_significant_changes(selected_category, selected_model)
    
    with tab4:
        display_model_comparison()
    
    # Display free tier information
    display_free_tier_info()

if __name__ == "__main__":
    main()