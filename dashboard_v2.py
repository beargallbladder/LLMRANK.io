"""
Enhanced Dashboard Module for LLMPageRank V2

This module implements the V2 requirements for the Private Observability Layer,
providing enhanced visualizations and insights for trust signals.
"""

import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px
import plotly.graph_objects as go
from datetime import datetime, timedelta
import time
import json

from data_storage import (
    load_trends_data, 
    load_domain_test_results,
    get_domain_status_summary,
    format_timestamp,
    get_latest_domain_result
)
import database_v2 as db_v2
from prompt_manager import prompt_manager
from delta_tracker import get_weekly_movers, get_opportunity_targets
from config import VERSION_INFO, CATEGORIES, LLM_MODELS

def render_v2_dashboard():
    """Render the enhanced V2 dashboard."""
    st.title("LLMPageRank V2 - Trust Signal Intelligence")
    
    # Display version info
    st.markdown(f"**System Version:** {VERSION_INFO['version']} ({VERSION_INFO['release_date']})")
    
    # Add enhanced dashboard style
    st.markdown("""
    <style>
        .metric-title {
            font-size: 14px;
            color: #666;
        }
        .metric-value {
            font-size: 28px;
            font-weight: bold;
        }
        .metric-delta {
            font-size: 12px;
        }
        .trust-rising {
            color: #00CC00;
        }
        .trust-falling {
            color: #CC0000;
        }
        .trust-stable {
            color: #666666;
        }
        .opportunity-score {
            font-size: 18px;
            font-weight: bold;
            color: #0000CC;
        }
    </style>
    """, unsafe_allow_html=True)
    
    # Load current trends data
    trends_data = load_trends_data()
    last_updated = format_timestamp(trends_data.get("last_updated", time.time()))
    
    # Top navigation
    st.markdown(f"**Last updated:** {last_updated}")
    tabs = st.tabs([
        "Trust Intelligence", 
        "Opportunity Targets", 
        "Prompt Precision", 
        "Longitudinal Analysis",
        "Customer Targeting"
    ])
    
    with tabs[0]:
        render_trust_intelligence(trends_data)
        
    with tabs[1]:
        render_opportunity_targets()
        
    with tabs[2]:
        render_prompt_precision()
        
    with tabs[3]:
        render_longitudinal_analysis()
        
    with tabs[4]:
        render_customer_targeting()

