#!/usr/bin/env python3
import argparse
import json
import subprocess
import sys
from datetime import datetime, timezone
from pathlib import Path

HERE = Path(__file__).resolve().parent


def run_json(script: str, args, cwd: Path):
    cmd = [sys.executable, str(HERE / script), *args, "--json"]
    proc = subprocess.run(cmd, cwd=str(cwd), capture_output=True, text=True)
    if proc.returncode != 0:
        return {
            "error": "command_failed",
            "returncode": proc.returncode,
            "stdout": proc.stdout.strip()[:2000],
            "stderr": proc.stderr.strip()[:2000],
            "cmd": cmd,
        }
    try:
        return json.loads(proc.stdout)
    except json.JSONDecodeError:
        return {
            "error": "invalid_json",
            "stdout": proc.stdout.strip()[:2000],
            "stderr": proc.stderr.strip()[:2000],
            "cmd": cmd,
        }


def write_json(path: Path, payload):
    path.write_text(json.dumps(payload, indent=2))


def write_if_missing(path: Path, content: str, overwrite: bool):
    if path.exists() and not overwrite:
        return False
    path.write_text(content)
    return True


def main():
    parser = argparse.ArgumentParser(description="Run Clawditor helper scripts and write draft eval/ outputs.")
    parser.add_argument("path", nargs="?", default=".", help="Workspace root")
    parser.add_argument("--out", default="eval", help="Output directory under workspace")
    parser.add_argument("--depth", type=int, default=4, help="Tree depth for inventory")
    parser.add_argument("--top", type=int, default=20, help="Top N largest files")
    parser.add_argument("--since", default="30 days", help="Git log lookback")
    parser.add_argument("--include-root-logs", action="store_true", help="Also scan root for log-like files")
    parser.add_argument("--overwrite", action="store_true", help="Overwrite draft markdown/json templates")
    args = parser.parse_args()

    root = Path(args.path).resolve()
    out_dir = root / args.out
    out_dir.mkdir(parents=True, exist_ok=True)

    inventory = run_json("workspace_inventory.py", [str(root), "--depth", str(args.depth), "--top", str(args.top)], cwd=root)
    memory_dupes = run_json("memory_dupes.py", [str(root / "memory")], cwd=root)

    log_args = [str(root)]
    if args.include_root_logs:
        log_args.append("--include-root")
    log_scan = run_json("log_scan.py", log_args, cwd=root)

    git_stats = run_json("git_stats.py", [str(root), "--since", args.since], cwd=root)

    write_json(out_dir / "inventory.json", inventory)
    write_json(out_dir / "memory_dupes.json", memory_dupes)
    write_json(out_dir / "log_scan.json", log_scan)
    write_json(out_dir / "git_stats.json", git_stats)

    ts = datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")
    git_head = ""
    if isinstance(git_stats, dict):
        git_head = git_stats.get("head", "") or ""

    exec_summary = """# Exec Summary

- Overall score: __ (Memory __, Retrieval __, Productive __, Quality __, Focus __)
- Claw-to-claw delta: __
- Win: __
- Win: __
- Bottleneck: __
- Bottleneck: __
- Intervention: __
- Intervention: __
- Intervention: __
- Risk: __
"""

    scorecard = """# Scorecard

| Category | Score | Evidence | Rationale |
| --- | --- | --- | --- |
| Memory Health | __ | __ | __ |
| Retrieval & Context Efficiency | __ | __ | __ |
| Productive Output | __ | __ | __ |
| Quality / Reliability | __ | __ | __ |
| Focus / Alignment | __ | __ | __ |

## Top Evidence
- __
"""

    latest_report = {
        "timestamp": ts,
        "workspace": {"path": str(root), "hash_or_git_head": git_head},
        "scores": {
            "overall": 0,
            "memory": 0,
            "retrieval": 0,
            "productive": 0,
            "quality": 0,
            "focus": 0,
        },
        "deltas_vs_previous": {
            "overall": 0,
            "memory": 0,
            "retrieval": 0,
            "productive": 0,
            "quality": 0,
            "focus": 0,
        },
        "key_findings": [],
        "risk_flags": [],
        "recommendations": [
            {"title": "", "impact": "med", "effort": "med", "steps": []}
        ],
    }

    write_if_missing(out_dir / "exec_summary.md", exec_summary, args.overwrite)
    write_if_missing(out_dir / "scorecard.md", scorecard, args.overwrite)
    if (out_dir / "latest_report.json").exists() and not args.overwrite:
        pass
    else:
        write_json(out_dir / "latest_report.json", latest_report)

    print(f"Wrote outputs to {out_dir}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
