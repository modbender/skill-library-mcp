#!/usr/bin/env python3
"""
Send email via SMTP or Resend API.

Usage:
    python3 send_email.py --to <recipient> --subject <subject> --body <body> [--html] [--attachments file1,file2]
    python3 send_email.py --to <recipient> --subject <subject> --body <body> --provider resend

Providers:
    smtp (default) - Traditional SMTP
    resend         - Resend.com API (simpler setup)

Environment variables (or ~/.smtp_config):
    # SMTP
    SMTP_HOST       - SMTP server hostname
    SMTP_PORT       - SMTP server port (default: 587)
    SMTP_USER       - SMTP username
    SMTP_PASSWORD   - SMTP password or app password
    SMTP_FROM       - From email address
    SMTP_USE_SSL    - Use SSL (true for port 465)
    
    # Resend
    RESEND_API_KEY  - Resend API key (or in ~/.smtp_config as "resend_api_key")
    RESEND_FROM     - From address (or in ~/.smtp_config as "resend_from")
"""

import argparse
import smtplib
import ssl
import sys
import os
import json
import base64
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from email.mime.base import MIMEBase
from email import encoders
from pathlib import Path
from urllib.request import Request, urlopen
from urllib.error import HTTPError

CONFIG_FILE = Path.home() / '.smtp_config'

def load_config():
    """Load config from environment or ~/.smtp_config file."""
    config = {}
    
    # Try to load from config file
    if CONFIG_FILE.exists():
        try:
            with open(CONFIG_FILE) as f:
                config = json.load(f)
        except Exception as e:
            print(f"Warning: Failed to load {CONFIG_FILE}: {e}", file=sys.stderr)
    
    # Environment variables override config file
    # SMTP settings
    config['host'] = os.getenv('SMTP_HOST', config.get('host'))
    config['port'] = int(os.getenv('SMTP_PORT', config.get('port', 587)))
    config['user'] = os.getenv('SMTP_USER', config.get('user'))
    config['password'] = os.getenv('SMTP_PASSWORD', config.get('password'))
    config['from'] = os.getenv('SMTP_FROM', config.get('from', config.get('user')))
    
    # Handle use_ssl
    use_ssl_value = os.getenv('SMTP_USE_SSL', config.get('use_ssl', False))
    if isinstance(use_ssl_value, bool):
        config['use_ssl'] = use_ssl_value
    else:
        config['use_ssl'] = str(use_ssl_value).lower() == 'true'
    
    # Resend settings
    config['resend_api_key'] = os.getenv('RESEND_API_KEY', config.get('resend_api_key'))
    config['resend_from'] = os.getenv('RESEND_FROM', config.get('resend_from', 'onboarding@resend.dev'))
    
    return config

def validate_smtp_config(config):
    """Check if SMTP config is valid."""
    required = ['host', 'user', 'password']
    return all(config.get(f) for f in required)

def validate_resend_config(config):
    """Check if Resend config is valid."""
    return bool(config.get('resend_api_key'))

def send_via_smtp(config, to, subject, body, is_html=False, attachments=None):
    """Send email via SMTP."""
    # Create message
    if attachments:
        message = MIMEMultipart()
        message['From'] = config['from']
        message['To'] = to
        message['Subject'] = subject
        
        msg_body = MIMEText(body, 'html' if is_html else 'plain')
        message.attach(msg_body)
        
        for filepath in attachments:
            filepath = Path(filepath)
            if not filepath.exists():
                print(f"Warning: Attachment not found: {filepath}", file=sys.stderr)
                continue
            
            with open(filepath, 'rb') as f:
                part = MIMEBase('application', 'octet-stream')
                part.set_payload(f.read())
            
            encoders.encode_base64(part)
            part.add_header('Content-Disposition', f'attachment; filename={filepath.name}')
            message.attach(part)
    else:
        message = MIMEText(body, 'html' if is_html else 'plain')
        message['From'] = config['from']
        message['To'] = to
        message['Subject'] = subject
    
    # Send
    try:
        if config['use_ssl']:
            context = ssl.create_default_context()
            server = smtplib.SMTP_SSL(config['host'], config['port'], context=context)
        else:
            server = smtplib.SMTP(config['host'], config['port'])
            server.starttls()
        
        server.login(config['user'], config['password'])
        server.send_message(message)
        server.quit()
        
        print(f"✓ Email sent via SMTP to {to}")
        return True
    except Exception as e:
        print(f"SMTP error: {e}", file=sys.stderr)
        return False

