#!/usr/bin/env python3
"""
小红书笔记信息获取 - 轻量级客户端

仅获取笔记信息，不下载文件。
如需完整功能（下载+OCR+保存），请使用 xhs_scraper.py

使用方法:
    # 确保 API 服务已启动
    ./xhs-api-service.sh start
    
    # 获取笔记信息
    python xhs_api_client.py "笔记URL"
    
    # 输出 JSON 格式
    python xhs_api_client.py "笔记URL" --json
"""

import argparse
import json
import sys
import requests
from pathlib import Path


API_BASE = "http://127.0.0.1:5556"


def check_api_running() -> bool:
    """检查 API 服务是否运行"""
    try:
        resp = requests.get(f"{API_BASE}/docs", timeout=3)
        return resp.status_code == 200
    except:
        return False


def fetch_note(url: str) -> dict:
    """获取笔记信息"""
    payload = {"url": url, "download": False}
    resp = requests.post(f"{API_BASE}/xhs/detail", json=payload, timeout=60)
    resp.raise_for_status()
    return resp.json()


def main():
    parser = argparse.ArgumentParser(
        description='小红书笔记信息获取（轻量级客户端）'
    )
    parser.add_argument('url', help='笔记 URL')
    parser.add_argument('--json', action='store_true', help='输出 JSON 格式')
    
    args = parser.parse_args()
    
    # 检查 API 服务
    if not check_api_running():
        print("❌ API 服务未运行", file=sys.stderr)
        print("请先运行: ./xhs-api-service.sh start", file=sys.stderr)
        sys.exit(1)
    
    # 获取笔记信息
    try:
        result = fetch_note(args.url)
    except Exception as e:
        print(f"❌ 获取失败: {e}", file=sys.stderr)
        sys.exit(1)
    
    # 解析响应
    data = result.get("data")
    if not data:
        print("❌ 未获取到数据", file=sys.stderr)
        sys.exit(1)
    
    if args.json:
        print(json.dumps(data, ensure_ascii=False, indent=2))
    else:
        print(f"📝 标题: {data.get('作品标题', '')}")
        print(f"👤 作者: {data.get('作者昵称', '')}")
        desc = data.get('作品描述', '')
        if len(desc) > 100:
            print(f"📄 描述: {desc[:100]}...")
        else:
            print(f"📄 描述: {desc}")
        print(f"❤️  点赞: {data.get('点赞数量', '')} | 收藏: {data.get('收藏数量', '')} | 评论: {data.get('评论数量', '')}")
        print(f"🏷️  标签: {data.get('作品标签', '')}")
        print(f"📅 发布: {data.get('发布时间', '')}")
        print(f"🔗 链接: {data.get('作品链接', '')}")
        print(f"🔢 ID: {data.get('作品ID', '')}")
        
        urls = data.get('下载地址', [])
        print(f"🖼️  文件: {len(urls)} 个")


if __name__ == '__main__':
    main()
