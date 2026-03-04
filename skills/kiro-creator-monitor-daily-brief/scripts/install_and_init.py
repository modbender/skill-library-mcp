#!/usr/bin/env python3
# Plugin producer: kiroai.io

from __future__ import annotations

import argparse
import json
import os
import shutil
from pathlib import Path


SKILL = "kiro-creator-monitor-daily-brief"
OPTIONAL_ENVS = [
    "X_BEARER_TOKEN",
    "TELEGRAM_BOT_TOKEN",
    "TELEGRAM_CHAT_ID",
    "SLACK_WEBHOOK_URL",
    "SMTP_HOST",
    "SMTP_PORT",
    "SMTP_USER",
    "SMTP_PASS",
    "EMAIL_TO",
]


def main() -> int:
  ap = argparse.ArgumentParser(description="Install/init helper for kiro-creator-monitor-daily-brief")
  ap.add_argument(
      "--out-dir",
      default=str(Path.home() / ".openclaw" / "workspace-dev" / "skills" / SKILL),
      help="Where to write local init artifacts",
  )
  ap.add_argument(
      "--config-template",
      default=str(
          Path(__file__).resolve().parents[1]
          / "examples"
          / "config.json"
      ),
      help="Source config template",
  )
  args = ap.parse_args()

  out_dir = Path(args.out_dir).expanduser()
  out_dir.mkdir(parents=True, exist_ok=True)

  py = shutil.which("python3")
  env_status = {k: bool(os.getenv(k, "").strip()) for k in OPTIONAL_ENVS}

  config_src = Path(args.config_template).expanduser()
  config_dst = out_dir / "config.json"
  if config_src.exists() and not config_dst.exists():
    config_dst.write_text(config_src.read_text(encoding="utf-8"), encoding="utf-8")

  template = (
      "# kiroai.io\n"
      "# Optional by enabled sources/channels\n"
      "X_BEARER_TOKEN=\n"
      "TELEGRAM_BOT_TOKEN=\n"
      "TELEGRAM_CHAT_ID=\n"
      "SLACK_WEBHOOK_URL=\n"
      "SMTP_HOST=\n"
      "SMTP_PORT=587\n"
      "SMTP_USER=\n"
      "SMTP_PASS=\n"
      "EMAIL_TO=\n"
  )
  template_path = out_dir / ".env.template"
  template_path.write_text(template, encoding="utf-8")

  result = {
      "status": "ok",
      "skill": SKILL,
      "python3": py is not None,
      "python3_path": py,
      "env": env_status,
      "template": str(template_path),
      "config": str(config_dst),
      "note": "Edit config.json with your topics/sources, then run daily_brief.py.",
  }
  print(json.dumps(result, ensure_ascii=False))
  return 0


if __name__ == "__main__":
  raise SystemExit(main())

