#!/usr/bin/env python3
"""
B 站视频播放 - Skill 脚本
用法：python3 bilibili-player.py "搜索关键词"
"""
from playwright.sync_api import sync_playwright
import subprocess
import sys

def search_and_open(keyword):
    """搜索 B 站并打开第一个视频"""
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        page = browser.new_page()
        
        print(f"🔍 Playwright 搜索：{keyword}")
        
        # 搜索
        search_url = f"https://search.bilibili.com/all?keyword={keyword}"
        page.goto(search_url, timeout=60000)
        page.wait_for_timeout(3000)
        
        # 获取第一个视频链接
        selectors = [
            "a[href*='/video/']",
            ".bili-video-card a",
        ]
        
        video_url = None
        for selector in selectors:
            element = page.query_selector(selector)
            if element:
                href = element.get_attribute("href")
                if href and "/video/" in href:
                    video_url = f"https:{href}" if href.startswith("//") else href
                    print(f"✅ 找到视频：{video_url}")
                    break
        
        if video_url:
            # 用 open 在当前浏览器打开
            subprocess.run(["open", video_url])
            print("🎬 已在浏览器中打开！")
        else:
            # 没找到视频，打开搜索页面
            print("❌ 没找到视频，打开搜索页面")
            subprocess.run(["open", search_url])
        
        browser.close()

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("用法：python3 bilibili-player.py \"搜索关键词\"")
        sys.exit(1)
    
    keyword = " ".join(sys.argv[1:])
    search_and_open(keyword)
