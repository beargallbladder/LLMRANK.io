"""
SaaS Monitoring Layer - Memory Repair Stack
Codename: GhostSignal SaaS MVP

Implements the complete SaaS experience with login, memory alerts,
tiered access, and revenue conversion for Memory Repair-as-a-Service.
"""

import streamlit as st
import json
import time
import os
import hashlib
from datetime import datetime, timedelta
from typing import Dict, List, Optional
import pandas as pd
import plotly.graph_objects as go
import plotly.express as px
from memory_decay_detector import memory_detector

# Page config
st.set_page_config(
    page_title="LLMRank.io - Memory Monitoring",
    page_icon="🧠",
    layout="wide",
    initial_sidebar_state="expanded"
)

# SaaS Configuration
PRICING_TIERS = {
    'free': {
        'name': 'Free',
        'price': '$0',
        'features': ['Memory scores (current)', 'Last 30 days', '1 alert/month'],
        'limits': {'alerts_per_month': 1, 'brands': 3, 'history_days': 30}
    },
    'pro': {
        'name': 'Pro',
        'price': '$29/mo',
        'features': ['Full drift graph', 'Weekly alerts', 'Competitor compare', 'Export data'],
        'limits': {'alerts_per_month': 30, 'brands': 25, 'history_days': 90}
    },
    'premium': {
        'name': 'Premium',
        'price': '$99/mo',
        'features': ['All models', 'Export API', 'Decay explorer', 'Custom categories', 'Priority support'],
        'limits': {'alerts_per_month': 1000, 'brands': 100, 'history_days': 365}
    }
}

