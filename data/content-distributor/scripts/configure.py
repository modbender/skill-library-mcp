#!/usr/bin/env python3
"""
凭据配置工具
用法: python3 configure.py --platform zhihu
"""

import argparse
import json
import os
from pathlib import Path

SECRETS_FILE = Path.home() / "clawd" / "secrets" / "content-distributor.json"

PLATFORM_COOKIES = {
    "zhihu": {
        "required": ["z_c0", "_xsrf"],
        "optional": ["d_c0"],
        "description": "知乎 - 从浏览器 DevTools → Application → Cookies 获取"
    },
    "douban": {
        "required": ["dbcl2", "ck"],
        "optional": ["bid"],
        "description": "豆瓣 - 从浏览器 DevTools → Application → Cookies 获取"
    },
    "weibo": {
        "required": ["SUB"],
        "optional": ["SUBP"],
        "description": "微博 - 从浏览器 DevTools → Application → Cookies 获取"
    }
}


def load_secrets() -> dict:
    """加载现有凭据"""
    if SECRETS_FILE.exists():
        with open(SECRETS_FILE, 'r', encoding='utf-8') as f:
            return json.load(f)
    return {}


def save_secrets(data: dict) -> None:
    """保存凭据（确保目录存在）"""
    SECRETS_FILE.parent.mkdir(parents=True, exist_ok=True)
    with open(SECRETS_FILE, 'w', encoding='utf-8') as f:
        json.dump(data, f, indent=2, ensure_ascii=False)
    # 设置文件权限为仅当前用户可读写
    os.chmod(SECRETS_FILE, 0o600)
    print(f"✅ 凭据已保存到 {SECRETS_FILE}")


def configure_platform(platform: str) -> None:
    """配置指定平台的凭据"""
    if platform not in PLATFORM_COOKIES:
        print(f"❌ 不支持的平台: {platform}")
        print(f"支持的平台: {', '.join(PLATFORM_COOKIES.keys())}")
        return
    
    config = PLATFORM_COOKIES[platform]
    print(f"\n📝 配置 {platform} 凭据")
    print(f"   {config['description']}\n")
    
    secrets = load_secrets()
    if platform not in secrets:
        secrets[platform] = {"cookies": {}}
    
    # 收集必需的 Cookie
    for cookie_name in config["required"]:
        current = secrets[platform].get("cookies", {}).get(cookie_name, "")
        prompt = f"  {cookie_name}"
        if current:
            prompt += f" [当前: {current[:20]}...]"
        prompt += ": "
        
        value = input(prompt).strip()
        if value:
            secrets[platform]["cookies"][cookie_name] = value
        elif not current:
            print(f"  ⚠️ {cookie_name} 是必需的")
            return
    
    # 可选的 Cookie
    print(f"\n  可选 Cookie (回车跳过):")
    for cookie_name in config.get("optional", []):
        value = input(f"  {cookie_name}: ").strip()
        if value:
            secrets[platform]["cookies"][cookie_name] = value
    
    # User-Agent
    default_ua = "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
    current_ua = secrets[platform].get("user_agent", "")
    print(f"\n  User-Agent [回车使用默认值]: ")
    ua = input("  ").strip()
    secrets[platform]["user_agent"] = ua if ua else (current_ua or default_ua)
    
    save_secrets(secrets)
    print(f"\n✅ {platform} 配置完成!")


def list_platforms() -> None:
    """列出所有已配置的平台"""
    secrets = load_secrets()
    print("\n📋 已配置的平台:")
    
    for platform, config in PLATFORM_COOKIES.items():
        if platform in secrets and secrets[platform].get("cookies"):
            cookies = secrets[platform]["cookies"]
            required = config["required"]
            configured = [c for c in required if c in cookies]
            status = "✅" if len(configured) == len(required) else "⚠️"
            print(f"  {status} {platform}: {len(configured)}/{len(required)} 必需 Cookie")
        else:
            print(f"  ❌ {platform}: 未配置")


def main():
    parser = argparse.ArgumentParser(description="内容分发平台凭据配置工具")
    parser.add_argument("--platform", "-p", help="要配置的平台 (zhihu/douban/weibo)")
    parser.add_argument("--list", "-l", action="store_true", help="列出已配置的平台")
    
    args = parser.parse_args()
    
    if args.list:
        list_platforms()
    elif args.platform:
        configure_platform(args.platform)
    else:
        parser.print_help()
        print("\n示例:")
        print("  python3 configure.py --platform zhihu")
        print("  python3 configure.py --list")


if __name__ == "__main__":
    main()
