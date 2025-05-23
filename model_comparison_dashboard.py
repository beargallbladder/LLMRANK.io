"""
PRD-25: LLM Model Enrichment & Signal Divergence Indexing (Purity25)

Model Comparison Dashboard
------------------------
This module provides a Streamlit dashboard for visualizing model comparisons and disagreements.
"""

import os
import json
import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from datetime import datetime, timedelta

# Import from project modules
import insight_schema
from agents import model_comparator, gap_detector, signal_rarity_profiler
import llm_clients

# Setup page config
st.set_page_config(
    page_title="LLMPageRank Model Comparison",
    page_icon="📊",
    layout="wide"
)

def load_divergence_logs():
    """Load model divergence logs."""
    logs_dir = f"{insight_schema.LOGS_DIR}/model_divergence"
    
    if not os.path.exists(logs_dir):
        return []
    
    logs = []
    
    for filename in os.listdir(logs_dir):
        if filename.endswith(".json"):
            file_path = os.path.join(logs_dir, filename)
            
            try:
                with open(file_path, 'r') as f:
                    file_logs = json.load(f)
                    
                    if isinstance(file_logs, list):
                        logs.extend(file_logs)
                    else:
                        logs.append(file_logs)
            except Exception as e:
                st.error(f"Error loading {filename}: {e}")
    
    return logs

def load_blindspot_data():
    """Load model blindspot data."""
    if not os.path.exists(gap_detector.MODEL_BLINDSPOTS_FILE):
        return []
    
    try:
        with open(gap_detector.MODEL_BLINDSPOTS_FILE, 'r') as f:
            data = json.load(f)
        
        return data
    except Exception as e:
        st.error(f"Error loading blindspot data: {e}")
        return []

def load_rare_signals():
    """Load rare signal data."""
    if not os.path.exists(signal_rarity_profiler.RARE_SIGNALS_FILE):
        return []
    
    try:
        with open(signal_rarity_profiler.RARE_SIGNALS_FILE, 'r') as f:
            data = json.load(f)
        
        return data
    except Exception as e:
        st.error(f"Error loading rare signal data: {e}")
        return []

def load_weekly_digest():
    """Load weekly digest data."""
    summary_file = f"{insight_schema.LOGS_DIR}/weekly_blindspot_summary.json"
    
    if not os.path.exists(summary_file):
        return None
    
    try:
        with open(summary_file, 'r') as f:
            data = json.load(f)
        
        return data
    except Exception as e:
        st.error(f"Error loading weekly digest: {e}")
        return None

def run_model_comparison(prompt, category):
    """Run a model comparison test and display results."""
    st.write("Running model comparison...")
    
    # Initialize multi-model client with mock models
    # (for production, set use_real_models=True)
    client = llm_clients.MultiModelClient(use_real_models=True)
    
    # Get responses from all models
    model_responses = client.get_all_model_responses(prompt)
    
    # Show raw responses
    st.subheader("Model Responses")
    
    for model, domains in model_responses.items():
        st.write(f"**{model}**: {', '.join(domains)}")
    
    # Run model comparator
    divergence_metrics = model_comparator.calculate_model_disagreement(
        model_responses=model_responses,
        category=category
    )
    
    # Run gap detector
    blindspot_metrics = gap_detector.detect_model_blindspots(
        prompt_id=f"test_{datetime.now().strftime('%Y%m%d%H%M%S')}",
        prompt_text=prompt,
        category=category,
        model_responses=model_responses
    )
    
    # Run signal rarity profiler
    rarity_metrics = signal_rarity_profiler.detect_rare_signals(
        prompt_id=f"test_{datetime.now().strftime('%Y%m%d%H%M%S')}",
        prompt_text=prompt,
        category=category,
        model_responses=model_responses
    )
    
    # Display metrics
    st.subheader("Divergence Metrics")
    
    cols = st.columns(3)
    
    with cols[0]:
        st.metric(
            "Model Disagreement Score", 
            f"{divergence_metrics['model_disagreement_score']:.2f}"
        )
    
    with cols[1]:
        st.metric(
            "Domain Citation Overlap", 
            f"{divergence_metrics['domain_citation_overlap']:.2f}"
        )
    
    with cols[2]:
        st.metric(
            "Total Domains Cited", 
            divergence_metrics['domains_cited']
        )
    
    # Display model distribution
    st.subheader("Model Distribution")
    
    model_dist = pd.DataFrame({
        "Model": list(divergence_metrics['model_distribution'].keys()),
        "Cited": [1 if v else 0 for v in divergence_metrics['model_distribution'].values()]
    })
    
    fig = px.bar(
        model_dist,
        x="Model",
        y="Cited",
        color="Cited",
        title="Models Citing Domains",
        color_continuous_scale=["red", "green"]
    )
    
    st.plotly_chart(fig, use_container_width=True)
    
    # Display blindspots
    st.subheader("Model Blindspots")
    
    if not blindspot_metrics['blindspots']:
        st.info("No blindspots detected.")
    else:
        for domain, missing_models in blindspot_metrics['blindspots'].items():
            st.write(f"**{domain}**: Missed by {', '.join(missing_models)}")
    
    # Display rare signals
    st.subheader("Rare Signals")
    
    if not rarity_metrics['rare_signals']:
        st.info("No rare signals detected.")
    else:
        for model, domains in rarity_metrics['rare_signals'].items():
            st.write(f"**{model}**: Unique finds: {', '.join(domains)}")
    
    # Return all metrics for further processing
    return {
        "divergence_metrics": divergence_metrics,
        "blindspot_metrics": blindspot_metrics,
        "rarity_metrics": rarity_metrics
    }

