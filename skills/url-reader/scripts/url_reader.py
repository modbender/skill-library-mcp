#!/usr/bin/env python3
"""
URL Reader - 智能网页内容读取器
策略：Firecrawl（首选）→ Jina（备选）→ Playwright（兜底）
自动保存内容和图片到指定目录
"""

import os
import sys
import json
import asyncio
import requests
import re
import hashlib
from urllib.parse import urlparse
from pathlib import Path
from datetime import datetime

# 配置
FIRECRAWL_API_KEY = os.environ.get("FIRECRAWL_API_KEY", "")
JINA_BASE_URL = "https://r.jina.ai/"
SCRIPT_DIR = Path(__file__).parent
DATA_DIR = SCRIPT_DIR.parent / "data"
WECHAT_AUTH_FILE = DATA_DIR / "wechat_auth.json"

# 默认保存目录
DEFAULT_OUTPUT_DIR = "/Users/ys/laoyang知识库/nickys/素材"


def identify_platform(url: str) -> dict:
    """识别URL所属平台"""
    parsed = urlparse(url)
    domain = parsed.netloc.lower()

    platforms = {
        'wechat': {
            'name': '微信公众号',
            'domains': ['mp.weixin.qq.com'],
            'need_login': True
        },
        'xiaohongshu': {
            'name': '小红书',
            'domains': ['xiaohongshu.com', 'xhslink.com'],
            'need_login': False
        },
        'toutiao': {
            'name': '今日头条',
            'domains': ['toutiao.com'],
            'need_login': False
        },
        'douyin': {
            'name': '抖音',
            'domains': ['douyin.com', 'v.douyin.com'],
            'need_login': False
        },
        'taobao': {
            'name': '淘宝',
            'domains': ['taobao.com', 'item.taobao.com'],
            'need_login': True
        },
        'tmall': {
            'name': '天猫',
            'domains': ['tmall.com', 'detail.tmall.com'],
            'need_login': True
        },
        'jd': {
            'name': '京东',
            'domains': ['jd.com', 'item.jd.com'],
            'need_login': False
        },
        'zhihu': {
            'name': '知乎',
            'domains': ['zhihu.com', 'zhuanlan.zhihu.com'],
            'need_login': False
        },
        'weibo': {
            'name': '微博',
            'domains': ['weibo.com', 'm.weibo.cn'],
            'need_login': True
        },
        'bilibili': {
            'name': 'B站',
            'domains': ['bilibili.com', 'b23.tv'],
            'need_login': False
        },
        'baidu': {
            'name': '百度',
            'domains': ['baidu.com', 'baijiahao.baidu.com'],
            'need_login': False
        },
    }

    for platform_id, info in platforms.items():
        for d in info['domains']:
            if d in domain:
                return {'id': platform_id, **info}

    return {
        'id': 'generic',
        'name': '通用网站',
        'domains': [],
        'need_login': False
    }


def read_with_firecrawl(url: str) -> dict:
    """策略A：使用 Firecrawl API 读取"""
    if not FIRECRAWL_API_KEY:
        return {'success': False, 'error': 'FIRECRAWL_API_KEY 未设置'}

    try:
        from firecrawl import Firecrawl
        app = Firecrawl(api_key=FIRECRAWL_API_KEY)
        result = app.scrape(url)

        if result:
            # Firecrawl v2 返回 Document 对象
            markdown = getattr(result, 'markdown', '') or ''
            metadata = getattr(result, 'metadata', None)
            if metadata:
                metadata = metadata.model_dump() if hasattr(metadata, 'model_dump') else {}
            else:
                metadata = {}

            if markdown and len(markdown) > 100:
                # 检查是否是验证页面
                if '环境异常' in markdown or '验证' in markdown[:200]:
                    return {'success': False, 'error': '页面需要验证'}

                return {
                    'success': True,
                    'strategy': 'Firecrawl',
                    'content': markdown,
                    'metadata': metadata
                }

        return {'success': False, 'error': 'Firecrawl 返回内容为空'}

    except Exception as e:
        return {'success': False, 'error': f'Firecrawl 错误: {str(e)}'}


def read_with_jina(url: str) -> dict:
    """策略B-1：使用 Jina Reader API 读取（免费）"""
    try:
        jina_url = f"{JINA_BASE_URL}{url}"
        headers = {
            'Accept': 'text/markdown',
            'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36'
        }

        response = requests.get(jina_url, headers=headers, timeout=30)

        if response.status_code == 200:
            content = response.text

            # 检查是否是有效内容
            if '环境异常' in content or '完成验证' in content:
                return {'success': False, 'error': '页面需要验证'}

            if len(content) < 100:
                return {'success': False, 'error': '内容太短，可能读取失败'}

            return {
                'success': True,
                'strategy': 'Jina Reader',
                'content': content,
                'metadata': {}
            }

        return {'success': False, 'error': f'HTTP {response.status_code}'}

    except Exception as e:
        return {'success': False, 'error': f'Jina 错误: {str(e)}'}


