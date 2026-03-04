#!/usr/bin/env python3
import argparse
import json
import re
import shutil
import subprocess
import sys
from pathlib import Path
from typing import Dict, List, Optional, Tuple


DEFAULT_ALLOWLIST = Path.home() / ".openclaw" / "security" / "egress_allowlist.json"


def parse_args() -> argparse.Namespace:
    p = argparse.ArgumentParser(description="Outbound TCP connection monitor against allowlist")
    p.add_argument("--allowlist", default=str(DEFAULT_ALLOWLIST), help="Allowlist JSON file")
    p.add_argument("--json", action="store_true", help="JSON output")
    return p.parse_args()


def run_lsof() -> str:
    cmd = ["lsof", "-nP", "-iTCP", "-sTCP:ESTABLISHED"]
    proc = subprocess.run(cmd, capture_output=True, text=True)
    if proc.returncode != 0:
        raise RuntimeError(proc.stderr.strip() or "Failed to run lsof")
    return proc.stdout


def run_ss() -> str:
    cmd = ["ss", "-tnp", "state", "established"]
    proc = subprocess.run(cmd, capture_output=True, text=True)
    if proc.returncode != 0:
        raise RuntimeError(proc.stderr.strip() or "Failed to run ss")
    return proc.stdout


def run_netstat_windows() -> str:
    cmd = ["netstat", "-ano", "-p", "tcp"]
    proc = subprocess.run(cmd, capture_output=True, text=True)
    if proc.returncode != 0:
        raise RuntimeError(proc.stderr.strip() or "Failed to run netstat")
    return proc.stdout


def _parse_host_port(s: str) -> Tuple[Optional[str], Optional[int]]:
    s = s.strip()
    # lsof: 1.2.3.4:55555->9.9.9.9:443 or [::1]:555->[...] etc.
    if "->" in s:
        s = s.split("->", 1)[1]
    s = s.replace("(ESTABLISHED)", "").strip()
    if s.startswith("["):
        m = re.search(r"\[(.*?)\]:(\d+)$", s)
    else:
        m = re.search(r"(.+):(\d+)$", s)
    if not m:
        return None, None
    return m.group(1), int(m.group(2))


def parse_lsof(text: str) -> List[Dict[str, object]]:
    lines = [ln for ln in text.splitlines() if ln.strip()]
    if len(lines) <= 1:
        return []
    out: List[Dict[str, object]] = []
    seen = set()
    for ln in lines[1:]:
        parts = ln.split()
        if len(parts) < 9:
            continue
        command = parts[0]
        pid = parts[1]
        user = parts[2]
        name = parts[-1]
        rhost, rport = _parse_host_port(name)
        if rport is None:
            continue
        entry = {
            "command": command,
            "pid": int(pid) if pid.isdigit() else pid,
            "user": user,
            "remote_host": rhost,
            "remote_port": rport,
            "protocol": "tcp",
        }
        key = (entry["command"], entry["pid"], entry["remote_host"], entry["remote_port"])
        if key in seen:
            continue
        seen.add(key)
        out.append(entry)
    return out


def parse_ss(text: str) -> List[Dict[str, object]]:
    out: List[Dict[str, object]] = []
    seen = set()
    for ln in text.splitlines():
        if not ln.strip() or ln.startswith("State"):
            continue
        # ESTAB 0 0 192.168.0.10:49820 1.2.3.4:443 users:(("proc",pid=123,fd=...))
        parts = ln.split()
        if len(parts) < 5:
            continue
        remote = parts[4]
        rhost, rport = _parse_host_port(remote)
        if rport is None:
            continue
        m = re.search(r'users:\\(\\(\"([^\"]+)\",pid=(\\d+)', ln)
        command = m.group(1) if m else "unknown"
        pid = int(m.group(2)) if m else "unknown"
        entry = {
            "command": command,
            "pid": pid,
            "user": None,
            "remote_host": rhost,
            "remote_port": rport,
            "protocol": "tcp",
        }
        key = (entry["command"], entry["pid"], entry["remote_host"], entry["remote_port"])
        if key in seen:
            continue
        seen.add(key)
        out.append(entry)
    return out


