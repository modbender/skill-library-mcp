#!/usr/bin/env python3
"""
Safe Email Parser

Parses email files (EML format) and extracts content safely with
security policy enforcement.

Usage:
    python parse_email.py --input "email.eml" --json
    python parse_email.py --input "email.eml" --attachments-dir "./attachments"
"""

import argparse
import email
import json
import os
import re
import sys
from email import policy
from email.parser import BytesParser
from pathlib import Path
from typing import Optional


# Attachment security policies
ALLOWED_EXTENSIONS = {'.pdf', '.txt', '.csv', '.png', '.jpg', '.jpeg', '.gif', '.docx', '.xlsx'}
BLOCKED_EXTENSIONS = {'.exe', '.bat', '.sh', '.ps1', '.js', '.vbs', '.jar', '.py', '.ics', '.vcf', '.scr', '.com'}
MAX_ATTACHMENT_SIZE_MB = 25


def extract_email_address(header_value: str) -> str:
    """Extract email address from header value like 'Name <email@domain.com>'."""
    if not header_value:
        return ""
    
    match = re.search(r'[\w\.-]+@[\w\.-]+\.\w+', header_value)
    return match.group(0).lower() if match else header_value.lower()


def get_headers(msg: email.message.Message) -> dict:
    """Extract security-relevant headers."""
    headers = {}
    
    relevant_headers = [
        'From', 'To', 'Cc', 'Bcc', 'Reply-To', 'Return-Path',
        'Subject', 'Date', 'Message-ID',
        'Authentication-Results', 'Received-SPF', 'DKIM-Signature',
        'X-Spam-Status', 'X-Spam-Score'
    ]
    
    for header in relevant_headers:
        value = msg.get(header)
        if value:
            headers[header] = str(value)
    
    return headers


def get_body(msg: email.message.Message) -> dict:
    """Extract email body (plain text preferred)."""
    body = {
        "plain": "",
        "html": "",
        "preferred": ""
    }
    
    if msg.is_multipart():
        for part in msg.walk():
            content_type = part.get_content_type()
            content_disposition = str(part.get("Content-Disposition", ""))
            
            # Skip attachments
            if "attachment" in content_disposition:
                continue
            
            try:
                payload = part.get_payload(decode=True)
                if payload:
                    charset = part.get_content_charset() or 'utf-8'
                    text = payload.decode(charset, errors='replace')
                    
                    if content_type == "text/plain":
                        body["plain"] = text
                    elif content_type == "text/html":
                        body["html"] = text
            except:
                pass
    else:
        try:
            payload = msg.get_payload(decode=True)
            if payload:
                charset = msg.get_content_charset() or 'utf-8'
                text = payload.decode(charset, errors='replace')
                
                if msg.get_content_type() == "text/html":
                    body["html"] = text
                else:
                    body["plain"] = text
        except:
            body["plain"] = str(msg.get_payload())
    
    # Set preferred body (plain text over HTML)
    body["preferred"] = body["plain"] if body["plain"] else body["html"]
    
    return body


def get_attachments(msg: email.message.Message) -> list:
    """Extract attachment metadata (without content for safety)."""
    attachments = []
    
    if not msg.is_multipart():
        return attachments
    
    for part in msg.walk():
        content_disposition = str(part.get("Content-Disposition", ""))
        
        if "attachment" not in content_disposition:
            continue
        
        filename = part.get_filename() or "unnamed"
        content_type = part.get_content_type()
        
        # Get size
        payload = part.get_payload(decode=True)
        size_bytes = len(payload) if payload else 0
        size_mb = size_bytes / (1024 * 1024)
        
        # Get extension
        ext = Path(filename).suffix.lower()
        
        # Determine safety
        if ext in BLOCKED_EXTENSIONS:
            safety = "blocked"
            reason = "Blocked file type"
        elif ext not in ALLOWED_EXTENSIONS:
            safety = "unknown"
            reason = "Unknown file type"
        elif size_mb > MAX_ATTACHMENT_SIZE_MB:
            safety = "blocked"
            reason = f"Exceeds size limit ({MAX_ATTACHMENT_SIZE_MB}MB)"
        else:
            safety = "allowed"
            reason = None
        
        attachments.append({
            "filename": filename,
            "content_type": content_type,
            "size_bytes": size_bytes,
            "size_mb": round(size_mb, 2),
            "extension": ext,
            "safety": safety,
            "reason": reason
        })
    
    return attachments


