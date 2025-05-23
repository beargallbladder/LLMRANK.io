"""
Logo Integration Test

This script tests the logo client library with various domains to ensure
it works consistently, provides high-quality results, and is optimized for SEO.
"""

import os
import json
import base64
from PIL import Image
from io import BytesIO
import streamlit as st
from logo_client_lib import logo_client, get_html_tag, generate_comparison_html

# Set up the test directory
TEST_OUTPUT_DIR = "data/logo_tests"
os.makedirs(TEST_OUTPUT_DIR, exist_ok=True)

# Test domains across different industries
TEST_DOMAINS = {
    "Tech": [
        "apple.com",
        "google.com", 
        "microsoft.com",
        "amazon.com", 
        "meta.com"
    ],
    "Retail": [
        "walmart.com",
        "target.com",
        "costco.com",
        "kroger.com"
    ],
    "Financial": [
        "jpmorgan.com",
        "bankofamerica.com",
        "wellsfargo.com",
        "goldmansachs.com"
    ],
    "Automotive": [
        "toyota.com",
        "honda.com",
        "ford.com",
        "tesla.com"
    ],
    "Media": [
        "netflix.com",
        "disney.com",
        "hulu.com",
        "spotify.com"
    ],
    "Random/Difficult": [
        "thisisaprobablyfakedomain123456.com",
        "a-very-long-domain-name-that-tests-the-limits.com",
        "example.org",
        "test-company-name.io"
    ]
}

def test_logo_retrieval(domain: str, force_refresh: bool = False):
    """Test retrieving a logo for a domain."""
    st.write(f"Testing: **{domain}**")
    
    # Get logo with timing
    import time
    start_time = time.time()
    logo_data = logo_client.get_logo(domain, force_refresh=force_refresh)
    elapsed_time = time.time() - start_time
    
    # Display basic info
    st.write(f"- Company Name: {logo_data.get('company_name', 'Unknown')}")
    st.write(f"- Source: {logo_data.get('source', 'Unknown')}")
    st.write(f"- Found: {'✅' if logo_data.get('found', False) else '❌'}")
    st.write(f"- Time: {elapsed_time:.2f} seconds")
    
    # Display the logo
    if logo_data.get("logo_data"):
        image_bytes = base64.b64decode(logo_data["logo_data"])
        st.image(image_bytes, width=150)
        
        # Save to file for inspection
        output_path = os.path.join(TEST_OUTPUT_DIR, f"{domain.replace('.', '_')}.png")
        with open(output_path, "wb") as f:
            f.write(image_bytes)
    
    # Show SEO keywords
    if "seo_keywords" in logo_data and logo_data["seo_keywords"]:
        with st.expander("SEO Keywords"):
            st.write(", ".join(logo_data["seo_keywords"]))
    
    # Show HTML tag example
    with st.expander("HTML Tag Example"):
        html_tag = logo_client.get_html_tag(domain)
        st.code(html_tag, language="html")
    
    return logo_data

def test_bulk_retrieval(domains: list):
    """Test retrieving logos in bulk."""
    st.write(f"Testing bulk retrieval for {len(domains)} domains...")
    
    # Get logos with timing
    import time
    start_time = time.time()
    logos_data = logo_client.get_logos_bulk(domains)
    elapsed_time = time.time() - start_time
    
    st.write(f"Total time: {elapsed_time:.2f} seconds")
    st.write(f"Average time per domain: {elapsed_time/len(domains):.2f} seconds")
    
    # Count successes
    success_count = sum(1 for logo in logos_data if logo.get("found", False))
    st.write(f"Success rate: {success_count}/{len(domains)} ({success_count/len(domains)*100:.1f}%)")
    
    # Display the logos in a grid
    cols = st.columns(4)
    for i, logo_data in enumerate(logos_data):
        domain = logo_data.get("domain", "unknown")
        with cols[i % 4]:
            if logo_data.get("logo_data"):
                image_bytes = base64.b64decode(logo_data["logo_data"])
                st.image(image_bytes, caption=domain, width=100)
            else:
                st.write(domain)
                st.write("❌ Not found")
    
    return logos_data

def test_comparison_html(category: str, domains: list):
    """Test generating comparison HTML."""
    st.write(f"Testing comparison HTML for {category}...")
    
    # Generate the HTML
    html = generate_comparison_html(domains, title=f"{category} Competitive Analysis")
    
    # Display it using Streamlit components
    st.components.v1.html(html, height=250)
    
    # Show the raw HTML
    with st.expander("Raw HTML"):
        st.code(html, language="html")

def main():
    """Main test function."""
    st.set_page_config(
        page_title="Logo Integration Test",
        page_icon="🖼️",
        layout="wide"
    )
    
    st.title("Logo Integration Test")
    st.write("Testing the logo client library to ensure it works for every domain and is optimized for SEO.")
    
    st.header("Individual Logo Tests")
    
    # Test tabs for different categories
    tabs = st.tabs(list(TEST_DOMAINS.keys()))
    
    for i, (category, domains) in enumerate(TEST_DOMAINS.items()):
        with tabs[i]:
            st.subheader(f"{category} Domains")
            
            # Individual tests
            for domain in domains:
                st.markdown("---")
                test_logo_retrieval(domain)
    
    st.header("Bulk Retrieval Tests")
    for category, domains in TEST_DOMAINS.items():
        st.subheader(f"{category} Bulk Test")
        test_bulk_retrieval(domains)
        st.markdown("---")
    
    st.header("Comparison HTML Tests")
    for category, domains in TEST_DOMAINS.items():
        st.subheader(f"{category} Comparison")
        test_comparison_html(category, domains)
        st.markdown("---")

if __name__ == "__main__":
    main()