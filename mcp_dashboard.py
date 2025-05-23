"""
LLMPageRank Model Context Protocol (MCP) Dashboard

This module implements the dashboard for the Model Context Protocol (MCP) interface
that visualizes real-time trust context for domains, categories, and the RankLLM.io leaderboard.
"""

import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import datetime
import json
import os
import random

import mcp_dispatcher


def render_mcp_dashboard():
    """Render the MCP dashboard."""
    st.title("LLMPageRank Model Context Protocol (MCP)")
    st.markdown("### Real-time trust context for agents, dashboards, and RankLLM.io")
    
    # Create tabs for different views
    tab1, tab2, tab3, tab4, tab5 = st.tabs([
        "Domain Context", 
        "Drift Events", 
        "Prompt Suggestions",
        "FOMA Threats",
        "RankLLM Leaderboard"
    ])
    
    with tab1:
        render_domain_context()
    
    with tab2:
        render_drift_events()
    
    with tab3:
        render_prompt_suggestions()
    
    with tab4:
        render_foma_threats()
    
    with tab5:
        render_rankllm_leaderboard()
    
    # MCP Health Metrics
    st.markdown("---")
    st.markdown("### MCP Health Metrics")
    
    # Get health metrics
    health_metrics = mcp_dispatcher.get_health_metrics()
    
    # Display metrics in columns
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        st.metric("Registered Agents", health_metrics.get("registered_agents", 0))
    
    with col2:
        st.metric("Context Requests", health_metrics.get("mcp_context_requests", 0))
    
    with col3:
        st.metric("RankLLM Updates", health_metrics.get("rankllm_updates", 0))
    
    with col4:
        st.metric("Runtime Uptime", health_metrics.get("runtime_uptime", "0%"))
    
    # Failed Prompts
    failed_prompts = health_metrics.get("failed_prompts", 0)
    if failed_prompts > 0:
        st.warning(f"Failed Prompts: {failed_prompts}")
    else:
        st.success("No Failed Prompts")


def render_domain_context():
    """Render the domain context section."""
    st.markdown("## Domain Trust Context")
    st.markdown("Get real-time trust context for a domain")
    
    # Domain input
    domain_options = [
        "asana.com",
        "monday.com",
        "notion.so",
        "salesforce.com",
        "hubspot.com",
        "shopify.com",
        "bigcommerce.com",
        "stripe.com",
        "twilio.com",
        "zendesk.com"
    ]
    
    selected_domain = st.selectbox("Select Domain", domain_options)
    
    if st.button("Get Domain Context"):
        with st.spinner(f"Getting context for {selected_domain}..."):
            # Get domain context
            context = mcp_dispatcher.mcp_context(selected_domain)
            
            # Display context
            col1, col2 = st.columns([2, 1])
            
            with col1:
                # Create metrics
                st.metric("LLM Score", context.get("llm_score", 0))
                st.metric("Trust Drift Delta", context.get("trust_drift_delta", 0), delta=context.get("trust_drift_delta", 0))
                st.metric("Benchmark Position", context.get("benchmark_position", 0))
                
                # Display recommendation
                st.info(f"**Recommendation:** {context.get('recommendation', 'No recommendation')}")
                
                # Display last prompt
                st.markdown(f"**Last Prompt:** {context.get('last_prompt', 'None')}")
                
                # Display category
                st.markdown(f"**Category:** {context.get('category', 'Unknown')}")
            
            with col2:
                # Display FOMA trigger
                foma_trigger = context.get("foma_trigger")
                if foma_trigger:
                    st.warning(f"**FOMA Trigger:** {foma_trigger}")
                else:
                    st.success("No FOMA Triggers")
                
                # Display peer set
                st.markdown("**Peer Set:**")
                for peer in context.get("peer_set", []):
                    st.markdown(f"- {peer}")
            
            # Create visualization
            st.markdown("### Trust Score Comparison")
            
            # Generate comparison data
            peers = context.get("peer_set", [])
            scores = [context.get("llm_score", 0)]
            for _ in peers:
                scores.append(random.uniform(max(0, context.get("llm_score", 0) - 20), 
                                           min(100, context.get("llm_score", 0) + 20)))
            
            # Create DataFrame
            df = pd.DataFrame({
                "Domain": [selected_domain] + peers,
                "LLM Score": scores
            })
            
            # Create bar chart
            fig = px.bar(
                df,
                x="Domain",
                y="LLM Score",
                title="Trust Score Comparison",
                color="Domain",
                color_discrete_sequence=px.colors.qualitative.Plotly
            )
            
            st.plotly_chart(fig, use_container_width=True)


