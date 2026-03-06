#!/usr/bin/env python3
"""
Suno.com 自动登录脚本
使用 Playwright + 真实 Chrome 浏览器 + persistent context 实现 Suno 的全自动登录。

✅ 已验证成功方案:
    channel='chrome' + launch_persistent_context + headless=False + ignore_default_args
    通过 Google OAuth 完成登录，Google 不会拦截

⚠️ 重要发现:
    - headless=True 模式下 Google 会 reject（即使用了 stealth/nodriver 等反检测）
    - headless=False 模式下 Google 不会 reject（100% 成功率）
    - 首次登录必须使用 headless=False（GUI 模式）
    - 登录成功后 persistent context 会保留会话，后续可用 headless=True 检查状态

用法:
    # 首次登录（必须 GUI 模式，macOS 会弹窗，Linux 需要 Xvfb）
    python suno_login.py --email <Gmail邮箱> --password <Gmail密码>

    # 检查登录状态（headless 即可）
    python suno_login.py --check-only

    # 强制重新登录
    python suno_login.py --email <Gmail邮箱> --password <Gmail密码> --force-login

    # Linux 云服务器（自动使用 Xvfb 虚拟显示）
    python suno_login.py --email <Gmail邮箱> --password <Gmail密码>

前置条件:
    - 系统安装了 Google Chrome 浏览器
    - pip install playwright && playwright install
    - Linux 云服务器还需: apt install -y xvfb && pip install PyVirtualDisplay
"""

import argparse
import json
import os
import sys
import time
import platform
from pathlib import Path
from urllib.parse import urlparse

try:
    from playwright.sync_api import sync_playwright, TimeoutError as PlaywrightTimeout
except ImportError:
    print("❌ 缺少 playwright 库，请先安装：")
    print("   pip install playwright && playwright install")
    sys.exit(1)


# ========== 配置 ==========
DEFAULT_COOKIE_FILE = os.path.expanduser("~/.suno/cookies.json")
DEFAULT_USER_DATA_DIR = os.path.expanduser("~/.suno/chrome_gui_profile")
SUNO_HOME = "https://suno.com"
SUNO_SIGN_IN = "https://suno.com/sign-in"
SUNO_CREATE = "https://suno.com/create"
DEFAULT_TIMEOUT = 30000


def ensure_dir(filepath: str):
    """确保文件所在目录存在"""
    Path(filepath).parent.mkdir(parents=True, exist_ok=True)


def save_cookies(context, cookie_file: str):
    """保存浏览器 cookies 到本地 JSON 文件"""
    ensure_dir(cookie_file)
    cookies = context.cookies()
    with open(cookie_file, "w") as f:
        json.dump(cookies, f, indent=2)
    print(f"✅ Cookies 已保存到 {cookie_file}（共 {len(cookies)} 条）", flush=True)


def _is_headless_linux():
    """检测是否在无 GUI 的 Linux 环境"""
    if platform.system() != "Linux":
        return False
    return not os.environ.get("DISPLAY")


def _setup_virtual_display():
    """
    在 Linux 无 GUI 环境下创建虚拟显示（Xvfb）
    返回 display 对象（需要在结束时 stop）
    """
    try:
        from pyvirtualdisplay import Display
        display = Display(visible=0, size=(1280, 800))
        display.start()
        print("   ✅ Xvfb 虚拟显示已启动", flush=True)
        return display
    except ImportError:
        print("   ⚠️ 未安装 PyVirtualDisplay，尝试直接运行", flush=True)
        print("   💡 安装方法: apt install -y xvfb && pip install PyVirtualDisplay", flush=True)
        return None


def _launch_context(pw, user_data_dir: str, headless: bool = False):
    """
    启动 Chrome persistent context

    关键参数:
    - channel='chrome': 使用系统安装的真实 Chrome（非 Playwright 自带 Chromium）
    - launch_persistent_context: 保留浏览器状态（cookies/localStorage 等）
    - ignore_default_args: 移除 --enable-automation 标志
    - headless=False: 必须使用 GUI 模式，否则 Google 会 reject
    """
    os.makedirs(user_data_dir, exist_ok=True)

    context = pw.chromium.launch_persistent_context(
        user_data_dir,
        channel="chrome",
        headless=headless,
        viewport={"width": 1280, "height": 800},
        locale="en-US",
        timezone_id="America/New_York",
        args=[
            "--disable-blink-features=AutomationControlled",
            "--no-sandbox",
            "--disable-dev-shm-usage",
            "--disable-automation",
        ],
        ignore_default_args=["--enable-automation"],
    )

    # 注入反检测脚本
    context.add_init_script("""
        Object.defineProperty(navigator, 'webdriver', { get: () => undefined });
        delete navigator.__proto__.webdriver;
        if (!window.chrome) window.chrome = {};
        if (!window.chrome.runtime) window.chrome.runtime = {};
    """)

    return context


