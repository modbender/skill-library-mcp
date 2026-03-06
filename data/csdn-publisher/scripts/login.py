#!/usr/bin/env python3
"""
CSDN 扫码登录 - 获取 Cookie

使用 Playwright 打开 CSDN 登录页面，截取二维码图片，
用户扫码登录后自动保存 Cookie，并可选发送 Telegram 通知。

用法:
    python login.py login [--timeout 300] [--notify]
    python login.py check

依赖:
    pip install playwright requests
    playwright install chromium
"""

import asyncio
import argparse
import json
import os
import sys
from pathlib import Path

# 默认路径
DEFAULT_COOKIE_FILE = Path.home() / ".openclaw/workspace/credentials/csdn-cookie.json"
DEFAULT_QR_OUTPUT = Path.home() / ".openclaw/workspace/credentials/csdn-qr.png"
DEFAULT_CONFIG_FILE = Path.home() / ".openclaw/workspace/credentials/telegram-notify.json"
DEFAULT_PROXY = "http://127.0.0.1:20171"  # 默认代理


def send_telegram_notification(message: str, config_file: str = None):
    """发送 Telegram 通知"""
    import requests
    
    config_path = Path(config_file) if config_file else DEFAULT_CONFIG_FILE
    
    if not config_path.exists():
        print(f"⚠️ Telegram 配置文件不存在: {config_path}", file=sys.stderr)
        return False
    
    try:
        with open(config_path, 'r') as f:
            config = json.load(f)
        
        bot_token = config.get('bot_token')
        chat_id = config.get('chat_id')
        
        if not bot_token or not chat_id:
            print("⚠️ Telegram 配置不完整（需要 bot_token 和 chat_id）", file=sys.stderr)
            return False
        
        # 发送消息
        url = f"https://api.telegram.org/bot{bot_token}/sendMessage"
        resp = requests.post(url, json={
            "chat_id": chat_id,
            "text": message,
            "parse_mode": "HTML"
        }, timeout=10)
        
        if resp.status_code == 200 and resp.json().get('ok'):
            print(f"📤 Telegram 通知已发送", file=sys.stderr)
            return True
        else:
            print(f"⚠️ Telegram 发送失败: {resp.text}", file=sys.stderr)
            return False
    except Exception as e:
        print(f"⚠️ Telegram 通知失败: {e}", file=sys.stderr)
        return False


