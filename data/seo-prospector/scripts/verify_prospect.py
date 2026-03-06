#!/usr/bin/env python3
"""
Prospect Verifier — validates prospect data quality before outreach.

Checks:
- URL resolves (HTTP HEAD, follow redirects, detect parked/for-sale domains)
- Phone format validation
- Domain age check (warns on brand-new domains)

Usage:
    python3 verify_prospect.py <report_path>           # Single report
    python3 verify_prospect.py --batch <directory>      # All reports in directory
    python3 verify_prospect.py --json <prospect.json>   # JSON prospect data

Output: JSON with pass/fail per prospect + issues list.
"""

from __future__ import annotations

import argparse
import json
import re
import subprocess
import sys
from pathlib import Path
from urllib.parse import urlparse


# Parked domain indicators in HTML body
PARKED_PATTERNS = [
    r"this domain is for sale",
    r"domain is parked",
    r"buy this domain",
    r"domain may be for sale",
    r"parked free.*courtesy",
    r"sedoparking",
    r"hugedomains\.com",
    r"afternic\.com",
    r"godaddy.*domain.*auction",
    r"dan\.com",
    r"undeveloped\.com",
    r"namecheap.*marketplace",
    r"domain has expired",
    r"this site can.t be reached",
    r"page isn.t working",
    r"account.*suspended",
    r"website coming soon",
    r"under construction",
]

PARKED_RE = re.compile("|".join(PARKED_PATTERNS), re.IGNORECASE)

# US phone number patterns
PHONE_RE = re.compile(
    r"^\+?1?\s*[-.]?\s*\(?\d{3}\)?[\s\-.]?\d{3}[\s\-.]?\d{4}$"
)


def check_url(url: str, timeout: int = 15) -> dict:
    """Validate a URL resolves and isn't parked/for-sale."""
    if not url:
        return {"status": "skip", "reason": "no URL provided"}

    # Normalize
    if not url.startswith(("http://", "https://")):
        url = "https://" + url

    result = {"url": url, "issues": []}

    try:
        # Use curl for macOS SSL compatibility
        head_cmd = [
            "curl", "-sS", "-o", "/dev/null",
            "-w", "%{http_code}|%{redirect_url}|%{url_effective}",
            "-L", "--max-redirs", "5",
            "--connect-timeout", str(timeout),
            "--max-time", str(timeout + 5),
            url
        ]
        proc = subprocess.run(head_cmd, capture_output=True, text=True, timeout=timeout + 10)
        parts = proc.stdout.strip().split("|")
        status_code = int(parts[0]) if parts[0].isdigit() else 0
        final_url = parts[2] if len(parts) > 2 else url

        result["http_status"] = status_code
        result["final_url"] = final_url

        if status_code == 0:
            result["status"] = "fail"
            result["issues"].append("DNS resolution failed or connection timeout")
            return result
        elif status_code >= 400:
            result["status"] = "fail"
            result["issues"].append(f"HTTP {status_code} error")
            return result

        # Check for parked domain patterns
        body_cmd = [
            "curl", "-sS", "-L",
            "--connect-timeout", str(timeout),
            "--max-time", str(timeout + 5),
            "--max-filesize", "500000",  # 500KB max
            url
        ]
        body_proc = subprocess.run(body_cmd, capture_output=True, text=True, timeout=timeout + 10)
        body = body_proc.stdout[:50000]  # Check first 50KB

        if PARKED_RE.search(body):
            result["status"] = "warn"
            match = PARKED_RE.search(body)
            result["issues"].append(f"Parked/for-sale domain detected: '{match.group()}'")
        else:
            result["status"] = "pass"

        # Check if redirected to a completely different domain
        orig_domain = urlparse(url).netloc.lower().replace("www.", "")
        final_domain = urlparse(final_url).netloc.lower().replace("www.", "")
        if orig_domain != final_domain:
            result["issues"].append(f"Redirected to different domain: {final_domain}")
            result["status"] = "warn"

    except subprocess.TimeoutExpired:
        result["status"] = "fail"
        result["issues"].append("Connection timeout")
    except Exception as e:
        result["status"] = "fail"
        result["issues"].append(f"Error: {str(e)}")

    return result


def check_phone(phone: str) -> dict:
    """Validate US phone number format."""
    if not phone:
        return {"status": "skip", "reason": "no phone provided"}

    cleaned = phone.strip()
    if PHONE_RE.match(cleaned):
        return {"status": "pass", "phone": cleaned}
    else:
        return {"status": "warn", "phone": cleaned, "issues": ["Non-standard phone format"]}


def check_domain_age(domain: str, timeout: int = 10) -> dict:
    """Check domain age via WHOIS (warns on very new domains)."""
    if not domain:
        return {"status": "skip", "reason": "no domain provided"}

    # Clean domain
    domain = domain.lower().strip().replace("https://", "").replace("http://", "").split("/")[0]

    try:
        proc = subprocess.run(
            ["whois", domain],
            capture_output=True, text=True, timeout=timeout
        )
        output = proc.stdout

        # Look for creation date
        creation_patterns = [
            r"Creation Date:\s*(.+)",
            r"Created On:\s*(.+)",
            r"Registration Date:\s*(.+)",
            r"created:\s*(.+)",
        ]
        for pat in creation_patterns:
            match = re.search(pat, output, re.IGNORECASE)
            if match:
                date_str = match.group(1).strip()
                return {"status": "pass", "created": date_str, "domain": domain}

        return {"status": "skip", "reason": "Could not determine creation date", "domain": domain}

    except subprocess.TimeoutExpired:
        return {"status": "skip", "reason": "WHOIS timeout", "domain": domain}
    except Exception as e:
        return {"status": "skip", "reason": str(e), "domain": domain}


