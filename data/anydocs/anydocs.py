#!/usr/bin/env python3
"""anydocs - Generic documentation indexing and search.

A flexible tool for indexing and searching ANY documentation site.
"""

import sys
import os

# Add lib directory to path
sys.path.insert(0, os.path.dirname(__file__))

from cli import cli

if __name__ == "__main__":
    cli()
