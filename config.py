import os
from datetime import datetime

# Admin access - V2: Only this email can access secure observability layer
ADMIN_EMAIL = "samkim@samkim.com"
ADMIN_PASSWORD = "LLMPageRank2025!"  # Secure password for production use

# LLM API configuration
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
ANTHROPIC_API_KEY = os.getenv("ANTHROPIC_API_KEY")
HUGGINGFACE_API_KEY = os.getenv("HUGGINGFACE_API_KEY")

# Data storage paths - V2: Added structured storage tiers
DATA_DIR = "data"
DOMAINS_FILE = f"{DATA_DIR}/domains.json"
RESULTS_DIR = f"{DATA_DIR}/results"
TRENDS_FILE = f"{DATA_DIR}/trends.json"
TRENDS_DIR = f"{DATA_DIR}/trends"
INTERNAL_DIR = f"{DATA_DIR}/internal/secure"
ADMIN_DIR = f"{DATA_DIR}/admin/visual"
PUBLIC_DIR = f"{DATA_DIR}/public/export"

# Ensure all data directories exist
for directory in [DATA_DIR, RESULTS_DIR, TRENDS_DIR, 
                  INTERNAL_DIR, ADMIN_DIR, PUBLIC_DIR]:
    os.makedirs(directory, exist_ok=True)

# V2: Updated categories focused on verticals where trust = money
CATEGORIES = [
    "finance", 
    "healthcare", 
    "legal", 
    "saas", 
    "ai_infrastructure", 
    "education", 
    "ecommerce",
    "enterprise_tech"
]

# Domain discovery settings - V2: More targeted criteria
MAX_DOMAINS_PER_CATEGORY = 1000
TARGET_CRITERIA = {
    "has_ads": 3,           # Weight for domains with active ad spend
    "has_schema": 3,         # Weight for domains with schema markup
    "has_seo_stack": 2,      # Weight for domains with SEO tools
    "has_conversion_path": 4 # Weight for domains with clear conversion paths
}

# LLM Models - V2: Track model versions
LLM_MODELS = {
    "gpt-4o": {
        "name": "OpenAI GPT-4o",
        "version": "20230501",
        "provider": "OpenAI",
        "capabilities": ["web_search", "reasoning", "summarization"]
    },
    "claude-3-5-sonnet-20241022": {
        "name": "Anthropic Claude 3.5", 
        "version": "20241022",
        "provider": "Anthropic",
        "capabilities": ["reasoning", "summarization", "long_context"]
    },
    "mixtral-8x7b": {
        "name": "Mixtral 8x7B",
        "version": "latest",
        "provider": "Mistral AI",
        "capabilities": ["reasoning", "summarization"]
    }
}

# Prompt configuration - V2: Added versioning and metadata
PROMPT_VERSION = "1.0"
PROMPT_CATEGORIES = {
    "informational": "Questions seeking factual information",
    "transactional": "Queries with buying intent",
    "decision_support": "Requests for recommendations or comparisons"
}

# Citation types
CITATION_TYPES = ["direct", "paraphrased", "none"]

# Scheduler settings
DAILY_RUN_HOUR = 2  # 2 AM
DOMAINS_PER_RUN = 50  # Number of domains to process per run

# API configuration
API_BASE_URL = "http://localhost:5000/api"
API_VERSION = "v1"
API_KEY_PATH = f"{DATA_DIR}/api/keys.json"

# Ensure API directories exist
API_DIR = f"{DATA_DIR}/api"
os.makedirs(API_DIR, exist_ok=True)

# V9: Version tracking
SYSTEM_VERSION = "9.0"
VERSION_INFO = {
    "version": SYSTEM_VERSION,
    "release_date": "2025-05-18",
    "codename": "Noisy, Colorful Truth",
    "features": [
        "Competitive Insight Theater",
        "Agent Conflict Engine",
        "API Checkpoint & Integrity",
        "Agent Self-Revision Loop",
        "Visual Insight Scoreboard",
        "Prompt Self-Awareness System",
        "Benchmark Conflict Framework",
        "API Runtime Validator",
        "Agent-Based Runtime Architecture",
        "Integration Assurance System",
        "Agent Competition Framework",
        "Cookie Jar Reward System",
        "Runtime Dispatcher",
        "Self-Healing Agent Structure",
    ],
    "products": {
        "platform": "LLMRank.io",
        "benchmark": "LLMPageRank.com",
        "badge": "LLM-Rated",
        "foma": "Outcited.com",
        "mcp": "MCPUKnowMe.com"
    }
}

# V2: Output settings
SCORE_HISTORY_RETENTION_DAYS = 90  # Keep 90 days of historical data
DEFAULT_EXPORT_FORMAT = "json"
