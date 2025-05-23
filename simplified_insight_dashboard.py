"""
Simplified Insight Dashboard

A streamlined version of the LLMPageRank Insight Dashboard focused on core functionality.
"""

import streamlit as st
import pandas as pd
import plotly.express as px
from datetime import datetime, timedelta
import os
import json

# Set page config
st.set_page_config(
    page_title="LLMPageRank Insight Dashboard",
    page_icon="📊",
    layout="wide"
)

# Constants
CATEGORIES = [
    "Technology", "Finance", "Healthcare", "Education", "Entertainment"
]

MODELS = [
    "gpt-4o", "claude-3-opus", "gemini-pro", "llama-3", "mixtral"
]

# Create data directories
os.makedirs("data", exist_ok=True)
os.makedirs("data/domain_memory", exist_ok=True)

# Generate demo data
def generate_demo_data():
    """Generate demonstration data for the dashboard."""
    # Sample domains
    domains = [
        "example.com", "google.com", "microsoft.com", "apple.com", "amazon.com",
        "facebook.com", "twitter.com", "linkedin.com", "github.com", "netflix.com"
    ]
    
    # Sample data structure
    data = {}
    
    for category in CATEGORIES:
        data[category] = {}
        
        for model in MODELS:
            model_data = []
            
            for i, domain in enumerate(domains):
                # Current rank (1-10)
                rank = i + 1
                
                # Add some model-specific variation
                if model == "gpt-4o":
                    rank = max(1, rank - 1)  # Ranks slightly better
                elif model == "llama-3":
                    rank = min(10, rank + 1)  # Ranks slightly worse
                
                # Weekly change (random: -2 to +2)
                weekly_change = (i % 5) - 2
                
                # Memory score (0.4 to 0.9)
                memory_score = 0.9 - (rank * 0.05)
                
                # Trend
                if weekly_change > 0:
                    trend = "improving"
                elif weekly_change < 0:
                    trend = "declining"
                else:
                    trend = "stable"
                
                model_data.append({
                    "domain": domain,
                    "rank": rank,
                    "weekly_change": weekly_change,
                    "memory_score": memory_score,
                    "trend": trend
                })
            
            data[category][model] = model_data
    
    # Save data
    with open("data/domain_memory/demo_data.json", "w") as f:
        json.dump(data, f, indent=2)
    
    return data

# Load or generate data
def load_data():
    """Load existing data or generate new demo data."""
    data_path = "data/domain_memory/demo_data.json"
    
    if os.path.exists(data_path):
        try:
            with open(data_path, "r") as f:
                return json.load(f)
        except:
            pass
    
    return generate_demo_data()

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

def display_domain_rankings(data, category, model):
    """Display domain rankings for a category and model."""
    st.header(f"Domain Rankings: {category} / {model}")
    
    if category not in data or model not in data[category]:
        st.info(f"No data available for {category} / {model}")
        return
    
    domain_data = data[category][model]
    
    # Create DataFrame
    df = pd.DataFrame(domain_data)
    
    # Format weekly change
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
        df[["rank", "domain", "change_display"]].rename(columns={
            "rank": "Rank",
            "domain": "Domain",
            "change_display": "Weekly Change"
        }),
        use_container_width=True
    )
    
    # Display chart
    st.subheader(f"Top Domains in {category} / {model}")
    
    fig = px.bar(
        df,
        y="domain",
        x="rank",
        orientation="h",
        title="Domain Rankings",
        labels={"domain": "Domain", "rank": "Rank"},
        color="weekly_change",
        color_continuous_scale="RdYlGn_r"
    )
    
    fig.update_layout(
        yaxis=dict(autorange="reversed"),
        xaxis=dict(range=[0, 15])
    )
    
    st.plotly_chart(fig, use_container_width=True)

