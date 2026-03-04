#!/usr/bin/env python3
"""
Agent Audit — Scan OpenClaw setup for cost optimization opportunities.
Works with any model provider (Anthropic, OpenAI, Google, xAI, etc.)

Usage:
    python3 audit.py [--format markdown|summary] [--output path] [--days N] [--dry-run]
"""

import json
import os
import sys
import glob
import re
import argparse
from datetime import datetime, timedelta
from pathlib import Path

# --- Model Pricing (per 1M tokens) ---
MODEL_PRICING = {
    # Anthropic
    "claude-opus": {"input": 15.0, "output": 75.0, "tier": "complex", "provider": "anthropic"},
    "claude-sonnet": {"input": 3.0, "output": 15.0, "tier": "medium", "provider": "anthropic"},
    "claude-haiku-3.5": {"input": 0.80, "output": 4.0, "tier": "simple", "provider": "anthropic"},
    "claude-haiku": {"input": 0.25, "output": 1.25, "tier": "simple", "provider": "anthropic"},
    # OpenAI
    "gpt-4.5": {"input": 75.0, "output": 150.0, "tier": "complex", "provider": "openai"},
    "gpt-4o": {"input": 2.5, "output": 10.0, "tier": "medium", "provider": "openai"},
    "gpt-4o-mini": {"input": 0.15, "output": 0.60, "tier": "simple", "provider": "openai"},
    "o1": {"input": 15.0, "output": 60.0, "tier": "complex", "provider": "openai"},
    "o3-mini": {"input": 1.10, "output": 4.40, "tier": "medium", "provider": "openai"},
    # Google
    "gemini-2.5-pro": {"input": 1.25, "output": 10.0, "tier": "complex", "provider": "google"},
    "gemini-2.0-flash": {"input": 0.10, "output": 0.40, "tier": "simple", "provider": "google"},
    "gemini-flash-lite": {"input": 0.025, "output": 0.10, "tier": "simple", "provider": "google"},
    # xAI
    "grok-3": {"input": 3.0, "output": 15.0, "tier": "complex", "provider": "xai"},
    "grok-3-mini": {"input": 0.30, "output": 0.50, "tier": "simple", "provider": "xai"},
    "grok-4": {"input": 5.0, "output": 25.0, "tier": "medium", "provider": "xai"},
}

# Task name patterns for classification
SIMPLE_PATTERNS = [
    r"health.?check", r"status", r"monitor", r"ping", r"reminder",
    r"notify", r"alert", r"heartbeat", r"uptime", r"wake",
]
MEDIUM_PATTERNS = [
    r"draft", r"research", r"summary", r"analysis", r"report",
    r"brief", r"scan", r"digest", r"trending", r"scrape",
    r"lesson", r"weather", r"bookmark",
]
COMPLEX_PATTERNS = [
    r"code", r"build", r"architect", r"security", r"audit",
    r"review", r"fix", r"debug", r"deploy", r"refactor",
    r"trading", r"trade", r"financial",
]

NEVER_DOWNGRADE_PATTERNS = [
    r"security", r"code", r"build", r"trading", r"trade",
    r"financial", r"deploy", r"critical",
]


def find_openclaw_config():
    """Find the OpenClaw config file."""
    candidates = [
        os.path.expanduser("~/.openclaw/openclaw.json"),
        os.path.expanduser("~/.openclaw/clawdbot.json"),
        os.path.expanduser("~/.config/openclaw/config.json"),
    ]
    for path in candidates:
        if os.path.exists(path):
            return path
    return None


def detect_model_pricing(model_string):
    """Match a model string to pricing info."""
    if not model_string:
        return None
    model_lower = model_string.lower()
    for key, pricing in MODEL_PRICING.items():
        if key in model_lower:
            return {**pricing, "model_key": key, "original": model_string}
    # Unknown model — return None so we can flag it
    return None