class SaaSMonitoringLayer:
    """
    Complete SaaS monitoring system for Memory Repair-as-a-Service.
    Handles user accounts, brand claiming, memory alerts, and monetization.
    """
    
    def __init__(self):
        """Initialize SaaS monitoring layer."""
        self.users_file = 'data/saas_users.json'
        self.watchlists_file = 'data/user_watchlists.json'
        self.alerts_file = 'data/memory_alerts.json'
        
        # Load existing data
        self.users = self._load_users()
        self.watchlists = self._load_watchlists()
        self.alerts = self._load_alerts()
    
    def _load_users(self) -> Dict:
        """Load user accounts."""
        try:
            if os.path.exists(self.users_file):
                with open(self.users_file, 'r') as f:
                    return json.load(f)
        except Exception:
            pass
        return {}
    
    def _load_watchlists(self) -> Dict:
        """Load user brand watchlists."""
        try:
            if os.path.exists(self.watchlists_file):
                with open(self.watchlists_file, 'r') as f:
                    return json.load(f)
        except Exception:
            pass
        return {}
    
    def _load_alerts(self) -> List:
        """Load memory alerts."""
        try:
            if os.path.exists(self.alerts_file):
                with open(self.alerts_file, 'r') as f:
                    return json.load(f)
        except Exception:
            pass
        return []
    
    def _save_data(self):
        """Save all SaaS data."""
        try:
            os.makedirs('data', exist_ok=True)
            
            with open(self.users_file, 'w') as f:
                json.dump(self.users, f, indent=2)
            
            with open(self.watchlists_file, 'w') as f:
                json.dump(self.watchlists, f, indent=2)
            
            with open(self.alerts_file, 'w') as f:
                json.dump(self.alerts, f, indent=2)
        except Exception as e:
            st.error(f"Error saving data: {e}")
    
    def authenticate_user(self, email: str, password: str) -> Optional[Dict]:
        """Authenticate user login."""
        if email in self.users:
            user = self.users[email]
            password_hash = hashlib.sha256(password.encode()).hexdigest()
            if user.get('password_hash') == password_hash:
                return user
        return None
    
    def register_user(self, email: str, password: str, company: str = "") -> bool:
        """Register new user account."""
        if email in self.users:
            return False
        
        password_hash = hashlib.sha256(password.encode()).hexdigest()
        
        self.users[email] = {
            'email': email,
            'password_hash': password_hash,
            'company': company,
            'tier': 'free',
            'created_at': time.time(),
            'last_login': time.time(),
            'alerts_this_month': 0,
            'brands_claimed': []
        }
        
        # Initialize empty watchlist
        self.watchlists[email] = []
        
        self._save_data()
        return True
    
    def claim_brand(self, user_email: str, brand_domain: str) -> bool:
        """Allow user to claim a brand for monitoring."""
        if user_email not in self.users:
            return False
        
        user = self.users[user_email]
        tier_limits = PRICING_TIERS[user['tier']]['limits']
        
        # Check brand limits
        if len(user['brands_claimed']) >= tier_limits['brands']:
            return False
        
        # Add to claimed brands
        if brand_domain not in user['brands_claimed']:
            user['brands_claimed'].append(brand_domain)
        
        # Add to watchlist
        if user_email not in self.watchlists:
            self.watchlists[user_email] = []
        
        if brand_domain not in self.watchlists[user_email]:
            self.watchlists[user_email].append({
                'domain': brand_domain,
                'claimed_at': time.time(),
                'alerts_enabled': True
            })
        
        self._save_data()
        return True
    
    def generate_memory_alert(self, brand_domain: str, decay_info: Dict) -> Dict:
        """Generate memory decay alert for a brand."""
        alert = {
            'id': f"alert_{brand_domain}_{int(time.time())}",
            'brand': brand_domain,
            'alert_type': 'memory_decay',
            'severity': decay_info.get('severity', 'mild'),
            'decay_percentage': decay_info.get('decay_percentage', 0),
            'model': decay_info.get('model', 'unknown'),
            'current_score': decay_info.get('current_score', 0),
            'previous_score': decay_info.get('previous_score', 0),
            'triggered_at': time.time(),
            'status': 'active',
            'message': self._generate_alert_message(brand_domain, decay_info)
        }
        
        self.alerts.append(alert)
        self._save_data()
        return alert
    
    def _generate_alert_message(self, brand: str, decay_info: Dict) -> str:
        """Generate human-readable alert message."""
        severity = decay_info.get('severity', 'mild')
        decay_pct = decay_info.get('decay_percentage', 0) * 100
        model = decay_info.get('model', 'LLM')
        
        severity_emoji = {'mild': '⚠️', 'moderate': '🚨', 'severe': '🔴'}
        emoji = severity_emoji.get(severity, '⚠️')
        
        return f"{emoji} {brand} memory decay detected: {decay_pct:.1f}% drop in {model} over 30 days. Your brand is being forgotten."
    
    def get_user_alerts(self, user_email: str) -> List[Dict]:
        """Get alerts for a specific user."""
        if user_email not in self.watchlists:
            return []
        
        user_brands = [item['domain'] for item in self.watchlists[user_email]]
        
        user_alerts = [
            alert for alert in self.alerts
            if alert['brand'] in user_brands and alert['status'] == 'active'
        ]
        
        return sorted(user_alerts, key=lambda x: x['triggered_at'], reverse=True)
    
    def send_memory_alert_email(self, user_email: str, alert: Dict) -> bool:
        """Send memory decay alert email to user."""
        try:
            user = self.users.get(user_email)
            if not user:
                return False
            
            # Check alert limits
            tier_limits = PRICING_TIERS[user['tier']]['limits']
            if user['alerts_this_month'] >= tier_limits['alerts_per_month']:
                return False
            
            # Create email content
            subject = f"🚨 Memory Decay Alert: {alert['brand']}"
            
            body = f"""
            Memory Decay Alert for {alert['brand']}
            
            {alert['message']}
            
            Details:
            - Current Memory Score: {alert['current_score']:.1f}/100
            - Previous Score: {alert['previous_score']:.1f}/100
            - Severity: {alert['severity'].title()}
            - Model: {alert['model']}
            
            What this means:
            Your brand is losing presence in AI model memory. This affects how AI systems respond to queries about your industry.
            
            Recommended Actions:
            1. Review your recent content strategy
            2. Increase brand mention frequency
            3. Strengthen competitive positioning
            
            View Full Analysis: https://llmrank.io/brand/{alert['brand']}
            
            Need help? Upgrade to Pro for weekly monitoring and competitor analysis.
            
            - The LLMRank.io Team
            """
            
            # Log email (in production, integrate with SendGrid/AWS SES)
            print(f"📧 Would send email to {user_email}: {subject}")
            print(f"Body: {body[:200]}...")
            
            # Increment alert count
            user['alerts_this_month'] += 1
            self._save_data()
            
            return True
            
        except Exception as e:
            print(f"Error sending alert email: {e}")
            return False
    
    def check_upgrade_triggers(self, user_email: str) -> Dict:
        """Check if user should see upgrade prompts."""
        user = self.users.get(user_email)
        if not user or user['tier'] != 'free':
            return {'show_upgrade': False}
        
        # Check usage patterns
        watchlist_size = len(self.watchlists.get(user_email, []))
        user_alerts = self.get_user_alerts(user_email)
        
        triggers = []
        
        if watchlist_size >= 2:
            triggers.append("tracking_multiple_brands")
        
        if len(user_alerts) > 0:
            triggers.append("active_decay_alerts")
        
        if user['alerts_this_month'] >= 1:
            triggers.append("alert_limit_reached")
        
        return {
            'show_upgrade': len(triggers) > 0,
            'triggers': triggers,
            'message': self._get_upgrade_message(triggers)
        }
    
    def _get_upgrade_message(self, triggers: List[str]) -> str:
        """Get upgrade message based on triggers."""
        if "alert_limit_reached" in triggers:
            return "🔒 You've reached your free alert limit. Upgrade to Pro for unlimited alerts and deeper insights."
        elif "active_decay_alerts" in triggers:
            return "📈 Memory decay detected! Upgrade to Pro for weekly monitoring and competitor analysis."
        elif "tracking_multiple_brands" in triggers:
            return "🎯 Tracking multiple brands? Upgrade to Pro for full drift analysis and export capabilities."
        else:
            return "💡 Unlock advanced memory monitoring with Pro features."

