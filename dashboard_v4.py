"""
LLMPageRank V4 Insight-Driven Dashboard

This module implements the enhanced dashboard for the V4 system with
focus on insight detection, trust movement decoding, and FOMA visualization.
"""

import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px
import plotly.graph_objects as go
import json
import os
import time
import re
from datetime import datetime, timedelta

# Import from project modules
from config import DATA_DIR, CATEGORIES, LLM_MODELS, SYSTEM_VERSION, VERSION_INFO
import database as db
from foma_insight_engine import analyze_domain, get_latest_insights, get_domain_insights, get_insight_stats

# Constants
INSIGHTS_DIR = f"{DATA_DIR}/insights"
INSIGHT_LOGS_FILE = f"{DATA_DIR}/insight_log.json"
SCAN_FAILURES_DIR = f"{DATA_DIR}/scan_failures"

def format_timestamp(timestamp):
    """Format a timestamp for display."""
    if not timestamp:
        return "N/A"
    return datetime.fromtimestamp(timestamp).strftime("%Y-%m-%d %H:%M")

def render_v4_dashboard():
    """Render the V4 insight-driven dashboard."""
    st.title("LLMRank.io - Insight-Driven FOMA Engine")
    
    # Display version info
    st.markdown(f"**System Version:** {SYSTEM_VERSION} | **Last Updated:** {format_timestamp(time.time())}")
    
    # Add dashboard style
    st.markdown("""
    <style>
        .insight-container {
            background-color: #f8f9fa;
            border-radius: 5px;
            padding: 15px;
            margin-bottom: 15px;
            border-left: 4px solid #007bff;
        }
        .insight-title {
            font-size: 16px;
            font-weight: bold;
            margin-bottom: 5px;
        }
        .insight-summary {
            font-size: 14px;
            color: #555;
            margin-bottom: 10px;
        }
        .insight-meta {
            font-size: 12px;
            color: #777;
        }
        .foma-tag {
            display: inline-block;
            padding: 2px 8px;
            border-radius: 12px;
            font-size: 12px;
            margin-right: 5px;
            margin-bottom: 5px;
        }
        .foma-high {
            background-color: #f8d7da;
            color: #721c24;
        }
        .foma-medium {
            background-color: #fff3cd;
            color: #856404;
        }
        .foma-low {
            background-color: #d1e7dd;
            color: #0f5132;
        }
        .emotion-alarm {
            border-left: 4px solid #dc3545;
        }
        .emotion-worry {
            border-left: 4px solid #fd7e14;
        }
        .emotion-caution {
            border-left: 4px solid #ffc107;
        }
        .emotion-guidance {
            border-left: 4px solid #0dcaf0;
        }
        .emotion-relief {
            border-left: 4px solid #198754;
        }
        .emotion-celebration {
            border-left: 4px solid #20c997;
        }
        .quality-indicator {
            display: inline-block;
            width: 12px;
            height: 12px;
            border-radius: 50%;
            margin-right: 5px;
        }
        .quality-high {
            background-color: #198754;
        }
        .quality-medium {
            background-color: #ffc107;
        }
        .quality-low {
            background-color: #dc3545;
        }
        .quality-none {
            background-color: #6c757d;
        }
        .insight-count-container {
            background-color: #f8f9fa;
            border-radius: 5px;
            padding: 20px;
            text-align: center;
            margin-bottom: 15px;
        }
        .insight-count {
            font-size: 36px;
            font-weight: bold;
            color: #0d6efd;
        }
        .insight-count-label {
            font-size: 14px;
            color: #555;
        }
        .vector-indicator {
            display: inline-block;
            padding: 2px 8px;
            border-radius: 12px;
            font-size: 12px;
            margin-right: 5px;
        }
        .vector-peer {
            background-color: #cfe2ff;
            color: #084298;
        }
        .vector-self {
            background-color: #d1e7dd;
            color: #0f5132;
        }
        .vector-benchmark {
            background-color: #e2e3e5;
            color: #41464b;
        }
    </style>
    """, unsafe_allow_html=True)
    
    # Create tabs
    tabs = st.tabs([
        "Trust Insights",
        "Insight Explorer",
        "FOMA Analysis",
        "Scan Quality",
        "API Intelligence"
    ])
    
    with tabs[0]:
        render_trust_insights()
        
    with tabs[1]:
        render_insight_explorer()
        
    with tabs[2]:
        render_foma_analysis()
        
    with tabs[3]:
        render_scan_quality()
        
    with tabs[4]:
        render_api_intelligence()

