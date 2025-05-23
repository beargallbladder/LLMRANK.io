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
    
    # Get data
    all_domains = db.get_all_tested_domains()
    
    # Main insights overview
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        st.markdown(
            f"<div class='insight-count-container'>"
            f"<div class='insight-count'>{len(all_domains)}</div>"
            f"<div class='insight-count-label'>Total Domains</div>"
            f"</div>",
            unsafe_allow_html=True
        )
    
    with col2:
        st.markdown(
            f"<div class='insight-count-container'>"
            f"<div class='insight-count'>5</div>"
            f"<div class='insight-count-label'>High-Quality Insights</div>"
            f"</div>",
            unsafe_allow_html=True
        )
    
    with col3:
        st.markdown(
            f"<div class='insight-count-container'>"
            f"<div class='insight-count'>8</div>"
            f"<div class='insight-count-label'>Categories Analyzed</div>"
            f"</div>",
            unsafe_allow_html=True
        )
    
    with col4:
        st.markdown(
            f"<div class='insight-count-container'>"
            f"<div class='insight-count'>3</div>"
            f"<div class='insight-count-label'>Critical FOMA Alerts</div>"
            f"</div>",
            unsafe_allow_html=True
        )
    
    # Sample FOMA Triggers distribution
    st.subheader("FOMA Triggers Distribution")
    
    sample_foma = {
        "Outpaced by peer": 12,
        "Drifting from index leader": 8,
        "SEO-LLM mismatch": 7, 
        "Trust signal decreased": 5,
        "Elite status lost": 4,
        "Citation pattern shift": 3
    }
    
    foma_df = pd.DataFrame({
        'trigger': list(sample_foma.keys()),
        'count': list(sample_foma.values())
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
    
    # Insight vector distribution
    st.subheader("Insight Vector Distribution")
    
    vector_counts = {
        "peer": 18,
        "self": 14,
        "benchmark": 9
    }
    
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
    
    # Latest insights visualization
    st.subheader("Latest Domain Insights")
    
    # Sample insights for demonstration
    sample_insights = [
        {
            "domain": "oracle.com",
            "llm_score": 82.4,
            "insight_delta": "+2.8",
            "insight_quality": "high",
            "foma_triggers": ["Trust signal increased", "Elite status gained"],
            "insights": [
                {
                    "insight": "Gained benchmark elite status",
                    "summary": "Your domain has joined the benchmark elite in enterprise_tech. This indicates your visibility strategy is working effectively.",
                    "vector": "benchmark",
                    "foma_tag": {"emotion": "celebration", "severity": "low"},
                    "clarity_score": 0.9
                }
            ]
        },
        {
            "domain": "healthline.com",
            "llm_score": 76.2,
            "insight_delta": "+4.5",
            "insight_quality": "high",
            "foma_triggers": ["Citation pattern shift", "Trust signal increased"],
            "insights": [
                {
                    "insight": "Gained 3 citations in GPT",
                    "summary": "Your domain has gained 3 citations in GPT, indicating a change in how this model perceives your content.",
                    "vector": "self",
                    "foma_tag": {"emotion": "relief", "severity": "medium"},
                    "clarity_score": 0.8
                }
            ]
        },
        {
            "domain": "findlaw.com",
            "llm_score": 71.9,
            "insight_delta": "-3.2",
            "insight_quality": "medium",
            "foma_triggers": ["Outpaced by peer", "SEO-LLM mismatch"],
            "insights": [
                {
                    "insight": "Outpaced by justia.com by 4.8 points",
                    "summary": "Ranked 3 out of 5 in your peer group, with justia.com showing stronger LLM citations.",
                    "vector": "peer",
                    "foma_tag": {"emotion": "concern", "severity": "medium"},
                    "clarity_score": 0.9
                }
            ]
        }
    ]
    
    # Display top insights
    for insight_data in sample_insights:
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

def render_insight_explorer():
    """Render the insight explorer tab."""
    st.header("Insight Explorer")
    
    # Get all tested domains for selection
    all_domains = db.get_all_tested_domains()
    
    if not all_domains and not os.path.exists(f"{DATA_DIR}/domains.json"):
        # Create some sample domains if none exist
        sample_domains = [
            "oracle.com", "microsoft.com", "healthline.com", 
            "findlaw.com", "chase.com", "mayoclinic.org"
        ]
        all_domains = sample_domains
    
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
    
    # Display domain info
    st.subheader(f"Domain: {selected_domain}")
    
    # Sample data for demonstration
    domain_data = {
        "oracle.com": {
            "score": 82.4,
            "structure": 85.1,
            "category": "enterprise_tech"
        },
        "microsoft.com": {
            "score": 80.1,
            "structure": 83.5,
            "category": "enterprise_tech"
        },
        "healthline.com": {
            "score": 76.2,
            "structure": 72.8,
            "category": "healthcare"
        },
        "findlaw.com": {
            "score": 71.9,
            "structure": 78.3,
            "category": "legal"
        },
        "chase.com": {
            "score": 77.5,
            "structure": 84.2,
            "category": "finance"
        },
        "mayoclinic.org": {
            "score": 79.8,
            "structure": 76.7,
            "category": "healthcare"
        }
    }
    
    domain_info = domain_data.get(selected_domain, {"score": 70.0, "structure": 75.0, "category": "unknown"})
    
    col1, col2, col3 = st.columns(3)
    
    with col1:
        st.metric(
            label="LLMRank Score",
            value=f"{domain_info['score']:.1f}"
        )
    
    with col2:
        st.metric(
            label="Structure Score",
            value=f"{domain_info['structure']:.1f}"
        )
    
    with col3:
        st.metric(
            label="Category",
            value=domain_info['category']
        )
    
    # Action buttons
    col1, col2 = st.columns(2)
    
    with col1:
        if st.button("Analyze Domain"):
            st.success(f"Domain {selected_domain} analysis complete!")
    
    # Display insight quality
    quality = "high" if domain_info['score'] > 80 else ("medium" if domain_info['score'] > 70 else "low")
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
    
    # Sample FOMA triggers
    domain_foma = {
        "oracle.com": ["Trust signal increased", "Elite status gained"],
        "microsoft.com": ["Citation pattern shift", "Elite status maintained"],
        "healthline.com": ["Citation pattern shift", "Trust signal increased"],
        "findlaw.com": ["Outpaced by peer", "SEO-LLM mismatch"],
        "chase.com": ["Trust signal stable", "Structure strength"],
        "mayoclinic.org": ["Peer rank up", "Citation increase"]
    }
    
    # Display FOMA triggers
    st.subheader("FOMA Triggers")
    
    foma_triggers = domain_foma.get(selected_domain, [])
    if foma_triggers:
        triggers_html = ""
        for trigger in foma_triggers:
            severity = "medium"  # Default
            
            # Set severity based on trigger type
            if "decreased" in trigger or "lost" in trigger or "Outpaced" in trigger:
                severity = "high"
            elif "increased" in trigger or "gained" in trigger:
                severity = "low"
            
            triggers_html += f"<span class='foma-tag foma-{severity}'>{trigger}</span>"
        
        st.markdown(f"<div>{triggers_html}</div>", unsafe_allow_html=True)
    else:
        st.info("No FOMA triggers detected for this domain.")
    
    # Sample insights for domains
    domain_insights = {
        "oracle.com": [
            {
                "insight": "Gained benchmark elite status",
                "summary": "Your domain has joined the benchmark elite in enterprise_tech. This indicates your visibility strategy is working effectively.",
                "vector": "benchmark",
                "foma_tag": {"emotion": "celebration", "severity": "low", "type": "Elite status gained"},
                "clarity": 0.9,
                "delta": 2.8,
                "actionable": False
            }
        ],
        "microsoft.com": [
            {
                "insight": "Citation pattern shift in Claude model",
                "summary": "Your domain has gained more direct citations in the Claude model, indicating improved perception of authoritative content.",
                "vector": "self",
                "foma_tag": {"emotion": "relief", "severity": "low", "type": "Citation pattern shift"},
                "clarity": 0.8,
                "delta": 1.5,
                "actionable": False
            }
        ],
        "healthline.com": [
            {
                "insight": "Gained 3 citations in GPT",
                "summary": "Your domain has gained 3 citations in GPT, indicating a change in how this model perceives your content.",
                "vector": "self",
                "foma_tag": {"emotion": "relief", "severity": "medium", "type": "Citation pattern shift"},
                "clarity": 0.8,
                "delta": 4.5,
                "actionable": False
            }
        ],
        "findlaw.com": [
            {
                "insight": "Outpaced by justia.com by 4.8 points",
                "summary": "Ranked 3 out of 5 in your peer group, with justia.com showing stronger LLM citations.",
                "vector": "peer",
                "foma_tag": {"emotion": "concern", "severity": "medium", "type": "Outpaced by peer"},
                "clarity": 0.9,
                "delta": -3.2,
                "actionable": True
            },
            {
                "insight": "Trust mismatch: Strong SEO but weak LLM visibility",
                "summary": "Your domain has strong SEO signals (score: 78.3) but lower LLM visibility (score: 71.9). This indicates a content/trust gap that can be bridged.",
                "vector": "self",
                "foma_tag": {"emotion": "frustration", "severity": "high", "type": "SEO-LLM mismatch"},
                "clarity": 0.9,
                "delta": -6.4,
                "actionable": True
            }
        ],
        "chase.com": [
            {
                "insight": "Stable trust positioning in Finance category",
                "summary": "Your domain maintains a strong position in the Finance category with consistent citation patterns.",
                "vector": "benchmark",
                "foma_tag": {"emotion": "relief", "severity": "low", "type": "Trust signal stable"},
                "clarity": 0.7,
                "delta": 0.2,
                "actionable": False
            }
        ],
        "mayoclinic.org": [
            {
                "insight": "Moved up 1 position in peer ranking",
                "summary": "Your rank changed from 2 to 1 among peers in healthcare.",
                "vector": "peer",
                "foma_tag": {"emotion": "relief", "severity": "low", "type": "Peer rank up"},
                "clarity": 0.8,
                "delta": 2.1,
                "actionable": False
            }
        ]
    }
    
    # Display individual insights
    st.subheader("Detailed Insights")
    
    insights = domain_insights.get(selected_domain, [])
    if insights:
        for insight in insights:
            # Get insight data
            insight_text = insight.get('insight', '')
            summary = insight.get('summary', '')
            vector = insight.get('vector', '')
            emotion = insight.get('foma_tag', {}).get('emotion', '')
            severity = insight.get('foma_tag', {}).get('severity', 'medium')
            clarity = insight.get('clarity', 0)
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
    
    # Sample history data
    history_data = [
        {"date": "2025-05-15", "visibility": 71.9, "structure": 78.3},
        {"date": "2025-05-08", "visibility": 75.1, "structure": 77.9},
        {"date": "2025-05-01", "visibility": 73.4, "structure": 77.2},
        {"date": "2025-04-24", "visibility": 69.8, "structure": 76.5},
        {"date": "2025-04-17", "visibility": 68.2, "structure": 75.8}
    ]
    
    if selected_domain == "oracle.com":
        history_data = [
            {"date": "2025-05-15", "visibility": 82.4, "structure": 85.1},
            {"date": "2025-05-08", "visibility": 79.6, "structure": 84.3},
            {"date": "2025-05-01", "visibility": 76.9, "structure": 83.7},
            {"date": "2025-04-24", "visibility": 75.2, "structure": 82.9},
            {"date": "2025-04-17", "visibility": 74.1, "structure": 82.2}
        ]
    elif selected_domain == "healthline.com":
        history_data = [
            {"date": "2025-05-15", "visibility": 76.2, "structure": 72.8},
            {"date": "2025-05-08", "visibility": 71.7, "structure": 72.3},
            {"date": "2025-05-01", "visibility": 70.9, "structure": 71.8},
            {"date": "2025-04-24", "visibility": 69.5, "structure": 71.4},
            {"date": "2025-04-17", "visibility": 68.3, "structure": 70.9}
        ]
    
    # Show historical data
    st.subheader("Trust Signal History")
    
    # Create DataFrame
    df = pd.DataFrame(history_data)
    
    # Create chart
    fig = go.Figure()
    
    fig.add_trace(go.Scatter(
        x=df["date"],
        y=df["visibility"],
        mode='lines+markers',
        name='LLMRank',
        line=dict(color='#0d6efd', width=3)
    ))
    
    fig.add_trace(go.Scatter(
        x=df["date"],
        y=df["structure"],
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

def render_foma_analysis():
    """Render the FOMA analysis tab."""
    st.header("FOMA Analysis")
    
    # Display FOMA overview
    st.subheader("FOMA Overview")
    
    col1, col2 = st.columns(2)
    
    with col1:
        # Count FOMA triggers
        st.metric(
            label="Total FOMA Triggers",
            value=39
        )
        
        # Display FOMA by platform
        st.markdown("### FOMA by Platform")
        
        platform_html = """
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
            "high": 12,
            "medium": 18,
            "low": 9
        }
        
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
            
        # FOMA emotion distribution
        emotion_counts = {
            "alarm": 8,
            "worry": 6,
            "concern": 9,
            "guidance": 7,
            "relief": 11,
            "celebration": 4
        }
        
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
    
    # FOMA by category
    st.subheader("FOMA by Category")
    
    # Sample category FOMA data
    category_foma = {
        "finance": {"total": 8, "triggers": {"Trust signal stable": 3, "Peer rank up": 2, "Structure strength": 3}},
        "healthcare": {"total": 7, "triggers": {"Citation pattern shift": 4, "Trust signal increased": 3}},
        "legal": {"total": 9, "triggers": {"Outpaced by peer": 3, "SEO-LLM mismatch": 4, "Citation pattern shift": 2}},
        "enterprise_tech": {"total": 6, "triggers": {"Elite status gained": 2, "Trust signal increased": 2, "Citation pattern shift": 2}},
        "education": {"total": 5, "triggers": {"Trust signal stable": 2, "Structure strength": 3}},
        "ecommerce": {"total": 4, "triggers": {"SEO-LLM mismatch": 2, "Citation pattern shift": 2}}
    }
    
    # Prepare data for chart
    categories = []
    totals = []
    
    for category, data in category_foma.items():
        categories.append(category)
        totals.append(data["total"])
    
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
    
    # FOMA example insights
    st.subheader("Example FOMA Insights")
    
    # Sample high-severity insights
    high_severity_insights = [
        {
            "domain": "findlaw.com",
            "insight": {
                "insight": "Trust mismatch: Strong SEO but weak LLM visibility",
                "summary": "Your domain has strong SEO signals (score: 78.3) but lower LLM visibility (score: 71.9). This indicates a content/trust gap that can be bridged.",
                "vector": "self",
                "foma_tag": {"emotion": "frustration", "severity": "high", "type": "SEO-LLM mismatch"},
                "clarity": 0.9
            }
        },
        {
            "domain": "shopify.com",
            "insight": {
                "insight": "Outpaced by three competitors in your category",
                "summary": "Your domain has fallen behind multiple competitors in the ecommerce category, creating a significant trust gap.",
                "vector": "peer",
                "foma_tag": {"emotion": "alarm", "severity": "high", "type": "Multi-peer outdistance"},
                "clarity": 0.9
            }
        },
        {
            "domain": "khanacademy.org",
            "insight": {
                "insight": "Lost benchmark elite status in Education category",
                "summary": "Your domain has fallen out of the benchmark elite in education. This indicates a competitive shift in your category.",
                "vector": "benchmark",
                "foma_tag": {"emotion": "urgency", "severity": "high", "type": "Elite status lost"},
                "clarity": 0.9
            }
        }
    ]
    
    for item in high_severity_insights:
        domain = item['domain']
        insight = item['insight']
        
        # Get insight data
        insight_text = insight.get('insight', '')
        summary = insight.get('summary', '')
        vector = insight.get('vector', '')
        emotion = insight.get('foma_tag', {}).get('emotion', '')
        clarity = insight.get('clarity', 0)
        
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

def render_scan_quality():
    """Render the scan quality tab."""
    st.header("Scan Quality")
    
    # Display scan failure overview
    st.subheader("Scan Failure Overview")
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.metric(
            label="Total Scan Failures",
            value=12
        )
    
    with col2:
        # Sample failure types
        failure_types = {
            "data_gap": 5,
            "prompt_problem": 3,
            "crawl_failure": 2,
            "model_fatigue": 1,
            "insight_miss": 1
        }
        
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
    
    # Insight quality distribution
    st.subheader("Insight Quality Distribution")
    
    # Sample quality counts
    quality_counts = {
        'high': 18,
        'medium': 24,
        'low': 9,
        'none': 3
    }
    
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
    
    # Vector insight distribution
    st.subheader("Vector Insight Distribution")
    
    # Sample vector counts
    vector_counts = {
        'peer': 18,
        'self': 14, 
        'benchmark': 9
    }
    
    # Create DataFrame
    vector_df = pd.DataFrame({
        'vector': list(vector_counts.keys()),
        'count': list(vector_counts.values())
    })
    
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
        insight_count = 41
        
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
API_HOST = "https://api.llmrank.io"

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
        """, language="python")
    
    with tab2:
        st.code("""
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
        """, language="javascript")
    
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