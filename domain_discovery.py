import json
import os
import random
import re
import trafilatura
import requests
from typing import List, Dict, Any
from urllib.parse import urlparse
import logging
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.cluster import KMeans

from config import CATEGORIES, DATA_DIR

# Setup logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# File to save seed URLs for each category
SEED_URLS_FILE = f"{DATA_DIR}/seed_urls.json"

# Default seed URLs if none are available
DEFAULT_SEED_URLS = {
    "finance": [
        "bankofamerica.com", "chase.com", "wellsfargo.com", "vanguard.com",
        "fidelity.com", "schwab.com", "coinbase.com", "robinhood.com"
    ],
    "healthcare": [
        "mayoclinic.org", "clevelandclinic.org", "hopkinsmedicine.org", "webmd.com",
        "healthline.com", "medlineplus.gov", "nih.gov", "cdc.gov"
    ],
    "legal": [
        "findlaw.com", "justia.com", "law.cornell.edu", "nolo.com",
        "legalzoom.com", "rocketlawyer.com", "avvo.com", "lawyers.com"
    ],
    "saas": [
        "salesforce.com", "hubspot.com", "zendesk.com", "slack.com",
        "monday.com", "asana.com", "notion.so", "airtable.com"
    ],
    "ai_infrastructure": [
        "huggingface.co", "openai.com", "tensorflow.org", "pytorch.org",
        "nvidia.com/en-us/ai", "cloud.google.com/vertex-ai", "aws.amazon.com/sagemaker", "azure.microsoft.com/en-us/products/machine-learning"
    ],
    "education": [
        "coursera.org", "edx.org", "udemy.com", "khanacademy.org",
        "pluralsight.com", "brilliant.org", "udacity.com", "skillshare.com"
    ],
    "ecommerce": [
        "shopify.com", "bigcommerce.com", "woocommerce.com", "magento.com",
        "squarespace.com", "wix.com/ecommerce", "volusion.com", "shift4shop.com"
    ],
    "enterprise_tech": [
        "oracle.com", "sap.com", "servicenow.com", "splunk.com",
        "vmware.com", "redhat.com", "ibm.com", "datastax.com"
    ]
}

def load_or_create_seed_urls() -> Dict[str, List[str]]:
    """Load seed URLs from file or create default if file doesn't exist."""
    if os.path.exists(SEED_URLS_FILE):
        with open(SEED_URLS_FILE, 'r') as f:
            return json.load(f)
    else:
        with open(SEED_URLS_FILE, 'w') as f:
            json.dump(DEFAULT_SEED_URLS, f)
        return DEFAULT_SEED_URLS

def extract_links_from_page(url: str) -> List[str]:
    """Extract links from a webpage."""
    try:
        # Ensure URL has http/https prefix
        if not url.startswith(('http://', 'https://')):
            url = f"https://{url}"
            
        downloaded = trafilatura.fetch_url(url)
        if not downloaded:
            return []
            
        # Use a regex pattern to find links in the HTML
        link_pattern = re.compile(r'href=["\'](https?://[^"\']+)["\']')
        links = link_pattern.findall(downloaded)
        
        # Extract base domains from links
        domains = []
        for link in links:
            try:
                parsed = urlparse(link)
                domain = parsed.netloc
                if domain and domain not in domains:
                    domains.append(domain)
            except:
                continue
                
        return domains
    except Exception as e:
        logger.error(f"Error extracting links from {url}: {e}")
        return []

def get_domain_content(domain: str) -> Dict[str, Any]:
    """Get content and metadata for a domain."""
    try:
        if not domain.startswith(('http://', 'https://')):
            url = f"https://{domain}"
        else:
            url = domain
            domain = urlparse(url).netloc
            
        downloaded = trafilatura.fetch_url(url)
        if not downloaded:
            return {"domain": domain, "content": "", "metadata": {}, "success": False}
            
        content = trafilatura.extract(downloaded, include_comments=False, include_tables=True)
        
        # Extract basic metadata
        title_match = re.search(r'<title>(.*?)</title>', downloaded, re.IGNORECASE)
        title = title_match.group(1) if title_match else ""
        
        description_match = re.search(r'<meta\s+name=["\'](description|Description)["\'].*?content=["\'](.*?)["\']', 
                                      downloaded, re.IGNORECASE)
        description = description_match.group(2) if description_match else ""
        
        # Look for schema markup
        schema_present = 'application/ld+json' in downloaded
        
        metadata = {
            "title": title,
            "description": description,
            "schema_present": schema_present
        }
        
        return {
            "domain": domain,
            "content": content if content else "",
            "metadata": metadata,
            "success": True
        }
    except Exception as e:
        logger.error(f"Error fetching content from {domain}: {e}")
        return {"domain": domain, "content": "", "metadata": {}, "success": False}

