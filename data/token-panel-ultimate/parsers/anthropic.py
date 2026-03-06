"""
Anthropic Usage API Parser

Fetches usage data from Anthropic's Admin API.
Requires ANTHROPIC_ADMIN_API_KEY environment variable.

API Docs: https://platform.claude.com/docs/en/build-with-claude/usage-cost-api
"""

import os
import httpx
from datetime import datetime, timedelta
from typing import Optional
import logging

logger = logging.getLogger(__name__)

# Pricing per million tokens (as of 2026)
PRICING = {
    "claude-opus-4-5": {"input": 5.0, "output": 25.0},
    "claude-opus-4": {"input": 5.0, "output": 25.0},
    "claude-sonnet-4-5": {"input": 3.0, "output": 15.0},
    "claude-sonnet-4": {"input": 3.0, "output": 15.0},
    "claude-haiku-4-5": {"input": 1.0, "output": 5.0},
    "claude-haiku-4": {"input": 0.25, "output": 1.25},
    "claude-3-5-sonnet": {"input": 3.0, "output": 15.0},
    "claude-3-opus": {"input": 15.0, "output": 75.0},
    "claude-3-sonnet": {"input": 3.0, "output": 15.0},
    "claude-3-haiku": {"input": 0.25, "output": 1.25},
}

# Cache discount
CACHE_READ_DISCOUNT = 0.1  # 90% off for cache reads
CACHE_WRITE_PREMIUM = 1.25  # 25% extra for cache writes


class AnthropicParser:
    """Parse usage data from Anthropic's API."""
    
    def __init__(self, admin_api_key: Optional[str] = None):
        self.api_key = admin_api_key or os.getenv("ANTHROPIC_ADMIN_API_KEY")
        self.base_url = "https://api.anthropic.com/v1"
        
    def is_configured(self) -> bool:
        """Check if the parser has required credentials."""
        return bool(self.api_key)
    
    def calculate_cost(
        self,
        model: str,
        input_tokens: int,
        output_tokens: int,
        cache_read_tokens: int = 0,
        cache_write_tokens: int = 0,
    ) -> float:
        """Calculate cost for a request."""
        # Normalize model name
        model_key = model.lower().replace("anthropic/", "")
        pricing = PRICING.get(model_key, PRICING.get("claude-sonnet-4"))
        
        if not pricing:
            logger.warning(f"Unknown model: {model}, using default pricing")
            pricing = {"input": 3.0, "output": 15.0}
        
        # Calculate costs (per million tokens)
        input_cost = (input_tokens / 1_000_000) * pricing["input"]
        output_cost = (output_tokens / 1_000_000) * pricing["output"]
        
        # Cache adjustments
        cache_read_cost = (cache_read_tokens / 1_000_000) * pricing["input"] * CACHE_READ_DISCOUNT
        cache_write_cost = (cache_write_tokens / 1_000_000) * pricing["input"] * CACHE_WRITE_PREMIUM
        
        return input_cost + output_cost + cache_read_cost + cache_write_cost
    
    async def fetch_daily_usage(self, date: datetime) -> list[dict]:
        """Fetch usage for a specific day from the Admin API."""
        if not self.api_key:
            logger.warning("ANTHROPIC_ADMIN_API_KEY not set, skipping API fetch")
            return []
        
        date_str = date.strftime("%Y-%m-%d")
        
        async with httpx.AsyncClient() as client:
            try:
                response = await client.get(
                    f"{self.base_url}/organizations/usage",
                    headers={
                        "x-api-key": self.api_key,
                        "anthropic-version": "2023-06-01",
                    },
                    params={
                        "start_date": date_str,
                        "end_date": date_str,
                    },
                    timeout=30,
                )
                response.raise_for_status()
                data = response.json()
                
                records = []
                for usage in data.get("usage", []):
                    records.append({
                        "model": usage.get("model", "unknown"),
                        "input_tokens": usage.get("input_tokens", 0),
                        "output_tokens": usage.get("output_tokens", 0),
                        "cache_read_tokens": usage.get("cache_read_tokens", 0),
                        "cache_write_tokens": usage.get("cache_write_tokens", 0),
                        "date": date_str,
                    })
                
                return records
                
            except httpx.HTTPError as e:
                logger.error(f"Failed to fetch Anthropic usage: {e}")
                return []
    
    def parse_response_usage(self, response: dict) -> dict:
        """Parse usage from an API response (for real-time tracking)."""
        usage = response.get("usage", {})
        model = response.get("model", "unknown")
        
        input_tokens = usage.get("input_tokens", 0)
        output_tokens = usage.get("output_tokens", 0)
        cache_read = usage.get("cache_read_input_tokens", 0)
        cache_write = usage.get("cache_creation_input_tokens", 0)
        
        cost = self.calculate_cost(model, input_tokens, output_tokens, cache_read, cache_write)
        
        return {
            "provider": "anthropic",
            "model": model,
            "input_tokens": input_tokens,
            "output_tokens": output_tokens,
            "cache_read_tokens": cache_read,
            "cache_write_tokens": cache_write,
            "cost_usd": cost,
        }


# Singleton instance
_parser = None

def get_parser() -> AnthropicParser:
    global _parser
    if _parser is None:
        _parser = AnthropicParser()
    return _parser
