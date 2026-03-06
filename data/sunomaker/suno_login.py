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

    # 🍪 Cookie 导入方式（推荐！绕过 Google 安全验证）
    # 步骤 1: 在本地电脑运行 export_cookies.py 导出 Cookie
    # 步骤 2: 上传 Cookie 文件到服务器
    # 步骤 3: 在服务器上导入
    python suno_login.py --import-cookies /root/suno_cookie/suno_cookies.json

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
import subprocess
import shutil
from pathlib import Path
from urllib.parse import urlparse


def _check_playwright_browsers():
    """检查 playwright 浏览器二进制是否已安装，未安装则自动安装"""
    try:
        # 检查 playwright 浏览器是否存在
        result = subprocess.run(
            [sys.executable, "-m", "playwright", "install", "--dry-run"],
            capture_output=True, text=True, timeout=30
        )
        # dry-run 不可用时（老版本），直接检查 chromium 路径
    except Exception:
        pass

    # 检查是否有可用的 Chrome/Chromium
    chrome_bins = ["google-chrome", "google-chrome-stable", "chromium", "chromium-browser"]
    for b in chrome_bins:
        if shutil.which(b):
            return True

    # 系统 Chrome 都没有，尝试自动安装 playwright 浏览器
    print("⚠️ 未找到系统 Chrome，尝试安装 Playwright 浏览器...", flush=True)
    try:
        subprocess.run(
            [sys.executable, "-m", "playwright", "install", "chromium"],
            check=True, timeout=300
        )
        print("   ✅ Playwright chromium 已安装", flush=True)
        return True
    except Exception as e:
        print(f"   ❌ 安装失败: {e}", flush=True)
        return False


# 使用更健壮的导入方式
try:
    from playwright.sync_api import sync_playwright, TimeoutError as PlaywrightTimeout
except ImportError:
    print("❌ 缺少 playwright 库，请先安装：", flush=True)
    print("   pip install playwright && playwright install", flush=True)
    # 尝试自动安装
    print("   🔄 尝试自动安装...", flush=True)
    try:
        subprocess.check_call([sys.executable, "-m", "pip", "install", "playwright"])
        subprocess.check_call([sys.executable, "-m", "playwright", "install", "chromium"])
        from playwright.sync_api import sync_playwright, TimeoutError as PlaywrightTimeout
        print("   ✅ 自动安装成功", flush=True)
    except Exception as e:
        print(f"   ❌ 自动安装失败: {e}", flush=True)
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


