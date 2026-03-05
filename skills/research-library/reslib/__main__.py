#!/usr/bin/env python3
"""
Entry point for running reslib as a module.

Usage:
    python -m reslib [command] [options]
"""

from reslib.cli import cli

if __name__ == "__main__":
    cli()