def classify_task(name, avg_output_tokens=0, avg_runtime_s=0, success_rate=1.0, error_rate=0):
    """Classify a task into simple/medium/complex based on signals."""
    name_lower = (name or "").lower()

    # Check never-downgrade first
    never_downgrade = any(re.search(p, name_lower) for p in NEVER_DOWNGRADE_PATTERNS)

    # Pattern matching
    is_simple = any(re.search(p, name_lower) for p in SIMPLE_PATTERNS)
    is_medium = any(re.search(p, name_lower) for p in MEDIUM_PATTERNS)
    is_complex = any(re.search(p, name_lower) for p in COMPLEX_PATTERNS)

    # Token-based signals
    if avg_output_tokens > 2000:
        is_complex = True
    elif avg_output_tokens < 500:
        is_simple = True

    # Runtime signals
    if avg_runtime_s > 180:
        is_complex = True
    elif avg_runtime_s < 30:
        is_simple = True

    # Error rate signal — high errors = don't downgrade
    if error_rate > 0.1:
        never_downgrade = True

    # Resolve conflicts (complex > medium > simple)
    if is_complex or never_downgrade:
        return "complex", never_downgrade
    elif is_medium:
        return "medium", never_downgrade
    elif is_simple:
        return "simple", never_downgrade
    else:
        return "medium", never_downgrade  # default to medium when unsure


def get_cheapest_model_for_tier(tier, provider):
    """Get the cheapest model for a given tier and provider."""
    matches = []
    for key, pricing in MODEL_PRICING.items():
        if pricing["tier"] == tier and pricing["provider"] == provider:
            cost = pricing["input"] + pricing["output"]
            matches.append((key, pricing, cost))
    if matches:
        matches.sort(key=lambda x: x[2])
        return matches[0][0], matches[0][1]
    return None, None


def estimate_cost(input_tokens, output_tokens, pricing):
    """Estimate cost for a single run."""
    if not pricing:
        return 0
    return (input_tokens / 1_000_000 * pricing["input"]) + (output_tokens / 1_000_000 * pricing["output"])


def parse_token_stats(stats_line):
    """Parse token stats from cron run output like 'tokens 691 (in 21 / out 670)'."""
    total = 0
    input_t = 0
    output_t = 0
    m = re.search(r"tokens\s+([\d.]+)k?\s*\(in\s+([\d.]+)k?\s*/\s*out\s+([\d.]+)k?\)", str(stats_line), re.I)
    if m:
        def parse_num(s):
            v = float(s)
            return int(v * 1000) if v < 100 else int(v)
        total = parse_num(m.group(1))
        input_t = parse_num(m.group(2))
        output_t = parse_num(m.group(3))
    return input_t, output_t


def parse_runtime(stats_line):
    """Parse runtime from stats like 'runtime 29s' or 'runtime 1m26s'."""
    m = re.search(r"runtime\s+(?:(\d+)m)?(\d+)s", str(stats_line))
    if m:
        mins = int(m.group(1) or 0)
        secs = int(m.group(2))
        return mins * 60 + secs
    return 0


