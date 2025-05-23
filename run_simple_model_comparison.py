"""
Simple Model Comparison Dashboard

This Streamlit app displays the model comparison results from Purity25, showing
model disagreement scores, domain citation overlap, blindspots, and rare signals.
"""
import os
import json
import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from datetime import datetime

# Set page config
st.set_page_config(
    page_title="LLMPageRank Model Comparison",
    page_icon="📊",
    layout="wide"
)

# Data directory
DATA_DIR = "data/purity25_output"

def load_all_data():
    """Load all comparison results from the data directory."""
    comparison_data = []
    
    # Check if directory exists
    if not os.path.exists(DATA_DIR):
        st.warning(f"Data directory {DATA_DIR} not found. Please run simple_purity25.py first.")
        return []
    
    # Load comparison files
    for filename in os.listdir(DATA_DIR):
        if filename.startswith("comparison_") and filename.endswith(".json"):
            file_path = os.path.join(DATA_DIR, filename)
            
            try:
                with open(file_path, 'r') as f:
                    data = json.load(f)
                    comparison_data.append(data)
            except Exception as e:
                st.error(f"Error loading {filename}: {e}")
    
    return comparison_data

def load_weekly_digest():
    """Load the weekly digest file."""
    digest_path = os.path.join(DATA_DIR, "weekly_digest.json")
    
    if not os.path.exists(digest_path):
        return None
    
    try:
        with open(digest_path, 'r') as f:
            digest = json.load(f)
        return digest
    except Exception as e:
        st.error(f"Error loading weekly digest: {e}")
        return None

