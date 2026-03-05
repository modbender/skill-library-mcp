"""Configuration for restaurant review cross-check skill."""

# Search thresholds
DEFAULT_THRESHOLDS = {
    "min_rating": 4.0,
    "min_dianping_reviews": 50,
    "min_xhs_notes": 20,
    "max_results": 10,
    "similarity_threshold": 0.6  # For fuzzy matching restaurant names
}

# Request settings
REQUEST_CONFIG = {
    "dianping_delay": 2,  # seconds between requests
    "xhs_delay": 3,  # seconds between requests
    "timeout": 10,
    "max_retries": 3,
    "retry_backoff": 2  # exponential backoff multiplier
}

# Proxy configuration (set to None if not using)
PROXY_CONFIG = {
    "use_proxy": False,
    "proxy_list": [
        # "http://proxy1:port",
        # "http://proxy2:port"
    ]
}

# Output formatting
OUTPUT_CONFIG = {
    "max_restaurants": 10,
    "show_details": True,
    "confidence_threshold": 0.5  # Below this, flag for manual review
}

# Weights for scoring
SCORING_WEIGHTS = {
    "dianping_rating": 0.4,
    "xhs_engagement": 0.3,
    "consistency": 0.3
}
