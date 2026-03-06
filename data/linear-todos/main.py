#!/usr/bin/env python3
"""
Linear Todos - Main entry point

A powerful todo management system built on Linear with smart date parsing.

Usage:
    python main.py --help
    python main.py create "Task title" --when day
    python main.py list
    python main.py done ISSUE-123
    python main.py review
"""

import sys
from pathlib import Path

# Add src directory to Python path
src_dir = Path(__file__).parent / "src"
if str(src_dir) not in sys.path:
    sys.path.insert(0, str(src_dir))

from linear_todos.cli import main

if __name__ == "__main__":
    main()
