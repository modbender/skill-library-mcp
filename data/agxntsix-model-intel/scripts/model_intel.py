#!/usr/bin/env python3
"""
Model Intelligence — Live model pricing & capabilities from OpenRouter.

Usage:
  model_intel.py list                       # Top models by category
  model_intel.py price <model_id>           # Pricing for specific model
  model_intel.py compare <model1> <model2>  # Side-by-side comparison
  model_intel.py best <task>                # Best model for task type
  model_intel.py search <query>             # Search models by name

Tasks: code, reasoning, creative, fast, cheap, vision, long-context
"""
import argparse
import json
import os
import sys
import requests

OPENROUTER_KEY = os.environ.get("OPENROUTER_API_KEY", "")
if not OPENROUTER_KEY:
    try:
        with open(os.path.expanduser("~/.openclaw/workspace/.env")) as f:
            for line in f:
                if line.startswith("OPENROUTER_API_KEY="):
                    OPENROUTER_KEY = line.strip().split("=", 1)[1]
    except:
        pass

CACHE = {}

def get_models():
    if "models" in CACHE:
        return CACHE["models"]
    resp = requests.get("https://openrouter.ai/api/v1/models", timeout=15)
    resp.raise_for_status()
    models = resp.json().get("data", [])
    CACHE["models"] = models
    return models

def fmt_price(p):
    if p is None: return "?"
    val = float(p) * 1_000_000
    if val == 0: return "FREE"
    if val < 0.01: return f"${val:.4f}/1M"
    return f"${val:.2f}/1M"

def model_summary(m):
    pricing = m.get("pricing", {})
    return {
        "id": m["id"],
        "name": m.get("name", m["id"]),
        "context": m.get("context_length", "?"),
        "input": fmt_price(pricing.get("prompt")),
        "output": fmt_price(pricing.get("completion")),
        "modalities": m.get("architecture", {}).get("modality", "?"),
    }

def cmd_list(args):
    models = get_models()
    # Group by provider
    by_provider = {}
    for m in models:
        provider = m["id"].split("/")[0] if "/" in m["id"] else "other"
        by_provider.setdefault(provider, []).append(m)
    
    top_providers = ["anthropic", "google", "openai", "meta-llama", "deepseek", "mistralai"]
    for p in top_providers:
        if p in by_provider:
            print(f"\n=== {p} ===")
            for m in sorted(by_provider[p], key=lambda x: x.get("name", ""))[:8]:
                s = model_summary(m)
                print(f"  {s['id']:50s}  ctx:{s['context']:>8}  in:{s['input']:>14}  out:{s['output']:>14}")

def cmd_price(args):
    models = get_models()
    matches = [m for m in models if args.model.lower() in m["id"].lower()]
    if not matches:
        print(f"No models matching '{args.model}'")
        return
    for m in matches[:5]:
        s = model_summary(m)
        print(json.dumps(s, indent=2))

def cmd_compare(args):
    models = get_models()
    results = []
    for target in [args.model1, args.model2]:
        match = [m for m in models if target.lower() in m["id"].lower()]
        if match:
            results.append(model_summary(match[0]))
        else:
            results.append({"id": target, "error": "not found"})
    print(json.dumps(results, indent=2))

def cmd_search(args):
    models = get_models()
    q = args.query.lower()
    matches = [m for m in models if q in m["id"].lower() or q in m.get("name", "").lower()]
    for m in matches[:15]:
        s = model_summary(m)
        print(f"  {s['id']:55s}  ctx:{s['context']:>8}  in:{s['input']:>14}  out:{s['output']:>14}")

def cmd_best(args):
    """Recommend best models for a task type based on live data."""
    models = get_models()
    
    task_filters = {
        "code": lambda m: any(k in m["id"].lower() for k in ["claude", "gpt-4", "deepseek-coder", "codestral"]),
        "reasoning": lambda m: any(k in m["id"].lower() for k in ["o1", "o3", "reasoning", "think", "r1"]),
        "creative": lambda m: any(k in m["id"].lower() for k in ["claude", "gpt-4", "gemini"]),
        "fast": lambda m: any(k in m["id"].lower() for k in ["flash", "mini", "haiku", "instant", "nano"]),
        "cheap": lambda m: float(m.get("pricing", {}).get("prompt", "999")) < 0.000001,
        "vision": lambda m: "image" in m.get("architecture", {}).get("modality", ""),
        "long-context": lambda m: (m.get("context_length") or 0) >= 100000,
    }
    
    filt = task_filters.get(args.task)
    if not filt:
        print(f"Unknown task: {args.task}. Options: {', '.join(task_filters.keys())}")
        return
    
    matches = [m for m in models if filt(m)]
    matches.sort(key=lambda m: float(m.get("pricing", {}).get("prompt") or "999"))
    
    print(f"\nBest models for '{args.task}' (sorted by input price):\n")
    for m in matches[:10]:
        s = model_summary(m)
        print(f"  {s['id']:55s}  ctx:{s['context']:>8}  in:{s['input']:>14}  out:{s['output']:>14}")

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Model Intelligence (OpenRouter)")
    sub = parser.add_subparsers(dest="cmd")
    
    sub.add_parser("list", help="List top models by provider")
    
    p = sub.add_parser("price", help="Get pricing for a model")
    p.add_argument("model")
    
    p = sub.add_parser("compare", help="Compare two models")
    p.add_argument("model1")
    p.add_argument("model2")
    
    p = sub.add_parser("search", help="Search models")
    p.add_argument("query")
    
    p = sub.add_parser("best", help="Best model for a task")
    p.add_argument("task", help="code|reasoning|creative|fast|cheap|vision|long-context")
    
    args = parser.parse_args()
    if not args.cmd:
        parser.print_help()
    else:
        globals()[f"cmd_{args.cmd}"](args)
