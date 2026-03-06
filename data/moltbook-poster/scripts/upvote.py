#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Moltbook 点赞脚本
支持点赞、取消点赞、检查是否已点赞
"""

import json
import argparse
import sys
import os

# 添加当前目录到路径
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from utils import MoltbookAPI, handle_rate_limit


def check_upvote(args):
    """检查是否已点赞"""
    api = MoltbookAPI()
    result = api.get(f"/api/v1/posts/{args.post_id}/upvote")
    return result


def upvote(args):
    """
    点赞操作
    
    参数:
        post_id: 帖子ID
        action: 操作类型 (upvote/unvote/check)
    """
    api = MoltbookAPI()
    
    if args.action == "check":
        return check_upvote(args)
    
    elif args.action == "upvote":
        # 点赞（处理 rate limiting）
        result = handle_rate_limit(
            api.post,
            f"/api/v1/posts/{args.post_id}/upvote"
        )
        return {
            "success": result.get("success", True),
            "action": "upvoted",
            "has_upvoted": True
        }
    
    elif args.action == "unvote":
        # 取消点赞（处理 rate limiting）
        result = handle_rate_limit(
            api.delete,
            f"/api/v1/posts/{args.post_id}/upvote"
        )
        return {
            "success": result.get("success", True),
            "action": "unvoted",
            "has_upvoted": False
        }
    
    else:
        raise ValueError(f"不支持的操作: {args.action}")


def main():
    parser = argparse.ArgumentParser(
        description="Moltbook 点赞脚本",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
示例:
  # 点赞帖子
  python upvote.py --post_id "abc123" --action "upvote"
  
  # 取消点赞
  python upvote.py --post_id "abc123" --action "unvote"
  
  # 检查是否已点赞
  python upvote.py --post_id "abc123" --action "check"
        """
    )
    
    parser.add_argument(
        "--post_id",
        required=True,
        help="帖子ID"
    )
    parser.add_argument(
        "--action",
        required=True,
        choices=["upvote", "unvote", "check"],
        help="操作类型: upvote(点赞) / unvote(取消点赞) / check(检查)"
    )
    
    args = parser.parse_args()
    
    try:
        result = upvote(args)
        print(json.dumps(result, ensure_ascii=False, indent=2))
    except Exception as e:
        error_result = {
            "success": False,
            "error": str(e),
            "error_code": "UPVOTE_ERROR"
        }
        print(json.dumps(error_result, ensure_ascii=False, indent=2))
        sys.exit(1)


if __name__ == "__main__":
    main()
