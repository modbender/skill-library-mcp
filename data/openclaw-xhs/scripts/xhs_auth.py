#!/usr/bin/env python3
"""
XHS Cookie Authentication — opens Chrome to Xiaohongshu creator center,
waits for user to scan QR code, then saves cookies.

Usage:
    uv run --project $XHS_TOOLKIT_DIR xhs_auth.py [--timeout 300] [--force]
"""

import argparse
import asyncio
import json
import os
import sys
from datetime import datetime
from pathlib import Path


def get_config():
    toolkit_dir = os.environ.get("XHS_TOOLKIT_DIR", os.path.expanduser("~/.openclaw/skills/xhs/xhs-toolkit"))
    sys.path.insert(0, toolkit_dir)
    from src.core.config import XHSConfig

    cookies_file = os.environ.get(
        "XHS_COOKIES_FILE",
        os.path.expanduser("~/.openclaw/credentials/xhs_cookies.json"),
    )
    os.environ.setdefault("COOKIES_FILE", cookies_file)
    os.environ.setdefault(
        "CHROME_PATH",
        "/Applications/Google Chrome.app/Contents/MacOS/Google Chrome",
    )
    return XHSConfig()


def main():
    parser = argparse.ArgumentParser(description="XHS Cookie Authentication")
    parser.add_argument("--timeout", type=int, default=300, help="Login timeout in seconds (default 300)")
    parser.add_argument("--force", action="store_true", help="Force re-login even if cookies exist")
    args = parser.parse_args()

    cookies_file = os.environ.get(
        "XHS_COOKIES_FILE",
        os.path.expanduser("~/.openclaw/credentials/xhs_cookies.json"),
    )

    if not args.force and Path(cookies_file).exists():
        try:
            data = json.loads(Path(cookies_file).read_text())
            cookies = data.get("cookies", data) if isinstance(data, dict) else data
            if cookies:
                print(json.dumps({
                    "status": "already_logged_in",
                    "message": "Cookie 文件已存在。使用 --force 强制重新登录。",
                    "cookies_file": cookies_file,
                    "cookie_count": len(cookies),
                }))
                return
        except (json.JSONDecodeError, KeyError):
            pass

    try:
        config = get_config()
        from src.auth.cookie_manager import CookieManager

        cm = CookieManager(config)

        print(json.dumps({
            "status": "waiting_for_login",
            "message": "Chrome 已打开小红书创作者中心登录页，请到 Mac 桌面扫码登录。",
            "timeout": args.timeout,
        }))
        sys.stdout.flush()

        success = cm.save_cookies_auto(timeout_seconds=args.timeout)

        if success:
            # Copy cookies to our target location if CookieManager saved elsewhere
            cm_cookies_path = Path(config.cookies_file)
            target_path = Path(cookies_file)
            if cm_cookies_path.resolve() != target_path.resolve() and cm_cookies_path.exists():
                target_path.parent.mkdir(parents=True, exist_ok=True)
                import shutil
                shutil.copy2(cm_cookies_path, target_path)

            print(json.dumps({
                "status": "success",
                "message": "登录成功！Cookie 已保存。",
                "cookies_file": cookies_file,
            }))
        else:
            print(json.dumps({
                "status": "failed",
                "message": "登录超时或失败，请重试。",
            }))
            sys.exit(1)

    except Exception as e:
        print(json.dumps({
            "status": "error",
            "message": f"登录过程出错: {str(e)}",
            "error": str(e),
        }))
        sys.exit(1)


if __name__ == "__main__":
    main()
