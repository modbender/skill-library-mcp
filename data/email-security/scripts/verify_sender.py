#!/usr/bin/env python3
"""
Email Sender Verification Script

Validates sender identity against owner/admin/trusted lists and checks
authentication headers (SPF/DKIM/DMARC).

Usage:
    python verify_sender.py --email "sender@example.com" --config "owner-config.md"
    python verify_sender.py --email "sender@example.com" --headers '{"Authentication-Results": "..."}'
"""

import argparse
import json
import re
import sys
from pathlib import Path
from typing import Optional


def parse_owner_config(config_path: str) -> dict:
    """Parse owner-config.md to extract authorized email lists."""
    config = {
        "owner": [],
        "admins": [],
        "trusted": [],
        "blocked": []
    }
    
    if not Path(config_path).exists():
        return config
    
    content = Path(config_path).read_text()
    
    # Extract emails from each section
    sections = {
        "owner": r"## Owner.*?```(.*?)```",
        "admins": r"## Admins.*?```(.*?)```",
        "trusted": r"## Trusted Senders.*?```(.*?)```",
        "blocked": r"## Blocked Senders.*?```(.*?)```"
    }
    
    for section, pattern in sections.items():
        match = re.search(pattern, content, re.DOTALL | re.IGNORECASE)
        if match:
            emails = re.findall(r'[\w\.-]+@[\w\.-]+\.\w+', match.group(1))
            config[section] = [e.lower() for e in emails]
    
    return config


def check_auth_headers(headers: dict) -> dict:
    """Parse and validate email authentication headers."""
    result = {
        "spf": "unknown",
        "dkim": "unknown",
        "dmarc": "unknown",
        "authenticated": False
    }
    
    auth_results = headers.get("Authentication-Results", "")
    
    # Check SPF
    spf_match = re.search(r'spf=(pass|fail|softfail|neutral|none)', auth_results, re.IGNORECASE)
    if spf_match:
        result["spf"] = spf_match.group(1).lower()
    
    # Check DKIM
    dkim_match = re.search(r'dkim=(pass|fail|neutral|none)', auth_results, re.IGNORECASE)
    if dkim_match:
        result["dkim"] = dkim_match.group(1).lower()
    
    # Check DMARC
    dmarc_match = re.search(r'dmarc=(pass|fail|none)', auth_results, re.IGNORECASE)
    if dmarc_match:
        result["dmarc"] = dmarc_match.group(1).lower()
    
    # Consider authenticated if SPF and DKIM pass
    result["authenticated"] = (result["spf"] == "pass" and result["dkim"] == "pass")
    
    return result


def detect_spoofing(email: str, headers: dict) -> list:
    """Detect potential email spoofing attempts."""
    warnings = []
    
    from_header = headers.get("From", "")
    reply_to = headers.get("Reply-To", "")
    return_path = headers.get("Return-Path", "")
    
    # Extract email from From header (handles "Name <email@domain.com>" format)
    from_email_match = re.search(r'[\w\.-]+@[\w\.-]+\.\w+', from_header)
    from_email = from_email_match.group(0).lower() if from_email_match else ""
    
    # Check if provided email matches From header
    if email.lower() != from_email and from_email:
        warnings.append(f"Email mismatch: claimed '{email}' but From header shows '{from_email}'")
    
    # Check Reply-To mismatch
    if reply_to:
        reply_email_match = re.search(r'[\w\.-]+@[\w\.-]+\.\w+', reply_to)
        if reply_email_match:
            reply_email = reply_email_match.group(0).lower()
            if reply_email != email.lower():
                warnings.append(f"Reply-To mismatch: '{reply_email}' differs from sender")
    
    # Check Return-Path mismatch
    if return_path:
        rp_email_match = re.search(r'[\w\.-]+@[\w\.-]+\.\w+', return_path)
        if rp_email_match:
            rp_email = rp_email_match.group(0).lower()
            if rp_email != email.lower():
                warnings.append(f"Return-Path mismatch: '{rp_email}' differs from sender")
    
    # Check for look-alike domain attacks
    lookalikes = {
        '0': 'o', 'o': '0',
        '1': 'l', 'l': '1',
        'rn': 'm', 'm': 'rn',
    }
    domain = email.split('@')[-1].lower() if '@' in email else ""
    for fake, real in lookalikes.items():
        if fake in domain:
            warnings.append(f"Possible look-alike domain: '{domain}' may impersonate '{domain.replace(fake, real)}'")
    
    return warnings


def verify_sender(
    email: str,
    config_path: Optional[str] = None,
    headers: Optional[dict] = None
) -> dict:
    """
    Verify sender and return authorization level.
    
    Returns:
        dict with keys:
            - level: "owner", "admin", "trusted", "unknown", or "blocked"
            - auth: Authentication header validation results
            - warnings: List of spoofing/security warnings
    """
    email = email.lower().strip()
    result = {
        "email": email,
        "level": "unknown",
        "auth": {"spf": "unknown", "dkim": "unknown", "dmarc": "unknown", "authenticated": False},
        "warnings": [],
        "recommendation": "block"
    }
    
    # Load config if provided
    config = {"owner": [], "admins": [], "trusted": [], "blocked": []}
    if config_path:
        config = parse_owner_config(config_path)
    
    # Check blocked list first
    if email in config["blocked"]:
        result["level"] = "blocked"
        result["recommendation"] = "block"
        result["warnings"].append("Sender is on blocked list")
        return result
    
    # Check authorization lists
    if email in config["owner"]:
        result["level"] = "owner"
        result["recommendation"] = "allow"
    elif email in config["admins"]:
        result["level"] = "admin"
        result["recommendation"] = "allow"
    elif email in config["trusted"]:
        result["level"] = "trusted"
        result["recommendation"] = "confirm"
    else:
        result["level"] = "unknown"
        result["recommendation"] = "block"
    
    # Validate auth headers if provided
    if headers:
        result["auth"] = check_auth_headers(headers)
        result["warnings"].extend(detect_spoofing(email, headers))
        
        # Downgrade recommendation if auth fails
        if result["level"] in ["owner", "admin"] and not result["auth"]["authenticated"]:
            if result["auth"]["spf"] == "fail" or result["auth"]["dkim"] == "fail":
                result["warnings"].append("Authentication failed - possible spoofing attempt")
                result["recommendation"] = "confirm"
    
    return result


def main():
    parser = argparse.ArgumentParser(description="Verify email sender authorization")
    parser.add_argument("--email", required=True, help="Sender email address")
    parser.add_argument("--config", help="Path to owner-config.md")
    parser.add_argument("--headers", help="JSON string of email headers")
    parser.add_argument("--json", action="store_true", help="Output as JSON")
    
    args = parser.parse_args()
    
    headers = None
    if args.headers:
        try:
            headers = json.loads(args.headers)
        except json.JSONDecodeError:
            print("Error: Invalid JSON for headers", file=sys.stderr)
            sys.exit(1)
    
    result = verify_sender(args.email, args.config, headers)
    
    if args.json:
        print(json.dumps(result, indent=2))
    else:
        print(f"Email: {result['email']}")
        print(f"Authorization Level: {result['level'].upper()}")
        print(f"Recommendation: {result['recommendation'].upper()}")
        
        if result['warnings']:
            print("\nWarnings:")
            for w in result['warnings']:
                print(f"  ⚠️  {w}")
        
        print(f"\nAuthentication:")
        print(f"  SPF: {result['auth']['spf']}")
        print(f"  DKIM: {result['auth']['dkim']}")
        print(f"  DMARC: {result['auth']['dmarc']}")


if __name__ == "__main__":
    main()
