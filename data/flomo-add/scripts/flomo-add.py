#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

import requests


def parse_kv_config(path: Path) -> dict[str, str]:
    if not path.exists():
        raise FileNotFoundError(f"配置文件不存在: {path}")

    config: dict[str, str] = {}
    for raw_line in path.read_text(encoding="utf-8").splitlines():
        line = raw_line.strip()
        if not line or line.startswith("#"):
            continue
        if "=" not in line:
            continue
        key, value = line.split("=", 1)
        config[key.strip()] = value.strip()
    return config


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="通过 requests 向 flomo 新增一条 memo")
    parser.add_argument("--content", required=True, help="memo 内容")
    parser.add_argument(
        "--config",
        default=".flomo.config",
        help="配置文件路径，默认读取当前目录下 .flomo.config",
    )
    parser.add_argument("--url", help="临时覆盖配置中的 webhook URL")
    parser.add_argument(
        "--dry-run",
        action="store_true",
        help="只打印将发送的请求信息，不发送请求",
    )
    return parser


def main() -> int:
    args = build_parser().parse_args()
    config_path = Path(args.config).expanduser().resolve()

    try:
        config = parse_kv_config(config_path)
    except FileNotFoundError as exc:
        print(str(exc), file=sys.stderr)
        print("请先在当前目录创建 .flomo.config 并配置 url=<webhook_url>，格式见 skills/flomo-add/SKILL.md", file=sys.stderr)
        return 2

    url = (args.url or config.get("url", "")).strip()
    if not url:
        print("缺少 flomo webhook url。请在 .flomo.config 中设置 url=...", file=sys.stderr)
        return 2

    payload = {"content": args.content}
    headers = {"Content-Type": "application/json"}

    if args.dry_run:
        print("即将发送请求：")
        print(f"POST {url}")
        print(f"Headers: {json.dumps(headers, ensure_ascii=False)}")
        print(f"Body: {json.dumps(payload, ensure_ascii=False)}")
        return 0

    try:
        response = requests.post(url, json=payload, headers=headers, timeout=15)
        response.raise_for_status()
    except requests.RequestException as exc:
        print(f"请求失败: {exc}", file=sys.stderr)
        if getattr(exc, "response", None) is not None and exc.response is not None:
            body = exc.response.text.strip()
            if body:
                print(body, file=sys.stderr)
        return 1

    if response.text.strip():
        print(response.text.strip())
    else:
        print("请求已发送（无响应体）")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
