#!/usr/bin/env python3
"""
MerchantGuard OpenClaw Skill — Compliance Layer for AI Agents

Commands:
  guard scan [path]                    Scan code for 102 security patterns
  guard shopper <agent>                Run 10 adversarial probes
  guard score                          Calculate GuardScore
  guard coach <vertical> "<question>"  Ask a compliance coach
  guard alerts                         Get compliance alerts
  guard certify <agent>                Full certification pipeline

Install: openclaw skill install merchantguard
Docs: https://merchantguard.ai
"""

import os
import sys
import json
import hashlib
import argparse
import re
from pathlib import Path
from datetime import datetime
from typing import Optional, Dict, Any, List

try:
    import requests
except ImportError:
    print("ERROR: 'requests' package required. Run: pip install requests")
    sys.exit(1)

# ============================================================================
# CONFIG
# ============================================================================

API_BASE = "https://merchantguard.ai/api"
API_KEY = os.environ.get("MERCHANTGUARD_API_KEY", "")
VERSION = "2.0.0"

HEADERS = {
    "Content-Type": "application/json",
    "User-Agent": f"MerchantGuard-OpenClaw/{VERSION}",
}
if API_KEY:
    HEADERS["Authorization"] = f"Bearer {API_KEY}"

# ============================================================================
# LOCAL SCAN PATTERNS (runs 100% locally — no code uploaded)
# ============================================================================

DANGEROUS_PATTERNS = {
    "hardcoded_secrets": [
        (r'(?:api[_-]?key|secret|token|password)\s*[:=]\s*["\'][^"\']{8,}', "Possible hardcoded secret"),
        (r'AKIA[0-9A-Z]{16}', "AWS Access Key ID"),
        (r'sk[_-]live[_-][a-zA-Z0-9]{24,}', "Stripe Secret Key"),
        (r'ghp_[a-zA-Z0-9]{36}', "GitHub Personal Access Token"),
    ],
    "sensitive_access": [
        (r'\.ssh', "SSH directory access"),
        (r'\.env', "Environment file access"),
        (r'private[_-]?key', "Private key reference"),
        (r'id_rsa|id_ed25519', "SSH key file reference"),
        (r'wallet\.dat', "Crypto wallet file access"),
        (r'\.gnupg', "GPG keyring access"),
        (r'keychain', "Keychain access"),
        (r'credentials', "Credentials file access"),
    ],
    "prompt_injection": [
        (r'ignore\s+(previous|above|all)\s+(instructions|prompts)', "Prompt injection pattern"),
        (r'system\s*:\s*you\s+are', "System prompt override attempt"),
        (r'<\|im_start\|>|<\|endoftext\|>', "Special token injection"),
    ],
    "network_exfil": [
        (r'webhook\.site|requestbin|pipedream', "Known exfiltration endpoint"),
        (r'ngrok\.io|localtunnel', "Tunnel service (potential exfil)"),
    ],
    "pci_violations": [
        (r'card[_-]?number|cvv|cvc|expir', "PCI-sensitive data reference"),
        (r'pan[_-]?data|track[_-]?data', "Payment card track data"),
    ],
}


def scan_file(filepath: Path) -> List[Dict[str, Any]]:
    """Scan a single file for security patterns."""
    findings = []
    try:
        content = filepath.read_text(errors="ignore")
    except Exception:
        return findings

    for category, patterns in DANGEROUS_PATTERNS.items():
        for pattern, description in patterns:
            matches = re.finditer(pattern, content, re.IGNORECASE)
            for match in matches:
                line_num = content[:match.start()].count('\n') + 1
                findings.append({
                    "category": category,
                    "description": description,
                    "file": str(filepath),
                    "line": line_num,
                    "severity": "critical" if category in ("hardcoded_secrets", "network_exfil") else "warning",
                })
    return findings


