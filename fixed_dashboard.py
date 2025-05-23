"""
Fixed Dashboard with Proper Domain Selection
No more broken search box - real dropdown with actual domains
"""

import streamlit as st
import json
import os
from domain_index_builder import get_domain_suggestions, build_domain_index
from database import get_domain_analysis, get_insights_for_domain, get_trends_for_domain

def render_fixed_dashboard():
    """
    Render dashboard with working domain dropdown
    """
    
    st.title("🔥 LLMPageRank Intelligence Dashboard")
    st.markdown("**Real domains with actual data - No broken search boxes!**")
    
    # Build/refresh domain index
    if st.button("🔄 Refresh Domain Index"):
        with st.spinner("Rebuilding domain index..."):
            domains = build_domain_index()
            st.success(f"✅ Indexed {len(domains)} domains with actual data")
            st.rerun()
    
    # Load domain index
    try:
        with open('data/domain_index.json', 'r') as f:
            all_domains = json.load(f)
    except:
        st.warning("Building domain index for first time...")
        all_domains = build_domain_index()
    
    if not all_domains:
        st.error("No domains found with data. Run the blitz engine to collect domain insights first.")
        return
    
    # Create dropdown options
    domain_options = []
    domain_map = {}
    
    for domain_data in all_domains:
        display_name = domain_data['display_name']
        domain = domain_data['domain']
        quality = domain_data['quality_score']
        insight_count = domain_data['insight_count']
        
        # Create rich display option
        if quality > 0:
            option_text = f"🏆 {display_name} (Quality: {quality:.2f}, {insight_count} insights)"
        elif insight_count > 0:
            option_text = f"📊 {display_name} ({insight_count} insights)"
        else:
            option_text = f"📋 {display_name}"
            
        domain_options.append(option_text)
        domain_map[option_text] = domain
    
    # Domain selection dropdown
    st.subheader("🎯 Select Domain")
    
    if domain_options:
        selected_option = st.selectbox(
            "Choose a domain with actual data:",
            options=domain_options,
            index=0,
            help="All domains listed have real data collected by your system"
        )
        
        selected_domain = domain_map[selected_option]
        
        # Show selected domain info
        selected_domain_data = next(d for d in all_domains if d['domain'] == selected_domain)
        
        col1, col2, col3, col4 = st.columns(4)
        with col1:
            st.metric("Domain", selected_domain)
        with col2:
            st.metric("Quality Score", f"{selected_domain_data['quality_score']:.2f}")
        with col3:
            st.metric("Insights", selected_domain_data['insight_count'])
        with col4:
            data_types = []
            if selected_domain_data['has_insights']:
                data_types.append("Insights")
            if selected_domain_data['has_results']:
                data_types.append("Results")
            if selected_domain_data['has_trends']:
                data_types.append("Trends")
            st.metric("Data Types", ", ".join(data_types) if data_types else "None")
        
        # Display domain data
        render_domain_details(selected_domain, selected_domain_data)
        
    else:
        st.warning("No domains found. Start the continuous blitz engine to collect domain data.")

def render_domain_details(domain, domain_data):
    """
    Render detailed information for selected domain
    """
    
    st.subheader(f"📊 {domain_data['display_name']} Analysis")
    
    # Tabs for different data types
    tabs = []
    if domain_data['has_insights']:
        tabs.append("💡 Insights")
    if domain_data['has_results']:
        tabs.append("📈 Results")
    if domain_data['has_trends']:
        tabs.append("📊 Trends")
    
    if not tabs:
        st.info("No detailed data available for this domain yet.")
        return
    
    tab_objects = st.tabs(tabs)
    
    # Insights tab
    if domain_data['has_insights'] and len(tab_objects) > 0:
        with tab_objects[0]:
            render_insights_tab(domain)
    
    # Results tab
    if domain_data['has_results'] and len(tab_objects) > (1 if domain_data['has_insights'] else 0):
        tab_index = 1 if domain_data['has_insights'] else 0
        if tab_index < len(tab_objects):
            with tab_objects[tab_index]:
                render_results_tab(domain)
    
    # Trends tab
    if domain_data['has_trends']:
        tab_index = 0
        if domain_data['has_insights']:
            tab_index += 1
        if domain_data['has_results']:
            tab_index += 1
        if tab_index < len(tab_objects):
            with tab_objects[tab_index]:
                render_trends_tab(domain)

def render_insights_tab(domain):
    """
    Render insights for domain
    """
    
    try:
        with open('data/insights/insight_log.json', 'r') as f:
            all_insights = json.load(f)
        
        domain_insights = [i for i in all_insights if i.get('domain') == domain]
        
        if not domain_insights:
            st.info(f"No insights found for {domain}")
            return
        
        st.write(f"**{len(domain_insights)} insights found for {domain}**")
        
        for i, insight in enumerate(domain_insights):
            with st.expander(f"Insight #{i+1} - Quality: {insight.get('quality_score', 0):.2f}"):
                content = insight.get('content', 'No content available')
                st.markdown(content)
                
                # Show metadata
                col1, col2 = st.columns(2)
                with col1:
                    if insight.get('timestamp'):
                        import datetime
                        dt = datetime.datetime.fromtimestamp(insight['timestamp'])
                        st.caption(f"Generated: {dt.strftime('%Y-%m-%d %H:%M')}")
                with col2:
                    st.caption(f"Quality: {insight.get('quality_score', 0):.2f}")
                    
    except Exception as e:
        st.error(f"Error loading insights: {e}")

def render_results_tab(domain):
    """
    Render results for domain
    """
    
    try:
        # Try to get results from database
        results = get_domain_analysis(domain)
        if results:
            st.json(results)
        else:
            st.info(f"No results found for {domain}")
            
    except Exception as e:
        st.info(f"Results data not available yet for {domain}")

def render_trends_tab(domain):
    """
    Render trends for domain
    """
    
    try:
        with open('data/trends.json', 'r') as f:
            all_trends = json.load(f)
        
        if isinstance(all_trends, list):
            domain_trends = [t for t in all_trends if t.get('domain') == domain]
        else:
            domain_trends = all_trends.get(domain, [])
        
        if domain_trends:
            st.json(domain_trends)
        else:
            st.info(f"No trends data found for {domain}")
            
    except Exception as e:
        st.info(f"Trends data not available yet for {domain}")

def main():
    render_fixed_dashboard()

if __name__ == "__main__":
    main()