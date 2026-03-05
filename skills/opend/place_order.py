#!/usr/bin/env python3
"""Backward-compatible wrapper for place-order."""

import argparse

from opend_cli import main


def _legacy_args():
    parser = argparse.ArgumentParser()
    parser.add_argument('--method', default='openclaw', choices=['openclaw', 'secret-ref', 'env', 'keyring', 'config'])
    parser.add_argument('--code', default='HK.00700')
    parser.add_argument('--price', default=100.0, type=float)
    parser.add_argument('--qty', default=100.0, type=float)
    parser.add_argument('--side', default='BUY', choices=['BUY', 'SELL'])
    return parser.parse_args()


if __name__ == "__main__":
    args = _legacy_args()
    raise SystemExit(
        main(
            [
                "--credential-method",
                args.method,
                "place-order",
                "--code",
                args.code,
                "--price",
                str(args.price),
                "--qty",
                str(args.qty),
                "--side",
                args.side,
            ]
        )
    )
