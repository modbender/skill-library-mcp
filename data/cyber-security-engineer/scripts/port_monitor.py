#!/usr/bin/env python3
import argparse
import json
import re
import shutil
import subprocess
import sys
from pathlib import Path
from typing import Dict, List, Optional, Tuple


INSECURE_PORT_RECOMMENDATIONS = {
    20: "Use SFTP (22) or FTPS (990) instead of FTP data.",
    21: "Use SFTP (22) or FTPS (990) instead of FTP control.",
    23: "Use SSH (22) instead of Telnet.",
    69: "Use HTTPS-based transfer APIs instead of TFTP.",
    80: "Use HTTPS (443) instead of HTTP.",
    110: "Use POP3S (995) instead of POP3.",
    143: "Use IMAPS (993) instead of IMAP.",
    389: "Use LDAPS (636) instead of LDAP.",
    512: "Disable r-commands and use SSH (22).",
    513: "Disable r-commands and use SSH (22).",
    514: "Use TLS-secured syslog transport.",
}

DEFAULT_APPROVED_PATH = Path.home() / ".openclaw" / "security" / "approved_ports.json"


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="OpenClaw port monitor and risk recommender")
    parser.add_argument(
        "--approved-file",
        default=str(DEFAULT_APPROVED_PATH),
        help="JSON file of approved listening ports/services",
    )
    parser.add_argument(
        "--json",
        action="store_true",
        help="Print JSON output only",
    )
    return parser.parse_args()


def run_lsof() -> str:
    cmd = ["lsof", "-nP", "-iTCP", "-sTCP:LISTEN"]
    proc = subprocess.run(cmd, capture_output=True, text=True)
    if proc.returncode != 0:
        raise RuntimeError(proc.stderr.strip() or "Failed to run lsof")
    return proc.stdout


def run_ss() -> str:
    cmd = ["ss", "-ltnp"]
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


def parse_name(name: str) -> Tuple[Optional[str], Optional[int]]:
    name = name.replace("(LISTEN)", "").strip()
    # *:22, 127.0.0.1:631, [::1]:8080
    if name.startswith("["):
        match = re.search(r"\[(.*?)\]:(\d+)$", name)
    else:
        match = re.search(r"(.+):(\d+)$", name)
    if not match:
        return None, None
    host = match.group(1)
    port = int(match.group(2))
    return host, port


def parse_lsof_output(text: str) -> List[Dict[str, object]]:
    lines = [line for line in text.splitlines() if line.strip()]
    if len(lines) <= 1:
        return []
    entries: List[Dict[str, object]] = []
    seen = set()
    for line in lines[1:]:
        parts = line.split()
        if len(parts) < 9:
            continue
        command = parts[0]
        pid = parts[1]
        user = parts[2]
        name = parts[-2] if parts[-1] == "(LISTEN)" else parts[-1]
        host, port = parse_name(name)
        if port is None:
            continue
        entry = {
            "command": command,
            "pid": int(pid) if pid.isdigit() else pid,
            "user": user,
            "host": host,
            "port": port,
            "protocol": "tcp",
        }
        dedupe_key = (entry["command"], entry["pid"], entry["host"], entry["port"], entry["protocol"])
        if dedupe_key in seen:
            continue
        seen.add(dedupe_key)
        entries.append(entry)
    return entries


def parse_ss_output(text: str) -> List[Dict[str, object]]:
    lines = [line for line in text.splitlines() if line.strip()]
    entries: List[Dict[str, object]] = []
    seen = set()
    for line in lines[1:]:
        if "LISTEN" not in line:
            continue
        parts = line.split()
        if len(parts) < 5:
            continue
        local = parts[3]
        host, port = parse_name(local)
        if port is None:
            continue
        cmd_match = re.search(r'users:\(\("([^"]+)",pid=(\d+)', line)
        command = cmd_match.group(1) if cmd_match else "unknown"
        pid = int(cmd_match.group(2)) if cmd_match else "unknown"
        entry = {
            "command": command,
            "pid": pid,
            "user": None,
            "host": host,
            "port": port,
            "protocol": "tcp",
        }
        dedupe_key = (entry["command"], entry["pid"], entry["host"], entry["port"], entry["protocol"])
        if dedupe_key in seen:
            continue
        seen.add(dedupe_key)
        entries.append(entry)
    return entries


