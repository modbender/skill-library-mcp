#!/usr/bin/env python3
"""
Temporary Email OTP Extractor

Uses mail.tm API (free, no API key required).
Supports custom domains, creates accounts, and extracts OTP codes.

API: https://api.mail.tm

Usage:
    tempmail_otp.py create [-d DOMAIN] [-e EMAIL] [-p PASSWORD]
    tempmail_otp.py check [--timeout SECONDS] [--poll SECONDS] [--sender SENDER] [--subject SUBJECT]
    tempmail_otp.py list
    tempmail_otp.py domains
"""

import argparse
import json
import os
import re
import sys
import time
import uuid
from typing import Optional

try:
    import urllib.request
    import urllib.error
except ImportError:
    print("Error: urllib required (Python 3 standard library)")
    sys.exit(1)


# Unified state directory for all temp files
# Following XDG-like pattern: ~/.tempmail_otp/
STATE_DIR = os.path.expanduser("~/.tempmail_otp")
STATE_FILE = os.path.join(STATE_DIR, "account.json")
LAST_OTP_FILE = os.path.join(STATE_DIR, "last_otp")
LAST_LINK_FILE = os.path.join(STATE_DIR, "last_link")


def ensure_state_dir():
    """Create state directory if it doesn't exist."""
    os.makedirs(STATE_DIR, exist_ok=True)


def save_state(data: dict):
    """Save account state to file."""
    ensure_state_dir()
    with open(STATE_FILE, "w") as f:
        json.dump(data, f, indent=2)
    os.chmod(STATE_FILE, 0o600)  # Restrictive permissions


def load_state() -> Optional[dict]:
    """Load account state from file."""
    if not os.path.exists(STATE_FILE):
        return None
    with open(STATE_FILE, "r") as f:
        return json.load(f)


def delete_state():
    """Delete account state file."""
    if os.path.exists(STATE_FILE):
        os.remove(STATE_FILE)


def fetch_json(url: str, data: Optional[dict] = None, method: str = "GET", token: Optional[str] = None) -> dict:
    """Fetch JSON data from URL."""
    headers = {
        "User-Agent": "Mozilla/5.0",
        "Accept": "application/json",
        "Content-Type": "application/json",
    }

    if token:
        headers["Authorization"] = f"Bearer {token}"

    body = None
    if data:
        body = json.dumps(data).encode("utf-8")

    req = urllib.request.Request(url, data=body, headers=headers, method=method)

    try:
        with urllib.request.urlopen(req, timeout=30) as response:
            response_text = response.read().decode()
            if not response_text:
                return {}
            return json.loads(response_text)
    except urllib.error.HTTPError as e:
        body = e.read().decode()
        try:
            err_json = json.loads(body)
            detail = err_json.get("detail", err_json.get("hydra:description", body))
            raise RuntimeError(f"HTTP {e.code}: {detail}")
        except json.JSONDecodeError:
            raise RuntimeError(f"HTTP {e.code}: {body}")


def get_domains() -> list:
    """Get available domains from mail.tm."""
    url = "https://api.mail.tm/domains"
    data = fetch_json(url)
    if "hydra:member" in data:
        return data["hydra:member"]
    return data if isinstance(data, list) else [data]


def create_account(address: Optional[str] = None, domain: Optional[str] = None, password: Optional[str] = None) -> dict:
    """Create a new mail.tm account."""
    import random

    domains = get_domains()
    active_domains = [d["domain"] for d in domains if d.get("isActive")]

    if not active_domains:
        raise RuntimeError("No active domains available")

    if domain and domain not in active_domains:
        print(f"Warning: Domain {domain} not available, using random")

    target_domain = domain if domain in active_domains else random.choice(active_domains)

    # Generate random username if address not provided
    if not address:
        username = str(uuid.uuid4())[:8]
        address = f"{username}@{target_domain}"

    if not password:
        password = str(uuid.uuid4())

    # Create account
    url = "https://api.mail.tm/accounts"
    data = {"address": address, "password": password}

    try:
        result = fetch_json(url, data=data, method="POST")
    except RuntimeError as e:
        if "already used" in str(e):
            # Try with different username
            username = str(uuid.uuid4())[:12]
            address = f"{username}@{target_domain}"
            data["address"] = address
            result = fetch_json(url, data=data, method="POST")
        else:
            raise

    account_id = result.get("id")
    address = result.get("address", address)

    # Login to get token
    token_url = "https://api.mail.tm/token"
    token_data = {"address": address, "password": password}
    token_result = fetch_json(token_url, data=token_data, method="POST")
    token = token_result.get("token")

    if not token:
        raise RuntimeError("Failed to get authentication token")

    return {
        "address": address,
        "password": password,
        "token": token,
        "accountId": account_id,
        "domain": target_domain,
        "createdAt": time.strftime("%Y-%m-%dT%H:%M:%SZ"),
    }


