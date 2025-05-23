"""
LLMRank.io Documentation Site

This module creates a documentation site for the LLMRank.io MCP API,
showing its capabilities while capturing leads through a waitlist system.
"""

import streamlit as st
import pandas as pd
import json
import os
import uuid
import datetime
import time
import plotly.graph_objects as go
import plotly.express as px
from typing import Dict, List, Any, Optional

# Make sure directories exist
os.makedirs("data/docs", exist_ok=True)
os.makedirs("data/docs/waitlist", exist_ok=True)

# Constants
WAITLIST_FILE = "data/docs/waitlist/subscribers.json"
PAGE_ICON = "📊"
SITE_TITLE = "LLMRank.io"
PRIMARY_COLOR = "#4F8BF9"
SECONDARY_COLOR = "#FF4B4B"
ACCENT_COLOR = "#1EAEDB"
BACKGROUND_COLOR = "#FFFFFF"
TEXT_COLOR = "#262730"

# Initialize waitlist if it doesn't exist
if not os.path.exists(WAITLIST_FILE):
    with open(WAITLIST_FILE, "w") as f:
        json.dump([], f)

def load_waitlist() -> List[Dict[str, Any]]:
    """Load the waitlist data."""
    try:
        with open(WAITLIST_FILE, "r") as f:
            return json.load(f)
    except Exception:
        return []

def save_to_waitlist(subscriber: Dict[str, Any]) -> bool:
    """Save a subscriber to the waitlist."""
    try:
        waitlist = load_waitlist()
        # Check if email already exists
        for entry in waitlist:
            if entry.get("email") == subscriber.get("email"):
                return False
        
        waitlist.append(subscriber)
        
        with open(WAITLIST_FILE, "w") as f:
            json.dump(waitlist, f, indent=2)
        return True
    except Exception:
        return False

def display_api_response(title: str, code: str, response: Dict[str, Any]) -> None:
    """Display an API request and response."""
    st.subheader(title)
    col1, col2 = st.columns([1, 1])
    
    with col1:
        st.code(code, language="python")
    
    with col2:
        st.json(response)

def display_pulse_animation() -> None:
    """Display a pulse animation representing agent activity."""
    # Create sample data for the animation
    times = list(range(100))
    signal = [50 + 40 * (0.6 + 0.4 * (i % 12) / 12) * (0.5 + 0.5 * (i % 7) / 7) for i in times]
    df = pd.DataFrame({"time": times, "signal": signal})
    
    # Create the animation
    fig = px.line(df, x="time", y="signal", title="Live Agent Pulse (Last 60 Minutes)")
    fig.update_layout(
        xaxis_title="Time (minutes ago)",
        yaxis_title="Signal Strength",
        height=300,
        margin=dict(l=20, r=20, t=40, b=20),
    )
    fig.update_traces(line_color=PRIMARY_COLOR)
    
    # Display the chart
    st.plotly_chart(fig, use_container_width=True)

def display_agent_deployment() -> None:
    """Display a heatmap of agent deployments."""
    # Create sample data for agent deployments
    categories = ["Technology", "Finance", "Healthcare", "Retail", "Media", "Automotive"]
    agents = ["IndexScan", "SurfaceSeed", "DriftPulse", "CitationVerifier", "BrandMonitor"]
    
    # Generate random deployment strengths
    import random
    random.seed(42)  # For consistent results
    data = []
    for i, category in enumerate(categories):
        for j, agent in enumerate(agents):
            # Create a pattern where some cells are hotter
            base = 30 + 10 * (i % 3) + 15 * (j % 2)
            variance = random.randint(-5, 15)
            data.append([category, agent, base + variance])
    
    df = pd.DataFrame(data, columns=["Category", "Agent", "Deployment"])
    
    # Create the heatmap
    fig = px.density_heatmap(
        df, 
        x="Category", 
        y="Agent", 
        z="Deployment",
        color_continuous_scale="Viridis",
        title="Agent Deployment Matrix"
    )
    fig.update_layout(
        height=300,
        margin=dict(l=20, r=20, t=40, b=20),
    )
    
    # Display the chart
    st.plotly_chart(fig, use_container_width=True)