def render_trust_intelligence(trends_data):
    """Render the trust intelligence tab with key metrics."""
    st.subheader("🔍 Trust Signal Intelligence")
    
    # Get domain summary and weekly movers
    domain_summary = get_domain_status_summary()
    weekly_movers = get_weekly_movers()
    
    # Top metrics row
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        st.metric(
            label="Total Domains Tracked", 
            value=domain_summary.get("total_discovered", 0)
        )
    
    with col2:
        movers_count = len(weekly_movers.get("movers", []))
        st.metric(
            label="Trust Shifting Domains", 
            value=movers_count
        )
        
    with col3:
        top_score = 0
        if trends_data.get("top_domains"):
            top_score = trends_data["top_domains"][0].get("visibility_score", 0)
        st.metric(
            label="Highest Trust Score", 
            value=f"{top_score:.1f}"
        )
        
    with col4:
        biggest_delta = 0
        if weekly_movers.get("movers"):
            biggest_delta = abs(weekly_movers["movers"][0].get("delta", 0))
        st.metric(
            label="Biggest Weekly Shift", 
            value=f"{biggest_delta:.1f}"
        )
    
    # Weekly movers
    st.subheader("📈 Trust Signal Movers (Weekly)")
    
    movers = weekly_movers.get("movers", [])
    if movers:
        # Create DataFrame
        movers_df = pd.DataFrame(movers)
        
        # Add direction for coloring
        movers_df["direction"] = movers_df["delta"].apply(
            lambda x: "up" if x > 0 else "down"
        )
        
        # Display date of measurement
        st.markdown(f"**Measurement date:** {weekly_movers.get('date', 'N/A')}")
        
        # Create visualization
        fig = px.bar(
            movers_df.head(10),
            x="delta",
            y="domain",
            orientation="h",
            color="direction",
            color_discrete_map={"up": "#00CC00", "down": "#CC0000"},
            labels={"delta": "Trust Score Delta", "domain": "Domain"},
            title="Top Trust Signal Movers",
            hover_data=["llmrank_today", "llmrank_last_week", "status"]
        )
        
        st.plotly_chart(fig, use_container_width=True)
        
        # Create detailed table
        cols = ["domain", "llmrank_today", "llmrank_last_week", "delta", "status"]
        st.dataframe(
            movers_df[cols].head(10).style.applymap(
                lambda x: "background-color: #E8F5E9" if isinstance(x, str) and "Rising" in x 
                else ("background-color: #FFEBEE" if isinstance(x, str) and "Falling" in x else ""),
                subset=["status"]
            )
        )
        
        # Show models and prompts for the top mover
        if movers:
            top_mover = movers[0]
            st.subheader(f"Detailed Analysis: {top_mover.get('domain', '')}")
            
            col1, col2 = st.columns(2)
            
            with col1:
                st.markdown("**Contributing Models:**")
                for model in top_mover.get("models", []):
                    if isinstance(model, str):
                        model_name = LLM_MODELS.get(model, {}).get("name", model) if isinstance(LLM_MODELS.get(model), dict) else model
                        st.markdown(f"- {model_name}")
            
            with col2:
                st.markdown("**Triggering Prompts:**")
                for prompt in top_mover.get("triggering_prompts", []):
                    st.markdown(f"- \"{prompt}\"")
    else:
        st.info("No weekly movers data available yet.")
    
    # Consensus breakdown
    st.subheader("🤝 Trust Consensus Breakdown")
    
    # Create example consensus data if real data not available yet
    if trends_data.get("consensus_breakdown"):
        consensus_data = trends_data["consensus_breakdown"]
    else:
        # Placeholder data
        consensus_data = {
            "high_consensus": {
                "count": sum(1 for d in trends_data.get("top_domains", []) 
                        if d.get("consensus_score", 0) > 0.8),
                "domains": [d for d in trends_data.get("top_domains", [])[:5] 
                        if d.get("consensus_score", 0) > 0.8]
            },
            "medium_consensus": {
                "count": sum(1 for d in trends_data.get("top_domains", []) 
                        if 0.4 <= d.get("consensus_score", 0) <= 0.8),
                "domains": [d for d in trends_data.get("top_domains", [])[:5] 
                        if 0.4 <= d.get("consensus_score", 0) <= 0.8]
            },
            "low_consensus": {
                "count": sum(1 for d in trends_data.get("top_domains", []) 
                        if d.get("consensus_score", 0) < 0.4),
                "domains": [d for d in trends_data.get("top_domains", [])[:5] 
                        if d.get("consensus_score", 0) < 0.4]
            }
        }
    
    # Display consensus breakdown
    col1, col2, col3 = st.columns(3)
    
    with col1:
        st.metric("High Consensus", consensus_data.get("high_consensus", {}).get("count", 0))
        for domain in consensus_data.get("high_consensus", {}).get("domains", [])[:3]:
            if isinstance(domain, dict):
                st.markdown(f"- {domain.get('domain', '')}")
    
    with col2:
        st.metric("Medium Consensus", consensus_data.get("medium_consensus", {}).get("count", 0))
        for domain in consensus_data.get("medium_consensus", {}).get("domains", [])[:3]:
            if isinstance(domain, dict):
                st.markdown(f"- {domain.get('domain', '')}")
    
    with col3:
        st.metric("Low Consensus", consensus_data.get("low_consensus", {}).get("count", 0))
        for domain in consensus_data.get("low_consensus", {}).get("domains", [])[:3]:
            if isinstance(domain, dict):
                st.markdown(f"- {domain.get('domain', '')}")
    
    # Vertical breakdown
    st.subheader("📊 Trust by Vertical")
    
    # Display vertical stats
    category_stats = trends_data.get("category_stats", {})
    
    if category_stats:
        # Prepare data
        categories = []
        avg_scores = []
        domain_counts = []
        
        for category, stats in category_stats.items():
            categories.append(category)
            avg_scores.append(stats.get("avg_visibility", 0))
            domain_counts.append(stats.get("domain_count", 0))
        
        # Create category comparison chart
        category_df = pd.DataFrame({
            "category": categories,
            "avg_trust_score": avg_scores,
            "domain_count": domain_counts
        })
        
        fig = px.bar(
            category_df,
            x="category",
            y="avg_trust_score",
            color="category",
            size="domain_count",
            labels={"category": "Vertical", "avg_trust_score": "Average Trust Score", "domain_count": "Number of Domains"},
            title="Average Trust Score by Vertical"
        )
        st.plotly_chart(fig, use_container_width=True)
    else:
        st.info("No category stats available yet.")

