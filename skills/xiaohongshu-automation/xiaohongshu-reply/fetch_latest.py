#!/usr/bin/env python3
"""
获取最新小红书评论
"""

import json
import os
from time import sleep
from playwright.sync_api import sync_playwright

def main():
    cookie_path = os.path.expanduser("~/.openclaw/secrets/xiaohongshu.json")
    
    with open(cookie_path, 'r') as f:
        cookie_dict = json.load(f)
    
    cookies = []
    for name, value in cookie_dict.items():
        cookies.append({'name': name, 'value': value, 'domain': '.xiaohongshu.com', 'path': '/'})
    
    with sync_playwright() as playwright:
        browser = playwright.chromium.launch(headless=True)
        context = browser.new_context()
        context.add_cookies(cookies)
        page = context.new_page()
        page.set_default_timeout(20000)
        
        page.goto('https://www.xiaohongshu.com/notification')
        sleep(4)
        
        # 点击评论标签
        page.locator('text=评论和@').first.click()
        sleep(3)
        
        # 尝试点击"查看更多历史消息"加载更多
        try:
            for _ in range(3):
                more_btn = page.get_by_text('查看更多历史消息')
                if more_btn.count() > 0:
                    more_btn.first.click()
                    sleep(2)
        except:
            pass
        
        # 提取评论内容
        body_text = page.text_content('body')
        
        # 保存到文件
        with open('./latest_comments.txt', 'w', encoding='utf-8') as f:
            f.write(body_text)
        
        print("✅ 已保存最新评论到 latest_comments.txt")
        
        # 截图
        page.screenshot(path='./debug_latest.png', full_page=True)
        print("📸 已截图")
        
        browser.close()

if __name__ == "__main__":
    main()
