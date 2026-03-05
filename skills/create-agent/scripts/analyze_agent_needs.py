#!/usr/bin/env python3
"""
Analyze workspace data to suggest new Overstory agents.
Used by create_agent.py --analyze-from-* --suggest-only or run standalone.
"""

from __future__ import annotations

import os
import re
import subprocess
import sys
from pathlib import Path
from typing import Any, Dict, List

WORKSPACE = Path(os.environ.get("NANOBOT_WORKSPACE", os.environ.get("OPENCLAW_WORKSPACE", "/Users/ghost/.openclaw/workspace")))
TROUBLESHOOTING_PATH = WORKSPACE / "TROUBLESHOOTING.md"
OVERSTORY_LOGS = WORKSPACE / ".overstory" / "logs"
OPENCLAW_LOGS = Path.home() / ".openclaw" / "logs"


def _read_text(path: Path, max_chars: int = 100_000) -> str:
    if not path.exists() or not path.is_file():
        return ""
    try:
        return path.read_text(encoding="utf-8", errors="ignore")[:max_chars]
    except OSError:
        return ""


def analyze_troubleshooting(workspace: Path) -> List[Dict[str, Any]]:
    path = workspace / "TROUBLESHOOTING.md"
    text = _read_text(path)
    if not text:
        return []
    suggestions = []
    # Section headers: ## N. Title or ## Title
    section_re = re.compile(r"^##\s+(?:\d+\.\s+)?(.+)$", re.MULTILINE)
    for m in section_re.finditer(text):
        title = m.group(1).strip()
        # Extract keywords that might map to capabilities
        lower = title.lower()
        if "gateway" in lower or "restart" in lower or "error" in lower:
            suggestions.append({
                "source": "TROUBLESHOOTING.md",
                "section": title,
                "suggested_agent": "gateway-health",
                "description": "Monitor gateway health, restarts, and run errors; suggest fixes from TROUBLESHOOTING.md",
                "capabilities": "gateway,health,monitor,troubleshoot",
            })
        if "zombie" in lower or "agent" in lower and ("stuck" in lower or "mail" in lower):
            suggestions.append({
                "source": "TROUBLESHOOTING.md",
                "section": title,
                "suggested_agent": "swarm-ops",
                "description": "Detect zombie agents, unread mail, and stuck workers; run slay or nudge from docs",
                "capabilities": "swarm,ops,zombie,mail",
            })
        if "approval" in lower or "supervisor" in lower or "lead" in lower:
            suggestions.append({
                "source": "TROUBLESHOOTING.md",
                "section": title,
                "suggested_agent": "approval-helper",
                "description": "Explain approval flow and gateway approval supervisor; debug unread-to-lead",
                "capabilities": "approval,supervisor,lead",
            })
        if "doctor" in lower or "syntax" in lower or "node" in lower or "cli" in lower:
            suggestions.append({
                "source": "TROUBLESHOOTING.md",
                "section": title,
                "suggested_agent": "cli-troubleshooter",
                "description": "Diagnose OpenClaw CLI and Node/syntax errors using TROUBLESHOOTING.md",
                "capabilities": "cli,diagnose,troubleshoot",
            })
    # Deduplicate by suggested_agent
    seen = set()
    out = []
    for s in suggestions:
        key = s["suggested_agent"]
        if key not in seen:
            seen.add(key)
            out.append(s)
    return out


def analyze_logs(workspace: Path, log_dirs: List[Path]) -> List[Dict[str, Any]]:
    suggestions = []
    for log_dir in log_dirs:
        if not log_dir.is_dir():
            continue
        for f in sorted(log_dir.glob("*.log"))[:5]:
            text = _read_text(f, max_chars=50_000)
            if "error" in text.lower() and "gateway" in text.lower():
                suggestions.append({
                    "source": str(f),
                    "suggested_agent": "log-analyzer",
                    "description": "Analyze OverClaw/gateway logs for errors and suggest next steps",
                    "capabilities": "log,analyze,error,gateway",
                })
                break
    return suggestions


def analyze_mulch(workspace: Path) -> List[Dict[str, Any]]:
    try:
        r = subprocess.run(
            ["mulch", "query", "--list-domains"],
            cwd=str(workspace),
            capture_output=True,
            text=True,
            timeout=10,
        )
        if r.returncode != 0:
            return []
        # Could parse domains and suggest an agent that primes/records per domain
        domains = (r.stdout or "").strip().splitlines()
        if domains:
            return [{
                "source": "mulch",
                "suggested_agent": "mulch-curator",
                "description": "Prime and record mulch domains for agents; suggest domains from project",
                "capabilities": "mulch,expertise,curate",
            }]
    except (FileNotFoundError, subprocess.TimeoutExpired):
        pass
    return []


def analyze_project_tree(workspace: Path, max_dirs: int = 50) -> List[Dict[str, Any]]:
    suggestions = []
    skills_dir = workspace / "skills"
    if skills_dir.is_dir():
        names = [d.name for d in sorted(skills_dir.iterdir()) if d.is_dir()][:max_dirs]
        # Suggest a "skill-runner" or "skill-dispatcher" if many skills
        if len(names) > 15:
            suggestions.append({
                "source": "project tree (skills/)",
                "suggested_agent": "skill-dispatcher",
                "description": "Run and coordinate skills from the workspace skills directory",
                "capabilities": "skill,exec,dispatch",
            })
    return suggestions


def run_analysis(
    workspace: Path,
    from_logs: bool = False,
    from_troubleshooting: bool = True,
    from_mulch: bool = False,
    from_project: bool = False,
) -> List[Dict[str, Any]]:
    results = []
    if from_troubleshooting:
        results.extend(analyze_troubleshooting(workspace))
    if from_logs:
        results.extend(analyze_logs(workspace, [OVERSTORY_LOGS, OPENCLAW_LOGS]))
    if from_mulch:
        results.extend(analyze_mulch(workspace))
    if from_project:
        results.extend(analyze_project_tree(workspace))
    return results


def format_suggestion(s: Dict[str, Any]) -> str:
    parts = [f"Agent: {s['suggested_agent']}", f"  Description: {s['description']}", f"  Capabilities: {s['capabilities']}", f"  Source: {s.get('source', '')}"]
    if s.get("section"):
        parts.insert(1, f"  Section: {s['section']}")
    return "\n".join(parts)


def main() -> int:
    import argparse
    p = argparse.ArgumentParser(description="Suggest new Overstory agents from workspace data")
    p.add_argument("--workspace", type=Path, default=WORKSPACE)
    p.add_argument("--from-logs", action="store_true")
    p.add_argument("--from-troubleshooting", action="store_true", default=True)
    p.add_argument("--from-mulch", action="store_true")
    p.add_argument("--from-project", action="store_true")
    args = p.parse_args()
    suggestions = run_analysis(
        args.workspace,
        from_logs=args.from_logs,
        from_troubleshooting=args.from_troubleshooting,
        from_mulch=args.from_mulch,
        from_project=args.from_project,
    )
    for s in suggestions:
        print(format_suggestion(s))
        print()
    return 0


if __name__ == "__main__":
    sys.exit(main())
