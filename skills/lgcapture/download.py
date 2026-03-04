#!/usr/bin/env python3
"""
抖音视频抓取脚本 v2.0
使用 Playwright 抓取抖音视频
优化：支持更多 URL 格式，提升抓取速度
"""

import asyncio
import re
import sys
import os
import time
import requests
from playwright.async_api import async_playwright

def extract_video_id(url):
    """从抖音链接提取视频 ID"""
    
    # 先处理短链接，解析重定向获取真实视频 ID
    if 'v.douyin.com' in url and '/' in url:
        try:
            import requests
            resp = requests.head(url, allow_redirects=True, timeout=10)
            final_url = resp.url
            # 从最终 URL 中提取视频 ID
            patterns = [
                r'douyin\.com/video/(\d+)',
                r'iesdouyin\.com/share/video/(\d+)',
            ]
            for pattern in patterns:
                match = re.search(pattern, final_url)
                if match:
                    return match.group(1)
        except:
            pass
    
    patterns = [
        r'douyin\.com/video/(\d+)',
        r'douyin\.com/(\w+)',
        r'iesdouyin\.com/share/video/(\d+)',
        r'iesdouyin\.com/share/note/(\d+)',
    ]
    
    for pattern in patterns:
        match = re.search(pattern, url)
        if match:
            return match.group(1)
    return None

async def download_douyin_video(url, output_file=None):
    """抓取抖音视频"""
    
    start_time = time.time()
    
    video_id = extract_video_id(url)
    if not video_id:
        print("Error: 无法从链接中提取视频 ID", file=sys.stderr)
        return None
    
    if not output_file:
        output_file = f"/tmp/douyin_{video_id}.mp4"
    
    async with async_playwright() as p:
        # 使用反自动化检测参数
        browser = await p.chromium.launch(
            headless=True, 
            args=['--disable-blink-features=AutomationControlled']
        )
        
        # 模拟手机浏览器
        context = await browser.new_context(
            viewport={'width': 390, 'height': 844},
            user_agent='Mozilla/5.0 (iPhone 15 Pro; CPU iPhone OS 17_0 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/17.0 Mobile/15E148 Safari/604.1'
        )
        page = await context.new_page()
        
        video_url = None
        
        def capture_response(response):
            nonlocal video_url
            url = response.url
            # 优先匹配 zjcdn.com
            if 'zjcdn.com' in url and ('video' in url or '.mp4' in url):
                video_url = url
        
        page.on('response', capture_response)
        
        # 构建 URL
        if 'iesdouyin.com' in url:
            full_url = f"https://www.douyin.com/video/{video_id}"
        else:
            full_url = url if 'douyin.com/video' in url else f"https://www.douyin.com/video/{video_id}"
        
        print(f"访问页面: {full_url}", file=sys.stderr)
        
        try:
            await page.goto(full_url, wait_until='domcontentloaded', timeout=20000)
            await page.wait_for_timeout(15000)  # 等待视频加载
        except Exception as e:
            print(f"Error: 页面加载失败: {e}", file=sys.stderr)
            await browser.close()
            return None
        
        # 方法1: 从网络请求获取
        if not video_url:
            # 方法2: 从页面元素获取
            video_url = await page.evaluate('''() => {
                let video = document.querySelector('video');
                return video ? video.src : null;
            }''')
        
        await browser.close()
        
        # 下载视频
        if video_url:
            # 如果是相对路径，转换为完整 URL
            if video_url.startswith('/'):
                video_url = 'https://m.douyin.com' + video_url
            
            print(f"下载视频: {video_url[:80]}...", file=sys.stderr)
            
            try:
                resp = requests.get(
                    video_url, 
                    headers={
                        'User-Agent': 'Mozilla/5.0 (iPhone; CPU iPhone OS 17_0 like Mac OS X) AppleWebKit/605.1.15',
                        'Referer': 'https://www.douyin.com/'
                    },
                    timeout=60
                )
                
                if resp.status_code == 200:
                    with open(output_file, 'wb') as f:
                        f.write(resp.content)
                    
                    elapsed_time = time.time() - start_time
                    print(f"视频已保存: {output_file}", file=sys.stderr)
                    print(f"抓取完成，耗时: {elapsed_time:.2f} 秒", file=sys.stderr)
                    return output_file
                else:
                    print(f"Error: 下载失败, 状态码: {resp.status_code}", file=sys.stderr)
            except Exception as e:
                print(f"Error: 下载异常: {e}", file=sys.stderr)
        else:
            print("Error: 未找到视频 URL", file=sys.stderr)
        
        return None

def main():
    if len(sys.argv) < 2:
        print("Usage: download.py <抖音链接> [输出文件]")
        print("Example: download.py https://v.douyin.com/xxx /tmp/video.mp4")
        sys.exit(1)
    
    url = sys.argv[1]
    output_file = sys.argv[2] if len(sys.argv) > 2 else None
    
    result = asyncio.run(download_douyin_video(url, output_file))
    
    if result:
        print(result)
        sys.exit(0)
    else:
        print("Error: 视频抓取失败", file=sys.stderr)
        sys.exit(1)

if __name__ == "__main__":
    main()
