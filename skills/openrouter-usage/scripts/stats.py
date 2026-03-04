#!/usr/bin/env python3
"""
OpenRouter Usage Monitor

Fetches real-time usage and per-model cost breakdown from OpenRouter API.
- Real-time totals: GET https://openrouter.ai/api/v1/auth/key
- Historical per-model: GET https://openrouter.ai/api/v1/activity?limit=200

Credentials are loaded from:
  1. Environment variables (recommended for security)
  2. credentials.env file (fallback)

Required:
  OPENROUTER_API_KEY - for real-time totals and balance

Optional:
  OPENROUTER_MGMT_KEY - for per-model history breakdown
"""
import json
import os
import urllib.request
import urllib.parse
from datetime import datetime, timezone, timedelta

# Credentials file in skill directory (same level as scripts/)
SCRIPT_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
CRED_FILE = os.path.join(SCRIPT_DIR, "credentials.env")

def load_creds():
    """Load credentials from environment variables first, then fallback to credentials.env file."""
    creds = {
        "OPENROUTER_API_KEY": os.environ.get("OPENROUTER_API_KEY", ""),
        "OPENROUTER_MGMT_KEY": os.environ.get("OPENROUTER_MGMT_KEY", "")
    }

    # If not in environment, try credentials.env file
    if not creds["OPENROUTER_API_KEY"] or not creds["OPENROUTER_MGMT_KEY"]:
        if os.path.exists(CRED_FILE):
            with open(CRED_FILE) as f:
                for line in f:
                    if not line.strip() or line.strip().startswith("#"):
                        continue
                    if "=" in line:
                        k, v = line.strip().split("=", 1)
                        key = k.strip()
                        if key in creds and not creds[key]:
                            creds[key] = v.strip()
    return creds

def api_get(url, key):
    req = urllib.request.Request(url, headers={
        "Authorization": f"Bearer {key}",
        "Content-Type": "application/json"
    })
    with urllib.request.urlopen(req, timeout=20) as resp:
        data = json.loads(resp.read().decode())
        return data

def parse_iso(iso_str):
    if not iso_str:
        return None
    try:
        return datetime.fromisoformat(iso_str.replace("Z", "+00:00"))
    except Exception:
        return None

def aggregate_model_history(items, cutoff_days=7):
    cutoff = datetime.now(timezone.utc) - timedelta(days=cutoff_days)
    models = {}
    for it in items:
        created_at = parse_iso(it.get("created_at"))
        if created_at and created_at < cutoff:
            continue
        model = it.get("model_id") or it.get("model") or "unknown"
        # cost could be under 'total_cost' or 'cost'
        cost = it.get("total_cost") or it.get("cost") or 0
        # tokens or counts (optional)
        count = int(it.get("requests", it.get("count", 0)) or 0)
        if model not in models:
            models[model] = {"cost": 0.0, "count": 0}
        try:
            models[model]["cost"] += float(cost)
        except Exception:
            pass
        models[model]["count"] += count if count else 1
    return models

def format_digest(today, week, month, balance, per_model):
    lines = []
    lines.append("💰 OpenRouter Usage")
    lines.append(f"Today: ${today:.2f} | Week: ${week:.2f} | Month: ${month:.2f}")
    lines.append(f"Balance: ${balance:.2f} / $TOTAL")  # TOTAL placeholder to be replaced if needed
    lines.append("")
    if per_model:
        lines.append("Recent Models (7d):")
        for name, data in sorted(per_model.items(), key=lambda x: x[1]["cost"], reverse=True)[:8]:
            short = str(name).split("/")[-1]
            lines.append(f"• {short}: ${data['cost']:.2f} ({data['count']})")
    else:
        lines.append("Model breakdown populates after UTC rollover")
    return "\n".join(lines)

def main():
    creds = load_creds()
    api_key = creds.get("OPENROUTER_API_KEY", "")
    mgmt_key = creds.get("OPENROUTER_MGMT_KEY", "")

    if not api_key:
        print("ERROR: OPENROUTER_API_KEY is required (set via environment variable or credentials.env)")
        return

    if not mgmt_key:
        print("WARNING: OPENROUTER_MGMT_KEY not found. Model breakdown will be unavailable.")

    # 1) Real-time totals
    auth_url = "https://openrouter.ai/api/v1/auth/key"
    auth = api_get(auth_url, api_key)
    data = auth.get("data", {})
    today = float(data.get("usage_daily", 0) or 0.0)
    week  = float(data.get("usage_weekly", 0) or 0.0)
    month = float(data.get("usage_monthly", 0) or 0.0)

    # 2) Balance (credits) if available
    credits_url = "https://openrouter.ai/api/v1/credits"
    try:
        credits = api_get(credits_url, api_key)
        total_credits = credits.get("data", {}).get("total_credits", 0.0)
        used = credits.get("data", {}).get("total_usage", 0.0)
        balance = total_credits - used
    except Exception:
        # If credits endpoint isn't accessible, skip balance
        balance = 0.0
        total_credits = 0.0

    # 3) Historical per-model data (only if mgmt_key is available)
    per_model = {}
    if mgmt_key:
        try:
            activity_url = "https://openrouter.ai/api/v1/activity?limit=200"
            activity = api_get(activity_url, mgmt_key)
            items = activity.get("data", [])
            per_model = aggregate_model_history(items, cutoff_days=7)
        except Exception as e:
            print(f"WARNING: Could not fetch model breakdown: {e}")

    # 4) Format a compact digest
    # If you want balance formatting to include TOTAL, adjust in formatting
    digest = f"💰 OpenRouter Usage\nToday: ${today:.2f} | Week: ${week:.2f} | Month: ${month:.2f}\n"
    digest += f"Balance: ${balance:.2f} / ${float(total_credits or 0):.2f}\n"
    if per_model:
        digest += "\n*Recent Models (7d):*\n"
        for name, data in sorted(per_model.items(), key=lambda x: x[1]["cost"], reverse=True)[:8]:
            short = str(name).split("/")[-1]
            digest += f"• {short}: ${data['cost']:.2f} ({data['count']})\n"
    else:
        digest += "\n*Live total — model breakdown available after UTC rollover"

    print(digest.strip())

if __name__ == "__main__":
    main()
