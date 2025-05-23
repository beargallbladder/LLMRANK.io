"""
Test Logo Service

This script tests the improved Logo Service by fetching logos for various domains.
"""

import requests
import base64
import os
import time
from PIL import Image
from io import BytesIO

# Create output directory
output_dir = "test_logos"
os.makedirs(output_dir, exist_ok=True)

# Test domains
test_domains = [
    "apple.com",
    "google.com",
    "microsoft.com",
    "amazon.com",
    "meta.com",
    "netflix.com",
    "tesla.com",
    "walmart.com",
    "target.com"
]

def test_health():
    """Test the health endpoint."""
    try:
        response = requests.get("http://localhost:6600/api/health")
        print(f"Health check: {response.status_code}")
        print(response.json())
        return response.status_code == 200
    except Exception as e:
        print(f"Error testing health endpoint: {e}")
        return False

def test_get_logo(domain):
    """Test getting a logo for a domain."""
    try:
        response = requests.get(f"http://localhost:6600/api/logos/{domain}")
        print(f"Logo for {domain}: {response.status_code}")
        
        if response.status_code == 200:
            logo_data = response.json()
            
            # Save the logo data for inspection
            with open(f"{output_dir}/{domain}_data.json", "w") as f:
                import json
                json.dump(logo_data, f, indent=2)
            
            # If logo data is present, save the image
            if logo_data.get("logo_data"):
                image_bytes = base64.b64decode(logo_data["logo_data"])
                img = Image.open(BytesIO(image_bytes))
                img.save(f"{output_dir}/{domain}.png")
                
                print(f"  - Saved logo for {domain}")
                return True
            else:
                print(f"  - No logo found for {domain}")
                return False
        
        return False
    except Exception as e:
        print(f"Error testing logo for {domain}: {e}")
        return False

def test_bulk_logos(domains):
    """Test getting logos for multiple domains in bulk."""
    try:
        response = requests.post(
            "http://localhost:6600/api/logos/bulk",
            json=domains
        )
        print(f"Bulk logos: {response.status_code}")
        
        if response.status_code == 200:
            logos_data = response.json()
            
            # Save the bulk response for inspection
            with open(f"{output_dir}/bulk_response.json", "w") as f:
                import json
                json.dump(logos_data, f, indent=2)
            
            success_count = 0
            for logo_data in logos_data:
                domain = logo_data.get("domain")
                if logo_data.get("logo_data"):
                    success_count += 1
            
            print(f"  - Found logos for {success_count}/{len(domains)} domains")
            return success_count > 0
        
        return False
    except Exception as e:
        print(f"Error testing bulk logos: {e}")
        return False

def main():
    """Run the tests."""
    print("\n===== TESTING LOGO SERVICE =====\n")
    
    # Test the health endpoint
    health_ok = test_health()
    print(f"\nHealth check: {'✓ PASS' if health_ok else '✗ FAIL'}")
    
    # Test getting logos for individual domains
    logo_results = []
    for domain in test_domains[:3]:  # Test first 3 domains
        result = test_get_logo(domain)
        logo_results.append(result)
    
    logo_success = any(logo_results)
    print(f"\nIndividual logos: {'✓ PASS' if logo_success else '✗ FAIL'}")
    
    # Test getting logos in bulk
    bulk_ok = test_bulk_logos(test_domains)
    print(f"\nBulk logos: {'✓ PASS' if bulk_ok else '✗ FAIL'}")
    
    # Overall result
    overall = health_ok and (logo_success or bulk_ok)
    print(f"\nOverall test: {'✓ PASS' if overall else '✗ FAIL'}")
    
    print("\nLogo files saved to the 'test_logos' directory")
    print("\n===============================\n")

if __name__ == "__main__":
    main()