def render_drift_events():
    """Render the drift events section."""
    st.markdown("## Category Drift Events")
    st.markdown("Track trust movement and benchmark reordering within categories")
    
    # Category input
    category_options = [
        "SaaS Productivity",
        "Enterprise CRM",
        "E-commerce Platforms",
        "Payment Processing",
        "Communication API",
        "Customer Support",
        "AI Platforms",
        "Developer Tools",
        "Technology"
    ]
    
    selected_category = st.selectbox("Select Category", category_options)
    
    if st.button("Get Drift Events"):
        with st.spinner(f"Getting drift events for {selected_category}..."):
            # Get drift events
            category_data = mcp_dispatcher.mcp_drift_events(selected_category)
            
            # Display metrics
            col1, col2 = st.columns(2)
            
            with col1:
                st.metric("Benchmark Volatility", f"{category_data.get('benchmark_volatility', 0):.2f}")
            
            with col2:
                st.metric("Prompt Sensitivity", f"{category_data.get('prompt_sensitivity', 0):.2f}")
            
            # Display drift events
            st.markdown("### Recent Drift Events")
            
            drift_events = category_data.get("drift_events", [])
            
            if drift_events:
                # Create DataFrame
                event_data = []
                
                for event in drift_events:
                    event_data.append({
                        "Timestamp": event.get("timestamp", ""),
                        "Primary Domain": event.get("domain_primary", ""),
                        "Secondary Domain": event.get("domain_secondary", ""),
                        "Event Type": event.get("event_type", ""),
                        "Magnitude": event.get("magnitude", 0),
                        "Description": event.get("description", "")
                    })
                
                df = pd.DataFrame(event_data)
                
                # Convert timestamp to datetime
                df["Timestamp"] = pd.to_datetime(df["Timestamp"])
                
                # Format timestamp
                df["Date"] = df["Timestamp"].dt.strftime("%Y-%m-%d")
                df["Time"] = df["Timestamp"].dt.strftime("%H:%M")
                
                # Display as table
                st.dataframe(df[["Date", "Time", "Primary Domain", "Secondary Domain", "Event Type", "Magnitude", "Description"]])
                
                # Create event timeline
                st.markdown("### Event Timeline")
                
                # Create time series data
                time_data = []
                
                for event in drift_events:
                    time_data.append({
                        "Timestamp": pd.to_datetime(event.get("timestamp", "")),
                        "Domain": event.get("domain_primary", ""),
                        "Event Type": event.get("event_type", ""),
                        "Magnitude": event.get("magnitude", 0)
                    })
                
                time_df = pd.DataFrame(time_data)
                
                # Sort by timestamp
                time_df = time_df.sort_values("Timestamp")
                
                # Create timeline
                fig = px.scatter(
                    time_df,
                    x="Timestamp",
                    y="Domain",
                    size="Magnitude",
                    color="Event Type",
                    hover_name="Domain",
                    title="Category Event Timeline"
                )
                
                fig.update_layout(
                    xaxis_title="Time",
                    yaxis_title="Domain"
                )
                
                st.plotly_chart(fig, use_container_width=True)
                
                # Create magnitude distribution
                st.markdown("### Event Magnitude Distribution")
                
                fig = px.histogram(
                    time_df,
                    x="Magnitude",
                    color="Event Type",
                    marginal="box",
                    title="Event Magnitude Distribution"
                )
                
                st.plotly_chart(fig, use_container_width=True)
            else:
                st.info("No drift events found for this category")


