#!/usr/bin/env python3
"""CLI helper to read secrets from keychain for bash scripts.

Usage: python3 get_secret.py <service-name> [--account ACCOUNT]

Note: This works from terminal and when Python IS the LaunchAgent process.
It HANGS when spawned as a subprocess from a bash LaunchAgent on macOS Tahoe.
For bash LaunchAgents, use Group B file bridge instead.
"""
import sys
import os

# Ensure local imports work regardless of how we're invoked
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from keychain_helper import get_secret

if len(sys.argv) < 2:
    print("Usage: python3 get_secret.py <service-name> [--account ACCOUNT]", file=sys.stderr)
    sys.exit(1)

service = sys.argv[1]
account = None
if "--account" in sys.argv:
    idx = sys.argv.index("--account")
    if idx + 1 < len(sys.argv):
        account = sys.argv[idx + 1]

value = get_secret(service, account=account)
if value:
    print(value, end='')
else:
    sys.exit(1)