def render_opportunity_targets():
    """Render the opportunity targets tab."""
    st.subheader("🎯 Opportunity Targets")
    
    # Get opportunity targets
    targets = get_opportunity_targets().get("targets", [])
    
    if targets:
        # Create DataFrame
        targets_df = pd.DataFrame(targets)
        
        # Calculate delta from SEO to visibility
        if "structure_score" in targets_df.columns and "visibility_score" in targets_df.columns:
            targets_df["gap"] = targets_df["structure_score"] - targets_df["visibility_score"]
        
        # Add filters
        col1, col2 = st.columns([1, 2])
        
        with col1:
            min_score = st.slider(
                "Minimum Opportunity Score", 
                min_value=0.0, 
                max_value=10.0, 
                value=5.0,
                step=0.5
            )
            
            # Initialize selected_categories with an empty list
            selected_categories = []
            if "category" in targets_df.columns:
                categories_list = targets_df["category"].unique().tolist()
                selected_categories = st.multiselect(
                    "Verticals",
                    options=categories_list,
                    default=[]
                )
        
        # Filter data
        filtered_df = targets_df[targets_df["opportunity_score"] >= min_score]
        if selected_categories:
            filtered_df = filtered_df[filtered_df["category"].isin(selected_categories)]
        
        # Display top opportunities
        st.subheader("Top Trust Gap Opportunities")
        
        # Create visualization
        if not filtered_df.empty:
            # Visualization of trust gap
            fig = px.scatter(
                filtered_df.head(20),
                x="structure_score",
                y="visibility_score",
                size="opportunity_score",
                color="customer_likelihood",
                hover_name="domain",
                labels={
                    "structure_score": "Structure Score (SEO)",
                    "visibility_score": "Trust Visibility Score",
                    "opportunity_score": "Opportunity Size",
                    "customer_likelihood": "Customer Likelihood"
                },
                title="Trust Gap Map - Structure vs Visibility"
            )
            
            # Add diagonal line (perfect alignment)
            fig.add_shape(
                type="line",
                x0=0, y0=0,
                x1=100, y1=100,
                line=dict(color="gray", dash="dash"),
                opacity=0.5
            )
            
            st.plotly_chart(fig, use_container_width=True)
            
            # Display table of opportunities
            st.dataframe(
                filtered_df[["domain", "category", "opportunity_score", 
                             "customer_likelihood", "structure_score", 
                             "visibility_score"]].head(10).style.format({
                    "opportunity_score": "{:.1f}",
                    "structure_score": "{:.1f}",
                    "visibility_score": "{:.1f}"
                }).background_gradient(cmap="Blues", subset=["opportunity_score"])
            )
            
            # Detailed view of top opportunity
            if not filtered_df.empty:
                top_opportunity = filtered_df.iloc[0]
                st.subheader(f"Top Opportunity: {top_opportunity.get('domain')}")
                
                col1, col2, col3 = st.columns(3)
                with col1:
                    st.metric("Opportunity Score", f"{top_opportunity.get('opportunity_score', 0):.1f}")
                with col2:
                    st.metric("Customer Likelihood", f"{top_opportunity.get('customer_likelihood', 0)}%")
                with col3:
                    st.metric("Trust Gap", f"{top_opportunity.get('gap', 0):.1f}")
                
                # Display attributes
                st.markdown("**Opportunity Attributes:**")
                col1, col2, col3 = st.columns(3)
                with col1:
                    st.markdown(f"Ad Spend: {'✓' if top_opportunity.get('has_ads') else '✗'}")
                with col2:
                    st.markdown(f"Schema Markup: {'✓' if top_opportunity.get('has_schema') else '✗'}")
                with col3:
                    st.markdown(f"SEO Stack: {'✓' if top_opportunity.get('has_seo_stack') else '✗'}")
        else:
            st.info("No opportunities match the current filters.")
    else:
        st.info("No opportunity targets data available yet.")

