"""
Google Gemini Usage Parser

Tracks Gemini API usage via:
1. Real-time response parsing
2. Google Cloud Billing API (requires service account)

Pricing Docs: https://ai.google.dev/gemini-api/docs/pricing
"""

import os
from datetime import datetime
from typing import Optional
import logging

logger = logging.getLogger(__name__)

# Pricing per million tokens (as of 2026)
# Context-dependent pricing: standard (≤200K) vs long (>200K)
PRICING = {
    "gemini-2.5-pro": {
        "standard": {"input": 2.0, "output": 12.0},
        "long": {"input": 4.0, "output": 18.0},
    },
    "gemini-2.5-flash": {
        "standard": {"input": 0.15, "output": 0.60},
        "long": {"input": 0.30, "output": 1.20},
    },
    "gemini-2.0-flash": {
        "standard": {"input": 0.10, "output": 0.40},
        "long": {"input": 0.10, "output": 0.40},
    },
    "gemini-3-pro": {
        "standard": {"input": 2.0, "output": 12.0},
        "long": {"input": 4.0, "output": 18.0},
    },
    "gemini-3-pro-image": {
        "standard": {"input": 2.0, "output": 12.0},
        "long": {"input": 4.0, "output": 18.0},
    },
}

# Threshold for long context pricing
LONG_CONTEXT_THRESHOLD = 200_000


class GeminiParser:
    """Parse usage data from Gemini API responses."""
    
    def __init__(self, api_key: Optional[str] = None):
        self.api_key = api_key or os.getenv("GOOGLE_API_KEY") or os.getenv("GEMINI_API_KEY")
        
    def is_configured(self) -> bool:
        """Check if the parser has required credentials."""
        return bool(self.api_key)
    
    def calculate_cost(
        self,
        model: str,
        input_tokens: int,
        output_tokens: int,
        context_length: int = 0,
    ) -> float:
        """Calculate cost for a Gemini request."""
        # Normalize model name
        model_key = model.lower()
        for key in PRICING:
            if key in model_key:
                pricing = PRICING[key]
                break
        else:
            logger.warning(f"Unknown Gemini model: {model}, using flash pricing")
            pricing = PRICING["gemini-2.5-flash"]
        
        # Determine if long context pricing applies
        total_context = context_length + input_tokens
        tier = "long" if total_context > LONG_CONTEXT_THRESHOLD else "standard"
        
        rates = pricing[tier]
        input_cost = (input_tokens / 1_000_000) * rates["input"]
        output_cost = (output_tokens / 1_000_000) * rates["output"]
        
        return input_cost + output_cost
    
    def parse_response_usage(self, response: dict, model: str = None) -> dict:
        """Parse usage from a Gemini API response."""
        # Gemini returns usage in usageMetadata
        usage = response.get("usageMetadata", {})
        
        input_tokens = usage.get("promptTokenCount", 0)
        output_tokens = usage.get("candidatesTokenCount", 0)
        total_tokens = usage.get("totalTokenCount", input_tokens + output_tokens)
        
        # Try to get model from response or use provided
        model_name = model or response.get("modelVersion", "gemini-2.5-flash")
        
        cost = self.calculate_cost(model_name, input_tokens, output_tokens)
        
        return {
            "provider": "gemini",
            "model": model_name,
            "input_tokens": input_tokens,
            "output_tokens": output_tokens,
            "total_tokens": total_tokens,
            "cost_usd": cost,
        }
    
    def parse_streaming_usage(self, chunks: list[dict], model: str = None) -> dict:
        """Aggregate usage from streaming response chunks."""
        total_input = 0
        total_output = 0
        model_name = model
        
        for chunk in chunks:
            usage = chunk.get("usageMetadata", {})
            # Streaming usually has cumulative counts in the last chunk
            if "promptTokenCount" in usage:
                total_input = max(total_input, usage["promptTokenCount"])
            if "candidatesTokenCount" in usage:
                total_output = max(total_output, usage["candidatesTokenCount"])
            if not model_name and "modelVersion" in chunk:
                model_name = chunk["modelVersion"]
        
        model_name = model_name or "gemini-2.5-flash"
        cost = self.calculate_cost(model_name, total_input, total_output)
        
        return {
            "provider": "gemini",
            "model": model_name,
            "input_tokens": total_input,
            "output_tokens": total_output,
            "cost_usd": cost,
        }


# Singleton instance
_parser = None

def get_parser() -> GeminiParser:
    global _parser
    if _parser is None:
        _parser = GeminiParser()
    return _parser