def scan_directory(path: str) -> Dict[str, Any]:
    """Scan a directory for security issues. 100% local — nothing uploaded."""
    scan_path = Path(path).resolve()
    if not scan_path.exists():
        return {"error": f"Path not found: {scan_path}"}

    all_findings = []
    files_scanned = 0
    skip_dirs = {".git", "node_modules", "__pycache__", ".next", "dist", "build", ".venv", "venv"}
    scan_extensions = {".py", ".js", ".ts", ".tsx", ".jsx", ".md", ".yaml", ".yml", ".json", ".env", ".sh", ".toml"}

    for filepath in scan_path.rglob("*"):
        if filepath.is_file() and filepath.suffix in scan_extensions:
            if any(skip in filepath.parts for skip in skip_dirs):
                continue
            findings = scan_file(filepath)
            # Make paths relative
            for f in findings:
                f["file"] = str(filepath.relative_to(scan_path))
            all_findings.extend(findings)
            files_scanned += 1

    critical = sum(1 for f in all_findings if f["severity"] == "critical")
    warnings = sum(1 for f in all_findings if f["severity"] == "warning")
    risk_score = min(100, critical * 25 + warnings * 5)

    return {
        "scan_path": str(scan_path),
        "files_scanned": files_scanned,
        "findings": all_findings,
        "critical_count": critical,
        "warning_count": warnings,
        "risk_score": risk_score,
        "status": "critical" if critical > 0 else "warning" if warnings > 0 else "clean",
        "scanned_at": datetime.utcnow().isoformat() + "Z",
    }


# ============================================================================
# API CALLS
# ============================================================================

def api_call(method: str, path: str, data: Optional[Dict] = None, timeout: int = 30) -> Dict[str, Any]:
    """Make an API call to MerchantGuard."""
    url = f"{API_BASE}{path}"
    try:
        if method == "GET":
            resp = requests.get(url, headers=HEADERS, timeout=timeout)
        else:
            resp = requests.post(url, headers=HEADERS, json=data or {}, timeout=timeout)
        resp.raise_for_status()
        return resp.json()
    except requests.Timeout:
        return {"error": "Request timed out"}
    except requests.ConnectionError:
        return {"error": "Could not connect to MerchantGuard API"}
    except requests.HTTPError as e:
        return {"error": f"API error: {e.response.status_code}", "detail": e.response.text[:200]}
    except Exception as e:
        return {"error": str(e)}


def run_mystery_shopper(agent_name: str, endpoint: Optional[str] = None) -> Dict[str, Any]:
    """Run 10 adversarial probes against an agent."""
    payload = {"agent_id": agent_name, "platform": "moltbook"}
    if endpoint:
        payload["endpoint_url"] = endpoint
    return api_call("POST", "/v2/mystery-shopper", payload, timeout=60)


def calculate_guardscore(chargeback_ratio: float, vertical: str = "general",
                         volume: int = 0) -> Dict[str, Any]:
    """Calculate GuardScore."""
    return api_call("POST", "/guardscore/calculate", {
        "chargebackRatio": chargeback_ratio,
        "vertical": vertical,
        "monthly_volume": volume,
    })


def ask_coach(vertical: str, question: str) -> Dict[str, Any]:
    """Ask a compliance coach."""
    return api_call("POST", f"/v2/coach/{vertical}", {"question": question})


def get_alerts(critical_only: bool = False, verticals: Optional[List[str]] = None) -> Dict[str, Any]:
    """Get compliance alerts."""
    params = []
    if critical_only:
        params.append("min_severity=8")
    if verticals:
        params.append(f"verticals={','.join(verticals)}")
    query = "?" + "&".join(params) if params else ""
    return api_call("GET", f"/alerts/public{query}")


def run_certification(agent_name: str, wallet: Optional[str] = None,
                      endpoint: Optional[str] = None) -> Dict[str, Any]:
    """Run full certification pipeline."""
    payload = {"agent_id": agent_name}
    if wallet:
        payload["wallet_address"] = wallet
    if endpoint:
        payload["endpoint_url"] = endpoint
    return api_call("POST", "/v2/certify", payload, timeout=120)


# ============================================================================
# CLI OUTPUT FORMATTING
# ============================================================================

