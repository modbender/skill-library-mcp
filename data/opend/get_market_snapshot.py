#!/usr/bin/env python3
"""Backward-compatible wrapper for snapshot query."""

import sys

from opend_cli import main

if __name__ == "__main__":
    argv = ["snapshot", *sys.argv[1:]]
    if len(argv) == 1:
        argv.extend(["--codes", "HK.00700,US.AAPL"])
    raise SystemExit(main(argv))
