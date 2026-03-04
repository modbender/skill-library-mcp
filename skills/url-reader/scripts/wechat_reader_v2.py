#!/usr/bin/env python3
"""
微信公众号文章读取器 - 增强版
支持自动处理验证页面
"""

import asyncio
import json
import sys
import os
from pathlib import Path
from datetime import datetime

DATA_DIR = Path(__file__).parent.parent / "data"
AUTH_FILE = DATA_DIR / "wechat_auth.json"


async def read_wechat_article(url: str, headless: bool = True, wait_for_manual: bool = False) -> dict:
    """
    读取微信公众号文章

    Args:
        url: 文章链接
        headless: 是否无头模式
        wait_for_manual: 是否等待手动验证
    """
    from playwright.async_api import async_playwright

    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=headless)

        # 加载已保存的认证状态
        if AUTH_FILE.exists():
            context = await browser.new_context(storage_state=str(AUTH_FILE))
        else:
            context = await browser.new_context()

        page = await context.new_page()

        # 设置微信客户端 User-Agent
        await page.set_extra_http_headers({
            'User-Agent': 'Mozilla/5.0 (iPhone; CPU iPhone OS 16_0 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Mobile/15E148 MicroMessenger/8.0.38(0x18002629) NetType/WIFI Language/zh_CN'
        })

        try:
            print(f"正在访问: {url[:60]}...")
            await page.goto(url, wait_until="networkidle", timeout=30000)
            await page.wait_for_timeout(2000)

            # 检查是否需要验证
            content = await page.content()

            if '环境异常' in content or '完成验证' in content:
                print("检测到需要验证...")

                if wait_for_manual and not headless:
                    print("\n" + "=" * 50)
                    print("请在浏览器中完成验证")
                    print("验证完成后按 Enter 继续...")
                    print("=" * 50)

                    # 等待用户手动验证（最多等待 120 秒）
                    for i in range(120):
                        await page.wait_for_timeout(1000)
                        content = await page.content()
                        if '环境异常' not in content and 'js_content' in content:
                            print("验证成功！")
                            break

                    # 保存新的认证状态
                    storage = await context.storage_state()
                    DATA_DIR.mkdir(parents=True, exist_ok=True)
                    with open(AUTH_FILE, 'w', encoding='utf-8') as f:
                        json.dump(storage, f, ensure_ascii=False, indent=2)
                    print(f"认证状态已保存")
                else:
                    await browser.close()
                    return {
                        'success': False,
                        'error': '需要验证',
                        'suggestion': '请运行: python wechat_reader_v2.py --verify <url>'
                    }

            # 等待文章内容加载
            try:
                await page.wait_for_selector('#js_content', timeout=10000)
            except:
                pass

            # 提取文章内容
            result = await page.evaluate("""
                () => {
                    const title = document.querySelector('#activity-name')?.innerText?.trim() || '';
                    const author = document.querySelector('#js_name')?.innerText?.trim() || '';
                    const content = document.querySelector('#js_content')?.innerText?.trim() || '';
                    const publishTime = document.querySelector('#publish_time')?.innerText?.trim() || '';
                    const originalUrl = window.location.href;

                    return {
                        title,
                        author,
                        content,
                        publishTime,
                        originalUrl
                    };
                }
            """)

            await browser.close()

            if result.get('content') and len(result['content']) > 50:
                return {
                    'success': True,
                    **result
                }
            else:
                return {
                    'success': False,
                    'error': '无法提取文章内容',
                    'suggestion': '文章可能已被删除或需要特殊权限'
                }

        except Exception as e:
            await browser.close()
            return {
                'success': False,
                'error': str(e)
            }


def format_output(result: dict) -> str:
    """格式化输出"""
    if not result.get('success'):
        output = ["# 读取失败\n"]
        output.append(f"**错误**: {result.get('error', '未知错误')}")
        if result.get('suggestion'):
            output.append(f"**建议**: {result['suggestion']}")
        return "\n".join(output)

    output = []
    output.append(f"# {result.get('title', '无标题')}\n")
    output.append(f"**作者**: {result.get('author', '未知')}")
    output.append(f"**发布时间**: {result.get('publishTime', '未知')}")
    output.append(f"**原文链接**: {result.get('originalUrl', '')}")
    output.append("\n---\n")
    output.append(result.get('content', ''))

    return "\n".join(output)


async def main():
    if len(sys.argv) < 2:
        print("=" * 60)
        print("微信公众号文章读取器 - 增强版")
        print("=" * 60)
        print("\n用法:")
        print("  python wechat_reader_v2.py <url>              # 普通读取")
        print("  python wechat_reader_v2.py --verify <url>     # 需要验证时使用")
        print("  python wechat_reader_v2.py --show <url>       # 显示浏览器")
        print("\n示例:")
        print("  python wechat_reader_v2.py https://mp.weixin.qq.com/s/xxxxx")
        print("  python wechat_reader_v2.py --verify 'https://mp.weixin.qq.com/s?__biz=xxx&mid=xxx&sn=xxx'")
        return

    # 解析参数
    verify_mode = '--verify' in sys.argv
    show_mode = '--show' in sys.argv

    # 获取 URL（最后一个非选项参数）
    url = None
    for arg in sys.argv[1:]:
        if not arg.startswith('--'):
            url = arg

    if not url:
        print("错误: 请提供 URL")
        return

    headless = not (verify_mode or show_mode)
    wait_for_manual = verify_mode

    print(f"\n正在读取文章...")
    if verify_mode:
        print("验证模式: 浏览器将打开，请手动完成验证")

    result = await read_wechat_article(url, headless=headless, wait_for_manual=wait_for_manual)

    print("\n" + "=" * 60)
    print(format_output(result))


if __name__ == "__main__":
    asyncio.run(main())
