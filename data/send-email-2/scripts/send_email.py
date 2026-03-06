#!/usr/bin/env python3
"""Email sending utility using smtplib with support for HTML and attachments."""

import argparse
import email.message
import email.policy
import json
import mimetypes
import os
import re
import smtplib
import ssl
import sys
from email.utils import formataddr
from pathlib import Path
from typing import Optional

import markdown


def is_markdown_content(content: str) -> bool:
    """Detect if content is in markdown format.

    Args:
        content: Text content to check

    Returns:
        True if content appears to be markdown
    """
    # Check for common markdown patterns
    markdown_patterns = [
        r'^#{1,6}\s+.+$',  # Headers
        r'^\*{1,3}.+\*{1,3}$',  # Bold/italic
        r'^\s*[-*+]\s+',  # Unordered lists
        r'^\s*\d+\.\s+',  # Ordered lists
        r'^\s*>\s+',  # Blockquotes
        r'```',  # Code blocks
        r'\[.+\]\(.+\)',  # Links
        r'^\s*---+\s*$',  # Horizontal rules
        r'^\*\*.+\*\*',  # Bold
    ]

    lines = content.split('\n')
    markdown_score = 0

    for line in lines:
        for pattern in markdown_patterns:
            if re.match(pattern, line.strip(), re.MULTILINE):
                markdown_score += 1
                break

    # If more than 20% of lines have markdown syntax, consider it markdown
    return markdown_score > len(lines) * 0.2 or markdown_score > 3


def markdown_to_html(content: str) -> str:
    """Convert markdown content to styled HTML.

    Args:
        content: Markdown text

    Returns:
        HTML formatted content with styling
    """
    # Use markdown library with extensions
    html = markdown.markdown(
        content,
        extensions=['extra', 'nl2br', 'sane_lists', 'tables']
    )

    # Wrap with email-friendly styling
    styled_html = f"""
<!DOCTYPE html>
<html>
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <style>
        body {{
            font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, 'Helvetica Neue', Arial, sans-serif;
            line-height: 1.6;
            color: #333;
            max-width: 800px;
            margin: 0 auto;
            padding: 20px;
            background-color: #f5f5f5;
        }}
        .email-content {{
            background-color: white;
            padding: 30px;
            border-radius: 8px;
            box-shadow: 0 2px 8px rgba(0,0,0,0.1);
        }}
        h1 {{
            color: #2c3e50;
            border-bottom: 3px solid #3498db;
            padding-bottom: 10px;
            margin-top: 0;
        }}
        h2 {{
            color: #34495e;
            border-bottom: 2px solid #95a5a6;
            padding-bottom: 8px;
            margin-top: 30px;
        }}
        h3 {{
            color: #5d6d7e;
            margin-top: 25px;
        }}
        h4 {{
            color: #7f8c8d;
        }}
        p {{
            margin: 12px 0;
        }}
        ul, ol {{
            margin: 12px 0;
            padding-left: 30px;
        }}
        li {{
            margin: 8px 0;
        }}
        code {{
            background-color: #f8f9fa;
            padding: 2px 6px;
            border-radius: 3px;
            font-family: 'Courier New', monospace;
            font-size: 0.9em;
            color: #e74c3c;
        }}
        pre {{
            background-color: #f8f9fa;
            padding: 15px;
            border-radius: 5px;
            border-left: 4px solid #3498db;
            overflow-x: auto;
        }}
        pre code {{
            background-color: transparent;
            padding: 0;
            color: inherit;
        }}
        blockquote {{
            border-left: 4px solid #3498db;
            padding-left: 20px;
            margin: 15px 0;
            color: #555;
            font-style: italic;
        }}
        strong {{
            color: #2c3e50;
            font-weight: 600;
        }}
        em {{
            color: #34495e;
        }}
        hr {{
            border: none;
            border-top: 2px solid #ecf0f1;
            margin: 30px 0;
        }}
        table {{
            border-collapse: collapse;
            width: 100%;
            margin: 20px 0;
        }}
        th, td {{
            border: 1px solid #ddd;
            padding: 12px;
            text-align: left;
        }}
        th {{
            background-color: #3498db;
            color: white;
            font-weight: 600;
        }}
        tr:nth-child(even) {{
            background-color: #f8f9fa;
        }}
        a {{
            color: #3498db;
            text-decoration: none;
        }}
        a:hover {{
            text-decoration: underline;
        }}
    </style>
</head>
<body>
    <div class="email-content">
        {html}
    </div>
</body>
</html>
"""
    return styled_html


def read_template(template_path: str, variables: dict) -> str:
    """Read email template and substitute variables.

    Template variables should be in format {{variable_name}}.

    Args:
        template_path: Path to template file
        variables: Dictionary of variable substitutions

    Returns:
        Rendered email content
    """
    with open(template_path, 'r', encoding='utf-8') as f:
        content = f.read()

    for key, value in variables.items():
        content = content.replace('{{' + key + '}}', str(value))

    return content


