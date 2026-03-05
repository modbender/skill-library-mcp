#!/usr/bin/env python3
"""
微信公众号长链接转短链接工具
将带参数的长链接转换为短链接格式
"""

import asyncio
import sys
import re
from urllib.parse import urlparse, parse_qs


async def convert_long_to_short(long_url: str) -> str:
    """
    将微信公众号长链接转换为短链接

    长链接格式: https://mp.weixin.qq.com/s?__biz=xxx&mid=xxx&idx=xxx&sn=xxx...
    短链接格式: https://mp.weixin.qq.com/s/xxxxxx
    """
    from playwright.async_api import async_playwright

    print(f"正在转换: {long_url[:80]}...")

    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=True)
        context = await browser.new_context()
        page = await context.new_page()

        # 设置 User-Agent
        await page.set_extra_http_headers({
            'User-Agent': 'Mozilla/5.0 (iPhone; CPU iPhone OS 16_0 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Mobile/15E148 MicroMessenger/8.0.38'
        })

        try:
            # 访问长链接，获取重定向后的短链接
            response = await page.goto(long_url, wait_until="domcontentloaded", timeout=15000)

            # 获取最终URL
            final_url = page.url

            # 检查是否已经是短链接
            if '/s/' in final_url and '?' not in final_url.split('/s/')[1].split('#')[0]:
                await browser.close()
                return final_url

            # 尝试从页面中提取短链接
            # 方法1: 从 meta 标签获取
            short_url = await page.evaluate("""
                () => {
                    // 尝试从 og:url 获取
                    const ogUrl = document.querySelector('meta[property="og:url"]');
                    if (ogUrl) return ogUrl.content;

                    // 尝试从 canonical 获取
                    const canonical = document.querySelector('link[rel="canonical"]');
                    if (canonical) return canonical.href;

                    return null;
                }
            """)

            if short_url and '/s/' in short_url:
                await browser.close()
                return short_url

            # 方法2: 从页面源码中查找
            content = await page.content()

            # 查找 msg_link 或其他短链接模式
            patterns = [
                r'var\s+msg_link\s*=\s*["\']([^"\']+)["\']',
                r'href="(https://mp\.weixin\.qq\.com/s/[a-zA-Z0-9_-]+)"',
                r'"url":"(https://mp\.weixin\.qq\.com/s/[a-zA-Z0-9_-]+)"',
            ]

            for pattern in patterns:
                match = re.search(pattern, content)
                if match:
                    found_url = match.group(1).replace('\\/', '/')
                    if '/s/' in found_url and len(found_url.split('/s/')[1]) > 10:
                        await browser.close()
                        return found_url

            await browser.close()

            # 如果无法获取短链接，返回原始URL
            return final_url

        except Exception as e:
            await browser.close()
            print(f"转换失败: {e}")
            return long_url


def is_long_url(url: str) -> bool:
    """判断是否是长链接格式"""
    parsed = urlparse(url)
    if 'mp.weixin.qq.com' not in parsed.netloc:
        return False

    # 长链接特征: 包含 __biz, mid, sn 等参数
    query = parse_qs(parsed.query)
    return '__biz' in query or 'mid' in query


def extract_short_id(url: str) -> str:
    """从短链接中提取ID"""
    match = re.search(r'/s/([a-zA-Z0-9_-]+)', url)
    return match.group(1) if match else None


async def main():
    if len(sys.argv) < 2:
        print("=" * 60)
        print("微信公众号长链接转短链接工具")
        print("=" * 60)
        print("\n用法: python wechat_url_converter.py <长链接>")
        print("\n示例:")
        print('  python wechat_url_converter.py "https://mp.weixin.qq.com/s?__biz=xxx&mid=xxx&idx=1&sn=xxx"')
        print("\n说明:")
        print("  长链接格式: https://mp.weixin.qq.com/s?__biz=xxx&mid=xxx&idx=xxx&sn=xxx")
        print("  短链接格式: https://mp.weixin.qq.com/s/xxxxxx")
        return

    long_url = sys.argv[1]

    if not is_long_url(long_url):
        # 检查是否已经是短链接
        short_id = extract_short_id(long_url)
        if short_id:
            print(f"已经是短链接格式: https://mp.weixin.qq.com/s/{short_id}")
            return
        print("错误: 不是有效的微信公众号链接")
        return

    short_url = await convert_long_to_short(long_url)

    print("\n" + "=" * 60)
    print("转换结果")
    print("=" * 60)
    print(f"\n原始链接: {long_url[:80]}...")
    print(f"\n短链接: {short_url}")

    short_id = extract_short_id(short_url)
    if short_id:
        print(f"\n文章ID: {short_id}")


if __name__ == "__main__":
    asyncio.run(main())
