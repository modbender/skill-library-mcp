#!/usr/bin/env python3
"""Shared utilities for email-resend skill."""
import os
import re
import yaml

PREFERENCES_FILE = os.path.expanduser("~/.openclaw/workspace/memory/email-preferences.md")


def load_preferences():
    """Load preferences from memory/email-preferences.md
    
    Returns dict with keys:
    - from_email: sender email address
    - from_name: sender display name
    - telegram: dict with 'target' and 'threadId'
    """
    if not os.path.exists(PREFERENCES_FILE):
        return None
    
    with open(PREFERENCES_FILE, 'r') as f:
        content = f.read()
    
    # Extract YAML frontmatter
    match = re.match(r'^---\n(.*?)\n---', content, re.DOTALL)
    if not match:
        return None
    
    try:
        prefs = yaml.safe_load(match.group(1))
        return prefs
    except Exception:
        return None


def get_from_email():
    """Get from_email, checking env var first, then preferences file."""
    # Check env var first (allows override)
    env_email = os.environ.get("DEFAULT_FROM_EMAIL")
    if env_email:
        return env_email
    
    # Fall back to preferences file
    prefs = load_preferences()
    if prefs and prefs.get('from_email'):
        return prefs['from_email']
    
    return None


def get_from_name():
    """Get from_name, checking env var first, then preferences file."""
    # Check env var first (allows override)
    env_name = os.environ.get("DEFAULT_FROM_NAME")
    if env_name:
        return env_name
    
    # Fall back to preferences file
    prefs = load_preferences()
    if prefs and prefs.get('from_name'):
        return prefs['from_name']
    
    return "User"


def get_telegram_target():
    """Get telegram target from preferences file."""
    prefs = load_preferences()
    if prefs and prefs.get('telegram'):
        return prefs['telegram'].get('target')
    return None


def get_telegram_thread_id():
    """Get telegram threadId from preferences file."""
    prefs = load_preferences()
    if prefs and prefs.get('telegram'):
        return prefs['telegram'].get('threadId')
    return None
