"""
MCP Logo Service Client

This script demonstrates how to use the MCP Logo Service to retrieve
brand logos for domains to enhance LLMPageRank visualizations.
"""

import requests
import base64
from PIL import Image
import io
import os
import json
from typing import Dict, Any, Optional
import logging

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Constants
MCP_LOGO_API_URL = "http://localhost:6500/api"
MCP_API_KEY = "mcp_81b5be8a0aeb934314741b4c3f4b9436"  # Use the admin key
LOGO_CACHE_DIR = "data/logos/demo"

# Ensure directories exist
os.makedirs(LOGO_CACHE_DIR, exist_ok=True)

def get_logo_for_domain(domain: str, force_refresh: bool = False) -> Optional[Dict[str, Any]]:
    """
    Get logo for a domain from the MCP Logo Service.
    
    Args:
        domain: Domain to get logo for
        force_refresh: Whether to force a refresh of cached logo
        
    Returns:
        Logo data or None if failed
    """
    try:
        headers = {"api-key": MCP_API_KEY}
        params = {"force_refresh": str(force_refresh).lower()}
        
        response = requests.get(
            f"{MCP_LOGO_API_URL}/logos/{domain}", 
            headers=headers,
            params=params
        )
        
        if response.status_code != 200:
            logger.error(f"Failed to get logo for {domain}: {response.status_code} {response.text}")
            return None
        
        return response.json()
    except Exception as e:
        logger.error(f"Error getting logo for {domain}: {e}")
        return None

def save_logo_image(logo_data: Dict[str, Any], output_path: Optional[str] = None) -> Optional[str]:
    """
    Save logo image to file.
    
    Args:
        logo_data: Logo data from API
        output_path: Path to save logo to (default: auto-generated)
        
    Returns:
        Path to saved logo or None if failed
    """
    try:
        if not logo_data.get("logo_data"):
            logger.warning(f"No logo data for {logo_data.get('domain')}")
            return None
        
        # Decode logo data
        image_bytes = base64.b64decode(logo_data["logo_data"])
        
        # Determine output path if not provided
        if not output_path:
            domain = logo_data["domain"]
            fmt = logo_data.get("format", "png")
            output_path = os.path.join(LOGO_CACHE_DIR, f"{domain}.{fmt}")
        
        # Save to file
        with open(output_path, "wb") as f:
            f.write(image_bytes)
        
        logger.info(f"Saved logo to {output_path}")
        return output_path
    except Exception as e:
        logger.error(f"Error saving logo: {e}")
        return None

def display_logo(logo_data: Dict[str, Any]) -> None:
    """
    Display logo (intended for interactive environments).
    
    Args:
        logo_data: Logo data from API
    """
    try:
        if not logo_data.get("logo_data"):
            print(f"No logo data for {logo_data.get('domain')}")
            return
        
        # Decode logo data
        image_bytes = base64.b64decode(logo_data["logo_data"])
        
        # Create PIL Image
        img = Image.open(io.BytesIO(image_bytes))
        
        # In interactive environments like Jupyter, this will display the image
        # Here we just print the image dimensions
        print(f"Logo dimensions: {img.width}x{img.height}")
    except Exception as e:
        logger.error(f"Error displaying logo: {e}")

def get_logos_for_competitive_set(domains: list[str]) -> Dict[str, Any]:
    """
    Get logos for a competitive set of domains.
    
    Args:
        domains: List of domains to get logos for
        
    Returns:
        Dictionary mapping domains to logo file paths
    """
    try:
        headers = {"api-key": MCP_API_KEY}
        
        payload = {
            "domains": domains,
            "force_refresh": False
        }
        
        response = requests.post(
            f"{MCP_LOGO_API_URL}/logos/bulk", 
            headers=headers,
            json=payload
        )
        
        if response.status_code != 200:
            logger.error(f"Failed to get logos for competitive set: {response.status_code} {response.text}")
            return {}
        
        logo_data_list = response.json()
        
        # Save logos to files
        result = {}
        for logo_data in logo_data_list:
            domain = logo_data["domain"]
            logo_path = save_logo_image(logo_data)
            result[domain] = logo_path
        
        return result
    except Exception as e:
        logger.error(f"Error getting logos for competitive set: {e}")
        return {}

