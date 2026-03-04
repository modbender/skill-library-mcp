#!/usr/bin/env python3
"""
Joplin API Configuration Module

Required: JOPLIN_TOKEN
Optional: JOPLIN_BASE_URL (default: http://localhost:41184)
"""
import os
from dotenv import load_dotenv

load_dotenv()

JOPLIN_BASE_URL = os.getenv('JOPLIN_BASE_URL', 'http://localhost:41184')
JOPLIN_TOKEN = os.getenv('JOPLIN_TOKEN', '')


def get_base_url():
    """Get Joplin API base URL."""
    return JOPLIN_BASE_URL


def get_auth_params():
    """Get API authentication parameters."""
    return {'token': JOPLIN_TOKEN} if JOPLIN_TOKEN else {}


def check_config():
    """Check if configuration is complete."""
    if not JOPLIN_TOKEN:
        return False, "JOPLIN_TOKEN not set"
    return True, None