def check_messages(token: str) -> list:
    """Fetch all messages in the inbox."""
    url = "https://api.mail.tm/messages"
    data = fetch_json(url, token=token)

    if "hydra:member" in data:
        return data["hydra:member"]
    return data if isinstance(data, list) else []


def get_message(token: str, msg_id: str) -> dict:
    """Fetch full message content by ID."""
    url = f"https://api.mail.tm/messages/{msg_id}"
    return fetch_json(url, token=token)


def extract_otp(text: str, pattern: Optional[str] = None) -> Optional[str]:
    """Extract OTP code from text."""
    if pattern:
        match = re.search(pattern, text)
        return match.group(1) if match else None

    # Remove HTML tags for cleaner matching
    text_clean = re.sub(r'<[^>]+>', ' ', text)

    # Common OTP patterns: 4-8 digits
    patterns = [
        r'\b(\d{6,8})\b',  # 6-8 digits (most common)
        r'\b(\d{4})\b',     # 4 digits
        r'code[:\s]+["\']?(\d{4,8})',  # "code: 123456"
        r'verification[:\s]+["\']?(\d{4,8})',  # "verification: 123456"
        r'otp[:\s]+["\']?(\d{4,8})',  # "otp: 123456"
        r'["\']?(\d{4,8})["\']?\s+is\s+(?:your|verification)',
    ]
    for p in patterns:
        match = re.search(p, text_clean, re.IGNORECASE)
        if match:
            return match.group(1)
    return None


def extract_urls(text: str) -> list:
    """Extract all URLs from text (handles HTML href attributes and plain URLs)."""
    urls = []

    # First, extract from HTML href attributes
    href_pattern = r'href=["\']([^"\']+)["\']'
    for match in re.finditer(href_pattern, text, re.IGNORECASE):
        url = match.group(1)
        # Clean up common URL issues
        if url and not url.startswith(('http://', 'https://', 'mailto:')):
            # Skip relative URLs and non-http links
            if not url.startswith('#') and not url.startswith('mailto:'):
                continue
        if url and not url.startswith('mailto:'):
            urls.append(url)

    # Also extract plain URLs that might not be in href tags
    url_pattern = r'https?://[^\s<>"\']+[^\s<>"\'.]'
    for match in re.finditer(url_pattern, text):
        url = match.group(0)
        # Remove trailing punctuation that's not part of URL
        url = url.rstrip('.,;:)')
        if url not in urls:
            urls.append(url)

    return urls


def cmd_create(args):
    """Create a new temporary email account."""
    try:
        account = create_account(
            address=args.email,
            domain=args.domain,
            password=args.password
        )
        save_state(account)

        if args.json:
            print(json.dumps(account, indent=2))
        else:
            print(f"Email: {account['address']}")
            print(f"Password: {account['password']}")
            print(f"Domain: {account['domain']}")
            print(f"\nAccount saved to {STATE_FILE}")
            print(f"Use 'tempmail_otp.py check' to wait for OTP")

        return 0
    except Exception as e:
        print(f"Error: {e}", file=sys.stderr)
        return 1