# Initialize SaaS system
saas = SaaSMonitoringLayer()

def main():
    """Main SaaS monitoring application."""
    
    st.title("🧠 LLMRank.io - Memory Monitoring")
    st.caption("Early warning system for AI memory decay")
    
    # Authentication system
    if 'user' not in st.session_state:
        st.session_state.user = None
    
    # Sidebar authentication
    with st.sidebar:
        if st.session_state.user is None:
            render_auth_sidebar()
        else:
            render_user_sidebar()
    
    # Main content
    if st.session_state.user is None:
        render_landing_page()
    else:
        render_dashboard()

def render_auth_sidebar():
    """Render authentication sidebar."""
    st.markdown("### 🔐 Account Access")
    
    tab1, tab2 = st.tabs(["Login", "Sign Up"])
    
    with tab1:
        with st.form("login_form"):
            email = st.text_input("Email")
            password = st.text_input("Password", type="password")
            
            if st.form_submit_button("Login"):
                user = saas.authenticate_user(email, password)
                if user:
                    st.session_state.user = user
                    st.success("Welcome back!")
                    st.rerun()
                else:
                    st.error("Invalid credentials")
    
    with tab2:
        with st.form("signup_form"):
            email = st.text_input("Email Address")
            company = st.text_input("Company (Optional)")
            password = st.text_input("Password", type="password")
            confirm_password = st.text_input("Confirm Password", type="password")
            
            if st.form_submit_button("Create Account"):
                if password != confirm_password:
                    st.error("Passwords don't match")
                elif len(password) < 6:
                    st.error("Password must be at least 6 characters")
                elif saas.register_user(email, password, company):
                    st.success("Account created! Please login.")
                else:
                    st.error("Email already exists")

def render_user_sidebar():
    """Render logged-in user sidebar."""
    user = st.session_state.user
    
    st.markdown(f"### 👋 {user['email']}")
    st.markdown(f"**Plan:** {PRICING_TIERS[user['tier']]['name']} {PRICING_TIERS[user['tier']]['price']}")
    
    # Plan usage
    tier_limits = PRICING_TIERS[user['tier']]['limits']
    st.progress(user['alerts_this_month'] / tier_limits['alerts_per_month'])
    st.caption(f"Alerts: {user['alerts_this_month']}/{tier_limits['alerts_per_month']}")
    
    st.progress(len(user['brands_claimed']) / tier_limits['brands'])
    st.caption(f"Brands: {len(user['brands_claimed'])}/{tier_limits['brands']}")
    
    # Navigation
    st.markdown("---")
    
    if st.button("🏠 Dashboard", use_container_width=True):
        st.session_state.page = 'dashboard'
    
    if st.button("🔔 Alerts", use_container_width=True):
        st.session_state.page = 'alerts'
    
    if st.button("📊 My Brands", use_container_width=True):
        st.session_state.page = 'brands'
    
    if st.button("💳 Upgrade", use_container_width=True):
        st.session_state.page = 'pricing'
    
    st.markdown("---")
    
    if st.button("Logout"):
        st.session_state.user = None
        st.rerun()