async def read_with_playwright_async(url: str, platform_id: str) -> dict:
    """策略B-2：使用 Playwright 浏览器读取（需要登录态）"""
    try:
        from playwright.async_api import async_playwright
        import time

        # 检查是否有登录态
        auth_file = None
        if platform_id == 'wechat' and WECHAT_AUTH_FILE.exists():
            auth_file = str(WECHAT_AUTH_FILE)

        async with async_playwright() as p:
            # 使用移动端 User-Agent 可能更容易通过验证
            browser = await p.chromium.launch(headless=True)

            # 使用微信内置浏览器的 User-Agent
            mobile_ua = 'Mozilla/5.0 (iPhone; CPU iPhone OS 16_0 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Mobile/15E148 MicroMessenger/8.0.38(0x18002629) NetType/WIFI Language/zh_CN'

            if auth_file:
                context = await browser.new_context(
                    storage_state=auth_file,
                    user_agent=mobile_ua
                )
            else:
                context = await browser.new_context(
                    user_agent=mobile_ua
                )

            page = await context.new_page()

            await page.goto(url, wait_until="networkidle", timeout=30000)

            # 等待页面完全加载
            await page.wait_for_timeout(2000)

            # 检查是否需要验证
            content = await page.content()
            if '环境异常' in content or '完成验证' in content:
                # 尝试点击验证按钮
                verify_btn = await page.query_selector("text=去验证")
                if verify_btn:
                    await verify_btn.click()
                    await page.wait_for_timeout(3000)
                    await page.wait_for_load_state("networkidle", timeout=15000)
                    content = await page.content()

                if '环境异常' in content or '完成验证' in content:
                    await browser.close()
                    return {'success': False, 'error': '需要手动验证，请运行 setup 命令登录'}

            # 等待文章内容加载
            if platform_id == 'wechat':
                try:
                    await page.wait_for_selector('#js_content', timeout=10000)
                except:
                    pass

            # 提取内容
            if platform_id == 'wechat':
                result = await page.evaluate("""
                    () => {
                        const title = document.querySelector('#activity-name')?.innerText?.trim() || '';
                        const author = document.querySelector('#js_name')?.innerText?.trim() || '';
                        const content = document.querySelector('#js_content')?.innerText?.trim() || '';
                        const publishTime = document.querySelector('#publish_time')?.innerText?.trim() || '';
                        return { title, author, content, publishTime };
                    }
                """)
            else:
                # 通用提取
                result = await page.evaluate("""
                    () => {
                        const title = document.querySelector('h1')?.innerText?.trim() ||
                                     document.querySelector('title')?.innerText?.trim() || '';
                        const content = document.body.innerText || '';
                        return { title, author: '', content, publishTime: '' };
                    }
                """)

            await browser.close()

            if result.get('content') and len(result['content']) > 100:
                # 格式化为 Markdown
                markdown = f"# {result.get('title', '无标题')}\n\n"
                if result.get('author'):
                    markdown += f"**作者**: {result['author']}\n"
                if result.get('publishTime'):
                    markdown += f"**发布时间**: {result['publishTime']}\n"
                markdown += f"\n---\n\n{result.get('content', '')}"

                return {
                    'success': True,
                    'strategy': 'Playwright',
                    'content': markdown,
                    'metadata': {
                        'title': result.get('title', ''),
                        'author': result.get('author', ''),
                        'publishTime': result.get('publishTime', '')
                    }
                }

            return {'success': False, 'error': '页面内容提取失败'}

    except Exception as e:
        return {'success': False, 'error': f'Playwright 错误: {str(e)}'}


def read_with_playwright(url: str, platform_id: str) -> dict:
    """Playwright 同步包装"""
    return asyncio.run(read_with_playwright_async(url, platform_id))