def display_memory_metrics(data, category, model):
    """Display memory metrics for domains."""
    st.header(f"Memory Analysis: {category} / {model}")
    
    if category not in data or model not in data[category]:
        st.info(f"No data available for {category} / {model}")
        return
    
    domain_data = data[category][model]
    
    # Create DataFrame
    df = pd.DataFrame(domain_data)
    
    # Display memory metrics
    col1, col2 = st.columns([2, 1])
    
    with col1:
        # Memory score chart
        fig = px.bar(
            df,
            x="domain",
            y="memory_score",
            color="trend",
            color_discrete_map={
                "improving": "green",
                "declining": "red",
                "stable": "blue"
            },
            title="Memory Scores by Domain",
            labels={"domain": "Domain", "memory_score": "Memory Score"}
        )
        
        fig.update_layout(
            xaxis_tickangle=-45,
            yaxis=dict(range=[0, 1])
        )
        
        st.plotly_chart(fig, use_container_width=True)
    
    with col2:
        # Trend distribution
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
    
    # Display metrics table
    st.dataframe(
        df[["domain", "memory_score", "trend", "rank"]].rename(columns={
            "domain": "Domain",
            "memory_score": "Memory Score",
            "trend": "Trend",
            "rank": "Rank"
        }),
        use_container_width=True
    )

def display_model_comparison(data, category):
    """Display model comparison for a category."""
    st.header(f"Model Comparison: {category}")
    
    if category not in data:
        st.info(f"No data available for {category}")
        return
    
    # Select a domain
    all_domains = set()
    
    for model in MODELS:
        if model in data[category]:
            for item in data[category][model]:
                all_domains.add(item["domain"])
    
    if not all_domains:
        st.info(f"No domains found for {category}")
        return
    
    domain = st.selectbox("Select Domain", sorted(list(all_domains)))
    
    # Get domain data across models
    domain_data = []
    
    for model in MODELS:
        if model in data[category]:
            for item in data[category][model]:
                if item["domain"] == domain:
                    domain_data.append({
                        "model": model,
                        "rank": item["rank"],
                        "memory_score": item["memory_score"],
                        "trend": item["trend"]
                    })
    
    if not domain_data:
        st.info(f"No data found for {domain} in {category}")
        return
    
    # Create DataFrame
    df = pd.DataFrame(domain_data)
    
    # Display comparison
    col1, col2 = st.columns(2)
    
    with col1:
        # Rank comparison
        fig = px.bar(
            df,
            x="model",
            y="rank",
            title=f"Rank Comparison for {domain}",
            labels={"model": "Model", "rank": "Rank"},
            color="model"
        )
        
        fig.update_layout(
            yaxis=dict(autorange="reversed")
        )
        
        st.plotly_chart(fig, use_container_width=True)
    
    with col2:
        # Memory score comparison
        fig = px.bar(
            df,
            x="model",
            y="memory_score",
            title=f"Memory Score Comparison for {domain}",
            labels={"model": "Model", "memory_score": "Memory Score"},
            color="model"
        )
        
        st.plotly_chart(fig, use_container_width=True)
    
    # Display comparison table
    st.dataframe(
        df.rename(columns={
            "model": "Model",
            "rank": "Rank",
            "memory_score": "Memory Score",
            "trend": "Trend"
        }),
        use_container_width=True
    )

def display_sidebar_info():
    """Display information in the sidebar."""
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
    
    if st.sidebar.button("Upgrade Now"):
        st.sidebar.success("Redirecting to upgrade page...")
    
    st.sidebar.markdown("---")
    
    st.sidebar.header("⚙️ Admin Controls")
    
    if st.sidebar.button("Generate Demo Data"):
        generate_demo_data()
        st.sidebar.success("Demo data generated successfully!")
        st.rerun()

def main():
    """Main application."""
    # Load data
    data = load_data()
    
    # Display header and get selected filters
    selected_category, selected_model = display_header()
    
    # Create tabs
    tab1, tab2, tab3 = st.tabs([
        "Domain Rankings", 
        "Memory Analysis",
        "Model Comparison"
    ])
    
    with tab1:
        display_domain_rankings(data, selected_category, selected_model)
    
    with tab2:
        display_memory_metrics(data, selected_category, selected_model)
    
    with tab3:
        display_model_comparison(data, selected_category)
    
    # Display sidebar information
    display_sidebar_info()

if __name__ == "__main__":
    main()