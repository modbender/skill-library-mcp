"""
Configuration for GEO Visual Opportunity Engine
Author: Tim (sales@dageno.ai)
"""

import os

# Author Information
AUTHOR_INFO = {
    "name": "Tim",
    "email": "sales@dageno.ai",
    "website": "https://dageno.ai/"
}

# Skill Configuration
SKILL_CONFIG = {
    "version": "3.0.0",
    "name": "geo-visual-opportunity-engine",
    "display_name": "GEO Visual Opportunity Engine"
}

# Nano Banana 2 Configuration
# Using Gemini 2.5 Flash Image (Nano Banana 2) for native image generation
NANO_BANANA_CONFIG = {
    "model": "gemini-2.5-flash-image",
    "api_env_var": "GOOGLE_API_KEY",
    "supported_styles": ["white_info", "lifestyle", "hero"],
    "default_size": "1024x1024",
    "output_dir": "output/images"
}

# Image Style Presets
IMAGE_STYLES = {
    "white_info": {
        "suffix": "white background, studio lighting, infographic style, minimal, 4k, vector aesthetic",
        "aspect_ratio": "1:1",
        "description": "Clean white background, product-focused infographic"
    },
    "lifestyle": {
        "suffix": "photorealistic, natural lighting, human interaction, depth of field, cinematic 35mm, 8k",
        "aspect_ratio": "16:9",
        "description": "Real-world场景 with human interaction, photorealistic"
    },
    "hero": {
        "suffix": "dramatic lighting, product focus, commercial photography, advertising standard, sharp focus, ray tracing",
        "aspect_ratio": "3:2",
        "description": "Dramatic hero shot with commercial photography quality"
    }
}

# Output Configuration
OUTPUT_CONFIG = {
    "max_opportunities": 8,
    "content_body_min_length": 150,
    "content_body_max_length": 300,
    "default_language": "en"
}

# API Configuration
def get_google_api_key() -> str:
    """Get Google API Key from environment variable"""
    # Support both GOOGLE_API_KEY and GEMINI_API_KEY
    return os.environ.get("GOOGLE_API_KEY", os.environ.get("GEMINI_API_KEY", ""))

def validate_api_key() -> bool:
    """Validate if Google API Key is set"""
    api_key = get_google_api_key()
    return bool(api_key and len(api_key) > 0)
