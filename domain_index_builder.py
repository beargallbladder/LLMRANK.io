"""
Domain Index Builder
Creates a comprehensive index of all domains with actual data
"""

import json
import os
from collections import defaultdict
import re

def normalize_domain_name(domain):
    """
    Normalize domain to clean company name
    """
    # Remove common prefixes and suffixes
    domain = domain.lower()
    domain = re.sub(r'^(www\.|http://|https://)', '', domain)
    domain = re.sub(r'/$', '', domain)
    
    # Map common domains to their company names
    domain_mappings = {
        'microsoft.com': 'Microsoft',
        'google.com': 'Google', 
        'amazon.com': 'Amazon',
        'apple.com': 'Apple',
        'facebook.com': 'Meta',
        'meta.com': 'Meta',
        'twitter.com': 'Twitter',
        'linkedin.com': 'LinkedIn',
        'netflix.com': 'Netflix',
        'salesforce.com': 'Salesforce',
        'oracle.com': 'Oracle',
        'ibm.com': 'IBM',
        'adobe.com': 'Adobe',
        'stripe.com': 'Stripe',
        'shopify.com': 'Shopify',
        'zoom.us': 'Zoom',
        'slack.com': 'Slack',
        'dropbox.com': 'Dropbox',
        'wellsfargo.com': 'Wells Fargo',
        'jpmorgan.com': 'JPMorgan Chase',
        'bankofamerica.com': 'Bank of America',
        'chase.com': 'JPMorgan Chase',
    }
    
    if domain in domain_mappings:
        return domain_mappings[domain]
    
    # Extract company name from domain
    parts = domain.split('.')
    if len(parts) >= 2:
        company = parts[0]
        # Clean up common patterns
        company = re.sub(r'(corp|inc|llc|ltd|co)$', '', company)
        company = company.replace('-', ' ').replace('_', ' ')
        company = company.title()
        return company
    
    return domain.title()

def build_domain_index():
    """
    Build comprehensive domain index from all data sources
    """
    domain_data = {}
    
    # Collect from insights
    try:
        with open('data/insights/insight_log.json', 'r') as f:
            insights = json.load(f)
        
        for insight in insights:
            domain = insight.get('domain')
            if domain:
                if domain not in domain_data:
                    domain_data[domain] = {
                        'domain': domain,
                        'display_name': normalize_domain_name(domain),
                        'has_insights': True,
                        'has_results': False,
                        'has_trends': False,
                        'quality_score': 0,
                        'insight_count': 0,
                        'last_updated': None
                    }
                
                domain_data[domain]['insight_count'] += 1
                quality = insight.get('quality_score', 0)
                if quality > domain_data[domain]['quality_score']:
                    domain_data[domain]['quality_score'] = quality
                
                timestamp = insight.get('timestamp')
                if timestamp and (not domain_data[domain]['last_updated'] or timestamp > domain_data[domain]['last_updated']):
                    domain_data[domain]['last_updated'] = timestamp
                    
    except Exception as e:
        print(f"Error reading insights: {e}")
    
    # Collect from results
    try:
        with open('data/results.json', 'r') as f:
            results = json.load(f)
        
        for result in results:
            domain = result.get('domain')
            if domain:
                if domain not in domain_data:
                    domain_data[domain] = {
                        'domain': domain,
                        'display_name': normalize_domain_name(domain),
                        'has_insights': False,
                        'has_results': True,
                        'has_trends': False,
                        'quality_score': 0,
                        'insight_count': 0,
                        'last_updated': None
                    }
                else:
                    domain_data[domain]['has_results'] = True
                    
    except Exception as e:
        print(f"Error reading results: {e}")
    
    # Collect from trends
    try:
        with open('data/trends.json', 'r') as f:
            trends = json.load(f)
        
        for trend in trends:
            domain = trend.get('domain')
            if domain:
                if domain not in domain_data:
                    domain_data[domain] = {
                        'domain': domain,
                        'display_name': normalize_domain_name(domain),
                        'has_insights': False,
                        'has_results': False,
                        'has_trends': True,
                        'quality_score': 0,
                        'insight_count': 0,
                        'last_updated': None
                    }
                else:
                    domain_data[domain]['has_trends'] = True
                    
    except Exception as e:
        print(f"Error reading trends: {e}")
    
    # Convert to sorted list for dropdown
    domains_list = list(domain_data.values())
    
    # Sort by: 1) Quality score (desc), 2) Insight count (desc), 3) Display name (asc)
    domains_list.sort(key=lambda x: (
        -x['quality_score'],
        -x['insight_count'],
        x['display_name']
    ))
    
    # Save the index
    os.makedirs('data', exist_ok=True)
    with open('data/domain_index.json', 'w') as f:
        json.dump(domains_list, f, indent=2)
    
    return domains_list

def get_domain_suggestions(query=""):
    """
    Get filtered domain suggestions for dropdown
    """
    try:
        with open('data/domain_index.json', 'r') as f:
            domains = json.load(f)
    except:
        domains = build_domain_index()
    
    if not query:
        return domains[:50]  # Top 50 domains
    
    query = query.lower()
    filtered = []
    
    for domain in domains:
        if (query in domain['domain'].lower() or 
            query in domain['display_name'].lower()):
            filtered.append(domain)
    
    return filtered[:20]  # Top 20 matches

if __name__ == "__main__":
    print("🔧 Building domain index...")
    domains = build_domain_index()
    print(f"✅ Indexed {len(domains)} domains")
    
    print("\nTop domains by quality:")
    for domain in domains[:10]:
        print(f"  • {domain['display_name']} ({domain['domain']}) - Quality: {domain['quality_score']:.2f}")