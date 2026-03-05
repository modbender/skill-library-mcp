#!/usr/bin/env python3
"""
Email Resend - Outbound Sender

Send emails via Resend API with multi-account support.
Always shows preview before sending (requires user approval).

Usage:
    python3 outbound.py --to "x@y.com" --subject "Hello" --body "Message"
    python3 outbound.py --interactive
"""

import argparse
import json
import os
import sys
from pathlib import Path

import requests

# Import shared preferences
sys.path.insert(0, str(Path(__file__).parent))
from preferences import get_from_email, get_from_name

# Configuration
API_KEY = os.environ.get("RESEND_API_KEY")
if not API_KEY:
    print("ERROR: RESEND_API_KEY not set")
    print("Run: export RESEND_API_KEY=re_...")
    sys.exit(1)

API_BASE = "https://api.resend.com"

# Default sender info - prefers env var, falls back to preferences file
DEFAULT_FROM_EMAIL = get_from_email()
DEFAULT_FROM_NAME = get_from_name()


def fetch_message_id(email_id: str) -> str:
    """Fetch the actual Message-ID from an email for threading.
    
    Args:
        email_id: The Resend email ID (e.g., 'abc123...')
        
    Returns:
        The Message-ID from email headers, or the original email_id if not found
    """
    if not API_KEY:
        print("ERROR: RESEND_API_KEY not set")
        sys.exit(1)
    
    # Check if it looks like a Resend ID (UUID format)
    if "-" not in email_id:
        # Probably already a Message-ID
        return email_id
    
    try:
        response = requests.get(
            f"{API_BASE}/emails/{email_id}",
            headers={"Authorization": f"Bearer {API_KEY}"}
        )
        
        if response.status_code != 200:
            print(f"WARNING: Could not fetch email {email_id}: {response.status_code}")
            return email_id
        
        email_data = response.json()
        
        # Try to get Message-ID from headers
        headers = email_data.get("headers", {})
        message_id = headers.get("Message-ID") or headers.get("Message-Id")
        
        if message_id:
            return message_id
        
        # Fallback to the Bounce ID (less ideal for threading)
        bounce_id = email_data.get("bounce_id")
        if bounce_id:
            print(f"WARNING: No Message-ID found, using bounce_id (threading may not work)")
            return f"<{bounce_id}@resend>"
        
        print(f"WARNING: Could not determine Message-ID for {email_id}")
        return email_id
        
    except Exception as e:
        print(f"WARNING: Error fetching email {email_id}: {e}")
        return email_id


def send_email(from_email: str, from_name: str, to: list, subject: str, 
               body: str = None, html: str = None, reply_to: str = None,
               attachments: list = None) -> dict:
    """Send email via Resend API."""
    if not API_KEY:
        print("ERROR: RESEND_API_KEY not set")
        sys.exit(1)
    
    # Auto-fetch Message-ID if reply_to looks like an email ID
    if reply_to:
        original_reply_to = reply_to
        reply_to = fetch_message_id(reply_to)
        if reply_to != original_reply_to:
            print(f"🔗 Using Message-ID: {reply_to}")
    
    payload = {
        "from": f"{from_name} <{from_email}>",
        "to": to,
        "subject": subject,
    }
    
    if body:
        payload["text"] = body
    if html:
        payload["html"] = html
    if reply_to:
        # Set BOTH In-Reply-To and References for proper threading
        payload["headers"] = {
            "In-Reply-To": reply_to,
            "References": reply_to
        }
    
    # Add attachments
    if attachments:
        import base64
        payload_attachments = []
        for att in attachments:
            att_path = Path(att)
            if not att_path.exists():
                print(f"WARNING: Attachment not found: {att}")
                continue
            with open(att_path, "rb") as f:
                encoded = base64.b64encode(f.read()).decode()
            # Determine content_type from extension
            content_type = "application/octet-stream"
            if att_path.suffix == ".pdf":
                content_type = "application/pdf"
            elif att_path.suffix == ".ics":
                content_type = "text/calendar"
            elif att_path.suffix == ".pkpass":
                content_type = "application/vnd.apple.pkpass"
            elif att_path.suffix.lower() in [".png", ".jpg", ".jpeg", ".gif"]:
                content_type = f"image/{att_path.suffix[1:]}"
            elif att_path.suffix.lower() == ".html":
                content_type = "text/html"
            elif att_path.suffix.lower() == ".txt":
                content_type = "text/plain"
            
            payload_attachments.append({
                "filename": att_path.name,
                "content": encoded,
                "content_type": content_type
            })
        if payload_attachments:
            payload["attachments"] = payload_attachments
    
    response = requests.post(
        f"{API_BASE}/emails",
        headers={
            "Authorization": f"Bearer {API_KEY}",
            "Content-Type": "application/json"
        },
        json=payload
    )
    
    if response.status_code != 200:
        print(f"ERROR: API returned {response.status_code}")
        print(response.text)
        sys.exit(1)
    
    return response.json()