def render_trust_insights():
    """Render the trust insights tab."""
    st.header("Trust Intelligence Dashboard")
    
    # Get latest insights
    latest_insights = get_latest_insights(limit=20)
    
    # Get insight stats
    insight_stats = get_insight_stats()
    
    # Main insights overview
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        st.markdown(
            f"<div class='insight-count-container'>"
            f"<div class='insight-count'>{insight_stats.get('total_insights', 0)}</div>"
            f"<div class='insight-count-label'>Total Insights</div>"
            f"</div>",
            unsafe_allow_html=True
        )
    
    with col2:
        high_quality = insight_stats.get('quality_counts', {}).get('high', 0)
        st.markdown(
            f"<div class='insight-count-container'>"
            f"<div class='insight-count'>{high_quality}</div>"
            f"<div class='insight-count-label'>High-Quality Insights</div>"
            f"</div>",
            unsafe_allow_html=True
        )
    
    with col3:
        domain_count = insight_stats.get('total_domains', 0)
        st.markdown(
            f"<div class='insight-count-container'>"
            f"<div class='insight-count'>{domain_count}</div>"
            f"<div class='insight-count-label'>Domains Analyzed</div>"
            f"</div>",
            unsafe_allow_html=True
        )
    
    with col4:
        failure_count = insight_stats.get('total_failures', 0)
        st.markdown(
            f"<div class='insight-count-container'>"
            f"<div class='insight-count'>{failure_count}</div>"
            f"<div class='insight-count-label'>Scan Failures</div>"
            f"</div>",
            unsafe_allow_html=True
        )
    
    # FOMA Triggers distribution
    st.subheader("FOMA Triggers Distribution")
    
    foma_counts = insight_stats.get('foma_counts', {})
    if foma_counts:
        foma_df = pd.DataFrame({
            'trigger': list(foma_counts.keys()),
            'count': list(foma_counts.values())
        })
        
        foma_df = foma_df.sort_values('count', ascending=False)
        
        fig = px.bar(
            foma_df,
            x='count',
            y='trigger',
            orientation='h',
            labels={'count': 'Frequency', 'trigger': 'FOMA Trigger'},
            title='Distribution of FOMA Triggers'
        )
        
        st.plotly_chart(fig, use_container_width=True)
    else:
        st.info("No FOMA triggers data available yet.")
    
    # Insight vector distribution
    st.subheader("Insight Vector Distribution")
    
    vector_counts = insight_stats.get('vector_counts', {})
    if vector_counts:
        vector_df = pd.DataFrame({
            'vector': list(vector_counts.keys()),
            'count': list(vector_counts.values())
        })
        
        fig = px.pie(
            vector_df,
            values='count',
            names='vector',
            title='Insight Vector Distribution',
            color='vector',
            color_discrete_map={
                'peer': '#0d6efd',
                'self': '#20c997',
                'benchmark': '#6c757d'
            }
        )
        
        st.plotly_chart(fig, use_container_width=True)
    else:
        st.info("No insight vector data available yet.")
    
    # Latest insights visualization
    st.subheader("Latest Domain Insights")
    
    if latest_insights:
        # Display top insights
        for idx, insight_data in enumerate(latest_insights):
            if idx >= 5:  # Limit to 5 insights on the main page
                break
                
            domain = insight_data.get('domain', 'Unknown')
            llm_score = insight_data.get('llm_score', 0)
            delta = insight_data.get('insight_delta', '0.0')
            quality = insight_data.get('insight_quality', 'none')
            
            # Format header with quality indicator
            quality_color = 'quality-none'
            if quality == 'high':
                quality_color = 'quality-high'
            elif quality == 'medium':
                quality_color = 'quality-medium'
            elif quality == 'low':
                quality_color = 'quality-low'
            
            st.markdown(
                f"<h3><span class='quality-indicator {quality_color}'></span> {domain} "
                f"<small style='color: #6c757d;'>LLMRank: {llm_score:.1f} ({delta})</small></h3>",
                unsafe_allow_html=True
            )
            
            # Show FOMA triggers
            foma_triggers = insight_data.get('foma_triggers', [])
            if foma_triggers:
                triggers_html = ""
                for trigger in foma_triggers:
                    severity = "medium"  # Default
                    
                    # Try to extract severity from insights
                    for i in insight_data.get('insights', []):
                        if i.get('foma_tag', {}).get('type') == trigger:
                            severity = i.get('foma_tag', {}).get('severity', 'medium')
                            break
                    
                    triggers_html += f"<span class='foma-tag foma-{severity}'>{trigger}</span>"
                
                st.markdown(f"<div>{triggers_html}</div>", unsafe_allow_html=True)
            
            # Display individual insights
            for insight in insight_data.get('insights', []):
                # Get insight data
                insight_text = insight.get('insight', '')
                summary = insight.get('summary', '')
                vector = insight.get('vector', '')
                emotion = insight.get('foma_tag', {}).get('emotion', '')
                clarity = insight.get('clarity_score', 0)
                
                # Format vector indicator
                vector_html = ""
                if vector:
                    vector_html = f"<span class='vector-indicator vector-{vector}'>{vector.title()}</span>"
                
                # Render insight
                st.markdown(
                    f"<div class='insight-container emotion-{emotion}'>"
                    f"<div class='insight-title'>{insight_text}</div>"
                    f"<div class='insight-summary'>{summary}</div>"
                    f"<div class='insight-meta'>"
                    f"{vector_html} Clarity: {clarity:.1f}"
                    f"</div>"
                    f"</div>",
                    unsafe_allow_html=True
                )
            
            st.markdown("---")
    else:
        st.info("No insights available yet. Run domain analysis to generate insights.")