def run_app():
    """Run the Streamlit app."""
    st.title("LLMPageRank Model Comparison Dashboard")
    st.markdown("### Purity25: Model Enrichment & Signal Divergence Indexing")
    
    # Create tabs
    tab1, tab2, tab3 = st.tabs(["Model Comparisons", "Blindspots & Rare Signals", "Weekly Digest"])
    
    # Load data
    comparison_data = load_all_data()
    weekly_digest = load_weekly_digest()
    
    if not comparison_data:
        st.info("No comparison data found. Please run simple_purity25.py first.")
        return
    
    with tab1:
        st.subheader("Model Comparison Results")
        
        # Convert comparison data to DataFrame for easier manipulation
        df_rows = []
        
        for data in comparison_data:
            row = {
                "prompt_id": data.get("prompt_id", ""),
                "prompt": data.get("prompt", ""),
                "category": data.get("category", ""),
                "timestamp": data.get("timestamp", ""),
                "model_disagreement_score": data.get("model_disagreement_score", 0),
                "domain_citation_overlap": data.get("domain_citation_overlap", 0),
                "domains_cited": data.get("domains_cited", 0),
                "blindspots_count": data.get("blindspots_count", 0),
                "rare_signals_count": data.get("rare_signals_count", 0)
            }
            
            df_rows.append(row)
        
        df = pd.DataFrame(df_rows)
        
        # Select a prompt to analyze
        selected_prompt = st.selectbox("Select a prompt to analyze:", df["prompt"].unique())
        
        # Filter data for selected prompt
        selected_rows = df[df["prompt"] == selected_prompt]
        if selected_rows.empty:
            st.error("No data found for selected prompt")
            return
            
        selected_data = selected_rows.iloc[0]
        
        # Display prompt details
        st.markdown(f"**Category:** {selected_data['category']}")
        st.markdown(f"**Timestamp:** {selected_data['timestamp']}")
        
        # Display metrics
        col1, col2, col3 = st.columns(3)
        
        with col1:
            st.metric("Model Disagreement Score", f"{selected_data['model_disagreement_score']:.2f}")
        
        with col2:
            st.metric("Domain Citation Overlap", f"{selected_data['domain_citation_overlap']:.2f}")
        
        with col3:
            st.metric("Domains Cited", selected_data['domains_cited'])
        
        # Get model responses for the selected prompt
        for data in comparison_data:
            if data["prompt"] == selected_prompt:
                model_responses = data.get("model_responses", {})
                break
        else:
            model_responses = {}
        
        # Create domain citation matrix
        if model_responses:
            st.subheader("Domain Citations by Model")
            
            # Get all unique domains
            all_domains = set()
            for domains in model_responses.values():
                all_domains.update(domains)
            
            # Create DataFrame for citation matrix
            matrix_data = []
            
            for domain in sorted(all_domains):
                row = {"Domain": domain}
                
                for model, domains in model_responses.items():
                    row[model] = 1 if domain in domains else 0
                
                matrix_data.append(row)
            
            matrix_df = pd.DataFrame(matrix_data)
            
            # Display matrix
            st.dataframe(matrix_df, use_container_width=True)
            
            # Create citation count chart
            citation_counts = {model: len(domains) for model, domains in model_responses.items()}
            
            fig = px.bar(
                x=list(citation_counts.keys()),
                y=list(citation_counts.values()),
                labels={"x": "Model", "y": "Domains Cited"},
                title="Number of Domains Cited by Each Model"
            )
            
            st.plotly_chart(fig, use_container_width=True)
    
    with tab2:
        st.subheader("Blindspots & Rare Signals Analysis")
        
        # Select a prompt to analyze
        selected_prompt = st.selectbox("Select a prompt:", df["prompt"].unique(), key="tab2_prompt_select")
        
        # Find blindspot and rarity data for the selected prompt
        blindspot_data = None
        rarity_data = None
        
        # Safely get the prompt_id
        prompt_id_series = df[df["prompt"] == selected_prompt]["prompt_id"]
        if not prompt_id_series.empty:
            selected_prompt_id = prompt_id_series.iloc[0]
        else:
            st.error("Could not find prompt ID for selected prompt")
            return
        
        for filename in os.listdir(DATA_DIR):
            if filename == f"blindspots_{selected_prompt_id}.json":
                with open(os.path.join(DATA_DIR, filename), 'r') as f:
                    blindspot_data = json.load(f)
            elif filename == f"rarity_{selected_prompt_id}.json":
                with open(os.path.join(DATA_DIR, filename), 'r') as f:
                    rarity_data = json.load(f)
        
        col1, col2 = st.columns(2)
        
        with col1:
            st.markdown("### Model Blindspots")
            
            if blindspot_data:
                # Display metrics
                st.markdown(f"**Total Blindspots:** {blindspot_data['metrics']['total_blindspots']}")
                st.markdown(f"**Blindspot Ratio:** {blindspot_data['metrics']['blindspot_ratio']:.2f}")
                st.markdown(f"**Domains with Blindspots:** {blindspot_data['metrics']['domains_with_blindspots']} / {blindspot_data['metrics']['total_domains']}")
                
                # Display blindspots
                st.markdown("#### Domains Missed by Models")
                
                for domain, models in blindspot_data["blindspots"].items():
                    st.markdown(f"**{domain}**: Missed by {', '.join(models)}")
            else:
                st.info("No blindspot data available for this prompt.")
        
        with col2:
            st.markdown("### Rare Signals")
            
            if rarity_data:
                # Display metrics
                st.markdown(f"**Total Rare Signals:** {rarity_data['metrics']['total_rare_signals']}")
                st.markdown(f"**Rarity Ratio:** {rarity_data['metrics']['rarity_ratio']:.2f}")
                st.markdown(f"**Models with Rare Signals:** {rarity_data['metrics']['models_with_rare_signals']} / {len(rarity_data['rare_signals'])}")
                
                # Display rare signals
                st.markdown("#### Unique Domains by Model")
                
                for model, domains in rarity_data["rare_signals"].items():
                    st.markdown(f"**{model}**: {', '.join(domains)}")
            else:
                st.info("No rarity data available for this prompt.")
    
    with tab3:
        st.subheader("Weekly Digest")
        
        if weekly_digest:
            st.markdown(f"**Timestamp:** {weekly_digest.get('timestamp', 'N/A')}")
            st.markdown(f"**Total Prompts Analyzed:** {weekly_digest.get('total_prompts_analyzed', 0)}")
            st.markdown(f"**Total Categories:** {weekly_digest.get('total_categories', 0)}")
            
            col1, col2 = st.columns(2)
            
            with col1:
                st.info(f"**Best Rare Signal Model:** {weekly_digest.get('best_rare_signal_model', 'N/A')}")
            
            with col2:
                st.warning(f"**Worst Blindspot Model:** {weekly_digest.get('worst_blindspot_model', 'N/A')}")
            
            # Model stats
            st.subheader("Model Performance")
            
            model_stats = weekly_digest.get("model_stats", {})
            
            if model_stats:
                # Create DataFrame for model stats
                model_df_data = []
                
                for model, stats in model_stats.items():
                    model_df_data.append({
                        "Model": model,
                        "Rare Signals": stats.get("rare_signals", 0),
                        "Blindspots": stats.get("blindspots", 0)
                    })
                
                model_df = pd.DataFrame(model_df_data)
                
                # Create model performance chart
                fig = go.Figure()
                
                fig.add_trace(go.Bar(
                    x=model_df["Model"],
                    y=model_df["Rare Signals"],
                    name="Rare Signals",
                    marker_color="green"
                ))
                
                fig.add_trace(go.Bar(
                    x=model_df["Model"],
                    y=model_df["Blindspots"],
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
                
                # Display model stats table
                st.dataframe(model_df, use_container_width=True)
            
            # Category stats
            st.subheader("Category Performance")
            
            category_stats = weekly_digest.get("category_stats", {})
            
            if category_stats:
                # Create DataFrame for category stats
                cat_df_data = []
                
                for category, stats in category_stats.items():
                    cat_df_data.append({
                        "Category": category,
                        "Prompts": stats.get("prompts", 0),
                        "Avg Disagreement": stats.get("avg_disagreement", 0),
                        "Total Domains Cited": stats.get("total_domains_cited", 0),
                        "Rare Signals": stats.get("rare_signals", 0),
                        "Blindspots": stats.get("blindspots", 0)
                    })
                
                cat_df = pd.DataFrame(cat_df_data)
                
                # Create category disagreement chart
                fig1 = px.bar(
                    cat_df,
                    x="Category",
                    y="Avg Disagreement",
                    title="Average Model Disagreement Score by Category",
                    color="Avg Disagreement",
                    color_continuous_scale="RdYlGn_r"
                )
                
                st.plotly_chart(fig1, use_container_width=True)
                
                # Create category metrics chart
                fig2 = go.Figure()
                
                fig2.add_trace(go.Bar(
                    x=cat_df["Category"],
                    y=cat_df["Rare Signals"],
                    name="Rare Signals",
                    marker_color="green"
                ))
                
                fig2.add_trace(go.Bar(
                    x=cat_df["Category"],
                    y=cat_df["Blindspots"],
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
                
                # Display category stats table
                st.dataframe(cat_df, use_container_width=True)
        else:
            st.info("No weekly digest available. Please run simple_purity25.py first.")

if __name__ == "__main__":
    run_app()