def display_agent_lifecycle() -> None:
    """Display the agent lifecycle as a circular flow diagram."""
    # Create sample data for agent lifecycle
    labels = ["Initialize", "Scan", "Process", "Generate Insights", "Verify", "Report", "Rest"]
    values = [10, 20, 25, 15, 10, 10, 10]
    
    # Create cycle colors - blue to green gradient
    colors = [
        "#1E3F66", "#2E5984", "#3E73A2", "#4F8CC0", 
        "#5FA5DE", "#6FBFFC", "#7FD9DA"
    ]
    
    # Create the chart
    fig = go.Figure(data=[
        go.Pie(
            labels=labels,
            values=values,
            hole=.4,
            marker_colors=colors,
            textinfo='label+percent',
            insidetextorientation='radial'
        )
    ])
    
    fig.update_layout(
        annotations=[dict(text='Agent<br>Lifecycle', x=0.5, y=0.5, font_size=15, showarrow=False)],
        height=350,
        margin=dict(l=20, r=20, t=40, b=20),
        title="Agent Runtime Lifecycle",
    )
    
    # Display the chart
    st.plotly_chart(fig, use_container_width=True)

def show_landing_page() -> None:
    """Show the landing page."""
    st.title("LLMRank.io")
    st.subheader("Memory Layer Protocol (MCP) API")
    
    st.markdown("""
    ## The Trust Signal Intelligence Layer
    
    LLMRank.io provides an advanced API for monitoring, tracking, and influencing how AI systems perceive
    brands and entities in the digital ecosystem. Our Memory Context Protocol (MCP) gives you
    programmatic access to the world's most comprehensive brand memory vulnerability data.
    """)
    
    # Show a pulse animation in a container
    with st.container():
        display_pulse_animation()
    
    # Highlights in three columns
    col1, col2, col3 = st.columns(3)
    
    with col1:
        st.markdown("### Monitor")
        st.markdown("""
        * Brand Memory Vulnerability Score
        * Competitive Position Tracking
        * Citation Drift Detection
        * Prompt Injection Defense
        """)
    
    with col2:
        st.markdown("### Analyze")
        st.markdown("""
        * Contextual Risk Assessment
        * Memory Imprint Depth Analysis
        * Cross-model Memory Verification
        * Brand-Specific Sentiment Tracking
        """)
    
    with col3:
        st.markdown("### Act")
        st.markdown("""
        * Signal Strength Enhancement
        * Vulnerability Gap Remediation
        * Competitive Intelligence
        * Proactive Memory Reinforcement
        """)
    
    # Show waitlist form
    st.markdown("---")
    st.subheader("Join the Waitlist for API Access")
    
    with st.form("waitlist_form"):
        col1, col2 = st.columns([3, 2])
        
        with col1:
            email = st.text_input("Email Address", key="email")
            company = st.text_input("Company Name", key="company")
            use_case = st.text_area("How do you plan to use the MCP API?", key="use_case")
        
        with col2:
            st.markdown("### Access to:")
            st.markdown("""
            * Up to 100 monitored domains
            * Real-time MCP data stream
            * Priority brand tracking
            * Memory evaluation alerts
            * Weekly vulnerability insights
            """)
        
        submitted = st.form_submit_button("Join Waitlist")
        
        if submitted:
            if not email or "@" not in email:
                st.error("Please enter a valid email address.")
            elif not company:
                st.error("Please enter your company name.")
            else:
                subscriber = {
                    "id": str(uuid.uuid4()),
                    "email": email,
                    "company": company,
                    "use_case": use_case,
                    "timestamp": datetime.datetime.now().isoformat()
                }
                
                if save_to_waitlist(subscriber):
                    st.success("Thank you for joining our waitlist! We'll be in touch soon with access details.")
                else:
                    st.info("You're already on our waitlist. We'll be in touch soon!")
    
    # Infrastructure section
    st.markdown("---")
    st.subheader("LLMRank.io Infrastructure")
    
    # System architecture diagram
    st.markdown("""
    Our Model Context Protocol (MCP) is powered by a multi-agent architecture that continuously
    monitors and maps the memory landscape across all major LLM providers, tracking how your brand
    is represented and recalled.
    """)
    
    # Show the agent matrix
    display_agent_deployment()
    
    # Show agent lifecycle
    display_agent_lifecycle()