def save_safe_attachments(msg: email.message.Message, output_dir: str) -> list:
    """Save allowed attachments to directory."""
    saved = []
    output_path = Path(output_dir)
    output_path.mkdir(parents=True, exist_ok=True)
    
    if not msg.is_multipart():
        return saved
    
    for part in msg.walk():
        content_disposition = str(part.get("Content-Disposition", ""))
        
        if "attachment" not in content_disposition:
            continue
        
        filename = part.get_filename() or "unnamed"
        ext = Path(filename).suffix.lower()
        
        # Check if allowed
        if ext in BLOCKED_EXTENSIONS:
            continue
        if ext not in ALLOWED_EXTENSIONS:
            continue
        
        payload = part.get_payload(decode=True)
        if not payload:
            continue
        
        # Check size
        size_mb = len(payload) / (1024 * 1024)
        if size_mb > MAX_ATTACHMENT_SIZE_MB:
            continue
        
        # Save file
        # Sanitize filename to prevent path traversal
        safe_filename = re.sub(r'[^\w\.-]', '_', filename)
        file_path = output_path / safe_filename
        
        # Avoid overwriting
        counter = 1
        while file_path.exists():
            stem = Path(safe_filename).stem
            suffix = Path(safe_filename).suffix
            file_path = output_path / f"{stem}_{counter}{suffix}"
            counter += 1
        
        file_path.write_bytes(payload)
        saved.append({
            "filename": safe_filename,
            "path": str(file_path),
            "size_bytes": len(payload)
        })
    
    return saved


def parse_email(
    input_path: str,
    save_attachments_to: Optional[str] = None
) -> dict:
    """
    Parse an email file safely.
    
    Returns:
        dict with keys:
            - headers: Security-relevant headers
            - sender: Extracted sender email
            - recipients: List of recipient emails
            - subject: Email subject
            - body: Email body content
            - attachments: Attachment metadata
            - saved_attachments: List of saved files (if output dir provided)
    """
    result = {
        "headers": {},
        "sender": "",
        "recipients": [],
        "subject": "",
        "body": {},
        "attachments": [],
        "saved_attachments": [],
        "warnings": []
    }
    
    # Parse email
    with open(input_path, 'rb') as f:
        msg = BytesParser(policy=policy.default).parse(f)
    
    # Extract components
    result["headers"] = get_headers(msg)
    result["sender"] = extract_email_address(result["headers"].get("From", ""))
    result["subject"] = result["headers"].get("Subject", "")
    
    # Get recipients
    for header in ["To", "Cc", "Bcc"]:
        if header in result["headers"]:
            addresses = re.findall(r'[\w\.-]+@[\w\.-]+\.\w+', result["headers"][header])
            result["recipients"].extend([a.lower() for a in addresses])
    
    # Get body
    result["body"] = get_body(msg)
    
    # Get attachments
    result["attachments"] = get_attachments(msg)
    
    # Add warnings for blocked attachments
    blocked = [a for a in result["attachments"] if a["safety"] == "blocked"]
    if blocked:
        result["warnings"].append(f"{len(blocked)} attachment(s) blocked for security")
    
    # Save attachments if requested
    if save_attachments_to:
        result["saved_attachments"] = save_safe_attachments(msg, save_attachments_to)
    
    return result


def main():
    parser = argparse.ArgumentParser(description="Parse email files safely")
    parser.add_argument("--input", required=True, help="Path to EML file")
    parser.add_argument("--attachments-dir", help="Directory to save safe attachments")
    parser.add_argument("--json", action="store_true", help="Output as JSON")
    parser.add_argument("--headers-only", action="store_true", help="Only show headers")
    
    args = parser.parse_args()
    
    if not Path(args.input).exists():
        print(f"Error: File not found: {args.input}", file=sys.stderr)
        sys.exit(1)
    
    result = parse_email(args.input, args.attachments_dir)
    
    if args.json:
        print(json.dumps(result, indent=2))
    elif args.headers_only:
        print("=== EMAIL HEADERS ===")
        for k, v in result["headers"].items():
            print(f"{k}: {v}")
    else:
        print("=== EMAIL SUMMARY ===")
        print(f"From: {result['sender']}")
        print(f"To: {', '.join(result['recipients'])}")
        print(f"Subject: {result['subject']}")
        
        print("\n=== BODY ===")
        body = result["body"]["preferred"][:500]
        if len(result["body"]["preferred"]) > 500:
            body += "...[truncated]"
        print(body)
        
        if result["attachments"]:
            print("\n=== ATTACHMENTS ===")
            for att in result["attachments"]:
                status = "✅" if att["safety"] == "allowed" else "❌"
                print(f"  {status} {att['filename']} ({att['size_mb']}MB) - {att['safety']}")
                if att["reason"]:
                    print(f"     Reason: {att['reason']}")
        
        if result["saved_attachments"]:
            print(f"\n✅ Saved {len(result['saved_attachments'])} attachment(s) to {args.attachments_dir}")
        
        if result["warnings"]:
            print("\n⚠️  WARNINGS:")
            for w in result["warnings"]:
                print(f"  - {w}")


if __name__ == "__main__":
    main()