def render_insight_explorer():
    """Render the insight explorer tab."""
    st.header("Insight Explorer")
    
    # Get all tested domains for selection
    all_domains = db.get_all_tested_domains()
    
    if not all_domains:
        st.warning("No domains available for analysis. Add domains to the system first.")
        return
    
    # Create domain selector
    selected_domain = st.selectbox(
        "Select Domain to Analyze",
        all_domains
    )
    
    if not selected_domain:
        st.info("Select a domain to view insights.")
        return
    
    # Get domain's latest result
    latest_result = db.get_latest_domain_result(selected_domain)
    
    if not latest_result:
        st.warning(f"No data available for {selected_domain}.")
        return
    
    # Get domain insights
    domain_insights = get_domain_insights(selected_domain)
    
    # Display domain info
    st.subheader(f"Domain: {selected_domain}")
    
    col1, col2, col3 = st.columns(3)
    
    with col1:
        st.metric(
            label="LLMRank Score",
            value=f"{latest_result.get('visibility_score', 0):.1f}"
        )
    
    with col2:
        st.metric(
            label="Structure Score",
            value=f"{latest_result.get('structure_score', 0):.1f}"
        )
    
    with col3:
        st.metric(
            label="Category",
            value=latest_result.get('category', 'Unknown')
        )
    
    # Check if we have existing insights
    if domain_insights:
        latest_insight = domain_insights[0]
        
        # Action buttons
        col1, col2 = st.columns(2)
        
        with col1:
            if st.button("Re-analyze Domain"):
                with st.spinner("Analyzing domain..."):
                    latest_insight = analyze_domain(selected_domain)
                st.success("Domain analysis complete!")
        
        # Display insight quality
        quality = latest_insight.get('insight_quality', 'none')
        quality_color = 'quality-none'
        
        if quality == 'high':
            quality_color = 'quality-high'
        elif quality == 'medium':
            quality_color = 'quality-medium'
        elif quality == 'low':
            quality_color = 'quality-low'
        
        st.markdown(
            f"<h4>Insight Quality: <span class='quality-indicator {quality_color}'></span> {quality.title()}</h4>",
            unsafe_allow_html=True
        )
        
        # Display FOMA triggers
        st.subheader("FOMA Triggers")
        
        foma_triggers = latest_insight.get('foma_triggers', [])
        if foma_triggers:
            triggers_html = ""
            for trigger in foma_triggers:
                severity = "medium"  # Default
                
                # Try to extract severity from insights
                for i in latest_insight.get('insights', []):
                    if i.get('foma_tag', {}).get('type') == trigger:
                        severity = i.get('foma_tag', {}).get('severity', 'medium')
                        break
                
                triggers_html += f"<span class='foma-tag foma-{severity}'>{trigger}</span>"
            
            st.markdown(f"<div>{triggers_html}</div>", unsafe_allow_html=True)
        else:
            st.info("No FOMA triggers detected for this domain.")
        
        # Display individual insights
        st.subheader("Detailed Insights")
        
        insights = latest_insight.get('insights', [])
        if insights:
            for insight in insights:
                # Get insight data
                insight_text = insight.get('insight', '')
                summary = insight.get('summary', '')
                vector = insight.get('vector', '')
                emotion = insight.get('foma_tag', {}).get('emotion', '')
                severity = insight.get('foma_tag', {}).get('severity', 'medium')
                clarity = insight.get('clarity_score', 0)
                delta = insight.get('delta', 0)
                actionable = insight.get('actionable', False)
                
                # Format vector indicator
                vector_html = ""
                if vector:
                    vector_html = f"<span class='vector-indicator vector-{vector}'>{vector.title()}</span>"
                
                # Format severity tag
                severity_html = f"<span class='foma-tag foma-{severity}'>{severity.title()}</span>"
                
                # Format actionable indicator
                actionable_html = ""
                if actionable:
                    actionable_html = "<span class='foma-tag foma-high'>Actionable</span>"
                
                # Render insight
                st.markdown(
                    f"<div class='insight-container emotion-{emotion}'>"
                    f"<div class='insight-title'>{insight_text}</div>"
                    f"<div class='insight-summary'>{summary}</div>"
                    f"<div class='insight-meta'>"
                    f"{vector_html} {severity_html} {actionable_html} | "
                    f"Delta: {delta:+.1f} | Clarity: {clarity:.1f}"
                    f"</div>"
                    f"</div>",
                    unsafe_allow_html=True
                )
        else:
            st.info("No detailed insights available for this domain.")
        
        # Show historical data if available
        domain_history = db.get_domain_history(selected_domain)
        
        if len(domain_history) > 1:
            st.subheader("Trust Signal History")
            
            # Prepare data for chart
            history_data = []
            for result in domain_history:
                history_data.append({
                    "timestamp": result.get("timestamp", 0),
                    "formatted_time": format_timestamp(result.get("timestamp", 0)),
                    "visibility_score": result.get("visibility_score", 0),
                    "structure_score": result.get("structure_score", 0)
                })
            
            # Sort by timestamp
            history_data.sort(key=lambda x: x["timestamp"])
            
            # Create DataFrame
            df = pd.DataFrame(history_data)
            
            # Create chart
            fig = go.Figure()
            
            fig.add_trace(go.Scatter(
                x=df["formatted_time"],
                y=df["visibility_score"],
                mode='lines+markers',
                name='LLMRank',
                line=dict(color='#0d6efd', width=3)
            ))
            
            fig.add_trace(go.Scatter(
                x=df["formatted_time"],
                y=df["structure_score"],
                mode='lines+markers',
                name='Structure',
                line=dict(color='#20c997', width=3, dash='dash')
            ))
            
            fig.update_layout(
                title="Trust Signal History",
                xaxis_title="Date",
                yaxis_title="Score",
                legend=dict(
                    orientation="h",
                    yanchor="bottom",
                    y=1.02,
                    xanchor="right",
                    x=1
                )
            )
            
            st.plotly_chart(fig, use_container_width=True)
    else:
        # No insights yet, offer to analyze
        st.info("No insights available for this domain yet.")
        
        if st.button("Analyze Domain"):
            with st.spinner("Analyzing domain..."):
                analyze_domain(selected_domain)
            st.success("Domain analysis complete!")
            st.rerun()