def show_api_docs() -> None:
    """Show the API documentation."""
    st.title("LLMRank.io API Documentation")
    
    st.markdown("""
    ## Memory Context Protocol (MCP) API
    
    The MCP API provides programmatic access to LLMRank.io's trust signal intelligence layer,
    allowing you to monitor and track how brands and entities are perceived across the LLM ecosystem.
    
    ### Authentication
    
    All API requests require an API key passed in the header:
    
    ```
    api-key: mcp_your_api_key_here
    ```
    
    ### Base URL
    
    ```
    https://api.llmrank.io/api
    ```
    """)
    
    # API Endpoints
    st.subheader("API Endpoints")
    
    # Tabs for different endpoint categories
    endpoint_tabs = st.tabs(["Brands", "Categories", "Rivalries", "Insights", "Statistics"])
    
    with endpoint_tabs[0]:
        st.markdown("""
        ### Brands API
        
        Get detailed information about brands, including memory vulnerability scores, citation health, and sentiment analysis.
        
        #### GET /mcp/brands
        
        Query Parameters:
        - `domain` (optional): Filter by domain name
        - `category` (optional): Filter by category
        - `limit` (optional): Maximum number of results to return (default: 20)
        - `offset` (optional): Offset for pagination (default: 0)
        """)
        
        # Sample response
        sample_brands_response = {
            "request_id": "req_1684912345",
            "timestamp": "2025-05-22T12:34:56.789Z",
            "brands": [
                {
                    "id": "brand_123456",
                    "name": "TechCorp",
                    "domain": "techcorp.com",
                    "category": "Technology",
                    "memory_vulnerability_score": 0.32,
                    "signal_strength": 0.68,
                    "last_updated": "2025-05-21T10:25:43.210Z"
                },
                {
                    "id": "brand_123457",
                    "name": "FinancePro",
                    "domain": "financepro.com",
                    "category": "Finance",
                    "memory_vulnerability_score": 0.41,
                    "signal_strength": 0.59,
                    "last_updated": "2025-05-21T11:32:18.654Z"
                }
            ],
            "count": 2
        }
        
        display_api_response(
            "Example Request & Response: Get Technology Brands",
            """
import requests

api_key = "mcp_your_api_key_here"
url = "https://api.llmrank.io/api/mcp/brands"

params = {
    "category": "Technology",
    "limit": 10
}

headers = {
    "api-key": api_key
}

response = requests.get(url, params=params, headers=headers)
data = response.json()
            """,
            sample_brands_response
        )
    
    with endpoint_tabs[1]:
        st.markdown("""
        ### Categories API
        
        Get detailed information about categories, including brands, competitive landscape, and memory vulnerability distribution.
        
        #### GET /mcp/categories/{category}
        
        Path Parameters:
        - `category`: Category name (e.g., "Technology", "Finance", "Healthcare")
        """)
        
        # Sample response
        sample_categories_response = {
            "request_id": "req_1684912346",
            "timestamp": "2025-05-22T12:34:57.789Z",
            "category": {
                "name": "Technology",
                "brand_count": 25,
                "avg_memory_vulnerability": 0.38,
                "top_brands": [
                    {"name": "TechCorp", "domain": "techcorp.com", "memory_vulnerability_score": 0.32},
                    {"name": "InnovationHub", "domain": "innovationhub.com", "memory_vulnerability_score": 0.34}
                ],
                "memory_distribution": {
                    "low_risk": 8,
                    "medium_risk": 12,
                    "high_risk": 5
                }
            }
        }
        
        display_api_response(
            "Example Request & Response: Get Technology Category",
            """
import requests

api_key = "mcp_your_api_key_here"
url = "https://api.llmrank.io/api/mcp/categories/Technology"

headers = {
    "api-key": api_key
}

response = requests.get(url, headers=headers)
data = response.json()
            """,
            sample_categories_response
        )
    
    with endpoint_tabs[2]:
        st.markdown("""
        ### Rivalries API
        
        Get information about competitive rivalries between brands, including signal differential, movement trends, and citation overlap.
        
        #### GET /mcp/rivalries
        
        Query Parameters:
        - `category` (optional): Filter by category
        - `min_delta` (optional): Minimum delta between rivals to include
        - `limit` (optional): Maximum number of results to return (default: 20)
        - `offset` (optional): Offset for pagination (default: 0)
        """)
        
        # Sample response
        sample_rivalries_response = {
            "request_id": "req_1684912347",
            "timestamp": "2025-05-22T12:34:58.789Z",
            "rivalries": [
                {
                    "id": "rivalry_123456",
                    "category": "Technology",
                    "top_brand": {
                        "name": "TechCorp",
                        "domain": "techcorp.com",
                        "signal": 0.68
                    },
                    "laggard_brand": {
                        "name": "TechRival",
                        "domain": "techrival.com",
                        "signal": 0.54
                    },
                    "delta": 0.14,
                    "trend": "widening",
                    "citation_overlap": 0.32,
                    "outcite_ready": True
                }
            ],
            "count": 1,
            "total": 8
        }
        
        display_api_response(
            "Example Request & Response: Get Technology Rivalries",
            """
import requests

api_key = "mcp_your_api_key_here"
url = "https://api.llmrank.io/api/mcp/rivalries"

params = {
    "category": "Technology",
    "min_delta": 0.1
}

headers = {
    "api-key": api_key
}

response = requests.get(url, params=params, headers=headers)
data = response.json()
            """,
            sample_rivalries_response
        )
    
    with endpoint_tabs[3]:
        st.markdown("""
        ### Insights API
        
        Get actionable insights generated by the LLMRank.io system, including memory vulnerability alerts, competitive shifts, and trend analysis.
        
        #### GET /mcp/insights
        
        Query Parameters:
        - `domain` (optional): Filter by domain
        - `category` (optional): Filter by category
        - `type` (optional): Filter by insight type (e.g., "vulnerability_alert", "competitive_shift")
        - `limit` (optional): Maximum number of results to return (default: 20)
        - `offset` (optional): Offset for pagination (default: 0)
        """)
        
        # Sample response
        sample_insights_response = {
            "request_id": "req_1684912348",
            "timestamp": "2025-05-22T12:34:59.789Z",
            "insights": [
                {
                    "id": "insight_123456",
                    "domain": "techcorp.com",
                    "category": "Technology",
                    "title": "Signal strength differential detected",
                    "content": "Brand signal strength for TechCorp is 0.68, showing a positive differential of 0.14 compared to TechRival.",
                    "timestamp": "2025-05-21T15:23:41.654Z",
                    "type": "signal_differential"
                },
                {
                    "id": "insight_123457",
                    "domain": "techcorp.com",
                    "category": "Technology",
                    "title": "Memory vulnerability analysis",
                    "content": "TechCorp has a memory vulnerability score of 0.32, placing it in the low risk category.",
                    "timestamp": "2025-05-21T15:23:42.123Z",
                    "type": "memory_vulnerability"
                }
            ],
            "count": 2
        }
        
        display_api_response(
            "Example Request & Response: Get Insights for TechCorp",
            """
import requests

api_key = "mcp_your_api_key_here"
url = "https://api.llmrank.io/api/mcp/insights"

params = {
    "domain": "techcorp.com",
    "limit": 10
}

headers = {
    "api-key": api_key
}

response = requests.get(url, params=params, headers=headers)
data = response.json()
            """,
            sample_insights_response
        )
    
    with endpoint_tabs[4]:
        st.markdown("""
        ### Statistics API
        
        Get system-wide statistics about the LLMRank.io platform, including brand counts, category breakdowns, and agent activity.
        
        #### GET /mcp/statistics
        """)
        
        # Sample response
        sample_statistics_response = {
            "timestamp": "2025-05-22T12:35:00.789Z",
            "brand_count": 1250,
            "category_count": 32,
            "rivalry_count": 843,
            "categories": {
                "Technology": 215,
                "Finance": 187,
                "Healthcare": 156,
                "Retail": 142,
                "Media": 121,
                "Automotive": 98,
                "Other": 331
            },
            "agent_activity": {
                "active_agents": 35,
                "scans_today": 4532,
                "insights_generated": 218
            }
        }
        
        display_api_response(
            "Example Request & Response: Get System Statistics",
            """
import requests

api_key = "mcp_your_api_key_here"
url = "https://api.llmrank.io/api/mcp/statistics"

headers = {
    "api-key": api_key
}

response = requests.get(url, headers=headers)
data = response.json()
            """,
            sample_statistics_response
        )
    
    # Rate limits
    st.markdown("---")
    st.subheader("Rate Limits")
    
    st.markdown("""
    The MCP API has rate limits to ensure fair usage and system stability. Rate limits vary by subscription tier:
    
    | Tier | Requests per Minute | Requests per Day |
    |------|---------------------|------------------|
    | Free | 10 | 1,000 |
    | Basic | 60 | 10,000 |
    | Pro | 300 | 100,000 |
    | Enterprise | 1,000 | Unlimited |
    
    Rate limit headers are included in all API responses:
    
    ```
    X-RateLimit-Limit: 60
    X-RateLimit-Remaining: 58
    X-RateLimit-Reset: 1684912400
    ```
    """)
    
    # Join waitlist
    st.markdown("---")
    
    st.warning("This API is currently in private beta. Join our waitlist to get access.")
    
    if st.button("Join Waitlist for API Access"):
        st.session_state["page"] = "landing"

