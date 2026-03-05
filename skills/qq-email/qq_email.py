#!/usr/bin/env python3
"""
QQ Email Tool for OpenClaw
Send and receive emails via QQ Mail SMTP/IMAP server.

Usage:
    # Send
    python3 qq_email.py send --to "recipient@example.com" --subject "Subject" --content "Content"
    python3 qq_email.py send --to "recipient@example.com" --subject "Subject" --content "Content" --html
    python3 qq_email.py send --to "recipient@example.com" --subject "Subject" --content "Content" --attachment "/path/to/file"
    
    # Receive
    python3 qq_email.py receive                      # List recent emails
    python3 qq_email.py receive --count 10           # List 10 emails
    python3 qq_email.py receive --unread             # List unread emails only
    python3 qq_email.py read --uid 123               # Read specific email
    python3 qq_email.py read --uid 123 --save        # Read and save attachments

Configuration:
    Store QQ email config in ~/.openclaw/workspace/TOOLS.md or use environment variables:
    - QQ_EMAIL_ADDRESS: your QQ email (e.g., 123456@qq.com)
    - QQ_EMAIL_AUTH: your 16-char authorization code
    - QQ_EMAIL_SENDER: sender name (optional)
"""

import argparse
import smtplib
import imaplib
import email
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from email.mime.base import MIMEBase
from email import encoders
from email.header import Header, decode_header
from email.utils import formataddr, parseaddr
import os
import sys
import json
import base64
import quopri
from datetime import datetime
from pathlib import Path

# QQ Mail Server Configuration
SMTP_SERVER = "smtp.qq.com"
SMTP_PORT = 465  # SSL port
IMAP_SERVER = "imap.qq.com"
IMAP_PORT = 993  # SSL port
TIMEOUT = 30


def get_qq_config():
    """Get QQ email configuration from environment or TOOLS.md"""
    config = {
        "email": os.environ.get("QQ_EMAIL_ADDRESS", ""),
        "auth": os.environ.get("QQ_EMAIL_AUTH", ""),
        "sender": os.environ.get("QQ_EMAIL_SENDER", "OpenClaw Assistant"),
    }

    # Try to load from TOOLS.md if env vars not set
    if not config["email"] or not config["auth"]:
        tools_path = os.path.expanduser("~/.openclaw/workspace/TOOLS.md")
        if os.path.exists(tools_path):
            try:
                with open(tools_path, "r", encoding="utf-8") as f:
                    content = f.read()
                    
                    # Parse QQ Email section
                    if "QQ Email" in content or "qq email" in content.lower():
                        lines = content.split("\n")
                        for i, line in enumerate(lines):
                            if "Email:" in line and ("qq.com" in line or "@" in line):
                                email_val = line.split(":", 1)[1].strip()
                                if email_val and not config["email"]:
                                    config["email"] = email_val
                            elif "Auth Code:" in line or "Authorization:" in line:
                                auth_val = line.split(":", 1)[1].strip()
                                if auth_val and not config["auth"]:
                                    config["auth"] = auth_val
                            elif "Sender Name:" in line or "Sender:" in line:
                                sender_val = line.split(":", 1)[1].strip()
                                if sender_val and config["sender"] == "OpenClaw Assistant":
                                    config["sender"] = sender_val
            except Exception as e:
                print(f"Warning: Could not read TOOLS.md: {e}", file=sys.stderr)

    return config


def decode_mime_words(s):
    """Decode MIME encoded words in email headers"""
    if not s:
        return ""
    
    decoded_parts = []
    for part, encoding in decode_header(s):
        if isinstance(part, bytes):
            try:
                if encoding:
                    decoded_parts.append(part.decode(encoding, errors='replace'))
                else:
                    decoded_parts.append(part.decode('utf-8', errors='replace'))
            except:
                decoded_parts.append(part.decode('utf-8', errors='replace'))
        else:
            decoded_parts.append(part)
    
    return ''.join(decoded_parts)


