#!/usr/bin/env python3
"""Burn rate tracker for DELLIGHT.AI.
Calculates monthly burn rate and runway from cost inputs."""

import json
import sys
from datetime import datetime

def calculate_burn(costs: dict, capital: float = 490000):
    """Calculate burn rate and runway."""
    monthly_burn = sum(costs.values())
    runway_months = capital / monthly_burn if monthly_burn > 0 else float('inf')
    
    return {
        "date": datetime.now().strftime("%Y-%m-%d"),
        "costs_breakdown": costs,
        "monthly_burn_usd": round(monthly_burn, 2),
        "daily_burn_usd": round(monthly_burn / 30, 2),
        "available_capital_usd": capital,
        "runway_months": round(runway_months, 1),
        "runway_status": (
            "COMFORTABLE" if runway_months > 24
            else "HEALTHY" if runway_months > 12
            else "CAUTION" if runway_months > 6
            else "CRITICAL"
        )
    }

# Default cost structure
DEFAULT_COSTS = {
    "ai_apis": 1500,        # OpenRouter, WaveSpeed, ElevenLabs
    "infrastructure": 350,   # Tailscale, hosting, compute
    "tools": 300,            # Subscriptions
    "difc_license": 500,     # Prorated annual
    "marketing": 1000,       # Content production, ads
}

if __name__ == "__main__":
    costs = DEFAULT_COSTS.copy()
    capital = 490000
    
    if len(sys.argv) > 1:
        try:
            costs = json.loads(sys.argv[1])
        except:
            pass
    if len(sys.argv) > 2:
        capital = float(sys.argv[2])
    
    result = calculate_burn(costs, capital)
    print(json.dumps(result, indent=2))
