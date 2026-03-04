#!/usr/bin/env python3
"""
NIMA Precognitive Actions — Predictions that DO things.

Compact module that maps precognitions to preparation actions.
Runs during heartbeats to pre-warm context before sessions start.

Usage:
    # During heartbeat
    python3 -m nima_core.cognition.precog_actions prepare
    
    # Check what's cached
    python3 -m nima_core.cognition.precog_actions status
    
    # Clear cache
    python3 -m nima_core.cognition.precog_actions clear

API:
    from nima_core.cognition.precog_actions import prepare, get_prep_context
    results = prepare()           # Run all preparations
    context = get_prep_context()  # Get cached prep for injection
"""

import json
import os
import re
import subprocess
import sys
import time
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Optional

# ─── Config ───────────────────────────────────────────────────────────────────

NIMA_HOME = Path(os.environ.get("NIMA_HOME", os.path.expanduser("~/.nima")))
PREP_DIR = NIMA_HOME / "precog_prep"
PRECOG_DB = NIMA_HOME / "memory" / "precognitions.sqlite"
PREP_TTL = 3600 * 4  # 4 hours before prep goes stale
WORKSPACE = Path(os.environ.get("OPENCLAW_WORKSPACE", os.path.expanduser("~/.openclaw/workspace")))
OPENCLAW_CONFIG = Path(os.environ.get("OPENCLAW_CONFIG", os.path.expanduser("~/.openclaw/openclaw.json")))

# ─── Model Tiers (capability-based, not provider-specific) ───────────────────
#
# Instead of hardcoding "opus" or "sonnet", we use capability tiers:
#   - "deep"    = Best available reasoning model (complex research, synthesis)
#   - "fast"    = Best available speed model (coding sprints, quick tasks)
#   - "balanced"= Good all-rounder (marketing, general work)
#   - "vision"  = Model with image understanding
#   - "default" = Whatever's configured as default
#
# The tier resolver reads openclaw.json to find what models are actually
# available and picks the best match per tier.

MODEL_TIERS = {
    "deep": {
        "description": "Complex reasoning, research, synthesis",
        "prefer_keywords": ["opus", "o1", "o3", "pro", "deep", "large", "think", "r1", "qwq"],
        "prefer_reasoning": True,
        "prefer_large_context": True,
    },
    "fast": {
        "description": "Quick tasks, coding sprints, iteration",
        "prefer_keywords": ["haiku", "flash", "mini", "fast", "nano", "lite", "small"],
        "prefer_reasoning": False,
        "prefer_large_context": False,
    },
    "balanced": {
        "description": "Good all-rounder for most tasks",
        "prefer_keywords": ["sonnet", "gpt-4", "claude", "gemini", "qwen", "glm"],
        "prefer_reasoning": False,
        "prefer_large_context": True,
    },
    "vision": {
        "description": "Image understanding needed",
        "prefer_keywords": ["vision", "vl", "4o", "gemini"],
        "prefer_input": "image",
    },
}


def get_available_models() -> List[Dict]:
    """Read available models from openclaw.json."""
    if not OPENCLAW_CONFIG.exists():
        return []
    try:
        config = json.loads(OPENCLAW_CONFIG.read_text())
        models_config = config.get("models", {})
        providers = models_config.get("providers", {})
        
        available = []
        for provider_name, provider in providers.items():
            for model in provider.get("models", []):
                available.append({
                    "id": f"{provider_name}/{model['id']}",
                    "name": model.get("name", model["id"]),
                    "reasoning": model.get("reasoning", False),
                    "context": model.get("contextWindow", 0),
                    "input": model.get("input", ["text"]),
                    "cost_in": model.get("cost", {}).get("input", 0),
                    "cost_out": model.get("cost", {}).get("output", 0),
                })
        return available
    except Exception:
        return []


