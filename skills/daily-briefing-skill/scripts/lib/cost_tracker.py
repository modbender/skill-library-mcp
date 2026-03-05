#!/usr/bin/env python3
"""
Model usage/cost tracker for daily briefing.
Fetches cost data from codexbar and formats a summary.
"""

import subprocess
import json
import sys

def get_cost_summary():
    """Get cost summary from codexbar."""
    lines = []
    
    # Try Codex
    try:
        result = subprocess.run(
            ["codexbar", "cost", "--format", "json", "--provider", "codex"],
            capture_output=True, text=True, timeout=10
        )
        if result.returncode == 0:
            data = json.loads(result.stdout)
            if data and len(data) > 0:
                cost_data = data[0]
                total = cost_data.get("last30DaysCostUSD", 0)
                session = cost_data.get("sessionCostUSD", 0)
                tokens = cost_data.get("last30DaysTokens", 0)
                lines.append(f"   Codex: ${total:.2f} (30d) | Session: ${session:.2f} | {tokens/1_000_000:.1f}M tokens")
    except Exception:
        pass
    
    # Try Claude
    try:
        result = subprocess.run(
            ["codexbar", "cost", "--format", "json", "--provider", "claude"],
            capture_output=True, text=True, timeout=10
        )
        if result.returncode == 0:
            data = json.loads(result.stdout)
            if data and len(data) > 0:
                cost_data = data[0]
                total = cost_data.get("last30DaysCostUSD", 0)
                session = cost_data.get("sessionCostUSD", 0)
                tokens = cost_data.get("last30DaysTokens", 0)
                lines.append(f"   Claude: ${total:.2f} (30d) | Session: ${session:.2f} | {tokens/1_000_000:.1f}M tokens")
                
                # Add model breakdown if available
                daily = cost_data.get("daily", [])
                if daily:
                    latest = daily[-1]
                    breakdowns = latest.get("modelBreakdowns", [])
                    if breakdowns:
                        lines.append("   Latest session models:")
                        for b in breakdowns[:3]:  # Top 3
                            model = b.get("modelName", "unknown")[:20]
                            cost = b.get("cost", 0)
                            lines.append(f"      • {model}: ${cost:.2f}")
    except Exception:
        pass
    
    if not lines:
        return "   💸 Cost tracking unavailable (codexbar not configured)"
    
    return "\n".join(lines)

if __name__ == "__main__":
    print(get_cost_summary())