def show_technology() -> None:
    """Show the technology page."""
    st.title("LLMRank.io Technology")
    
    st.markdown("""
    ## The Memory Context Protocol (MCP)
    
    The Memory Context Protocol (MCP) is the core technology behind LLMRank.io. It powers
    our ability to monitor, track, and influence how AI systems perceive brands and entities
    across the digital ecosystem.
    
    ### Agent Architecture
    
    LLMRank.io's MCP is powered by a multi-agent system that continuously scans, analyzes,
    and monitors the digital ecosystem. Our agents operate in a complex hierarchical structure,
    each with specialized roles:
    """)
    
    # Agent descriptions in 3 columns
    col1, col2, col3 = st.columns(3)
    
    with col1:
        st.markdown("#### IndexScan Agents")
        st.markdown("""
        * Rapidly survey large brand categories
        * Identify entity relationships
        * Map competitive landscapes
        * Track domain reputation signals
        """)
    
    with col2:
        st.markdown("#### SurfaceSeed Agents")
        st.markdown("""
        * Deep-dive brand analysis
        * Memory imprint evaluation
        * Sentiment context tracking
        * Citation verification
        """)
    
    with col3:
        st.markdown("#### DriftPulse Agents")
        st.markdown("""
        * Detect memory drift patterns
        * Monitor citation chain health
        * Identify vulnerability windows
        * Track competitive signal shifts
        """)
    
    # Agent deployment visualization
    display_agent_deployment()
    
    # Agent lifecycle
    st.subheader("Agent Runtime Lifecycle")
    st.markdown("""
    Our agents operate in continuous cycles of scanning, processing, and insight generation.
    Each agent's lifecycle is carefully orchestrated to ensure comprehensive coverage while
    maximizing efficiency.
    """)
    
    display_agent_lifecycle()
    
    # Technical architecture
    st.subheader("Technical Architecture")
    
    st.markdown("""
    The LLMRank.io platform is built on a sophisticated technical architecture designed for
    scalability, reliability, and real-time performance:
    
    * **High-Performance API Layer**: Built with FastAPI, our API layer handles thousands of
      requests per second with minimal latency.
    
    * **Advanced Caching System**: Multi-level caching ensures rapid response times for
      frequently requested data.
    
    * **Distributed Agent Framework**: Our agents operate in a distributed environment,
      allowing for parallel processing and horizontal scaling.
    
    * **Real-time Analytics Pipeline**: Stream processing enables immediate insight
      generation and alerting.
    
    * **Secure Authentication**: Enterprise-grade security with API key management,
      rate limiting, and access controls.
    """)
    
    # Memory Vulnerability Score explanation
    st.subheader("Memory Vulnerability Score (MVS)")
    
    st.markdown("""
    The Memory Vulnerability Score (MVS) is our proprietary metric for measuring how
    vulnerable a brand's memory is across large language models. It incorporates:
    
    1. **Signal Strength**: How strongly the brand is remembered
    2. **Citation Quality**: The health of citation chains referencing the brand
    3. **Context Integrity**: How accurately the brand's context is preserved
    4. **Competitive Position**: Relative strength compared to competitors
    5. **Sentiment Volatility**: Stability of sentiment across different contexts
    
    Lower MVS scores indicate less vulnerability (stronger memory position), while
    higher scores indicate greater vulnerability (weaker memory position).
    """)
    
    # Create a scatter plot of example MVS scores
    companies = [
        "TechCorp", "FinancePro", "HealthPlus", "RetailGiant", 
        "MediaStream", "AutoDrive", "FoodFresh", "TravelEase",
        "EduLearn", "EnergyPower"
    ]
    mvs_scores = [0.32, 0.41, 0.38, 0.51, 0.29, 0.44, 0.63, 0.47, 0.35, 0.58]
    signal_strength = [1.0 - score for score in mvs_scores]
    
    df = pd.DataFrame({
        "Company": companies,
        "MVS": mvs_scores,
        "Signal Strength": signal_strength
    })
    
    fig = px.scatter(
        df, 
        x="MVS", 
        y="Signal Strength", 
        color="MVS",
        size="Signal Strength",
        hover_name="Company",
        color_continuous_scale="RdYlGn_r",
        title="Sample Memory Vulnerability Scores",
        labels={"MVS": "Memory Vulnerability Score (Lower is Better)"}
    )
    
    fig.update_layout(
        height=400,
        margin=dict(l=20, r=20, t=40, b=20),
    )
    
    st.plotly_chart(fig, use_container_width=True)
    
    # Join waitlist
    st.markdown("---")
    
    st.info("Our technology is currently available to select partners through our API. Join our waitlist to get access.")
    
    if st.button("Join Waitlist for Access", key="tech_waitlist"):
        st.session_state["page"] = "landing"