def render_landing_page():
    """Render landing page for non-authenticated users."""
    
    # Hero section
    col1, col2 = st.columns([2, 1])
    
    with col1:
        st.markdown("## Don't Get Forgotten by AI")
        st.markdown("**Monitor how LLMs remember your brand. Get alerts when memory decays.**")
        
        st.markdown("""
        🧠 **Real-time memory tracking** across GPT-4, Claude, Gemini  
        📉 **Decay detection** - 15%+ drops trigger instant alerts  
        🔔 **Early warning system** - know before your competitors  
        📈 **Competitive analysis** - see who's gaining mindshare  
        """)
        
        if st.button("🚀 Start Free Monitoring", type="primary"):
            st.info("👈 Create your account in the sidebar to get started!")
    
    with col2:
        # Show sample memory chart
        sample_data = {
            'Date': pd.date_range(start='2024-01-01', periods=30, freq='D'),
            'Memory Score': [85 - i*0.8 + (i%3)*2 for i in range(30)]
        }
        df = pd.DataFrame(sample_data)
        
        fig = px.line(df, x='Date', y='Memory Score', 
                     title="Sample: Brand Memory Decay")
        fig.add_hline(y=70, line_dash="dash", line_color="red",
                     annotation_text="Alert Threshold")
        fig.update_layout(height=300)
        st.plotly_chart(fig, use_container_width=True)
    
    # Pricing preview
    st.markdown("---")
    st.markdown("### 💎 Simple, Transparent Pricing")
    
    col1, col2, col3 = st.columns(3)
    
    for i, (tier_key, tier_info) in enumerate(PRICING_TIERS.items()):
        with [col1, col2, col3][i]:
            st.markdown(f"**{tier_info['name']}**")
            st.markdown(f"# {tier_info['price']}")
            
            for feature in tier_info['features']:
                st.markdown(f"✅ {feature}")
            
            if tier_key == 'pro':
                st.button(f"Choose {tier_info['name']}", type="primary", key=f"pricing_{tier_key}")
            else:
                st.button(f"Choose {tier_info['name']}", key=f"pricing_{tier_key}")

def render_dashboard():
    """Render main dashboard for authenticated users."""
    user = st.session_state.user
    page = st.session_state.get('page', 'dashboard')
    
    if page == 'dashboard':
        render_main_dashboard()
    elif page == 'alerts':
        render_alerts_page()
    elif page == 'brands':
        render_brands_page()
    elif page == 'pricing':
        render_pricing_page()

def render_main_dashboard():
    """Render main dashboard."""
    user = st.session_state.user
    
    st.markdown("## 📊 Memory Monitoring Dashboard")
    
    # Check for upgrade triggers
    upgrade_check = saas.check_upgrade_triggers(user['email'])
    if upgrade_check['show_upgrade']:
        st.warning(f"🔔 {upgrade_check['message']}")
        if st.button("Upgrade Now"):
            st.session_state.page = 'pricing'
            st.rerun()
    
    # Key metrics
    col1, col2, col3, col4 = st.columns(4)
    
    user_alerts = saas.get_user_alerts(user['email'])
    watchlist = saas.watchlists.get(user['email'], [])
    
    with col1:
        st.metric("Brands Monitored", len(watchlist))
    
    with col2:
        st.metric("Active Alerts", len(user_alerts))
    
    with col3:
        avg_score = 85.2  # Mock current average
        st.metric("Avg Memory Score", f"{avg_score:.1f}/100")
    
    with col4:
        alerts_used = user['alerts_this_month']
        alerts_limit = PRICING_TIERS[user['tier']]['limits']['alerts_per_month']
        st.metric("Alerts Used", f"{alerts_used}/{alerts_limit}")
    
    # Recent alerts
    if user_alerts:
        st.markdown("### 🚨 Recent Alerts")
        for alert in user_alerts[:3]:
            with st.expander(f"{alert['brand']} - {alert['severity'].title()} Decay"):
                st.write(alert['message'])
                st.write(f"**Triggered:** {datetime.fromtimestamp(alert['triggered_at']).strftime('%Y-%m-%d %H:%M')}")
    
    # Brand claiming
    st.markdown("### 🎯 Claim Your Brand")
    with st.form("claim_brand_form"):
        domain = st.text_input("Brand Domain (e.g., yourcompany.com)")
        
        if st.form_submit_button("Claim Brand"):
            if saas.claim_brand(user['email'], domain):
                st.success(f"✅ Successfully claimed {domain}!")
                st.rerun()
            else:
                st.error("Failed to claim brand. Check your plan limits.")

