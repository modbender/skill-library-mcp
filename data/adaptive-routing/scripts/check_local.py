#!/usr/bin/env python3
"""Check which local LLM providers are running and return the best available one.

Output (JSON):
  { "any_available": bool, "best": { provider, url, models } | null, "providers": [...] }
"""
import json
import urllib.request
import urllib.error
import urllib.parse

PROVIDERS = [
    {"name": "ollama", "url": "http://localhost:11434/api/tags"},
    {"name": "lm-studio", "url": "http://localhost:1234/v1/models"},
    {"name": "llamafile", "url": "http://localhost:8080/v1/models"},
]


def check_provider(p: dict) -> dict:
    try:
        with urllib.request.urlopen(p["url"], timeout=2) as resp:
            data = json.loads(resp.read())
        if p["name"] == "ollama":
            models = [m["name"] for m in data.get("models", [])]
        else:
            models = [m["id"] for m in data.get("data", [])]
        # Strip path entirely to get scheme+host+port only
        parsed = urllib.parse.urlparse(p["url"])
        base_url = f"{parsed.scheme}://{parsed.netloc}"
        return {"available": True, "provider": p["name"], "url": base_url, "models": models}
    except Exception:
        return {"available": False, "provider": p["name"], "models": []}


results = [check_provider(p) for p in PROVIDERS]
available = [r for r in results if r["available"]]

print(json.dumps({
    "any_available": len(available) > 0,
    "best": available[0] if available else None,
    "providers": results,
}))
