import json
import os
import re
import logging
import time
from typing import Dict, List, Any
import numpy as np
from datetime import datetime

# Setup logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def calculate_cosine_similarity(text1: str, text2: str) -> float:
    """
    Calculate cosine similarity between two text strings.
    Used to compare ground truth content with LLM response.
    
    Args:
        text1: First text string
        text2: Second text string
        
    Returns:
        Similarity score between 0 and 1
    """
    # Normalize and tokenize
    text1 = re.sub(r'[^\w\s]', '', text1.lower())
    text2 = re.sub(r'[^\w\s]', '', text2.lower())
    
    words1 = text1.split()
    words2 = text2.split()
    
    # Create vocabulary
    vocabulary = list(set(words1 + words2))
    
    # Create vectors
    vector1 = np.zeros(len(vocabulary))
    vector2 = np.zeros(len(vocabulary))
    
    for i, word in enumerate(vocabulary):
        vector1[i] = words1.count(word)
        vector2[i] = words2.count(word)
    
    # Calculate cosine similarity
    dot_product = np.dot(vector1, vector2)
    norm1 = np.linalg.norm(vector1)
    norm2 = np.linalg.norm(vector2)
    
    if norm1 == 0 or norm2 == 0:
        return 0.0
    
    similarity = dot_product / (norm1 * norm2)
    return similarity

def calculate_z_score(value: float, mean: float, std_dev: float) -> float:
    """
    Calculate z-score for a value.
    
    Args:
        value: The value to calculate z-score for
        mean: Mean of the population
        std_dev: Standard deviation of the population
        
    Returns:
        The z-score
    """
    if std_dev == 0:
        return 0.0
    
    return (value - mean) / std_dev

def format_timestamp_for_filename(timestamp: float = None) -> str:
    """
    Format a timestamp for use in filenames.
    
    Args:
        timestamp: Unix timestamp (default: current time)
        
    Returns:
        Formatted timestamp string
    """
    if timestamp is None:
        timestamp = time.time()
    
    dt = datetime.fromtimestamp(timestamp)
    return dt.strftime("%Y%m%d_%H%M%S")

def safe_domain_to_filename(domain: str) -> str:
    """
    Convert a domain to a safe filename.
    
    Args:
        domain: Domain name
        
    Returns:
        Safe filename string
    """
    return domain.replace('.', '_').replace(':', '_').replace('/', '_')

def extract_domain_from_url(url: str) -> str:
    """
    Extract the domain name from a URL.
    
    Args:
        url: Full URL
        
    Returns:
        Domain name
    """
    # Strip protocol
    if '://' in url:
        url = url.split('://', 1)[1]
    
    # Strip path
    if '/' in url:
        url = url.split('/', 1)[0]
    
    # Strip query/fragment
    if '?' in url:
        url = url.split('?', 1)[0]
    
    if '#' in url:
        url = url.split('#', 1)[0]
    
    return url

def get_citation_color(citation_type: str) -> str:
    """
    Get a color code for a citation type.
    
    Args:
        citation_type: One of 'direct', 'paraphrased', or 'none'
        
    Returns:
        Hex color code
    """
    if citation_type == 'direct':
        return '#4CAF50'  # Green
    elif citation_type == 'paraphrased':
        return '#2196F3'  # Blue
    else:
        return '#F44336'  # Red

def get_trend_icon(trend: str) -> str:
    """
    Get an icon for a trend direction.
    
    Args:
        trend: One of 'rising', 'falling', or 'stable'
        
    Returns:
        Trend icon
    """
    if trend == 'rising':
        return '↗️'
    elif trend == 'falling':
        return '↘️'
    else:
        return '→'

if __name__ == "__main__":
    # Test functionality
    text1 = "This is a test of cosine similarity calculation"
    text2 = "Calculating cosine similarity for this test"
    similarity = calculate_cosine_similarity(text1, text2)
    print(f"Similarity: {similarity:.4f}")
    
    z = calculate_z_score(120, 100, 15)
    print(f"Z-score: {z:.4f}")
    
    print(f"Timestamp: {format_timestamp_for_filename()}")
    print(f"Safe domain: {safe_domain_to_filename('example.com/path?query')}")
    print(f"Extracted domain: {extract_domain_from_url('https://example.com/path?query')}")