def cmd_check(args):
    """Check for OTP emails."""
    state = load_state()
    if not state:
        print("Error: No account found. Use 'create' command first.", file=sys.stderr)
        return 1

    token = state.get("token")
    address = state.get("address")

    if not token:
        print("Error: Invalid account state (no token). Recreate account.", file=sys.stderr)
        return 1

    start_time = time.time()
    seen_ids = set()

    print(f"Monitoring: {address}")
    print(f"Timeout: {args.timeout}s | Poll interval: {args.poll}s")
    print("-" * 50)

    while time.time() - start_time < args.timeout:
        try:
            messages = check_messages(token)
        except Exception as e:
            print(f"Warning: Failed to check messages: {e}")
            time.sleep(args.poll)
            continue

        for msg in messages:
            msg_id = msg.get("id")

            if msg_id in seen_ids:
                continue
            seen_ids.add(msg_id)

            from_addr = msg.get("from", {}).get("address", "")
            subject = msg.get("subject", "")

            # Apply filters
            if args.sender and args.sender.lower() not in from_addr.lower():
                continue
            if args.subject and args.subject.lower() not in subject.lower():
                continue

            print(f"\n📧 New email from: {from_addr}")
            print(f"   Subject: {subject}")

            # Get full message and extract OTP/Links
            try:
                full_msg = get_message(token, msg_id)

                text_content = ""
                html_content = ""
                if "text" in full_msg:
                    text_content = full_msg["text"] if isinstance(full_msg["text"], str) else ""
                if "html" in full_msg:
                    html_val = full_msg["html"]
                    if isinstance(html_val, list):
                        html_content = " ".join(html_val) if html_val else ""
                    elif isinstance(html_val, str):
                        html_content = html_val
                    else:
                        html_content = ""

                full_content = text_content + " " + html_content

                # Extract OTP
                otp = extract_otp(full_content, args.pattern)
                if otp:
                    print(f"\n✅ OTP FOUND: {otp}")

                    # Save OTP to file
                    ensure_state_dir()
                    with open(LAST_OTP_FILE, "w") as f:
                        f.write(otp)
                    print(f"OTP saved to {LAST_OTP_FILE}")
                    print("-" * 50)

                    if args.once:
                        return 0

                # Extract URLs
                urls = extract_urls(html_content or text_content)
                if urls:
                    print(f"\n🔗 Links found ({len(urls)}):")
                    # Filter out common tracking/utility URLs
                    interesting_urls = [
                        u for u in urls
                        if 'unsubscribe' not in u.lower()
                        and 'tracking' not in u.lower()
                        and not u.endswith('.png')
                        and not u.endswith('.jpg')
                        and not u.endswith('.gif')
                    ]
                    for i, url in enumerate(interesting_urls[:10], 1):  # Max 10 links
                        print(f"   {i}. {url}")
                    if len(interesting_urls) > 10:
                        print(f"   ... and {len(interesting_urls) - 10} more")

                    # Save first interesting link
                    if interesting_urls:
                        ensure_state_dir()
                        with open(LAST_LINK_FILE, "w") as f:
                            f.write(interesting_urls[0])
                        print(f"\nFirst link saved to {LAST_LINK_FILE}")

                if not otp and not urls:
                    print("   No OTP or links detected in message")
                    # Show preview of message
                    preview = re.sub(r'<[^>]+>', ' ', full_content)[:300]
                    print(f"   Preview: {preview}...")
                else:
                    print("-" * 50)

            except Exception as e:
                print(f"   Error reading message: {e}")

        # Progress indicator
        elapsed = int(time.time() - start_time)
        remaining = args.timeout - elapsed
        sys.stdout.write(f"\r⏳ Waiting... ({elapsed}s elapsed, {remaining}s remaining) | Messages seen: {len(seen_ids)}")
        sys.stdout.flush()
        time.sleep(args.poll)

    print(f"\n\n⏱️ Timeout waiting for OTP")
    return 1


