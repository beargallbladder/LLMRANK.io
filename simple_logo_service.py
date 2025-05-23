"""
Simple Logo Service

This module provides a streamlined logo service for the LLMRank platform
that doesn't rely on external dependencies.
"""

import os
import base64
import json
import logging
from typing import Dict, Any, List, Optional
import streamlit as st
import requests
from PIL import Image, ImageDraw, ImageFont
import io
from datetime import datetime

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Constants
LOGO_CACHE_DIR = "data/logos/simple"
os.makedirs(LOGO_CACHE_DIR, exist_ok=True)

def generate_placeholder_logo(domain: str, size: tuple = (200, 200)) -> bytes:
    """
    Generate a high-quality placeholder logo for a domain that looks professional and is SEO-friendly.
    
    Args:
        domain: Domain name
        size: Image size as (width, height)
        
    Returns:
        PNG image data as bytes
    """
    # Extract company name from domain for SEO
    company_name = domain.split('.')[0]
    company_name = company_name.replace('-', ' ').replace('_', ' ')
    company_name = ' '.join(word.capitalize() for word in company_name.split())
    
    # Choose color based on domain name for consistency
    # This creates a unique but consistent color for each domain
    domain_hash = hash(domain) % 360  # 0-359 for hue
    import colorsys
    hue = domain_hash / 360.0  # Convert to 0-1 range
    rgb = colorsys.hsv_to_rgb(hue, 0.8, 0.9)  # Saturation 0.8, Value 0.9
    color = tuple(int(255 * c) for c in rgb)
    
    # Create gradient background for more professional look
    img = Image.new('RGB', size, color=(255, 255, 255))
    draw = ImageDraw.Draw(img)
    
    # Draw rounded rectangle with gradient
    # Since PIL doesn't support gradients directly, we'll create an approximation
    for y in range(size[1]):
        # Calculate gradient color
        ratio = y / size[1]
        r = int(color[0] * (1 - ratio * 0.2))
        g = int(color[1] * (1 - ratio * 0.2))
        b = int(color[2] * (1 - ratio * 0.2))
        draw.line([(0, y), (size[0], y)], fill=(r, g, b))
    
    # Try to load a font, fallback to default with increased size
    try:
        font_size = min(size) // 3
        font = ImageFont.truetype("DejaVuSans-Bold.ttf", font_size)
    except:
        try:
            font = ImageFont.truetype("DejaVuSans.ttf", font_size)
        except:
            font = ImageFont.load_default()
    
    # Get initial letters from company name (up to 2 letters)
    if company_name and len(company_name) > 0:
        words = company_name.split()
        if len(words) > 1:
            letters = words[0][0] + words[1][0]
        else:
            letters = company_name[0]
        letters = letters.upper()
    else:
        letters = domain[0].upper()
    
    # Calculate text position to center it
    w, h = draw.textsize(letters, font=font) if hasattr(draw, 'textsize') else (size[0]//3, size[1]//3)
    position = ((size[0] - w) // 2, (size[1] - h) // 2)
    
    # Draw text in white with shadow for depth
    # Shadow
    shadow_offset = max(1, min(size) // 50)
    shadow_pos = (position[0] + shadow_offset, position[1] + shadow_offset)
    draw.text(shadow_pos, letters, fill=(0, 0, 0, 100), font=font)
    
    # Main text
    draw.text(position, letters, fill=(255, 255, 255), font=font)
    
    # Add company name at bottom for SEO visibility
    try:
        small_font_size = max(10, min(size) // 10)
        small_font = ImageFont.truetype("DejaVuSans.ttf", small_font_size)
    except:
        small_font = ImageFont.load_default()
    
    # Truncate company name if too long
    max_chars = size[0] // (small_font_size // 2)
    if len(company_name) > max_chars:
        company_name = company_name[:max_chars-3] + "..."
    
    sw, sh = draw.textsize(company_name, font=small_font) if hasattr(draw, 'textsize') else (size[0]//2, size[1]//10)
    small_position = ((size[0] - sw) // 2, size[1] - sh - size[1]//20)
    
    # Draw company name with slight shadow
    draw.text((small_position[0]+1, small_position[1]+1), company_name, fill=(0, 0, 0, 100), font=small_font)
    draw.text(small_position, company_name, fill=(255, 255, 255), font=small_font)
    
    # Convert to bytes
    buffer = io.BytesIO()
    img.save(buffer, format="PNG")
    return buffer.getvalue()

def clean_domain(domain: str) -> str:
    """
    Clean a domain name by removing www, http, etc.
    
    Args:
        domain: Domain name to clean
        
    Returns:
        Cleaned domain name
    """
    # Lowercase
    domain = domain.lower()
    
    # Remove protocol
    if "://" in domain:
        domain = domain.split("://")[1]
    
    # Remove www.
    if domain.startswith("www."):
        domain = domain[4:]
    
    # Remove path
    domain = domain.split("/")[0]
    
    # Remove port
    domain = domain.split(":")[0]
    
    return domain

def get_logo_from_clearbit(domain: str) -> Optional[bytes]:
    """
    Try to get a logo from Clearbit's logo API.
    
    Args:
        domain: Domain name
        
    Returns:
        Logo image data or None if not found
    """
    try:
        url = f"https://logo.clearbit.com/{domain}"
        response = requests.get(url, timeout=5)
        
        if response.status_code == 200:
            return response.content
        return None
    except Exception as e:
        logger.error(f"Error fetching logo from Clearbit: {e}")
        return None

def get_logo_from_brandfetch(domain: str) -> Optional[bytes]:
    """
    Try to get a logo from Brandfetch API (fallback).
    This is a placeholder for a real integration - actual implementation
    would require an API key.
    
    Args:
        domain: Domain name
        
    Returns:
        Logo image data or None if not found
    """
    # In a real implementation, you would call the Brandfetch API
    # and extract the logo URL from the response
    return None

def get_logo_from_favicon(domain: str) -> Optional[bytes]:
    """
    Try to get a logo from the website's favicon.
    
    Args:
        domain: Domain name
        
    Returns:
        Logo image data or None if not found
    """
    try:
        url = f"https://{domain}/favicon.ico"
        response = requests.get(url, timeout=5)
        
        if response.status_code == 200 and response.content:
            return response.content
        return None
    except Exception as e:
        logger.error(f"Error fetching favicon for {domain}: {e}")
        return None

def get_logo(domain: str, force_refresh: bool = False) -> Dict[str, Any]:
    """
    Get a logo for a domain (from cache or generate).
    Enhanced to try multiple sources and ensure it works for every domain.
    
    Args:
        domain: Domain name
        force_refresh: Whether to bypass cache
        
    Returns:
        Logo data dictionary
    """
    # Clean the domain
    domain = clean_domain(domain)
    
    # Check cache first
    cache_path = os.path.join(LOGO_CACHE_DIR, f"{domain}.json")
    
    if not force_refresh and os.path.exists(cache_path):
        try:
            with open(cache_path, 'r') as f:
                cache_data = json.load(f)
                # Check if the cached data is complete and not too old (max 30 days)
                if (cache_data.get("logo_data") and 
                    "timestamp" in cache_data and
                    (datetime.now() - datetime.fromisoformat(cache_data["timestamp"])).days < 30):
                    return cache_data
        except Exception as e:
            logger.error(f"Error loading cached logo: {e}")
    
    # Try multiple sources in order of quality
    
    # 1. Try Clearbit (best quality)
    logo_bytes = get_logo_from_clearbit(domain)
    source = "clearbit"
    
    # 2. Try Brandfetch if Clearbit failed
    if not logo_bytes:
        logo_bytes = get_logo_from_brandfetch(domain)
        source = "brandfetch"
    
    # 3. Try website favicon as last resort
    if not logo_bytes:
        logo_bytes = get_logo_from_favicon(domain)
        source = "favicon"
    
    if logo_bytes:
        # Found a real logo from one of the sources
        logo_data = {
            "domain": domain,
            "found": True,
            "source": source,
            "logo_data": base64.b64encode(logo_bytes).decode('utf-8'),
            "format": "png",
            "timestamp": datetime.now().isoformat(),
            "company_name": extract_company_name_from_domain(domain),
            "seo_keywords": generate_seo_keywords(domain)
        }
    else:
        # Generate a placeholder with enhanced design
        placeholder_bytes = generate_placeholder_logo(domain)
        logo_data = {
            "domain": domain,
            "found": False,
            "source": "generated",
            "logo_data": base64.b64encode(placeholder_bytes).decode('utf-8'),
            "format": "png",
            "timestamp": datetime.now().isoformat(),
            "company_name": extract_company_name_from_domain(domain),
            "seo_keywords": generate_seo_keywords(domain)
        }
    
    # Save to cache
    try:
        with open(cache_path, 'w') as f:
            json.dump(logo_data, f)
    except Exception as e:
        logger.error(f"Error saving logo to cache: {e}")
    
    return logo_data

def extract_company_name_from_domain(domain: str) -> str:
    """
    Extract a human-readable company name from a domain for SEO purposes.
    
    Args:
        domain: Clean domain name
        
    Returns:
        Company name
    """
    # Remove TLD
    name_part = domain.split('.')[0]
    
    # Replace common separators with spaces
    name_part = name_part.replace('-', ' ').replace('_', ' ').replace('.', ' ')
    
    # Capitalize each word
    company_name = ' '.join(word.capitalize() for word in name_part.split())
    
    # Handle common abbreviations and post-processing
    # (like Inc, LLC, etc. or special cases like IBM, BMW)
    common_abbreviations = {
        'Ibm': 'IBM', 'Bmw': 'BMW', 'Hp': 'HP', 'Bbc': 'BBC', 
        'Cnn': 'CNN', 'Nbc': 'NBC', 'Abc': 'ABC', 'Mtv': 'MTV',
        'Inc': 'Inc.', 'Llc': 'LLC', 'Ltd': 'Ltd.', 'Co': 'Co.',
        'Corp': 'Corp.', 'Intl': 'International'
    }
    
    words = company_name.split()
    for i, word in enumerate(words):
        if word in common_abbreviations:
            words[i] = common_abbreviations[word]
    
    return ' '.join(words)

def generate_seo_keywords(domain: str) -> List[str]:
    """
    Generate SEO keywords for the domain.
    
    Args:
        domain: Domain name
        
    Returns:
        List of SEO keywords
    """
    # Extract company name
    company_name = extract_company_name_from_domain(domain)
    
    # Base keywords
    keywords = [
        domain,
        company_name,
        f"{company_name} logo",
        f"{company_name} brand"
    ]
    
    # Add industry-specific keywords based on TLD
    tld = domain.split('.')[-1] if '.' in domain else ''
    
    tld_keywords = {
        'com': ['business', 'company', 'commercial'],
        'org': ['organization', 'non-profit', 'nonprofit'],
        'edu': ['education', 'university', 'college', 'school'],
        'gov': ['government', 'official', 'federal'],
        'io': ['technology', 'startup', 'tech company'],
        'ai': ['artificial intelligence', 'AI company', 'machine learning'],
        'app': ['application', 'mobile app', 'software'],
        'dev': ['developer', 'software', 'coding'],
        'net': ['network', 'internet', 'web service']
    }
    
    if tld in tld_keywords:
        keywords.extend([f"{company_name} {keyword}" for keyword in tld_keywords[tld]])
    
    # Add common search terms
    keywords.extend([
        f"{company_name} official",
        f"{company_name} website",
        f"{company_name} official logo",
        "brand identity",
        "logo design"
    ])
    
    # Ensure keywords are unique
    return list(dict.fromkeys(keywords))

def main():
    """Main function for the Streamlit app."""
    st.set_page_config(
        page_title="MCP Logo Service",
        page_icon="🖼️",
        layout="wide"
    )
    
    st.title("MCP Logo Service")
    st.write("This service provides brand logos for the LLMRank platform.")
    
    col1, col2 = st.columns([1, 1])
    
    with col1:
        st.subheader("Get Logo for Domain")
        domain = st.text_input("Enter domain", "apple.com")
        force_refresh = st.checkbox("Force refresh (ignore cache)")
        
        if st.button("Get Logo"):
            logo_data = get_logo(domain, force_refresh)
            
            if logo_data.get("logo_data"):
                st.success(f"Logo found for {domain}")
                img_data = base64.b64decode(logo_data["logo_data"])
                st.image(img_data, caption=f"Logo for {domain}")
                
                st.json(logo_data)
            else:
                st.error(f"No logo found for {domain}")
    
    with col2:
        st.subheader("Bulk Logo Retrieval")
        
        domains_text = st.text_area(
            "Enter domains (one per line)", 
            "apple.com\ngoogle.com\nmicrosoft.com\namazon.com"
        )
        
        if st.button("Get Bulk Logos"):
            domains = [d.strip() for d in domains_text.split("\n") if d.strip()]
            
            results = []
            for domain in domains:
                with st.spinner(f"Getting logo for {domain}..."):
                    logo_data = get_logo(domain)
                    results.append(logo_data)
                    
                    if logo_data.get("logo_data"):
                        img_data = base64.b64decode(logo_data["logo_data"])
                        st.image(img_data, caption=f"Logo for {domain}", width=100)
            
            st.success(f"Retrieved {len(results)} logos")
    
    # API Documentation section
    st.markdown("---")
    st.header("API Documentation")
    
    st.markdown("""
    ### GET /logo/{domain}
    Returns logo data for a specific domain.
    
    **Example:**
    ```
    GET /logo/apple.com
    ```
    
    ### POST /logos/bulk
    Get logos for multiple domains at once.
    
    **Example Request:**
    ```json
    {
        "domains": ["apple.com", "google.com", "microsoft.com"]
    }
    ```
    """)

if __name__ == "__main__":
    main()