def parse_netstat_windows(text: str) -> List[Dict[str, object]]:
    out: List[Dict[str, object]] = []
    seen = set()
    for ln in text.splitlines():
        if not ln.strip().startswith("TCP"):
            continue
        parts = ln.split()
        if len(parts) < 5:
            continue
        remote = parts[2]
        state = parts[3]
        pid = parts[4]
        if state.upper() != "ESTABLISHED":
            continue
        rhost, rport = _parse_host_port(remote)
        if rport is None:
            continue
        entry = {
            "command": "unknown",
            "pid": int(pid) if pid.isdigit() else pid,
            "user": None,
            "remote_host": rhost,
            "remote_port": rport,
            "protocol": "tcp",
        }
        key = (entry["command"], entry["pid"], entry["remote_host"], entry["remote_port"])
        if key in seen:
            continue
        seen.add(key)
        out.append(entry)
    return out


def collect_connections() -> Tuple[List[Dict[str, object]], str]:
    if shutil.which("lsof"):
        return parse_lsof(run_lsof()), "lsof"
    if sys.platform.startswith("linux") and shutil.which("ss"):
        return parse_ss(run_ss()), "ss"
    if sys.platform.startswith("win") and shutil.which("netstat"):
        return parse_netstat_windows(run_netstat_windows()), "netstat"
    raise RuntimeError("No supported connection tool found (lsof/ss/netstat)")


def load_allowlist(path: Path) -> List[Dict[str, object]]:
    if not path.exists():
        return []
    raw = json.loads(path.read_text(encoding="utf-8"))
    return raw if isinstance(raw, list) else []


def is_allowed(conn: Dict[str, object], rules: List[Dict[str, object]]) -> bool:
    host = str(conn.get("remote_host") or "")
    port = int(conn.get("remote_port") or 0)
    proto = str(conn.get("protocol") or "tcp").lower()
    cmd = str(conn.get("command") or "")
    for rule in rules:
        if not isinstance(rule, dict):
            continue
        if str(rule.get("protocol") or "tcp").lower() != proto:
            continue
        if "port" in rule and int(rule.get("port") or 0) != port:
            continue
        if "command" in rule and str(rule.get("command") or "").lower() != cmd.lower():
            continue
        host_re = rule.get("host_regex")
        if host_re:
            try:
                if not re.search(str(host_re), host):
                    continue
            except re.error:
                continue
        else:
            host_exact = rule.get("host")
            if host_exact and str(host_exact) != host:
                continue
        return True
    return False


def main() -> int:
    args = parse_args()
    allow_path = Path(args.allowlist).expanduser()
    try:
        conns, tool = collect_connections()
        rules = load_allowlist(allow_path)
        findings = []
        for c in conns:
            if not is_allowed(c, rules):
                findings.append(
                    {
                        "type": "unapproved-egress",
                        "severity": "medium",
                        "remote_host": c.get("remote_host"),
                        "remote_port": c.get("remote_port"),
                        "command": c.get("command"),
                        "recommendation": "Add to egress allowlist with justification or terminate the connection.",
                    }
                )
        report = {
            "status": "ok",
            "allowlist_file": str(allow_path),
            "allowlist_rules_count": len(rules),
            "tool": tool,
            "connections": conns,
            "findings": findings,
        }
    except Exception as exc:
        report = {"status": "error", "error": str(exc)}

    if args.json:
        print(json.dumps(report, indent=2))
    else:
        print(f"Egress connections: {len(report.get('connections', []))}")
        print(f"Findings: {len(report.get('findings', []))}")
    return 0 if report.get("status") == "ok" else 1


if __name__ == "__main__":
    raise SystemExit(main())

