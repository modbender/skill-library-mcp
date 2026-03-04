#!/usr/bin/env python3
"""
IMAP IDLE Listener - Event-driven email notifications for OpenClaw

Monitors IMAP accounts using IDLE protocol and triggers OpenClaw webhooks
when new emails arrive. Zero tokens while waiting, instant notifications.

Usage:
    python3 listener.py [--config CONFIG_PATH]

Config format (JSON):
{
  "accounts": [
    {
      "host": "mail.example.com",
      "port": 993,
      "username": "user@example.com",
      "password": "password",
      "ssl": true
    }
  ],
  "webhook_url": "http://127.0.0.1:18789/hooks/wake",
  "webhook_token": "your-webhook-token",
  "log_file": null,
  "idle_timeout": 300,
  "reconnect_interval": 900
}
"""

import sys
import json
import time
import logging
import threading
import urllib.request
from pathlib import Path
from datetime import datetime

try:
    from imapclient import IMAPClient
except ImportError:
    print("ERROR: imapclient library not found", file=sys.stderr)
    print("Install with: pip3 install imapclient --user", file=sys.stderr)
    sys.exit(1)

# Optional keyring support for secure credential storage
try:
    import keyring
    KEYRING_AVAILABLE = True
except ImportError:
    KEYRING_AVAILABLE = False


