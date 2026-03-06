#!/usr/bin/env python
"""微信 MCP 测试工具"""

import sys
import os

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from server import send_message_to_current


def test_send(message):
    print(f"\n=== Test: Send Message ===")
    print(f"Message: {message}")
    
    success, err = send_message_to_current(message)
    
    if success:
        print(f"[OK] Sent: {message}")
    else:
        print(f"[ERROR] {err}")
    
    return success, err


def main():
    import argparse
    
    parser = argparse.ArgumentParser(description="WeChat MCP Test")
    parser.add_argument("action", choices=["send"], help="Action")
    parser.add_argument("--message", "-m", help="Message")
    
    args = parser.parse_args()
    
    if args.action == "send":
        if not args.message:
            print("Error: Need --message")
            return
        test_send(args.message)


if __name__ == "__main__":
    main()
