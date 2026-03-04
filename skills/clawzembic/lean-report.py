#!/usr/bin/env python3
"""Clawzembic — Weight Loss for Your OpenClaw Instance.

Audits an OpenClaw installation and produces a scored report.
Zero external dependencies beyond Python 3.8+ stdlib.
"""

import argparse
import glob
import json
import os
import sys
from pathlib import Path

# ── Styling ──────────────────────────────────────────────────────────

GREEN = "\033[92m"
YELLOW = "\033[93m"
RED = "\033[91m"
CYAN = "\033[96m"
BOLD = "\033[1m"
DIM = "\033[2m"
RESET = "\033[0m"
PILL = "💊"

def color(text, c):
    return f"{c}{text}{RESET}"

def grade_color(score):
    if score >= 90: return GREEN
    if score >= 75: return CYAN
    if score >= 60: return YELLOW
    return RED

def letter_grade(score):
    if score >= 95: return "A+"
    if score >= 90: return "A"
    if score >= 85: return "B+"
    if score >= 75: return "B"
    if score >= 65: return "C+"
    if score >= 60: return "C"
    if score >= 50: return "D+"
    if score >= 45: return "D"
    return "F"

def status_icon(score):
    if score >= 90: return "✅"
    if score >= 75: return "🟡"
    if score >= 60: return "🟠"
    return "🔴"

# ── Data Collection ──────────────────────────────────────────────────

def find_workspace(openclaw_dir):
    """Find the workspace directory."""
    ws = os.path.join(openclaw_dir, "workspace")
    if os.path.isdir(ws):
        return ws
    return None

def find_agents_dir(openclaw_dir):
    """Find agents sessions directory."""
    agents = os.path.join(openclaw_dir, "agents")
    if os.path.isdir(agents):
        return agents
    return None

def find_cron_dir(openclaw_dir):
    """Find cron store."""
    cron = os.path.join(openclaw_dir, "cron")
    if os.path.isdir(cron):
        return cron
    return None

def read_json(path):
    try:
        with open(path) as f:
            return json.load(f)
    except (json.JSONDecodeError, FileNotFoundError, PermissionError):
        return None

def file_size(path):
    try:
        return os.path.getsize(path)
    except (FileNotFoundError, PermissionError):
        return 0

def dir_size(path):
    total = 0
    try:
        for dirpath, _, filenames in os.walk(path):
            for f in filenames:
                fp = os.path.join(dirpath, f)
                try:
                    total += os.path.getsize(fp)
                except (FileNotFoundError, PermissionError):
                    pass
    except (FileNotFoundError, PermissionError):
        pass
    return total

# ── Audit Checks ─────────────────────────────────────────────────────

def audit_context_injection(workspace):
    """Check workspace file sizes injected into every session."""
    results = {"score": 100, "findings": [], "files": {}, "total_bytes": 0}
    if not workspace:
        results["findings"].append(("warn", "No workspace directory found"))
        results["score"] = 50
        return results

    inject_files = ["MEMORY.md", "SOUL.md", "AGENTS.md", "IDENTITY.md",
                    "TOOLS.md", "USER.md", "HEARTBEAT.md", "BOOTSTRAP.md"]
    total = 0
    for fname in inject_files:
        fpath = os.path.join(workspace, fname)
        sz = file_size(fpath)
        if sz > 0:
            results["files"][fname] = sz
            total += sz

    results["total_bytes"] = total

    # Scoring
    if total > 50000:
        results["score"] = 20
        results["findings"].append(("fail", f"Workspace files total {total:,} bytes ({total//1024}KB) — severely bloated"))
    elif total > 30000:
        results["score"] = 45
        results["findings"].append(("fail", f"Workspace files total {total:,} bytes ({total//1024}KB) — too large"))
    elif total > 20000:
        results["score"] = 60
        results["findings"].append(("warn", f"Workspace files total {total:,} bytes ({total//1024}KB) — could be leaner"))
    elif total > 15000:
        results["score"] = 75
        results["findings"].append(("warn", f"Workspace files total {total:,} bytes ({total//1024}KB) — slightly heavy"))
    else:
        results["findings"].append(("pass", f"Workspace files total {total:,} bytes ({total//1024}KB) — lean"))

    # Flag individual big files
    for fname, sz in sorted(results["files"].items(), key=lambda x: -x[1]):
        if sz > 15000:
            results["findings"].append(("fail", f"  {fname}: {sz:,} bytes — compress or archive"))
        elif sz > 8000:
            results["findings"].append(("warn", f"  {fname}: {sz:,} bytes — could be trimmed"))
        else:
            results["findings"].append(("pass", f"  {fname}: {sz:,} bytes"))

    return results


