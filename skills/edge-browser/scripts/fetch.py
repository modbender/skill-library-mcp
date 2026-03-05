#!/usr/bin/env python3
"""
Edge Browser Controller
使用 Playwright 控制 Microsoft Edge 浏览器访问网页并提取内容
"""

import sys
import json
import argparse
from playwright.sync_api import sync_playwright

def fetch_url(url: str, wait_time: int = 3) -> dict:
    """
    使用 Edge 浏览器访问指定 URL 并提取页面内容
    
    Args:
        url: 要访问的 URL
        wait_time: 页面加载后等待时间（秒），用于等待动态内容加载
    
    Returns:
        包含页面信息的字典
    """
    try:
        with sync_playwright() as p:
            # 尝试启动 Edge（Windows 上通常是 msedge.exe）
            # 首先尝试 Edge 的默认路径
            edge_paths = [
                "C:\\Program Files (x86)\\Microsoft\\Edge\\Application\\msedge.exe",
                "C:\\Program Files\\Microsoft\\Edge\\Application\\msedge.exe",
            ]
            
            browser = None
            for edge_path in edge_paths:
                try:
                    browser = p.chromium.launch(
                        executable_path=edge_path,
                        headless=True  # 无头模式
                    )
                    break
                except:
                    continue
            
            # 如果 Edge 启动失败，退回到普通 Chromium
            if browser is None:
                print("Warning: Edge not found, falling back to Chromium", file=sys.stderr)
                browser = p.chromium.launch(headless=True)
            
            context = browser.new_context(
                user_agent="Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36 Edg/120.0.0.0"
            )
            page = context.new_page()
            
            # 访问页面
            page.goto(url, wait_until="networkidle")
            
            # 等待动态内容加载
            page.wait_for_timeout(wait_time * 1000)
            
            # 提取页面信息
            result = {
                "url": url,
                "title": page.title(),
                "content": page.content(),
                "text": page.inner_text("body"),
                "status": "success"
            }
            
            context.close()
            browser.close()
            
            return result
            
    except Exception as e:
        return {
            "url": url,
            "status": "error",
            "error": str(e)
        }

def main():
    parser = argparse.ArgumentParser(description="Edge Browser Controller")
    parser.add_argument("url", help="URL to fetch")
    parser.add_argument("--wait", type=int, default=3, help="Wait time in seconds after page load")
    parser.add_argument("--output", "-o", help="Output file (default: stdout)")
    
    args = parser.parse_args()
    
    result = fetch_url(args.url, args.wait)
    
    output = json.dumps(result, ensure_ascii=False, indent=2)
    
    if args.output:
        with open(args.output, "w", encoding="utf-8") as f:
            f.write(output)
    else:
        # Fix encoding for Windows console
        import io
        sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')
        print(output)

if __name__ == "__main__":
    main()