def render_model_comparison_dashboard():
    """Render the model comparison dashboard."""
    st.title("🔍 LLMPageRank Model Comparison")
    st.subheader("PRD-25: LLM Model Enrichment & Signal Divergence Indexing (Purity25)")
    
    # Tabs for different views
    tab1, tab2, tab3, tab4, tab5 = st.tabs([
        "Live Comparison", 
        "Divergence Analysis", 
        "Blindspot Detection", 
        "Signal Rarity", 
        "Weekly Digest"
    ])
    
    # Tab 1: Live Comparison
    with tab1:
        st.subheader("Run Live Model Comparison")
        
        with st.form("comparison_form"):
            prompt = st.text_area(
                "Enter a prompt to compare across models:",
                "What are the top AI research and development websites?"
            )
            
            category = st.text_input(
                "Enter a category for this prompt:",
                "AI Research"
            )
            
            submitted = st.form_submit_button("Run Comparison")
        
        if submitted:
            metrics = run_model_comparison(prompt, category)
            
            # Option to generate weekly summaries
            if st.button("Generate Weekly Digest"):
                with st.spinner("Generating weekly digest..."):
                    gap_detector.generate_weekly_blindspot_summary()
                    signal_rarity_profiler.generate_signal_opportunity_report()
                
                st.success("Weekly digest generated! Check the Weekly Digest tab.")
    
    # Tab 2: Divergence Analysis
    with tab2:
        st.subheader("Model Divergence Analysis")
        
        # Load divergence logs
        divergence_logs = load_divergence_logs()
        
        if not divergence_logs:
            st.info("No divergence logs available. Run a comparison first.")
        else:
            # Convert to DataFrame
            df = pd.DataFrame(divergence_logs)
            
            # Display overall metrics
            cols = st.columns(3)
            
            with cols[0]:
                avg_disagreement = df['model_disagreement_score'].mean()
                st.metric(
                    "Average Disagreement Score", 
                    f"{avg_disagreement:.2f}"
                )
            
            with cols[1]:
                avg_overlap = df['domain_citation_overlap'].mean()
                st.metric(
                    "Average Citation Overlap", 
                    f"{avg_overlap:.2f}"
                )
            
            with cols[2]:
                total_prompts = len(df)
                st.metric(
                    "Total Prompts Analyzed", 
                    total_prompts
                )
            
            # Filter by category
            categories = df['category'].unique()
            selected_category = st.selectbox(
                "Filter by Category",
                options=["All Categories"] + list(categories)
            )
            
            if selected_category != "All Categories":
                filtered_df = df[df['category'] == selected_category]
            else:
                filtered_df = df
            
            # Display disagreement trend
            st.subheader("Disagreement Score Trend")
            
            if 'timestamp' in filtered_df.columns:
                filtered_df['date'] = pd.to_datetime(filtered_df['timestamp'])
                filtered_df = filtered_df.sort_values('date')
                
                fig = px.line(
                    filtered_df,
                    x='date',
                    y='model_disagreement_score',
                    title="Model Disagreement Score Over Time",
                    labels={
                        "date": "Date",
                        "model_disagreement_score": "Disagreement Score"
                    }
                )
                
                st.plotly_chart(fig, use_container_width=True)
            
            # Display category comparison
            st.subheader("Category Comparison")
            
            category_metrics = df.groupby('category').agg({
                'model_disagreement_score': 'mean',
                'domain_citation_overlap': 'mean',
                'domains_cited': 'mean'
            }).reset_index()
            
            fig = px.bar(
                category_metrics,
                x='category',
                y='model_disagreement_score',
                color='model_disagreement_score',
                title="Average Disagreement Score by Category",
                labels={
                    "category": "Category",
                    "model_disagreement_score": "Disagreement Score"
                },
                color_continuous_scale="Viridis"
            )
            
            st.plotly_chart(fig, use_container_width=True)
    
    # Tab 3: Blindspot Detection
    with tab3:
        st.subheader("Model Blindspot Detection")
        
        # Load blindspot data
        blindspot_data = load_blindspot_data()
        
        if not blindspot_data:
            st.info("No blindspot data available. Run a comparison first.")
        else:
            # Extract metrics
            metrics_list = [item.get('metrics', {}) for item in blindspot_data]
            
            # Convert to DataFrame
            metrics_df = pd.DataFrame(metrics_list)
            
            # Display overall metrics
            cols = st.columns(3)
            
            with cols[0]:
                avg_blindspot_ratio = metrics_df['blindspot_ratio'].mean()
                st.metric(
                    "Average Blindspot Ratio", 
                    f"{avg_blindspot_ratio:.2f}"
                )
            
            with cols[1]:
                total_blindspots = metrics_df['total_blindspots'].sum()
                st.metric(
                    "Total Blindspots Detected", 
                    total_blindspots
                )
            
            with cols[2]:
                total_prompts = len(metrics_df)
                st.metric(
                    "Total Prompts Analyzed", 
                    total_prompts
                )
            
            # Show detailed blindspot analysis
            st.subheader("Blindspot Analysis")
            
            # Count domains with blindspots
            blindspot_counts = {}
            
            for item in blindspot_data:
                for domain, missing_models in item.get('blindspots', {}).items():
                    if domain not in blindspot_counts:
                        blindspot_counts[domain] = 0
                    
                    blindspot_counts[domain] += len(missing_models)
            
            # Convert to DataFrame
            blindspot_df = pd.DataFrame({
                "Domain": list(blindspot_counts.keys()),
                "Missing Count": list(blindspot_counts.values())
            })
            
            # Sort by missing count
            blindspot_df = blindspot_df.sort_values("Missing Count", ascending=False)
            
            # Display as bar chart
            fig = px.bar(
                blindspot_df.head(10),
                x="Domain",
                y="Missing Count",
                title="Top 10 Domains with Most Blindspots",
                color="Missing Count",
                color_continuous_scale="Reds"
            )
            
            st.plotly_chart(fig, use_container_width=True)
            
            # Count which models miss the most
            model_miss_counts = {}
            
            for item in blindspot_data:
                for domain, missing_models in item.get('blindspots', {}).items():
                    for model in missing_models:
                        if model not in model_miss_counts:
                            model_miss_counts[model] = 0
                        
                        model_miss_counts[model] += 1
            
            # Convert to DataFrame
            model_df = pd.DataFrame({
                "Model": list(model_miss_counts.keys()),
                "Missing Count": list(model_miss_counts.values())
            })
            
            # Sort by missing count
            model_df = model_df.sort_values("Missing Count", ascending=False)
            
            # Display as bar chart
            fig = px.bar(
                model_df,
                x="Model",
                y="Missing Count",
                title="Models with Most Blindspots",
                color="Missing Count",
                color_continuous_scale="Oranges"
            )
            
            st.plotly_chart(fig, use_container_width=True)
    
    # Tab 4: Signal Rarity
    with tab4:
        st.subheader("Signal Rarity Analysis")
        
        # Load rare signal data
        rare_signal_data = load_rare_signals()
        
        if not rare_signal_data:
            st.info("No rare signal data available. Run a comparison first.")
        else:
            # Extract metrics
            metrics_list = [item.get('metrics', {}) for item in rare_signal_data]
            
            # Convert to DataFrame
            metrics_df = pd.DataFrame(metrics_list)
            
            # Display overall metrics
            cols = st.columns(3)
            
            with cols[0]:
                avg_rarity_ratio = metrics_df['rarity_ratio'].mean()
                st.metric(
                    "Average Rarity Ratio", 
                    f"{avg_rarity_ratio:.2f}"
                )
            
            with cols[1]:
                total_rare_signals = metrics_df['total_rare_signals'].sum()
                st.metric(
                    "Total Rare Signals Detected", 
                    total_rare_signals
                )
            
            with cols[2]:
                total_prompts = len(metrics_df)
                st.metric(
                    "Total Prompts Analyzed", 
                    total_prompts
                )
            
            # Count unique domains by model
            model_unique_domains = {}
            
            for item in rare_signal_data:
                for model, domains in item.get('rare_signals', {}).items():
                    if model not in model_unique_domains:
                        model_unique_domains[model] = set()
                    
                    model_unique_domains[model].update(domains)
            
            # Convert to DataFrame
            model_df = pd.DataFrame({
                "Model": list(model_unique_domains.keys()),
                "Unique Domains": [len(domains) for domains in model_unique_domains.values()]
            })
            
            # Sort by unique domains
            model_df = model_df.sort_values("Unique Domains", ascending=False)
            
            # Display as bar chart
            fig = px.bar(
                model_df,
                x="Model",
                y="Unique Domains",
                title="Models with Most Unique Domain Citations",
                color="Unique Domains",
                color_continuous_scale="Greens"
            )
            
            st.plotly_chart(fig, use_container_width=True)
            
            # Show opportunity scores
            st.subheader("Model Opportunity Scores")
            
            # Extract opportunity scores
            opportunity_scores = {}
            
            for item in rare_signal_data:
                for model, score in item.get('opportunity_scores', {}).items():
                    if model not in opportunity_scores:
                        opportunity_scores[model] = []
                    
                    opportunity_scores[model].append(score)
            
            # Calculate average scores
            avg_scores = {
                model: sum(scores) / len(scores) if scores else 0
                for model, scores in opportunity_scores.items()
            }
            
            # Convert to DataFrame
            scores_df = pd.DataFrame({
                "Model": list(avg_scores.keys()),
                "Average Opportunity Score": list(avg_scores.values())
            })
            
            # Sort by score
            scores_df = scores_df.sort_values("Average Opportunity Score", ascending=False)
            
            # Display as bar chart
            fig = px.bar(
                scores_df,
                x="Model",
                y="Average Opportunity Score",
                title="Average Opportunity Scores by Model",
                color="Average Opportunity Score",
                color_continuous_scale="Blues"
            )
            
            st.plotly_chart(fig, use_container_width=True)
    
    # Tab 5: Weekly Digest
    with tab5:
        st.subheader("Weekly Digest")
        
        # Load weekly digest
        weekly_digest = load_weekly_digest()
        
        if not weekly_digest:
            st.info("No weekly digest available. Generate one in the Live Comparison tab.")
        else:
            # Display digest info
            st.write(f"**Week of:** {weekly_digest.get('week')}")
            st.write(f"**Total Prompts Analyzed:** {weekly_digest.get('total_prompts')}")
            st.write(f"**Categories Covered:** {weekly_digest.get('total_categories')}")
            st.write(f"**Best Model Overall:** {weekly_digest.get('best_model_overall')}")
            st.write(f"**Most Missing Model:** {weekly_digest.get('worst_model_overall')}")
            
            # Display example entry
            st.subheader("Weekly Digest Example Entry")
            
            example = weekly_digest.get('weekly_digest_example', {})
            
            if example:
                st.json(example)
            
            # Display category summaries
            st.subheader("Category Summaries")
            
            category_summaries = weekly_digest.get('category_summaries', {})
            
            for category, summary in category_summaries.items():
                with st.expander(f"{category} ({summary.get('prompts', 0)} prompts)"):
                    cols = st.columns(2)
                    
                    with cols[0]:
                        st.write(f"**Best Model:** {summary.get('best_model', 'N/A')}")
                        st.write(f"**Blindspot Ratio:** {summary.get('blindspot_ratio', 0):.2f}")
                    
                    with cols[1]:
                        st.write(f"**Worst Model:** {summary.get('worst_model', 'N/A')}")
                        st.write(f"**Total Blindspots:** {summary.get('total_blindspots', 0)}")
                    
                    st.write("**Most Missed Domains:**")
                    
                    most_missed = summary.get('most_missed_domains', {})
                    
                    for domain, count in most_missed.items():
                        st.write(f"- {domain}: Missed {count} times")

def main():
    """Main function."""
    render_model_comparison_dashboard()

if __name__ == "__main__":
    main()