def audit_cron_health(openclaw_dir):
    """Check cron job configuration for waste."""
    results = {"score": 100, "findings": [], "enabled": 0, "disabled": 0, "issues": []}
    cron_dir = find_cron_dir(openclaw_dir)
    if not cron_dir:
        results["findings"].append(("warn", "No cron directory found"))
        results["score"] = 70
        return results

    # Find cron store
    cron_file = os.path.join(cron_dir, "jobs.json")
    if not os.path.exists(cron_file):
        # Try alternate locations
        for pattern in [os.path.join(cron_dir, "*.json")]:
            files = glob.glob(pattern)
            if files:
                cron_file = files[0]
                break

    data = read_json(cron_file)
    if not data:
        results["findings"].append(("warn", "Could not read cron store"))
        results["score"] = 70
        return results

    # Handle various cron store formats
    if isinstance(data, dict):
        if "jobs" in data:
            jobs = data["jobs"]
            if isinstance(jobs, dict):
                jobs = list(jobs.values())
            elif not isinstance(jobs, list):
                jobs = []
        else:
            jobs = list(data.values())
    elif isinstance(data, list):
        jobs = data
    else:
        jobs = []

    penalties = 0
    enabled_jobs = []
    disabled_count = 0

    for job in jobs:
        if not isinstance(job, dict):
            continue
        if not job.get("enabled", True):
            disabled_count += 1
            continue
        enabled_jobs.append(job)

    results["enabled"] = len(enabled_jobs)
    results["disabled"] = disabled_count
    results["findings"].append(("info", f"Cron jobs: {len(enabled_jobs)} enabled, {disabled_count} disabled"))

    for job in enabled_jobs:
        name = job.get("name", job.get("id", "unknown"))[:50]
        payload = job.get("payload", {})
        model = payload.get("model", "default")
        thinking = payload.get("thinking", "default")
        target = job.get("sessionTarget", "unknown")

        issues = []

        # Flag main-session targeting
        if target == "main":
            issues.append("targets main session (context pollution)")
            penalties += 15

        # Flag default/Opus model on routine tasks
        is_security = any(kw in name.lower() for kw in ["security", "merith", "pyroblast", "knight", "patrol", "vigilant"])
        is_council = any(kw in name.lower() for kw in ["council", "deliberat"])
        if model in ("default", "") and not is_security and not is_council:
            issues.append(f"uses default model (likely Opus) — consider Sonnet")
            penalties += 5
        if "opus" in model.lower() and not is_security and not is_council:
            issues.append(f"uses Opus ({model}) — Sonnet likely sufficient")
            penalties += 5

        # Flag high thinking on routine tasks
        if thinking in ("high", "default") and not is_security and not is_council:
            issues.append(f"thinking={thinking} — low is fine for routine tasks")
            penalties += 3

        # Flag very frequent crons
        schedule = job.get("schedule", {})
        if schedule.get("kind") == "every":
            every_ms = schedule.get("everyMs", 0)
            if every_ms > 0 and every_ms < 1800000:  # < 30 min
                issues.append(f"fires every {every_ms//60000}m — very frequent")
                penalties += 10
        if schedule.get("kind") == "cron":
            expr = schedule.get("expr", "")
            # Detect */N minute patterns
            if expr.startswith("*/") and " " in expr:
                minute_part = expr.split()[0] if expr.split() else ""
                if minute_part.startswith("*/"):
                    try:
                        interval = int(minute_part[2:])
                        if interval < 30:
                            issues.append(f"fires every {interval}m — very frequent")
                            penalties += 10
                    except ValueError:
                        pass

        if issues:
            for issue in issues:
                results["findings"].append(("warn", f"  [{name}] {issue}"))
                results["issues"].append({"job": name, "issue": issue})
        else:
            results["findings"].append(("pass", f"  [{name}] model={model} thinking={thinking} ✓"))

    # Total enabled crons penalty
    if len(enabled_jobs) > 30:
        penalties += 20
        results["findings"].append(("fail", f"Too many enabled crons ({len(enabled_jobs)}) — consider disabling non-essential"))
    elif len(enabled_jobs) > 20:
        penalties += 10
        results["findings"].append(("warn", f"Many enabled crons ({len(enabled_jobs)}) — review necessity"))

    results["score"] = max(0, 100 - penalties)
    return results