def resolve_tier(tier: str) -> Optional[str]:
    """Resolve a capability tier to the best available model ID."""
    models = get_available_models()
    if not models:
        return None
    
    tier_config = MODEL_TIERS.get(tier, MODEL_TIERS["balanced"])
    keywords = tier_config.get("prefer_keywords", [])
    want_reasoning = tier_config.get("prefer_reasoning", False)
    want_large_ctx = tier_config.get("prefer_large_context", False)
    want_input = tier_config.get("prefer_input", None)
    
    # Score each model
    scored = []
    for m in models:
        score = 0
        mid = m["id"].lower()
        mname = m["name"].lower()
        
        # Keyword match
        for kw in keywords:
            if kw.lower() in mid or kw.lower() in mname:
                score += 10
                break
        
        # Reasoning preference
        if want_reasoning and m["reasoning"]:
            score += 5
        elif not want_reasoning and not m["reasoning"]:
            score += 2
        
        # Context window preference
        if want_large_ctx and m["context"] >= 128000:
            score += 3
        elif not want_large_ctx and m["context"] < 128000:
            score += 1
        
        # Input type requirement
        if want_input and want_input in m.get("input", []):
            score += 10
        elif want_input and want_input not in m.get("input", []):
            score -= 100  # Disqualify
        
        # Cost tiebreaker: prefer cheaper for fast, don't care for deep
        if tier == "fast" and m["cost_in"] > 0:
            score -= m["cost_in"] / 10  # Slight penalty for expensive
        
        scored.append((score, m["id"]))
    
    scored.sort(key=lambda x: -x[0])
    return scored[0][1] if scored else None


# ─── Category Detection ──────────────────────────────────────────────────────

CATEGORIES = {
    # ─── Engineering ──────────────────────────────────────────────────────
    "coding": {
        "patterns": [r"coding|sprint|dev|technical|debug|refactor|implement|build|fix|PR|pull request|CI|typescript|python|rust|javascript"],
        "tier": "fast",
        "actions": ["git_status", "open_prs", "ci_status", "recent_commits", "recall_coding"],
    },
    "architecture": {
        "patterns": [r"architect|system design|scale|microservice|monolith|database design|schema|migration|API design"],
        "tier": "deep",
        "actions": ["git_status", "recall_architecture", "check_docs"],
    },
    "debugging": {
        "patterns": [r"debug|error|bug|crash|exception|traceback|stack trace|failing|broken|issue"],
        "tier": "fast",
        "actions": ["git_status", "recent_errors", "ci_status", "recall_debugging"],
    },
    
    # ─── Research & Learning ──────────────────────────────────────────────
    "research": {
        "patterns": [r"research|study|deep dive|paper|academic|explore|investigate|analysis|neuroscience|consciousness"],
        "tier": "deep",
        "actions": ["recall_research", "check_topics", "recent_papers"],
    },
    "learning": {
        "patterns": [r"learn|tutorial|course|teach|explain|understand|how does|what is|concept"],
        "tier": "deep",
        "actions": ["recall_learning", "check_topics"],
    },
    
    # ─── Marketing & Creative ─────────────────────────────────────────────
    "marketing": {
        "patterns": [r"marketing|campaign|SEO|ads|funnel|conversion|growth|acquisition|retention|analytics"],
        "tier": "balanced",
        "actions": ["recall_marketing", "load_assets", "check_analytics"],
    },
    "content": {
        "patterns": [r"content|blog|article|copy|write|editorial|newsletter|social media|post"],
        "tier": "balanced",
        "actions": ["recall_content", "load_assets", "check_calendar"],
    },
    "creative": {
        "patterns": [r"creative|design|brand|visual|logo|color|typography|aesthetic|mockup|wireframe"],
        "tier": "vision",
        "actions": ["recall_creative", "load_assets", "load_design_system"],
    },
    
    # ─── Business & Strategy ──────────────────────────────────────────────
    "business": {
        "patterns": [r"business|strategy|revenue|pricing|competitor|market|product|roadmap|planning|OKR|KPI"],
        "tier": "deep",
        "actions": ["recall_business", "check_calendar", "load_docs"],
    },
    "finance": {
        "patterns": [r"finance|budget|cost|invoice|expense|profit|loss|accounting|tax|payroll"],
        "tier": "balanced",
        "actions": ["recall_finance", "load_spreadsheets"],
    },
    "sales": {
        "patterns": [r"sales|deal|pipeline|prospect|lead|CRM|outreach|pitch|proposal|close"],
        "tier": "balanced",
        "actions": ["recall_sales", "check_calendar"],
    },
    
    # ─── Operations & Infrastructure ──────────────────────────────────────
    "ops": {
        "patterns": [r"deploy|devops|server|infra|docker|CI.?CD|monitor|scale|kubernetes|terraform"],
        "tier": "fast",
        "actions": ["check_services", "ci_status", "recall_ops"],
    },
    "security": {
        "patterns": [r"security|auth|permission|vulnerability|CVE|audit|firewall|SSL|encrypt|breach"],
        "tier": "deep",
        "actions": ["recall_security", "check_services", "recent_errors"],
    },
    
    # ─── Data & Analytics ─────────────────────────────────────────────────
    "data": {
        "patterns": [r"data|analytics|dashboard|metric|report|SQL|query|database|ETL|pipeline|warehouse"],
        "tier": "balanced",
        "actions": ["recall_data", "check_services", "load_spreadsheets"],
    },
    
    # ─── Communication & Collaboration ────────────────────────────────────
    "communication": {
        "patterns": [r"email|meeting|call|present|slide|deck|standup|retro|sync|agenda"],
        "tier": "fast",
        "actions": ["check_calendar", "check_email", "recall_communication"],
    },
    
    # ─── Personal & Wellbeing ─────────────────────────────────────────────
    "personal": {
        "patterns": [r"family|church|personal|life|feeling|emotion|faith|prayer|health|exercise|sleep"],
        "tier": "deep",
        "actions": ["recall_personal", "mood_check", "check_calendar"],
    },
    "philosophy": {
        "patterns": [r"philosophy|theology|ethics|meaning|consciousness|existence|soul|metaphysics|epistemology"],
        "tier": "deep",
        "actions": ["recall_philosophy", "check_topics", "recent_papers"],
    },
}