class IMAPIdleListener:
    def __init__(self, config):
        self.config = config
        self.webhook_url = config['webhook_url']
        self.webhook_token = config['webhook_token']
        self.idle_timeout = config.get('idle_timeout', 300)  # 5 min default
        self.reconnect_interval = config.get('reconnect_interval', 900)  # 15 min default
        self.debounce_seconds = config.get('debounce_seconds', 10)  # 10 sec default
        
        # Debouncing buffer
        self.pending_events = []
        self.debounce_timer = None
        self.debounce_lock = threading.Lock()
        
        # Setup logging
        log_file = config.get('log_file')
        logging.basicConfig(
            level=logging.INFO,
            format='%(asctime)s [%(levelname)s] %(message)s',
            handlers=[
                logging.FileHandler(log_file) if log_file else logging.StreamHandler(),
            ]
        )
        self.logger = logging.getLogger(__name__)
    
    def get_password(self, username, account_config):
        """
        Get password for account with secure fallback:
        1. Try keyring (if available)
        2. Fall back to config file
        
        Returns password string or None
        """
        # Try keyring first (most secure)
        if KEYRING_AVAILABLE:
            try:
                password = keyring.get_password('imap-idle', username)
                if password:
                    self.logger.debug(f"🔐 Using keyring password for {username}")
                    return password
            except Exception as e:
                self.logger.warning(f"⚠️  Keyring access failed for {username}: {e}")
        
        # Fall back to config file
        password = account_config.get('password')
        if password:
            self.logger.debug(f"📄 Using config file password for {username}")
            return password
        
        # No password found
        self.logger.error(f"❌ No password found for {username} (not in keyring or config)")
        return None
    
    def queue_event(self, account, from_addr, subject, body_preview=""):
        """Queue an email event for debounced webhook trigger"""
        with self.debounce_lock:
            # Add event to buffer
            event = {
                'account': account,
                'from': from_addr,
                'subject': subject,
                'body_preview': body_preview,
                'timestamp': datetime.now()
            }
            self.pending_events.append(event)
            
            self.logger.info(f"📥 Queued: {account} from {from_addr[:50]} (buffer: {len(self.pending_events)})")
            
            # Cancel existing timer
            if self.debounce_timer:
                self.debounce_timer.cancel()
            
            # Start new timer
            self.debounce_timer = threading.Timer(
                self.debounce_seconds,
                self.flush_events
            )
            self.debounce_timer.daemon = True
            self.debounce_timer.start()
    
    def flush_events(self):
        """Send batched events via webhook"""
        with self.debounce_lock:
            if not self.pending_events:
                return
            
            events = self.pending_events.copy()
            self.pending_events.clear()
            self.debounce_timer = None
        
        try:
            # Format message based on event count
            if len(events) == 1:
                # Single event - format normally
                event = events[0]
                text = self._format_single_event(event)
            else:
                # Multiple events - batch format
                text = f"📬 {len(events)} новых писем:\n\n"
                
                # Group GitHub notifications separately
                github_events = [e for e in events if 'github' in e['from'].lower()]
                other_events = [e for e in events if 'github' not in e['from'].lower()]
                
                if github_events:
                    text += f"🔔 GitHub ({len(github_events)}):\n"
                    for event in github_events[:5]:  # Max 5 to avoid overflow
                        preview = self._format_github_preview(event)
                        text += f"  • {preview}\n"
                    if len(github_events) > 5:
                        text += f"  • ... и ещё {len(github_events) - 5}\n"
                    text += "\n"
                
                if other_events:
                    text += f"📧 Другие ({len(other_events)}):\n"
                    for event in other_events[:5]:  # Max 5
                        text += f"  • {event['account']}: {event['from'][:40]}\n"
                        text += f"    {event['subject'][:60]}\n"
                    if len(other_events) > 5:
                        text += f"  • ... и ещё {len(other_events) - 5}\n"
            
            text = text[:2000]  # Limit total length
            
            payload = {
                "text": text,
                "mode": "now"
            }
            
            headers = {
                "Authorization": f"Bearer {self.webhook_token}",
                "Content-Type": "application/json"
            }
            
            req = urllib.request.Request(
                self.webhook_url,
                data=json.dumps(payload).encode('utf-8'),
                headers=headers,
                method='POST'
            )
            
            with urllib.request.urlopen(req, timeout=5) as response:
                self.logger.info(f"✅ Webhook sent: {len(events)} event(s)")
                
        except Exception as e:
            self.logger.error(f"❌ Webhook failed: {e}")
    
    def _format_single_event(self, event):
        """Format a single event for webhook"""
        account = event['account']
        from_addr = event['from']
        subject = event['subject']
        body_preview = event['body_preview']
        
        # Special handling for GitHub notifications
        if 'github' in from_addr.lower() and account == "a.parmeev@jakeberrimor.com":
            # Parse GitHub notification type
            if '@arkasha-ai' in subject or '@arkasha-ai' in body_preview:
                icon = "💬"
                action = "упомянули"
            elif 'review requested' in subject.lower():
                icon = "👀"
                action = "запросили review"
            elif 'assigned you' in subject.lower() or 'assigned to you' in subject.lower():
                icon = "📌"
                action = "назначили"
            elif 'mentioned you' in subject.lower():
                icon = "💬"
                action = "mention"
            else:
                icon = "🔔"
                action = "уведомление"
            
            return f"{icon} GitHub: тебя {action}\n{subject}\n\n{body_preview[:500]}"
        else:
            # Regular email notification
            text = f"📧 New email in {account}:\nFrom: {from_addr}\nSubject: {subject}"
            if body_preview:
                text += f"\n\n{body_preview[:300]}"
            return text
    
    def _format_github_preview(self, event):
        """Format GitHub event for batch display"""
        subject = event['subject']
        body = event['body_preview']
        
        if '@arkasha-ai' in subject or '@arkasha-ai' in body:
            return f"💬 mention: {subject[:60]}"
        elif 'review requested' in subject.lower():
            return f"👀 review: {subject[:60]}"
        elif 'assigned' in subject.lower():
            return f"📌 assigned: {subject[:60]}"
        else:
            return f"🔔 {subject[:60]}"
    
    def parse_email_body(self, body_data):
        """Parse and extract preview from email body"""
        if not body_data:
            return ""
        
        try:
            body_text = body_data.decode('utf-8', errors='ignore')
            # Take first 500 chars, strip excessive whitespace
            lines = [line.strip() for line in body_text.split('\n') if line.strip()]
            preview = '\n'.join(lines[:10])  # First 10 non-empty lines
            return preview[:500]
        except Exception:
            return ""
    
    def parse_email_headers(self, header_data):
        """Parse From and Subject from email headers"""
        headers_text = header_data.decode('utf-8', errors='ignore')
        lines = headers_text.split('\n')
        
        from_addr = ""
        subject = ""
        
        for line in lines:
            line_lower = line.lower()
            if line_lower.startswith('from:'):
                from_addr = line[5:].strip()
            elif line_lower.startswith('subject:'):
                subject = line[8:].strip()
        
        return from_addr or "Unknown", subject or "(no subject)"
    
    def listen_account(self, account_config):
        """Monitor one IMAP account with IDLE"""
        host = account_config['host']
        port = account_config.get('port', 993)
        username = account_config['username']
        password = self.get_password(username, account_config)
        ssl = account_config.get('ssl', True)
        
        # Abort if no password available
        if not password:
            self.logger.error(f"❌ Cannot monitor {username}: no password available")
            return
        
        # Track last processed UID to prevent duplicates
        last_uid = None
        
        # Exponential backoff for reconnects
        backoff = 5
        max_backoff = 300
        
        while True:
            try:
                self.logger.info(f"🔌 Connecting to {username}@{host}...")
                
                # Connect to IMAP server
                client = IMAPClient(host, port=port, ssl=ssl, timeout=30)
                client.login(username, password)
                client.select_folder('INBOX')
                
                # Get current latest UID (don't process old emails on startup)
                messages = client.search(['ALL'])
                if messages:
                    last_uid = max(messages)
                    self.logger.info(f"📬 {username}: Starting from UID {last_uid}")
                
                # Start IDLE mode
                client.idle()
                self.logger.info(f"✅ {username}: IDLE monitoring active")
                
                # Reset backoff on successful connect
                backoff = 5
                
                # Track when we started IDLE for periodic reconnect
                idle_start = time.time()
                
                while True:
                    # Check for IDLE responses (5 min timeout)
                    responses = client.idle_check(timeout=self.idle_timeout)
                    
                    # If we got responses, new mail arrived
                    if responses:
                        self.logger.info(f"📨 {username}: IDLE notification received")
                        
                        # Exit IDLE to check messages
                        client.idle_done()
                        
                        # Search for new messages
                        messages = client.search(['ALL'])
                        if messages:
                            latest_uid = max(messages)
                            
                            # Only process if this is a NEW message
                            if latest_uid != last_uid:
                                # Fetch headers and body preview
                                msg_data = client.fetch(
                                    [latest_uid],
                                    ['BODY.PEEK[HEADER.FIELDS (FROM SUBJECT)]', 'BODY.PEEK[TEXT]']
                                )
                                
                                header_data = msg_data[latest_uid][b'BODY[HEADER.FIELDS (FROM SUBJECT)]']
                                from_addr, subject = self.parse_email_headers(header_data)
                                
                                body_data = msg_data[latest_uid].get(b'BODY[TEXT]', b'')
                                body_preview = self.parse_email_body(body_data)
                                
                                # Queue event for debounced webhook
                                self.queue_event(username, from_addr, subject, body_preview)
                                
                                # Update last processed UID
                                last_uid = latest_uid
                        
                        # Re-enter IDLE mode
                        client.idle()
                        idle_start = time.time()
                    
                    # Periodic reconnect (every 15 min by default)
                    if time.time() - idle_start > self.reconnect_interval:
                        self.logger.info(f"🔄 {username}: Periodic reconnect")
                        client.idle_done()
                        client.noop()  # Keep-alive
                        client.idle()
                        idle_start = time.time()
                
            except KeyboardInterrupt:
                self.logger.info(f"⏹️  {username}: Stopped by user")
                break
                
            except Exception as e:
                self.logger.error(f"❌ {username}: Connection error: {e}")
                self.logger.info(f"🔁 {username}: Reconnecting in {backoff}s...")
                time.sleep(backoff)
                
                # Exponential backoff
                backoff = min(backoff * 2, max_backoff)
    
    def start(self):
        """Start monitoring all configured accounts"""
        accounts = self.config.get('accounts', [])
        
        if not accounts:
            self.logger.error("❌ No accounts configured")
            return
        
        self.logger.info(f"🚀 Starting IMAP IDLE listener for {len(accounts)} account(s)")
        
        # Start one thread per account
        threads = []
        for account in accounts:
            t = threading.Thread(
                target=self.listen_account,
                args=(account,),
                daemon=True,
                name=f"IMAP-{account['username']}"
            )
            t.start()
            threads.append(t)
        
        # Wait for all threads (blocks until Ctrl+C)
        try:
            for t in threads:
                t.join()
        except KeyboardInterrupt:
            self.logger.info("⏹️  Shutting down...")