def get_email_body(msg):
    """Extract email body (plain text or HTML)"""
    body = ""
    attachments = []
    
    if msg.is_multipart():
        for part in msg.walk():
            content_type = part.get_content_type()
            content_disposition = str(part.get("Content-Disposition") or "")
            
            # Check for attachments
            if "attachment" in content_disposition:
                filename = part.get_filename()
                if filename:
                    filename = decode_mime_words(filename)
                    attachments.append({
                        "filename": filename,
                        "payload": part.get_payload(decode=True)
                    })
            # Get email body
            elif content_type == "text/plain":
                try:
                    payload = part.get_payload(decode=True)
                    if payload:
                        body = payload.decode('utf-8', errors='replace')
                except:
                    pass
            elif content_type == "text/html":
                if not body:  # Prefer plain text, but use HTML if no plain text
                    try:
                        payload = part.get_payload(decode=True)
                        if payload:
                            body = payload.decode('utf-8', errors='replace')
                    except:
                        pass
    else:
        # Not multipart
        try:
            payload = msg.get_payload(decode=True)
            if payload:
                body = payload.decode('utf-8', errors='replace')
        except:
            body = msg.get_payload()
    
    return body, attachments


def send_email(to_email, subject, content, html=False, attachment=None):
    """
    Send email via QQ Mail SMTP
    
    Args:
        to_email: Recipient email address (comma-separated for multiple)
        subject: Email subject
        content: Email content (plain text or HTML)
        html: If True, send as HTML; otherwise plain text
        attachment: Optional file path to attach
    
    Returns:
        dict: {"success": bool, "message": str}
    """
    config = get_qq_config()
    
    # Validate configuration
    if not config["email"]:
        return {
            "success": False,
            "message": "QQ email address not configured. Set QQ_EMAIL_ADDRESS env var or add to TOOLS.md"
        }
    
    if not config["auth"]:
        return {
            "success": False,
            "message": "QQ auth code not configured. Set QQ_EMAIL_AUTH env var or add to TOOLS.md"
        }
    
    # Parse recipients
    recipients = [email.strip() for email in to_email.split(",")]
    
    try:
        # Create message
        if attachment:
            msg = MIMEMultipart()
            msg.attach(MIMEText(content, "html" if html else "plain", "utf-8"))
            
            # Add attachment
            with open(attachment, "rb") as f:
                part = MIMEBase("application", "octet-stream")
                part.set_payload(f.read())
                encoders.encode_base64(part)
                part.add_header(
                    "Content-Disposition",
                    f"attachment; filename={os.path.basename(attachment)}"
                )
                msg.attach(part)
        else:
            msg = MIMEText(content, "html" if html else "plain", "utf-8")
        
        # Set headers
        msg["From"] = formataddr((Header(config["sender"], "utf-8").encode(), config["email"]))
        msg["To"] = ", ".join(recipients)
        msg["Subject"] = Header(subject, "utf-8")
        
        # Connect and send
        server = smtplib.SMTP_SSL(SMTP_SERVER, SMTP_PORT, timeout=TIMEOUT)
        server.set_debuglevel(0)
        
        try:
            server.login(config["email"], config["auth"])
            server.sendmail(config["email"], recipients, msg.as_string())
            server.quit()
            
            return {
                "success": True,
                "message": f"Email sent successfully to {len(recipients)} recipient(s)"
            }
        except smtplib.SMTPAuthenticationError:
            return {
                "success": False,
                "message": "Authentication failed. Check your QQ email auth code (not password!)"
            }
        except smtplib.SMTPException as e:
            return {
                "success": False,
                "message": f"SMTP error: {str(e)}"
            }
        finally:
            try:
                server.quit()
            except:
                pass
                
    except FileNotFoundError:
        return {
            "success": False,
            "message": f"Attachment file not found: {attachment}"
        }
    except Exception as e:
        return {
            "success": False,
            "message": f"Error: {str(e)}"
        }