def send_via_resend(config, to, subject, body, is_html=False, attachments=None):
    """Send email via Resend API."""
    api_key = config['resend_api_key']
    from_addr = config['resend_from']
    
    # Build payload
    payload = {
        "from": from_addr,
        "to": [to],
        "subject": subject,
    }
    
    if is_html:
        payload["html"] = body
    else:
        payload["text"] = body
    
    # Add attachments
    if attachments:
        attachment_list = []
        for filepath in attachments:
            filepath = Path(filepath)
            if not filepath.exists():
                print(f"Warning: Attachment not found: {filepath}", file=sys.stderr)
                continue
            
            with open(filepath, 'rb') as f:
                content = base64.b64encode(f.read()).decode('utf-8')
            
            attachment_list.append({
                "filename": filepath.name,
                "content": content
            })
        
        if attachment_list:
            payload["attachments"] = attachment_list
    
    # Send request
    try:
        req = Request(
            "https://api.resend.com/emails",
            data=json.dumps(payload).encode('utf-8'),
            headers={
                "Authorization": f"Bearer {api_key}",
                "Content-Type": "application/json",
                "User-Agent": "Mozilla/5.0 (compatible; Clawdbot/1.0)"
            },
            method="POST"
        )
        
        with urlopen(req, timeout=30) as response:
            result = json.loads(response.read().decode('utf-8'))
            print(f"✓ Email sent via Resend to {to} (id: {result.get('id', 'unknown')})")
            return True
            
    except HTTPError as e:
        error_body = e.read().decode('utf-8')
        print(f"Resend API error: {e.code} - {error_body}", file=sys.stderr)
        return False
    except Exception as e:
        print(f"Resend error: {e}", file=sys.stderr)
        return False

def print_config_help():
    """Print configuration help."""
    print("Error: No email provider configured.", file=sys.stderr)
    print(f"\nCreate {CONFIG_FILE} with SMTP or Resend settings:", file=sys.stderr)
    print("""
Option 1 - SMTP (163/QQ/Gmail/etc):
{
    "host": "smtp.163.com",
    "port": 465,
    "user": "your-email@163.com",
    "password": "your-auth-code",
    "from": "your-email@163.com",
    "use_ssl": true
}

Option 2 - Resend (recommended, simpler):
{
    "resend_api_key": "re_xxxxx",
    "resend_from": "you@your-domain.com"
}

Get a free Resend API key at: https://resend.com
""", file=sys.stderr)

def main():
    parser = argparse.ArgumentParser(description='Send email via SMTP or Resend')
    parser.add_argument('--to', required=True, help='Recipient email address')
    parser.add_argument('--subject', required=True, help='Email subject')
    parser.add_argument('--body', required=True, help='Email body')
    parser.add_argument('--html', action='store_true', help='Send as HTML email')
    parser.add_argument('--attachments', help='Comma-separated list of attachment file paths')
    parser.add_argument('--provider', choices=['smtp', 'resend', 'auto'], default='auto',
                        help='Email provider (default: auto)')
    
    args = parser.parse_args()
    
    # Load config
    config = load_config()
    
    # Parse attachments
    attachments = None
    if args.attachments:
        attachments = [p.strip() for p in args.attachments.split(',')]
    
    # Determine provider
    provider = args.provider
    has_smtp = validate_smtp_config(config)
    has_resend = validate_resend_config(config)
    
    if provider == 'auto':
        # Prefer Resend if configured, fallback to SMTP
        if has_resend:
            provider = 'resend'
        elif has_smtp:
            provider = 'smtp'
        else:
            print_config_help()
            sys.exit(1)
    
    # Validate chosen provider
    if provider == 'smtp' and not has_smtp:
        print("Error: SMTP not configured. Set host/user/password.", file=sys.stderr)
        sys.exit(1)
    
    if provider == 'resend' and not has_resend:
        print("Error: Resend not configured. Set resend_api_key.", file=sys.stderr)
        sys.exit(1)
    
    # Send
    if provider == 'resend':
        success = send_via_resend(config, args.to, args.subject, args.body, args.html, attachments)
    else:
        success = send_via_smtp(config, args.to, args.subject, args.body, args.html, attachments)
    
    # If auto mode and failed, try fallback
    if not success and args.provider == 'auto':
        if provider == 'resend' and has_smtp:
            print("Trying SMTP fallback...", file=sys.stderr)
            success = send_via_smtp(config, args.to, args.subject, args.body, args.html, attachments)
        elif provider == 'smtp' and has_resend:
            print("Trying Resend fallback...", file=sys.stderr)
            success = send_via_resend(config, args.to, args.subject, args.body, args.html, attachments)
    
    sys.exit(0 if success else 1)

if __name__ == '__main__':
    main()