def audit_session_bloat(openclaw_dir):
    """Check for bloated and stale sessions."""
    results = {"score": 100, "findings": [], "sessions": 0, "stale": 0, "total_tokens": 0, "waste_tokens": 0}
    agents_dir = find_agents_dir(openclaw_dir)
    if not agents_dir:
        results["findings"].append(("warn", "No agents directory found"))
        results["score"] = 70
        return results

    penalties = 0
    import time
    now_ms = int(time.time() * 1000)

    # Check all agent session stores
    for agent_dir in glob.glob(os.path.join(agents_dir, "*")):
        sessions_file = os.path.join(agent_dir, "sessions", "sessions.json")
        store = read_json(sessions_file)
        if not store or not isinstance(store, dict):
            continue

        for key, entry in store.items():
            if not isinstance(entry, dict):
                continue
            results["sessions"] += 1
            tokens = entry.get("totalTokens", 0) or 0
            ctx = entry.get("contextTokens", 200000) or 200000
            pct = round(tokens / ctx * 100) if ctx else 0
            updated = entry.get("updatedAt", 0) or 0
            age_hours = (now_ms - updated) / 3600000 if updated else 999

            results["total_tokens"] += tokens

            is_main = key.endswith(":main")

            # Flag bloated non-main sessions
            if pct >= 40 and not is_main:
                penalties += 8
                results["waste_tokens"] += tokens
                results["findings"].append(("fail", f"  {key}: {pct}% ({tokens:,} tokens) — bloated"))
                results["stale"] += 1
            elif pct >= 25 and age_hours > 24 and not is_main:
                penalties += 4
                results["waste_tokens"] += tokens
                results["findings"].append(("warn", f"  {key}: {pct}% ({tokens:,} tokens), {age_hours:.0f}h stale"))
                results["stale"] += 1
            elif pct >= 60 and is_main:
                penalties += 5
                results["findings"].append(("warn", f"  {key}: {pct}% — main session running hot"))

    waste_ratio = results["waste_tokens"] / results["total_tokens"] if results["total_tokens"] else 0
    results["findings"].insert(0, ("info", f"Sessions: {results['sessions']} total, {results['stale']} stale/bloated, waste ratio: {waste_ratio:.0%}"))
    results["score"] = max(0, 100 - penalties)
    return results


