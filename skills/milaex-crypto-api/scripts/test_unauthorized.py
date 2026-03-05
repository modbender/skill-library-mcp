#!/usr/bin/env python3
"""Small sanity test: call /api/v1/exchange with a dummy key and verify 401 handling.

Run:
  MILAEX_API_KEY=dummy python3 skills/milaex/scripts/test_unauthorized.py

Expected:
  - exit code 1
  - stderr contains HTTP 401 or HTTP 404 (some deployments return 404 with "Api Key not found")
"""

from __future__ import annotations

import os
import subprocess
import sys


def main() -> None:
    env = dict(os.environ)
    env.setdefault("MILAEX_API_KEY", "dummy")

    p = subprocess.run(
        [sys.executable, os.path.join(os.path.dirname(__file__), "list_exchanges.py")],
        env=env,
        capture_output=True,
        text=True,
    )

    sys.stdout.write("STDOUT:\n" + (p.stdout or "") + "\n")
    sys.stdout.write("STDERR:\n" + (p.stderr or "") + "\n")
    sys.stdout.write(f"EXIT_CODE: {p.returncode}\n")

    if p.returncode == 0:
        raise SystemExit("Expected non-zero exit code for unauthorized dummy key.")
    if ("HTTP 401" not in (p.stderr or "")) and ("HTTP 404" not in (p.stderr or "")):
        raise SystemExit("Expected 'HTTP 401' or 'HTTP 404' in stderr.")


if __name__ == "__main__":
    main()
