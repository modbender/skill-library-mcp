#!/usr/bin/env python3
"""
Send Telegram notification for pet reminders
Uses subprocess to call OpenClaw CLI if available
"""

import sys
import subprocess
import json
from datetime import datetime

def send_telegram(chat_id, message):
    """Send message via Telegram"""
    try:
        # Try using telegram-send if installed
        result = subprocess.run(
            ['telegram-send', '--format', 'markdown', message],
            capture_output=True,
            text=True,
            timeout=10
        )
        
        if result.returncode == 0:
            print(f"[{datetime.utcnow().isoformat()}] ✅ Sent via telegram-send")
            return True
        else:
            print(f"[{datetime.utcnow().isoformat()}] ⚠️  telegram-send failed: {result.stderr}")
            
    except FileNotFoundError:
        print(f"[{datetime.utcnow().isoformat()}] telegram-send not installed")
    except Exception as e:
        print(f"[{datetime.utcnow().isoformat()}] Error: {e}")
    
    return False

def main():
    if len(sys.argv) < 2:
        print("Usage: telegram-notify.py <message>")
        sys.exit(1)
    
    message = sys.argv[1]
    chat_id = "322059822"
    
    print(f"[{datetime.utcnow().isoformat()}] Attempting to send notification...")
    print(f"Message: {message[:100]}...")
    
    if send_telegram(chat_id, message):
        sys.exit(0)
    else:
        print(f"[{datetime.utcnow().isoformat()}] ❌ All methods failed")
        sys.exit(1)

if __name__ == "__main__":
    main()
