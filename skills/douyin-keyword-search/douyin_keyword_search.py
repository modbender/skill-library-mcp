#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
抖音关键词搜索文章抓取工具
使用 Playwright 浏览器自动化抓取抖音搜索结果
"""

import argparse
import json
import sys
import os
from datetime import datetime

def parse_args():
    """解析命令行参数"""
    parser = argparse.ArgumentParser(description='抖音关键词搜索抓取工具')
    parser.add_argument('--keyword', '-k', required=True, help='搜索关键词')
    parser.add_argument('--output', '-o', default='json', choices=['json', 'csv', 'txt'],
                       help='输出格式 (默认: json)')
    parser.add_argument('--limit', '-l', type=int, default=20,
                       help='抓取数量限制 (默认: 20)')
    parser.add_argument('--headless', action='store_true',
                       help='无头模式运行（不显示浏览器窗口）')
    parser.add_argument('--output-file', '-f',
                       help='输出文件路径 (默认打印到控制台)')
    parser.add_argument('--browser', '-b', default='chrome', choices=['chrome', 'chromium', 'firefox', 'msedge'],
                       help='浏览器类型 (默认: chrome，使用本地Chrome)')
    return parser.parse_args()

def check_playwright():
    """检查 Playwright 是否安装"""
    try:
        from playwright.sync_api import sync_playwright
        return True
    except ImportError:
        return False

def install_dependencies():
    """安装依赖"""
    print("正在安装 Playwright...")
    os.system(f'"{sys.executable}" -m pip install playwright')
    os.system(f'"{sys.executable}" -m playwright install chromium')
    print("依赖安装完成，请重新运行脚本")
    sys.exit(0)

def get_chrome_path():
    """获取本地 Chrome 浏览器路径"""
    chrome_paths = [
        r"C:\Program Files\Google\Chrome\Application\chrome.exe",
        r"C:\Program Files (x86)\Google\Chrome\Application\chrome.exe",
        os.path.expandvars(r"%LOCALAPPDATA%\Google\Chrome\Application\chrome.exe"),
        os.path.expandvars(r"%PROGRAMFILES%\Google\Chrome\Application\chrome.exe"),
    ]
    for path in chrome_paths:
        if os.path.exists(path):
            return path
    return None

def get_edge_path():
    """获取本地 Edge 浏览器路径"""
    edge_paths = [
        r"C:\Program Files (x86)\Microsoft\Edge\Application\msedge.exe",
        r"C:\Program Files\Microsoft\Edge\Application\msedge.exe",
    ]
    for path in edge_paths:
        if os.path.exists(path):
            return path
    return None

def scrape_douyin_search(keyword, limit=20, headless=False, browser_type='chrome'):
    """
    抓取抖音搜索结果

    注意：抖音需要登录才能查看完整搜索结果
    建议首次运行时不使用 headless 模式，手动登录后再使用
    """
    from playwright.sync_api import sync_playwright

    results = []

    with sync_playwright() as p:
        # 启动浏览器
        launch_options = {'headless': headless}

        if browser_type == 'chrome':
            chrome_path = get_chrome_path()
            if chrome_path:
                launch_options['executable_path'] = chrome_path
                print(f"使用本地 Chrome: {chrome_path}")
            else:
                print("未找到本地 Chrome，使用 Playwright 内置浏览器")
        elif browser_type == 'msedge':
            edge_path = get_edge_path()
            if edge_path:
                launch_options['executable_path'] = edge_path
                print(f"使用本地 Edge: {edge_path}")
            else:
                print("未找到本地 Edge，使用 Playwright 内置浏览器")

        browser = p.chromium.launch(**launch_options)
        context = browser.new_context(
            viewport={'width': 1280, 'height': 800},
            user_agent='Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36'
        )
        page = context.new_page()

        try:
            # 访问抖音搜索页面
            search_url = f"https://www.douyin.com/search/{keyword}"
            print(f"正在访问: {search_url}")
            page.goto(search_url, wait_until='networkidle', timeout=60000)

            # 等待页面加载
            print("等待页面加载...")
            page.wait_for_timeout(3000)

            # 检查是否需要登录
            if page.locator('text=登录').count() > 0:
                print("\n" + "="*50)
                print("提示：检测到需要登录")
                print("请在浏览器中手动登录，登录后按 Enter 继续...")
                print("="*50 + "\n")
                if not headless:
                    input("登录完成后按 Enter 继续...")

            # 滚动加载更多内容
            scroll_count = max(1, limit // 10)
            for i in range(scroll_count):
                page.evaluate('window.scrollTo(0, document.body.scrollHeight)')
                page.wait_for_timeout(1500)

            # 尝试多种选择器定位视频卡片
            selectors = [
                'div[data-e2e="search-video-item"]',
                '.search-card',
                '[class*="VideoCard"]',
                '[class*="video-card"]'
            ]

            items = []
            for selector in selectors:
                try:
                    found = page.locator(selector).all()
                    if found:
                        items = found
                        print(f"找到 {len(items)} 个结果 (使用选择器: {selector})")
                        break
                except:
                    continue

            if not items:
                # 尝试获取页面内容用于调试
                print("警告：未能找到视频卡片，尝试获取页面信息...")
                content = page.content()
                print(f"页面内容长度: {len(content)}")

                # 截图保存用于调试
                screenshot_path = os.path.join(os.path.dirname(__file__), 'debug_screenshot.png')
                page.screenshot(path=screenshot_path)
                print(f"已保存截图到: {screenshot_path}")

            # 解析每个视频卡片
            for i, item in enumerate(items[:limit]):
                try:
                    data = {}

                    # 提取标题/描述
                    title_selectors = ['[class*="title"]', '[class*="desc"]', 'h3', 'h2']
                    for sel in title_selectors:
                        try:
                            title_elem = item.locator(sel).first
                            if title_elem:
                                data['title'] = title_elem.inner_text(timeout=1000)
                                break
                        except:
                            pass

                    # 提取作者
                    try:
                        author_elem = item.locator('[class*="author"], [class*="name"]').first
                        data['author'] = author_elem.inner_text(timeout=1000)
                    except:
                        data['author'] = ''

                    # 提取链接
                    try:
                        link_elem = item.locator('a').first
                        href = link_elem.get_attribute('href', timeout=1000)
                        if href:
                            if href.startswith('/'):
                                data['url'] = f"https://www.douyin.com{href}"
                            else:
                                data['url'] = href
                    except:
                        data['url'] = ''

                    # 提取互动数据
                    try:
                        stats = item.locator('[class*="stats"], [class*="count"]').all_inner_texts()
                        data['stats'] = stats if stats else []
                    except:
                        data['stats'] = []

                    data['keyword'] = keyword
                    data['crawl_time'] = datetime.now().isoformat()

                    if data.get('title'):
                        results.append(data)

                except Exception as e:
                    print(f"解析第 {i+1} 个项目时出错: {e}")
                    continue

        except Exception as e:
            print(f"抓取过程出错: {e}")

        finally:
            browser.close()

    return results

def format_output(results, output_format, keyword):
    """格式化输出结果"""
    if output_format == 'json':
        return json.dumps(results, ensure_ascii=False, indent=2)
    elif output_format == 'csv':
        import csv
        import io
        output = io.StringIO()
        if results:
            writer = csv.DictWriter(output, fieldnames=['title', 'author', 'url', 'stats', 'keyword', 'crawl_time'])
            writer.writeheader()
            writer.writerows(results)
        return output.getvalue()
    else:  # txt
        lines = []
        for i, r in enumerate(results, 1):
            lines.append(f"--- 结果 {i} ---")
            lines.append(f"标题: {r.get('title', 'N/A')}")
            lines.append(f"作者: {r.get('author', 'N/A')}")
            lines.append(f"链接: {r.get('url', 'N/A')}")
            lines.append(f"互动数据: {', '.join(r.get('stats', []))}")
            lines.append("")
        return '\n'.join(lines)

def main():
    args = parse_args()

    # 检查依赖
    if not check_playwright():
        print("Playwright 未安装")
        response = input("是否现在安装? (y/n): ").strip().lower()
        if response == 'y':
            install_dependencies()
        else:
            print("已取消。请手动运行: pip install playwright && playwright install chromium")
            sys.exit(1)

    print(f"\n开始抓取抖音搜索关键词: {args.keyword}")
    print(f"数量限制: {args.limit}")
    print(f"输出格式: {args.output}")
    print(f"浏览器类型: {args.browser}")
    print("-" * 50)

    # 执行抓取
    results = scrape_douyin_search(
        keyword=args.keyword,
        limit=args.limit,
        headless=args.headless,
        browser_type=args.browser
    )

    print(f"\n抓取完成，共获取 {len(results)} 条结果")
    print("-" * 50)

    # 格式化输出
    output = format_output(results, args.output, args.keyword)

    if args.output_file:
        with open(args.output_file, 'w', encoding='utf-8') as f:
            f.write(output)
        print(f"结果已保存到: {args.output_file}")
    else:
        print(output)

if __name__ == '__main__':
    main()