def render_foma_analysis():
    """Render the FOMA analysis tab."""
    st.header("FOMA Analysis")
    
    # Get insight stats
    insight_stats = get_insight_stats()
    
    # Display FOMA overview
    st.subheader("FOMA Overview")
    
    col1, col2 = st.columns(2)
    
    with col1:
        # Count FOMA triggers
        foma_counts = insight_stats.get('foma_counts', {})
        total_foma = sum(foma_counts.values()) if foma_counts else 0
        
        st.metric(
            label="Total FOMA Triggers",
            value=total_foma
        )
        
        # Display FOMA by platform
        st.markdown("### FOMA by Platform")
        
        platform_html = f"""
        <div style="padding: 15px; background-color: #f8f9fa; border-radius: 5px; margin-bottom: 15px;">
            <h4>LLMRank.io</h4>
            <p>API, scorecard, core product</p>
        </div>
        <div style="padding: 15px; background-color: #f8f9fa; border-radius: 5px; margin-bottom: 15px;">
            <h4>LLMPageRank.com</h4>
            <p>Public index + trust ranking system</p>
        </div>
        <div style="padding: 15px; background-color: #f8f9fa; border-radius: 5px; margin-bottom: 15px;">
            <h4>LLM-Rated™</h4>
            <p>Status certification and brand messaging</p>
        </div>
        <div style="padding: 15px; background-color: #f8f9fa; border-radius: 5px; margin-bottom: 15px;">
            <h4>Outcited.com</h4>
            <p>"You've been outsided" FOMA driver</p>
        </div>
        """
        
        st.markdown(platform_html, unsafe_allow_html=True)
    
    with col2:
        # FOMA severity distribution
        severity_counts = {
            "high": 0,
            "medium": 0,
            "low": 0
        }
        
        # Get all insights to count severities
        latest_insights = get_latest_insights(limit=100)
        
        for insight_data in latest_insights:
            for insight in insight_data.get('insights', []):
                severity = insight.get('foma_tag', {}).get('severity', 'medium')
                severity_counts[severity] = severity_counts.get(severity, 0) + 1
        
        if sum(severity_counts.values()) > 0:
            severity_df = pd.DataFrame({
                'severity': list(severity_counts.keys()),
                'count': list(severity_counts.values())
            })
            
            # Add colors
            severity_df['color'] = severity_df['severity'].apply(lambda x: {
                'high': '#dc3545',
                'medium': '#ffc107',
                'low': '#198754'
            }.get(x, '#6c757d'))
            
            fig = px.pie(
                severity_df,
                values='count',
                names='severity',
                title='FOMA Severity Distribution',
                color='severity',
                color_discrete_map={
                    'high': '#dc3545',
                    'medium': '#ffc107',
                    'low': '#198754'
                }
            )
            
            st.plotly_chart(fig, use_container_width=True)
        else:
            st.info("No severity data available yet.")
            
        # FOMA emotion distribution
        emotion_counts = {}
        
        for insight_data in latest_insights:
            for insight in insight_data.get('insights', []):
                emotion = insight.get('foma_tag', {}).get('emotion', '')
                if emotion:
                    emotion_counts[emotion] = emotion_counts.get(emotion, 0) + 1
        
        if emotion_counts:
            emotion_df = pd.DataFrame({
                'emotion': list(emotion_counts.keys()),
                'count': list(emotion_counts.values())
            })
            
            fig = px.bar(
                emotion_df,
                x='emotion',
                y='count',
                title='FOMA Emotion Distribution',
                color='emotion'
            )
            
            st.plotly_chart(fig, use_container_width=True)
        else:
            st.info("No emotion data available yet.")
    
    # FOMA by category
    st.subheader("FOMA by Category")
    
    # Get all insights to count by category
    latest_insights = get_latest_insights(limit=100)
    
    category_foma = {}
    
    for insight_data in latest_insights:
        category = insight_data.get('category', '')
        if not category:
            continue
            
        if category not in category_foma:
            category_foma[category] = {
                'total': 0,
                'triggers': {}
            }
        
        # Count triggers
        for trigger in insight_data.get('foma_triggers', []):
            category_foma[category]['triggers'][trigger] = category_foma[category]['triggers'].get(trigger, 0) + 1
            category_foma[category]['total'] += 1
    
    # Display category FOMA
    if category_foma:
        # Prepare data for chart
        categories = []
        totals = []
        
        for category, data in category_foma.items():
            categories.append(category)
            totals.append(data['total'])
        
        # Create DataFrame
        df = pd.DataFrame({
            'category': categories,
            'total': totals
        })
        
        # Sort by total
        df = df.sort_values('total', ascending=False)
        
        # Create chart
        fig = px.bar(
            df,
            x='category',
            y='total',
            title='FOMA Triggers by Category',
            color='category'
        )
        
        st.plotly_chart(fig, use_container_width=True)
        
        # Display detailed breakdown
        for category, data in category_foma.items():
            if data['total'] > 0:
                with st.expander(f"{category} ({data['total']} triggers)"):
                    # Show triggers
                    trigger_data = []
                    
                    for trigger, count in data['triggers'].items():
                        trigger_data.append({
                            'trigger': trigger,
                            'count': count
                        })
                    
                    # Sort by count
                    trigger_data.sort(key=lambda x: x['count'], reverse=True)
                    
                    # Create DataFrame
                    trigger_df = pd.DataFrame(trigger_data)
                    
                    # Create chart
                    fig = px.bar(
                        trigger_df,
                        x='trigger',
                        y='count',
                        title=f'FOMA Triggers for {category}',
                        color='trigger'
                    )
                    
                    st.plotly_chart(fig, use_container_width=True)
    else:
        st.info("No category FOMA data available yet.")
    
    # FOMA example insights
    st.subheader("Example FOMA Insights")
    
    # Get insights with high severity
    high_severity_insights = []
    
    for insight_data in latest_insights:
        for insight in insight_data.get('insights', []):
            severity = insight.get('foma_tag', {}).get('severity', '')
            if severity == 'high':
                high_severity_insights.append({
                    'domain': insight_data.get('domain', ''),
                    'insight': insight
                })
    
    if high_severity_insights:
        # Display limited number of examples
        for idx, item in enumerate(high_severity_insights):
            if idx >= 5:  # Limit to 5 examples
                break
                
            domain = item['domain']
            insight = item['insight']
            
            # Get insight data
            insight_text = insight.get('insight', '')
            summary = insight.get('summary', '')
            vector = insight.get('vector', '')
            emotion = insight.get('foma_tag', {}).get('emotion', '')
            clarity = insight.get('clarity_score', 0)
            
            # Format vector indicator
            vector_html = ""
            if vector:
                vector_html = f"<span class='vector-indicator vector-{vector}'>{vector.title()}</span>"
            
            # Render insight
            st.markdown(
                f"<h4>{domain}</h4>"
                f"<div class='insight-container emotion-{emotion}'>"
                f"<div class='insight-title'>{insight_text}</div>"
                f"<div class='insight-summary'>{summary}</div>"
                f"<div class='insight-meta'>"
                f"{vector_html} Clarity: {clarity:.1f}"
                f"</div>"
                f"</div>",
                unsafe_allow_html=True
            )
    else:
        st.info("No high severity FOMA insights available yet.")

