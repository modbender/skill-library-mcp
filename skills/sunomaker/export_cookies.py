#!/usr/bin/env python3
"""
Suno Cookie 导出工具（在本地有 GUI 的电脑上运行）

用途:
    在你自己的电脑（macOS/Windows/Linux 桌面）上运行此脚本，
    它会打开一个 Chrome 浏览器窗口，你手动登录 Suno.com，
    登录成功后脚本自动导出 Cookie 为 JSON 文件。
    然后你把这个文件上传到云服务器，用 --import-cookies 导入即可。

用法:
    python3 export_cookies.py
    python3 export_cookies.py --output /path/to/suno_cookies.json
    python3 export_cookies.py --timeout 300

流程:
    1. 启动 Chrome 浏览器（GUI 模式）
    2. 自动打开 suno.com/sign-in 页面
    3. 你手动登录（Google 登录 / 邮箱登录 / 任何方式）
    4. 脚本检测到登录成功后自动导出 Cookie
    5. 将 Cookie 保存为 JSON 文件
    6. 你把文件上传到服务器: scp <导出的Cookie文件> user@server:/root/suno_cookie/suno_cookies.json

前置条件:
    - pip install playwright && playwright install
    - 系统有 Google Chrome 浏览器（或 Chromium）
"""

import argparse
import json
import os
import sys
import time
from pathlib import Path
from urllib.parse import urlparse

try:
    from playwright.sync_api import sync_playwright
except ImportError:
    print("❌ 缺少 playwright 库，请先安装：", flush=True)
    print("   pip install playwright && playwright install", flush=True)
    sys.exit(1)


DEFAULT_OUTPUT = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "tmp", "suno_cookies.json")
DEFAULT_TIMEOUT = 180  # 3 分钟