def render_alerts_page():
    """Render alerts management page."""
    st.markdown("## 🔔 Memory Decay Alerts")
    
    user_alerts = saas.get_user_alerts(st.session_state.user['email'])
    
    if not user_alerts:
        st.info("No active alerts. Your brands are maintaining strong memory scores! 🎉")
        return
    
    for alert in user_alerts:
        severity_color = {'mild': 'orange', 'moderate': 'red', 'severe': 'darkred'}
        
        with st.container():
            st.markdown(f"<div style='border-left: 4px solid {severity_color.get(alert['severity'], 'gray')}; padding-left: 10px; margin-bottom: 10px;'>", unsafe_allow_html=True)
            
            col1, col2 = st.columns([3, 1])
            
            with col1:
                st.markdown(f"**{alert['brand']}** - {alert['severity'].title()} Decay")
                st.write(alert['message'])
                st.caption(f"Triggered: {datetime.fromtimestamp(alert['triggered_at']).strftime('%Y-%m-%d %H:%M')}")
            
            with col2:
                if st.button("View Details", key=f"alert_{alert['id']}"):
                    st.info("Detailed analysis requires Pro upgrade")
            
            st.markdown("</div>", unsafe_allow_html=True)

def render_brands_page():
    """Render brand management page."""
    st.markdown("## 📈 My Brands")
    
    watchlist = saas.watchlists.get(st.session_state.user['email'], [])
    
    if not watchlist:
        st.info("No brands claimed yet. Claim your first brand from the dashboard!")
        return
    
    for brand_info in watchlist:
        with st.expander(f"🏢 {brand_info['domain']}"):
            col1, col2 = st.columns(2)
            
            with col1:
                st.write(f"**Claimed:** {datetime.fromtimestamp(brand_info['claimed_at']).strftime('%Y-%m-%d')}")
                st.write(f"**Alerts Enabled:** {'✅' if brand_info['alerts_enabled'] else '❌'}")
            
            with col2:
                # Mock memory score
                current_score = 82.5
                st.metric("Current Memory Score", f"{current_score:.1f}/100")
                
                if st.session_state.user['tier'] == 'free':
                    st.info("🔒 Upgrade to Pro for detailed trends")

def render_pricing_page():
    """Render pricing and upgrade page."""
    st.markdown("## 💳 Upgrade Your Plan")
    
    current_tier = st.session_state.user['tier']
    
    col1, col2, col3 = st.columns(3)
    
    for i, (tier_key, tier_info) in enumerate(PRICING_TIERS.items()):
        with [col1, col2, col3][i]:
            is_current = tier_key == current_tier
            
            if is_current:
                st.success(f"✅ Current Plan")
            
            st.markdown(f"### {tier_info['name']}")
            st.markdown(f"# {tier_info['price']}")
            
            for feature in tier_info['features']:
                st.markdown(f"✅ {feature}")
            
            limits = tier_info['limits']
            st.caption(f"Up to {limits['brands']} brands")
            st.caption(f"{limits['alerts_per_month']} alerts/month")
            st.caption(f"{limits['history_days']} days history")
            
            if not is_current and tier_key != 'free':
                if st.button(f"Upgrade to {tier_info['name']}", key=f"upgrade_{tier_key}"):
                    st.success(f"🎉 Upgrading to {tier_info['name']}! (Demo mode)")
                    # In production: integrate with Stripe/payment processor

if __name__ == "__main__":
    main()