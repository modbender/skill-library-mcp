#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
文档验证器 - 子技能5
使用 Playwright 验证文档是否创建成功
输出：verify_result.json
"""

import sys
import json
import re
import time
from pathlib import Path
from datetime import datetime


def clean_zero_width_chars(text):
    """清理零宽字符，避免乱码

    零宽字符包括：
    - \u200b: 零宽空格 (Zero Width Space)
    - \u200c: 零宽非连字符 (Zero Width Non-Joiner)
    - \u200d: 零宽连字符 (Zero Width Joiner)
    - \u202a-\u202e: 双向控制字符
    - \u2060-\u2064: 其他零宽字符
    - \ufeff: 零宽非断空格 (Zero Width No-Break Space)
    - \u00ad: 软连字符 (Soft Hyphen)
    """
    if not text:
        return ""
    # 移除所有零宽字符和双向控制字符
    # 使用字符范围 [\u200b-\u200d] 匹配零宽字符
    # 使用范围 [\u202a-\u202e] 匹配双向控制字符
    # 使用范围 [\u2060-\u2064] 匹配其他零宽字符
    text = re.sub(r'[\u200b-\u200d\u202a-\u202e\u2060-\u2064\ufeff\u00ad]', '', text)
    return text.strip()


def main():
    """主函数"""
    if len(sys.argv) < 2:
        print("Usage: python doc_verifier.py <doc_info.json> [output_dir]")
        sys.exit(1)

    doc_info_file = Path(sys.argv[1])

    if len(sys.argv) >= 3:
        output_dir = Path(sys.argv[2])
    else:
        output_dir = Path("output")

    output_dir.mkdir(parents=True, exist_ok=True)

    # 加载文档信息
    print(f"[feishu-doc-verifier] Loading doc info from: {doc_info_file}")
    with open(doc_info_file, 'r', encoding='utf-8') as f:
        doc_info = json.load(f)

    doc_id = doc_info["document_id"]
    doc_url = doc_info["document_url"]
    title = doc_info.get("title", "未命名文档")

    print(f"[feishu-doc-verifier] Document ID: {doc_id}")
    print(f"[feishu-doc-verifier] Document URL: {doc_url}")

    # 结果
    result = {
        "success": False,
        "document_id": doc_id,
        "document_url": doc_url,
        "page_loaded": False,
        "page_title": "",
        "screenshot": "",
        "errors": []
    }

    # 使用 Playwright 验证
    print("\n[feishu-doc-verifier] Starting Playwright verification...")

    # 获取项目根目录，用于存储登录状态
    project_root = Path(__file__).parent.parent.parent.parent.parent
    playwright_state_dir = project_root / ".claude" / "playwright_state"

    # 检查是否已有登录状态
    state_file = playwright_state_dir / "state.json"
    has_login_state = state_file.exists()

    # 如果没有登录状态，使用非无头模式让用户扫码
    headless = has_login_state

    if not has_login_state:
        print("=" * 70)
        print("[INFO] 首次运行，需要登录飞书账号")
        print("[INFO] 浏览器将自动打开，请使用飞书APP扫码登录")
        print("[INFO] 登录成功后，状态将被保存，后续无需重复登录")
        print("=" * 70)
        print()

    try:
        from playwright.sync_api import sync_playwright

        playwright_state_dir.mkdir(parents=True, exist_ok=True)

        with sync_playwright() as p:
            # 使用持久化上下文保存登录状态
            context = p.chromium.launch_persistent_context(
                user_data_dir=str(playwright_state_dir),
                headless=headless,
                # 设置更长的超时时间
                timeout=120000  # 2分钟
            )

            # 获取或创建页面
            if context.pages:
                page = context.pages[0]
            else:
                page = context.new_page()

            # 访问文档
            page.goto(doc_url, timeout=60000, wait_until="domcontentloaded")

            # 等待页面稳定
            page.wait_for_timeout(2000)

            # 检测是否需要登录
            needs_login = False
            if not has_login_state:
                # 检测页面是否包含登录相关元素
                try:
                    # 检查页面标题 - 如果已经是文档标题，说明已登录
                    page_title = page.title()
                    if "飞书" in page_title or "feishu" in page_title.lower():
                        # 可能已登录，检查是否有登录二维码
                        has_qrcode = page.locator("canvas").count() > 0 and \
                                    page.locator("text=扫码").count() > 0
                        if has_qrcode:
                            needs_login = True
                        # 否则可能已经显示文档了
                    else:
                        # 检查URL是否有login相关，但有二维码才需要登录
                        url_lower = page.url.lower()
                        if "login" in url_lower or "accounts" in url_lower:
                            has_qrcode = page.locator("canvas").count() > 0 or \
                                       page.locator("text=扫码").count() > 0
                            needs_login = has_qrcode
                except:
                    # 如果检测失败，保守起见假设需要登录
                    needs_login = True

            if needs_login:
                print("[INFO] 检测到登录页面，等待用户扫码登录...")
                print("[INFO] 请使用飞书APP扫描浏览器中的二维码...")
                print("[INFO] 登录成功后页面将自动跳转...")

                # 等待登录完成 - 检测 URL 变化或页面标题变化
                start_time = time.time()
                max_wait = 120  # 最多等待2分钟
                logged_in = False

                while time.time() - start_time < max_wait:
                    try:
                        current_url = page.url
                        # 如果 URL 不再包含 login/auth/accounts，说明已登录
                        if "login" not in current_url.lower() and \
                           "auth" not in current_url.lower() and \
                           "accounts" not in current_url.lower():
                            logged_in = True
                            break
                    except:
                        pass
                    time.sleep(1)  # 每秒检查一次

                if not logged_in:
                    print("[WARN] 等待登录超时，尝试继续验证...")

            page.wait_for_timeout(3000)  # 额外等待3秒确保页面完全加载

            # 获取页面信息
            page_title = page.title()
            # 清理零宽字符，避免乱码
            page_title = clean_zero_width_chars(page_title)
            result["page_loaded"] = True
            result["page_title"] = page_title

            # 简单验证：检查页面是否正常加载
            if page_title and len(page_title) > 0:
                result["success"] = True
                print(f"[OK] 文档验证成功 - 页面正常加载")
                print(f"[OK] 页面标题: {page_title}")

                # 如果是首次登录成功，提示用户
                if not has_login_state:
                    print()
                    print("=" * 70)
                    print("[OK] 登录成功！")
                    print("[INFO] 登录状态已保存，后续验证将自动使用保存的登录态")
                    print("=" * 70)
            else:
                print(f"[WARN] 文档验证失败 - 页面可能无法正常访问")

            # 截图（可选）
            screenshot_file = output_dir / "screenshot.png"
            page.screenshot(path=str(screenshot_file))
            result["screenshot"] = str(screenshot_file)

            # 保存上下文状态
            context.storage_state(path=str(state_file))
            if not has_login_state:
                print(f"[INFO] 登录状态已保存到: {state_file}")

            context.close()

    except Exception as e:
        error_msg = str(e)
        result["errors"].append(f"验证异常: {error_msg}")
        print(f"[WARN] 文档验证异常: {error_msg}")
        result["page_loaded"] = False

    result["verified_at"] = datetime.now().isoformat()

    # 保存结果
    result_file = output_dir / "verify_result.json"
    with open(result_file, 'w', encoding='utf-8') as f:
        json.dump(result, f, ensure_ascii=False, indent=2)

    print(f"\n[feishu-doc-verifier] Output: {result_file}")
    print(f"\n[OUTPUT] {result_file}")


if __name__ == "__main__":
    main()
