#!/usr/bin/env python3
from __future__ import annotations

import argparse

from milaex_client import print_json, request_json


def main() -> None:
    ap = argparse.ArgumentParser(description="List available exchanges from Milaex")
    ap.add_argument("--no-rate-headers", action="store_true", help="Do not print rate limit headers to stderr")
    args = ap.parse_args()

    data = request_json("/api/v1/exchange", print_rate_headers=not args.no_rate_headers)
    print_json(data)


if __name__ == "__main__":
    main()
