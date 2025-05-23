"""
Sentinel Dashboard

This dashboard provides a user interface for the Sentinel Loop system,
showing MISS scores, domain influence, and tier-based features.
"""

import os
import json
import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from datetime import datetime, timedelta
import random

import miss_score_calculator
import subscription_tier

# Page configuration
st.set_page_config(
    page_title="Sentinel Dashboard",
    page_icon="🔍",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom styling
st.markdown("""
<style>
    .main-header {
        font-size: 2.5rem;
        font-weight: 700;
        margin-bottom: 0.5rem;
        color: #1E3A8A;
    }
    .sub-header {
        font-size: 1.5rem;
        font-weight: 500;
        margin-bottom: 1rem;
        color: #1E293B;
    }
    .tier-card {
        background-color: #F8FAFC;
        border-radius: 8px;
        padding: 1.5rem;
        margin-bottom: 1rem;
        border-left: 4px solid #3B82F6;
    }
    .tier-card.free {
        border-left-color: #60A5FA;
    }
    .tier-card.pro {
        border-left-color: #3B82F6;
    }
    .tier-card.growth {
        border-left-color: #8B5CF6;
    }
    .tier-card.enterprise {
        border-left-color: #1D4ED8;
    }
    .card-header {
        font-size: 1.25rem;
        font-weight: 600;
        margin-bottom: 0.5rem;
    }
    .card-content {
        font-size: 1rem;
        margin-bottom: 1rem;
    }
    .feature-available {
        color: #047857;
        font-weight: 500;
    }
    .feature-locked {
        color: #6B7280;
        font-style: italic;
    }
    .miss-score {
        font-size: 3rem;
        font-weight: 700;
        color: #1D4ED8;
    }
    .upgrade-box {
        background-color: #EFF6FF;
        border: 1px solid #BFDBFE;
        border-radius: 8px;
        padding: 1rem;
        margin: 1rem 0;
    }
    .upgrade-title {
        font-size: 1.1rem;
        font-weight: 600;
        color: #1E40AF;
        margin-bottom: 0.5rem;
    }
</style>
""", unsafe_allow_html=True)

# Initialize session state
if "user_id" not in st.session_state:
    st.session_state.user_id = "test"  # Default test user

if "active_tab" not in st.session_state:
    st.session_state.active_tab = "miss_score"
    
if "domain" not in st.session_state:
    st.session_state.domain = "techcrunch.com"
    
if "show_upgrade" not in st.session_state:
    st.session_state.show_upgrade = False

def get_user_data():
    """Get current user data."""
    user_id = st.session_state.user_id
    return subscription_tier.get_user(user_id)

def check_feature_access(feature):
    """Check if current user has access to a feature."""
    user_id = st.session_state.user_id
    return subscription_tier.check_feature_access(user_id, feature)

def show_login_form():
    """Show login form."""
    st.markdown("<div class='main-header'>Sentinel Login</div>", unsafe_allow_html=True)
    
    col1, col2 = st.columns([1, 1])
    
    with col1:
        # Login form
        st.markdown("### Login")
        user_id = st.text_input("User ID", value="test")
        login = st.button("Login")
        
        if login:
            user = subscription_tier.get_user(user_id)
            if user:
                st.session_state.user_id = user_id
                st.success(f"Logged in as {user['name']}")
                st.rerun()
            else:
                st.error("User not found")
    
    with col2:
        # Registration form
        st.markdown("### Register")
        name = st.text_input("Name")
        email = st.text_input("Email")
        tier = st.selectbox("Tier", ["free", "pro", "growth", "enterprise"], index=0)
        
        register = st.button("Register")
        
        if register:
            try:
                user = subscription_tier.create_user(name, email, tier)
                st.session_state.user_id = user["user_id"]
                st.success(f"Registered as {user['name']}")
                st.rerun()
            except ValueError as e:
                st.error(f"Registration failed: {e}")

def show_upgrade_box():
    """Show upgrade recommendations box."""
    if not st.session_state.show_upgrade:
        return
    
    user_id = st.session_state.user_id
    user = subscription_tier.get_user(user_id)
    
    if not user:
        return
    
    recommendations = subscription_tier.get_upgrade_recommendations(user_id)
    
    if not recommendations:
        return
    
    rec = recommendations[0]
    
    st.markdown(
        f"""
        <div class="upgrade-box">
            <div class="upgrade-title">🚀 Upgrade to {rec['name']}</div>
            <p>{rec['message']}</p>
            <ul>
                {"".join([f"<li>{feature}</li>" for feature in rec['new_features'][:3]])}
                {f"<li>...and {len(rec['new_features']) - 3} more</li>" if len(rec['new_features']) > 3 else ""}
            </ul>
        </div>
        """,
        unsafe_allow_html=True
    )
    
    col1, col2 = st.columns([3, 1])
    
    with col2:
        upgrade = st.button("Upgrade Now")
        
        if upgrade:
            try:
                subscription_tier.update_user_tier(user_id, rec["tier"])
                st.success(f"Upgraded to {rec['name']} tier")
                st.session_state.show_upgrade = False
                st.rerun()
            except ValueError as e:
                st.error(f"Upgrade failed: {e}")

def show_miss_score_tab():
    """Show MISS score tab."""
    st.markdown("<div class='sub-header'>Model Influence Signal Score (MISS)</div>", unsafe_allow_html=True)
    
    user = get_user_data()
    if not user:
        st.error("User data not found")
        return
    
    col1, col2 = st.columns([2, 1])
    
    with col1:
        domains = user.get("domains", [])
        if not domains:
            domains = ["techcrunch.com", "wired.com", "theverge.com"]
        
        selected_domain = st.selectbox("Select Domain", domains)
        st.session_state.domain = selected_domain
        
        # Calculate MISS score
        score_data = miss_score_calculator.calculate_miss_score(selected_domain)
        miss_score = score_data["miss_score"]
        
        # Show score
        st.markdown(f"<div class='miss-score'>{miss_score}</div>", unsafe_allow_html=True)
        st.markdown(f"**Last Updated:** {datetime.now().strftime('%Y-%m-%d %H:%M')}")
        
        # Show components if Pro or higher
        if check_feature_access("signal_audit"):
            st.markdown("### Score Components")
            
            components_df = pd.DataFrame(score_data["components"])
            
            if not components_df.empty:
                # Create a component breakdown chart
                fig = px.bar(
                    components_df,
                    x="model",
                    y="component_score",
                    color="category",
                    title="MISS Score Components by Model and Category",
                    barmode="group"
                )
                
                st.plotly_chart(fig, use_container_width=True)
            else:
                st.info("No score components available for this domain")
        else:
            # Show upgrade message
            st.info("⭐ Upgrade to Pro tier to see score components and detailed analysis")
            if st.button("Learn More", key="learn_more_components"):
                st.session_state.show_upgrade = True
                st.rerun()
    
    with col2:
        # Tier info
        tier = user["tier"]
        tier_data = subscription_tier.get_tier_features(tier)
        
        st.markdown(
            f"""
            <div class="tier-card {tier}">
                <div class="card-header">Your tier: {tier.capitalize()}</div>
                <div class="card-content">
                    Domains: {len(user.get("domains", []))}/{subscription_tier.get_tier_limits(tier)["domains"]}
                </div>
            </div>
            """,
            unsafe_allow_html=True
        )
        
        # Quick stats
        st.markdown("### Quick Stats")
        
        # Get benchmarks
        benchmarks = miss_score_calculator.get_score_benchmarks()
        
        # Create metrics
        col_a, col_b = st.columns(2)
        
        with col_a:
            # Show how this score compares to average
            if benchmarks["average"] > 0:
                diff = miss_score - benchmarks["average"]
                diff_text = f"{diff:+.1f}" if diff != 0 else "0"
                st.metric("vs Average", diff_text, delta_color="normal" if diff >= 0 else "inverse")
            else:
                st.metric("vs Average", "N/A")
        
        with col_b:
            # Show signal strength
            signal_strength = "Strong" if miss_score >= 75 else "Medium" if miss_score >= 50 else "Weak"
            st.metric("Signal Strength", signal_strength)
        
        # Show drift detection for Pro or higher
        if check_feature_access("score_drift_alerts"):
            st.markdown("### Score Drift")
            
            drift_data = miss_score_calculator.detect_score_drift(selected_domain)
            
            if drift_data["drift_detected"]:
                drift = drift_data["drift"]
                drift_text = f"{drift:+.1f}" if drift != 0 else "0"
                
                st.metric(
                    "Recent Change",
                    drift_text,
                    delta=f"{drift_data['drift_pct']:+.1f}%",
                    delta_color="normal" if drift >= 0 else "inverse"
                )
                
                st.info(drift_data["message"])
            else:
                st.metric("Recent Change", "0", delta="0%")
                st.info("No significant drift detected")
        else:
            st.info("⭐ Upgrade to see score drift alerts")
    
    # Show history for Pro or higher (longer history for higher tiers)
    if check_feature_access("weekly_miss_score"):
        weeks = subscription_tier.get_tier_limits(tier)["history_weeks"]
        
        st.markdown("### Score History")
        
        history_data = miss_score_calculator.get_score_history(selected_domain, weeks)
        
        if history_data and history_data.get("weekly_scores"):
            df = pd.DataFrame(history_data["weekly_scores"])
            df["timestamp"] = pd.to_datetime(df["timestamp"])
            
            # Sample some data if not enough points
            if len(df) < 3:
                # Generate some fake history data
                end_date = datetime.now()
                start_date = end_date - timedelta(days=weeks * 7)
                
                dates = []
                scores = []
                
                current_score = miss_score
                
                # Work backwards
                for i in range(weeks):
                    week_date = end_date - timedelta(days=i * 7)
                    
                    # Add some random variation
                    if i > 0:  # Keep the most recent score as is
                        variation = random.uniform(-5, 5)
                        week_score = max(0, min(100, current_score + variation))
                        current_score = week_score
                    else:
                        week_score = current_score
                    
                    dates.append(week_date)
                    scores.append(week_score)
                
                # Create dataframe
                df = pd.DataFrame({
                    "timestamp": dates,
                    "miss_score": scores
                })
            
            # Sort by timestamp
            df = df.sort_values("timestamp")
            
            # Create line chart
            fig = px.line(
                df,
                x="timestamp",
                y="miss_score",
                title=f"MISS Score History ({weeks} weeks)",
                labels={"miss_score": "MISS Score", "timestamp": "Date"}
            )
            
            # Add markers for each data point
            fig.update_traces(mode="lines+markers")
            
            # Add reference line for average
            if benchmarks["average"] > 0:
                fig.add_hline(
                    y=benchmarks["average"],
                    line_dash="dash",
                    line_color="gray",
                    annotation_text="Average",
                    annotation_position="bottom right"
                )
            
            st.plotly_chart(fig, use_container_width=True)
        else:
            st.info("No score history available for this domain")
    else:
        st.info("⭐ Upgrade to see score history")
    
    # Show recommendations
    show_upgrade_box()

def show_benchmarking_tab():
    """Show competitive benchmarking tab."""
    st.markdown("<div class='sub-header'>Competitive Benchmarking</div>", unsafe_allow_html=True)
    
    # Check if user has access to competitive benchmarking
    if not check_feature_access("competitive_benchmarking"):
        st.markdown(
            """
            <div class="tier-card">
                <div class="card-header">💎 Growth Tier Feature</div>
                <div class="card-content">
                    Competitive benchmarking allows you to compare your domains against competitors
                    and industry benchmarks. Upgrade to Growth tier to access this feature.
                </div>
            </div>
            """,
            unsafe_allow_html=True
        )
        
        if st.button("Upgrade to Growth Tier"):
            user_id = st.session_state.user_id
            subscription_tier.update_user_tier(user_id, "growth")
            st.success("Upgraded to Growth tier!")
            st.rerun()
        
        return
    
    user = get_user_data()
    domains = user.get("domains", [])
    
    if not domains:
        st.warning("No domains added to your account. Please add domains to use this feature.")
        return
    
    # Category selection
    categories = [
        "Technology", "Finance", "Healthcare", "Education", 
        "Entertainment", "Travel", "News", "Shopping"
    ]
    
    selected_category = st.selectbox("Select Category", categories)
    
    col1, col2 = st.columns([2, 1])
    
    with col1:
        # Get benchmarks for category
        benchmarks = miss_score_calculator.get_score_benchmarks(selected_category)
        
        # Calculate scores for user domains
        domain_scores = []
        
        for domain in domains:
            try:
                score_data = miss_score_calculator.calculate_miss_score(
                    domain, categories=[selected_category]
                )
                domain_scores.append({
                    "domain": domain,
                    "miss_score": score_data["miss_score"]
                })
            except Exception as e:
                st.error(f"Error calculating score for {domain}: {e}")
        
        # Add industry benchmarks
        benchmark_records = [
            {"domain": "Industry Average", "miss_score": benchmarks["average"]},
            {"domain": "Top Quartile", "miss_score": benchmarks["top_quartile"]},
            {"domain": "Median", "miss_score": benchmarks["median"]}
        ]
        
        # Create dataframe
        df = pd.DataFrame(domain_scores + benchmark_records)
        
        # Add domain type column
        df["domain_type"] = df["domain"].apply(
            lambda d: "Your Domain" if d in domains else "Benchmark"
        )
        
        # Sort by score
        df = df.sort_values("miss_score", ascending=False)
        
        # Create bar chart
        fig = px.bar(
            df,
            x="domain",
            y="miss_score",
            color="domain_type",
            title=f"MISS Score Comparison for {selected_category}",
            labels={"miss_score": "MISS Score", "domain": "Domain"},
            color_discrete_map={"Your Domain": "#3B82F6", "Benchmark": "#9CA3AF"}
        )
        
        # Customize bar chart
        fig.update_layout(xaxis_tickangle=-45)
        
        st.plotly_chart(fig, use_container_width=True)
    
    with col2:
        st.markdown("### Benchmark Summary")
        
        # Show benchmark metrics
        st.metric("Industry Average", f"{benchmarks['average']:.1f}")
        st.metric("Top Quartile", f"{benchmarks['top_quartile']:.1f}")
        st.metric("Median", f"{benchmarks['median']:.1f}")
        
        st.info(f"Based on data from {benchmarks['count']} domains in the {selected_category} category.")
        
        # Add insights based on data
        if domain_scores:
            best_domain = max(domain_scores, key=lambda x: x["miss_score"])
            avg_score = sum(d["miss_score"] for d in domain_scores) / len(domain_scores)
            
            above_avg = sum(1 for d in domain_scores if d["miss_score"] > benchmarks["average"])
            above_avg_pct = above_avg / len(domain_scores) * 100
            
            st.markdown("### Your Performance")
            st.metric("Your Average", f"{avg_score:.1f}")
            st.metric("Best Domain", f"{best_domain['domain']} ({best_domain['miss_score']})")
            st.metric("Above Industry Avg", f"{above_avg}/{len(domain_scores)} ({above_avg_pct:.1f}%)")

def show_insight_preview_tab():
    """Show insight preview tab."""
    st.markdown("<div class='sub-header'>Insight Preview</div>", unsafe_allow_html=True)
    
    # Check if user has access to insight preview
    if not check_feature_access("insight_preview"):
        st.markdown(
            """
            <div class="tier-card">
                <div class="card-header">💎 Pro Tier Feature</div>
                <div class="card-content">
                    Insight preview allows you to see drafted insights based on your domain's
                    MISS score and influence data. Upgrade to Pro tier to access this feature.
                </div>
            </div>
            """,
            unsafe_allow_html=True
        )
        
        if st.button("Upgrade to Pro Tier"):
            user_id = st.session_state.user_id
            subscription_tier.update_user_tier(user_id, "pro")
            st.success("Upgraded to Pro tier!")
            st.rerun()
        
        return
    
    user = get_user_data()
    selected_domain = st.session_state.domain
    
    # Show insight preview
    st.markdown(f"### Generated Insights for {selected_domain}")
    
    # Generate some example insights based on the domain
    insights = [
        {
            "title": f"MISS Score Trend Analysis for {selected_domain}",
            "summary": f"{selected_domain} has shown a 12% increase in model influence over the past 4 weeks, outperforming 78% of domains in its category.",
            "confidence": 0.88
        },
        {
            "title": f"Contextual Relevance Gap for {selected_domain}",
            "summary": f"While {selected_domain} has strong citation confidence (0.92), its contextual relevance is lower (0.76), suggesting an opportunity to improve content semantic structure.",
            "confidence": 0.82
        },
        {
            "title": f"Model Divergence Signal for {selected_domain}",
            "summary": f"{selected_domain} shows 23% higher influence in GPT-4o compared to Claude-3-Opus, indicating a potential model-specific optimization opportunity.",
            "confidence": 0.75
        }
    ]
    
    # Show insights in tabs
    insight_tabs = st.tabs([f"Insight {i+1}" for i in range(len(insights))])
    
    for i, (tab, insight) in enumerate(zip(insight_tabs, insights)):
        with tab:
            st.markdown(f"#### {insight['title']}")
            st.markdown(insight['summary'])
            
            col1, col2 = st.columns([3, 1])
            
            with col1:
                st.progress(insight['confidence'], text=f"Confidence: {insight['confidence']:.0%}")
            
            with col2:
                # Only show publish button for Growth tier or higher
                if check_feature_access("publishing_step"):
                    st.button("Publish Insight", key=f"publish_{i}")
                else:
                    st.info("⭐ Upgrade to Growth tier to publish insights")
    
    # Show human override options for Pro tier or higher
    if check_feature_access("human_override"):
        st.markdown("### Human Override")
        st.text_area("Edit Insight", height=100)
        
        col1, col2 = st.columns([1, 3])
        
        with col1:
            st.button("Save Override")
        
        with col2:
            st.checkbox("Apply my edits to future insights")
    
    # Show AB testing options for Growth tier or higher
    if check_feature_access("ab_testing"):
        st.markdown("### A/B Testing")
        
        st.markdown(
            """
            Configure A/B testing for your insights to optimize for:
            - Higher engagement
            - More clicks
            - Better feedback ratings
            """
        )
        
        col1, col2 = st.columns(2)
        
        with col1:
            st.selectbox("Optimization Goal", ["Engagement", "Clicks", "Feedback"])
        
        with col2:
            st.selectbox("Test Duration", ["1 week", "2 weeks", "30 days"])
        
        st.button("Start A/B Test")

def show_platform_settings_tab():
    """Show platform settings tab."""
    st.markdown("<div class='sub-header'>Platform Settings</div>", unsafe_allow_html=True)
    
    user = get_user_data()
    tier = user["tier"]
    
    col1, col2 = st.columns([1, 1])
    
    with col1:
        st.markdown("### User Information")
        
        st.text_input("Name", value=user["name"], disabled=True)
        st.text_input("Email", value=user["email"], disabled=True)
        st.selectbox(
            "Subscription Tier",
            ["free", "pro", "growth", "enterprise"],
            index=["free", "pro", "growth", "enterprise"].index(tier)
        )
        
        st.markdown("### Domain Management")
        
        # Show current domains
        domains = user.get("domains", [])
        
        if domains:
            st.markdown("Current domains:")
            for domain in domains:
                col_a, col_b = st.columns([3, 1])
                
                with col_a:
                    st.text(domain)
                
                with col_b:
                    if st.button("Remove", key=f"remove_{domain}"):
                        subscription_tier.remove_user_domain(user["user_id"], domain)
                        st.success(f"Removed domain: {domain}")
                        st.rerun()
        
        # Add new domain
        new_domain = st.text_input("Add new domain")
        
        if st.button("Add Domain") and new_domain:
            try:
                subscription_tier.add_user_domain(user["user_id"], new_domain)
                st.success(f"Added domain: {new_domain}")
                st.rerun()
            except ValueError as e:
                st.error(f"Error adding domain: {e}")
    
    with col2:
        st.markdown("### Feature Access")
        
        # Show feature access based on tier
        features = subscription_tier.get_user_feature_access(user["user_id"])
        
        # Group features by category
        feature_groups = {
            "Core Features": [
                "weekly_miss_score", "model_presence_tracker", "score_drift_alerts"
            ],
            "Analysis Features": [
                "signal_audit", "purity_score", "multi_domain", "competitive_benchmarking"
            ],
            "Workflow Features": [
                "detection_step", "drafting_step", "publishing_step", 
                "validation_step", "feedback_step"
            ],
            "Advanced Features": [
                "insight_preview", "human_override", "ab_testing", "feedback_analysis",
                "auto_publishing", "signal_triggers", "model_prioritization",
                "api_export", "custom_policies"
            ]
        }
        
        for group, group_features in feature_groups.items():
            st.markdown(f"#### {group}")
            
            for feature in group_features:
                feature_name = feature.replace("_", " ").title()
                if features.get(feature, False):
                    st.markdown(f"✅ <span class='feature-available'>{feature_name}</span>", unsafe_allow_html=True)
                else:
                    st.markdown(f"🔒 <span class='feature-locked'>{feature_name}</span>", unsafe_allow_html=True)
        
        # Show upgrade button
        if tier != "enterprise":
            next_tier = {"free": "pro", "pro": "growth", "growth": "enterprise"}[tier]
            
            st.button(f"Upgrade to {next_tier.capitalize()}", on_click=lambda: subscription_tier.update_user_tier(user["user_id"], next_tier))

def show_dashboard():
    """Show the main dashboard."""
    user = get_user_data()
    
    # Header
    st.markdown("<div class='main-header'>Sentinel Dashboard</div>", unsafe_allow_html=True)
    st.markdown(f"Welcome, {user['name']} | {user['tier'].capitalize()} Tier")
    
    # Tabs
    tab1, tab2, tab3, tab4 = st.tabs([
        "MISS Score", 
        "Competitive Benchmarking", 
        "Insight Preview",
        "Settings"
    ])
    
    with tab1:
        show_miss_score_tab()
    
    with tab2:
        show_benchmarking_tab()
    
    with tab3:
        show_insight_preview_tab()
    
    with tab4:
        show_platform_settings_tab()

def main():
    """Main function."""
    # Check if user is logged in
    if "user_id" in st.session_state and st.session_state.user_id:
        user = get_user_data()
        
        if user:
            show_dashboard()
        else:
            st.session_state.user_id = None
            show_login_form()
    else:
        show_login_form()

if __name__ == "__main__":
    main()