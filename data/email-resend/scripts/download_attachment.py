#!/usr/bin/env python3
"""
Resend Inbound Email Attachment Downloader

Downloads attachments from received emails using the Resend API.

Usage:
    python3 download_attachment.py <email_id> [--output-dir DIR]
    python3 download_attachment.py <email_id> --list    # Just list attachments
"""

import argparse
import json
import os
import sys
from pathlib import Path

import requests

API_KEY = os.environ.get("RESEND_API_KEY")
if not API_KEY:
    print("ERROR: RESEND_API_KEY not set")
    sys.exit(1)

API_BASE = "https://api.resend.com"


def list_attachments(email_id: str) -> dict:
    """List attachments for an email."""
    # Path is /emails/receiving/{email_id}/attachments
    url = f"{API_BASE}/emails/receiving/{email_id}/attachments"
    headers = {"Authorization": f"Bearer {API_KEY}"}
    
    response = requests.get(url, headers=headers)
    response.raise_for_status()
    return response.json()


def download_attachment_url(url: str, output_path: Path) -> None:
    """Download an attachment from the signed URL."""
    response = requests.get(url)
    response.raise_for_status()
    
    with open(output_path, "wb") as f:
        f.write(response.content)
    print(f"✅ Downloaded: {output_path.name} ({len(response.content)} bytes)")


def main():
    parser = argparse.ArgumentParser(description="Download attachments from Resend inbound emails")
    parser.add_argument("email_id", help="The email ID (from Resend)")
    parser.add_argument("--output-dir", "-o", default=".", help="Output directory (default: current)")
    parser.add_argument("--list", "-l", action="store_true", help="Only list attachments, don't download")
    parser.add_argument("--attachment-id", "-a", help="Download specific attachment by ID")
    
    args = parser.parse_args()
    
    # List attachments
    print(f"📋 Listing attachments for email: {args.email_id}")
    result = list_attachments(args.email_id)
    
    if "data" not in result or not result["data"]:
        print("❌ No attachments found")
        sys.exit(1)
    
    attachments = result["data"]
    print(f"Found {len(attachments)} attachment(s):\n")
    
    for att in attachments:
        print(f"  - {att['filename']} ({att.get('size', '?')} bytes, {att.get('content_type', '?')})")
        print(f"    ID: {att['id']}")
        print(f"    Expires: {att.get('expires_at', '?')}")
        print()
    
    if args.list:
        print("Use --attachment-id <id> to download specific attachment")
        return
    
    # Download
    output_dir = Path(args.output_dir)
    output_dir.mkdir(parents=True, exist_ok=True)
    
    if args.attachment_id:
        # Download specific
        att = next((a for a in attachments if a["id"] == args.attachment_id), None)
        if not att:
            print(f"❌ Attachment not found: {args.attachment_id}")
            sys.exit(1)
        
        output_path = output_dir / att["filename"]
        download_attachment_url(att["download_url"], output_path)
    else:
        # Download all
        for att in attachments:
            output_path = output_dir / att["filename"]
            try:
                download_attachment_url(att["download_url"], output_path)
            except Exception as e:
                print(f"❌ Failed to download {att['filename']}: {e}")


if __name__ == "__main__":
    main()