def receive_emails(count=10, unread_only=False, search_from=None, search_subject=None):
    """
    Receive/list emails via QQ Mail IMAP
    
    Args:
        count: Number of emails to retrieve
        unread_only: If True, only fetch unread emails
        search_from: Filter by sender
        search_subject: Filter by subject
    
    Returns:
        dict: {"success": bool, "emails": list, "message": str}
    """
    config = get_qq_config()
    
    # Validate configuration
    if not config["email"]:
        return {
            "success": False,
            "message": "QQ email address not configured"
        }
    
    if not config["auth"]:
        return {
            "success": False,
            "message": "QQ auth code not configured"
        }
    
    try:
        # Connect to IMAP server
        mail = imaplib.IMAP4_SSL(IMAP_SERVER, IMAP_PORT, timeout=TIMEOUT)
        
        # Login
        mail.login(config["email"], config["auth"])
        
        # Select inbox
        mail.select("inbox")
        
        # Search for emails
        if unread_only:
            status, messages = mail.search(None, "UNSEEN")
        else:
            status, messages = mail.search(None, "ALL")
        
        if status != "OK":
            return {
                "success": False,
                "message": "Failed to search emails"
            }
        
        # Get email IDs
        email_ids = messages[0].split()
        
        if not email_ids:
            mail.close()
            mail.logout()
            return {
                "success": True,
                "emails": [],
                "message": "No emails found"
            }
        
        # Get the most recent emails
        email_ids = email_ids[-count:]
        email_ids.reverse()  # Most recent first
        
        emails = []
        for uid in email_ids:
            try:
                status, msg_data = mail.fetch(uid, "(RFC822)")
                if status != "OK":
                    continue
                
                raw_email = msg_data[0][1]
                msg = email.message_from_bytes(raw_email)
                
                # Get email info
                subject = decode_mime_words(msg.get("Subject", ""))
                from_ = decode_mime_words(msg.get("From", ""))
                to_ = decode_mime_words(msg.get("To", ""))
                date_str = msg.get("Date", "")
                
                # Parse date
                try:
                    parsed_date = datetime.strptime(date_str[:25], "%a, %d %b %Y %H:%M:%S")
                    date_formatted = parsed_date.strftime("%Y-%m-%d %H:%M")
                except:
                    date_formatted = date_str
                
                # Get body and attachments
                body, attachments = get_email_body(msg)
                
                # Check if unread
                status, _ = mail.fetch(uid, "(FLAGS)")
                flags = str(status)
                is_unread = "\\Seen" not in flags
                
                emails.append({
                    "uid": uid.decode() if isinstance(uid, bytes) else str(uid),
                    "subject": subject,
                    "from": from_,
                    "to": to_,
                    "date": date_formatted,
                    "unread": is_unread,
                    "body": body[:500] + "..." if len(body) > 500 else body,  # Truncate for list view
                    "body_full": body,
                    "has_attachments": len(attachments) > 0,
                    "attachments": [att["filename"] for att in attachments]
                })
            except Exception as e:
                print(f"Warning: Error processing email {uid}: {e}", file=sys.stderr)
                continue
        
        mail.close()
        mail.logout()
        
        return {
            "success": True,
            "emails": emails,
            "message": f"Retrieved {len(emails)} email(s)"
        }
        
    except imaplib.IMAP4.error as e:
        return {
            "success": False,
            "message": f"IMAP error: {str(e)}"
        }
    except Exception as e:
        return {
            "success": False,
            "message": f"Error: {str(e)}"
        }


