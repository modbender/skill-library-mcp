#!/usr/bin/env python3
"""
Check XHS login status by validating saved cookies.

Usage:
    uv run --project $XHS_TOOLKIT_DIR xhs_status.py
"""

import json
import os
import sys
from datetime import datetime, timezone
from pathlib import Path


def main():
    cookies_file = os.environ.get(
        "XHS_COOKIES_FILE",
        os.path.expanduser("~/.openclaw/credentials/xhs_cookies.json"),
    )

    if not Path(cookies_file).exists():
        print(json.dumps({
            "status": "not_logged_in",
            "message": "未找到 Cookie 文件，请先登录小红书。",
            "cookies_file": cookies_file,
            "logged_in": False,
        }))
        return

    try:
        data = json.loads(Path(cookies_file).read_text())
    except json.JSONDecodeError:
        print(json.dumps({
            "status": "invalid",
            "message": "Cookie 文件格式错误，请重新登录。",
            "logged_in": False,
        }))
        sys.exit(1)

    # Support v1 (list) and v2 (dict with metadata)
    if isinstance(data, dict):
        cookies = data.get("cookies", [])
        saved_at = data.get("saved_at", "unknown")
        version = data.get("version", "1.0")
    elif isinstance(data, list):
        cookies = data
        saved_at = "unknown"
        version = "1.0"
    else:
        print(json.dumps({
            "status": "invalid",
            "message": "Cookie 文件格式不支持。",
            "logged_in": False,
        }))
        sys.exit(1)

    if not cookies:
        print(json.dumps({
            "status": "empty",
            "message": "Cookie 文件为空，请重新登录。",
            "logged_in": False,
        }))
        return

    # Check critical cookies
    critical_names = {"web_session", "a1", "gid", "webId"}
    found_critical = set()
    expired_cookies = []
    now_ts = datetime.now(timezone.utc).timestamp()

    for cookie in cookies:
        name = cookie.get("name", "")
        if name in critical_names:
            found_critical.add(name)
        expiry = cookie.get("expiry") or cookie.get("expirationDate")
        if expiry and float(expiry) < now_ts:
            expired_cookies.append(name)

    missing_critical = critical_names - found_critical
    has_web_session = "web_session" in found_critical
    is_valid = has_web_session and len(missing_critical) <= 2 and "web_session" not in expired_cookies

    if is_valid:
        status = "valid"
        message = "登录状态正常，Cookie 有效。"
    elif expired_cookies:
        status = "expired"
        message = f"Cookie 已过期（{', '.join(expired_cookies)}），请重新登录。"
    else:
        status = "incomplete"
        message = f"缺少关键 Cookie（{', '.join(missing_critical)}），请重新登录。"

    print(json.dumps({
        "status": status,
        "message": message,
        "logged_in": is_valid,
        "cookies_file": cookies_file,
        "cookie_count": len(cookies),
        "saved_at": saved_at,
        "version": version,
        "critical_cookies_found": sorted(found_critical),
        "critical_cookies_missing": sorted(missing_critical),
        "expired_cookies": expired_cookies,
    }))


if __name__ == "__main__":
    main()