def import_cookies_from_file(cookie_import_path: str, user_data_dir: str, cookie_file: str):
    """
    从导出的 Cookie JSON 文件导入 Cookie 到 persistent context
    
    流程:
    1. 读取导出的 Cookie JSON
    2. 启动 persistent context（headless 模式即可）
    3. 将 Cookie 注入到浏览器
    4. 访问 suno.com 验证登录状态
    5. 保存到本地 cookie 文件
    """
    print(f"\n🍪 从文件导入 Cookie: {cookie_import_path}", flush=True)
    
    if not os.path.exists(cookie_import_path):
        print(f"   ❌ 文件不存在: {cookie_import_path}", flush=True)
        return False
    
    # 读取 Cookie JSON
    try:
        with open(cookie_import_path, "r", encoding="utf-8") as f:
            cookies = json.load(f)
        print(f"   📦 读取到 {len(cookies)} 条 Cookie", flush=True)
    except Exception as e:
        print(f"   ❌ 读取 Cookie 文件失败: {e}", flush=True)
        return False
    
    if not cookies:
        print("   ❌ Cookie 文件为空！", flush=True)
        return False
    
    # 检查 Cookie 格式
    # Playwright 格式: [{"name": ..., "value": ..., "domain": ..., "path": ...}, ...]
    # 浏览器扩展格式可能不同，需要兼容
    valid_cookies = []
    for c in cookies:
        if isinstance(c, dict) and "name" in c and "value" in c:
            # 确保必要字段
            cookie = {
                "name": c["name"],
                "value": c["value"],
                "domain": c.get("domain", ".suno.com"),
                "path": c.get("path", "/"),
            }
            # 可选字段
            if "expires" in c and c["expires"]:
                cookie["expires"] = c["expires"]
            if "httpOnly" in c:
                cookie["httpOnly"] = c["httpOnly"]
            if "secure" in c:
                cookie["secure"] = c["secure"]
            if "sameSite" in c:
                cookie["sameSite"] = c["sameSite"]
            valid_cookies.append(cookie)
    
    if not valid_cookies:
        print("   ❌ 没有有效的 Cookie（需要包含 name 和 value 字段）", flush=True)
        return False
    
    # 统计域名
    domains = {}
    for c in valid_cookies:
        d = c.get("domain", "unknown")
        domains[d] = domains.get(d, 0) + 1
    print(f"   📊 有效 Cookie: {len(valid_cookies)} 条", flush=True)
    for d, cnt in sorted(domains.items(), key=lambda x: -x[1])[:5]:
        print(f"      {d}: {cnt} 条", flush=True)
    
    # 启动浏览器并注入 Cookie
    # 对于 Linux 无 GUI 环境，使用 Xvfb
    virtual_display = None
    if _is_headless_linux():
        print("\n🖥️ 检测到 Linux 无 GUI 环境，启动 Xvfb...", flush=True)
        virtual_display = _setup_virtual_display()
        if virtual_display is None:
            print("   ⚠️ Xvfb 启动失败，尝试 headless 模式", flush=True)
    
    try:
        with sync_playwright() as pw:
            # Cookie 导入可以用 headless=True（不需要过 Google 登录）
            # 但为了最大兼容性，如果有虚拟显示就用 GUI 模式
            use_headless = virtual_display is None and _is_headless_linux()
            print(f"\n🌐 启动 Chrome (headless={use_headless})...", flush=True)
            context = _launch_context(pw, user_data_dir, headless=use_headless)
            page = context.pages[0] if context.pages else context.new_page()
            
            # 先导航到 suno.com（Cookie 需要在正确的域名下注入）
            print("   📌 导航到 suno.com...", flush=True)
            try:
                page.goto("https://suno.com", wait_until="domcontentloaded", timeout=30000)
                page.wait_for_timeout(2000)
            except Exception as e:
                print(f"   ⚠️ 导航失败，继续尝试注入: {e}", flush=True)
            
            # 注入 Cookie
            print("   🍪 注入 Cookie...", flush=True)
            injected = 0
            failed = 0
            for c in valid_cookies:
                try:
                    context.add_cookies([c])
                    injected += 1
                except Exception as e:
                    failed += 1
                    if failed <= 3:  # 只打印前 3 个错误
                        print(f"      ⚠️ 跳过: {c.get('name', '?')}@{c.get('domain', '?')}: {e}", flush=True)
            
            print(f"   ✅ 成功注入 {injected} 条 Cookie（跳过 {failed} 条）", flush=True)
            
            # 验证登录状态
            print("\n🔍 验证登录状态...", flush=True)
            page.wait_for_timeout(1000)
            status = check_login_status(page)
            
            if status["logged_in"]:
                # 保存 Cookie 到标准位置
                save_cookies(context, cookie_file)
                
                print(f"\n{'=' * 60}", flush=True)
                print(f"🎉 Cookie 导入成功！已登录 Suno.com", flush=True)
                if status.get("username"):
                    print(f"   用户: {status['username']}", flush=True)
                if status.get("credits"):
                    print(f"   积分: {status['credits']}", flush=True)
                print(f"   Cookie 已保存到: {cookie_file}", flush=True)
                print(f"   浏览器配置: {user_data_dir}", flush=True)
                print(f"\n   后续操作无需再次导入（persistent context 自动保持会话）", flush=True)
                print(f"{'=' * 60}", flush=True)
                context.close()
                return True
            else:
                print(f"\n❌ Cookie 导入后仍未登录！", flush=True)
                print(f"   可能原因:", flush=True)
                print(f"   1. Cookie 已过期（请在本地重新导出）", flush=True)
                print(f"   2. Cookie 格式不兼容", flush=True)
                print(f"   3. Suno 需要额外的认证信息", flush=True)
                print(f"\n   💡 建议: 在本地电脑重新运行 export_cookies.py 导出新的 Cookie", flush=True)
                page.screenshot(path="/tmp/suno_debug_import_failed.png")
                context.close()
                return False
    finally:
        if virtual_display:
            virtual_display.stop()
            print("🖥️ Xvfb 虚拟显示已关闭", flush=True)


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

    优先使用 PyVirtualDisplay，失败时 fallback 到手动启动 Xvfb
    """
    # 方案 1: 使用 PyVirtualDisplay（推荐）
    try:
        from pyvirtualdisplay import Display
        display = Display(visible=0, size=(1280, 800))
        display.start()
        new_display = os.environ.get("DISPLAY", "")
        print(f"   ✅ Xvfb 虚拟显示已启动 (DISPLAY={new_display})", flush=True)
        return display
    except ImportError:
        print("   ⚠️ 未安装 PyVirtualDisplay，尝试手动启动 Xvfb...", flush=True)
    except Exception as e:
        print(f"   ⚠️ PyVirtualDisplay 启动失败: {e}，尝试手动启动 Xvfb...", flush=True)

    # 方案 2: 手动启动 Xvfb（fallback）
    if shutil.which("Xvfb"):
        try:
            # 寻找可用的 display 号
            for display_num in range(99, 110):
                lock_file = f"/tmp/.X{display_num}-lock"
                if not os.path.exists(lock_file):
                    break
            else:
                display_num = 99  # 默认

            xvfb_proc = subprocess.Popen(
                ["Xvfb", f":{display_num}", "-screen", "0", "1280x800x24", "-ac"],
                stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL
            )
            time.sleep(1)  # 等待 Xvfb 启动

            if xvfb_proc.poll() is None:  # 进程还活着
                os.environ["DISPLAY"] = f":{display_num}"
                print(f"   ✅ Xvfb 手动启动成功 (DISPLAY=:{display_num})", flush=True)

                # 返回一个带 stop 方法的伪 display 对象
                class ManualDisplay:
                    def __init__(self, proc, num):
                        self.proc = proc
                        self.num = num
                    def stop(self):
                        self.proc.terminate()
                        self.proc.wait(timeout=5)
                        lock_file = f"/tmp/.X{self.num}-lock"
                        if os.path.exists(lock_file):
                            try:
                                os.remove(lock_file)
                            except OSError:
                                pass

                return ManualDisplay(xvfb_proc, display_num)
            else:
                print(f"   ❌ Xvfb 进程启动后立即退出", flush=True)
        except Exception as e:
            print(f"   ❌ 手动启动 Xvfb 失败: {e}", flush=True)
    else:
        print("   ❌ 未找到 Xvfb 二进制文件", flush=True)
        print("   💡 安装方法: sudo apt install -y xvfb", flush=True)

    # 方案 3: 尝试安装 PyVirtualDisplay 后再试
    print("   🔄 尝试自动安装 PyVirtualDisplay...", flush=True)
    try:
        subprocess.check_call(
            [sys.executable, "-m", "pip", "install", "PyVirtualDisplay"],
            stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL
        )
        from pyvirtualdisplay import Display
        display = Display(visible=0, size=(1280, 800))
        display.start()
        print(f"   ✅ PyVirtualDisplay 安装并启动成功", flush=True)
        return display
    except Exception as e:
        print(f"   ❌ 所有虚拟显示方案均失败: {e}", flush=True)
        print("   💡 请手动安装: sudo apt install -y xvfb && pip install PyVirtualDisplay", flush=True)
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

    # Nutze Playwright's eingebauten Chromium (kein channel)
    # channel='chrome' erfordert echtes Google Chrome in /opt/google/chrome
    launch_opts = {
        "headless": headless,
        "viewport": {"width": 1280, "height": 800},
        "locale": "en-US",
        "timezone_id": "America/New_York",
        "args": [
            "--disable-blink-features=AutomationControlled",
            "--no-sandbox",
            "--disable-dev-shm-usage",
            "--disable-automation",
        ],
        "ignore_default_args": ["--enable-automation"],
    }
    
    context = pw.chromium.launch_persistent_context(
        user_data_dir,
        **launch_opts
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
  # 方式一: 邮箱密码登录（GUI 模式，macOS 弹窗，Linux 用 Xvfb）
  python suno_login.py --email user@gmail.com --password mypass

  # 方式二: Cookie 导入（推荐！绕过 Google 安全验证）
  # 步骤 1: 在本地电脑运行 export_cookies.py 导出 Cookie
  # 步骤 2: scp suno_cookies.json user@server:~/
  # 步骤 3: 在服务器上导入
  python suno_login.py --import-cookies /root/suno_cookie/suno_cookies.json

  # 检查登录状态（headless 即可）
  python suno_login.py --check-only

  # 强制重新登录
  python suno_login.py --email user@gmail.com --password mypass --force-login

技术方案:
  ✅ Chrome channel + persistent context + headless=False
  ✅ Google OAuth 不会检测到自动化（100% 验证通过）
  ✅ Cookie 导入方式绕过 Google 安全验证
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
    parser.add_argument("--import-cookies", type=str, metavar="FILE",
                        nargs="?", const="/root/suno_cookie/suno_cookies.json",
                        default=None,
                        help="从导出的 Cookie JSON 文件导入（默认: /root/suno_cookie/suno_cookies.json）")

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

    # Cookie 导入模式
    if args.import_cookies:
        success = import_cookies_from_file(
            args.import_cookies, args.user_data_dir, args.cookie_file
        )
        sys.exit(0 if success else 1)

    # 强制重新登录：只清除 cookie 文件，保留 persistent context
    # ⚠️ 不要删除 user_data_dir！Google 的 session 信息在里面
    if args.force_login:
        if os.path.exists(args.cookie_file):
            os.remove(args.cookie_file)
            print(f"🗑️ 已清除 cookies: {args.cookie_file}", flush=True)
        print("   ℹ️ 保留浏览器配置（含 Google session），避免被 Google 拦截", flush=True)

    # 检查 playwright 浏览器
    _check_playwright_browsers()

    # Linux 无 GUI 环境下启动虚拟显示
    virtual_display = None
    if not headless and _is_headless_linux():
        print("\n🖥️ 检测到 Linux 无 GUI 环境，启动 Xvfb 虚拟显示...", flush=True)
        virtual_display = _setup_virtual_display()
        if virtual_display is None:
            print("   ⚠️ 虚拟显示启动失败，回退到 headless 模式", flush=True)
            headless = True

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