def read_email(uid, save_attachments=False, output_dir=None):
    """
    Read a specific email by UID
    
    Args:
        uid: Email UID
        save_attachments: If True, save attachments to disk
        output_dir: Directory to save attachments (default: ~/Downloads)
    
    Returns:
        dict: {"success": bool, "email": dict, "message": str}
    """
    config = get_qq_config()
    
    if not config["email"] or not config["auth"]:
        return {
            "success": False,
            "message": "QQ email not configured"
        }
    
    try:
        # Connect to IMAP server
        mail = imaplib.IMAP4_SSL(IMAP_SERVER, IMAP_PORT, timeout=TIMEOUT)
        mail.login(config["email"], config["auth"])
        mail.select("inbox")
        
        # Fetch email
        status, msg_data = mail.fetch(uid.encode(), "(RFC822)")
        
        if status != "OK":
            mail.close()
            mail.logout()
            return {
                "success": False,
                "message": f"Failed to fetch email {uid}"
            }
        
        raw_email = msg_data[0][1]
        msg = email.message_from_bytes(raw_email)
        
        # Get email info
        subject = decode_mime_words(msg.get("Subject", ""))
        from_ = decode_mime_words(msg.get("From", ""))
        to_ = decode_mime_words(msg.get("To", ""))
        date_str = msg.get("Date", "")
        
        # Parse date
        try:
            parsed_date = datetime.strptime(date_str[:25], "%a, %d %b %Y %H:%M:%S")
            date_formatted = parsed_date.strftime("%Y-%m-%d %H:%M")
        except:
            date_formatted = date_str
        
        # Get body and attachments
        body, attachments = get_email_body(msg)
        
        # Check if unread
        status, _ = mail.fetch(uid.encode(), "(FLAGS)")
        flags = str(status)
        is_unread = "\\Seen" not in flags
        
        email_data = {
            "uid": uid,
            "subject": subject,
            "from": from_,
            "to": to_,
            "date": date_formatted,
            "unread": is_unread,
            "body": body,
            "has_attachments": len(attachments) > 0,
            "attachments": []
        }
        
        # Save attachments if requested
        if save_attachments and attachments:
            if output_dir is None:
                output_dir = os.path.expanduser("~/Downloads")
            
            os.makedirs(output_dir, exist_ok=True)
            
            for att in attachments:
                try:
                    filepath = os.path.join(output_dir, att["filename"])
                    with open(filepath, "wb") as f:
                        f.write(att["payload"])
                    email_data["attachments"].append({
                        "filename": att["filename"],
                        "saved_to": filepath,
                        "size": len(att["payload"])
                    })
                except Exception as e:
                    email_data["attachments"].append({
                        "filename": att["filename"],
                        "error": str(e)
                    })
        
        mail.close()
        mail.logout()
        
        return {
            "success": True,
            "email": email_data,
            "message": f"Email retrieved successfully"
        }
        
    except Exception as e:
        return {
            "success": False,
            "message": f"Error: {str(e)}"
        }


def mark_as_read(uid):
    """Mark email as read"""
    config = get_qq_config()
    
    if not config["email"] or not config["auth"]:
        return {"success": False, "message": "QQ email not configured"}
    
    try:
        mail = imaplib.IMAP4_SSL(IMAP_SERVER, IMAP_PORT, timeout=TIMEOUT)
        mail.login(config["email"], config["auth"])
        mail.select("inbox")
        
        # Mark as seen
        mail.store(uid.encode(), "+FLAGS", "\\Seen")
        
        mail.close()
        mail.logout()
        
        return {"success": True, "message": f"Email {uid} marked as read"}
    except Exception as e:
        return {"success": False, "message": f"Error: {str(e)}"}


