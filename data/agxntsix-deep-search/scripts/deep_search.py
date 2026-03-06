#!/usr/bin/env python3
"""
AgxntSix Deep Search — Multi-tier Perplexity search with Langfuse tracing

Three tiers of search depth:
  quick   → sonar           (fast, simple lookups, ~1-2s)
  pro     → sonar-pro       (multi-step reasoning, ~3-5s)  
  deep    → sonar-reasoning-pro  (chain-of-thought, thorough, ~10-20s)

Usage:
  deep_search.py quick "what time is it in Austin TX"
  deep_search.py pro "compare Neo4j vs FalkorDB for AI agent memory"
  deep_search.py deep "analyze the current state of AI agent memory architectures"
"""
import argparse
import json
import os
import sys
import requests
from datetime import datetime

# Langfuse tracing
os.environ.setdefault("LANGFUSE_SECRET_KEY", "sk-lf-115cb6b4-7153-4fe6-9255-bf28f8b115de")
os.environ.setdefault("LANGFUSE_PUBLIC_KEY", "pk-lf-8a9322b9-5eb1-4e8b-815e-b3428dc69bc4")
os.environ.setdefault("LANGFUSE_HOST", "http://langfuse-web:3000")

try:
    from langfuse import observe, get_client, Langfuse
    TRACING = True
except ImportError:
    TRACING = False
    def observe(**kwargs):
        def decorator(fn):
            return fn
        return decorator

def get_session_id():
    """Generate session ID based on date+hour for grouping related calls."""
    return datetime.now().strftime("session-%Y%m%d-%H")

DEFAULT_USER_ID = "agxntsix"

API_KEY = os.environ.get("PERPLEXITY_API_KEY") or os.environ.get("PPLX_API_KEY")
BASE_URL = "https://api.perplexity.ai"

if not API_KEY:
    try:
        config_path = os.path.expanduser("~/.openclaw/openclaw.json")
        with open(config_path) as f:
            config = json.load(f)
        API_KEY = config.get("tools", {}).get("web", {}).get("search", {}).get("perplexity", {}).get("apiKey", "")
    except:
        pass

TIERS = {
    "quick": {
        "model": "sonar",
        "description": "Fast lookup (~1-2s)",
        "system_prompt": "Be concise. Answer in 2-3 sentences max."
    },
    "pro": {
        "model": "sonar-pro", 
        "description": "Multi-step reasoning (~3-5s)",
        "system_prompt": "Provide a thorough, well-structured answer with key details and sources."
    },
    "deep": {
        "model": "sonar-reasoning-pro",
        "description": "Deep chain-of-thought analysis (~10-20s)",
        "system_prompt": "You are a research analyst. Provide comprehensive, deeply-reasoned analysis. Include multiple perspectives, cite sources, identify trends, and highlight what matters most. Structure your response with clear sections."
    }
}

@observe(as_type="generation")
def search(tier: str, query: str, focus: str = "internet"):
    if not API_KEY:
        print(json.dumps({"error": "No Perplexity API key found."}))
        return
    
    tier_config = TIERS.get(tier)
    if not tier_config:
        print(json.dumps({"error": f"Unknown tier: {tier}. Use: quick, pro, deep"}))
        return
    
    # Update Langfuse trace with session/user context
    if TRACING:
        try:
            lf = get_client()
            lf.update_current_trace(
                session_id=get_session_id(),
                user_id=DEFAULT_USER_ID,
                tags=[f"search-{tier}", f"focus-{focus}"],
                metadata={"tier": tier, "focus": focus}
            )
        except Exception:
            pass
    
    headers = {
        "Authorization": f"Bearer {API_KEY}",
        "Content-Type": "application/json"
    }
    
    payload = {
        "model": tier_config["model"],
        "messages": [
            {"role": "system", "content": tier_config["system_prompt"]},
            {"role": "user", "content": query}
        ],
        "search_domain_filter": [],
        "return_citations": True,
        "return_related_questions": tier == "deep"
    }
    
    if focus != "internet":
        payload["search_focus"] = focus
    
    start = datetime.now()
    
    try:
        resp = requests.post(
            f"{BASE_URL}/chat/completions",
            headers=headers,
            json=payload,
            timeout=60
        )
        resp.raise_for_status()
        data = resp.json()
        
        elapsed = (datetime.now() - start).total_seconds()
        
        result = {
            "tier": tier,
            "model": tier_config["model"],
            "query": query,
            "elapsed_seconds": round(elapsed, 1),
            "answer": data["choices"][0]["message"]["content"],
            "citations": data.get("citations", []),
        }
        
        if data.get("related_questions"):
            result["related_questions"] = data["related_questions"]
        
        if data.get("usage"):
            result["tokens"] = {
                "prompt": data["usage"].get("prompt_tokens"),
                "completion": data["usage"].get("completion_tokens"),
                "total": data["usage"].get("total_tokens")
            }
        
        if TRACING:
            try:
                lf = get_client()
                lf.update_current_generation(
                    model=tier_config["model"],
                    input=query,
                    output=result.get("answer", ""),
                    usage_details={
                        "input": result.get("tokens", {}).get("prompt", 0),
                        "output": result.get("tokens", {}).get("completion", 0),
                    },
                    metadata={
                        "tier": tier,
                        "focus": focus,
                        "citations": result.get("citations", []),
                        "elapsed_seconds": result.get("elapsed_seconds"),
                    }
                )
            except Exception:
                pass
        
        print(json.dumps(result, indent=2))
        return result
        
    except requests.exceptions.HTTPError as e:
        print(json.dumps({
            "error": f"HTTP {e.response.status_code}",
            "detail": e.response.text[:500] if e.response else str(e)
        }))
    except Exception as e:
        print(json.dumps({"error": str(e)}))

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="AgxntSix Deep Search (Perplexity)")
    parser.add_argument("tier", choices=["quick", "pro", "deep"], 
                        help="Search depth: quick (sonar), pro (sonar-pro), deep (sonar-reasoning-pro)")
    parser.add_argument("query", help="Search query")
    parser.add_argument("--focus", default="internet", 
                        help="Search focus (internet, academic, news, youtube, reddit)")
    
    args = parser.parse_args()
    search(args.tier, args.query, args.focus)
    
    if TRACING:
        try:
            get_client().flush()
        except:
            pass