def render_prompt_precision():
    """Render the prompt precision tab."""
    st.subheader("⚙️ Prompt Precision Engine")
    
    # Get top performing prompts
    top_prompts = prompt_manager.get_top_performing_prompts(limit=20)
    
    if top_prompts:
        # Create DataFrame
        prompts_df = pd.DataFrame(top_prompts)
        
        # Add filters
        col1, col2 = st.columns([1, 2])
        
        # Initialize filter variables
        selected_intents = []
        selected_categories = []
        
        with col1:
            if "intent" in prompts_df.columns:
                intent_list = prompts_df["intent"].unique().tolist()
                selected_intents = st.multiselect(
                    "Intent Type",
                    options=intent_list,
                    default=[]
                )
            
            if "category" in prompts_df.columns:
                category_list = prompts_df["category"].unique().tolist()
                selected_categories = st.multiselect(
                    "Verticals",
                    options=category_list,
                    default=[]
                )
        
        # Filter data
        filtered_df = prompts_df.copy()
        if selected_intents:
            filtered_df = filtered_df[filtered_df["intent"].isin(selected_intents)]
        if selected_categories:
            filtered_df = filtered_df[filtered_df["category"].isin(selected_categories)]
        
        # Display prompts analysis
        st.subheader("Top Performing Prompts")
        
        if not filtered_df.empty:
            # Visualization
            if "category" in filtered_df.columns and "citation_frequency" in filtered_df.columns:
                fig = px.bar(
                    filtered_df.head(10),
                    x="citation_frequency",
                    y="prompt_id",
                    color="category",
                    labels={
                        "citation_frequency": "Citation Frequency",
                        "prompt_id": "Prompt ID",
                        "category": "Vertical"
                    },
                    title="Top Performing Prompts by Citation Frequency",
                    orientation="h",
                    hover_data=["prompt_text", "intent", "total_runs"]
                )
                
                st.plotly_chart(fig, use_container_width=True)
            
            # Display detailed prompt data
            st.dataframe(
                filtered_df[["prompt_id", "prompt_text", "intent", "category", 
                             "citation_frequency", "model_coverage", "total_runs"]].head(10)
                .style.format({
                    "citation_frequency": "{:.2f}",
                    "model_coverage": "{:.2f}"
                }).background_gradient(cmap="Greens", subset=["citation_frequency"])
            )
            
            # Show prompt performance by intent type
            st.subheader("Performance by Intent Type")
            
            if "intent" in filtered_df.columns and "citation_frequency" in filtered_df.columns:
                intent_perf = filtered_df.groupby("intent").agg({
                    "citation_frequency": "mean",
                    "model_coverage": "mean",
                    "total_runs": "sum",
                    "prompt_id": "count"
                }).reset_index()
                
                intent_perf = intent_perf.rename(columns={"prompt_id": "prompt_count"})
                
                fig = px.bar(
                    intent_perf,
                    x="intent",
                    y="citation_frequency",
                    color="intent",
                    size="prompt_count",
                    labels={
                        "intent": "Intent Type",
                        "citation_frequency": "Avg. Citation Frequency",
                        "prompt_count": "Number of Prompts"
                    },
                    title="Performance by Intent Type"
                )
                
                st.plotly_chart(fig, use_container_width=True)
        else:
            st.info("No prompts match the current filters.")
    else:
        st.info("No prompt performance data available yet.")