def main():
    parser = argparse.ArgumentParser(
        description="Send and receive emails via QQ Mail",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Send email
  %(prog)s send -t "test@example.com" -s "Hello" -c "Content"
  %(prog)s send -t "test@example.com" -s "HTML" -c "<h1>Hi</h1>" --html
  %(prog)s send -t "test@example.com" -s "File" -c "See attached" -a "/path/to/file.pdf"
  
  # Receive emails
  %(prog)s receive                    # List 10 recent emails
  %(prog)s receive -n 20              # List 20 emails
  %(prog)s receive --unread           # List unread only
  
  # Read specific email
  %(prog)s read --uid 123             # Read email with UID 123
  %(prog)s read --uid 123 --save      # Save attachments

Configuration:
  Set environment variables or add to ~/.openclaw/workspace/TOOLS.md:
  - QQ_EMAIL_ADDRESS: your_qq_number@qq.com
  - QQ_EMAIL_AUTH: 16-character authorization code
  - QQ_EMAIL_SENDER: Your Name (optional)
        """
    )
    
    subparsers = parser.add_subparsers(dest="command", help="Command to execute")
    
    # Send command
    send_parser = subparsers.add_parser("send", help="Send an email")
    send_parser.add_argument("--to", "-t", required=True, help="Recipient email(s)")
    send_parser.add_argument("--subject", "-s", required=True, help="Email subject")
    send_parser.add_argument("--content", "-c", required=True, help="Email content")
    send_parser.add_argument("--html", action="store_true", help="Send as HTML")
    send_parser.add_argument("--attachment", "-a", help="File path to attach")
    send_parser.add_argument("--json", action="store_true", help="Output as JSON")
    
    # Receive command
    recv_parser = subparsers.add_parser("receive", help="List emails")
    recv_parser.add_argument("--count", "-n", type=int, default=10, help="Number of emails")
    recv_parser.add_argument("--unread", action="store_true", help="Unread only")
    recv_parser.add_argument("--json", action="store_true", help="Output as JSON")
    
    # Read command
    read_parser = subparsers.add_parser("read", help="Read specific email")
    read_parser.add_argument("--uid", required=True, help="Email UID")
    read_parser.add_argument("--save", action="store_true", help="Save attachments")
    read_parser.add_argument("--output-dir", help="Output directory for attachments")
    read_parser.add_argument("--json", action="store_true", help="Output as JSON")
    
    # Mark as read command
    mark_parser = subparsers.add_parser("mark-read", help="Mark email as read")
    mark_parser.add_argument("--uid", required=True, help="Email UID")
    mark_parser.add_argument("--json", action="store_true", help="Output as JSON")
    
    args = parser.parse_args()
    
    if args.command == "send":
        result = send_email(
            to_email=args.to,
            subject=args.subject,
            content=args.content,
            html=args.html,
            attachment=args.attachment
        )
    elif args.command == "receive":
        result = receive_emails(count=args.count, unread_only=args.unread)
    elif args.command == "read":
        result = read_email(
            uid=args.uid,
            save_attachments=args.save,
            output_dir=args.output_dir
        )
    elif args.command == "mark-read":
        result = mark_as_read(uid=args.uid)
    else:
        parser.print_help()
        sys.exit(1)
    
    # Output result
    if args.json:
        print(json.dumps(result, ensure_ascii=False, indent=2))
    else:
        if result["success"]:
            print(f"✅ {result['message']}")
            
            # Display emails for receive command
            if args.command == "receive" and "emails" in result:
                for i, email in enumerate(result["emails"], 1):
                    unread_marker = "📬" if email["unread"] else "📭"
                    att_marker = "📎" if email["has_attachments"] else ""
                    print(f"\n{unread_marker} [{i}] UID: {email['uid']}")
                    print(f"   主题：{email['subject']}")
                    print(f"   发件人：{email['from']}")
                    print(f"   日期：{email['date']}")
                    print(f"   预览：{email['body'][:100]}...")
                    if email["has_attachments"]:
                        print(f"   附件：{', '.join(email['attachments'])}")
            
            # Display email for read command
            elif args.command == "read" and "email" in result:
                e = result["email"]
                print(f"\n📧 {e['subject']}")
                print(f"发件人：{e['from']}")
                print(f"收件人：{e['to']}")
                print(f"日期：{e['date']}")
                print(f"状态：{'未读' if e['unread'] else '已读'}")
                if e["has_attachments"]:
                    print(f"附件：{len(e['attachments'])} 个")
                    for att in e["attachments"]:
                        if "saved_to" in att:
                            print(f"  ✅ {att['filename']} → {att['saved_to']}")
                        else:
                            print(f"  ⚠️ {att['filename']}: {att.get('error', '')}")
                print(f"\n{'='*50}")
                print(e["body"])
        else:
            print(f"❌ {result['message']}", file=sys.stderr)
            sys.exit(1)


if __name__ == "__main__":
    main()
