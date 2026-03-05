#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""Lightweight GitHub update checker for xuexitong-homework-submit.

Behavior:
- On each script run, fetch latest VERSION from GitHub main branch.
- If remote > local, print update hint to stdout.
- Fail open: never block core functionality if network/check fails.
"""

from __future__ import annotations

import os
import re
from pathlib import Path
from urllib.error import HTTPError, URLError
from urllib.request import Request, urlopen

DEFAULT_REPO = os.environ.get(
    "XUEXITONG_UPDATE_REPO", "smallwhiteman/xuexitong-homework-submit-skill"
)


def _parse_version(v: str) -> tuple[int, int, int]:
    nums = [int(x) for x in re.findall(r"\d+", (v or "")[:64])[:3]]
    while len(nums) < 3:
        nums.append(0)
    return tuple(nums[:3])


def _read_local_version() -> str:
    root = Path(__file__).resolve().parents[1]
    version_file = root / "VERSION"
    if version_file.exists():
        text = version_file.read_text(encoding="utf-8", errors="ignore").strip()
        if text:
            return text

    # fallback: parse frontmatter version from SKILL.md
    skill_file = root / "SKILL.md"
    if skill_file.exists():
        text = skill_file.read_text(encoding="utf-8", errors="ignore")
        m = re.search(r"(?im)^version\s*:\s*['\"]?([0-9]+(?:\.[0-9]+){0,2})['\"]?\s*$", text)
        if m:
            return m.group(1)

    return "0.0.0"


def _fetch_remote_version(repo: str, timeout: float = 2.5) -> str | None:
    url = f"https://raw.githubusercontent.com/{repo}/main/VERSION"
    req = Request(
        url,
        headers={
            "User-Agent": "xuexitong-homework-submit-update-checker/1.0",
            "Cache-Control": "no-cache",
            "Pragma": "no-cache",
        },
    )
    try:
        with urlopen(req, timeout=timeout) as resp:
            if resp.status != 200:
                return None
            data = resp.read().decode("utf-8", errors="ignore").strip()
            if not data:
                return None
            # keep first token only
            return data.split()[0]
    except (HTTPError, URLError, TimeoutError, OSError):
        return None


def maybe_check_for_update(*, repo: str = DEFAULT_REPO) -> None:
    """Check GitHub for updates and print notice when newer version exists.

    Opt-out:
      XUEXITONG_SKIP_UPDATE_CHECK=1
    """
    if os.environ.get("XUEXITONG_SKIP_UPDATE_CHECK", "").lower() in {"1", "true", "yes", "on"}:
        return

    local_v = _read_local_version()
    remote_v = _fetch_remote_version(repo)
    if not remote_v:
        return

    if _parse_version(remote_v) > _parse_version(local_v):
        print(
            f"[xuexitong-homework-submit] 新版本可用：{remote_v}（当前：{local_v}）\n"
            f"[xuexitong-homework-submit] 更新方式：clawhub update xuexitong-homework-submit\n"
            f"[xuexitong-homework-submit] 源码仓库：https://github.com/{repo}"
        )
