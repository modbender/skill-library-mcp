#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Moltbook 发帖脚本
支持发布帖子到指定 submolt，处理 rate limiting，保存草稿
"""

import json
import argparse
import sys
import os

# 添加当前目录到路径
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from utils import MoltbookAPI, handle_rate_limit, save_draft, load_draft


def post(args):
    """
    发布帖子
    
    参数:
        submolt: 目标子社区
        title: 帖子标题
        content: 帖子内容
        draft: 是否保存草稿
    """
    api = MoltbookAPI()
    
    # 准备请求数据
    data = {
        "submolt": args.submolt,
        "title": args.title,
        "content": args.content
    }
    
    # 如果指定保存草稿
    if args.draft:
        draft_data = {
            "submolt": args.submolt,
            "title": args.title,
            "content": args.content,
            "saved_at": "2026-02-08T12:00:00Z"
        }
        save_draft(draft_data)
        return {
            "success": True,
            "message": "草稿已保存",
            "draft": draft_data
        }
    
    # 发布帖子（处理 rate limiting）
    result = handle_rate_limit(
        api.post,
        "/api/v1/posts",
        json=data
    )
    
    return result


def main():
    parser = argparse.ArgumentParser(
        description="Moltbook 发帖脚本",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
示例:
  # 发布普通帖子
  python post.py --submolt "general" --title "你好，Moltbook！" --content "内容"
  
  # 保存草稿
  python post.py --submolt "tech" --title "标题" --content "内容" --draft
        """
    )
    
    parser.add_argument(
        "--submolt",
        required=True,
        help="目标子社区名称"
    )
    parser.add_argument(
        "--title",
        required=True,
        help="帖子标题"
    )
    parser.add_argument(
        "--content",
        required=True,
        help="帖子内容"
    )
    parser.add_argument(
        "--draft",
        action="store_true",
        help="保存草稿到 configs/moltbook-post.json"
    )
    
    args = parser.parse_args()
    
    try:
        result = post(args)
        print(json.dumps(result, ensure_ascii=False, indent=2))
    except Exception as e:
        error_result = {
            "success": False,
            "error": str(e),
            "error_code": "POST_ERROR"
        }
        print(json.dumps(error_result, ensure_ascii=False, indent=2))
        sys.exit(1)


if __name__ == "__main__":
    main()
