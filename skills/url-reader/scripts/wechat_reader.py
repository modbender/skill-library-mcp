#!/usr/bin/env python3
"""
微信公众号文章读取器
使用 Playwright 浏览器自动化，支持登录态保持
"""

import asyncio
import json
import sys
import os
from pathlib import Path
from datetime import datetime

# 数据目录
DATA_DIR = Path(__file__).parent.parent / "data"
AUTH_FILE = DATA_DIR / "wechat_auth.json"

async def setup_auth(wait_seconds: int = 120):
    """首次登录，保存认证状态"""
    from playwright.async_api import async_playwright

    print("正在启动浏览器，请扫码登录微信...")

    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=False)
        context = await browser.new_context()
        page = await context.new_page()

        # 打开微信文章页面（任意一个）
        await page.goto("https://mp.weixin.qq.com/")

        print("\n请在浏览器中完成以下操作：")
        print("1. 点击右上角「登录」")
        print("2. 使用微信扫码登录")
        print(f"3. 登录成功后会自动保存（等待 {wait_seconds} 秒）")
        print("\n等待登录中...")

        # 等待登录成功（检测页面变化）
        try:
            # 等待登录成功后的元素出现
            await page.wait_for_selector(".weui-desktop-account__nickname", timeout=wait_seconds * 1000)
            print("✓ 检测到登录成功！")
        except:
            # 超时后也保存，可能用户已经登录
            print("等待超时，尝试保存当前状态...")

        # 保存认证状态
        storage = await context.storage_state()
        DATA_DIR.mkdir(parents=True, exist_ok=True)

        with open(AUTH_FILE, 'w', encoding='utf-8') as f:
            json.dump(storage, f, ensure_ascii=False, indent=2)

        await browser.close()

    print(f"✓ 认证状态已保存到: {AUTH_FILE}")
    return True


async def read_article(url: str, headless: bool = True):
    """读取微信公众号文章"""
    from playwright.async_api import async_playwright

    if not AUTH_FILE.exists():
        print("错误：未找到认证状态，请先运行 setup 命令")
        print("运行: python wechat_reader.py setup")
        return None

    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=headless)

        # 加载已保存的认证状态
        context = await browser.new_context(storage_state=str(AUTH_FILE))
        page = await context.new_page()

        try:
            print(f"正在读取: {url}")
            await page.goto(url, wait_until="networkidle", timeout=30000)

            # 检查是否需要验证
            if await page.query_selector("text=环境异常"):
                print("检测到验证页面，尝试自动处理...")
                # 点击验证按钮
                verify_btn = await page.query_selector("text=去验证")
                if verify_btn:
                    await verify_btn.click()
                    await page.wait_for_load_state("networkidle", timeout=30000)

            # 等待文章内容加载
            await page.wait_for_selector("#js_content", timeout=10000)

            # 提取文章信息
            result = await page.evaluate("""
                () => {
                    const title = document.querySelector('#activity-name')?.innerText?.trim() || '';
                    const author = document.querySelector('#js_name')?.innerText?.trim() || '';
                    const content = document.querySelector('#js_content')?.innerText?.trim() || '';
                    const publishTime = document.querySelector('#publish_time')?.innerText?.trim() || '';
                    const originalUrl = window.location.href;

                    // 提取图片
                    const images = [];
                    document.querySelectorAll('#js_content img').forEach(img => {
                        if (img.dataset.src) {
                            images.push(img.dataset.src);
                        }
                    });

                    return {
                        title,
                        author,
                        content,
                        publishTime,
                        originalUrl,
                        images
                    };
                }
            """)

            await browser.close()
            return result

        except Exception as e:
            print(f"读取失败: {e}")

            # 如果是验证问题，提示重新登录
            if "环境异常" in str(e) or "验证" in str(e):
                print("\n认证可能已过期，请重新登录：")
                print("运行: python wechat_reader.py setup")

            await browser.close()
            return None


async def check_auth():
    """检查认证状态"""
    if not AUTH_FILE.exists():
        print("✗ 未找到认证状态")
        print("运行: python wechat_reader.py setup")
        return False

    # 检查文件修改时间
    mtime = datetime.fromtimestamp(AUTH_FILE.stat().st_mtime)
    age = datetime.now() - mtime

    print(f"✓ 认证文件存在")
    print(f"  路径: {AUTH_FILE}")
    print(f"  创建时间: {mtime.strftime('%Y-%m-%d %H:%M:%S')}")
    print(f"  已过去: {age.days} 天 {age.seconds // 3600} 小时")

    if age.days > 7:
        print("\n⚠ 认证可能已过期，建议重新登录")

    return True


def format_article(article: dict) -> str:
    """格式化文章输出"""
    if not article:
        return "无法读取文章内容"

    output = []
    output.append(f"# {article.get('title', '无标题')}")
    output.append("")
    output.append(f"**来源**：微信公众号")
    output.append(f"**作者**：{article.get('author', '未知')}")
    output.append(f"**发布时间**：{article.get('publishTime', '未知')}")
    output.append(f"**原文链接**：{article.get('originalUrl', '')}")
    output.append("")
    output.append("---")
    output.append("")
    output.append(article.get('content', ''))

    if article.get('images'):
        output.append("")
        output.append("---")
        output.append("")
        output.append(f"**文章图片**：共 {len(article['images'])} 张")

    return "\n".join(output)


async def main():
    if len(sys.argv) < 2:
        print("用法:")
        print("  python wechat_reader.py setup          # 首次登录")
        print("  python wechat_reader.py status         # 检查认证状态")
        print("  python wechat_reader.py read <url>     # 读取文章")
        print("  python wechat_reader.py read <url> --show  # 显示浏览器")
        return

    command = sys.argv[1]

    if command == "setup":
        await setup_auth()

    elif command == "status":
        await check_auth()

    elif command == "read":
        if len(sys.argv) < 3:
            print("请提供文章URL")
            return

        url = sys.argv[2]
        headless = "--show" not in sys.argv

        article = await read_article(url, headless=headless)
        if article:
            print("\n" + "=" * 50)
            print(format_article(article))

    else:
        print(f"未知命令: {command}")


if __name__ == "__main__":
    asyncio.run(main())
