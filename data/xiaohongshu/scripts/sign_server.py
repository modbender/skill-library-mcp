#!/usr/bin/env python3
"""
小红书签名服务器 - 使用用户自己的 Cookie
启动后保持运行，提供签名 API
"""

import asyncio
import json
import os
import sys
from pathlib import Path
from aiohttp import web
from playwright.async_api import async_playwright
from dotenv import load_dotenv

# 加载环境变量
env_path = Path(__file__).parent.parent / '.env'
load_dotenv(env_path)

STEALTH_JS = Path(__file__).parent / 'stealth.min.js'
PORT = 5006

# 全局 playwright 对象
browser = None
page = None

def parse_cookie_string(cookie_str):
    """解析 cookie 字符串为字典"""
    cookies = {}
    for item in cookie_str.split(';'):
        item = item.strip()
        if '=' in item:
            key, value = item.split('=', 1)
            cookies[key.strip()] = value.strip()
    return cookies

async def init_browser():
    """初始化浏览器和页面"""
    global browser, page
    
    cookie_str = os.getenv('XHS_COOKIE', '')
    if not cookie_str:
        print("❌ 未设置 XHS_COOKIE 环境变量")
        sys.exit(1)
    
    cookie_dict = parse_cookie_string(cookie_str)
    a1 = cookie_dict.get('a1', '')
    
    print(f"🚀 启动浏览器...")
    print(f"📝 a1 值: {a1[:20]}...")
    
    playwright = await async_playwright().start()
    browser = await playwright.chromium.launch(headless=True)
    context = await browser.new_context()
    
    # 加载 stealth.js
    if STEALTH_JS.exists():
        await context.add_init_script(path=str(STEALTH_JS))
        print(f"✅ 加载 stealth.js")
    
    page = await context.new_page()
    
    # 访问小红书
    print(f"🌐 访问小红书...")
    await page.goto("https://www.xiaohongshu.com")
    
    # 设置 cookies
    cookies_to_add = []
    for key, value in cookie_dict.items():
        cookies_to_add.append({
            'name': key,
            'value': value,
            'domain': '.xiaohongshu.com',
            'path': '/'
        })
    
    await context.add_cookies(cookies_to_add)
    print(f"🍪 设置了 {len(cookies_to_add)} 个 cookies")
    
    # 刷新页面使 cookies 生效
    await page.reload()
    await asyncio.sleep(2)
    
    print(f"✅ 浏览器初始化完成")
    return a1

async def sign_request(request):
    """签名 API 端点"""
    global page
    
    try:
        data = await request.json()
        uri = data.get('uri', '')
        payload = data.get('data')
        a1 = data.get('a1', '')
        
        if not uri:
            return web.json_response({'error': 'uri is required'}, status=400)
        
        # 构建签名字符串
        if payload:
            if isinstance(payload, dict):
                sign_str = uri + json.dumps(payload, separators=(',', ':'), ensure_ascii=False)
            else:
                sign_str = uri + str(payload)
        else:
            sign_str = uri
        
        # 调用页面的签名函数
        try:
            result = await page.evaluate(
                "([url, data]) => window._webmsxyw(url, data)",
                [uri, payload]
            )
            
            return web.json_response({
                'x-s': result.get('X-s', ''),
                'x-t': str(result.get('X-t', ''))
            })
        except Exception as e:
            print(f"⚠️ 签名失败: {e}")
            # 尝试刷新页面
            await page.reload()
            await asyncio.sleep(1)
            return web.json_response({'error': str(e)}, status=500)
            
    except Exception as e:
        return web.json_response({'error': str(e)}, status=500)

async def health_check(request):
    """健康检查"""
    return web.json_response({'status': 'ok', 'port': PORT})

async def main():
    a1 = await init_browser()
    
    app = web.Application()
    app.router.add_post('/sign', sign_request)
    app.router.add_get('/health', health_check)
    
    runner = web.AppRunner(app)
    await runner.setup()
    site = web.TCPSite(runner, '127.0.0.1', PORT)
    await site.start()
    
    print(f"\n🎉 签名服务已启动: http://127.0.0.1:{PORT}")
    print(f"📝 使用的 a1: {a1[:20]}...")
    print(f"\n按 Ctrl+C 停止服务\n")
    
    # 保持运行
    while True:
        await asyncio.sleep(3600)

if __name__ == '__main__':
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print("\n👋 服务已停止")
