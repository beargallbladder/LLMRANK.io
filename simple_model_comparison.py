"""
Simple Model Comparison

A streamlined dashboard to display the model comparison results from Purity25,
focusing on clear visualization of model disagreement metrics across categories.
"""
import os
import json
import streamlit as st
import plotly.express as px
import plotly.graph_objects as go

# Set page config
st.set_page_config(
    page_title="LLMPageRank Model Comparison",
    page_icon="📊",
    layout="wide"
)

# Data directory
DATA_DIR = "data/purity25_output"

# Load weekly digest
def load_weekly_digest():
    """Load the weekly digest data."""
    digest_path = os.path.join(DATA_DIR, "weekly_digest.json")
    
    if not os.path.exists(digest_path):
        return None
    
    try:
        with open(digest_path, 'r') as f:
            return json.load(f)
    except Exception as e:
        st.error(f"Error loading weekly digest: {e}")
        return None

def display_model_comparison(weekly_digest):
    """Display model comparison visualizations."""
    st.title("LLMPageRank Model Comparison")
    st.subheader("Purity25: Model Enrichment & Signal Divergence Indexing")
    
    if not weekly_digest:
        st.warning("No weekly digest found. Please run simple_purity25.py first.")
        return
    
    # Display weekly digest summary
    st.markdown(f"**Timestamp:** {weekly_digest.get('timestamp', 'N/A')}")
    st.markdown(f"**Total Prompts Analyzed:** {weekly_digest.get('total_prompts_analyzed', 0)}")
    st.markdown(f"**Total Categories:** {weekly_digest.get('total_categories', 0)}")
    
    # Model performance metrics
    st.header("Model Performance")
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.info(f"**Best Rare Signal Model:** {weekly_digest.get('best_rare_signal_model', 'N/A')}")
    
    with col2:
        st.warning(f"**Worst Blindspot Model:** {weekly_digest.get('worst_blindspot_model', 'N/A')}")
    
    # Prepare model stats for visualization
    model_stats = weekly_digest.get("model_stats", {})
    models = list(model_stats.keys())
    rare_signals = [model_stats[model]["rare_signals"] for model in models]
    blindspots = [model_stats[model]["blindspots"] for model in models]
    
    # Create model comparison chart
    fig = go.Figure()
    
    fig.add_trace(go.Bar(
        x=models,
        y=rare_signals,
        name="Rare Signals",
        marker_color="green"
    ))
    
    fig.add_trace(go.Bar(
        x=models,
        y=blindspots,
        name="Blindspots",
        marker_color="red"
    ))
    
    fig.update_layout(
        title="Model Performance: Rare Signals vs. Blindspots",
        xaxis_title="Model",
        yaxis_title="Count",
        barmode="group"
    )
    
    st.plotly_chart(fig, use_container_width=True)
    
    # Category performance metrics
    st.header("Category Performance")
    
    category_stats = weekly_digest.get("category_stats", {})
    categories = list(category_stats.keys())
    
    if categories:
        # Create arrays for category metrics
        prompts = []
        disagreement = []
        domains = []
        signals = []
        blind = []
        
        for category in categories:
            stats = category_stats[category]
            prompts.append(stats.get("prompts", 0))
            disagreement.append(stats.get("avg_disagreement", 0))
            domains.append(stats.get("total_domains_cited", 0))
            signals.append(stats.get("rare_signals", 0))
            blind.append(stats.get("blindspots", 0))
        
        # Create disagreement chart
        fig1 = go.Figure()
        
        fig1.add_trace(go.Bar(
            x=categories,
            y=disagreement,
            name="Model Disagreement",
            marker_color="orange"
        ))
        
        fig1.update_layout(
            title="Average Model Disagreement by Category",
            xaxis_title="Category",
            yaxis_title="Disagreement Score (0-1)",
            yaxis=dict(range=[0, 1])
        )
        
        st.plotly_chart(fig1, use_container_width=True)
        
        # Create category metrics chart
        fig2 = go.Figure()
        
        fig2.add_trace(go.Bar(
            x=categories,
            y=signals,
            name="Rare Signals",
            marker_color="green"
        ))
        
        fig2.add_trace(go.Bar(
            x=categories,
            y=blind,
            name="Blindspots",
            marker_color="red"
        ))
        
        fig2.update_layout(
            title="Category Performance: Rare Signals vs. Blindspots",
            xaxis_title="Category",
            yaxis_title="Count",
            barmode="group"
        )
        
        st.plotly_chart(fig2, use_container_width=True)
    else:
        st.info("No category data available.")

def main():
    """Main function to run the app."""
    # Check if data directory exists
    if not os.path.exists(DATA_DIR):
        st.warning(f"Data directory {DATA_DIR} not found. Please run simple_purity25.py first.")
        return
    
    # Load weekly digest
    weekly_digest = load_weekly_digest()
    
    # Display model comparison
    display_model_comparison(weekly_digest)
    
    # Add explanation of metrics
    with st.expander("About Model Comparison Metrics"):
        st.markdown("""
        ### Model Comparison Metrics Explained
        
        **Model Disagreement Score**: Measures how much models disagree with each other on which domains to cite. Higher values (closer to 1.0) indicate more disagreement.
        
        **Domain Citation Overlap**: Measures how much overlap exists in domain citations between models. Lower values indicate less overlap.
        
        **Rare Signals**: Domains that are cited by only one model. These represent unique insights that only one model provides.
        
        **Blindspots**: Domains that a model fails to cite but other models do cite. These represent potential gaps in a model's knowledge.
        """)
    
    st.markdown("---")
    st.markdown("Data generated by Purity25 Model Comparison System")

if __name__ == "__main__":
    main()