def check_login_status(page) -> dict:
    """
    检查是否已登录 Suno，返回状态信息
    """
    result = {"logged_in": False, "username": None, "credits": None}
    try:
        page.goto(SUNO_SIGN_IN, wait_until="domcontentloaded", timeout=DEFAULT_TIMEOUT)
        page.wait_for_timeout(5000)

        url = page.url
        parsed = urlparse(url)
        # 只检查 URL 的 path 部分（忽略 query 参数中的 sign-in 字样）
        if "sign-in" not in parsed.path and "suno.com" in parsed.netloc:
            result["logged_in"] = True
            # 尝试获取用户信息
            try:
                body = page.locator("body").text_content()[:500]
                if "credits" in body:
                    parts = body.split("credits")[0].strip()
                    words = parts.split()
                    for w in reversed(words):
                        if w.isdigit():
                            result["credits"] = int(w)
                            break
                    for w in reversed(words):
                        if not w.isdigit() and len(w) > 1:
                            result["username"] = w
                            break
            except:
                pass
            return result

        return result
    except Exception as e:
        print(f"⚠️ 检查登录状态出错: {e}", flush=True)
        return result


def login_google_oauth(page, email: str, password: str) -> bool:
    """
    通过 Google OAuth 登录 Suno.com（全自动）

    流程:
    1. 打开 suno.com/sign-in
    2. 点击 "Continue with Google"
    3. 跳转到 Google → 输入邮箱 → Next
    4. 输入密码 → Next
    5. 跳转回 suno.com/create → 登录成功
    """
    print(f"🔐 开始通过 Google OAuth 登录 Suno.com", flush=True)
    print(f"   邮箱: {email}", flush=True)

    # 1. Warmup: 先访问 Google 首页建立正常浏览历史
    print("\n📌 步骤 1/6: 建立正常浏览历史...", flush=True)
    try:
        page.goto("https://www.google.com", wait_until="domcontentloaded", timeout=15000)
        page.wait_for_timeout(2000)
    except:
        pass

    # 2. 打开 Suno 登录页
    print("📌 步骤 2/6: 打开 Suno 登录页...", flush=True)
    page.goto(SUNO_SIGN_IN, wait_until="domcontentloaded", timeout=DEFAULT_TIMEOUT)
    page.wait_for_timeout(5000)
    print(f"   URL: {page.url}", flush=True)

    # 检查是否已登录
    parsed_url = urlparse(page.url)
    if "sign-in" not in parsed_url.path and "suno.com" in parsed_url.netloc:
        print("   ✅ 已登录（persistent context 中有有效会话）", flush=True)
        return True

    # 3. 点击 "Continue with Google"
    print("📌 步骤 3/6: 点击 'Continue with Google'...", flush=True)
    try:
        btn = page.locator('button:has-text("Continue with Google")').first
        btn.click(timeout=10000)
        print("   ✅ 已点击", flush=True)
    except Exception as e:
        print(f"   ❌ 未找到 Google 登录按钮: {e}", flush=True)
        page.screenshot(path="/tmp/suno_debug_no_google.png")
        return False

    # 4. 等待 Google OAuth 页面
    print("📌 步骤 4/6: 等待 Google 登录页面...", flush=True)
    try:
        page.wait_for_url("**/accounts.google.com/**", timeout=30000)
        print("   ✅ 已跳转到 Google", flush=True)
    except PlaywrightTimeout:
        print(f"   ❌ 未跳转到 Google: {page.url}", flush=True)
        page.screenshot(path="/tmp/suno_debug_no_redirect.png")
        return False

    page.wait_for_timeout(5000)

    if "rejected" in page.url:
        print("   ❌ Google 拒绝了登录！", flush=True)
        print("   💡 这通常发生在 headless=True 模式下。请用 --no-headless 模式重试", flush=True)
        page.screenshot(path="/tmp/suno_debug_rejected.png")
        return False

    page.screenshot(path="/tmp/suno_debug_google.png")

    # 5. 输入邮箱
    print("📌 步骤 5/6: 输入 Google 邮箱...", flush=True)
    try:
        email_input = page.locator('input[type="email"], input#identifierId').first
        email_input.wait_for(state="visible", timeout=10000)
        email_input.click()
        page.wait_for_timeout(500)
        for char in email:
            page.keyboard.type(char, delay=80 + (ord(char) % 70))
        print(f"   ✅ 已输入邮箱", flush=True)
    except Exception as e:
        print(f"   ❌ 输入邮箱失败: {e}", flush=True)
        page.screenshot(path="/tmp/suno_debug_email.png")
        return False

    page.wait_for_timeout(2000)
    try:
        page.locator('#identifierNext').first.click()
        print("   ✅ 点击 Next", flush=True)
    except:
        page.keyboard.press("Enter")

    page.wait_for_timeout(8000)
    page.screenshot(path="/tmp/suno_debug_after_email.png")

    if "rejected" in page.url:
        print("   ❌ 输入邮箱后被 Google 拒绝！", flush=True)
        page.screenshot(path="/tmp/suno_debug_rejected_email.png")
        return False

    # 6. 输入密码
    print("📌 步骤 6/6: 输入 Google 密码...", flush=True)
    try:
        pwd_input = page.locator('input[type="password"], input[name="Passwd"]').first
        pwd_input.wait_for(state="visible", timeout=15000)
        pwd_input.click()
        page.wait_for_timeout(600)
        for char in password:
            page.keyboard.type(char, delay=60 + (ord(char) % 50))
        print("   ✅ 已输入密码", flush=True)
    except Exception as e:
        print(f"   ❌ 输入密码失败: {e}", flush=True)
        page.screenshot(path="/tmp/suno_debug_password.png")
        return False

    page.wait_for_timeout(2000)
    try:
        page.locator('#passwordNext').first.click()
        print("   ✅ 点击 Next", flush=True)
    except:
        page.keyboard.press("Enter")

    # 等待跳转回 Suno
    print("\n⏳ 等待登录完成...", flush=True)
    for i in range(30):
        page.wait_for_timeout(3000)
        url = page.url
        elapsed = (i + 1) * 3
        print(f"   [{elapsed}s] {url[:100]}", flush=True)

        parsed_u = urlparse(url)
        if "suno.com" in parsed_u.netloc and "sign-in" not in parsed_u.path:
            print(f"\n🎉 登录成功！已跳转到 Suno", flush=True)
            page.wait_for_timeout(3000)
            return True

        if "rejected" in url:
            print("   ❌ Google 拒绝了登录", flush=True)
            page.screenshot(path="/tmp/suno_debug_rejected_final.png")
            return False

        # Google 同意/授权页面
        if "consent" in url:
            try:
                page.locator('button:has-text("Allow"), button:has-text("Continue")').first.click()
                print("   ✅ 已授权", flush=True)
            except:
                pass

        # Google 安全验证
        if "challenge" in url and "pwd" not in url:
            page.screenshot(path="/tmp/suno_debug_challenge.png")
            try:
                body = page.locator("body").text_content()[:300]
                print(f"   ⚠️ Google 要求安全验证: {body[:150]}", flush=True)
            except:
                pass
            print("   💡 提示: 如果 Google 要求手机验证，请先在普通浏览器中登录 Google 并信任此设备", flush=True)

        # Google 选择账号页面
        if "accounts.google.com" in url and "chooser" in url:
            try:
                page.locator(f'[data-email="{email}"]').first.click()
                print(f"   ✅ 已选择账号 {email}", flush=True)
            except:
                pass

    print("\n⏰ 等待超时", flush=True)
    page.screenshot(path="/tmp/suno_debug_timeout.png")
    return False


