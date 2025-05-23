"""
Logo Client Library

This module provides a clean, reliable client library for retrieving brand logos
that works with every domain and is optimized for SEO and LLM use cases.
"""

import os
import base64
import json
import logging
import requests
import time
from io import BytesIO
from typing import Dict, Any, List, Optional, Tuple, Union
from datetime import datetime
from PIL import Image, ImageDraw, ImageFont
import colorsys
import hashlib

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Constants
LOGO_CACHE_DIR = "data/logos/client_lib"
CACHE_EXPIRY_DAYS = 30  # Cache logos for 30 days
DEFAULT_LOGO_SIZE = (200, 200)

# Ensure cache directory exists
os.makedirs(LOGO_CACHE_DIR, exist_ok=True)

class LogoClient:
    """
    Client for retrieving and managing brand logos with advanced features:
    - Multi-source logo retrieval
    - Smart caching
    - Fallback to high-quality generated logos
    - SEO optimization
    - LLM-friendly metadata
    """
    
    def __init__(self, cache_dir: Optional[str] = None, expiry_days: int = CACHE_EXPIRY_DAYS):
        """
        Initialize the logo client.
        
        Args:
            cache_dir: Directory to store cached logos (default: LOGO_CACHE_DIR)
            expiry_days: Number of days to cache logos (default: 30)
        """
        self.cache_dir = cache_dir or LOGO_CACHE_DIR
        self.expiry_days = expiry_days
        os.makedirs(self.cache_dir, exist_ok=True)
    
    def get_logo(self, domain: str, force_refresh: bool = False, size: Optional[Tuple[int, int]] = None) -> Dict[str, Any]:
        """
        Get logo for a domain with comprehensive fallbacks to ensure it always works.
        
        Args:
            domain: Domain to get logo for
            force_refresh: Whether to bypass cache
            size: Logo size as (width, height)
            
        Returns:
            Logo data with metadata
        """
        # Clean domain
        clean_domain = self._clean_domain(domain)
        
        # Check cache first unless forcing refresh
        if not force_refresh:
            cached_data = self._get_cached_logo(clean_domain)
            if cached_data:
                return cached_data
        
        # Try multiple sources
        logo_bytes, source = self._get_logo_from_sources(clean_domain)
        
        # If found, format the result
        if logo_bytes:
            company_name = self._extract_company_name(clean_domain)
            
            # Resize if needed
            if size and size != DEFAULT_LOGO_SIZE:
                try:
                    logo_bytes = self._resize_image(logo_bytes, size)
                except Exception as e:
                    logger.error(f"Error resizing logo: {e}")
            
            # Format metadata for SEO and LLM use
            logo_data = {
                "domain": clean_domain,
                "found": True,
                "source": source,
                "logo_data": base64.b64encode(logo_bytes).decode('utf-8'),
                "format": "png",
                "timestamp": datetime.now().isoformat(),
                "company_name": company_name,
                "full_name": self._enhance_company_name(company_name, clean_domain),
                "seo_keywords": self._generate_seo_keywords(clean_domain, company_name),
                "industries": self._guess_industries(clean_domain),
                "colors": self._extract_dominant_colors(logo_bytes),
                "size": self._get_image_size(logo_bytes)
            }
        else:
            # Generate a placeholder
            company_name = self._extract_company_name(clean_domain)
            size = size or DEFAULT_LOGO_SIZE
            placeholder_bytes = self._generate_logo(clean_domain, size)
            
            logo_data = {
                "domain": clean_domain,
                "found": False,
                "source": "generated",
                "logo_data": base64.b64encode(placeholder_bytes).decode('utf-8'),
                "format": "png",
                "timestamp": datetime.now().isoformat(),
                "company_name": company_name,
                "full_name": self._enhance_company_name(company_name, clean_domain),
                "seo_keywords": self._generate_seo_keywords(clean_domain, company_name),
                "industries": self._guess_industries(clean_domain),
                "colors": self._extract_dominant_colors(placeholder_bytes),
                "size": size
            }
        
        # Cache the result
        self._cache_logo(clean_domain, logo_data)
        
        return logo_data
    
    def get_logos_bulk(self, domains: List[str], force_refresh: bool = False, size: Optional[Tuple[int, int]] = None) -> List[Dict[str, Any]]:
        """
        Get logos for multiple domains in one call.
        
        Args:
            domains: List of domains to get logos for
            force_refresh: Whether to bypass cache
            size: Logo size as (width, height)
            
        Returns:
            List of logo data dictionaries
        """
        results = []
        for domain in domains:
            try:
                logo_data = self.get_logo(domain, force_refresh, size)
                results.append(logo_data)
            except Exception as e:
                logger.error(f"Error getting logo for {domain}: {e}")
                # Include a failed entry rather than skipping
                results.append({
                    "domain": domain,
                    "found": False,
                    "error": str(e),
                    "timestamp": datetime.now().isoformat()
                })
        
        return results
    
    def get_html_tag(self, domain: str, alt_text: Optional[str] = None, 
                    width: int = 100, class_name: str = "brand-logo",
                    lazy_load: bool = True) -> str:
        """
        Get HTML img tag for a domain logo that can be directly embedded.
        
        Args:
            domain: Domain to get logo for
            alt_text: Alt text for the image (default: company name)
            width: Image width in pixels
            class_name: CSS class name
            lazy_load: Whether to use lazy loading
            
        Returns:
            HTML img tag
        """
        logo_data = self.get_logo(domain)
        
        if not logo_data.get("logo_data"):
            return ""
        
        # Use company name for alt text if not provided
        if not alt_text:
            alt_text = logo_data.get("company_name", domain)
        
        # Create data URL for direct embedding
        data_url = f"data:image/png;base64,{logo_data['logo_data']}"
        
        # Add lazy loading if requested
        lazy_attr = 'loading="lazy"' if lazy_load else ''
        
        return f'<img src="{data_url}" alt="{alt_text}" width="{width}" class="{class_name}" {lazy_attr}>'
    
    def generate_comparison_html(self, domains: List[str], title: str = "Competitive Analysis") -> str:
        """
        Generate HTML for side-by-side comparison of domain logos.
        
        Args:
            domains: List of domains to compare
            title: Title for the comparison
            
        Returns:
            HTML for comparison view
        """
        logo_data_list = self.get_logos_bulk(domains)
        
        html = f"""
        <div class="logo-comparison">
            <h2>{title}</h2>
            <div class="logo-grid">
        """
        
        for logo_data in logo_data_list:
            domain = logo_data.get("domain", "")
            company_name = logo_data.get("company_name", domain)
            
            html += f"""
            <div class="logo-item">
                {self.get_html_tag(domain, width=120)}
                <div class="company-name">{company_name}</div>
            </div>
            """
        
        html += """
            </div>
        </div>
        <style>
            .logo-grid {
                display: flex;
                flex-wrap: wrap;
                gap: 20px;
                justify-content: center;
            }
            .logo-item {
                text-align: center;
                width: 150px;
            }
            .company-name {
                margin-top: 10px;
                font-weight: bold;
            }
        </style>
        """
        
        return html
    
    def save_logo_to_file(self, domain: str, output_path: Optional[str] = None,
                         size: Optional[Tuple[int, int]] = None) -> Optional[str]:
        """
        Save logo to a file.
        
        Args:
            domain: Domain to get logo for
            output_path: Path to save to (default: auto-generated)
            size: Size to resize to
            
        Returns:
            Path to saved file or None if failed
        """
        logo_data = self.get_logo(domain, size=size)
        
        if not logo_data.get("logo_data"):
            return None
        
        try:
            # Decode logo data
            logo_bytes = base64.b64decode(logo_data["logo_data"])
            
            # Determine output path if not provided
            if not output_path:
                output_dir = os.path.join(self.cache_dir, "exports")
                os.makedirs(output_dir, exist_ok=True)
                output_path = os.path.join(output_dir, f"{domain}.png")
            
            # Save to file
            with open(output_path, "wb") as f:
                f.write(logo_bytes)
            
            return output_path
        except Exception as e:
            logger.error(f"Error saving logo to file: {e}")
            return None
    
    # Private helper methods
    
    def _clean_domain(self, domain: str) -> str:
        """Clean domain name by removing www, http, etc."""
        # Ensure domain is lowercase
        domain = domain.lower().strip()
        
        # Remove protocol if present
        if "://" in domain:
            domain = domain.split("://")[1]
        
        # Remove www. prefix if present
        if domain.startswith("www."):
            domain = domain[4:]
        
        # Remove path if present
        domain = domain.split("/")[0]
        
        # Remove port if present
        domain = domain.split(":")[0]
        
        return domain
    
    def _get_cached_logo(self, domain: str) -> Optional[Dict[str, Any]]:
        """Get cached logo if it exists and is not expired."""
        cache_path = os.path.join(self.cache_dir, f"{domain}.json")
        
        if not os.path.exists(cache_path):
            return None
        
        try:
            with open(cache_path, "r") as f:
                cache_data = json.load(f)
            
            # Check if data is present and not expired
            if (cache_data.get("logo_data") and 
                "timestamp" in cache_data):
                
                # Check expiry
                cache_date = datetime.fromisoformat(cache_data["timestamp"])
                age_days = (datetime.now() - cache_date).days
                
                if age_days < self.expiry_days:
                    return cache_data
            
            return None
        except Exception as e:
            logger.error(f"Error reading cached logo: {e}")
            return None
    
    def _cache_logo(self, domain: str, logo_data: Dict[str, Any]) -> bool:
        """Cache logo data to file."""
        cache_path = os.path.join(self.cache_dir, f"{domain}.json")
        
        try:
            with open(cache_path, "w") as f:
                json.dump(logo_data, f)
            return True
        except Exception as e:
            logger.error(f"Error caching logo: {e}")
            return False
    
    def _get_logo_from_sources(self, domain: str) -> Tuple[Optional[bytes], str]:
        """Try multiple sources to get a logo."""
        # 1. Try Clearbit (best quality)
        logo_bytes = self._get_logo_from_clearbit(domain)
        if logo_bytes:
            return logo_bytes, "clearbit"
        
        # 2. Try Google (additional source)
        logo_bytes = self._get_logo_from_google(domain)
        if logo_bytes:
            return logo_bytes, "google"
        
        # 3. Try favicon as last resort
        logo_bytes = self._get_logo_from_favicon(domain)
        if logo_bytes:
            return logo_bytes, "favicon"
        
        # No logo found
        return None, "none"
    
    def _get_logo_from_clearbit(self, domain: str) -> Optional[bytes]:
        """Get logo from Clearbit's logo API."""
        try:
            url = f"https://logo.clearbit.com/{domain}"
            response = requests.get(url, timeout=5)
            
            if response.status_code == 200:
                return response.content
            return None
        except Exception as e:
            logger.error(f"Error fetching logo from Clearbit: {e}")
            return None
    
    def _get_logo_from_google(self, domain: str) -> Optional[bytes]:
        """Get logo from alternative source (placeholder for future API)."""
        # This is a placeholder - in production, you would implement
        # integration with another API source
        return None
    
    def _get_logo_from_favicon(self, domain: str) -> Optional[bytes]:
        """Get logo from website favicon."""
        try:
            urls = [
                f"https://{domain}/favicon.ico",
                f"https://{domain}/favicon.png",
                f"https://{domain}/apple-touch-icon.png",
                f"https://{domain}/apple-touch-icon-precomposed.png"
            ]
            
            for url in urls:
                try:
                    response = requests.get(url, timeout=3)
                    if response.status_code == 200 and response.content:
                        return response.content
                except:
                    continue
            
            return None
        except Exception as e:
            logger.error(f"Error fetching favicon: {e}")
            return None
    
    def _generate_logo(self, domain: str, size: Tuple[int, int] = DEFAULT_LOGO_SIZE) -> bytes:
        """Generate a high-quality placeholder logo for a domain."""
        company_name = self._extract_company_name(domain)
        
        # Choose color based on domain name for consistency
        # This creates a unique but consistent color for each domain
        domain_hash = int(hashlib.md5(domain.encode()).hexdigest(), 16) % 360
        
        hue = domain_hash / 360.0
        rgb = colorsys.hsv_to_rgb(hue, 0.8, 0.95)
        color = tuple(int(255 * c) for c in rgb)
        
        # Create background with gradient
        img = Image.new('RGB', size, color=(255, 255, 255))
        draw = ImageDraw.Draw(img)
        
        # Draw gradient
        for y in range(size[1]):
            ratio = y / size[1]
            r = int(color[0] * (1 - ratio * 0.3))
            g = int(color[1] * (1 - ratio * 0.3))
            b = int(color[2] * (1 - ratio * 0.3))
            draw.line([(0, y), (size[0], y)], fill=(r, g, b))
        
        # Try to load a font
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
        
        # Calculate text position
        text_width, text_height = font.getsize(letters) if hasattr(font, 'getsize') else (size[0]//3, size[1]//3)
        position = ((size[0] - text_width) // 2, (size[1] - text_height) // 2)
        
        # Draw shadow and text
        shadow_offset = max(1, min(size) // 50)
        draw.text((position[0] + shadow_offset, position[1] + shadow_offset), letters, fill=(0, 0, 0, 128), font=font)
        draw.text(position, letters, fill=(255, 255, 255), font=font)
        
        # Add company name at bottom
        try:
            small_font_size = max(10, min(size) // 10)
            small_font = ImageFont.truetype("DejaVuSans.ttf", small_font_size)
        except:
            small_font = ImageFont.load_default()
        
        # Truncate if too long
        max_chars = size[0] // (small_font_size // 2) 
        if len(company_name) > max_chars:
            company_name = company_name[:max_chars-3] + "..."
        
        # Get size and position
        text_width, text_height = small_font.getsize(company_name) if hasattr(small_font, 'getsize') else (size[0]//2, size[1]//10)
        small_position = ((size[0] - text_width) // 2, size[1] - text_height - size[1]//20)
        
        # Draw name
        draw.text((small_position[0]+1, small_position[1]+1), company_name, fill=(0, 0, 0, 128), font=small_font)
        draw.text(small_position, company_name, fill=(255, 255, 255), font=small_font)
        
        # Convert to bytes
        buffer = BytesIO()
        img.save(buffer, format="PNG")
        return buffer.getvalue()
    
    def _extract_company_name(self, domain: str) -> str:
        """Extract a human-readable company name from domain."""
        # Remove TLD
        name_part = domain.split('.')[0] 
        
        # Replace common separators with spaces
        name_part = name_part.replace('-', ' ').replace('_', ' ').replace('.', ' ')
        
        # Capitalize each word
        company_name = ' '.join(word.capitalize() for word in name_part.split())
        
        # Handle common abbreviations
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
    
    def _enhance_company_name(self, company_name: str, domain: str) -> str:
        """Add industry and business type hints to company name."""
        # Guess business type from TLD
        business_types = {
            'com': 'Corporation',
            'org': 'Organization',
            'edu': 'University',
            'gov': 'Government Agency',
            'io': 'Tech Company',
            'ai': 'AI Company',
            'app': 'App Developer',
            'dev': 'Software Company',
            'co': 'Company'
        }
        
        tld = domain.split('.')[-1] if '.' in domain else ''
        
        if tld in business_types and not any(suffix in company_name for suffix in ['Inc', 'LLC', 'Ltd', 'Co.', 'Corp']):
            return f"{company_name} {business_types[tld]}"
        
        return company_name
    
    def _generate_seo_keywords(self, domain: str, company_name: str) -> List[str]:
        """Generate SEO keywords for the domain."""
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
            "logo design",
            "company logo",
            "corporate branding",
            "brand recognition",
            "visual identity"
        ])
        
        # Ensure keywords are unique
        return list(dict.fromkeys(keywords))
    
    def _guess_industries(self, domain: str) -> List[str]:
        """Guess possible industries based on domain name."""
        # This is a simplified version - in production you would use
        # more sophisticated algorithms, industry databases, or AI
        
        name_part = domain.split('.')[0].lower()
        
        industry_keywords = {
            'tech': ['tech', 'software', 'app', 'ai', 'ml', 'code', 'dev', 'data', 'cloud', 'cyber', 'web'],
            'finance': ['bank', 'finance', 'money', 'invest', 'capital', 'wealth', 'fund', 'pay', 'cash', 'loan'],
            'healthcare': ['health', 'med', 'care', 'clinic', 'hospital', 'pharma', 'doctor', 'therapy', 'wellness'],
            'retail': ['shop', 'store', 'retail', 'market', 'buy', 'mall', 'outlet', 'goods', 'product'],
            'media': ['media', 'news', 'tv', 'radio', 'press', 'journal', 'blog', 'podcast', 'stream', 'tube'],
            'travel': ['travel', 'tour', 'trip', 'journey', 'vacation', 'hotel', 'booking', 'fly', 'air', 'cruise'],
            'education': ['edu', 'learn', 'school', 'college', 'university', 'academy', 'course', 'train', 'tutor'],
            'food': ['food', 'restaurant', 'eat', 'kitchen', 'meal', 'cook', 'chef', 'dish', 'dining', 'grill']
        }
        
        matched_industries = []
        
        for industry, keywords in industry_keywords.items():
            if any(keyword in name_part for keyword in keywords):
                matched_industries.append(industry)
        
        # If no match, add some general industries
        if not matched_industries:
            tld = domain.split('.')[-1] if '.' in domain else ''
            
            if tld == 'edu':
                matched_industries.append('education')
            elif tld == 'gov':
                matched_industries.append('government')
            elif tld == 'io' or tld == 'dev' or tld == 'ai':
                matched_industries.append('technology')
            elif tld == 'org':
                matched_industries.append('non-profit')
            else:
                matched_industries.append('business')
        
        return matched_industries
    
    def _extract_dominant_colors(self, image_bytes: bytes, num_colors: int = 3) -> List[str]:
        """Extract dominant colors from image as hex codes."""
        try:
            # Open image
            img = Image.open(BytesIO(image_bytes))
            
            # Convert to RGB if needed
            if img.mode != 'RGB':
                img.convert('RGB')
            
            # Resize for faster processing
            img = img.resize((100, 100))
            
            # Get pixel data
            pixels = list(img.getdata())
            
            # Count colors
            color_counts = {}
            for pixel in pixels:
                if pixel in color_counts:
                    color_counts[pixel] += 1
                else:
                    color_counts[pixel] = 1
            
            # Get most common colors
            sorted_colors = sorted(color_counts.items(), key=lambda x: x[1], reverse=True)
            top_colors = [color for color, _ in sorted_colors[:num_colors]]
            
            # Convert to hex
            hex_colors = [f"#{r:02x}{g:02x}{b:02x}" for r, g, b in top_colors]
            
            return hex_colors
        except Exception as e:
            logger.error(f"Error extracting colors: {e}")
            return ["#000000"]  # Default to black
    
    def _get_image_size(self, image_bytes: bytes) -> Tuple[int, int]:
        """Get image dimensions."""
        try:
            img = Image.open(BytesIO(image_bytes))
            return img.size
        except Exception as e:
            logger.error(f"Error getting image size: {e}")
            return (0, 0)
    
    def _resize_image(self, image_bytes: bytes, size: Tuple[int, int]) -> bytes:
        """Resize an image to the given dimensions."""
        try:
            img = Image.open(BytesIO(image_bytes))
            
            # Resize with antialiasing
            img = img.resize(size, Image.LANCZOS if hasattr(Image, 'LANCZOS') else Image.ANTIALIAS)
            
            # Save to bytes
            buffer = BytesIO()
            img.save(buffer, format="PNG")
            return buffer.getvalue()
        except Exception as e:
            logger.error(f"Error resizing image: {e}")
            return image_bytes

# Create a singleton instance for easy import
logo_client = LogoClient()

# Simplified API for direct usage
def get_logo(domain: str, force_refresh: bool = False, size: Optional[Tuple[int, int]] = None) -> Dict[str, Any]:
    """Get logo for a domain."""
    return logo_client.get_logo(domain, force_refresh, size)

def get_logos_bulk(domains: List[str], force_refresh: bool = False, size: Optional[Tuple[int, int]] = None) -> List[Dict[str, Any]]:
    """Get logos for multiple domains."""
    return logo_client.get_logos_bulk(domains, force_refresh, size)

def get_html_tag(domain: str, alt_text: Optional[str] = None, width: int = 100) -> str:
    """Get HTML img tag for domain logo."""
    return logo_client.get_html_tag(domain, alt_text, width)

def generate_comparison_html(domains: List[str], title: str = "Competitive Analysis") -> str:
    """Generate HTML for side-by-side comparison."""
    return logo_client.generate_comparison_html(domains, title)

def save_logo_to_file(domain: str, output_path: Optional[str] = None, size: Optional[Tuple[int, int]] = None) -> Optional[str]:
    """Save logo to file."""
    return logo_client.save_logo_to_file(domain, output_path, size)