def render_prompt_suggestions():
    """Render the prompt suggestions section."""
    st.markdown("## Prompt Suggestions")
    st.markdown("Get optimized prompts for different trust signal tasks")
    
    # Task input
    task_options = [
        "domain_discovery",
        "trust_assessment",
        "benchmark_comparison",
        "insight_generation",
        "foma_analysis"
    ]
    
    selected_task = st.selectbox("Select Task", task_options)
    
    if st.button("Get Prompt Suggestions"):
        with st.spinner(f"Getting prompt suggestions for {selected_task}..."):
            # Get prompt suggestions
            prompt_data = mcp_dispatcher.mcp_prompt_suggestions(selected_task)
            
            # Display recommended prompt
            st.markdown("### Recommended Prompt")
            st.info(prompt_data.get("recommended", "No recommendation available"))
            st.markdown(f"**Reason:** {prompt_data.get('recommendation_reason', '')}")
            
            # Display all suggestions
            st.markdown("### All Prompt Suggestions")
            
            suggestions = prompt_data.get("suggestions", [])
            
            if suggestions:
                # Create DataFrame
                suggestion_data = []
                
                for suggestion in suggestions:
                    suggestion_data.append({
                        "Prompt": suggestion.get("prompt", ""),
                        "Effectiveness": suggestion.get("effectiveness", 0),
                        "Last Used": suggestion.get("last_used", ""),
                        "Signal Clarity": suggestion.get("signal_clarity", 0),
                        "Benchmark Clarity": suggestion.get("benchmark_clarity", 0),
                        "Insight Quality": suggestion.get("insight_quality", 0),
                        "FOMA Trigger Rate": suggestion.get("foma_trigger_rate", 0),
                        "Domains Discovered": suggestion.get("domains_discovered", 0)
                    })
                
                df = pd.DataFrame(suggestion_data)
                
                # Display as table
                st.dataframe(df)
                
                # Create effectiveness comparison
                st.markdown("### Prompt Effectiveness Comparison")
                
                fig = px.bar(
                    df,
                    y="Prompt",
                    x="Effectiveness",
                    title="Prompt Effectiveness",
                    orientation="h",
                    color="Effectiveness",
                    color_continuous_scale="Viridis"
                )
                
                st.plotly_chart(fig, use_container_width=True)
                
                # Create radar chart for prompt performance
                st.markdown("### Prompt Performance Metrics")
                
                # Prepare radar chart data
                metrics = ["Effectiveness"]
                
                if "Signal Clarity" in df.columns and not df["Signal Clarity"].isna().all():
                    metrics.append("Signal Clarity")
                
                if "Benchmark Clarity" in df.columns and not df["Benchmark Clarity"].isna().all():
                    metrics.append("Benchmark Clarity")
                
                if "Insight Quality" in df.columns and not df["Insight Quality"].isna().all():
                    metrics.append("Insight Quality")
                
                if "FOMA Trigger Rate" in df.columns and not df["FOMA Trigger Rate"].isna().all():
                    metrics.append("FOMA Trigger Rate")
                
                # Only create radar chart if we have multiple metrics
                if len(metrics) > 1:
                    fig = go.Figure()
                    
                    for i, row in df.iterrows():
                        values = [row[metric] for metric in metrics]
                        values.append(values[0])  # Close the loop
                        
                        fig.add_trace(go.Scatterpolar(
                            r=values,
                            theta=metrics + [metrics[0]],  # Close the loop
                            fill='toself',
                            name=row["Prompt"][:30] + "..."  # Truncate for display
                        ))
                    
                    fig.update_layout(
                        polar=dict(
                            radialaxis=dict(
                                visible=True,
                                range=[0, 1]
                            )
                        ),
                        title="Prompt Performance Metrics"
                    )
                    
                    st.plotly_chart(fig, use_container_width=True)
            else:
                st.info("No prompt suggestions found for this task")