def main():
    parser = argparse.ArgumentParser(
        description="Suno.com 全自动登录工具（通过 Google OAuth）",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
使用示例:
  # 首次登录（默认 GUI 模式，macOS 弹窗，Linux 用 Xvfb）
  python suno_login.py --email user@gmail.com --password mypass

  # 检查登录状态（headless 即可）
  python suno_login.py --check-only

  # 强制重新登录
  python suno_login.py --email user@gmail.com --password mypass --force-login

技术方案:
  ✅ Chrome channel + persistent context + headless=False
  ✅ Google OAuth 不会检测到自动化（100% 验证通过）
  ✅ Linux 服务器自动使用 Xvfb 虚拟显示
  ✅ 首次登录后 persistent context 保留会话，后续可 headless
"""
    )
    parser.add_argument("--email", help="Gmail 邮箱地址")
    parser.add_argument("--password", help="Gmail 密码")
    parser.add_argument("--headless", action="store_true",
                        help="强制使用 headless 模式（仅 check-only 或已登录时推荐）")
    parser.add_argument("--cookie-file", default=DEFAULT_COOKIE_FILE,
                        help=f"Cookie 保存路径（默认: {DEFAULT_COOKIE_FILE}）")
    parser.add_argument("--user-data-dir", default=DEFAULT_USER_DATA_DIR,
                        help=f"浏览器配置目录（默认: {DEFAULT_USER_DATA_DIR}）")
    parser.add_argument("--check-only", action="store_true",
                        help="仅检查登录状态（使用 headless 模式）")
    parser.add_argument("--force-login", action="store_true",
                        help="强制重新登录")

    args = parser.parse_args()

    # 确定 headless 模式
    # - check-only: 默认 headless（只是检查状态，不需要 GUI）
    # - 登录: 默认 headless=False（GUI 模式，避免被 Google reject）
    # - --headless: 强制 headless
    if args.check_only:
        headless = True
    elif args.headless:
        headless = True
    else:
        headless = False  # 登录时默认用 GUI 模式

    print("=" * 60, flush=True)
    print("🎵 Suno.com 全自动登录工具", flush=True)
    print("   方案: Chrome + persistent context + Google OAuth", flush=True)
    if headless:
        print("   模式: headless（无头）", flush=True)
    else:
        print("   模式: GUI（图形界面）", flush=True)
    print("=" * 60, flush=True)

    # 强制重新登录：只清除 cookie 文件，保留 persistent context
    # ⚠️ 不要删除 user_data_dir！Google 的 session 信息在里面
    if args.force_login:
        if os.path.exists(args.cookie_file):
            os.remove(args.cookie_file)
            print(f"🗑️ 已清除 cookies: {args.cookie_file}", flush=True)
        print("   ℹ️ 保留浏览器配置（含 Google session），避免被 Google 拦截", flush=True)

    # Linux 无 GUI 环境下启动虚拟显示
    virtual_display = None
    if not headless and _is_headless_linux():
        print("\n🖥️ 检测到 Linux 无 GUI 环境，启动 Xvfb 虚拟显示...", flush=True)
        virtual_display = _setup_virtual_display()

    try:
        with sync_playwright() as pw:
            print(f"\n🌐 启动 Chrome (headless={headless})...", flush=True)
            context = _launch_context(pw, args.user_data_dir, headless=headless)
            page = context.pages[0] if context.pages else context.new_page()

            # 检查模式
            if args.check_only:
                status = check_login_status(page)
                if status["logged_in"]:
                    print(f"\n✅ 已登录 Suno.com", flush=True)
                    if status["username"]:
                        print(f"   用户: {status['username']}", flush=True)
                    if status["credits"]:
                        print(f"   积分: {status['credits']}", flush=True)
                    context.close()
                    sys.exit(0)
                else:
                    print("\n❌ 未登录 Suno.com", flush=True)
                    context.close()
                    sys.exit(2)

            # 检查是否需要登录
            if not args.force_login:
                print("\n🔍 检查现有登录状态...", flush=True)
                status = check_login_status(page)
                if status["logged_in"]:
                    print(f"✅ 已登录！用户: {status.get('username', '未知')}, 积分: {status.get('credits', '未知')}", flush=True)
                    save_cookies(context, args.cookie_file)
                    context.close()
                    sys.exit(0)
                print("   未登录，准备执行登录...\n", flush=True)

            # 执行登录
            if not args.email or not args.password:
                print("\n❌ 需要 --email 和 --password 参数", flush=True)
                context.close()
                parser.print_help()
                sys.exit(1)

            success = login_google_oauth(page, args.email, args.password)

            if success:
                save_cookies(context, args.cookie_file)
                page.wait_for_timeout(3000)
                status = check_login_status(page)
                print("\n" + "=" * 60, flush=True)
                print("🎉 登录成功！", flush=True)
                if status.get("username"):
                    print(f"   用户: {status['username']}", flush=True)
                if status.get("credits"):
                    print(f"   积分: {status['credits']}", flush=True)
                print(f"   Cookies: {args.cookie_file}", flush=True)
                print(f"   浏览器配置: {args.user_data_dir}", flush=True)
                print("", flush=True)
                print("   后续运行无需重新登录（persistent context 自动保持登录）", flush=True)
                print("   后续可用 --check-only 检查状态（自动 headless 模式）", flush=True)
                print("=" * 60, flush=True)
                context.close()
                sys.exit(0)
            else:
                print("\n" + "=" * 60, flush=True)
                print("❌ 登录失败！可能原因：", flush=True)
                print("   1. Gmail 邮箱或密码不正确", flush=True)
                print("   2. Google 要求手机/两步验证", flush=True)
                print("   3. 系统未安装 Chrome 浏览器", flush=True)
                print("   4. 网络问题", flush=True)
                if headless:
                    print("   5. headless 模式被 Google 检测到 → 请去掉 --headless 重试", flush=True)
                print("", flush=True)
                print("💡 排查: 查看 /tmp/suno_debug_*.png 截图", flush=True)
                print("=" * 60, flush=True)
                context.close()
                sys.exit(1)
    finally:
        # 清理虚拟显示
        if virtual_display:
            virtual_display.stop()
            print("🖥️ Xvfb 虚拟显示已关闭", flush=True)


if __name__ == "__main__":
    main()
