#!/usr/bin/env python3
"""Search Airbnb listings from the command line.

Run directly (no install needed):
    uv run --with requests scripts/airbnb-search.py "Denver, CO" --checkin 2025-06-01 --checkout 2025-06-03

Source code: ../airbnb_search/
"""

import os
import sys

# Add repo root to path so we can import the package source directly
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from airbnb_search.cli import main  # noqa: E402

if __name__ == "__main__":
    main()
