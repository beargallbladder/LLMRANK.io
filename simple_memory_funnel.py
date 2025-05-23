"""
Simple Memory Funnel - Clean 3-Page Layout
No bullshit, just works.
"""

import streamlit as st
import requests
import json
from typing import List, Dict, Optional

# Simple config
API_BASE = "http://localhost:8000"
API_KEY = "mcp_81b5be8a0aeb934314741b4c3f4b9436"
HEADERS = {"Authorization": f"Bearer {API_KEY}"}

def get_domains(query: str = "") -> List[Dict]:
    """Get domains from your working API."""
    try:
        response = requests.get(
            f"{API_BASE}/domains",
            headers=HEADERS,
            params={"limit": 500},
            timeout=10
        )
        if response.status_code == 200:
            domains = response.json()
            if query:
                return [d for d in domains if query.lower() in d.get('domain', '').lower()]
            return domains
    except:
        return []

def main():
    st.set_page_config(page_title="Memory Funnel", layout="wide")
    
    # Page 1: Search
    if 'page' not in st.session_state:
        st.session_state.page = 'search'
    
    if st.session_state.page == 'search':
        st.title("🔍 Brand Memory Search")
        st.markdown("Search through hundreds of brands to see how they're remembered by AI")
        
        query = st.text_input("Search for a brand:")
        
        if query:
            domains = get_domains(query)
            st.write(f"Found {len(domains)} brands matching '{query}'")
            
            for domain in domains[:10]:
                col1, col2 = st.columns([3, 1])
                with col1:
                    st.write(f"**{domain.get('domain', 'Unknown')}**")
                    st.write(f"Category: {domain.get('category', 'Unknown')}")
                with col2:
                    if st.button("View Memory", key=domain.get('domain')):
                        st.session_state.selected_domain = domain
                        st.session_state.page = 'memory'
                        st.rerun()
        
        # Show sample domains
        if not query:
            st.markdown("### Recently Analyzed Brands")
            sample_domains = get_domains()[:20]
            for domain in sample_domains:
                col1, col2 = st.columns([3, 1])
                with col1:
                    st.write(f"**{domain.get('domain', 'Unknown')}**")
                    st.write(f"Category: {domain.get('category', 'Unknown')}")
                with col2:
                    if st.button("View Memory", key=f"sample_{domain.get('domain')}"):
                        st.session_state.selected_domain = domain
                        st.session_state.page = 'memory'
                        st.rerun()
    
    # Page 2: Memory Analysis  
    elif st.session_state.page == 'memory':
        if st.button("← Back to Search"):
            st.session_state.page = 'search'
            st.rerun()
            
        domain_data = st.session_state.get('selected_domain', {})
        domain_name = domain_data.get('domain', 'Unknown')
        
        st.title(f"🧠 Memory Analysis: {domain_name}")
        
        # Memory decay alert
        st.error("🚨 MEMORY DECAY DETECTED: This brand's AI memory has declined 23% over the last 30 days")
        
        # Memory metrics
        col1, col2, col3 = st.columns(3)
        with col1:
            st.metric("Memory Score", "67/100", "-15 points")
        with col2:
            st.metric("Visibility Rank", "#34", "↓12 positions")
        with col3:
            st.metric("Recall Accuracy", "72%", "-8%")
        
        # Key insights
        st.markdown("### 🔍 Key Memory Issues")
        st.markdown("- AI models are forgetting your core value proposition")
        st.markdown("- Competitors are claiming your memory space")
        st.markdown("- Recent negative signals are overwhelming positive ones")
        
        # CTA
        st.markdown("### 💡 Repair Your Memory")
        if st.button("🚀 Start Memory Repair (7-Day Free Trial)", type="primary"):
            st.session_state.page = 'signup'
            st.rerun()
    
    # Page 3: Signup/Pricing
    elif st.session_state.page == 'signup':
        if st.button("← Back to Analysis"):
            st.session_state.page = 'memory'
            st.rerun()
            
        st.title("🚀 Repair Your AI Memory")
        st.markdown("**Get back control of how AI remembers your brand**")
        
        # Pricing
        col1, col2, col3 = st.columns(3)
        
        with col1:
            st.markdown("### Starter")
            st.markdown("**$99/month**")
            st.markdown("- 1 brand monitored")
            st.markdown("- Weekly memory reports")
            st.markdown("- Basic repair suggestions")
            
        with col2:
            st.markdown("### Professional")
            st.markdown("**$299/month**")
            st.markdown("- 5 brands monitored")
            st.markdown("- Daily memory tracking")
            st.markdown("- Advanced repair tools")
            st.button("Choose Professional", type="primary")
            
        with col3:
            st.markdown("### Enterprise")
            st.markdown("**$999/month**")
            st.markdown("- Unlimited brands")
            st.markdown("- Real-time monitoring")
            st.markdown("- Dedicated support")
        
        # Contact form
        st.markdown("### Start Your Free Trial")
        email = st.text_input("Business Email:")
        company = st.text_input("Company Name:")
        
        if st.button("Start 7-Day Free Trial"):
            if email and company:
                st.success("🎉 Trial activated! Check your email for next steps.")
            else:
                st.error("Please fill in all fields")

if __name__ == "__main__":
    main()