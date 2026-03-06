#!/usr/bin/env python3
"""Example wrapper for keyring-based credential place-order."""

import sys

from opend_cli import main

if __name__ == "__main__":
    args = ["--credential-method", "keyring", "place-order", *sys.argv[1:]]
    if len(args) == 3:
        args.extend(["--code", "HK.00700", "--price", "100", "--qty", "100", "--side", "BUY"])
    raise SystemExit(main(args))