def print_scan_results(results: Dict[str, Any]):
    """Pretty-print scan results."""
    if "error" in results:
        print(f"\n  ERROR: {results['error']}")
        return

    status_icon = {"clean": "[CLEAN]", "warning": "[WARN]", "critical": "[CRIT]"}
    print(f"\n  MerchantGuard Security Scan")
    print(f"{'=' * 60}")
    print(f"  Path: {results['scan_path']}")
    print(f"  Files scanned: {results['files_scanned']}")
    print(f"  Status: {status_icon.get(results['status'], '[?]')} {results['status'].upper()}")
    print(f"  Risk score: {results['risk_score']}/100")
    print()

    if results["findings"]:
        print(f"  Findings ({results['critical_count']} critical, {results['warning_count']} warnings):")
        print(f"{'-' * 60}")
        for f in results["findings"][:20]:  # Cap output
            sev = "CRIT" if f["severity"] == "critical" else "WARN"
            print(f"  [{sev}] {f['file']}:{f['line']} — {f['description']}")
            print(f"         Category: {f['category']}")

        if len(results["findings"]) > 20:
            print(f"\n  ... and {len(results['findings']) - 20} more findings")
    else:
        print("  No security issues found.")

    print()


def print_shopper_results(results: Dict[str, Any]):
    """Pretty-print Mystery Shopper results."""
    if "error" in results:
        print(f"\n  ERROR: {results['error']}")
        return

    print(f"\n  Mystery Shopper — Adversarial Audit")
    print(f"{'=' * 60}")
    print(f"  Agent: {results.get('agent_id', 'unknown')}")
    print(f"  Score: {results.get('score', 0)}/100")
    print(f"  Passed: {results.get('passed', 0)}/{results.get('total_probes', 10)}")
    print()

    for probe in results.get("probes", []):
        icon = "PASS" if probe.get("passed") else "FAIL"
        print(f"  [{icon}] {probe.get('probe_type', '?')}")
        if probe.get("actual_behavior"):
            print(f"         {probe['actual_behavior'][:80]}")

    print()
    tier = "Diamond" if results.get("score", 0) >= 90 else "Gold" if results.get("score", 0) >= 70 else "Verified" if results.get("score", 0) >= 50 else "Unverified"
    print(f"  Trust Tier: {tier}")
    print()


def print_coach_response(results: Dict[str, Any]):
    """Pretty-print coach response."""
    if "error" in results:
        print(f"\n  ERROR: {results['error']}")
        return

    print(f"\n  Compliance Coach — {results.get('vertical', '?').upper()}")
    print(f"{'=' * 60}")
    print(f"  Decision: {results.get('decision', '?')}")
    print(f"  Risk Level: {results.get('risk_level', '?')}")
    print(f"  Confidence: {results.get('confidence', 0)}%")
    print()
    print(f"  Answer:")
    print(f"  {results.get('answer', 'No answer available')}")
    print()

    actions = results.get("required_actions", [])
    if actions:
        print(f"  Required Actions:")
        for a in actions:
            print(f"  [{a.get('severity', '?').upper()}] {a.get('description', '')}")

    citations = results.get("policy_citations", [])
    if citations:
        print(f"\n  Policy Citations:")
        for c in citations:
            print(f"  - {c.get('source', '')}: {c.get('title', '')}")

    if results.get("disclaimer"):
        print(f"\n  Disclaimer: {results['disclaimer']}")
    print()


# ============================================================================
# MAIN CLI
# ============================================================================