def show_use_cases() -> None:
    """Show the use cases page."""
    st.title("LLMRank.io Use Cases")
    
    st.markdown("""
    ## How Businesses Use the Memory Context Protocol
    
    The LLMRank.io API enables a wide range of use cases across different industries
    and business functions. Here are some of the ways our clients are leveraging
    our technology:
    """)
    
    # Use case tabs
    use_case_tabs = st.tabs([
        "Brand Protection", 
        "Competitive Intelligence", 
        "Market Research",
        "Product Development",
        "Risk Management"
    ])
    
    with use_case_tabs[0]:
        st.markdown("### Brand Protection")
        
        st.markdown("""
        **Challenge**: Brands are vulnerable to misrepresentation in AI systems, leading to
        potential damage to reputation and customer trust.
        
        **Solution**: LLMRank.io's MCP API provides real-time monitoring of brand memory
        vulnerability across the AI ecosystem, enabling proactive protection.
        
        **Implementation**:
        * Continuous monitoring of Memory Vulnerability Score (MVS)
        * Alerts for significant changes in brand representation
        * Detection of harmful context associations
        * Identification of citation chain weaknesses
        
        **Results**:
        * 78% reduction in brand memory vulnerabilities
        * 23% improvement in brand sentiment consistency
        * 45% faster response to emerging misrepresentations
        """)
        
        # Sample brand protection visualization
        df = pd.DataFrame({
            "Week": list(range(1, 11)),
            "MVS": [0.65, 0.62, 0.58, 0.55, 0.49, 0.46, 0.42, 0.39, 0.36, 0.34],
            "Intervention": ["None", "None", "None", "Citation Repair", "None", 
                            "Memory Reinforcement", "None", "None", "Context Enhancement", "None"]
        })
        
        fig = px.line(
            df, 
            x="Week", 
            y="MVS", 
            title="Brand Memory Vulnerability Reduction Over Time",
            markers=True
        )
        
        for i, row in df.iterrows():
            if row["Intervention"] != "None":
                fig.add_annotation(
                    x=row["Week"],
                    y=row["MVS"],
                    text=row["Intervention"],
                    showarrow=True,
                    arrowhead=1,
                    ax=0,
                    ay=-40
                )
        
        fig.update_layout(
            height=400,
            margin=dict(l=20, r=20, t=40, b=20),
            yaxis_title="Memory Vulnerability Score (Lower is Better)",
        )
        
        st.plotly_chart(fig, use_container_width=True)
    
    with use_case_tabs[1]:
        st.markdown("### Competitive Intelligence")
        
        st.markdown("""
        **Challenge**: Understanding how competitors are perceived in AI systems provides
        crucial intelligence for strategic decision-making.
        
        **Solution**: LLMRank.io's MCP API provides detailed analysis of competitive
        landscapes, including signal differentials and memory vulnerability comparisons.
        
        **Implementation**:
        * Tracking of competitive signal differentials
        * Identification of memory vulnerability gaps
        * Analysis of citation overlaps and unique citations
        * Monitoring of competitive movement trends
        
        **Results**:
        * 52% more accurate competitive positioning insights
        * 31% improvement in strategic response effectiveness
        * 18% increase in market share for brands using competitive intelligence
        """)
        
        # Sample competitive intelligence visualization
        categories = ["Product Features", "Innovation", "Customer Service", 
                    "Reliability", "Value", "Market Presence"]
        
        company_a = [0.82, 0.78, 0.65, 0.71, 0.69, 0.77]
        company_b = [0.75, 0.85, 0.72, 0.68, 0.76, 0.71]
        
        fig = go.Figure()
        
        fig.add_trace(go.Scatterpolar(
            r=company_a,
            theta=categories,
            fill='toself',
            name='Your Brand'
        ))
        
        fig.add_trace(go.Scatterpolar(
            r=company_b,
            theta=categories,
            fill='toself',
            name='Competitor'
        ))
        
        fig.update_layout(
            polar=dict(
                radialaxis=dict(
                    visible=True,
                    range=[0, 1]
                )
            ),
            showlegend=True,
            title="Competitive Signal Strength Comparison",
            height=500
        )
        
        st.plotly_chart(fig, use_container_width=True)
    
    with use_case_tabs[2]:
        st.markdown("### Market Research")
        
        st.markdown("""
        **Challenge**: Traditional market research methods can be slow, expensive, and limited
        in scope, missing important AI perception factors.
        
        **Solution**: LLMRank.io's MCP API provides real-time insight into how brands and
        categories are perceived across the AI ecosystem.
        
        **Implementation**:
        * Category-wide analysis of brand perceptions
        * Identification of emerging category trends
        * Discovery of brand association patterns
        * Analysis of sentiment landscapes
        
        **Results**:
        * 63% faster market insights compared to traditional research
        * 42% more comprehensive view of brand perceptions
        * 28% cost reduction in market research operations
        """)
        
        # Sample market research visualization
        market_data = [
            {"Category": "Technology", "Brand Count": 215, "Avg MVS": 0.38, "Growth": 12.5},
            {"Category": "Finance", "Brand Count": 187, "Avg MVS": 0.42, "Growth": 8.3},
            {"Category": "Healthcare", "Brand Count": 156, "Avg MVS": 0.44, "Growth": 15.7},
            {"Category": "Retail", "Brand Count": 142, "Avg MVS": 0.47, "Growth": 5.2},
            {"Category": "Media", "Brand Count": 121, "Avg MVS": 0.35, "Growth": 18.9},
            {"Category": "Automotive", "Brand Count": 98, "Avg MVS": 0.51, "Growth": 3.8}
        ]
        
        df = pd.DataFrame(market_data)
        
        fig = px.scatter(
            df, 
            x="Avg MVS", 
            y="Growth", 
            size="Brand Count",
            color="Category",
            hover_name="Category",
            text="Category",
            title="Category Growth vs. Memory Vulnerability"
        )
        
        fig.update_traces(textposition='top center')
        
        fig.update_layout(
            height=500,
            xaxis_title="Average Memory Vulnerability Score (Lower is Better)",
            yaxis_title="Category Growth Rate (%)"
        )
        
        st.plotly_chart(fig, use_container_width=True)
    
    with use_case_tabs[3]:
        st.markdown("### Product Development")
        
        st.markdown("""
        **Challenge**: Understanding how products are perceived in AI systems can inform
        product development strategies and positioning.
        
        **Solution**: LLMRank.io's MCP API provides detailed analysis of product attributes
        and feature perceptions across the AI ecosystem.
        
        **Implementation**:
        * Analysis of product feature perceptions
        * Identification of product differentiation opportunities
        * Monitoring of product category trends
        * Tracking of product sentiment across use cases
        
        **Results**:
        * 37% more effective product positioning
        * 25% reduction in product launch risks
        * 19% higher customer satisfaction with new features
        """)
        
        # Sample product development visualization
        product_data = [
            {"Product": "Product A", "Feature": "Speed", "Perception": 0.85},
            {"Product": "Product A", "Feature": "Reliability", "Perception": 0.78},
            {"Product": "Product A", "Feature": "Design", "Perception": 0.92},
            {"Product": "Product A", "Feature": "Value", "Perception": 0.65},
            {"Product": "Product A", "Feature": "Support", "Perception": 0.71},
            {"Product": "Product B", "Feature": "Speed", "Perception": 0.91},
            {"Product": "Product B", "Feature": "Reliability", "Perception": 0.82},
            {"Product": "Product B", "Feature": "Design", "Perception": 0.75},
            {"Product": "Product B", "Feature": "Value", "Perception": 0.88},
            {"Product": "Product B", "Feature": "Support", "Perception": 0.69}
        ]
        
        df = pd.DataFrame(product_data)
        
        fig = px.bar(
            df, 
            x="Feature", 
            y="Perception", 
            color="Product", 
            barmode="group",
            title="Product Feature Perception Comparison"
        )
        
        fig.update_layout(
            height=400,
            yaxis_title="Feature Perception Strength",
            yaxis=dict(range=[0, 1])
        )
        
        st.plotly_chart(fig, use_container_width=True)
    
    with use_case_tabs[4]:
        st.markdown("### Risk Management")
        
        st.markdown("""
        **Challenge**: AI systems can introduce new risks to brand reputation and
        market position that traditional risk management approaches miss.
        
        **Solution**: LLMRank.io's MCP API provides continuous monitoring of brand
        vulnerabilities and potential risks across the AI ecosystem.
        
        **Implementation**:
        * Real-time monitoring of memory vulnerability spikes
        * Detection of emerging negative associations
        * Identification of citation chain vulnerabilities
        * Tracking of competitive threat patterns
        
        **Results**:
        * 68% faster detection of emerging brand risks
        * 43% reduction in negative impact from AI misrepresentations
        * 34% improvement in risk mitigation response times
        """)
        
        # Sample risk management visualization
        risk_data = [
            {"Date": "2025-01-01", "MVS": 0.38, "Alert Threshold": 0.50, "Risk Event": None},
            {"Date": "2025-01-15", "MVS": 0.41, "Alert Threshold": 0.50, "Risk Event": None},
            {"Date": "2025-02-01", "MVS": 0.39, "Alert Threshold": 0.50, "Risk Event": None},
            {"Date": "2025-02-15", "MVS": 0.45, "Alert Threshold": 0.50, "Risk Event": None},
            {"Date": "2025-03-01", "MVS": 0.58, "Alert Threshold": 0.50, "Risk Event": "Negative News Coverage"},
            {"Date": "2025-03-15", "MVS": 0.63, "Alert Threshold": 0.50, "Risk Event": "Citation Chain Break"},
            {"Date": "2025-04-01", "MVS": 0.52, "Alert Threshold": 0.50, "Risk Event": "Mitigation Started"},
            {"Date": "2025-04-15", "MVS": 0.48, "Alert Threshold": 0.50, "Risk Event": None},
            {"Date": "2025-05-01", "MVS": 0.42, "Alert Threshold": 0.50, "Risk Event": None},
            {"Date": "2025-05-15", "MVS": 0.39, "Alert Threshold": 0.50, "Risk Event": None}
        ]
        
        df = pd.DataFrame(risk_data)
        
        fig = px.line(
            df, 
            x="Date", 
            y=["MVS", "Alert Threshold"], 
            title="Risk Event Detection and Response",
            markers=True
        )
        
        # Add annotations for risk events
        for i, row in df.iterrows():
            if row["Risk Event"] is not None:
                fig.add_annotation(
                    x=row["Date"],
                    y=row["MVS"],
                    text=row["Risk Event"],
                    showarrow=True,
                    arrowhead=1,
                    ax=0,
                    ay=-40
                )
        
        fig.update_layout(
            height=400,
            yaxis_title="Memory Vulnerability Score",
            yaxis=dict(range=[0, 0.7])
        )
        
        st.plotly_chart(fig, use_container_width=True)
    
    # Join waitlist
    st.markdown("---")
    
    st.success("These use cases represent just a few of the ways our clients are leveraging the LLMRank.io MCP API.")
    
    if st.button("Join Waitlist for Access", key="usecase_waitlist"):
        st.session_state["page"] = "landing"

