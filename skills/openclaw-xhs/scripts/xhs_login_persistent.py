#!/usr/bin/env python3
"""
One-time login to XHS using the persistent Chrome profile.
Opens a visible Chrome window for QR code scanning.
After login, cookies are saved both in Chrome profile AND in the JSON file.

Usage:
    python3 ~/.openclaw/skills/xhs/scripts/xhs_login_persistent.py
"""

import json
import os
import time
from datetime import datetime
from pathlib import Path

from selenium import webdriver
from selenium.webdriver.chrome.options import Options


def main():
    profile_dir = os.environ.get(
        "XHS_CHROME_PROFILE",
        os.path.expanduser("~/.openclaw/skills/xhs/chrome-data"),
    )
    os.makedirs(profile_dir, exist_ok=True)

    cookies_file = os.environ.get(
        "XHS_COOKIES_FILE",
        os.path.expanduser("~/.openclaw/credentials/xhs_cookies.json"),
    )

    chrome_path = os.environ.get(
        "CHROME_PATH",
        "/Applications/Google Chrome.app/Contents/MacOS/Google Chrome",
    )

    options = Options()
    options.binary_location = chrome_path
    # NOT headless — user needs to see the browser to scan QR
    options.add_argument("--disable-dev-shm-usage")
    options.add_argument(f"--user-data-dir={profile_dir}")
    options.add_argument("--window-size=1200,900")

    print("🌐 正在打开 Chrome（持久化 profile）...")
    driver = webdriver.Chrome(options=options)

    print("📱 跳转到小红书创作者中心...")
    driver.get("https://creator.xiaohongshu.com/")
    time.sleep(3)

    if "login" not in driver.current_url.lower():
        print("✅ 已登录！无需扫码。")
    else:
        print()
        print("=" * 50)
        print("  请在 Chrome 窗口中扫码登录小红书")
        print("  登录成功后回来按 Enter 键继续")
        print("=" * 50)
        input()

    # Verify login
    current_url = driver.current_url
    if "login" not in current_url.lower():
        print(f"✅ 登录成功！当前页面: {current_url}")

        # Export cookies to JSON file
        cookies = driver.get_cookies()
        data = {
            "version": "2.0",
            "saved_at": datetime.now().isoformat(),
            "domain": "xiaohongshu.com",
            "cookies": cookies,
        }
        Path(cookies_file).parent.mkdir(parents=True, exist_ok=True)
        Path(cookies_file).write_text(json.dumps(data, ensure_ascii=False, indent=2))
        print(f"   Cookie 文件已更新: {cookies_file} ({len(cookies)} cookies)")
        print(f"   Chrome profile: {profile_dir}")
        print()
        print("之后发布笔记不再需要扫码。")
    else:
        print("❌ 登录似乎未成功，请重新运行此脚本。")

    driver.quit()
    print("Chrome 已关闭。")


if __name__ == "__main__":
    main()