def cmd_list(_args):
    """List saved account and current messages."""
    state = load_state()
    if not state:
        print("No account found. Use 'create' command first.")
        return 1

    token = state.get("token")
    address = state.get("address")

    print(f"📧 Email: {address}")
    print(f"🔐 Password: {state.get('password')}")
    print(f"🌐 Domain: {state.get('domain')}")
    print(f"📅 Created: {state.get('createdAt')}")

    if token:
        try:
            messages = check_messages(token)
            total = len(messages)
            print(f"\n📬 Messages in inbox: {total}")

            for i, msg in enumerate(messages, 1):
                from_addr = msg.get("from", {}).get("address", "unknown")
                subject = msg.get("subject", "no subject")
                msg_date = msg.get("createdAt", "")[:16]
                msg_id = msg.get("id")

                print(f"   {i}. {msg_date} | {from_addr}")
                print(f"      └─ {subject}")

                # Fetch full message to extract links
                try:
                    full_msg = get_message(token, msg_id)
                    html_val = full_msg.get("html", "")
                    if isinstance(html_val, list):
                        html_content = " ".join(html_val) if html_val else ""
                    else:
                        html_content = html_val or ""
                    text_content = full_msg.get("text", "") or ""
                    urls = extract_urls(html_content or text_content)

                    interesting_urls = [
                        u for u in urls
                        if 'unsubscribe' not in u.lower()
                        and 'tracking' not in u.lower()
                        and not u.endswith('.png')
                        and not u.endswith('.jpg')
                        and not u.endswith('.gif')
                    ]

                    if interesting_urls:
                        for url in interesting_urls[:3]:  # Show up to 3 links
                            print(f"      🔗 {url}")
                        if len(interesting_urls) > 3:
                            print(f"      ... and {len(interesting_urls) - 3} more links")

                except Exception as e:
                    pass  # Skip link extraction on error
        except Exception as e:
            print(f"Error fetching messages: {e}")

    return 0


def cmd_domains(args):
    """List available domains."""
    try:
        domains = get_domains()
        if args.json:
            print(json.dumps({"domains": domains}, indent=2))
        else:
            print("Available domains:")
            for d in domains:
                status = "✓" if d.get("isActive") else "✗"
                private = " [private]" if d.get("isPrivate") else ""
                print(f"  {status} {d.get('domain')}{private}")
        return 0
    except Exception as e:
        print(f"Error: {e}", file=sys.stderr)
        return 1


def main():
    parser = argparse.ArgumentParser(
        description="Temporary Email OTP Extractor",
        formatter_class=argparse.RawDescriptionHelpFormatter,
    )
    subparsers = parser.add_subparsers(dest="command", help="Command to run")

    # Create command
    create_parser = subparsers.add_parser("create", help="Create a new temporary email account")
    create_parser.add_argument("-e", "--email", help="Custom full email address")
    create_parser.add_argument("-d", "--domain", help="Specific domain to use")
    create_parser.add_argument("-p", "--password", help="Account password (auto-generated if not specified)")
    create_parser.add_argument("--json", action="store_true", help="Output as JSON")

    # Check command
    check_parser = subparsers.add_parser("check", help="Check for OTP emails")
    check_parser.add_argument("--timeout", type=int, default=300, help="Max seconds to wait (default: 300)")
    check_parser.add_argument("--poll", type=int, default=3, help="Poll interval in seconds (default: 3)")
    check_parser.add_argument("--sender", help="Only accept emails from this sender")
    check_parser.add_argument("--subject", help="Only accept emails with this in subject")
    check_parser.add_argument("--pattern", help="Custom regex pattern for OTP extraction")
    check_parser.add_argument("--once", action="store_true", help="Exit after first OTP found")
    check_parser.add_argument("--json", action="store_true", help="Output messages as JSON")

    # List command
    list_parser = subparsers.add_parser("list", help="List saved account and messages")

    # Domains command
    domains_parser = subparsers.add_parser("domains", help="List available domains")
    domains_parser.add_argument("--json", action="store_true", help="Output as JSON")

    args = parser.parse_args()

    if not args.command:
        parser.print_help()
        return 1

    commands = {
        "create": cmd_create,
        "check": cmd_check,
        "list": cmd_list,
        "domains": cmd_domains,
    }

    return commands[args.command](args)


if __name__ == "__main__":
    sys.exit(main())