def main():
    parser = argparse.ArgumentParser(description="Send email via Resend")
    parser.add_argument("--from", "--from-email", dest="from_email", help="Sender email (or set DEFAULT_FROM_EMAIL env var)")
    parser.add_argument("--from-name", dest="from_name", help="Sender display name (or set DEFAULT_FROM_NAME env var)")
    parser.add_argument("--to", help="Recipient email(s), comma-separated")
    parser.add_argument("--subject", help="Email subject")
    parser.add_argument("--body", help="Plain text body")
    parser.add_argument("--html", help="HTML body (alternative to --body)")
    parser.add_argument("--reply-to", help="Message-ID to reply to (threading)")
    parser.add_argument("--attachment", "-a", action="append", help="Attachment file(s). Use multiple -a flags for multiple files")
    parser.add_argument("--interactive", action="store_true", help="Interactive mode")
    parser.add_argument("--dry-run", action="store_true", help="Show preview only, don't send")
    parser.add_argument("--yes", action="store_true", help="Skip confirmation (for scripts)")
    
    args = parser.parse_args()
    
    # Determine sender - CLI arg > env var > error
    from_email = args.from_email or DEFAULT_FROM_EMAIL
    from_name = args.from_name or DEFAULT_FROM_NAME
    
    if not from_email:
        print("ERROR: Sender email not specified")
        print("Use --from or set DEFAULT_FROM_EMAIL environment variable")
        sys.exit(1)
    
    # Interactive mode
    if args.interactive:
        print(f"\n📧 Send Email (from: {from_name} <{from_email}>)\n")
        to_input = input("To: ").strip()
        subject = input("Subject: ").strip()
        body = input("Body (plain text):\n").strip()
        args.to = to_input
        args.subject = subject
        args.body = body
    
    # Validate required args
    if not args.to or not args.subject:
        print("ERROR: --to and --subject are required (or use --interactive)")
        parser.print_help()
        sys.exit(1)
    
    # Threading validation - CRITICAL for replies
    if args.subject and args.subject.lower().startswith("re:"):
        if not args.reply_to:
            print("\n" + "=" * 50)
            print("⚠️  WARNING: Subject starts with 'Re:' but no --reply-to")
            print("=" * 50)
            print("This appears to be a REPLY but threading headers are missing.")
            print("The email will appear as a NEW thread, not a reply.")
            print("\nUse draft-reply.py for replies:")
            print("  python3 draft-reply.py start <email_id>")
            print("  python3 draft-reply.py content 'Your reply'")
            print("  python3 draft-reply.py send")
            print("=" * 50)
            if not args.yes:
                confirm = input("\nSend anyway? [y/N]: ").strip().lower()
                if confirm not in ("y", "yes"):
                    print("❌ Cancelled - use draft-reply.py for replies")
                    sys.exit(0)
            else:
                print("⚠️  Sending anyway (--yes flag)")
        else:
            print(f"🔗 Threading enabled via --reply-to")
    
    # Parse recipients
    to_list = [t.strip() for t in args.to.split(",")]
    
    # Show preview
    print("\n" + "=" * 50)
    print("📧 EMAIL PREVIEW")
    print("=" * 50)
    print(f"From: {from_name} <{from_email}>")
    print(f"To:  {', '.join(to_list)}")
    print(f"Subj: {args.subject}")
    if args.body:
        print(f"\nBody:\n{args.body}")
    if args.html:
        print(f"\n[HTML body - not shown]")
    print("=" * 50 + "\n")
    
    # Confirm
    if args.yes:
        print("✅ Auto-confirmed (--yes flag)")
    elif args.dry_run:
        print("🚫 Dry run - not sending")
        sys.exit(0)
    else:
        confirm = input("Send? [y/N]: ").strip().lower()
        if confirm not in ("y", "yes"):
            print("❌ Cancelled")
            sys.exit(0)
    
    # Send
    result = send_email(
        from_email=from_email,
        from_name=from_name,
        to=to_list,
        subject=args.subject,
        body=args.body,
        html=args.html,
        reply_to=args.reply_to,
        attachments=args.attachment
    )
    
    print(f"✅ Sent! ID: {result.get('id')}")


if __name__ == "__main__":
    main()