def run_audit(args):
    """Main audit logic."""
    print("🔍 Agent Audit — Scanning your OpenClaw setup...\n")

    # Phase 1: Discovery
    config_path = find_openclaw_config()
    if not config_path:
        print("❌ Could not find OpenClaw config. Looked in:")
        print("   ~/.openclaw/openclaw.json")
        print("   ~/.openclaw/clawdbot.json")
        print("   ~/.config/openclaw/config.json")
        sys.exit(1)

    print(f"📁 Config: {config_path}")

    with open(config_path) as f:
        config = json.load(f)

    # Extract agents — handle various config shapes
    agents_raw = config.get("agents", {})
    agents = {}
    if isinstance(agents_raw, dict):
        # Could be {"defaults": {...}, "list": [...]} or {"agent1": {...}, ...}
        agent_list = agents_raw.get("list", [])
        if isinstance(agent_list, list):
            for a in agent_list:
                if isinstance(a, dict):
                    agents[a.get("id", a.get("name", "unknown"))] = a
        # Also check for defaults
        defaults = agents_raw.get("defaults", {})
        if defaults and isinstance(defaults, dict):
            agents["_defaults"] = defaults
        # If no list key, treat dict entries as agents
        if not agent_list:
            for k, v in agents_raw.items():
                if isinstance(v, dict) and k not in ("defaults", "list"):
                    agents[k] = v
    elif isinstance(agents_raw, list):
        for a in agents_raw:
            if isinstance(a, dict):
                agents[a.get("id", a.get("name", "unknown"))] = a

    print(f"👥 Agents found: {len(agents)}")

    # We'll collect cron data via the report — for now, output the framework
    # In a real deployment, this would call the cron API

    report = []
    report.append("# 🔍 Agent Audit Report")
    report.append(f"\n**Generated:** {datetime.now().strftime('%Y-%m-%d %H:%M')}")
    report.append(f"**Config:** `{config_path}`")
    report.append(f"**Agents:** {len(agents)}")
    report.append("")

    # Phase 2: Agent Analysis
    report.append("## 👥 Agent Overview\n")
    total_estimated_monthly = 0

    for name, agent_config in agents.items():
        if isinstance(agent_config, str):
            continue
        model = agent_config.get("model", agent_config.get("defaultModel", "unknown"))
        pricing = detect_model_pricing(model)
        tier = pricing["tier"] if pricing else "unknown"
        provider = pricing["provider"] if pricing else "unknown"

        report.append(f"### {name}")
        report.append(f"- **Model:** `{model}`")
        report.append(f"- **Tier:** {tier}")
        report.append(f"- **Provider:** {provider}")
        if pricing:
            report.append(f"- **Pricing:** ${pricing['input']}/M input, ${pricing['output']}/M output")
        report.append("")

    # Phase 3: Recommendations placeholder
    report.append("## 💡 Recommendations\n")
    report.append("To generate specific recommendations, the audit needs cron job run history.")
    report.append("Run this audit with OpenClaw's cron API access for detailed per-job analysis.\n")
    report.append("### General Guidelines\n")
    report.append("| Task Type | Recommended Tier | Example Models |")
    report.append("|-----------|-----------------|----------------|")
    report.append("| Health checks, status, reminders | Simple | Haiku, GPT-4o-mini, Flash-Lite, Grok-mini |")
    report.append("| Content drafts, research, summaries | Medium | Sonnet, GPT-4o, Flash, Grok |")
    report.append("| Coding, security, complex reasoning | Complex | Opus, GPT-4.5, 2.5-Pro, Grok-3 |")
    report.append("")
    report.append("### ⛔ Never Downgrade")
    report.append("- Coding/development tasks")
    report.append("- Security reviews")
    report.append("- Financial/trading tasks")
    report.append("- Tasks that previously failed on weaker models")
    report.append("- User's main interactive session model")

    full_report = "\n".join(report)

    if args.output:
        with open(args.output, "w") as f:
            f.write(full_report)
        print(f"\n📄 Report saved to: {args.output}")
    else:
        print(full_report)

    print("\n✅ Audit complete.")
    print("\n💡 TIP: For detailed per-cron analysis, run the audit from within an OpenClaw session")
    print("   where the agent can access cron job history and session data directly.")


def main():
    parser = argparse.ArgumentParser(description="Agent Audit — AI cost optimization scanner")
    parser.add_argument("--format", choices=["markdown", "summary"], default="markdown")
    parser.add_argument("--output", "-o", help="Save report to file")
    parser.add_argument("--days", type=int, default=7, help="Days of history to analyze")
    parser.add_argument("--dry-run", action="store_true", help="Show what would be analyzed")
    args = parser.parse_args()

    if args.dry_run:
        config_path = find_openclaw_config()
        print(f"Would analyze config at: {config_path or 'NOT FOUND'}")
        print(f"Would analyze {args.days} days of history")
        return

    run_audit(args)


if __name__ == "__main__":
    main()