def render_scan_quality():
    """Render the scan quality tab."""
    st.header("Scan Quality")
    
    # Get insight stats
    insight_stats = get_insight_stats()
    
    # Display scan failure overview
    st.subheader("Scan Failure Overview")
    
    col1, col2 = st.columns(2)
    
    with col1:
        total_failures = insight_stats.get('total_failures', 0)
        st.metric(
            label="Total Scan Failures",
            value=total_failures
        )
    
    with col2:
        failure_types = insight_stats.get('failure_types', {})
        if failure_types:
            # Create DataFrame
            failure_df = pd.DataFrame({
                'type': list(failure_types.keys()),
                'count': list(failure_types.values())
            })
            
            # Create chart
            fig = px.pie(
                failure_df,
                values='count',
                names='type',
                title='Scan Failure Types',
                color='type',
                color_discrete_map={
                    'data_gap': '#dc3545',
                    'prompt_problem': '#ffc107',
                    'crawl_failure': '#0dcaf0',
                    'model_fatigue': '#6c757d',
                    'insight_miss': '#fd7e14'
                }
            )
            
            st.plotly_chart(fig, use_container_width=True)
        else:
            st.info("No scan failure data available yet.")
    
    # Insight quality distribution
    st.subheader("Insight Quality Distribution")
    
    quality_counts = insight_stats.get('quality_counts', {})
    if quality_counts:
        # Create DataFrame
        quality_df = pd.DataFrame({
            'quality': list(quality_counts.keys()),
            'count': list(quality_counts.values())
        })
        
        # Create chart
        fig = px.bar(
            quality_df,
            x='quality',
            y='count',
            title='Insight Quality Distribution',
            color='quality',
            color_discrete_map={
                'high': '#198754',
                'medium': '#ffc107',
                'low': '#dc3545',
                'none': '#6c757d'
            }
        )
        
        st.plotly_chart(fig, use_container_width=True)
        
        # Calculate insight quality ratio
        total_insights = sum(quality_counts.values())
        high_quality = quality_counts.get('high', 0)
        medium_quality = quality_counts.get('medium', 0)
        
        quality_ratio = (high_quality + medium_quality) / total_insights if total_insights > 0 else 0
        
        st.metric(
            label="Quality Insight Ratio",
            value=f"{quality_ratio:.1%}"
        )
    else:
        st.info("No insight quality data available yet.")
    
    # Vector insight distribution
    st.subheader("Vector Insight Distribution")
    
    vector_counts = insight_stats.get('vector_counts', {})
    if vector_counts:
        # Create DataFrame
        vector_df = pd.DataFrame({
            'vector': list(vector_counts.keys()),
            'count': list(vector_counts.values())
        })
        
        # Sort vectors
        vector_df['vector'] = pd.Categorical(
            vector_df['vector'],
            categories=['peer', 'self', 'benchmark'],
            ordered=True
        )
        vector_df = vector_df.sort_values('vector')
        
        # Create chart
        fig = px.bar(
            vector_df,
            x='vector',
            y='count',
            title='Vector Insight Distribution',
            color='vector',
            color_discrete_map={
                'peer': '#0d6efd',
                'self': '#20c997',
                'benchmark': '#6c757d'
            }
        )
        
        st.plotly_chart(fig, use_container_width=True)
        
        # Calculate vector distribution
        total_vectors = sum(vector_counts.values())
        peer_ratio = vector_counts.get('peer', 0) / total_vectors if total_vectors > 0 else 0
        self_ratio = vector_counts.get('self', 0) / total_vectors if total_vectors > 0 else 0
        benchmark_ratio = vector_counts.get('benchmark', 0) / total_vectors if total_vectors > 0 else 0
        
        col1, col2, col3 = st.columns(3)
        
        with col1:
            st.metric(
                label="Peer Insight Ratio",
                value=f"{peer_ratio:.1%}"
            )
        
        with col2:
            st.metric(
                label="Self Insight Ratio",
                value=f"{self_ratio:.1%}"
            )
        
        with col3:
            st.metric(
                label="Benchmark Insight Ratio",
                value=f"{benchmark_ratio:.1%}"
            )
    else:
        st.info("No vector insight data available yet.")
    
    # Scan failure log locations
    st.subheader("Scan Failure Logs")
    
    st.markdown(
        f"""
        Scan failures are logged to:
        - Insight Log: `{INSIGHT_LOGS_FILE}`
        - Scan Failures Directory: `{SCAN_FAILURES_DIR}`
        
        Each scan failure includes:
        - Domain
        - Reason for failure
        - Failure type
        - Timestamp
        """
    )