def render_foma_threats():
    """Render the FOMA threats section."""
    st.markdown("## FOMA Threats Analysis")
    st.markdown("Identify trust loss, peer overtaking, and visibility gaps")
    
    # Domain input
    domain_options = [
        "asana.com",
        "monday.com",
        "notion.so",
        "salesforce.com",
        "hubspot.com",
        "shopify.com",
        "bigcommerce.com",
        "stripe.com",
        "twilio.com",
        "zendesk.com"
    ]
    
    selected_domain = st.selectbox("Select Domain for FOMA Analysis", domain_options)
    
    if st.button("Analyze FOMA Threats"):
        with st.spinner(f"Analyzing FOMA threats for {selected_domain}..."):
            # Get FOMA threats
            foma_data = mcp_dispatcher.mcp_foma_threats(selected_domain)
            
            # Display metrics
            col1, col2, col3 = st.columns(3)
            
            with col1:
                st.metric("Threat Count", foma_data.get("threatcountscore", 0))
            
            with col2:
                st.metric("Max Severity", f"{foma_data.get('max_severity', 0):.2f}")
            
            with col3:
                st.markdown(f"**Category:** {foma_data.get('category', 'Unknown')}")
            
            # Display threats
            st.markdown("### Identified Threats")
            
            threats = foma_data.get("threats", [])
            
            if threats:
                # Create cards for each threat
                for i, threat in enumerate(threats):
                    with st.expander(f"{threat.get('threat_type', 'Threat').title()} - Severity: {threat.get('severity', 0):.2f}", expanded=i == 0):
                        st.markdown(f"**Description:** {threat.get('description', 'No description')}")
                        st.markdown(f"**Triggered:** {pd.to_datetime(threat.get('trigger_date', '')).strftime('%Y-%m-%d')}")
                        st.markdown(f"**Recommendation:** {threat.get('recommendation', 'No recommendation')}")
                        
                        # Display affected prompts if available
                        affected_prompts = threat.get("affected_prompts")
                        if affected_prompts:
                            st.markdown("**Affected Prompts:**")
                            for prompt in affected_prompts:
                                st.markdown(f"- {prompt}")
                        
                        # Display comparison metrics if available
                        comparison_metrics = threat.get("comparison_metrics")
                        if comparison_metrics:
                            st.markdown("**Comparison Metrics:**")
                            
                            metrics_data = []
                            for metric, value in comparison_metrics.items():
                                metrics_data.append({
                                    "Metric": metric.replace("_", " ").title(),
                                    "Value": value
                                })
                            
                            metrics_df = pd.DataFrame(metrics_data)
                            
                            # Create bar chart
                            fig = px.bar(
                                metrics_df,
                                y="Metric",
                                x="Value",
                                orientation="h",
                                range_x=[0, 1],
                                title="Comparison Metrics",
                                color="Value",
                                color_continuous_scale="RdYlGn"
                            )
                            
                            st.plotly_chart(fig, use_container_width=True)
                        
                        # Display gap topics if available
                        gap_topics = threat.get("gap_topics")
                        if gap_topics:
                            st.markdown("**Gap Topics:**")
                            for topic in gap_topics:
                                st.markdown(f"- {topic}")
                
                # Create severity comparison
                st.markdown("### Threat Severity Comparison")
                
                # Create DataFrame
                severity_data = []
                
                for threat in threats:
                    severity_data.append({
                        "Threat Type": threat.get("threat_type", "").replace("_", " ").title(),
                        "Severity": threat.get("severity", 0),
                        "Description": threat.get("description", "")
                    })
                
                severity_df = pd.DataFrame(severity_data)
                
                # Create bar chart
                fig = px.bar(
                    severity_df,
                    y="Threat Type",
                    x="Severity",
                    orientation="h",
                    range_x=[0, 1],
                    title="Threat Severity",
                    color="Severity",
                    color_continuous_scale="Reds",
                    hover_data=["Description"]
                )
                
                st.plotly_chart(fig, use_container_width=True)
            else:
                st.success("No FOMA threats found for this domain")