def get_logo_html_tag(domain: str, alt_text: Optional[str] = None, width: int = 100) -> str:
    """
    Get HTML img tag for domain logo.
    
    Args:
        domain: Domain to get logo for
        alt_text: Alt text for image (default: domain name)
        width: Image width in pixels (default: 100)
        
    Returns:
        HTML img tag or empty string if failed
    """
    try:
        logo_data = get_logo_for_domain(domain)
        
        if not logo_data or not logo_data.get("logo_data"):
            return ""
        
        # Use direct image endpoint URL for better performance
        logo_url = f"{MCP_LOGO_API_URL}/logos/{domain}/image"
        
        # Use domain as alt text if not provided
        if not alt_text:
            alt_text = domain
        
        return f'<img src="{logo_url}" alt="{alt_text}" width="{width}" class="brand-logo">'
    except Exception as e:
        logger.error(f"Error getting logo HTML tag for {domain}: {e}")
        return ""

def generate_competitive_html(category: str, domains: list[str]) -> str:
    """
    Generate HTML for competitive comparison with logos.
    
    Args:
        category: Category name
        domains: List of domains to compare
        
    Returns:
        HTML for competitive comparison
    """
    logos = get_logos_for_competitive_set(domains)
    
    html = f"""
    <div class="competitive-analysis">
        <h2>{category} - Competitive Analysis</h2>
        <div class="brand-grid">
    """
    
    for domain in domains:
        logo_path = logos.get(domain)
        
        if logo_path:
            html += f"""
            <div class="brand-card">
                <div class="brand-logo-container">
                    <img src="{logo_path}" alt="{domain}" class="brand-logo">
                </div>
                <div class="brand-name">{domain}</div>
            </div>
            """
        else:
            html += f"""
            <div class="brand-card">
                <div class="brand-logo-container no-logo">
                    <span class="logo-placeholder">{domain[0].upper()}</span>
                </div>
                <div class="brand-name">{domain}</div>
            </div>
            """
    
    html += """
        </div>
    </div>
    """
    
    return html

def demonstrate_logo_service() -> None:
    """Demonstrate the MCP Logo Service functionality."""
    print("\n===== MCP Logo Service Demonstration =====\n")
    
    # Test with some well-known tech companies
    tech_domains = ["apple.com", "google.com", "microsoft.com", "amazon.com", "meta.com"]
    
    print(f"Getting logos for {len(tech_domains)} tech domains...")
    tech_logos = get_logos_for_competitive_set(tech_domains)
    
    print("\nResults:")
    for domain, logo_path in tech_logos.items():
        status = "✓ Found" if logo_path else "✗ Not found"
        print(f"{domain}: {status}")
    
    # Test with some retail companies
    retail_domains = ["walmart.com", "target.com", "costco.com", "kroger.com"]
    
    print(f"\nGetting logos for {len(retail_domains)} retail domains...")
    retail_logos = get_logos_for_competitive_set(retail_domains)
    
    print("\nResults:")
    for domain, logo_path in retail_logos.items():
        status = "✓ Found" if logo_path else "✗ Not found"
        print(f"{domain}: {status}")
    
    print("\nHTML integration examples:")
    print("\n1. Single logo tag:")
    print(get_logo_html_tag("nike.com"))
    
    print("\n2. Competitive comparison HTML (snippet):")
    html_snippet = generate_competitive_html("Technology", tech_domains)
    print(html_snippet[:500] + "...\n")
    
    print("===== Demonstration Complete =====\n")

if __name__ == "__main__":
    demonstrate_logo_service()