def read_url(url: str, verbose: bool = True) -> dict:
    """
    智能读取URL内容
    策略顺序：Firecrawl → Jina → Playwright
    """
    # 识别平台
    platform = identify_platform(url)
    if verbose:
        print(f"📍 平台识别: {platform['name']}")

    errors = []

    # 策略1: Firecrawl（如果有 API Key）
    if FIRECRAWL_API_KEY:
        if verbose:
            print("🔄 尝试策略 A: Firecrawl...")
        result = read_with_firecrawl(url)
        if result.get('success'):
            if verbose:
                print("✅ Firecrawl 读取成功")
            result['platform'] = platform
            return result
        errors.append(f"Firecrawl: {result.get('error')}")
        if verbose:
            print(f"❌ {result.get('error')}")

    # 策略2: Jina Reader（免费，不需要登录的平台优先尝试）
    if not platform.get('need_login'):
        if verbose:
            print("🔄 尝试策略 B-1: Jina Reader...")
        result = read_with_jina(url)
        if result.get('success'):
            if verbose:
                print("✅ Jina Reader 读取成功")
            result['platform'] = platform
            return result
        errors.append(f"Jina: {result.get('error')}")
        if verbose:
            print(f"❌ {result.get('error')}")

    # 策略3: Playwright（需要登录的平台或前面都失败）
    if verbose:
        print("🔄 尝试策略 B-2: Playwright 浏览器...")
    result = read_with_playwright(url, platform['id'])
    if result.get('success'):
        if verbose:
            print("✅ Playwright 读取成功")
        result['platform'] = platform
        return result
    errors.append(f"Playwright: {result.get('error')}")
    if verbose:
        print(f"❌ {result.get('error')}")

    # 如果是需要登录的平台，Jina 作为最后尝试
    if platform.get('need_login'):
        if verbose:
            print("🔄 最后尝试: Jina Reader...")
        result = read_with_jina(url)
        if result.get('success'):
            if verbose:
                print("✅ Jina Reader 读取成功")
            result['platform'] = platform
            return result
        errors.append(f"Jina (fallback): {result.get('error')}")

    return {
        'success': False,
        'platform': platform,
        'errors': errors
    }


def format_output(result: dict, url: str) -> str:
    """格式化输出为 Markdown"""
    if not result.get('success'):
        output = ["# ❌ 读取失败\n"]
        output.append(f"**URL**: {url}")
        output.append(f"**平台**: {result.get('platform', {}).get('name', '未知')}")
        output.append("\n**尝试的策略及错误**:")
        for err in result.get('errors', []):
            output.append(f"- {err}")
        output.append("\n**建议**:")
        output.append("1. 如果是微信公众号，请运行 `python wechat_reader.py setup` 设置登录态")
        output.append("2. 设置 FIRECRAWL_API_KEY 环境变量以使用 Firecrawl")
        output.append("3. 或手动复制文章内容")
        return "\n".join(output)

    platform = result.get('platform', {})
    metadata = result.get('metadata', {})
    content = result.get('content', '')

    output = []
    output.append(f"**来源**: {platform.get('name', '未知')}")
    output.append(f"**读取策略**: {result.get('strategy', '未知')}")
    output.append(f"**原文链接**: {url}")
    output.append("\n---\n")
    output.append(content)

    return "\n".join(output)


# ============== 保存功能 ==============

def sanitize_filename(name: str, max_length: int = 50) -> str:
    """清理文件名，移除非法字符"""
    name = re.sub(r'[<>:"/\\|?*\n\r\t]', '', name)
    name = re.sub(r'\s+', ' ', name).strip()
    if len(name) > max_length:
        name = name[:max_length]
    return name or "untitled"


def extract_title_from_content(content: str) -> str:
    """从内容中提取标题"""
    # 尝试从 Markdown 一级标题提取
    match = re.search(r'^#\s+(.+)$', content, re.MULTILINE)
    if match:
        title = match.group(1).strip()
        # 排除一些无意义的标题
        if title and not title.startswith('来源') and not title.startswith('**') and len(title) > 2:
            return title

    # 尝试从 **标题**: 格式提取
    match = re.search(r'\*\*标题\*\*[：:]\s*(.+)', content)
    if match:
        return match.group(1).strip()

    # 尝试从第一个有意义的行提取
    lines = content.strip().split('\n')
    for line in lines:
        line = line.strip()
        # 跳过空行、元数据行
        if not line or line.startswith('**') or line.startswith('---') or line.startswith('#'):
            continue
        if len(line) > 5 and len(line) < 100:
            return line[:50]

    return "untitled"


def extract_images_from_content(content: str) -> list:
    """从内容中提取图片URL"""
    md_images = re.findall(r'!\[.*?\]\((https?://[^\s\)]+)\)', content)
    direct_images = re.findall(r'(https?://[^\s\)]+\.(?:jpg|jpeg|png|gif|webp|bmp)[^\s\)]*)', content, re.IGNORECASE)
    xhs_images = re.findall(r'(https?://sns-webpic[^\s\)]+)', content)
    feishu_images = re.findall(r'(https?://[^\s\)]*feishu[^\s\)]+\.(?:jpg|jpeg|png|gif|webp)[^\s\)]*)', content, re.IGNORECASE)
    qq_images = re.findall(r'(https?://docimg[^\s\)]+\.(?:jpg|jpeg|png|gif|webp)[^\s\)]*)', content, re.IGNORECASE)
    all_images = list(dict.fromkeys(md_images + direct_images + xhs_images + feishu_images + qq_images))
    return all_images