def classify(text: str) -> List[str]:
    """Classify prediction text into action categories."""
    matches = []
    for cat, cfg in CATEGORIES.items():
        for pattern in cfg["patterns"]:
            if re.search(pattern, text, re.IGNORECASE):
                matches.append(cat)
                break
    return matches or ["general"]


# ─── Actions ─────────────────────────────────────────────────────────────────

def _run(cmd: List[str], timeout: int = 10) -> str:
    """Run command as list of args (no shell=True), return stdout."""
    try:
        r = subprocess.run(cmd, capture_output=True, text=True, timeout=timeout)
        return r.stdout.strip()[:500]  # Cap output
    except Exception:
        return ""


def _shell(cmd: str, timeout: int = 10) -> str:
    """Run a shell pipeline (only for trusted, static commands). Never pass user input."""
    try:
        r = subprocess.run(["sh", "-c", cmd], capture_output=True, text=True, timeout=timeout)
        return r.stdout.strip()[:500]
    except Exception:
        return ""


def _recall(topic: str, top: int = 3) -> str:
    """Quick recall from NIMA."""
    recall_script = WORKSPACE / "lilu_core" / "cli" / "quick_recall.py"
    if not recall_script.exists():
        return ""
    try:
        r = subprocess.run(
            [sys.executable, str(recall_script), topic, "--top", str(top), "--compact"],
            capture_output=True, text=True, timeout=15
        )
        # Extract just the results, skip the header
        lines = r.stdout.strip().split("\n")
        results = [l for l in lines if l.strip() and not l.startswith("#") and not l.startswith("=")]
        return "\n".join(results[:top])[:500]
    except Exception:
        return ""


# Action implementations
def git_status() -> str:
    repos = [WORKSPACE]
    results = []
    for repo in repos:
        if (repo / ".git").exists():
            status = _run(["git", "-C", str(repo), "status", "--short"], timeout=5)
            # Limit to 5 lines
            status = "\n".join(status.split("\n")[:5])
            branch = _run(["git", "-C", str(repo), "branch", "--show-current"], timeout=5)
            if status or branch:
                results.append(f"{repo.name}: [{branch}] {status[:100]}")
    return " | ".join(results) if results else "clean"


def open_prs() -> str:
    return _run(["gh", "pr", "list", "--limit", "3", "--json", "number,title", "--jq", '.[] | "#\\(.number) \\(.title)"'], timeout=10)


def recall_coding() -> str:
    return _recall("coding development bugs fixes")


def recall_research() -> str:
    return _recall("research papers neuroscience NIMA")


def recall_marketing() -> str:
    return _recall("marketing brand content campaign")


def recall_ops() -> str:
    return _recall("deploy server infrastructure")


def recall_personal() -> str:
    return _recall("David family personal")


def check_topics() -> str:
    """Check recent research topics."""
    research_dir = WORKSPACE / "research"
    if not research_dir.exists():
        return ""
    recent = sorted(research_dir.glob("**/*.md"), key=lambda p: p.stat().st_mtime, reverse=True)[:3]
    return " | ".join(p.stem for p in recent)


def load_assets() -> str:
    """Check available marketing assets."""
    assets_dir = WORKSPACE / "assets"
    if not assets_dir.exists():
        return ""
    files = sorted(assets_dir.glob("*"), key=lambda p: p.stat().st_mtime, reverse=True)[:5]
    return " | ".join(p.name for p in files)


