#!/usr/bin/env python3
"""
AdsPower 指纹浏览器管理脚本

通过 AdsPower Local API 启动/关闭指纹浏览器实例。
启动时可指定 CDP 调试端口，用于后续 Agent browser 工具连接。

Usage:
    # 启动浏览器
    python scripts/adspower_browser.py open --user-id k194pjlr --cdp-port 30001

    # 关闭浏览器
    python scripts/adspower_browser.py close --user-id k194pjlr
"""

import argparse
import json
import os
import sys

import httpx

ADSPOWER_BASE_URL = os.getenv("ADSPOWER_BASE_URL", "http://127.0.0.1:50325")
ADSPOWER_API_KEY = os.getenv("ADSPOWER_API_KEY", "")


def open_browser(user_id: str, cdp_port: int) -> dict:
    """启动 AdsPower 指纹浏览器。

    Args:
        user_id: AdsPower 配置文件 ID
        cdp_port: 期望的 CDP 远程调试端口

    Returns:
        {"debug_port": int, "ws": str} 成功时返回调试信息
        {"error": str} 失败时返回错误信息
    """
    launch_args = json.dumps([f"--remote-debugging-port={cdp_port}"])
    params = {
        "user_id": user_id,
        "open_tabs": "1",  # 1=不打开历史tab，0=打开（默认）
        "ip_tab": "0",
        "headless": "0",
        "launch_args": launch_args,
    }
    headers = {}
    if ADSPOWER_API_KEY:
        headers["Authorization"] = f"Bearer {ADSPOWER_API_KEY}"

    url = f"{ADSPOWER_BASE_URL.rstrip('/')}/api/v1/browser/start"
    try:
        resp = httpx.get(url, params=params, headers=headers, timeout=30)
        data = resp.json()
    except Exception as e:
        return {"error": f"请求失败: {e}"}

    if data.get("code") != 0:
        return {"error": data.get("msg", "未知错误")}

    browser_data = data.get("data", {})
    return {
        "debug_port": browser_data.get("debug_port"),
        "ws": browser_data.get("ws", {}).get("puppeteer", ""),
    }


def close_browser(user_id: str) -> dict:
    """关闭 AdsPower 指纹浏览器。

    Args:
        user_id: AdsPower 配置文件 ID

    Returns:
        {"success": True} 或 {"error": str}
    """
    params = {"user_id": user_id}
    headers = {}
    if ADSPOWER_API_KEY:
        headers["Authorization"] = f"Bearer {ADSPOWER_API_KEY}"

    url = f"{ADSPOWER_BASE_URL.rstrip('/')}/api/v1/browser/stop"
    try:
        resp = httpx.get(url, params=params, headers=headers, timeout=15)
        data = resp.json()
    except Exception as e:
        return {"error": f"请求失败: {e}"}

    if data.get("code") != 0:
        return {"error": data.get("msg", "未知错误")}

    return {"success": True}


def main():
    parser = argparse.ArgumentParser(description="AdsPower 指纹浏览器管理")
    subparsers = parser.add_subparsers(dest="command", required=True)

    # open 子命令
    open_parser = subparsers.add_parser("open", help="启动浏览器")
    open_parser.add_argument("--user-id", required=True, help="AdsPower 配置文件 ID")
    open_parser.add_argument(
        "--cdp-port", type=int, required=True, help="CDP 远程调试端口"
    )
    # close 子命令
    close_parser = subparsers.add_parser("close", help="关闭浏览器")
    close_parser.add_argument("--user-id", required=True, help="AdsPower 配置文件 ID")

    args = parser.parse_args()

    if args.command == "open":
        result = open_browser(user_id=args.user_id, cdp_port=args.cdp_port)
    elif args.command == "close":
        result = close_browser(user_id=args.user_id)

    print(json.dumps(result, ensure_ascii=False, indent=2))

    if "error" in result:
        sys.exit(1)


if __name__ == "__main__":
    main()