def render_longitudinal_analysis():
    """Render the longitudinal analysis tab."""
    st.subheader("📏 Longitudinal Trust Analysis")
    
    # Domain search for time-series data
    domain_search = st.text_input("Search for a domain", placeholder="example.com")
    
    if domain_search:
        # Get time-series data for the domain
        time_series = db_v2.get_domain_time_series(domain_search)
        
        if time_series:
            # Convert to DataFrame
            ts_df = pd.DataFrame(time_series)
            
            # Display domain trend
            st.subheader(f"Trust Trend for {domain_search}")
            
            # Extract and convert date
            if "date" in ts_df.columns and "llmrank" in ts_df.columns:
                # Convert date strings to datetime if needed
                if ts_df["date"].dtype == object:
                    ts_df["date"] = pd.to_datetime(ts_df["date"])
                
                # Sort by date
                ts_df = ts_df.sort_values("date")
                
                # Create trend visualization
                fig = px.line(
                    ts_df,
                    x="date",
                    y="llmrank",
                    labels={
                        "date": "Date",
                        "llmrank": "Trust Score (LLMRank)"
                    },
                    title=f"LLMRank Trend for {domain_search}",
                    markers=True
                )
                
                # Add trend annotations
                if "status" in ts_df.columns:
                    for idx, row in ts_df.iterrows():
                        status = row.get("status")
                        date = row.get("date")
                        llmrank = row.get("llmrank")
                        
                        if status == "Trust Rising":
                            fig.add_annotation(
                                x=date,
                                y=llmrank,
                                text="▲",
                                showarrow=False,
                                font=dict(color="green", size=16)
                            )
                        elif status == "Trust Falling":
                            fig.add_annotation(
                                x=date,
                                y=llmrank,
                                text="▼",
                                showarrow=False,
                                font=dict(color="red", size=16)
                            )
                
                st.plotly_chart(fig, use_container_width=True)
                
                # Display events table
                st.subheader("Trust Events")
                
                events_df = ts_df[["date", "llmrank", "delta", "status"]].copy()
                
                # Format delta for display
                events_df["formatted_delta"] = events_df["delta"].apply(
                    lambda x: f"+{x:.1f}" if x > 0 else f"{x:.1f}" if x < 0 else "0.0"
                )
                
                st.dataframe(
                    events_df[["date", "llmrank", "formatted_delta", "status"]].style.applymap(
                        lambda x: "color: green" if isinstance(x, str) and "+" in x 
                        else ("color: red" if isinstance(x, str) and "-" in x else ""),
                        subset=["formatted_delta"]
                    )
                )
                
                # Show triggering models and prompts
                st.subheader("Contributing Factors")
                
                if len(ts_df) > 0:
                    latest = ts_df.iloc[-1]
                    models = latest.get("models")
                    prompts = latest.get("triggering_prompts")
                    
                    col1, col2 = st.columns(2)
                    
                    with col1:
                        st.markdown("**Models:**")
                        if isinstance(models, list):
                            for model in models:
                                model_name = LLM_MODELS.get(model, {}).get("name", model) if isinstance(LLM_MODELS.get(model), dict) else model
                                st.markdown(f"- {model_name}")
                        else:
                            st.info("No model data available.")
                    
                    with col2:
                        st.markdown("**Triggering Prompts:**")
                        if isinstance(prompts, list):
                            for prompt in prompts:
                                st.markdown(f"- \"{prompt}\"")
                        else:
                            st.info("No prompt data available.")
            else:
                st.warning("Time-series data has an unexpected format.")
        else:
            st.warning(f"No time-series data found for domain: {domain_search}")
            
            # Show regular domain results if available
            domain_results = load_domain_test_results(domain_search)
            if domain_results:
                st.info("Regular domain test results are available, but no time-series data yet.")
                
                latest = domain_results[0]
                
                # Display basic metrics
                col1, col2, col3 = st.columns(3)
                with col1:
                    st.metric("Visibility Score", f"{latest.get('visibility_score', 0):.1f}")
                with col2:
                    st.metric("Structure Score", f"{latest.get('structure_score', 0):.1f}")
                with col3:
                    st.metric("Consensus Score", f"{latest.get('consensus_score', 0):.2f}")
            else:
                st.warning(f"No data found for domain: {domain_search}")
    else:
        st.info("Enter a domain name to see longitudinal analysis.")