def setup_page() -> None:
    """Set up the page."""
    # Set page config
    st.set_page_config(
        page_title=SITE_TITLE,
        page_icon=PAGE_ICON,
        layout="wide",
        initial_sidebar_state="expanded"
    )
    
    # Add custom CSS
    st.markdown("""
    <style>
    a {
        color: #4F8BF9 !important;
    }
    .stButton>button {
        color: white;
        background-color: #4F8BF9;
        border: none;
        border-radius: 4px;
        padding: 0.5rem 1rem;
    }
    .stButton>button:hover {
        background-color: #3A7AD5;
    }
    </style>
    """, unsafe_allow_html=True)

def main() -> None:
    """Main function."""
    setup_page()
    
    # Initialize session state for navigation
    if "page" not in st.session_state:
        st.session_state["page"] = "landing"
    
    # Sidebar navigation
    with st.sidebar:
        st.title("LLMRank.io")
        st.markdown("### Memory Context Protocol")
        
        if st.button("🏠 Home"):
            st.session_state["page"] = "landing"
        
        if st.button("📚 API Documentation"):
            st.session_state["page"] = "api_docs"
        
        if st.button("🔬 Technology"):
            st.session_state["page"] = "technology"
        
        if st.button("📊 Use Cases"):
            st.session_state["page"] = "use_cases"
        
        st.markdown("---")
        
        # Waitlist join button
        if st.button("✉️ Join Waitlist", key="sidebar_waitlist"):
            st.session_state["page"] = "landing"
        
        # Contact information
        st.markdown("### Contact")
        st.markdown("📧 contact@llmrank.io")
        
        # Footer
        st.markdown("---")
        st.markdown("© 2025 LLMRank.io")
        st.markdown("All Rights Reserved")
    
    # Display the selected page
    if st.session_state["page"] == "landing":
        show_landing_page()
    elif st.session_state["page"] == "api_docs":
        show_api_docs()
    elif st.session_state["page"] == "technology":
        show_technology()
    elif st.session_state["page"] == "use_cases":
        show_use_cases()

if __name__ == "__main__":
    main()