#!/usr/bin/env python3
"""
Configuration for etf-investor skill.
Centralized configuration to avoid path confusion.
"""
import os
import sys

# Add venv to path for yfinance import
VENV_PATH = os.path.expanduser("~/.clawdbot/etf_investor/venv")
if os.path.exists(VENV_PATH):
    sys.path.insert(0, os.path.join(VENV_PATH, "lib", f"python3.{sys.version_info.minor}", "site-packages"))

# Data directory
DATA_DIR = os.path.expanduser("~/.clawdbot/etf_investor")

# Positions file
POSITIONS_FILE = os.path.join(DATA_DIR, "positions.json")

# Alerts file
ALERTS_FILE = os.path.join(DATA_DIR, "alerts.json")

# Price cache file (optional, for storing latest prices)
PRICES_FILE = os.path.join(DATA_DIR, "prices.json")

# Ensure directory exists
os.makedirs(DATA_DIR, exist_ok=True)

# Price update interval in seconds (default: 300 = 5 minutes)
PRICE_UPDATE_INTERVAL = 300