def render_customer_targeting():
    """Render the customer targeting tab."""
    st.subheader("💼 Customer Targeting")
    
    # Get opportunity targets for customer targeting
    targets = get_opportunity_targets().get("targets", [])
    
    if targets:
        # Filter for high customer likelihood
        high_likelihood_targets = [t for t in targets if t.get("customer_likelihood", 0) >= 70]
        
        if high_likelihood_targets:
            # Create DataFrame
            targets_df = pd.DataFrame(high_likelihood_targets)
            
            # Display top prospects
            st.subheader("Top Customer Prospects")
            
            # Create visualization
            fig = px.scatter(
                targets_df,
                x="structure_score",
                y="visibility_score",
                size="opportunity_score",
                color="customer_likelihood",
                hover_name="domain",
                labels={
                    "structure_score": "Structure Score (SEO)",
                    "visibility_score": "Trust Visibility Score",
                    "opportunity_score": "Opportunity Size",
                    "customer_likelihood": "Customer Likelihood"
                },
                title="Customer Prospect Matrix"
            )
            
            st.plotly_chart(fig, use_container_width=True)
            
            # Display table of prospects
            st.dataframe(
                targets_df[["domain", "category", "opportunity_score", 
                           "customer_likelihood"]].head(10).style.format({
                    "opportunity_score": "{:.1f}",
                    "customer_likelihood": "{:.0f}%"
                }).background_gradient(cmap="Reds", subset=["customer_likelihood"])
            )
            
            # Show targeting criteria
            st.subheader("Targeting Criteria")
            
            # Count by attribute
            has_ads_count = sum(1 for t in high_likelihood_targets if t.get("has_ads", False))
            has_schema_count = sum(1 for t in high_likelihood_targets if t.get("has_schema", False))
            has_seo_count = sum(1 for t in high_likelihood_targets if t.get("has_seo_stack", False))
            
            total = len(high_likelihood_targets)
            
            # Create attribute distribution chart
            attr_data = pd.DataFrame({
                "Attribute": ["Has Ads", "Has Schema", "Has SEO Tools"],
                "Count": [has_ads_count, has_schema_count, has_seo_count],
                "Percentage": [has_ads_count/total*100, has_schema_count/total*100, has_seo_count/total*100]
            })
            
            fig = px.bar(
                attr_data,
                x="Attribute",
                y="Percentage",
                color="Attribute",
                text="Count",
                labels={
                    "Attribute": "Customer Attribute",
                    "Percentage": "% of Prospects"
                },
                title="Prospect Attribute Distribution"
            )
            
            st.plotly_chart(fig, use_container_width=True)
            
            # Breakdown by category
            if "category" in targets_df.columns:
                category_counts = targets_df["category"].value_counts().reset_index()
                category_counts.columns = ["Category", "Count"]
                
                # Add percentage
                category_counts["Percentage"] = category_counts["Count"] / category_counts["Count"].sum() * 100
                
                # Create pie chart
                fig = px.pie(
                    category_counts,
                    names="Category",
                    values="Count",
                    title="Prospects by Vertical"
                )
                
                st.plotly_chart(fig, use_container_width=True)
            
            # Top prospect detail
            if len(high_likelihood_targets) > 0:
                top_prospect = high_likelihood_targets[0]
                st.subheader(f"Priority Target: {top_prospect.get('domain')}")
                
                col1, col2, col3 = st.columns(3)
                with col1:
                    st.metric("Customer Likelihood", f"{top_prospect.get('customer_likelihood', 0)}%")
                with col2:
                    st.metric("Opportunity Score", f"{top_prospect.get('opportunity_score', 0):.1f}")
                with col3:
                    st.metric("Category", top_prospect.get("category", "Unknown"))
                
                # Display attributes
                st.markdown("**Target Attributes:**")
                col1, col2, col3 = st.columns(3)
                with col1:
                    st.markdown(f"Ad Spend: {'✓' if top_prospect.get('has_ads') else '✗'}")
                with col2:
                    st.markdown(f"Schema Markup: {'✓' if top_prospect.get('has_schema') else '✗'}")
                with col3:
                    st.markdown(f"SEO Stack: {'✓' if top_prospect.get('has_seo_stack') else '✗'}")
                
                # Marketing message template
                st.subheader("Target Messaging Template")
                
                domain = top_prospect.get("domain", "example.com")
                category = top_prospect.get("category", "your industry")
                visibility_score = top_prospect.get("visibility_score", 0)
                structure_score = top_prospect.get("structure_score", 0)
                
                message = f"""
                Dear {domain} Team,
                
                Our AI Trust Intelligence platform has identified that while your website has strong technical optimization (Structure Score: {structure_score:.1f}), your visibility to AI systems is significantly lower (Trust Score: {visibility_score:.1f}).
                
                This gap represents a critical opportunity in {category}, as more users are now finding information through AI systems rather than traditional search.
                
                We'd like to offer a complimentary Trust Signal Analysis to show you specifically why AIs may not be citing your content despite your strong technical foundation.
                
                Would you have 15 minutes this week to discuss how we can help ensure your content gets the AI visibility it deserves?
                
                Best regards,
                The LLMPageRank Team
                """
                
                st.text_area("Personalized Outreach Template", message, height=300)
        else:
            st.info("No high likelihood customer prospects identified yet.")
    else:
        st.info("No customer targeting data available yet.")