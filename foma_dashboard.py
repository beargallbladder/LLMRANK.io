"""
LLMPageRank FOMA Publishing Dashboard

This module implements the dashboard for the PRD 11 FOMA Publishing Flow,
displaying published insights, agent cooperation, and story effectiveness.
"""

import random
import datetime
from typing import Dict, List, Optional

import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go

import foma_publisher
import agent_survival_loop


def render_foma_dashboard():
    """Render the FOMA Publishing Dashboard."""
    st.title("LLMPageRank V11 FOMA Publishing Flow")
    st.markdown("### Signal → Curiosity → Regret")
    
    # Add tabs for different sections
    tab1, tab2, tab3 = st.tabs([
        "Published Stories", 
        "Agent Survival Organism", 
        "Public FOMA Feed"
    ])
    
    with tab1:
        render_published_stories()
    
    with tab2:
        render_agent_survival_organism()
    
    with tab3:
        render_public_foma_feed()


def render_published_stories():
    """Render the published stories section."""
    st.markdown("## Published Stories")
    st.markdown("Trust signal shifts converted into compelling narratives")
    
    # Get recent stories
    stories = foma_publisher.get_recent_stories()
    
    if not stories:
        # Generate some sample stories for demonstration
        sample_stories = generate_sample_stories()
        stories = sample_stories
    
    # Create metrics
    col1, col2, col3 = st.columns(3)
    with col1:
        st.metric("Stories Published", len(stories), "+5 today")
    with col2:
        clarity_avg = sum(s.get("clarity_score", 0) for s in stories) / len(stories) if stories else 0
        st.metric("Avg Clarity Score", f"{clarity_avg:.2f}", "+0.05")
    with col3:
        impact_avg = sum(s.get("impact_score", 0) for s in stories) / len(stories) if stories else 0
        st.metric("Avg Impact Score", f"{impact_avg:.2f}", "+0.08")
    
    # Display stories
    st.markdown("### Recent Stories")
    
    for i, story in enumerate(stories[:5]):
        with st.expander(f"{story.get('domain_class', 'Unknown')} - {story.get('insight_type', 'Unknown')}", expanded=i==0):
            st.markdown(f"**Published:** {story.get('published_at', '')[:10]}")
            st.markdown(f"**Triggered by prompt:** \"{story.get('prompt_trigger', '')}\"")
            st.markdown(f"**Trust Delta:** {story.get('trust_delta', 0)}")
            st.markdown(f"**Story:**")
            st.markdown(f"> {story.get('story_summary', '')}")
            
            # Display metrics
            cols = st.columns(3)
            cols[0].metric("Clarity Score", f"{story.get('clarity_score', 0):.2f}")
            cols[1].metric("Impact Score", f"{story.get('impact_score', 0):.2f}")
            cols[2].metric("Peer Set", story.get('peer_set', 0))
            
            # Display engagement metrics if available
            if "engagement_metrics" in story:
                metrics = story["engagement_metrics"]
                st.markdown("**Engagement Metrics:**")
                eng_cols = st.columns(3)
                eng_cols[0].metric("Views", metrics.get("views", 0))
                eng_cols[1].metric("Clicks", metrics.get("clicks", 0))
                eng_cols[2].metric("Conversions", metrics.get("conversions", 0))
                
                # Calculate CTR
                views = metrics.get("views", 0)
                clicks = metrics.get("clicks", 0)
                ctr = (clicks / views) * 100 if views > 0 else 0
                
                st.progress(ctr / 100)
                st.markdown(f"**Click-through Rate:** {ctr:.1f}%")
    
    # Story distribution by domain class
    st.markdown("### Story Distribution")
    
    domain_classes = {}
    for story in stories:
        domain_class = story.get("domain_class", "Unknown")
        if domain_class not in domain_classes:
            domain_classes[domain_class] = 0
        domain_classes[domain_class] += 1
    
    if domain_classes:
        # Create DataFrame
        domain_class_data = pd.DataFrame({
            "Domain Class": list(domain_classes.keys()),
            "Story Count": list(domain_classes.values())
        })
        
        # Create pie chart
        fig = px.pie(
            domain_class_data,
            names="Domain Class",
            values="Story Count",
            title="Stories by Domain Class"
        )
        
        st.plotly_chart(fig, use_container_width=True)
    
    # Trust delta distribution
    st.markdown("### Trust Delta Distribution")
    
    trust_deltas = [story.get("trust_delta", 0) for story in stories]
    
    if trust_deltas:
        # Create histogram
        fig = px.histogram(
            trust_deltas,
            title="Trust Delta Distribution",
            labels={"value": "Trust Delta", "count": "Story Count"},
            color_discrete_sequence=["#3366CC"],
        )
        
        fig.update_layout(
            xaxis_title="Trust Delta",
            yaxis_title="Story Count"
        )
        
        st.plotly_chart(fig, use_container_width=True)
    
    # Top movers
    st.markdown("### Top Movers")
    
    top_movers = foma_publisher.get_top_movers()
    
    if not top_movers and stories:
        # Use top stories by trust delta
        top_movers = sorted(stories, key=lambda x: abs(x.get("trust_delta", 0)), reverse=True)[:5]
    
    if top_movers:
        # Create DataFrame
        mover_data = []
        
        for mover in top_movers:
            mover_data.append({
                "Domain Class": mover.get("domain_class", "Unknown"),
                "Trust Delta": mover.get("trust_delta", 0),
                "Insight Type": mover.get("insight_type", "Unknown"),
                "Clarity Score": mover.get("clarity_score", 0)
            })
        
        mover_df = pd.DataFrame(mover_data)
        
        # Display as table
        st.dataframe(mover_df)
        
        # Create bar chart
        fig = px.bar(
            mover_df,
            x="Domain Class",
            y="Trust Delta",
            color="Trust Delta",
            color_continuous_scale=["red", "yellow", "green"],
            title="Top Movers by Trust Delta"
        )
        
        st.plotly_chart(fig, use_container_width=True)