async def csdn_login(cookie_file: str = None, qr_output: str = None, headless: bool = True, 
                     timeout: int = 120, notify: bool = False, config_file: str = None,
                     proxy: str = None):
    """
    打开 CSDN 登录页面，截取二维码，等待用户扫码登录，保存 Cookie
    
    Args:
        cookie_file: Cookie 保存路径
        qr_output: 二维码图片保存路径
        headless: 是否无头模式
        timeout: 等待登录的超时时间（秒）
        notify: 登录成功后是否发送 Telegram 通知
        config_file: Telegram 配置文件路径
        proxy: 代理服务器地址
    
    Returns:
        dict: {"success": bool, "qr_path": str or None, "message": str}
    """
    from playwright.async_api import async_playwright
    
    cookie_path = Path(cookie_file) if cookie_file else DEFAULT_COOKIE_FILE
    qr_path = Path(qr_output) if qr_output else DEFAULT_QR_OUTPUT
    proxy_server = proxy or os.environ.get('https_proxy') or os.environ.get('HTTPS_PROXY') or DEFAULT_PROXY
    cookie_path.parent.mkdir(parents=True, exist_ok=True)
    qr_path.parent.mkdir(parents=True, exist_ok=True)
    
    print("🚀 启动浏览器...", file=sys.stderr)
    print(f"   代理: {proxy_server}", file=sys.stderr)
    
    async with async_playwright() as p:
        browser = await p.chromium.launch(
            headless=headless,
            args=['--no-sandbox', '--disable-setuid-sandbox'],
            proxy={"server": proxy_server} if proxy_server else None
        )
        context = await browser.new_context()
        page = await context.new_page()
        
        print("🌐 打开 CSDN 登录页面...", file=sys.stderr)
        await page.goto("https://passport.csdn.net/login", timeout=60000)
        await asyncio.sleep(3)
        
        # 尝试切换到扫码登录
        try:
            qr_tab = await page.query_selector('text=扫码登录')
            if qr_tab:
                await qr_tab.click()
                await asyncio.sleep(2)
                print("📱 已切换到扫码登录", file=sys.stderr)
        except Exception as e:
            print(f"⚠️ 切换扫码登录失败: {e}", file=sys.stderr)
        
        # 截取二维码图片
        qr_captured = False
        try:
            qr_selectors = [
                'img[src*="qrcode"]',
                'img[src*="qr"]',
                '.qr-img',
                '.qrcode',
                '[class*="qr"] img',
                'canvas',
            ]
            
            for selector in qr_selectors:
                qr_element = await page.query_selector(selector)
                if qr_element:
                    await qr_element.screenshot(path=str(qr_path))
                    qr_captured = True
                    print(f"📸 二维码已保存: {qr_path}", file=sys.stderr)
                    break
            
            if not qr_captured:
                login_box = await page.query_selector('.main-login, .login-box, [class*="login"]')
                if login_box:
                    await login_box.screenshot(path=str(qr_path))
                    qr_captured = True
                    print(f"📸 登录区域已截图: {qr_path}", file=sys.stderr)
                else:
                    await page.screenshot(path=str(qr_path))
                    qr_captured = True
                    print(f"📸 整页截图已保存: {qr_path}", file=sys.stderr)
        except Exception as e:
            print(f"⚠️ 截图失败: {e}", file=sys.stderr)
        
        if qr_captured:
            print(f"QR_PATH:{qr_path}")
        
        # 等待登录成功
        print(f"⏳ 等待扫码登录（最多 {timeout} 秒）...", file=sys.stderr)
        
        logged_in = False
        for i in range(timeout):
            current_url = page.url
            
            if "passport.csdn.net/login" not in current_url:
                logged_in = True
                break
            
            try:
                user_info = await page.query_selector('.user-info, .avatar, [class*="user"]')
                if user_info:
                    logged_in = True
                    break
            except:
                pass
            
            await asyncio.sleep(1)
            if (i + 1) % 15 == 0:
                print(f"   已等待 {i + 1} 秒...", file=sys.stderr)
        
        if not logged_in:
            print("❌ 登录超时", file=sys.stderr)
            if notify:
                send_telegram_notification("❌ CSDN 登录超时，请重试", config_file)
            await browser.close()
            return {"success": False, "qr_path": str(qr_path) if qr_captured else None, "message": "登录超时"}
        
        print("✅ 登录成功！", file=sys.stderr)
        
        # 访问 CSDN 主站以获取完整 Cookie
        await page.goto("https://www.csdn.net/")
        await asyncio.sleep(2)
        
        # 保存 Cookie
        cookies = await context.cookies()
        
        storage_state = await context.storage_state()
        with open(cookie_path, 'w', encoding='utf-8') as f:
            json.dump(storage_state, f, ensure_ascii=False, indent=2)
        
        print(f"💾 Cookie 已保存到: {cookie_path}", file=sys.stderr)
        
        cookie_str_path = cookie_path.with_suffix('.txt')
        cookie_str = '; '.join([f"{c['name']}={c['value']}" for c in cookies if 'csdn' in c.get('domain', '')])
        with open(cookie_str_path, 'w', encoding='utf-8') as f:
            f.write(cookie_str)
        print(f"💾 Cookie 字符串已保存到: {cookie_str_path}", file=sys.stderr)
        
        # 发送 Telegram 通知
        if notify:
            send_telegram_notification("✅ CSDN 登录成功！Cookie 已保存，可以继续发布文章了。", config_file)
        
        await browser.close()
        return {"success": True, "qr_path": str(qr_path) if qr_captured else None, "message": "登录成功"}