def download_image(url: str, save_dir: Path, index: int) -> str:
    """下载图片并返回本地文件名"""
    try:
        headers = {
            'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36',
            'Referer': 'https://www.xiaohongshu.com/'
        }
        response = requests.get(url, headers=headers, timeout=30)
        response.raise_for_status()

        content_type = response.headers.get('content-type', '')
        if 'webp' in content_type or 'webp' in url:
            ext = '.webp'
        elif 'png' in content_type or 'png' in url:
            ext = '.png'
        elif 'gif' in content_type or 'gif' in url:
            ext = '.gif'
        else:
            ext = '.jpg'

        filename = f"img_{index:02d}{ext}"
        filepath = save_dir / filename

        with open(filepath, 'wb') as f:
            f.write(response.content)

        return filename
    except Exception as e:
        return None


def save_content(content: str, url: str, platform_name: str = "", output_dir: str = None, title: str = None, verbose: bool = True) -> dict:
    """
    保存内容到本地
    """
    output_dir = Path(output_dir or DEFAULT_OUTPUT_DIR)
    output_dir.mkdir(parents=True, exist_ok=True)

    if not title:
        title = extract_title_from_content(content)

    date_str = datetime.now().strftime("%Y-%m-%d")
    folder_name = f"{date_str}_{sanitize_filename(title)}"

    content_dir = output_dir / folder_name
    content_dir.mkdir(parents=True, exist_ok=True)

    images = extract_images_from_content(content)
    image_mapping = {}

    if images and verbose:
        print(f"📷 发现 {len(images)} 张图片，正在下载...")

    for i, img_url in enumerate(images, 1):
        local_name = download_image(img_url, content_dir, i)
        if local_name:
            image_mapping[img_url] = local_name
            if verbose:
                print(f"  ✓ {local_name}")

    updated_content = content
    for orig_url, local_name in image_mapping.items():
        updated_content = updated_content.replace(orig_url, local_name)

    meta = f"""---
title: {title}
platform: {platform_name}
url: {url}
saved_at: {datetime.now().strftime("%Y-%m-%d %H:%M:%S")}
images: {len(image_mapping)}
---

"""

    md_path = content_dir / "content.md"
    with open(md_path, 'w', encoding='utf-8') as f:
        f.write(meta + updated_content)

    if verbose:
        print(f"\n💾 已保存到: {content_dir}")
        print(f"   - content.md")
        print(f"   - 图片: {len(image_mapping)} 张")

    return {
        'success': True,
        'dir': str(content_dir),
        'md_file': str(md_path),
        'images': len(image_mapping),
        'title': title
    }


def read_and_save(url: str, output_dir: str = None, verbose: bool = True) -> dict:
    """
    读取URL内容并保存到本地
    """
    result = read_url(url, verbose=verbose)

    if not result.get('success'):
        return result

    platform = result.get('platform', {})
    content = format_output(result, url)

    save_result = save_content(
        content=content,
        url=url,
        platform_name=platform.get('name', '未知'),
        output_dir=output_dir,
        verbose=verbose
    )

    result['save'] = save_result
    return result


def main():
    if len(sys.argv) < 2:
        print("=" * 60)
        print("URL Reader - 智能网页内容读取器")
        print("=" * 60)
        print("\n用法:")
        print("  python url_reader.py <url>              # 读取并显示")
        print("  python url_reader.py <url> --save       # 读取并保存")
        print("\n示例:")
        print("  python url_reader.py https://mp.weixin.qq.com/s/xxxxx --save")
        print("\n保存目录:")
        print(f"  {DEFAULT_OUTPUT_DIR}")
        print("\n策略优先级:")
        print("  1. Firecrawl (需要 API Key)")
        print("  2. Jina Reader (免费)")
        print("  3. Playwright (需要登录态)")
        print("\n环境变量:")
        print(f"  FIRECRAWL_API_KEY: {'已设置' if FIRECRAWL_API_KEY else '未设置'}")
        print(f"  微信登录态: {'已设置' if WECHAT_AUTH_FILE.exists() else '未设置'}")
        return

    url = sys.argv[1]
    save_mode = '--save' in sys.argv

    print(f"\n{'=' * 60}")
    print(f"正在读取: {url}")
    print(f"{'=' * 60}\n")

    if save_mode:
        result = read_and_save(url)
        if result.get('success') and result.get('save'):
            print(f"\n{'=' * 60}")
            print("✅ 读取并保存成功")
            print(f"{'=' * 60}")
    else:
        result = read_url(url)
        output = format_output(result, url)
        print(f"\n{'=' * 60}")
        print("读取结果")
        print(f"{'=' * 60}\n")
        print(output)


if __name__ == "__main__":
    main()