def render_agent_survival_organism():
    """Render the agent survival organism section."""
    st.markdown("## Agent Survival Organism")
    st.markdown("When one agent fails, others must coordinate or no one gets paid")
    
    # Get colony health
    colony_health = agent_survival_loop.get_colony_health()
    
    # Get active responses
    active_responses = agent_survival_loop.get_active_responses()
    
    # Create colony health metrics
    status_color = {
        "stable": "green",
        "stressed": "orange",
        "critical": "red"
    }.get(colony_health.get("status", "stable"), "gray")
    
    sustainability_color = {
        "high": "green",
        "medium": "orange",
        "low": "red"
    }.get(colony_health.get("sustainability", "high"), "gray")
    
    st.markdown(f"### Colony Status: <span style='color:{status_color}'>{colony_health.get('status', 'stable').title()}</span>", unsafe_allow_html=True)
    
    col1, col2, col3, col4 = st.columns(4)
    with col1:
        st.metric("Active Agents", colony_health.get("active_agents", 0))
    with col2:
        st.metric("Failing Agents", colony_health.get("failing_agents", 0))
    with col3:
        st.metric("Avg Cookies", f"{colony_health.get('average_cookies', 0):.1f}")
    with col4:
        st.metric("Cookie Flow", colony_health.get("cookie_flow", 0))
    
    st.markdown(f"### Sustainability: <span style='color:{sustainability_color}'>{colony_health.get('sustainability', 'high').title()}</span>", unsafe_allow_html=True)
    
    # Display active responses
    if active_responses:
        st.markdown("### Active Survival Responses")
        
        for i, response in enumerate(active_responses):
            with st.expander(f"Response for {response.get('failing_agent', 'Unknown')}", expanded=i==0):
                st.markdown(f"**Status:** {response.get('status', 'unknown')}")
                st.markdown(f"**Initiated:** {response.get('timestamp', '')[:10]}")
                st.markdown(f"**Response Type:** {response.get('response_type', 'unknown')}")
                
                # Display helpers
                st.markdown("**Selected Helpers:**")
                helper_list = ", ".join(response.get("helpers", []))
                st.markdown(f"- {helper_list}")
                
                # Display responded helpers
                if "helpers_responded" in response:
                    helpers_responded = response["helpers_responded"]
                    if helpers_responded:
                        st.markdown("**Helpers Responded:**")
                        responded_list = ", ".join(helpers_responded)
                        st.markdown(f"- {responded_list}")
                        
                        # Progress bar for response rate
                        response_rate = len(helpers_responded) / len(response.get("helpers", [])) if response.get("helpers", []) else 0
                        st.progress(response_rate)
                        st.markdown(f"**Response Rate:** {response_rate * 100:.0f}%")
    else:
        st.info("No active survival responses. The agent colony is functioning normally.")
    
    # Display cookie matrix
    st.markdown("### Cookie Reward Matrix")
    
    cookie_matrix = [
        {"Condition": "Agent assists weak agent", "Cookie Bonus": "+1.0 (shared)", "Cookie Penalty": "0"},
        {"Condition": "All agents ignore weak agent", "Cookie Bonus": "0", "Cookie Penalty": "-1.5 (global)"}
    ]
    
    cookie_df = pd.DataFrame(cookie_matrix)
    st.table(cookie_df)
    
    # Visualize agent interactions
    st.markdown("### Agent Interaction Network")
    
    # Create a sample network for demonstration
    if not active_responses:
        # Generate sample failing agents for visualization
        failing_agents = generate_sample_failing_agents()
    else:
        # Use real failing agents
        failing_agents = agent_survival_loop.check_for_failing_agents()
    
    # Get agent registry for visualization
    registry = {"scan_scheduler.agent": {"status": "active", "cookies": 8},
               "prompt_optimizer.agent": {"status": "active", "cookies": 6},
               "benchmark_validator.agent": {"status": "active", "cookies": 7},
               "insight_monitor.agent": {"status": "dormant", "cookies": 2},
               "trust_drift.agent": {"status": "active", "cookies": 9},
               "scorecard_writer.agent": {"status": "active", "cookies": 5},
               "integration_tester.agent": {"status": "active", "cookies": 4},
               "api_validator.agent": {"status": "active", "cookies": 7},
               "revalidator.agent": {"status": "active", "cookies": 6}}
    
    # Create nodes
    nodes = []
    node_colors = []
    node_sizes = []
    
    for agent_name, agent_data in registry.items():
        nodes.append(agent_name)
        
        # Set node color based on status
        if any(fa.get("agent_name", "") == agent_name for fa in failing_agents):
            node_colors.append("red")
        elif agent_data.get("status", "") == "dormant":
            node_colors.append("orange")
        else:
            node_colors.append("green")
        
        # Set node size based on cookies
        node_sizes.append(agent_data.get("cookies", 5) * 5)
    
    # Create figure
    fig = go.Figure()
    
    # Add nodes
    fig.add_trace(go.Scatter(
        x=[0, 1, 2, 0, 1, 2, 0, 1, 2],
        y=[0, 0, 0, 1, 1, 1, 2, 2, 2],
        mode="markers+text",
        marker=dict(
            color=node_colors,
            size=node_sizes,
            line=dict(color="black", width=1)
        ),
        text=nodes,
        textposition="bottom center",
        name="Agents"
    ))
    
    # Add edges for helping relationships
    if active_responses:
        for response in active_responses:
            failing_agent = response.get("failing_agent", "")
            helpers = response.get("helpers_responded", [])
            
            if failing_agent and helpers:
                failing_idx = nodes.index(failing_agent)
                failing_x = [0, 1, 2][failing_idx % 3]
                failing_y = [0, 1, 2][failing_idx // 3]
                
                for helper in helpers:
                    helper_idx = nodes.index(helper)
                    helper_x = [0, 1, 2][helper_idx % 3]
                    helper_y = [0, 1, 2][helper_idx // 3]
                    
                    fig.add_trace(go.Scatter(
                        x=[helper_x, failing_x],
                        y=[helper_y, failing_y],
                        mode="lines",
                        line=dict(color="blue", width=2),
                        showlegend=False
                    ))
    
    fig.update_layout(
        title="Agent Network",
        showlegend=False,
        margin=dict(l=10, r=10, t=30, b=10),
        xaxis=dict(showgrid=False, zeroline=False, showticklabels=False),
        yaxis=dict(showgrid=False, zeroline=False, showticklabels=False),
        width=600,
        height=400
    )
    
    st.plotly_chart(fig, use_container_width=True)


def render_public_foma_feed():
    """Render the public FOMA feed section."""
    st.markdown("## Public FOMA Feed")
    st.markdown("Anonymized insights to create tension and drive engagement")
    
    # Get category summaries
    category_insights = foma_publisher.get_category_insight_summary()
    
    if not category_insights:
        # Generate sample insights for demonstration
        category_insights = generate_sample_category_insights()
    
    # Display weekly insight blurbs
    st.markdown("### Weekly Insight Blurbs")
    
    blurbs = foma_publisher.generate_weekly_insight_blurbs()
    
    if not blurbs:
        # Generate sample blurbs for demonstration
        blurbs = generate_sample_blurbs()
    
    for blurb in blurbs:
        st.markdown(f"- {blurb}")
    
    # CTA button
    st.markdown("---")
    st.markdown("### Concerned About Your Brand's Position?")
    
    col1, col2 = st.columns([3, 1])
    with col1:
        st.markdown("One in five brands in this category dropped trust last week.")
    with col2:
        st.button("See Where You Stand", type="primary")
    
    # Capture email modal
    if "show_modal" not in st.session_state:
        st.session_state.show_modal = False
    
    if st.button("Register for FOMA Alerts"):
        st.session_state.show_modal = True
    
    if st.session_state.show_modal:
        with st.form("email_form"):
            st.text_input("Email Address", placeholder="your@email.com")
            st.text_input("Company", placeholder="Your Company")
            st.selectbox("Industry", ["AI Tools", "Financial Services", "Healthcare Providers", "Legal Resources", "Creator Platforms", "Web3 Services", "Consumer Technology"])
            
            if st.form_submit_button("Register"):
                st.success("Thank you for registering! You will receive FOMA alerts when your category experiences significant trust shifts.")
                st.session_state.show_modal = False


def generate_sample_stories() -> List[Dict]:
    """
    Generate sample stories for demonstration.
    
    Returns:
        List of sample story dictionaries
    """
    domain_classes = [
        "AI Tools", "Financial Services", "Healthcare Providers",
        "Legal Resources", "Creator Platforms", "Web3 Services"
    ]
    
    insight_types = [
        "peer overtaken", "rising star", "stability anomaly", "trust shift"
    ]
    
    stories = []
    
    for i in range(10):
        domain_class = random.choice(domain_classes)
        insight_type = random.choice(insight_types)
        
        # Generate trust delta based on insight type
        if insight_type == "peer overtaken":
            trust_delta = -1 * random.uniform(1.5, 5.0)
        elif insight_type == "rising star":
            trust_delta = random.uniform(1.5, 5.0)
        elif insight_type == "stability anomaly":
            trust_delta = random.uniform(-0.5, 0.5)
        else:
            trust_delta = random.uniform(-3.0, 3.0)
        
        published_days_ago = random.randint(0, 14)
        published_at = (datetime.datetime.now() - datetime.timedelta(days=published_days_ago)).isoformat()
        
        # Generate story
        if insight_type == "peer overtaken":
            story = f"A previously top-ranked {domain_class.lower()} lost significant visibility after competitors upgraded their trust signals."
        elif insight_type == "rising star":
            story = f"An emerging {domain_class.lower()} gained unprecedented visibility through consistent trust signal optimization."
        elif insight_type == "stability anomaly":
            story = f"Despite market turbulence, one {domain_class.lower()} maintained perfect visibility while competitors fluctuated wildly."
        else:
            story = f"Subtle trust signal changes in a {domain_class.lower()} resulted in a dramatic reordering of visibility rankings."
        
        # Create story dictionary
        stories.append({
            "id": f"story-{i+1}",
            "published_at": published_at,
            "domain_class": domain_class,
            "insight_type": insight_type,
            "trust_delta": round(trust_delta, 1),
            "peer_set": random.randint(3, 8),
            "clarity_score": round(random.uniform(0.7, 0.95), 2),
            "impact_score": round(random.uniform(0.6, 0.95), 2),
            "prompt_trigger": f"Best {domain_class.lower()} 2025",
            "story_summary": story,
            "anonymized": True,
            "engagement_metrics": {
                "views": random.randint(50, 500),
                "clicks": random.randint(5, 50),
                "conversions": random.randint(0, 10)
            }
        })
    
    return stories


def generate_sample_failing_agents() -> List[Dict]:
    """
    Generate sample failing agents for demonstration.
    
    Returns:
        List of sample failing agent dictionaries
    """
    return [
        {
            "agent_name": "insight_monitor.agent",
            "consecutive_failures": 2,
            "cookie_count": 2,
            "performance_score": 0.3,
            "last_success": (datetime.datetime.now() - datetime.timedelta(days=3)).isoformat()
        }
    ]


def generate_sample_category_insights() -> Dict[str, Dict]:
    """
    Generate sample category insights for demonstration.
    
    Returns:
        Dictionary of sample category insight dictionaries
    """
    categories = {
        "AI Tools": {
            "story_count": 15,
            "negative_shifts": 5,
            "positive_shifts": 7,
            "avg_delta": 0.8,
            "avg_clarity": 0.85,
            "avg_impact": 0.78,
            "pct_negative": 33,
            "headline": "33% of AI Tools brands lost trust position last week."
        },
        "Financial Services": {
            "story_count": 12,
            "negative_shifts": 2,
            "positive_shifts": 8,
            "avg_delta": 1.5,
            "avg_clarity": 0.82,
            "avg_impact": 0.75,
            "pct_negative": 16,
            "headline": "Trust positions stable for Financial Services this week."
        },
        "Healthcare Providers": {
            "story_count": 8,
            "negative_shifts": 3,
            "positive_shifts": 4,
            "avg_delta": 0.3,
            "avg_clarity": 0.88,
            "avg_impact": 0.82,
            "pct_negative": 37,
            "headline": "37% of Healthcare Providers brands lost trust position last week."
        },
        "Web3 Services": {
            "story_count": 20,
            "negative_shifts": 12,
            "positive_shifts": 5,
            "avg_delta": -1.8,
            "avg_clarity": 0.79,
            "avg_impact": 0.85,
            "pct_negative": 60,
            "headline": "60% of Web3 Services brands lost trust position last week."
        }
    }
    
    return categories


def generate_sample_blurbs() -> List[str]:
    """
    Generate sample blurbs for demonstration.
    
    Returns:
        List of sample blurb strings
    """
    return [
        "One in 3 brands in AI Tools dropped trust last week.",
        "Average trust position dropped significantly in Web3 Services.",
        "Web3 Services showed high volatility with 20 trust changes detected.",
        "Trust positions stable for Financial Services this week.",
        "Healthcare Providers experienced moderate trust shifts, with 37% of brands showing negative movement.",
        "Creator Platforms showed the highest clarity scores across all categories.",
        "60% of Web3 Services brands lost trust position last week."
    ]