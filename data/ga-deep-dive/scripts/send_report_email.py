#!/usr/bin/env python3
"""
GA4 Deep Dive - Email Report Sender
Runs reports and sends via AgentMail

CONFIGURATION REQUIRED:
Set these environment variables before running:
  - GA4_REPORT_RECIPIENTS: Comma-separated list of email addresses
  - AGENTMAIL_INBOX: Your AgentMail inbox address
  - AGENTMAIL_API_KEY: Your AgentMail API key

Example:
  export GA4_REPORT_RECIPIENTS="you@example.com,team@example.com"
  export AGENTMAIL_INBOX="youragent@agentmail.to"
  export AGENTMAIL_API_KEY="am_your_key_here"
"""

import os
import subprocess
import sys
from datetime import datetime
from pathlib import Path

# Only try to import agentmail if we're actually sending
def get_agentmail_client():
    try:
        from agentmail import AgentMail
        return AgentMail
    except ImportError:
        print("❌ agentmail not installed. Run: pip install agentmail")
        sys.exit(1)

# Config
SCRIPT_DIR = Path(__file__).parent
VENV_PYTHON = SCRIPT_DIR.parent / ".venv" / "bin" / "python3"
REPORTS_DIR = SCRIPT_DIR.parent / "data" / "reports"
REPORTS_DIR.mkdir(parents=True, exist_ok=True)

def get_config():
    """Get configuration from environment variables."""
    recipients = os.environ.get("GA4_REPORT_RECIPIENTS", "")
    inbox = os.environ.get("AGENTMAIL_INBOX", "")
    api_key = os.environ.get("AGENTMAIL_API_KEY", "")
    
    errors = []
    if not recipients:
        errors.append("GA4_REPORT_RECIPIENTS not set")
    if not inbox:
        errors.append("AGENTMAIL_INBOX not set")
    if not api_key:
        errors.append("AGENTMAIL_API_KEY not set")
    
    if errors:
        print("❌ Missing required configuration:")
        for e in errors:
            print(f"   - {e}")
        print("\nSet environment variables before running. See script header for details.")
        sys.exit(1)
    
    return {
        "recipients": [r.strip() for r in recipients.split(",") if r.strip()],
        "inbox": inbox,
        "api_key": api_key
    }

def run_report(script_name: str, property_name: str, days: int = 14) -> str:
    """Run a deep dive script and capture output."""
    script_path = SCRIPT_DIR / script_name
    
    result = subprocess.run(
        [str(VENV_PYTHON), str(script_path), property_name, "--days", str(days)],
        capture_output=True,
        text=True,
        timeout=300
    )
    
    return result.stdout + result.stderr

def send_email(config: dict, subject: str, body: str):
    """Send email via AgentMail."""
    AgentMail = get_agentmail_client()
    client = AgentMail(api_key=config["api_key"])
    
    # Format body as HTML (preserve formatting)
    html_body = f"""
    <html>
    <body style="font-family: monospace; white-space: pre-wrap; background: #1a1a2e; color: #eee; padding: 20px;">
    <pre style="font-size: 12px; line-height: 1.4;">
{body}
    </pre>
    </body>
    </html>
    """
    
    for email in config["recipients"]:
        try:
            client.inboxes.messages.send(
                inbox_id=config["inbox"],
                to=email,
                subject=subject,
                html=html_body
            )
            print(f"✅ Email sent to {email}")
        except Exception as e:
            print(f"❌ Failed to send to {email}: {e}")
    
    return True

def main():
    import argparse
    parser = argparse.ArgumentParser(description="Generate and send GA4 reports via email")
    parser.add_argument("property", help="GA4 property name (from config)")
    parser.add_argument("--days", type=int, default=14, help="Analysis period in days")
    parser.add_argument("--dry-run", action="store_true", help="Generate report without sending email")
    args = parser.parse_args()
    
    print("🏴‍☠️ GA4 Deep Dive - Report Generator")
    print(f"   Time: {datetime.utcnow().strftime('%Y-%m-%d %H:%M UTC')}")
    print(f"   Property: {args.property}")
    print(f"   Period: {args.days} days")
    print()
    
    # Get config (skip if dry-run)
    config = None
    if not args.dry_run:
        config = get_config()
        print(f"📧 Recipients: {', '.join(config['recipients'])}")
        print(f"📤 From inbox: {config['inbox']}")
    else:
        print("🔍 DRY RUN - No email will be sent")
    print()
    
    # Run reports
    print("📊 Running V3 (Executive Summary)...")
    v3_report = run_report("deep_dive_v3.py", args.property, args.days)
    
    print("📊 Running V4 (Full Monty)...")
    v4_report = run_report("deep_dive_v4.py", args.property, args.days)
    
    # Combine
    timestamp = datetime.utcnow().strftime("%Y-%m-%d %H:%M UTC")
    full_report = f"""
{'═'*80}
   GA4 ANALYTICS REPORT
   Generated: {timestamp}
   Property: {args.property}
   Period: Last {args.days} days
{'═'*80}

{'='*80}
   PART 1: EXECUTIVE SUMMARY (V3)
{'='*80}

{v3_report}


{'='*80}
   PART 2: THE FULL MONTY (V4)
{'='*80}

{v4_report}


{'═'*80}
   Report generated by ga-deep-dive
   https://clawhub.com/skills/ga-deep-dive
{'═'*80}
"""
    
    # Save report
    report_file = REPORTS_DIR / f"{args.property}_report_{datetime.now().strftime('%Y%m%d_%H%M')}.txt"
    report_file.write_text(full_report)
    print(f"💾 Report saved: {report_file}")
    
    # Send email (unless dry-run)
    if not args.dry_run and config:
        subject = f"📊 GA4 Report: {args.property} - {datetime.now().strftime('%b %d, %Y')}"
        print(f"\n📧 Sending report...")
        send_email(config, subject, full_report)
    
    print("\n✅ Done!")

if __name__ == "__main__":
    main()