def send_email(
    to: str,
    subject: str,
    content: str,
    smtp_server: str,
    smtp_port: int,
    username: str,
    password: str,
    from_addr: Optional[str] = None,
    from_name: Optional[str] = None,
    content_type: str = 'html',
    attachments: Optional[list[str]] = None,
    use_tls: bool = True,
    use_ssl: bool = False,
) -> bool:
    """Send email via SMTP.

    Args:
        to: Recipient email address
        subject: Email subject
        content: Email body content
        smtp_server: SMTP server hostname
        smtp_port: SMTP server port
        username: SMTP username
        password: SMTP password
        from_addr: Sender email address (defaults to username)
        from_name: Sender display name
        content_type: 'html' or 'plain'
        attachments: List of file paths to attach
        use_tls: Use STARTTLS encryption
        use_ssl: Use SSL encryption (exclusive with use_tls)

    Returns:
        True if successful, False otherwise
    """
    if from_addr is None:
        from_addr = username

    msg = email.message.EmailMessage(policy=email.policy.default)

    msg['To'] = to
    msg['Subject'] = subject

    if from_name:
        msg['From'] = formataddr((from_name, from_addr))
    else:
        msg['From'] = from_addr

    if content_type == 'html':
        msg.set_content(content, subtype='html')
    else:
        msg.set_content(content)

    if attachments:
        for filepath in attachments:
            path = Path(filepath)
            if not path.exists():
                print(f"Warning: Attachment not found: {filepath}", file=sys.stderr)
                continue

            mime_type, encoding = mimetypes.guess_type(filepath)
            if mime_type is None:
                mime_type = 'application/octet-stream'

            main_type, sub_type = mime_type.split('/', 1)

            with open(filepath, 'rb') as f:
                msg.add_attachment(
                    f.read(),
                    maintype=main_type,
                    subtype=sub_type,
                    filename=path.name,
                )

    try:
        if use_ssl:
            context = ssl.create_default_context()
            with smtplib.SMTP_SSL(smtp_server, smtp_port, context=context) as server:
                server.login(username, password)
                server.send_message(msg)
        else:
            context = ssl.create_default_context()
            with smtplib.SMTP(smtp_server, smtp_port) as server:
                if use_tls:
                    server.starttls(context=context)
                server.login(username, password)
                server.send_message(msg)

        print(f"Email sent successfully to {to}")
        return True

    except Exception as e:
        print(f"Failed to send email: {e}", file=sys.stderr)
        return False


def main():
    parser = argparse.ArgumentParser(description='Send email via SMTP')
    parser.add_argument('--to', required=True, help='Recipient email address')
    parser.add_argument('--subject', required=True, help='Email subject')
    parser.add_argument('--content', help='Email body content (or use --template)')
    parser.add_argument('--template', help='Path to email template file')
    parser.add_argument('--template-vars', help='JSON string of template variables')
    parser.add_argument('--smtp-server', required=True, help='SMTP server hostname')
    parser.add_argument('--smtp-port', type=int, required=True, help='SMTP server port')
    parser.add_argument('--username', required=True, help='SMTP username')
    parser.add_argument('--password', required=True, help='SMTP password')
    parser.add_argument('--from-addr', help='Sender email address (default: username)')
    parser.add_argument('--from-name', help='Sender display name')
    parser.add_argument('--content-type', choices=['plain', 'html'], default='plain',
                        help='Content type (default: plain)')
    parser.add_argument('--attach', action='append', help='File attachment (can be used multiple times)')
    parser.add_argument('--no-tls', action='store_true', help='Disable STARTTLS')
    parser.add_argument('--use-ssl', action='store_true', help='Use SSL instead of STARTTLS')

    args = parser.parse_args()

    if args.template and args.content:
        print("Error: Cannot specify both --template and --content", file=sys.stderr)
        sys.exit(1)

    if args.template:
        if not args.template_vars:
            print("Warning: No template variables provided", file=sys.stderr)
            variables = {}
        else:
            variables = json.loads(args.template_vars)
        content = read_template(args.template, variables)
    elif args.content:
        content = args.content
    else:
        content = ""

    # Auto-detect and convert markdown to HTML
    content_type = args.content_type
    if content and content_type == 'plain' and is_markdown_content(content):
        print("Detected markdown content, converting to HTML...", file=sys.stderr)
        content = markdown_to_html(content)
        content_type = 'html'

    success = send_email(
        to=args.to,
        subject=args.subject,
        content=content,
        smtp_server=args.smtp_server,
        smtp_port=args.smtp_port,
        username=args.username,
        password=args.password,
        from_addr=args.from_addr,
        from_name=args.from_name,
        content_type=content_type,
        attachments=args.attach,
        use_tls=not args.no_tls,
        use_ssl=args.use_ssl,
    )

    sys.exit(0 if success else 1)


if __name__ == '__main__':
    main()