def audit_config_health(openclaw_dir):
    """Check gateway config for efficiency settings."""
    results = {"score": 100, "findings": []}
    config_path = os.path.join(openclaw_dir, "openclaw.json")
    cfg = read_json(config_path)
    if not cfg:
        results["findings"].append(("warn", "Could not read openclaw.json"))
        results["score"] = 50
        return results

    penalties = 0
    defaults = cfg.get("agents", {}).get("defaults", {})

    # Heartbeat
    hb = defaults.get("heartbeat", {})
    hb_every = hb.get("every", "30m") if isinstance(hb, dict) else "30m"
    hb_minutes = parse_duration_minutes(hb_every)
    if hb_minutes < 60:
        penalties += 10
        results["findings"].append(("warn", f"Heartbeat every {hb_every} — consider 60m+ to reduce idle context growth"))
    else:
        results["findings"].append(("pass", f"Heartbeat every {hb_every} ✓"))

    # Thinking default
    thinking = defaults.get("thinkingDefault", "default")
    if thinking == "high":
        penalties += 8
        results["findings"].append(("warn", f"Default thinking: {thinking} — high for everything wastes tokens"))
    else:
        results["findings"].append(("pass", f"Default thinking: {thinking} ✓"))

    # Subagent model
    sub = defaults.get("subagents", {})
    sub_model = sub.get("model", "default")
    sub_thinking = sub.get("thinking", "default")
    if "opus" in sub_model.lower():
        penalties += 8
        results["findings"].append(("warn", f"Subagent model: {sub_model} — Sonnet handles most tasks"))
    else:
        results["findings"].append(("pass", f"Subagent model: {sub_model} ✓"))
    if sub_thinking in ("high", "medium"):
        penalties += 3
        results["findings"].append(("warn", f"Subagent thinking: {sub_thinking} — low is fine for most"))

    # Compaction
    compaction = defaults.get("compaction", {})
    comp_mode = compaction.get("mode", "none")
    if comp_mode == "safeguard":
        results["findings"].append(("pass", f"Compaction: safeguard mode ✓"))
    elif comp_mode == "none" or not compaction:
        penalties += 10
        results["findings"].append(("fail", "Compaction not configured — sessions will fill and lose context"))
    else:
        results["findings"].append(("pass", f"Compaction: {comp_mode}"))

    # Context pruning
    pruning = defaults.get("contextPruning", {})
    if pruning:
        results["findings"].append(("pass", f"Context pruning: {pruning.get('mode', 'enabled')} ✓"))
    else:
        penalties += 5
        results["findings"].append(("warn", "No context pruning configured"))

    # Session auto-reset
    session = cfg.get("session", {})
    reset = session.get("reset", {})
    if reset:
        results["findings"].append(("pass", f"Session auto-reset: {reset.get('mode', 'configured')} ✓"))
    else:
        penalties += 5
        results["findings"].append(("warn", "No session auto-reset — stale sessions accumulate"))

    results["score"] = max(0, 100 - penalties)
    return results


def audit_skill_bloat(workspace):
    """Check for excessive skill injection."""
    results = {"score": 100, "findings": [], "custom": 0, "builtin": 0}
    if not workspace:
        results["findings"].append(("warn", "No workspace found"))
        results["score"] = 70
        return results

    penalties = 0

    # Count custom skills
    skills_dir = os.path.join(workspace, "skills")
    custom = 0
    if os.path.isdir(skills_dir):
        for entry in os.listdir(skills_dir):
            skill_md = os.path.join(skills_dir, entry, "SKILL.md")
            if os.path.isfile(skill_md):
                custom += 1
    results["custom"] = custom

    # Estimate built-in skills (look for node_modules openclaw skills)
    builtin = 0
    found = False
    for search in ["/opt/homebrew/lib/node_modules/openclaw/skills",
                   "/usr/local/lib/node_modules/openclaw/skills",
                   os.path.expanduser("~/.nvm/versions/node/*/lib/node_modules/openclaw/skills")]:
        for skills_path in glob.glob(search):
            if os.path.isdir(skills_path):
                for entry in os.listdir(skills_path):
                    if os.path.isfile(os.path.join(skills_path, entry, "SKILL.md")):
                        builtin += 1
                found = True
                break
        if found:
            break
    results["builtin"] = builtin

    total = custom + builtin
    results["findings"].append(("info", f"Skills: {custom} custom + {builtin} built-in = {total} total"))

    # Each skill description adds ~100-200 tokens to system prompt
    est_tokens = total * 150
    results["findings"].append(("info", f"Estimated system prompt cost: ~{est_tokens:,} tokens per session"))

    if custom > 25:
        penalties += 20
        results["findings"].append(("fail", f"Too many custom skills ({custom}) — prune unused ones"))
    elif custom > 15:
        penalties += 10
        results["findings"].append(("warn", f"Many custom skills ({custom}) — consider pruning"))
    elif custom > 10:
        penalties += 3
        results["findings"].append(("info", f"Custom skills ({custom}) — reasonable"))
    else:
        results["findings"].append(("pass", f"Custom skills ({custom}) — lean ✓"))

    return results