def categorize_domain(domain_content: str, domain_metadata: Dict) -> str:
    """
    Categorize a domain based on its content and metadata.
    This is a simple implementation - in a production system,
    you would use a more sophisticated ML model.
    """
    if not domain_content:
        return random.choice(CATEGORIES)
    
    # V2: Enhanced keyword-based categorization focused on trust verticals
    finance_keywords = ["bank", "invest", "finance", "loan", "mortgage", "credit", "trading", 
                       "stock", "market", "fund", "wealth", "retirement", "portfolio", 
                       "brokerage", "insurance", "payment", "crypto", "financial"]
    
    healthcare_keywords = ["health", "medical", "doctor", "patient", "hospital", "clinic", 
                          "treatment", "therapy", "diagnosis", "wellness", "medicine", 
                          "symptom", "disease", "pharmacy", "healthcare", "telehealth"]
    
    legal_keywords = ["law", "legal", "attorney", "lawyer", "court", "justice", "litigation",
                     "contract", "regulation", "compliance", "case", "firm", "statute",
                     "document", "rights", "filing", "counsel"]
    
    saas_keywords = ["software", "platform", "cloud", "solution", "service", "subscription",
                    "automation", "integration", "api", "dashboard", "interface", "crm",
                    "enterprise", "workflow", "collaboration", "productivity"]
    
    ai_infrastructure_keywords = ["ai", "machine learning", "neural", "model", "inference",
                                 "training", "dataset", "algorithm", "compute", "gpu",
                                 "transformer", "llm", "deep learning", "nlp", "vision"]
    
    education_keywords = ["learn", "course", "education", "class", "student", "teacher",
                         "school", "university", "degree", "training", "skill", "academy",
                         "curriculum", "certificate", "knowledge", "lesson"]
    
    ecommerce_keywords = ["shop", "store", "product", "cart", "checkout", "payment",
                         "merchant", "retail", "buy", "sell", "customer", "shipping",
                         "order", "inventory", "marketplace", "conversion"]
    
    enterprise_tech_keywords = ["enterprise", "business", "corporation", "solution",
                               "scale", "infrastructure", "database", "security",
                               "network", "compliance", "management", "analytics",
                               "integration", "system", "performance"]
    
    domain_content_lower = domain_content.lower()
    title_lower = domain_metadata.get("title", "").lower()
    description_lower = domain_metadata.get("description", "").lower()
    
    combined_text = domain_content_lower + " " + title_lower + " " + description_lower
    
    # Count keyword matches for each V2 category
    finance_score = sum(1 for keyword in finance_keywords if keyword in combined_text)
    healthcare_score = sum(1 for keyword in healthcare_keywords if keyword in combined_text)
    legal_score = sum(1 for keyword in legal_keywords if keyword in combined_text)
    saas_score = sum(1 for keyword in saas_keywords if keyword in combined_text)
    ai_score = sum(1 for keyword in ai_infrastructure_keywords if keyword in combined_text)
    education_score = sum(1 for keyword in education_keywords if keyword in combined_text)
    ecommerce_score = sum(1 for keyword in ecommerce_keywords if keyword in combined_text)
    enterprise_score = sum(1 for keyword in enterprise_tech_keywords if keyword in combined_text)
    
    # Determine category based on highest score
    scores = {
        "finance": finance_score,
        "healthcare": healthcare_score,
        "legal": legal_score,
        "saas": saas_score,
        "ai_infrastructure": ai_score,
        "education": education_score,
        "ecommerce": ecommerce_score,
        "enterprise_tech": enterprise_score
    }
    
    # Find the category with the highest score
    max_score = -1
    max_category = None
    for category, score in scores.items():
        if score > max_score:
            max_score = score
            max_category = category
    
    # If no clear winner, return a random category
    if max_score == 0 or max_category is None:
        return random.choice(CATEGORIES)
        
    return max_category

def discover_and_categorize_domains(limit_per_category: int = 100) -> Dict[str, List[Dict]]:
    """
    Discover domains across categories and categorize them.
    Returns a dictionary of categorized domains.
    """
    seed_urls = load_or_create_seed_urls()
    discovered_domains = {category: [] for category in CATEGORIES}
    
    for category, seeds in seed_urls.items():
        category_count = 0
        domain_set = set()
        
        # First add the seed domains themselves
        for seed in seeds:
            if category_count >= limit_per_category:
                break
                
            domain_info = get_domain_content(seed)
            if domain_info["success"]:
                # Verify the category using the content
                detected_category = categorize_domain(domain_info["content"], domain_info["metadata"])
                
                domain_info["category"] = detected_category
                discovered_domains[detected_category].append(domain_info)
                domain_set.add(domain_info["domain"])
                category_count += 1
        
        # Then discover more from each seed
        for seed in seeds:
            if category_count >= limit_per_category:
                break
                
            links = extract_links_from_page(seed)
            for link in links:
                if category_count >= limit_per_category:
                    break
                    
                # Skip if we've already processed this domain
                if link in domain_set:
                    continue
                    
                domain_info = get_domain_content(link)
                if domain_info["success"]:
                    detected_category = categorize_domain(domain_info["content"], domain_info["metadata"])
                    
                    domain_info["category"] = detected_category
                    discovered_domains[detected_category].append(domain_info)
                    domain_set.add(domain_info["domain"])
                    category_count += 1
    
    return discovered_domains

def save_domains(domains: Dict[str, List[Dict]]) -> None:
    """Save discovered domains to the database."""
    # Use database module to save domains
    import database as db
    domains_added = db.save_domains(domains)
    logger.info(f"Added {domains_added} new domains to the database")

def get_domains_for_testing(limit: int = 50) -> List[Dict]:
    """Get a list of domains for testing with LLMs."""
    # Use database module to get domains for testing
    import database as db
    
    # Check if we have domains in the database
    domains = db.get_domains_for_testing(limit)
    
    if not domains:
        # If no domains exist, discover some domains first
        logger.info("No domains found in database, discovering new domains")
        discovered = discover_and_categorize_domains(limit_per_category=25)
        save_domains(discovered)
        # Try again to get domains for testing
        domains = db.get_domains_for_testing(limit)
    
    return domains

if __name__ == "__main__":
    # Test functionality
    discovered_domains = discover_and_categorize_domains(limit_per_category=10)
    print(f"Discovered domains: {sum(len(domains) for domains in discovered_domains.values())}")
    for category, domains in discovered_domains.items():
        print(f"{category}: {len(domains)} domains")
    
    save_domains(discovered_domains)
    test_domains = get_domains_for_testing(limit=10)
    print(f"Selected {len(test_domains)} domains for testing")
