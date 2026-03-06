#!/usr/bin/env python3
import json
import os
import sys
from datetime import datetime, timezone, timedelta

if len(sys.argv) != 2 or sys.argv[1] not in {"on", "off"}:
    print("Usage: set_phone_receipt_state.py on|off")
    sys.exit(2)

state = sys.argv[1] == "on"
root = os.path.abspath(os.path.join(os.path.dirname(__file__), "../../../"))
path = os.path.join(root, "memory", "phone-receipt-state.json")
os.makedirs(os.path.dirname(path), exist_ok=True)

now = datetime.now(timezone(timedelta(hours=8))).isoformat(timespec="seconds")
obj = {
    "enabled": state,
    "updatedAt": now,
    "keywords": {"on": "phone-receipt=on", "off": "phone-receipt=off"},
    "policy": {"onComplete": False, "onFailure": True, "onUrgent": True},
}

with open(path, "w", encoding="utf-8") as f:
    json.dump(obj, f, ensure_ascii=False, indent=2)

print(f"[OK] phone receipt {'enabled' if state else 'disabled'}: {path}")