def load_config(config_path=None):
    """Load configuration from file"""
    if config_path is None:
        # Default config locations
        default_paths = [
            Path.home() / '.openclaw' / 'imap-idle.json',
            Path.home() / '.config' / 'imap-idle' / 'config.json',
        ]
        
        for path in default_paths:
            if path.exists():
                config_path = path
                break
        
        if config_path is None:
            print("ERROR: No config file found", file=sys.stderr)
            print("Searched:", file=sys.stderr)
            for path in default_paths:
                print(f"  - {path}", file=sys.stderr)
            print("\nRun 'imap-idle-setup' to create config", file=sys.stderr)
            sys.exit(1)
    
    config_path = Path(config_path)
    if not config_path.exists():
        print(f"ERROR: Config file not found: {config_path}", file=sys.stderr)
        sys.exit(1)
    
    with open(config_path) as f:
        return json.load(f)


def main():
    import argparse
    
    parser = argparse.ArgumentParser(
        description='IMAP IDLE listener for OpenClaw webhook notifications'
    )
    parser.add_argument(
        '--config',
        help='Path to config file (default: ~/.openclaw/imap-idle.json)'
    )
    
    args = parser.parse_args()
    
    # Load config
    config = load_config(args.config)
    
    # Start listener
    listener = IMAPIdleListener(config)
    listener.start()


if __name__ == '__main__':
    main()

    def is_github_notification(self, from_addr, subject):
        """Check if email is a GitHub notification"""
        return ('github' in from_addr.lower() or 
                'noreply@github.com' in from_addr.lower())
    
    def parse_github_notification(self, from_addr, subject, body_preview):
        """Parse GitHub notification and extract mention/issue info"""
        # GitHub notification patterns
        if '@arkasha-ai' in subject or '@arkasha-ai' in body_preview:
            return "💬 GitHub: тебя упомянули!"
        elif 'review requested' in subject.lower():
            return "👀 GitHub: запросили review"
        elif 'assigned you' in subject.lower():
            return "📌 GitHub: назначили на задачу"
        elif 'mentioned you' in subject.lower():
            return "💬 GitHub: mention"
        else:
            return "🔔 GitHub notification"