def check_services() -> str:
    """Quick service health check."""
    checks = {
        "hive": ["curl", "-s", "-o", "/dev/null", "-w", "%{http_code}", "http://localhost:7777/health"],
        "n8n": ["curl", "-s", "-o", "/dev/null", "-w", "%{http_code}", "http://localhost:5678"],
    }
    results = []
    for name, cmd in checks.items():
        code = _run(cmd, timeout=3)
        results.append(f"{name}:{'✅' if code == '200' else '❌'}")
    return " ".join(results)


def mood_check() -> str:
    """Check current day/time patterns for mood calibration."""
    now = datetime.now()
    day = now.strftime("%A")
    hour = now.hour
    
    if hour < 8:
        return f"{day} early morning — be gentle, grounding"
    elif hour < 12:
        return f"{day} morning — energetic, productive"
    elif hour < 17:
        return f"{day} afternoon — focused, efficient"
    elif hour < 21:
        return f"{day} evening — relaxed, reflective"
    else:
        return f"{day} late night — calm, supportive"


# ─── New Actions ──────────────────────────────────────────────────────────────

def ci_status() -> str:
    """Check CI/CD status for recent runs."""
    return _run(["gh", "run", "list", "--limit", "3", "--json", "status,conclusion,name", "--jq", '.[] | "\\(.name): \\(.conclusion // .status)"'], timeout=10)


def recent_commits() -> str:
    """Get recent commits across active repos."""
    return _run(["git", "-C", str(WORKSPACE), "log", "--oneline", "-5", "--format=%h %s"], timeout=5)


def recent_errors() -> str:
    """Check for recent errors in logs."""
    nima_logs = NIMA_HOME / "logs"
    if not nima_logs.exists():
        return ""
    # Read log files directly instead of shell grep
    errors = []
    for log_file in sorted(nima_logs.glob("*.log"), key=lambda p: p.stat().st_mtime, reverse=True)[:3]:
        try:
            # Read only last 4KB to avoid loading huge files
            size = log_file.stat().st_size
            with open(log_file, "r") as f:
                if size > 4096:
                    f.seek(size - 4096)
                    f.readline()  # Skip partial line
                lines = f.readlines()
            for line in reversed(lines[-50:]):
                if any(kw in line.lower() for kw in ["error", "exception", "fail"]):
                    errors.append(line.strip()[:100])
                    if len(errors) >= 3:
                        break
        except Exception:
            continue
        if len(errors) >= 3:
            break
    return " | ".join(errors) if errors else "no recent errors"


def recent_papers() -> str:
    """Check recently accessed research papers."""
    research_dir = WORKSPACE / "research"
    if not research_dir.exists():
        return ""
    recent = sorted(research_dir.glob("**/*.md"), key=lambda p: p.stat().st_mtime, reverse=True)[:5]
    return " | ".join(p.stem[:40] for p in recent)


def check_calendar() -> str:
    """Check upcoming calendar events (if available)."""
    # Try icalBuddy on macOS
    result = _run(["icalBuddy", "-n", "-nc", "-li", "3", "eventsToday+2"], timeout=5)
    return result[:300] if result else "no calendar access"


def check_email() -> str:
    """Check for recent unread emails (if available)."""
    # Placeholder — implement per mail provider
    return "email check not configured"


def check_analytics() -> str:
    """Check marketing analytics dashboards."""
    return _recall("analytics metrics dashboard KPI")


def check_docs() -> str:
    """Check recently modified documentation."""
    docs_dir = WORKSPACE / "docs"
    if not docs_dir.exists():
        docs_dir = WORKSPACE
    recent = sorted(
        [f for f in docs_dir.glob("**/*.md") if ".git" not in str(f)],
        key=lambda p: p.stat().st_mtime, reverse=True
    )[:3]
    return " | ".join(p.name for p in recent)


def load_spreadsheets() -> str:
    """Find recent spreadsheet/data files (max 2 levels deep)."""
    exts = ["*.csv", "*.xlsx", "*.tsv", "*.json"]
    files = []
    for ext in exts:
        files.extend(WORKSPACE.glob(ext))        # Top level
        files.extend(WORKSPACE.glob(f"*/{ext}"))  # 1 level deep
    # Filter out node_modules, .git, etc.
    files = [f for f in files if not any(skip in str(f) for skip in [".git", "node_modules", ".venv", "__pycache__"])]
    recent = sorted(files, key=lambda p: p.stat().st_mtime, reverse=True)[:3]
    return " | ".join(p.name for p in recent) if recent else ""


