#!/usr/bin/env python3
"""Fastmail Suite wrapper.

Provides a single entrypoint for mail, contacts, calendar, and suite helpers.

Examples:
  python3 skills/fastmail-suite/scripts/fastmail.py mail inbox --limit 20
  python3 skills/fastmail-suite/scripts/fastmail.py contacts search "gazelle"
  python3 skills/fastmail-suite/scripts/fastmail.py calendar upcoming --days 7
  python3 skills/fastmail-suite/scripts/fastmail.py suite status

This wrapper delegates to the underlying scripts.
"""

from __future__ import annotations

import os
import subprocess
import sys
from pathlib import Path


HERE = Path(__file__).resolve().parent


def _run(script: str, argv: list[str]) -> int:
    path = str(HERE / script)
    cmd = [sys.executable, path, *argv]
    # Preserve env and let the child handle safety checks.
    return subprocess.call(cmd, env=os.environ.copy())


def main() -> None:
    if len(sys.argv) < 2 or sys.argv[1] in ("-h", "--help"):
        print(__doc__)
        sys.exit(0)

    # Allow passing child-script flags before the area, e.g.:
    #   fastmail.py --raw --json contacts get <id>
    argv = sys.argv[1:]
    passthru: list[str] = []
    while argv and argv[0].startswith("-") and argv[0] not in ("-h", "--help"):
        passthru.append(argv.pop(0))

    if not argv:
        print(__doc__)
        sys.exit(2)

    area = argv[0]
    rest = passthru + argv[1:]

    if area == "mail":
        rc = _run("mail.py", rest)
    elif area == "contacts":
        rc = _run("contacts.py", rest)
    elif area == "calendar":
        rc = _run("calendar_caldav.py", rest)
    elif area == "suite":
        rc = _run("suite.py", rest)
    else:
        print(f"Unknown area: {area}\n")
        print(__doc__)
        rc = 2

    raise SystemExit(rc)


if __name__ == "__main__":
    main()