def render_api_intelligence():
    """Render the API intelligence tab."""
    st.header("API Intelligence")
    
    # Display API overview
    st.subheader("API Overview")
    
    col1, col2, col3 = st.columns(3)
    
    with col1:
        st.metric(
            label="API Version",
            value=SYSTEM_VERSION
        )
    
    with col2:
        # Count API endpoints
        endpoint_count = 8  # Fixed number based on implementation
        st.metric(
            label="Endpoints",
            value=endpoint_count
        )
    
    with col3:
        # Count insights available via API
        latest_insights = get_latest_insights(limit=1000)
        insight_count = len(latest_insights)
        
        st.metric(
            label="Insights Available",
            value=insight_count
        )
    
    # API endpoints
    st.subheader("API Endpoints")
    
    endpoints = [
        {
            "endpoint": "/api/v1/score/{domain}",
            "method": "GET",
            "description": "Get visibility score and insights for a domain",
            "params": "domain: Domain name",
            "v4_fields": "Added insight_delta, foma_triggers, insight_quality fields"
        },
        {
            "endpoint": "/api/v1/insights/{domain}",
            "method": "GET",
            "description": "Get detailed insights for a domain",
            "params": "domain: Domain name",
            "v4_fields": "New in V4 - provides full insight data"
        },
        {
            "endpoint": "/api/v1/insights/latest",
            "method": "GET",
            "description": "Get latest insights across all domains",
            "params": "limit: Maximum number of insights to return",
            "v4_fields": "New in V4 - provides global insight feed"
        },
        {
            "endpoint": "/api/v1/foma/{domain}",
            "method": "GET",
            "description": "Get FOMA details for a domain",
            "params": "domain: Domain name",
            "v4_fields": "Enhanced with foma_triggers, actionable flags, clarity scores"
        },
        {
            "endpoint": "/api/v1/top/{category}",
            "method": "GET",
            "description": "Get top domains by visibility score for a category",
            "params": "category: Category name, limit: Maximum number of domains",
            "v4_fields": "Added insight_quality and foma_triggers fields"
        },
        {
            "endpoint": "/api/v1/benchmark/{category}",
            "method": "GET",
            "description": "Get benchmark data for a category",
            "params": "category: Category name",
            "v4_fields": "New in V4 - provides benchmark elite data"
        },
        {
            "endpoint": "/api/v1/visibility-deltas",
            "method": "GET",
            "description": "Get domains with the biggest changes in visibility",
            "params": "limit: Maximum number of domains",
            "v4_fields": "Added insight attribution for visibility changes"
        },
        {
            "endpoint": "/api/v1/metadata",
            "method": "GET",
            "description": "Get system metadata",
            "params": "None",
            "v4_fields": "Added insight_stats field with global insight metrics"
        }
    ]
    
    for endpoint in endpoints:
        with st.expander(f"{endpoint['method']} {endpoint['endpoint']}"):
            st.markdown(f"**Description:** {endpoint['description']}")
            st.markdown(f"**Parameters:** {endpoint['params']}")
            st.markdown(f"**V4 Enhancements:** {endpoint['v4_fields']}")
            
            # Add example request
            st.code(
                f"curl -H 'Authorization: Bearer YOUR_API_KEY' \\\n"
                f"     -H 'x-mcp-agent: true' \\\n"
                f"     -H 'x-session-type: agent' \\\n"
                f"     -H 'x-query-purpose: trust_query' \\\n"
                f"     http://api.llmrank.io{endpoint['endpoint'].replace('{domain}', 'example.com').replace('{category}', 'finance')}"
            )
    
    # New V4 response format
    st.subheader("V4 API Response Format")
    
    st.markdown(
        """
        V4 enhances all API responses with additional insight fields:
        """
    )
    
    st.code(
        """{
  "domain": "acmehealth.com",
  "llm_score": 73.1,
  "insight_delta": "-3.4",
  "foma_triggers": ["Outpaced by peer", "Drifting from index leader"],
  "insight_quality": "high",
  "last_scan_quality": "pass",
  "category": "healthcare",
  "insights": [
    {
      "insight": "Outpaced by healthline.com in 3 prompts after site update",
      "delta": -4.6,
      "actionable": true,
      "summary": "Healthline gained citations on FAQ prompt after blog refresh.",
      "foma_tag": {
        "category": "healthcare",
        "type": "Outpaced by peer",
        "severity": "high",
        "emotion": "alarm"
      },
      "clarity_score": 0.9,
      "vector": "peer"
    }
  ]
}""",
        language="json"
    )
    
    # LLM-Compatible JSON
    st.subheader("LLM & Machine-Compatible Format")
    
    st.markdown(
        """
        All V4 API endpoints support the `x-mcp-agent: true` header for Machine-Compatible Processing.
        
        This format is optimized for:
        - Large Language Models
        - Agent-based workflows
        - Automated decision systems
        - Programmatic FOMA analysis
        """
    )
    
    # API integration examples
    st.subheader("API Integration Examples")
    
    tab1, tab2 = st.tabs(["Python", "JavaScript"])
    
    with tab1:
        st.code("""
import requests
import json

API_KEY = "your_api_key"
API_HOST = "https://api.llmrank.io"""

def get_domain_insights(domain):
    """Get insights for a domain."""
    headers = {
        "Authorization": f"Bearer {API_KEY}",
        "x-mcp-agent": "true",
        "x-session-type": "agent",
        "x-query-purpose": "trust_query"
    }
    
    response = requests.get(
        f"{API_HOST}/api/v1/insights/{domain}",
        headers=headers
    )
    
    if response.status_code == 200:
        return response.json()
    else:
        return {"error": response.text}

def check_foma_triggers(domain):
    """Check if a domain has FOMA triggers."""
    insights = get_domain_insights(domain)
    
    if "error" in insights:
        return {"error": insights["error"]}
    
    foma_triggers = insights.get("foma_triggers", [])
    
    if foma_triggers:
        return {
            "domain": domain,
            "has_foma": True,
            "triggers": foma_triggers,
            "actionable_insights": [
                i for i in insights.get("insights", [])
                if i.get("actionable", False)
            ]
        }
    else:
        return {
            "domain": domain,
            "has_foma": False
        }

# Example usage
domain = "acmehealth.com"
foma_check = check_foma_triggers(domain)

if foma_check.get("has_foma", False):
    print(f"FOMA detected for {domain}:")
    for trigger in foma_check.get("triggers", []):
        print(f"- {trigger}")
    
    print("\nActionable insights:")
    for insight in foma_check.get("actionable_insights", []):
        print(f"- {insight.get('insight', '')}")
else:
    print(f"No FOMA detected for {domain}")
            """,
            language="python"
        )
    
    with tab2:
        st.code(
            """
const API_KEY = 'your_api_key';
const API_HOST = 'https://api.llmrank.io';

async function getDomainInsights(domain) {
  try {
    const response = await fetch(`${API_HOST}/api/v1/insights/${domain}`, {
      headers: {
        'Authorization': `Bearer ${API_KEY}`,
        'x-mcp-agent': 'true',
        'x-session-type': 'agent',
        'x-query-purpose': 'trust_query'
      }
    });
    
    if (!response.ok) {
      throw new Error(`API error: ${response.status}`);
    }
    
    return await response.json();
  } catch (error) {
    console.error('Error fetching insights:', error);
    return { error: error.message };
  }
}

async function checkFomaRisk(domains) {
  const results = [];
  
  for (const domain of domains) {
    const insights = await getDomainInsights(domain);
    
    if (insights.error) {
      results.push({
        domain,
        error: insights.error
      });
      continue;
    }
    
    const fomaRisk = insights.foma_triggers && insights.foma_triggers.length > 0;
    const severity = insights.insights.reduce((maxSeverity, insight) => {
      const currentSeverity = insight.foma_tag?.severity || 'medium';
      const severityValue = { high: 3, medium: 2, low: 1 }[currentSeverity] || 0;
      const maxValue = { high: 3, medium: 2, low: 1 }[maxSeverity] || 0;
      
      return severityValue > maxValue ? currentSeverity : maxSeverity;
    }, 'low');
    
    results.push({
      domain,
      fomaRisk,
      triggers: insights.foma_triggers || [],
      severity,
      insightQuality: insights.insight_quality,
      score: insights.llm_score
    });
  }
  
  return results;
}

// Example usage
const domainPortfolio = ['acmehealth.com', 'financialsite.com', 'legalexample.com'];

checkFomaRisk(domainPortfolio).then(results => {
  console.log('FOMA Risk Analysis:');
  results.forEach(result => {
    console.log(`${result.domain}: ${result.fomaRisk ? 'AT RISK' : 'OK'} (Severity: ${result.severity})`);
    if (result.fomaRisk) {
      console.log(`  Triggers: ${result.triggers.join(', ')}`);
    }
  });
});
            """,
            language="javascript"
        )
    
    # Badge integration
    st.subheader("LLM-Rated™ Badge Integration")
    
    st.markdown(
        """
        Showcase trust verification with the LLM-Rated™ badge:
        """
    )
    
    badge_html = """
    <div style="max-width: 300px; padding: 15px; text-align: center; border: 1px solid #ddd; border-radius: 5px; margin: 20px auto;">
        <div style="background-color: #f8f9fa; padding: 10px; border-radius: 50%; width: 100px; height: 100px; margin: 0 auto; display: flex; align-items: center; justify-content: center;">
            <span style="font-size: 48px;">✓</span>
        </div>
        <h3 style="margin-top: 15px;">LLM-Rated™</h3>
        <p style="color: #198754; font-weight: bold;">VERIFIED</p>
        <p style="font-size: 14px; color: #6c757d;">This site has been verified by LLMPageRank</p>
        <p style="font-size: 12px; margin-top: 10px;">Score: 82.4 | Updated: May 15, 2025</p>
    </div>
    """
    
    st.markdown(badge_html, unsafe_allow_html=True)
    
    st.markdown(
        """
        Integrate with a simple JavaScript snippet:
        """
    )
    
    st.code(
        """
<script src="https://llm-rated.com/badge.js" data-domain="yourdomain.com" data-key="YOUR_API_KEY"></script>
        """,
        language="html"
    )