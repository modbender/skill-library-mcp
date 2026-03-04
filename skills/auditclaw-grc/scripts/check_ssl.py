#!/usr/bin/env python3
"""SSL/TLS certificate checker.

Checks certificate validity, expiry, chain, protocol, and cipher.
Returns structured results with a grade (A-F) and warnings.

Usage:
    python3 check_ssl.py --domain <domain> [--port 443] [--format json|text]

Exit codes:
    0 = success (cert checked)
    1 = connection error
    2 = certificate error
"""

import argparse
import json
import socket
import ssl
import sys
from datetime import datetime, timezone


def check_ssl(domain, port=443):
    """Check SSL/TLS certificate for a domain."""
    context = ssl.create_default_context()

    try:
        with socket.create_connection((domain, port), timeout=15) as sock:
            with context.wrap_socket(sock, server_hostname=domain) as ssock:
                cert = ssock.getpeercert()
                cipher = ssock.cipher()
                protocol = ssock.version()

        return parse_cert(domain, cert, cipher, protocol), None

    except ssl.SSLCertVerificationError as e:
        # Try again without verification to get cert details
        context_no_verify = ssl.create_default_context()
        context_no_verify.check_hostname = False
        context_no_verify.verify_mode = ssl.CERT_NONE

        try:
            with socket.create_connection((domain, port), timeout=15) as sock:
                with context_no_verify.wrap_socket(sock, server_hostname=domain) as ssock:
                    cert = ssock.getpeercert(binary_form=True)
                    cipher = ssock.cipher()
                    protocol = ssock.version()

            # Parse basic info from the error
            return {
                "status": "error",
                "domain": domain,
                "valid": False,
                "chain_valid": False,
                "error": str(e),
                "grade": "F",
                "warnings": [f"Certificate verification failed: {e}"],
                "protocol": protocol,
                "cipher": cipher[0] if cipher else "unknown",
                "checked_at": datetime.now(timezone.utc).isoformat()
            }, None

        except Exception:
            return None, f"SSL connection failed: {e}"

    except socket.timeout:
        return None, "Connection timed out"
    except ConnectionRefusedError:
        return None, f"Connection refused on {domain}:{port}"
    except socket.gaierror:
        return None, f"DNS resolution failed for {domain}"
    except Exception as e:
        return None, f"Connection error: {e}"


def parse_cert(domain, cert, cipher, protocol):
    """Parse certificate details into structured result."""
    # Extract dates
    not_before = datetime.strptime(cert["notBefore"], "%b %d %H:%M:%S %Y %Z")
    not_after = datetime.strptime(cert["notAfter"], "%b %d %H:%M:%S %Y %Z")
    now = datetime.now(timezone.utc).replace(tzinfo=None)
    days_until_expiry = (not_after - now).days

    # Extract SAN
    san = []
    for entry_type, value in cert.get("subjectAltName", []):
        if entry_type == "DNS":
            san.append(value)

    # Extract issuer
    issuer_parts = []
    for rdn in cert.get("issuer", []):
        for attr_type, attr_value in rdn:
            if attr_type == "organizationName":
                issuer_parts.append(attr_value)
            elif attr_type == "commonName":
                issuer_parts.append(attr_value)
    issuer = " - ".join(issuer_parts) if issuer_parts else "Unknown"

    # Extract subject CN
    subject = "Unknown"
    for rdn in cert.get("subject", []):
        for attr_type, attr_value in rdn:
            if attr_type == "commonName":
                subject = attr_value

    # Determine validity
    is_valid = now >= not_before and now <= not_after
    is_expired = now > not_after

    # Warnings
    warnings = []
    if is_expired:
        warnings.append(f"Certificate expired {abs(days_until_expiry)} days ago")
    elif days_until_expiry <= 7:
        warnings.append(f"Certificate expires in {days_until_expiry} days — URGENT")
    elif days_until_expiry <= 14:
        warnings.append(f"Certificate expires in {days_until_expiry} days — action needed soon")
    elif days_until_expiry <= 30:
        warnings.append(f"Certificate expires in {days_until_expiry} days")

    # Check protocol
    if protocol and "TLSv1.0" in protocol:
        warnings.append("Using deprecated TLS 1.0 — upgrade to TLS 1.2+")
    elif protocol and "TLSv1.1" in protocol:
        warnings.append("Using deprecated TLS 1.1 — upgrade to TLS 1.2+")

    # Grade
    if is_expired:
        grade = "F"
    elif days_until_expiry <= 7:
        grade = "D"
    elif days_until_expiry <= 30:
        grade = "C"
    elif protocol and "TLSv1.3" in protocol:
        grade = "A"
    elif protocol and "TLSv1.2" in protocol:
        grade = "B" if days_until_expiry <= 60 else "A"
    else:
        grade = "C"

    return {
        "status": "ok",
        "domain": domain,
        "valid": is_valid,
        "issuer": issuer,
        "subject": subject,
        "san": san,
        "not_before": not_before.strftime("%Y-%m-%d"),
        "not_after": not_after.strftime("%Y-%m-%d"),
        "days_until_expiry": days_until_expiry,
        "protocol": protocol or "unknown",
        "cipher": cipher[0] if cipher else "unknown",
        "chain_valid": True,
        "grade": grade,
        "warnings": warnings,
        "checked_at": datetime.now(timezone.utc).isoformat()
    }


def format_text(result):
    """Format results as human-readable text."""
    lines = [
        f"SSL/TLS Certificate Check: {result['domain']}",
        f"Grade: {result['grade']}",
        f"Valid: {'Yes' if result['valid'] else 'NO'}",
        f"Issuer: {result.get('issuer', 'N/A')}",
        f"Subject: {result.get('subject', 'N/A')}",
    ]

    if result.get("san"):
        lines.append(f"SANs: {', '.join(result['san'][:5])}")
        if len(result.get("san", [])) > 5:
            lines.append(f"  ... and {len(result['san']) - 5} more")

    lines.extend([
        f"Not Before: {result.get('not_before', 'N/A')}",
        f"Not After: {result.get('not_after', 'N/A')}",
        f"Days Until Expiry: {result.get('days_until_expiry', 'N/A')}",
        f"Protocol: {result.get('protocol', 'N/A')}",
        f"Cipher: {result.get('cipher', 'N/A')}",
        f"Chain Valid: {'Yes' if result.get('chain_valid') else 'NO'}",
    ])

    if result.get("warnings"):
        lines.append("\nWarnings:")
        for w in result["warnings"]:
            lines.append(f"  - {w}")

    if result.get("error"):
        lines.append(f"\nError: {result['error']}")

    return "\n".join(lines)


def main():
    parser = argparse.ArgumentParser(description="Check SSL/TLS certificate for a domain")
    parser.add_argument("--domain", required=True, help="Domain to check")
    parser.add_argument("--port", type=int, default=443, help="Port (default: 443)")
    parser.add_argument("--format", choices=["json", "text"], default="json", help="Output format")
    args = parser.parse_args()

    result, error = check_ssl(args.domain, args.port)
    if error:
        print(json.dumps({"status": "error", "message": error}), file=sys.stderr)
        sys.exit(1)

    if not result.get("valid", True) and result.get("status") == "error":
        if args.format == "json":
            print(json.dumps(result, indent=2))
        else:
            print(format_text(result))
        sys.exit(2)

    if args.format == "json":
        print(json.dumps(result, indent=2))
    else:
        print(format_text(result))


if __name__ == "__main__":
    main()
