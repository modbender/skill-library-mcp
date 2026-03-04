#!/usr/bin/env python3
"""
Outlook 日历登录脚本 - MFA 数字匹配版
用法：python login.py
登录成功后自动保存 Cookie 到 data/cookies.json
"""
import json, time, os, re
from pathlib import Path
from playwright.sync_api import sync_playwright

BASE_DIR = Path(__file__).parent
OUTLOOK_DIR = Path.home() / ".outlook"
with open(OUTLOOK_DIR / "config.json") as f:
    cfg = json.load(f)

EMAIL = cfg["email"]
PASSWORD = cfg["password"]
COOKIE_FILE = OUTLOOK_DIR / "cookies.json"
COOKIE_FILE.parent.mkdir(exist_ok=True)

STATUS_FILE = OUTLOOK_DIR / "login_status.txt"
CMD_FILE = OUTLOOK_DIR / "login_cmd.txt"


def log(msg):
    print(msg, flush=True)
    with open(STATUS_FILE, "a") as f:
        f.write(f"{msg}\n")


def shot(page, name):
    try:
        path = OUTLOOK_DIR / f"debug_{name}.png"
        page.screenshot(path=str(path))
    except:
        pass


def safe_content(page):
    try:
        return page.content()
    except:
        return ""


def find_number(page):
    """从页面提取数字匹配的数字"""
    for sel in ["#idRichContext_DisplaySign", ".displaySign"]:
        try:
            el = page.query_selector(sel)
            if el:
                t = el.inner_text().strip()
                if t.isdigit():
                    return t
        except:
            pass
    content = safe_content(page)
    m = re.search(r'displaySign["\s:]+(\d+)', content)
    if m:
        return m.group(1)
    return None


def get_url(page):
    try:
        return page.url
    except:
        return ""


open(STATUS_FILE, "w").close()

with sync_playwright() as p:
    browser = p.chromium.launch(
        headless=True,
        args=["--no-sandbox", "--disable-dev-shm-usage"]
    )
    ctx = browser.new_context(
        user_agent="Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/121.0.0.0 Safari/537.36",
        viewport={"width": 1280, "height": 800},
    )
    page = ctx.new_page()

    log("[1] 登录 Microsoft 365...")
    page.goto("https://login.microsoftonline.com", timeout=30000)
    page.wait_for_load_state("load", timeout=20000)
    page.fill('input[type="email"]', EMAIL)
    page.click('input[type="submit"]')
    page.wait_for_load_state("load", timeout=20000)
    page.wait_for_selector('input[type="password"]', timeout=10000)
    page.fill('input[type="password"]', PASSWORD)
    page.click('input[type="submit"]')
    page.wait_for_load_state("load", timeout=20000)
    log(f"[1] 完成，URL: {get_url(page)}")

    # 等待并提取 MFA 数字
    time.sleep(3)
    log("[2] 等待 MFA 数字匹配页面...")
    for i in range(20):
        time.sleep(2)
        n = find_number(page)
        if n:
            log(f"[2] 屏幕数字: 【{n}】")
            log(f"[NUMBER:{n}]")
            break
        shot(page, f"wait_{i:02d}")

    # 等用户在 Authenticator 批准（最多 3 分钟）
    log("[3] 等待 Authenticator 批准...（最多 180 秒）")
    for i in range(90):
        time.sleep(2)
        url = get_url(page)

        # 成功离开登录页
        if "login.microsoftonline.com" not in url and url.startswith("https://"):
            log(f"[3] 成功！URL: {url}")
            break

        # KMSI 页面
        try:
            btn = page.query_selector("#idSIButton9")
            if btn:
                log("[3] 点击保持登录...")
                page.evaluate("document.querySelector('#idSIButton9').click()")
                time.sleep(3)
                new_url = get_url(page)
                if "login.microsoftonline.com" not in new_url:
                    log(f"[3] 保持登录成功！URL: {new_url}")
                    break
        except:
            pass

        if i % 10 == 0:
            shot(page, f"poll_{i:02d}")
            log(f"[3/{i*2}s] 等待中...")

    # 导航到 Outlook 获取完整 Cookie
    log("[4] 导航到 Outlook 日历...")
    page.goto("https://outlook.office.com/calendar/", timeout=30000)
    page.wait_for_load_state("load", timeout=30000)
    time.sleep(8)
    log(f"[4] URL: {get_url(page)}")

    # 保存 Cookie
    cookies = ctx.cookies()
    with open(COOKIE_FILE, "w") as f:
        json.dump(cookies, f, indent=2)

    outlook_count = len([c for c in cookies if "outlook" in c.get("domain", "")])
    log(f"[✓] Cookie 保存完毕：共 {len(cookies)} 条，outlook 域 {outlook_count} 条")
    log(f"[DONE]")
    browser.close()
