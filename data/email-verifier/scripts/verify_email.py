#!/usr/bin/env python3
"""
Email deliverability verifier via SMTP.
Checks MX records and performs RCPT TO verification without sending mail.

Usage:
    python3 verify_email.py email1@example.com email2@example.com ...
    echo "email@example.com" | python3 verify_email.py --stdin
    python3 verify_email.py --csv input.csv --email-column "Contact Email"

Output: JSON array of results to stdout.

Dependencies: dnspython (pip3 install dnspython)
"""

import smtplib
import socket
import json
import sys
import csv
import io
import argparse
import time
from collections import defaultdict

try:
    import dns.resolver
except ImportError:
    print("Error: dnspython required. Install with: pip3 install dnspython", file=sys.stderr)
    sys.exit(1)


def get_mx_host(domain):
    """Resolve the highest-priority MX record for a domain."""
    try:
        mx_records = dns.resolver.resolve(domain, 'MX')
        return str(sorted(mx_records, key=lambda x: x.preference)[0].exchange).rstrip('.')
    except dns.resolver.NXDOMAIN:
        return None
    except dns.resolver.NoAnswer:
        return None
    except Exception:
        return None


def verify_email(email, helo_domain="verify.local", timeout=10):
    """
    Verify an email address via SMTP RCPT TO.
    
    Returns dict with:
        email, domain, mx_host, smtp_code, smtp_response, deliverable, error
    
    deliverable values:
        "yes"     - Server accepted the recipient (250)
        "no"      - Server rejected the recipient (550)
        "catch-all" - Server accepts everything (if detected)
        "unknown" - Could not determine (timeout, block, greylisting, etc.)
    """
    domain = email.split('@')[-1].lower()
    result = {"email": email, "domain": domain}

    # Step 1: MX lookup
    mx_host = get_mx_host(domain)
    if not mx_host:
        result["mx_host"] = None
        result["deliverable"] = "unknown"
        result["error"] = "No MX record found"
        return result
    result["mx_host"] = mx_host

    # Step 2: SMTP verification
    try:
        smtp = smtplib.SMTP(timeout=timeout)
        smtp.connect(mx_host, 25)
        smtp.helo(helo_domain)
        smtp.mail(f"verify@{helo_domain}")
        code, msg = smtp.rcpt(email)
        result["smtp_code"] = code
        result["smtp_response"] = msg.decode('utf-8', errors='replace')

        if code == 250:
            # Check for catch-all by testing a random address
            import random, string
            fake = ''.join(random.choices(string.ascii_lowercase, k=12)) + f"@{domain}"
            fake_code, _ = smtp.rcpt(fake)
            if fake_code == 250:
                result["deliverable"] = "catch-all"
                result["note"] = "Server accepts all addresses; cannot confirm inbox exists"
            else:
                result["deliverable"] = "yes"
        elif code in (550, 551, 552, 553, 554):
            result["deliverable"] = "no"
        elif code == 450 or code == 451:
            result["deliverable"] = "unknown"
            result["note"] = "Greylisted or temporarily unavailable"
        else:
            result["deliverable"] = "unknown"

        smtp.quit()

    except smtplib.SMTPServerDisconnected:
        result["deliverable"] = "unknown"
        result["error"] = "Server disconnected (may block SMTP verification)"
    except socket.timeout:
        result["deliverable"] = "unknown"
        result["error"] = "Connection timed out"
    except ConnectionRefusedError:
        result["deliverable"] = "unknown"
        result["error"] = "Connection refused on port 25"
    except Exception as e:
        result["deliverable"] = "unknown"
        result["error"] = str(e)

    return result


def main():
    parser = argparse.ArgumentParser(description="Verify email deliverability via SMTP")
    parser.add_argument("emails", nargs="*", help="Email addresses to verify")
    parser.add_argument("--stdin", action="store_true", help="Read emails from stdin (one per line)")
    parser.add_argument("--csv", type=str, help="Read emails from a CSV file")
    parser.add_argument("--email-column", type=str, default="email", help="CSV column name containing emails")
    parser.add_argument("--helo", type=str, default="verify.local", help="HELO domain (default: verify.local)")
    parser.add_argument("--timeout", type=int, default=10, help="SMTP timeout in seconds (default: 10)")
    args = parser.parse_args()

    emails = list(args.emails)

    if args.stdin:
        for line in sys.stdin:
            line = line.strip()
            if line and '@' in line:
                emails.append(line)

    if args.csv:
        with open(args.csv, 'r') as f:
            reader = csv.DictReader(f)
            col = args.email_column
            for row in reader:
                val = row.get(col, "").strip()
                if val and '@' in val:
                    emails.append(val)

    parser.add_argument("--delay", type=float, default=1.0,
                        help="Seconds between checks to same domain (default: 1.0)")
    parser.add_argument("--max-per-domain", type=int, default=20,
                        help="Max checks per domain before pausing (default: 20)")
    parser.add_argument("--burst-pause", type=float, default=30.0,
                        help="Seconds to pause after hitting max-per-domain (default: 30)")
    args = parser.parse_args()

    if not emails:
        print("No emails provided. Use positional args, --stdin, or --csv.", file=sys.stderr)
        sys.exit(1)

    # Deduplicate while preserving order
    seen = set()
    unique = []
    for e in emails:
        lower = e.lower()
        if lower not in seen:
            seen.add(lower)
            unique.append(e)

    results = []
    domain_counts = defaultdict(int)

    for i, email in enumerate(unique):
        domain = email.split('@')[-1].lower()

        # Rate limiting: pause between checks
        if i > 0:
            time.sleep(args.delay)

        # Rate limiting: burst protection per domain
        if domain_counts[domain] >= args.max_per_domain:
            print(f"Rate limit: pausing {args.burst_pause}s after {args.max_per_domain} "
                  f"checks to {domain}...", file=sys.stderr)
            time.sleep(args.burst_pause)
            domain_counts[domain] = 0

        print(f"Verifying {email}... [{i+1}/{len(unique)}]", file=sys.stderr)
        r = verify_email(email, helo_domain=args.helo, timeout=args.timeout)
        results.append(r)
        domain_counts[domain] += 1

    print(json.dumps(results, indent=2))


if __name__ == "__main__":
    main()