def audit_transcript_size(openclaw_dir):
    """Check transcript disk usage."""
    results = {"score": 100, "findings": [], "total_bytes": 0, "file_count": 0, "oversized": []}
    agents_dir = find_agents_dir(openclaw_dir)
    if not agents_dir:
        results["findings"].append(("warn", "No agents directory found"))
        results["score"] = 70
        return results

    penalties = 0
    total_bytes = 0
    file_count = 0
    oversized = []

    for jsonl in glob.glob(os.path.join(agents_dir, "**", "*.jsonl"), recursive=True):
        sz = file_size(jsonl)
        total_bytes += sz
        file_count += 1
        if sz > 10 * 1024 * 1024:  # > 10MB
            oversized.append((jsonl, sz))

    results["total_bytes"] = total_bytes
    results["file_count"] = file_count
    results["oversized"] = [(p, s) for p, s in oversized]

    mb = total_bytes / (1024 * 1024)
    results["findings"].append(("info", f"Transcripts: {file_count} files, {mb:.1f}MB total"))

    if total_bytes > 500 * 1024 * 1024:
        penalties += 25
        results["findings"].append(("fail", f"Transcript storage: {mb:.0f}MB — needs cleanup"))
    elif total_bytes > 200 * 1024 * 1024:
        penalties += 15
        results["findings"].append(("warn", f"Transcript storage: {mb:.0f}MB — getting heavy"))
    elif total_bytes > 100 * 1024 * 1024:
        penalties += 5
        results["findings"].append(("warn", f"Transcript storage: {mb:.0f}MB — watch it"))
    else:
        results["findings"].append(("pass", f"Transcript storage: {mb:.1f}MB — reasonable ✓"))

    for path, sz in oversized:
        fname = os.path.basename(path)
        penalties += 5
        results["findings"].append(("warn", f"  {fname}: {sz/(1024*1024):.1f}MB — oversized"))

    results["score"] = max(0, 100 - penalties)
    return results


# ── Helpers ──────────────────────────────────────────────────────────

def parse_duration_minutes(s):
    """Parse '30m', '2h', etc. to minutes."""
    if not s:
        return 30
    s = str(s).strip().lower()
    try:
        if s.endswith("m"):
            return int(s[:-1])
        if s.endswith("h"):
            return int(s[:-1]) * 60
        if s.endswith("s"):
            return int(s[:-1]) // 60
        return int(s)
    except (ValueError, TypeError):
        return 30


# ── Report ───────────────────────────────────────────────────────────

WEIGHTS = {
    "context_injection": 0.25,
    "cron_health": 0.25,
    "session_bloat": 0.20,
    "config_health": 0.15,
    "skill_bloat": 0.10,
    "transcript_size": 0.05,
}

CATEGORY_NAMES = {
    "context_injection": "Context Injection",
    "cron_health": "Cron Health",
    "session_bloat": "Session Bloat",
    "config_health": "Config Health",
    "skill_bloat": "Skill Bloat",
    "transcript_size": "Transcript Size",
}


def run_audit(openclaw_dir):
    workspace = find_workspace(openclaw_dir)
    return {
        "context_injection": audit_context_injection(workspace),
        "cron_health": audit_cron_health(openclaw_dir),
        "session_bloat": audit_session_bloat(openclaw_dir),
        "config_health": audit_config_health(openclaw_dir),
        "skill_bloat": audit_skill_bloat(workspace),
        "transcript_size": audit_transcript_size(openclaw_dir),
    }


def compute_total(audits):
    total = 0
    for cat, weight in WEIGHTS.items():
        total += audits[cat]["score"] * weight
    return round(total)