def load_design_system() -> str:
    """Check for design system files (max 2 levels deep)."""
    patterns = ["*design*", "*brand*", "*style*", "*theme*", "*tokens*"]
    files = []
    for p in patterns:
        files.extend(WORKSPACE.glob(p))        # Top level
        files.extend(WORKSPACE.glob(f"*/{p}"))  # 1 level deep
    files = [f for f in files if not any(skip in str(f) for skip in [".git", "node_modules", ".venv", "__pycache__"])]
    return " | ".join(f.name for f in files[:5]) if files else ""


# ─── Recall functions for new categories ─────────────────────────────────────

def recall_architecture() -> str:
    return _recall("architecture system design API schema")

def recall_debugging() -> str:
    return _recall("debug error fix traceback exception")

def recall_learning() -> str:
    return _recall("learning tutorial concept explain")

def recall_content() -> str:
    return _recall("blog article content writing editorial")

def recall_creative() -> str:
    return _recall("design brand visual creative mockup")

def recall_business() -> str:
    return _recall("business strategy revenue product roadmap")

def recall_finance() -> str:
    return _recall("finance budget cost invoice expense")

def recall_sales() -> str:
    return _recall("sales deal pipeline prospect outreach")

def recall_security() -> str:
    return _recall("security auth vulnerability audit permission")

def recall_data() -> str:
    return _recall("data analytics dashboard SQL query report")

def recall_communication() -> str:
    return _recall("meeting email agenda presentation sync")

def recall_philosophy() -> str:
    return _recall("philosophy theology consciousness meaning soul")


ACTION_MAP = {
    # Engineering
    "git_status": git_status,
    "open_prs": open_prs,
    "ci_status": ci_status,
    "recent_commits": recent_commits,
    "recent_errors": recent_errors,
    "recall_coding": recall_coding,
    "recall_architecture": recall_architecture,
    "recall_debugging": recall_debugging,
    
    # Research & Learning
    "recall_research": recall_research,
    "recall_learning": recall_learning,
    "check_topics": check_topics,
    "recent_papers": recent_papers,
    
    # Marketing & Creative
    "recall_marketing": recall_marketing,
    "recall_content": recall_content,
    "recall_creative": recall_creative,
    "load_assets": load_assets,
    "load_design_system": load_design_system,
    "check_analytics": check_analytics,
    
    # Business
    "recall_business": recall_business,
    "recall_finance": recall_finance,
    "recall_sales": recall_sales,
    "load_spreadsheets": load_spreadsheets,
    "load_docs": check_docs,
    
    # Ops & Security
    "check_services": check_services,
    "recall_ops": recall_ops,
    "recall_security": recall_security,
    
    # Data
    "recall_data": recall_data,
    
    # Communication
    "check_calendar": check_calendar,
    "check_email": check_email,
    "recall_communication": recall_communication,
    
    # Personal
    "recall_personal": recall_personal,
    "recall_philosophy": recall_philosophy,
    "mood_check": mood_check,
}


# ─── Core API ────────────────────────────────────────────────────────────────

def get_active_precognitions() -> List[Dict]:
    """Read active precognitions from SQLite."""
    if not PRECOG_DB.exists():
        return []
    
    try:
        import sqlite3
        conn = sqlite3.connect(str(PRECOG_DB))
        conn.row_factory = sqlite3.Row
        rows = conn.execute("""
            SELECT what AS prediction_text, confidence, when_predicted, who AS participants
            FROM precognitions
            WHERE status = 'active' OR status = 'pending'
            ORDER BY confidence DESC
            LIMIT 5
        """).fetchall()
        conn.close()
        return [dict(r) for r in rows]
    except Exception:
        return []


