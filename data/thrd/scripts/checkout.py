#!/usr/bin/env python3
import requests
import json
import sys
import os

# Configuration from memory/environment
API_KEY = os.environ.get("THRD_API_KEY")

def create_checkout(plan):
    if not API_KEY:
        print(json.dumps({"ok": False, "error": "THRD_API_KEY environment variable not set."}))
        return

    url = "https://api.thrd.email/v1/billing/checkout/self"
    headers = {
        "Authorization": f"Bearer {API_KEY}",
        "Content-Type": "application/json"
    }
    payload = {"plan": plan}
    
    try:
        response = requests.post(url, json=payload, headers=headers, timeout=30)
        response.raise_for_status()
        data = response.json()
        print(json.dumps(data, indent=2))
    except Exception as e:
        print(json.dumps({"ok": False, "error": str(e)}))
        sys.exit(1)

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: python3 checkout.py <sandbox|limited|verified>")
        sys.exit(1)
    
    plan_name = sys.argv[1].lower()
    if plan_name not in {"sandbox", "limited", "verified"}:
        print(json.dumps({"ok": False, "error": "invalid_plan", "allowed": ["sandbox", "limited", "verified"]}))
        sys.exit(1)
    create_checkout(plan_name)
