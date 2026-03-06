#!/usr/bin/env python3
import argparse
import json
import subprocess
import sys
from pathlib import Path
from typing import Dict, List, Tuple


DEFAULT_OUT = Path.home() / ".openclaw" / "security" / "approved_ports.json"


def parse_args() -> argparse.Namespace:
    p = argparse.ArgumentParser(
        description="Generate an approved listening-port baseline from current services."
    )
    p.add_argument(
        "--output",
        default=str(DEFAULT_OUT),
        help="Where to write the approved ports JSON baseline",
    )
    p.add_argument(
        "--skill-dir",
        default=str(Path(__file__).resolve().parent.parent),
        help="Path to cyber-security-engineer skill directory (for calling port_monitor.py)",
    )
    p.add_argument(
        "--include-command",
        action="store_true",
        default=True,
        help="Include the command name in each rule (recommended)",
    )
    return p.parse_args()


def run_port_monitor(skill_dir: Path) -> Dict[str, object]:
    port_monitor = skill_dir / "scripts" / "port_monitor.py"
    if not port_monitor.exists():
        raise FileNotFoundError(f"port_monitor.py not found at {port_monitor}")
    # Use an empty-but-valid approved file so we always get a full inventory.
    # (port_monitor expects JSON; passing /dev/null would cause JSON parse errors.)
    empty_approved = Path("/tmp/openclaw-approved-ports-empty.json")
    try:
        empty_approved.write_text("[]\n", encoding="utf-8")
    except Exception:
        # Best-effort fallback: if we can't write /tmp, omit approved-file entirely.
        empty_approved = None
    cmd = [
        sys.executable,
        str(port_monitor),
        "--json",
    ]
    if empty_approved is not None:
        cmd.extend(["--approved-file", str(empty_approved)])
    proc = subprocess.run(cmd, capture_output=True, text=True)
    if proc.returncode != 0:
        raise RuntimeError(proc.stderr.strip() or proc.stdout.strip() or "port_monitor failed")
    return json.loads(proc.stdout)


def normalize_listeners(listening: List[Dict[str, object]], include_command: bool) -> Tuple[List[Dict[str, object]], int]:
    rules: List[Dict[str, object]] = []
    seen = set()
    for entry in listening:
        try:
            port = int(entry.get("port"))
        except Exception:
            continue
        proto = str(entry.get("protocol") or "tcp").lower()
        cmd = str(entry.get("command") or "").strip()

        rule: Dict[str, object] = {"port": port, "protocol": proto}
        if include_command and cmd:
            rule["command"] = cmd
        # Note: keep extra fields for human review; port_monitor ignores unknown keys.
        if entry.get("host"):
            rule["host"] = entry.get("host")
        if entry.get("user"):
            rule["user"] = entry.get("user")
        if entry.get("pid") not in (None, "", "unknown"):
            rule["pid"] = entry.get("pid")

        dedupe = (rule.get("port"), rule.get("protocol"), rule.get("command"))
        if dedupe in seen:
            continue
        seen.add(dedupe)
        rules.append(rule)

    rules.sort(key=lambda r: (int(r.get("port", 0)), str(r.get("protocol", "")), str(r.get("command", ""))))
    return rules, len(seen)


def main() -> int:
    args = parse_args()
    out = Path(args.output).expanduser()
    skill_dir = Path(args.skill_dir).expanduser()

    report = run_port_monitor(skill_dir)
    listening = report.get("listening_services")
    if not isinstance(listening, list):
        raise SystemExit("Unexpected port_monitor output: listening_services missing or not a list")

    rules, _ = normalize_listeners(listening, include_command=bool(args.include_command))
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(json.dumps(rules, indent=2) + "\n", encoding="utf-8")

    print(json.dumps({"status": "ok", "output": str(out), "rules": len(rules)}, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
