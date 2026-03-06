#!/usr/bin/env python3
"""Ensure ~/.ssh/config contains a managed ssh-op block.

Reads:
  - skill-local config.env (SSH_OP_HOSTS_FILE)
  - hosts.conf (ssh config snippet)

Writes:
  - ~/.ssh/config (creates if missing)

The managed block is delimited by markers so it can be updated idempotently.
"""

from __future__ import annotations

import re
from pathlib import Path

BEGIN = "# BEGIN ssh-op (managed)"
END = "# END ssh-op (managed)"


def read_env(path: Path) -> dict[str, str]:
    out: dict[str, str] = {}
    if not path.exists():
        return out
    for raw in path.read_text(encoding="utf-8").splitlines():
        line = raw.strip()
        if not line or line.startswith("#") or "=" not in line:
            continue
        k, v = line.split("=", 1)
        k = k.strip()
        v = v.strip().strip('"').strip("'")
        out[k] = v
    return out


def main() -> int:
    skill_dir = Path(__file__).resolve().parent.parent
    cfg = read_env(skill_dir / "config.env")
    hosts_file = cfg.get("SSH_OP_HOSTS_FILE", "hosts.conf")
    snippet_path = (skill_dir / hosts_file).resolve()

    if not snippet_path.exists():
        raise SystemExit(f"hosts snippet not found: {snippet_path}")

    snippet = snippet_path.read_text(encoding="utf-8").rstrip() + "\n"

    ssh_dir = Path.home() / ".ssh"
    ssh_dir.mkdir(parents=True, exist_ok=True)
    config_path = ssh_dir / "config"

    existing = ""
    if config_path.exists():
        existing = config_path.read_text(encoding="utf-8")

    block = f"{BEGIN}\n{snippet}{END}\n"

    pattern = re.compile(rf"(?ms)^\Q{BEGIN}\E\n.*?^\Q{END}\E\n")
    if pattern.search(existing):
        updated = pattern.sub(block, existing)
    else:
        updated = existing
        if updated and not updated.endswith("\n"):
            updated += "\n"
        updated += "\n" + block

    config_path.write_text(updated, encoding="utf-8")
    print(str(config_path))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
