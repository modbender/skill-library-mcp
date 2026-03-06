#!/usr/bin/env python3
# Plugin producer: kiroai.io

from __future__ import annotations

import argparse
import json
import os
import shutil
from pathlib import Path


SKILL = "kiro-x-hot-publisher"
SEARCH_ENVS = ["X_BEARER_TOKEN"]
PUBLISH_ENVS = ["X_API_KEY", "X_API_SECRET", "X_ACCESS_TOKEN", "X_ACCESS_TOKEN_SECRET"]


def main() -> int:
  ap = argparse.ArgumentParser(description="Install/init helper for kiro-x-hot-publisher")
  ap.add_argument(
      "--out-dir",
      default=str(Path.home() / ".openclaw" / "workspace-dev" / "skills" / SKILL),
      help="Where to write local init artifacts",
  )
  args = ap.parse_args()

  out_dir = Path(args.out_dir).expanduser()
  out_dir.mkdir(parents=True, exist_ok=True)

  py = shutil.which("python3")
  search_status = {k: bool(os.getenv(k, "").strip()) for k in SEARCH_ENVS}
  publish_status = {k: bool(os.getenv(k, "").strip()) for k in PUBLISH_ENVS}

  template = (
      "# kiroai.io\n"
      "# Required for search\n"
      "X_BEARER_TOKEN=\n\n"
      "# Required for posting (--post)\n"
      "X_API_KEY=\n"
      "X_API_SECRET=\n"
      "X_ACCESS_TOKEN=\n"
      "X_ACCESS_TOKEN_SECRET=\n"
  )
  template_path = out_dir / ".env.template"
  template_path.write_text(template, encoding="utf-8")

  result = {
      "status": "ok",
      "skill": SKILL,
      "python3": py is not None,
      "python3_path": py,
      "env": {"search": search_status, "publish": publish_status},
      "template": str(template_path),
      "note": "Search-only mode needs only X_BEARER_TOKEN. Posting needs OAuth 1.0a keys.",
  }
  print(json.dumps(result, ensure_ascii=False))
  return 0


if __name__ == "__main__":
  raise SystemExit(main())