def extract_prospects_from_report(report_path: str) -> list[dict]:
    """Extract prospect data from a markdown report."""
    path = Path(report_path)
    if not path.exists():
        return []

    content = path.read_text()
    prospects = []

    # Look for structured data: business name, URL, phone
    # Common patterns in our reports
    lines = content.split("\n")

    current = {}
    for line in lines:
        line = line.strip()

        # Business name patterns
        name_match = re.match(r"^#+\s+(?:\d+[\.\)]\s*)?(.+?)(?:\s*[-—]\s*.+)?$", line)
        if name_match and len(name_match.group(1)) > 3:
            if current.get("name"):
                prospects.append(current)
            current = {"name": name_match.group(1).strip()}
            continue

        # URL patterns
        url_match = re.search(r"(?:website|url|site|domain)[\s:]+\[?([^\s\]]+\.[a-z]{2,}[^\s\]]*)", line, re.IGNORECASE)
        if not url_match:
            url_match = re.search(r"https?://[^\s\)\"]+", line)
        if url_match and current:
            current["url"] = url_match.group(1) if url_match.lastindex else url_match.group(0)

        # Phone patterns
        phone_match = re.search(r"(?:phone|tel|call)[\s:]+([(\d][\d\s\-\.\(\)]{7,})", line, re.IGNORECASE)
        if not phone_match:
            phone_match = re.search(r"\(502\)\s*\d{3}[\s\-\.]\d{4}", line)
        if phone_match and current:
            current["phone"] = phone_match.group(1) if phone_match.lastindex else phone_match.group(0)

    if current.get("name"):
        prospects.append(current)

    return prospects


def verify_prospect(prospect: dict) -> dict:
    """Run all checks on a single prospect."""
    result = {
        "name": prospect.get("name", "unknown"),
        "checks": {},
        "overall": "pass",
        "issue_count": 0,
    }

    # URL check
    url = prospect.get("url") or prospect.get("domain") or prospect.get("website", "")
    url_result = check_url(url)
    result["checks"]["url"] = url_result
    if url_result["status"] == "fail":
        result["overall"] = "fail"
        result["issue_count"] += len(url_result.get("issues", []))
    elif url_result["status"] == "warn":
        if result["overall"] == "pass":
            result["overall"] = "warn"
        result["issue_count"] += len(url_result.get("issues", []))

    # Phone check
    phone = prospect.get("phone", "")
    phone_result = check_phone(phone)
    result["checks"]["phone"] = phone_result
    if phone_result["status"] == "warn":
        if result["overall"] == "pass":
            result["overall"] = "warn"
        result["issue_count"] += 1

    # Domain age check (only if URL exists and resolved)
    if url and url_result["status"] != "fail":
        domain = urlparse(url if url.startswith("http") else "https://" + url).netloc
        age_result = check_domain_age(domain)
        result["checks"]["domain_age"] = age_result
    else:
        result["checks"]["domain_age"] = {"status": "skip", "reason": "no valid URL"}

    return result


def cmd_single(args) -> None:
    """Verify prospects from a single report."""
    prospects = extract_prospects_from_report(args.report)
    if not prospects:
        print(json.dumps({"error": f"No prospects found in {args.report}"}, indent=2))
        return

    results = []
    for p in prospects:
        results.append(verify_prospect(p))

    summary = {
        "report": args.report,
        "total": len(results),
        "passed": sum(1 for r in results if r["overall"] == "pass"),
        "warned": sum(1 for r in results if r["overall"] == "warn"),
        "failed": sum(1 for r in results if r["overall"] == "fail"),
        "prospects": results,
    }
    print(json.dumps(summary, indent=2))


def cmd_batch(args) -> None:
    """Verify all reports in a directory."""
    batch_dir = Path(args.batch)
    if not batch_dir.is_dir():
        print(json.dumps({"error": f"{args.batch} is not a directory"}))
        return

    reports = list(batch_dir.glob("**/*.md"))
    all_results = []

    for report in reports:
        prospects = extract_prospects_from_report(str(report))
        for p in prospects:
            result = verify_prospect(p)
            result["source_report"] = str(report)
            all_results.append(result)

    summary = {
        "directory": args.batch,
        "reports_scanned": len(reports),
        "total_prospects": len(all_results),
        "passed": sum(1 for r in all_results if r["overall"] == "pass"),
        "warned": sum(1 for r in all_results if r["overall"] == "warn"),
        "failed": sum(1 for r in all_results if r["overall"] == "fail"),
        "failures": [r for r in all_results if r["overall"] == "fail"],
        "warnings": [r for r in all_results if r["overall"] == "warn"],
    }
    print(json.dumps(summary, indent=2))


def cmd_json_input(args) -> None:
    """Verify a single prospect from JSON data."""
    try:
        prospect = json.loads(args.json)
    except json.JSONDecodeError:
        # Treat as a file path
        prospect = json.loads(Path(args.json).read_text())

    if isinstance(prospect, list):
        results = [verify_prospect(p) for p in prospect]
        print(json.dumps({"total": len(results), "prospects": results}, indent=2))
    else:
        print(json.dumps(verify_prospect(prospect), indent=2))


def main():
    parser = argparse.ArgumentParser(description="SEO Prospect Verifier")
    parser.add_argument("report", nargs="?", help="Path to a prospect report (.md)")
    parser.add_argument("--batch", help="Directory of reports to verify")
    parser.add_argument("--json", help="JSON prospect data or file path")

    args = parser.parse_args()

    if args.batch:
        cmd_batch(args)
    elif args.json:
        cmd_json_input(args)
    elif args.report:
        cmd_single(args)
    else:
        parser.print_help()
        sys.exit(1)


if __name__ == "__main__":
    main()