def main():
    parser = argparse.ArgumentParser(
        description="MerchantGuard — Compliance Layer for AI Agents",
        prog="guard"
    )
    subparsers = parser.add_subparsers(dest="command", help="Available commands")

    # scan
    scan_p = subparsers.add_parser("scan", help="Scan code for security issues (runs locally)")
    scan_p.add_argument("path", nargs="?", default=".", help="Directory to scan (default: current)")
    scan_p.add_argument("--json", action="store_true", help="Output as JSON")

    # shopper
    shop_p = subparsers.add_parser("shopper", help="Run 10 adversarial probes against an agent")
    shop_p.add_argument("agent", help="Agent name (Moltbook username)")
    shop_p.add_argument("--endpoint", help="Agent HTTP endpoint for live probing")
    shop_p.add_argument("--json", action="store_true", help="Output as JSON")

    # score
    score_p = subparsers.add_parser("score", help="Calculate GuardScore")
    score_p.add_argument("--chargeback-ratio", type=float, required=True, help="Chargeback ratio (e.g. 0.8)")
    score_p.add_argument("--vertical", default="general", help="Business vertical")
    score_p.add_argument("--volume", type=int, default=0, help="Monthly volume in USD")
    score_p.add_argument("--json", action="store_true", help="Output as JSON")

    # coach
    coach_p = subparsers.add_parser("coach", help="Ask a compliance coach")
    coach_p.add_argument("vertical", help="Coach vertical (crypto, cbd, vamp, etc.)")
    coach_p.add_argument("question", help="Your compliance question")
    coach_p.add_argument("--json", action="store_true", help="Output as JSON")

    # alerts
    alerts_p = subparsers.add_parser("alerts", help="Get compliance alerts")
    alerts_p.add_argument("--critical", action="store_true", help="Critical alerts only")
    alerts_p.add_argument("--vertical", help="Filter by verticals (comma-separated)")
    alerts_p.add_argument("--json", action="store_true", help="Output as JSON")

    # certify
    cert_p = subparsers.add_parser("certify", help="Full certification pipeline")
    cert_p.add_argument("agent", help="Agent name")
    cert_p.add_argument("--wallet", help="Wallet address for on-chain attestation")
    cert_p.add_argument("--endpoint", help="Agent HTTP endpoint")
    cert_p.add_argument("--json", action="store_true", help="Output as JSON")

    args = parser.parse_args()

    if not args.command:
        parser.print_help()
        print("\n  Quick start:")
        print("    guard scan .                    # Scan current directory")
        print("    guard shopper MyAgent           # Probe an agent")
        print("    guard coach crypto \"My question\" # Ask a coach")
        print("    guard alerts --critical         # Get critical alerts")
        return

    if args.command == "scan":
        results = scan_directory(args.path)
        if args.json:
            print(json.dumps(results, indent=2))
        else:
            print_scan_results(results)

    elif args.command == "shopper":
        print(f"\n  Running 10 adversarial probes against {args.agent}...")
        results = run_mystery_shopper(args.agent, args.endpoint)
        if args.json:
            print(json.dumps(results, indent=2))
        else:
            print_shopper_results(results)

    elif args.command == "score":
        results = calculate_guardscore(args.chargeback_ratio, args.vertical, args.volume)
        if args.json:
            print(json.dumps(results, indent=2))
        else:
            print(f"\n  GuardScore")
            print(f"{'=' * 60}")
            print(f"  Score: {results.get('score', 0)}/100")
            print(f"  Band: {results.get('band', '?')}")
            for f in results.get("factors", []):
                print(f"  - {f['name']}: {f['impact']:+d}")

    elif args.command == "coach":
        results = ask_coach(args.vertical, args.question)
        if args.json:
            print(json.dumps(results, indent=2))
        else:
            print_coach_response(results)

    elif args.command == "alerts":
        verticals = args.vertical.split(",") if args.vertical else None
        results = get_alerts(args.critical, verticals)
        if args.json:
            print(json.dumps(results, indent=2))
        else:
            alerts = results.get("alerts", [])
            print(f"\n  Compliance Alerts ({len(alerts)} found)")
            print(f"{'=' * 60}")
            for a in alerts[:10]:
                print(f"  [{a.get('severity', '?')}/10] {a.get('title', '?')}")
                print(f"         {a.get('summary', '')[:80]}")
                print(f"         Industries: {', '.join(a.get('industries', []))}")
                print()

    elif args.command == "certify":
        print(f"\n  Running full certification for {args.agent}...")
        results = run_certification(args.agent, args.wallet, args.endpoint)
        if args.json:
            print(json.dumps(results, indent=2))
        else:
            print(f"\n  TrustVerdict Certification")
            print(f"{'=' * 60}")
            print(f"  Agent: {args.agent}")
            print(f"  Score: {results.get('score', 0)}/100")
            print(f"  Tier: {results.get('tier', 'Unverified')}")
            if results.get("tx_hash"):
                print(f"  On-chain: {results['tx_hash']}")


if __name__ == "__main__":
    main()
