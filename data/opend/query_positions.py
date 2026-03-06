#!/usr/bin/env python3
"""Backward-compatible wrapper for positions query."""

import argparse

from opend_cli import main


def _legacy_args():
    parser = argparse.ArgumentParser()
    parser.add_argument('--method', default='openclaw', choices=['openclaw', 'secret-ref', 'env', 'keyring', 'config'])
    return parser.parse_args()


if __name__ == "__main__":
    args = _legacy_args()
    raise SystemExit(main(["--credential-method", args.method, "positions"]))