def export_cookies(output_file: str, timeout: int):
    """
    打开浏览器让用户手动登录 Suno，登录成功后导出 Cookie
    """
    print("=" * 60, flush=True)
    print("🍪 Suno Cookie 导出工具", flush=True)
    print("=" * 60, flush=True)
    print("", flush=True)
    print("📋 操作步骤：", flush=True)
    print("   1. 马上会弹出一个 Chrome 浏览器窗口", flush=True)
    print("   2. 在浏览器中登录你的 Suno 账号（任何方式都行）", flush=True)
    print("   3. 登录成功后脚本会自动检测并导出 Cookie", flush=True)
    print(f"   4. Cookie 将保存到: {output_file}", flush=True)
    print(f"   5. 超时时间: {timeout} 秒", flush=True)
    print("", flush=True)

    # 使用临时的 user_data_dir，避免污染用户已有的浏览器 profile
    temp_dir = os.path.join(os.path.expanduser("~"), ".suno", "export_temp_profile")
    os.makedirs(temp_dir, exist_ok=True)

    with sync_playwright() as pw:
        print("🌐 启动 Chrome 浏览器...", flush=True)

        # 尝试使用系统 Chrome，失败则用 Playwright 自带的 Chromium
        context = None
        for channel in ["chrome", "msedge", None]:
            try:
                launch_opts = {
                    "headless": False,
                    "viewport": {"width": 1280, "height": 800},
                    "locale": "en-US",
                    "args": [
                        "--disable-blink-features=AutomationControlled",
                        "--no-sandbox",
                    ],
                    "ignore_default_args": ["--enable-automation"],
                }
                if channel:
                    launch_opts["channel"] = channel

                context = pw.chromium.launch_persistent_context(
                    temp_dir,
                    **launch_opts,
                )
                browser_name = channel or "chromium"
                print(f"   ✅ 已启动 ({browser_name})", flush=True)
                break
            except Exception as e:
                if channel:
                    continue
                print(f"   ❌ 无法启动浏览器: {e}", flush=True)
                sys.exit(1)

        # 注入反检测
        context.add_init_script("""
            Object.defineProperty(navigator, 'webdriver', { get: () => undefined });
            delete navigator.__proto__.webdriver;
        """)

        page = context.pages[0] if context.pages else context.new_page()

        # 打开 Suno 登录页
        print("\n📌 打开 Suno 登录页面...", flush=True)
        page.goto("https://suno.com/sign-in", wait_until="domcontentloaded", timeout=30000)
        page.wait_for_timeout(2000)

        # 检查是否已经登录
        parsed = urlparse(page.url)
        if "sign-in" not in parsed.path and "suno.com" in parsed.netloc:
            print("   ✅ 检测到已登录状态！", flush=True)
        else:
            print("\n⏳ 请在浏览器中手动登录 Suno.com...", flush=True)
            print("   （支持 Google 登录、邮箱登录、任何方式）", flush=True)
            print("   （登录成功后脚本会自动检测）", flush=True)
            print("", flush=True)

            # 等待用户手动登录
            logged_in = False
            start_time = time.time()
            last_print = 0

            while time.time() - start_time < timeout:
                elapsed = int(time.time() - start_time)

                # 每 10 秒打印一次状态
                if elapsed - last_print >= 10:
                    print(f"   ⏳ [{elapsed}s/{timeout}s] 等待登录... 当前页面: {page.url[:80]}", flush=True)
                    last_print = elapsed

                try:
                    current_url = page.url
                    parsed = urlparse(current_url)

                    # 检测条件: URL 不在 sign-in 页面，且在 suno.com 域名下
                    if "suno.com" in parsed.netloc and "sign-in" not in parsed.path:
                        # 额外等待一下确保 Cookie 完全写入
                        page.wait_for_timeout(3000)
                        print(f"\n   🎉 检测到登录成功！当前页面: {current_url[:80]}", flush=True)
                        logged_in = True
                        break
                except Exception:
                    pass

                page.wait_for_timeout(2000)

            if not logged_in:
                print(f"\n   ❌ 等待超时（{timeout}秒）！请重试", flush=True)
                context.close()
                sys.exit(1)

        # 等待页面完全加载，确保所有 Cookie 已设置
        print("\n📌 等待页面完全加载...", flush=True)
        page.wait_for_timeout(5000)

        # 额外访问一下 create 页面确保获取到所有需要的 Cookie
        try:
            page.goto("https://suno.com/create", wait_until="domcontentloaded", timeout=15000)
            page.wait_for_timeout(3000)
        except Exception:
            pass

        # 导出 Cookie
        print("📌 导出 Cookie...", flush=True)
        cookies = context.cookies()

        if not cookies:
            print("   ❌ 未获取到任何 Cookie！", flush=True)
            context.close()
            sys.exit(1)

        # 过滤只保留 suno.com 相关的 Cookie（以及 Google 授权相关）
        suno_cookies = [
            c for c in cookies
            if "suno.com" in c.get("domain", "") or
               "suno" in c.get("domain", "") or
               "clerk" in c.get("domain", "")
        ]

        # 同时保存完整版和精简版
        # 完整版：所有 Cookie（包含 Google 登录状态等，更可靠）
        full_output = output_file
        # 精简版：仅 Suno 相关
        slim_output = output_file.replace(".json", "_slim.json")

        # 保存完整版
        Path(full_output).parent.mkdir(parents=True, exist_ok=True)
        with open(full_output, "w", encoding="utf-8") as f:
            json.dump(cookies, f, indent=2, ensure_ascii=False)

        # 保存精简版
        with open(slim_output, "w", encoding="utf-8") as f:
            json.dump(suno_cookies, f, indent=2, ensure_ascii=False)

        print(f"\n{'=' * 60}", flush=True)
        print(f"🎉 Cookie 导出成功！", flush=True)
        print(f"", flush=True)
        print(f"   📁 完整版（推荐）: {full_output}", flush=True)
        print(f"      共 {len(cookies)} 条 Cookie", flush=True)
        print(f"      大小: {os.path.getsize(full_output) / 1024:.1f} KB", flush=True)
        print(f"", flush=True)
        print(f"   📁 精简版: {slim_output}", flush=True)
        print(f"      共 {len(suno_cookies)} 条 Suno 相关 Cookie", flush=True)
        print(f"", flush=True)
        print(f"📋 下一步：把 Cookie 文件上传到云服务器，然后导入：", flush=True)
        print(f"", flush=True)
        print(f"   # 1. 上传到服务器", flush=True)
        print(f"   scp {full_output} user@your-server:/root/suno_cookie/suno_cookies.json", flush=True)
        print(f"", flush=True)
        print(f"   # 2. 在服务器上导入（默认读取 /root/suno_cookie/suno_cookies.json）", flush=True)
        print(f"   cd /path/to/suno-headless", flush=True)
        print(f"   python3 suno_login.py --import-cookies", flush=True)
        print(f"", flush=True)
        print(f"   # 3. 验证登录状态", flush=True)
        print(f"   python3 suno_login.py --check-only", flush=True)
        print(f"{'=' * 60}", flush=True)

        # 打印 Cookie 概要
        print(f"\n📊 Cookie 概要:", flush=True)
        domains = {}
        for c in cookies:
            d = c.get("domain", "unknown")
            domains[d] = domains.get(d, 0) + 1
        for d, cnt in sorted(domains.items(), key=lambda x: -x[1]):
            print(f"   {d}: {cnt} 条", flush=True)

        context.close()

    # 清理临时 profile
    import shutil
    try:
        shutil.rmtree(temp_dir, ignore_errors=True)
    except Exception:
        pass

    print(f"\n✅ 完成！浏览器已关闭。", flush=True)


def main():
    parser = argparse.ArgumentParser(
        description="Suno Cookie 导出工具 — 在本地电脑上运行，导出 Cookie 供云服务器使用",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
使用示例:
  # 默认导出到当前目录
  python3 export_cookies.py

  # 指定输出文件
  python3 export_cookies.py --output /path/to/suno_cookies.json

  # 延长超时时间（5 分钟）
  python3 export_cookies.py --timeout 300

导出后:
  # 上传到服务器
  scp <导出的Cookie文件> user@server:/root/suno_cookie/suno_cookies.json

  # 在服务器上导入（默认读取 /root/suno_cookie/suno_cookies.json）
  python3 suno_login.py --import-cookies
"""
    )
    parser.add_argument("--output", "-o", default=DEFAULT_OUTPUT,
                        help=f"Cookie 输出文件路径（默认: {DEFAULT_OUTPUT}）")
    parser.add_argument("--timeout", "-t", type=int, default=DEFAULT_TIMEOUT,
                        help=f"等待登录的超时时间/秒（默认: {DEFAULT_TIMEOUT}）")

    args = parser.parse_args()
    export_cookies(args.output, args.timeout)


if __name__ == "__main__":
    main()
