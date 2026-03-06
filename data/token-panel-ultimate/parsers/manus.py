"""
Manus AI Task Tracker

Tracks Manus task completions and credit usage.
Since Manus doesn't have a public API for usage, this relies on:
1. Manual recording via the collector API
2. Parsing webhook responses
3. Scraping the dashboard (optional)

Manus Docs: https://manus.im/docs/introduction/plans
"""

import os
import httpx
from datetime import datetime
from typing import Optional
import logging
import json

logger = logging.getLogger(__name__)

# Manus API endpoints
MANUS_API_BASE = "https://api.manus.ai/v1"


class ManusParser:
    """Track Manus AI task usage."""
    
    def __init__(self, api_key: Optional[str] = None):
        self.api_key = api_key or os.getenv("MANUS_API_KEY")
        
    def is_configured(self) -> bool:
        """Check if the parser has required credentials."""
        return bool(self.api_key)
    
    async def get_task_status(self, task_id: str) -> Optional[dict]:
        """Fetch task status from Manus API."""
        if not self.api_key:
            logger.warning("MANUS_API_KEY not set")
            return None
        
        async with httpx.AsyncClient() as client:
            try:
                response = await client.get(
                    f"{MANUS_API_BASE}/tasks/{task_id}",
                    headers={"API_KEY": self.api_key},
                    timeout=30,
                )
                response.raise_for_status()
                return response.json()
            except httpx.HTTPError as e:
                logger.error(f"Failed to fetch Manus task {task_id}: {e}")
                return None
    
    def parse_task_response(self, response: dict) -> dict:
        """Parse a Manus task response into our format."""
        return {
            "task_id": response.get("task_id", "unknown"),
            "credits_used": response.get("credit_usage", 0),
            "status": response.get("status", "unknown"),
            "description": response.get("prompt", "")[:200],  # Truncate
            "started_at": response.get("created_at"),
            "completed_at": response.get("completed_at"),
            "metadata": {
                "task_url": response.get("task_url"),
                "output_count": len(response.get("output", [])),
            }
        }
    
    async def poll_active_tasks(self, task_ids: list[str]) -> list[dict]:
        """Poll multiple tasks for their current status."""
        results = []
        for task_id in task_ids:
            status = await self.get_task_status(task_id)
            if status:
                results.append(self.parse_task_response(status))
        return results
    
    def estimate_credits(self, description: str) -> dict:
        """Estimate credit usage based on task description.
        
        Based on observed patterns:
        - Simple queries: 2-5 credits
        - Research tasks: 10-30 credits
        - Complex multi-step: 30-100 credits
        - Deep research with browsing: 50-200 credits
        """
        desc_lower = description.lower()
        
        # Keywords that indicate complexity
        research_keywords = ["research", "analyze", "comprehensive", "detailed", "explore"]
        browse_keywords = ["browse", "search", "find", "look up", "website"]
        multi_step_keywords = ["step by step", "multiple", "compare", "list of"]
        
        base = 5
        
        if any(k in desc_lower for k in research_keywords):
            base += 20
        if any(k in desc_lower for k in browse_keywords):
            base += 15
        if any(k in desc_lower for k in multi_step_keywords):
            base += 10
        
        # Length factor
        if len(description) > 500:
            base += 10
        elif len(description) > 200:
            base += 5
        
        return {
            "min": max(2, int(base * 0.5)),
            "expected": base,
            "max": int(base * 2.5),
        }


# Singleton instance
_parser = None

def get_parser() -> ManusParser:
    global _parser
    if _parser is None:
        _parser = ManusParser()
    return _parser
