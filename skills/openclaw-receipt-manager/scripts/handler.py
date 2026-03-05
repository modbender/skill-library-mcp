#!/usr/bin/env python3
"""
Receipt skill handler for OpenClaw.
Receives extracted receipt info and saves to database.
"""

import sys
import json
import subprocess
import re
from pathlib import Path
import shlex

SCRIPT_DIR = Path(__file__).parent

def sanitize_string(s, max_len=200):
    """Sanitize string input to prevent injection."""
    if not s:
        return ''
    # Remove any shell metacharacters
    s = re.sub(r'[;&|`$<>]', '', str(s))
    return s[:max_len]

def validate_path(p):
    """Validate and sanitize file path."""
    if not p:
        return ''
    # Only allow alphanumeric, dash, underscore, dot, slash
    if not re.match(r'^[\w\-./]+$', p):
        return ''
    # Prevent path traversal
    if '..' in p:
        return ''
    return p

def handle(data):
    """Handle receipt data from OpenClaw."""
    required = ['vendor', 'total']
    for field in required:
        if field not in data:
            return {"ok": False, "error": f"missing {field}"}

    # Validate and sanitize inputs
    vendor = sanitize_string(data.get('vendor', ''), 100)
    if not vendor:
        return {"ok": False, "error": "invalid vendor"}
    
    try:
        total = float(data.get('total', 0))
        if total < 0 or total > 1000000:
            return {"ok": False, "error": "invalid total amount"}
    except (ValueError, TypeError):
        return {"ok": False, "error": "total must be a number"}

    date = sanitize_string(data.get('date', ''), 20)
    currency = sanitize_string(data.get('currency', 'CAD'), 10)
    category = sanitize_string(data.get('category', 'other'), 50)
    
    # Validate image path if provided
    image_path = validate_path(data.get('image', ''))
    
    text = sanitize_string(data.get('text', ''), 1000)

    # Build command with sanitized args
    cmd = [
        str(SCRIPT_DIR / "receipt_db.py"),
        "add",
        "--vendor", vendor,
        "--total", str(total),
    ]
    
    if date:
        cmd.extend(["--date", date])
    if currency:
        cmd.extend(["--currency", currency])
    if category:
        cmd.extend(["--category", category])
    if image_path:
        cmd.extend(["--image", image_path])
    if text:
        cmd.extend(["--text", text])

    try:
        result = subprocess.run(cmd, capture_output=True, text=True, timeout=30)
        if result.returncode == 0:
            return {"ok": True, "message": f"✅ 已保存收据: {vendor} ${total} {currency}"}
        else:
            return {"ok": False, "error": result.stderr[:200]}
    except subprocess.TimeoutExpired:
        return {"ok": False, "error": "timeout"}
    except Exception as e:
        return {"ok": False, "error": str(e)[:100]}

if __name__ == '__main__':
    try:
        data = json.load(sys.stdin)
        result = handle(data)
        print(json.dumps(result))
    except json.JSONDecodeError:
        print(json.dumps({"ok": False, "error": "invalid json input"}))
    except Exception as e:
        print(json.dumps({"ok": False, "error": str(e)[:100]}))
