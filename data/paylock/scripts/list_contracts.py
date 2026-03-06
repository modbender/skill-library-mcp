#!/usr/bin/env python3
from __future__ import annotations

import argparse

from paylock_api import PayLockClient, print_json, run_with_error_handling


def main() -> None:
    parser = argparse.ArgumentParser(description="List PayLock contracts")
    parser.add_argument("--api", default=None, help="Override API base URL")
    args = parser.parse_args()

    client = PayLockClient(base_url=args.api)
    print_json(client.request("GET", "/contracts"))


if __name__ == "__main__":
    run_with_error_handling(main)