def print_report(audits, json_mode=False):
    total_score = compute_total(audits)
    grade = letter_grade(total_score)

    if json_mode:
        output = {
            "tool": "clawzembic",
            "version": "1.0.0",
            "score": total_score,
            "grade": grade,
            "categories": {}
        }
        for cat in WEIGHTS:
            output["categories"][cat] = {
                "score": audits[cat]["score"],
                "grade": letter_grade(audits[cat]["score"]),
                "findings": audits[cat]["findings"],
            }
        print(json.dumps(output, indent=2))
        return

    # Pretty terminal output
    gc = grade_color(total_score)
    print()
    print(f"  {BOLD}{PILL} Clawzembic Audit Report{RESET}")
    print(f"  {'─' * 50}")
    print()
    print(f"  Overall Score: {color(f'{total_score}/100', gc)}  Grade: {color(grade, gc)}")
    print()

    for cat in WEIGHTS:
        audit = audits[cat]
        score = audit["score"]
        name = CATEGORY_NAMES[cat]
        weight_pct = int(WEIGHTS[cat] * 100)
        sc = grade_color(score)
        icon = status_icon(score)

        print(f"  {icon} {BOLD}{name}{RESET} ({weight_pct}% weight) — {color(f'{score}/100 {letter_grade(score)}', sc)}")

        for level, msg in audit["findings"]:
            if level == "fail":
                print(f"     {RED}✗{RESET} {msg}")
            elif level == "warn":
                print(f"     {YELLOW}⚠{RESET} {msg}")
            elif level == "pass":
                print(f"     {GREEN}✓{RESET} {msg}")
            else:
                print(f"     {DIM}ℹ{RESET} {msg}")
        print()

    # Summary
    print(f"  {'─' * 50}")
    if total_score >= 90:
        print(f"  {GREEN}{BOLD}Lean machine! Your instance is in great shape. {PILL}{RESET}")
    elif total_score >= 75:
        print(f"  {CYAN}{BOLD}Good shape — a few tweaks and you're golden. {PILL}{RESET}")
    elif total_score >= 60:
        print(f"  {YELLOW}{BOLD}Needs a diet. Run with --fix for recommendations. {PILL}{RESET}")
    elif total_score >= 45:
        print(f"  {RED}{BOLD}Significant bloat detected. Time for Clawzembic. {PILL}{RESET}")
    else:
        print(f"  {RED}{BOLD}Emergency intervention needed. 🚨{PILL}{RESET}")
    print()


def main():
    parser = argparse.ArgumentParser(description="Clawzembic — OpenClaw Instance Audit")
    parser.add_argument("--openclaw-dir", default=os.path.expanduser("~/.openclaw"),
                        help="Path to .openclaw directory")
    parser.add_argument("--json", action="store_true", help="JSON output")
    parser.add_argument("--fix", action="store_true", help="Show fix commands")
    args = parser.parse_args()

    audits = run_audit(args.openclaw_dir)
    print_report(audits, json_mode=args.json)

    if args.fix:
        print_fixes(audits)


def print_fixes(audits):
    """Print actionable fix commands."""
    print(f"\n  {BOLD}{PILL} Recommended Fixes{RESET}")
    print(f"  {'─' * 50}\n")

    fixes = []

    # Context injection fixes
    ci = audits["context_injection"]
    if ci["score"] < 75:
        fixes.append(("Compact MEMORY.md", "Move historical content to memory/*.md archives. Target: <8KB."))

    # Cron fixes
    ch = audits["cron_health"]
    for issue_data in ch.get("issues", []):
        job = issue_data["job"]
        issue = issue_data["issue"]
        if "default model" in issue or "Opus" in issue:
            fixes.append((f"Right-size [{job}]", f"openclaw cron edit <id> --model anthropic/claude-sonnet-4-5"))
        if "thinking" in issue:
            fixes.append((f"Lower thinking [{job}]", f"openclaw cron edit <id> --thinking low"))
        if "main session" in issue:
            fixes.append((f"Isolate [{job}]", f"openclaw cron edit <id> --session isolated"))

    # Session fixes
    sb = audits["session_bloat"]
    if sb.get("stale", 0) > 0:
        fixes.append(("Clean stale sessions", "Delete bloated entries from agents/*/sessions/sessions.json (safe — they recreate on demand)"))

    # Config fixes
    cfg = audits["config_health"]
    for level, msg in cfg["findings"]:
        if level == "warn" and "Heartbeat" in msg:
            fixes.append(("Increase heartbeat", 'Set agents.defaults.heartbeat.every to "120m" in openclaw.json'))
        if level == "warn" and "Subagent model" in msg:
            fixes.append(("Right-size subagents", 'Set agents.defaults.subagents.model to "anthropic/claude-sonnet-4-5"'))
        if level == "fail" and "Compaction" in msg:
            fixes.append(("Enable compaction", 'Set agents.defaults.compaction.mode to "safeguard" in openclaw.json'))

    # Skill fixes
    sk = audits["skill_bloat"]
    if sk["custom"] > 15:
        fixes.append(("Prune skills", "Move unused skills to skills-disabled/ directory"))

    if fixes:
        for i, (title, cmd) in enumerate(fixes, 1):
            print(f"  {i}. {BOLD}{title}{RESET}")
            print(f"     {DIM}{cmd}{RESET}")
            print()
    else:
        print(f"  {GREEN}No fixes needed — you're lean! ✓{RESET}\n")


if __name__ == "__main__":
    main()