async def check_cookie(cookie_file: str = None):
    """检查 Cookie 是否有效"""
    from playwright.async_api import async_playwright
    
    cookie_path = Path(cookie_file) if cookie_file else DEFAULT_COOKIE_FILE
    
    if not cookie_path.exists():
        print(f"❌ Cookie 文件不存在: {cookie_path}", file=sys.stderr)
        return False
    
    print("🔍 检查 Cookie 有效性...", file=sys.stderr)
    
    async with async_playwright() as p:
        browser = await p.chromium.launch(
            headless=True,
            args=['--no-sandbox', '--disable-setuid-sandbox']
        )
        
        with open(cookie_path, 'r', encoding='utf-8') as f:
            storage_state = json.load(f)
        
        context = await browser.new_context(storage_state=storage_state)
        page = await context.new_page()
        
        await page.goto("https://editor.csdn.net/md")
        await asyncio.sleep(3)
        
        current_url = page.url
        page_content = await page.content()
        
        if "passport.csdn.net" in current_url or "login" in current_url.lower():
            print("❌ Cookie 已失效（被重定向到登录页）", file=sys.stderr)
            await browser.close()
            return False
        
        if "登录" in page_content and "扫码" in page_content:
            print("❌ Cookie 已失效（页面显示登录框）", file=sys.stderr)
            await browser.close()
            return False
        
        print("✅ Cookie 有效", file=sys.stderr)
        await browser.close()
        return True


def main():
    parser = argparse.ArgumentParser(description='CSDN 扫码登录工具')
    subparsers = parser.add_subparsers(dest='command')
    
    # login 命令
    login_parser = subparsers.add_parser('login', help='扫码登录获取 Cookie')
    login_parser.add_argument('--cookie-file', '-f', help='Cookie 保存路径')
    login_parser.add_argument('--qr-output', '-q', help='二维码图片保存路径')
    login_parser.add_argument('--no-headless', action='store_true', help='显示浏览器窗口')
    login_parser.add_argument('--timeout', '-t', type=int, default=120, help='登录超时时间（秒）')
    login_parser.add_argument('--notify', '-n', action='store_true', help='登录成功后发送 Telegram 通知')
    login_parser.add_argument('--config', '-c', help='Telegram 配置文件路径')
    login_parser.add_argument('--proxy', '-p', help='代理服务器地址')
    
    # check 命令
    check_parser = subparsers.add_parser('check', help='检查 Cookie 是否有效')
    check_parser.add_argument('--cookie-file', '-f', help='Cookie 文件路径')
    
    # setup-notify 命令
    setup_parser = subparsers.add_parser('setup-notify', help='配置 Telegram 通知')
    setup_parser.add_argument('--bot-token', required=True, help='Telegram Bot Token')
    setup_parser.add_argument('--chat-id', required=True, help='Telegram Chat ID')
    setup_parser.add_argument('--config', '-c', help='配置文件保存路径')
    
    args = parser.parse_args()
    
    if args.command == 'login':
        result = asyncio.run(csdn_login(
            cookie_file=args.cookie_file,
            qr_output=args.qr_output,
            headless=not args.no_headless,
            timeout=args.timeout,
            notify=args.notify,
            config_file=args.config,
            proxy=args.proxy
        ))
        if result["success"]:
            print("LOGIN_SUCCESS")
        else:
            print(f"LOGIN_FAILED:{result['message']}")
        sys.exit(0 if result["success"] else 1)
    
    elif args.command == 'check':
        valid = asyncio.run(check_cookie(cookie_file=args.cookie_file))
        sys.exit(0 if valid else 1)
    
    elif args.command == 'setup-notify':
        config_path = Path(args.config) if args.config else DEFAULT_CONFIG_FILE
        config_path.parent.mkdir(parents=True, exist_ok=True)
        
        config = {
            "bot_token": args.bot_token,
            "chat_id": args.chat_id
        }
        
        with open(config_path, 'w') as f:
            json.dump(config, f, indent=2)
        
        print(f"✅ Telegram 配置已保存到: {config_path}")
        
        # 测试发送
        if send_telegram_notification("🔔 CSDN Publisher 通知已配置成功！", str(config_path)):
            print("✅ 测试消息发送成功")
        else:
            print("⚠️ 测试消息发送失败，请检查配置")
    
    else:
        parser.print_help()


if __name__ == '__main__':
    main()
