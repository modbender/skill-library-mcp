#!/usr/bin/env python3
"""
视频抓取工具
支持抖音和推特视频抓取
"""

import sys
import os
import subprocess
import re
import asyncio
import requests
from playwright.async_api import async_playwright

# ===== 配置 =====
DASHSCOPE_API_KEY = "sk-c0f66bb7aeff4b94810691214a1477fd"

def extract_douyin_id(url):
    """从抖音链接提取视频ID"""
    if 'v.douyin.com' in url:
        try:
            resp = requests.head(url, allow_redirects=True, timeout=10)
            url = resp.url
        except:
            pass
    
    patterns = [
        r'douyin\.com/video/(\d+)',
        r'iesdouyin\.com/share/video/(\d+)',
    ]
    for pattern in patterns:
        match = re.search(pattern, url)
        if match:
            return match.group(1)
    return None

async def download_douyin(url, output_file=None):
    """抓取抖音视频"""
    video_id = extract_douyin_id(url)
    if not video_id:
        print("Error: 无法提取抖音视频ID", file=sys.stderr)
        return None
    
    if not output_file:
        output_file = f"/tmp/douyin_{video_id}.mp4"
    
    async with async_playwright() as p:
        browser = await p.chromium.launch(
            headless=True,
            args=['--disable-blink-features=AutomationControlled']
        )
        context = await browser.new_context(
            viewport={'width': 390, 'height': 844},
            user_agent='Mozilla/5.0 (iPhone 15 Pro; CPU iPhone OS 17_0 like Mac OS X) AppleWebKit/605.1.15'
        )
        page = await context.new_page()
        
        video_url = None
        
        def capture_response(response):
            nonlocal video_url
            if 'zjcdn.com' in response.url and 'video' in response.url:
                video_url = response.url
        
        page.on('response', capture_response)
        
        full_url = f"https://www.douyin.com/video/{video_id}"
        
        try:
            await page.goto(full_url, wait_until='domcontentloaded', timeout=20000)
            await page.wait_for_timeout(15000)
        except Exception as e:
            print(f"Error: {e}", file=sys.stderr)
            await browser.close()
            return None
        
        if not video_url:
            video_url = await page.evaluate('() => document.querySelector("video")?.src')
        
        await browser.close()
        
        if video_url:
            if video_url.startswith('/'):
                video_url = 'https://m.douyin.com' + video_url
            
            try:
                resp = requests.get(video_url, headers={'User-Agent': 'Mozilla/5.0'}, timeout=60)
                if resp.status_code == 200:
                    with open(output_file, 'wb') as f:
                        f.write(resp.content)
                    return output_file
            except Exception as e:
                print(f"Error: {e}", file=sys.stderr)
        
        return None

def download_twitter(url, output_file=None):
    """抓取推特视频"""
    if not output_file:
        output_file = "/tmp/twitter_video.mp4"
    
    cmd = ["yt-dlp", "-o", output_file, "--no-warnings", url]
    
    try:
        result = subprocess.run(cmd, capture_output=True, text=True, timeout=120)
        if result.returncode == 0:
            return output_file
    except Exception as e:
        print(f"Error: {e}", file=sys.stderr)
    
    return None

def main():
    if len(sys.argv) < 3:
        print("Usage: video_crawler.py <平台> <链接> [输出文件]")
        print("平台: douyin, twitter")
        sys.exit(1)
    
    platform = sys.argv[1]
    url = sys.argv[2]
    output = sys.argv[3] if len(sys.argv) > 3 else None
    
    if platform == "douyin":
        result = asyncio.run(download_douyin(url, output))
    elif platform == "twitter":
        result = download_twitter(url, output)
    else:
        print(f"Error: 不支持的平台 {platform}", file=sys.stderr)
        sys.exit(1)
    
    if result:
        print(result)
    else:
        print("Error: 下载失败", file=sys.stderr)
        sys.exit(1)

if __name__ == "__main__":
    main()