def render_rankllm_leaderboard():
    """Render the RankLLM.io leaderboard section."""
    st.markdown("## RankLLM.io Leaderboard")
    st.markdown("Trust signal leaderboard for domains across categories")
    
    if st.button("Get RankLLM Leaderboard"):
        with st.spinner("Loading RankLLM.io leaderboard..."):
            # Get RankLLM data
            rankllm_data = mcp_dispatcher.mcp_rankllm_input()
            
            # Display update timestamp
            st.markdown(f"**Last Updated:** {pd.to_datetime(rankllm_data.get('update_timestamp', '')).strftime('%Y-%m-%d %H:%M:%S')}")
            
            # Display metrics
            col1, col2 = st.columns(2)
            
            with col1:
                st.metric("Total Domains", rankllm_data.get("total_domains", 0))
            
            with col2:
                st.metric("Categories", rankllm_data.get("categories_represented", 0))
            
            # Display leaderboard
            st.markdown("### Domain Rankings")
            
            entries = rankllm_data.get("entries", [])
            
            if entries:
                # Create DataFrame
                leaderboard_data = []
                
                for entry in entries:
                    leaderboard_data.append({
                        "Rank": entry.get("rank", 0),
                        "Domain": entry.get("domain", ""),
                        "LLM Score": entry.get("llm_score", 0),
                        "Trust Velocity": entry.get("trust_velocity", 0),
                        "FOMA Status": entry.get("foma_status", ""),
                        "Cited By": ", ".join(entry.get("cited_by", [])),
                        "Missed By": ", ".join(entry.get("missed_by", [])),
                        "Category": entry.get("category", "")
                    })
                
                df = pd.DataFrame(leaderboard_data)
                
                # Add styling
                def highlight_foma(val):
                    if val == "Rising":
                        return "background-color: #c5f5c5"
                    elif val == "Falling":
                        return "background-color: #f5c5c5"
                    elif val == "Outcited":
                        return "background-color: #f5f5c5"
                    elif val == "Undervalued":
                        return "background-color: #c5c5f5"
                    elif val == "Gap":
                        return "background-color: #f5c5f5"
                    else:
                        return ""
                
                # Display as table with styling
                st.dataframe(df.style.applymap(highlight_foma, subset=["FOMA Status"]))
                
                # Filter by category
                st.markdown("### Category Analysis")
                
                categories = ["All"] + sorted(df["Category"].unique().tolist())
                selected_cat = st.selectbox("Filter by Category", categories)
                
                if selected_cat != "All":
                    filtered_df = df[df["Category"] == selected_cat]
                else:
                    filtered_df = df
                
                # Create scatter plot
                fig = px.scatter(
                    filtered_df,
                    x="LLM Score",
                    y="Trust Velocity",
                    size="Rank",
                    size_max=15,
                    color="Category" if selected_cat == "All" else "Domain",
                    hover_name="Domain",
                    text="Domain",
                    title=f"LLM Score vs. Trust Velocity - {selected_cat}"
                )
                
                fig.update_traces(
                    textposition="top center",
                    textfont=dict(size=10)
                )
                
                fig.update_layout(
                    xaxis_title="LLM Score",
                    yaxis_title="Trust Velocity",
                    height=600
                )
                
                st.plotly_chart(fig, use_container_width=True)
                
                # Create FOMA status distribution
                st.markdown("### FOMA Status Distribution")
                
                foma_counts = filtered_df["FOMA Status"].value_counts().reset_index()
                foma_counts.columns = ["FOMA Status", "Count"]
                
                fig = px.pie(
                    foma_counts,
                    values="Count",
                    names="FOMA Status",
                    title="FOMA Status Distribution"
                )
                
                st.plotly_chart(fig, use_container_width=True)
                
                # Create citation analysis
                st.markdown("### Model Citation Analysis")
                
                # Prepare citation data
                citation_data = []
                
                for entry in entries:
                    domain = entry.get("domain", "")
                    category = entry.get("category", "")
                    
                    for model in entry.get("cited_by", []):
                        citation_data.append({
                            "Domain": domain,
                            "Model": model,
                            "Status": "Cited",
                            "Category": category
                        })
                    
                    for model in entry.get("missed_by", []):
                        citation_data.append({
                            "Domain": domain,
                            "Model": model,
                            "Status": "Missed",
                            "Category": category
                        })
                
                citation_df = pd.DataFrame(citation_data)
                
                if selected_cat != "All":
                    citation_df = citation_df[citation_df["Category"] == selected_cat]
                
                # Create citation heatmap
                if not citation_df.empty:
                    citation_pivot = pd.crosstab(citation_df["Domain"], citation_df["Model"], 
                                                values=citation_df["Status"].apply(lambda x: 1 if x == "Cited" else 0),
                                                aggfunc="sum")
                    
                    fig = px.imshow(
                        citation_pivot,
                        labels=dict(x="Model", y="Domain", color="Cited"),
                        x=citation_pivot.columns,
                        y=citation_pivot.index,
                        color_continuous_scale="Greens",
                        title="Model Citation Matrix"
                    )
                    
                    fig.update_layout(height=600)
                    
                    st.plotly_chart(fig, use_container_width=True)
            else:
                st.info("No leaderboard entries found")