def prepare() -> Dict:
    """Run all preparation actions based on active precognitions."""
    PREP_DIR.mkdir(parents=True, exist_ok=True)
    
    precogs = get_active_precognitions()
    if not precogs:
        return {"status": "no_predictions", "actions": []}
    
    # Classify all predictions
    all_categories = set()
    tier_votes = {}
    for p in precogs:
        cats = classify(p.get("prediction_text", ""))
        all_categories.update(cats)
        for cat in cats:
            tier = CATEGORIES.get(cat, {}).get("tier", "balanced")
            tier_votes[tier] = tier_votes.get(tier, 0) + 1
    
    # Determine winning tier (most votes, "deep" wins ties)
    if not tier_votes:
        winning_tier = "balanced"
    else:
        max_votes = max(tier_votes.values())
        tied = [t for t, v in tier_votes.items() if v == max_votes]
        winning_tier = "deep" if "deep" in tied else tied[0]
    
    # Resolve tier to actual available model
    recommended_model = resolve_tier(winning_tier) or "default"
    
    # Collect unique actions
    actions_to_run = set()
    for cat in all_categories:
        cfg = CATEGORIES.get(cat, {})
        for action in cfg.get("actions", []):
            actions_to_run.add(action)
    
    # Execute actions
    results = {}
    for action_name in actions_to_run:
        fn = ACTION_MAP.get(action_name)
        if fn:
            try:
                results[action_name] = fn()
            except Exception as e:
                results[action_name] = f"error: {e}"
    
    # Save prep cache
    # Resolve all tiers for reference
    all_resolved = {}
    for tier_name in MODEL_TIERS:
        resolved = resolve_tier(tier_name)
        if resolved:
            all_resolved[tier_name] = resolved
    
    prep = {
        "timestamp": int(time.time()),
        "categories": list(all_categories),
        "winning_tier": winning_tier,
        "recommended_model": recommended_model,
        "available_tiers": all_resolved,
        "mood": mood_check(),
        "actions": results,
        "precog_count": len(precogs),
    }
    
    cache_path = PREP_DIR / "latest.json"
    cache_path.write_text(json.dumps(prep, indent=2))
    
    return prep


def get_prep_context() -> Optional[str]:
    """Get cached preparation context for injection. Returns compact string or None."""
    cache_path = PREP_DIR / "latest.json"
    if not cache_path.exists():
        return None
    
    try:
        prep = json.loads(cache_path.read_text())
    except Exception:
        return None
    
    # Check TTL
    age = int(time.time()) - prep.get("timestamp", 0)
    if age > PREP_TTL:
        return None  # Stale
    
    # Build compact context
    tier = prep.get('winning_tier', '?')
    model = prep.get('recommended_model', 'default')
    # Show short model name (strip provider prefix)
    short_model = model.split("/")[-1] if "/" in model else model
    parts = [f"🔮 Prep: {','.join(prep['categories'])} | {tier}→{short_model} | {prep['mood']}"]
    
    for action, result in prep.get("actions", {}).items():
        if result and result != "clean" and result != "error":
            short = result[:100].replace("\n", " ")
            parts.append(f"  {action}: {short}")
    
    return "\n".join(parts)


def status() -> str:
    """Show current prep status."""
    cache_path = PREP_DIR / "latest.json"
    if not cache_path.exists():
        return "No preparation cached."
    
    prep = json.loads(cache_path.read_text())
    age_min = (int(time.time()) - prep.get("timestamp", 0)) / 60
    
    lines = [
        f"📋 Precognitive Prep (cached {age_min:.0f}m ago)",
        f"   Categories: {', '.join(prep.get('categories', []))}",
        f"   Tier: {prep.get('winning_tier', '?')} → {prep.get('recommended_model', '?')}",
        f"   Mood: {prep.get('mood', '?')}",
        f"   Actions: {len(prep.get('actions', {}))} completed",
    ]
    
    # Show all available tier mappings
    for tier, model in prep.get("available_tiers", {}).items():
        lines.append(f"   🎯 {tier}: {model}")
    
    for action, result in prep.get("actions", {}).items():
        short = (result or "")[:80].replace("\n", " ")
        lines.append(f"   → {action}: {short}")
    
    return "\n".join(lines)


def clear():
    """Clear prep cache."""
    cache_path = PREP_DIR / "latest.json"
    if cache_path.exists():
        cache_path.unlink()
        return "Cleared."
    return "Nothing to clear."


# ─── CLI ──────────────────────────────────────────────────────────────────────

if __name__ == "__main__":
    cmd = sys.argv[1] if len(sys.argv) > 1 else "prepare"
    
    if cmd == "prepare":
        result = prepare()
        print(json.dumps(result, indent=2))
    elif cmd == "status":
        print(status())
    elif cmd == "clear":
        print(clear())
    elif cmd == "context":
        ctx = get_prep_context()
        print(ctx or "No context available.")
    else:
        print(f"Unknown command: {cmd}")
        print("Usage: precog_actions [prepare|status|context|clear]")