def parse_netstat_windows_output(text: str) -> List[Dict[str, object]]:
    entries: List[Dict[str, object]] = []
    seen = set()
    for line in text.splitlines():
        if not line.strip().startswith("TCP"):
            continue
        parts = line.split()
        if len(parts) < 5:
            continue
        local = parts[1]
        state = parts[3]
        pid = parts[4]
        if state.upper() != "LISTENING":
            continue
        host, port = parse_name(local)
        if port is None:
            continue
        entry = {
            "command": "unknown",
            "pid": int(pid) if pid.isdigit() else pid,
            "user": None,
            "host": host,
            "port": port,
            "protocol": "tcp",
        }
        dedupe_key = (entry["command"], entry["pid"], entry["host"], entry["port"], entry["protocol"])
        if dedupe_key in seen:
            continue
        seen.add(dedupe_key)
        entries.append(entry)
    return entries


def collect_entries() -> Tuple[List[Dict[str, object]], str]:
    if shutil.which("lsof"):
        return parse_lsof_output(run_lsof()), "lsof"
    if sys.platform.startswith("linux") and shutil.which("ss"):
        return parse_ss_output(run_ss()), "ss"
    if sys.platform.startswith("win") and shutil.which("netstat"):
        return parse_netstat_windows_output(run_netstat_windows()), "netstat"
    raise RuntimeError("No supported port listing tool found (lsof/ss/netstat)")


def load_approved_ports(path: Path) -> List[Dict[str, object]]:
    if not path.exists():
        return []
    with path.open("r", encoding="utf-8") as f:
        data = json.load(f)
    if not isinstance(data, list):
        raise ValueError("Approved ports file must be a JSON array.")
    normalized: List[Dict[str, object]] = []
    for item in data:
        if not isinstance(item, dict):
            continue
        if "port" not in item:
            continue
        normalized.append(item)
    return normalized


def is_approved(entry: Dict[str, object], approved: List[Dict[str, object]]) -> bool:
    for rule in approved:
        if int(rule.get("port")) != int(entry["port"]):
            continue
        rule_proto = str(rule.get("protocol", "tcp")).lower()
        if rule_proto != str(entry["protocol"]).lower():
            continue
        rule_cmd = rule.get("command")
        if rule_cmd and str(rule_cmd).lower() != str(entry["command"]).lower():
            continue
        return True
    return False


def build_findings(entries: List[Dict[str, object]], approved: List[Dict[str, object]]) -> List[Dict[str, object]]:
    findings: List[Dict[str, object]] = []
    for entry in entries:
        port = int(entry["port"])
        host = str(entry.get("host") or "")

        if not is_approved(entry, approved):
            findings.append(
                {
                    "severity": "medium",
                    "type": "unapproved-port",
                    "port": port,
                    "command": entry["command"],
                    "message": "Listening port is not in approved baseline.",
                    "recommendation": "Approve it with business justification or close the service.",
                }
            )

        if port in INSECURE_PORT_RECOMMENDATIONS:
            findings.append(
                {
                    "severity": "high",
                    "type": "insecure-port",
                    "port": port,
                    "command": entry["command"],
                    "message": "Insecure protocol/port detected.",
                    "recommendation": INSECURE_PORT_RECOMMENDATIONS[port],
                }
            )

        if host in ("*", "0.0.0.0", "::"):
            findings.append(
                {
                    "severity": "medium",
                    "type": "public-bind",
                    "port": port,
                    "command": entry["command"],
                    "message": "Service listens on all interfaces.",
                    "recommendation": "Bind to localhost or a restricted interface unless external exposure is required.",
                }
            )
    return findings


def output_text(report: Dict[str, object]) -> None:
    print("Port Monitoring Report")
    print(f"Listening services: {len(report['listening_services'])}")
    print(f"Findings: {len(report['findings'])}")
    if report["findings"]:
        print("")
        for finding in report["findings"]:
            print(
                f"- [{finding['severity'].upper()}] {finding['type']} "
                f"port {finding['port']} ({finding['command']}): {finding['recommendation']}"
            )


def main() -> int:
    args = parse_args()
    approved_path = Path(args.approved_file).expanduser()
    try:
        entries, tool_used = collect_entries()
        approved = load_approved_ports(approved_path)
        findings = build_findings(entries, approved)
    except Exception as exc:
        print(json.dumps({"status": "error", "error": str(exc)}))
        return 1

    report = {
        "status": "ok",
        "approved_file": str(approved_path),
        "approved_rules_count": len(approved),
        "tool": tool_used,
        "listening_services": entries,
        "findings": findings,
    }

    if args.json:
        print(json.dumps(report, indent=2))
    else:
        output_text(report)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
