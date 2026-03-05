#!/usr/bin/env python3
"""Playwright + Stealth 模式 - 绕过机器人检测"""
import sys
sys.path.insert(0, '/home/Kano/.playwright-env/lib/python3.11/site-packages')

from playwright.sync_api import sync_playwright

def screenshot_with_stealth(url='https://www.bilibili.com', output_path=None):
    """
    使用Stealth模式截图，绕过反爬虫检测
    
    Args:
        url: 要访问的网址
        output_path: 截图保存路径（默认自动生成）
    """
    if output_path is None:
        from datetime import datetime
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        output_path = f'/home/Kano/.openclaw/workspace/screenshot_{timestamp}.png'
    
    with sync_playwright() as p:
        # 启动浏览器（带stealth参数）
        browser = p.chromium.launch(
            headless=True,
            args=[
                '--no-sandbox',
                '--disable-gpu',
                '--disable-dev-shm-usage',
                '--disable-setuid-sandbox',
                '--disable-accelerated-2d-canvas',
                '--disable-accelerated-jpeg-decoding',
                '--disable-accelerated-mjpeg-decode',
                '--disable-accelerated-video-decode',
                '--disable-app-list-dismiss-on-blur',
                '--disable-background-networking',
                '--disable-background-timer-throttling',
                '--disable-backgrounding-occluded-windows',
                '--disable-breakpad',
                '--disable-client-side-phishing-detection',
                '--disable-component-update',
                '--disable-default-apps',
                '--disable-features=TranslateUI',
                '--disable-hang-monitor',
                '--disable-ipc-flooding-protection',
                '--disable-popup-blocking',
                '--disable-prompt-on-repost',
                '--disable-renderer-backgrounding',
                '--disable-sync',
                '--force-color-profile=srgb',
                '--metrics-recording-only',
                '--no-first-run',
                '--safebrowsing-disable-auto-update',
            ]
        )
        
        # 创建上下文（模拟真实设备指纹）
        context = browser.new_context(
            viewport={'width': 1920, 'height': 1080},
            user_agent='Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
            locale='zh-CN',
            timezone_id='Asia/Shanghai',
            permissions=['notifications'],
            color_scheme='light',
        )
        
        # 添加 stealth 脚本（移除 webdriver 标记等）
        context.add_init_script("""
            Object.defineProperty(navigator, 'webdriver', {
                get: () => undefined
            });
            Object.defineProperty(navigator, 'plugins', {
                get: () => [1, 2, 3, 4, 5]
            });
            window.chrome = { runtime: {} };
        """)
        
        page = context.new_page()
        
        # 访问页面
        print(f"正在打开: {url}")
        page.goto(url, wait_until='networkidle', timeout=60000)
        
        # 等待一下确保页面渲染完成
        page.wait_for_timeout(2000)
        
        # 截图
        page.screenshot(path=output_path, full_page=False)
        print(f"✅ 截图已保存: {output_path}")
        
        # 获取页面信息
        title = page.title()
        url_final = page.url
        print(f"📄 页面标题: {title}")
        print(f"🔗 最终URL: {url_final}")
        
        browser.close()
        return output_path, title, url_final

def auto_fill_form(url, form_data, submit_selector=None):
    """
    自动填写表单
    
    Args:
        url: 表单页面URL
        form_data: 字典，格式为 {'selector': 'value'}
        submit_selector: 提交按钮的选择器（可选）
    """
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True, args=['--no-sandbox', '--disable-gpu'])
        context = browser.new_context(viewport={'width': 1920, 'height': 1080})
        page = context.new_page()
        
        page.goto(url, wait_until='networkidle')
        
        # 填写表单
        for selector, value in form_data.items():
            print(f"填写 {selector}: {value}")
            page.fill(selector, value)
            page.wait_for_timeout(500)  # 模拟人类输入间隔
        
        # 点击提交
        if submit_selector:
            print(f"点击提交: {submit_selector}")
            page.click(submit_selector)
            page.wait_for_timeout(3000)
        
        # 截图保存结果
        screenshot_path = '/home/Kano/.openclaw/workspace/form_result.png'
        page.screenshot(path=screenshot_path)
        print(f"✅ 表单提交完成，截图: {screenshot_path}")
        
        browser.close()
        return screenshot_path

if __name__ == '__main__':
    import argparse
    parser = argparse.ArgumentParser(description='Playwright 自动化工具')
    parser.add_argument('url', nargs='?', default='https://www.bilibili.com', help='要访问的URL')
    parser.add_argument('-o', '--output', help='截图输出路径')
    args = parser.parse_args()
    
    try:
        path, title, final_url = screenshot_with_stealth(args.url, args.output)
        print(f"\n🎉 完成！")
    except Exception as e:
        print(f"❌ 错误: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
