#!/usr/bin/env python3
"""
知乎 AI Bot API 工具
支持发布想法、点赞、评论等功能
"""

import sys
import os
import json
import time
import hmac
import hashlib
import base64
import argparse
from datetime import datetime
from typing import Optional, List, Dict, Any

import requests


class ZhihuBot:
    """知乎 API 客户端"""

    BASE_URL = "https://openapi.zhihu.com"

    def __init__(self):
        self.app_key = os.environ.get("ZHIHU_APP_KEY", "")
        self.app_secret = os.environ.get("ZHIHU_APP_SECRET", "")

        if not self.app_key or not self.app_secret:
            print("错误: 请设置环境变量 ZHIHU_APP_KEY 和 ZHIHU_APP_SECRET")
            print("示例:")
            print('  export ZHIHU_APP_KEY="your_app_key"')
            print('  export ZHIHU_APP_SECRET="your_app_secret"')
            sys.exit(1)

    def _generate_signature(self, timestamp: str, log_id: str, extra_info: str = "") -> str:
        """生成签名"""
        sign_string = f"app_key:{self.app_key}|ts:{timestamp}|logid:{log_id}|extra_info:{extra_info}"
        hmac_obj = hmac.new(
            self.app_secret.encode('utf-8'),
            sign_string.encode('utf-8'),
            hashlib.sha256
        )
        signature = base64.b64encode(hmac_obj.digest()).decode('utf-8')
        return signature

    def _make_request(self, method: str, endpoint: str, params: Dict = None, data: Dict = None) -> Dict:
        """发送 API 请求"""
        timestamp = str(int(time.time()))
        log_id = f"zhihu_{timestamp}_{int(time.time() * 1000000) % 1000000}"
        signature = self._generate_signature(timestamp, log_id)

        headers = {
            "X-App-Key": self.app_key,
            "X-Timestamp": timestamp,
            "X-Log-Id": log_id,
            "X-Sign": signature,
        }

        if data:
            headers["Content-Type"] = "application/json"

        url = f"{self.BASE_URL}{endpoint}"

        try:
            if method == "GET":
                response = requests.get(url, headers=headers, params=params, timeout=30)
            elif method == "POST":
                response = requests.post(url, headers=headers, params=params, json=data, timeout=30)
            else:
                raise ValueError(f"不支持的 HTTP 方法: {method}")

            response.raise_for_status()
            result = response.json()

            # 检查业务状态码
            if result.get("status") != 0 and result.get("code") != 0:
                print(f"API 错误: {result.get('msg', '未知错误')}")
                return result

            return result

        except requests.exceptions.RequestException as e:
            print(f"请求失败: {e}")
            return {"status": 1, "msg": str(e)}
        except json.JSONDecodeError as e:
            print(f"JSON 解析失败: {e}")
            return {"status": 1, "msg": str(e)}


def ring_detail(args):
    """获取圈子详情"""
    bot = ZhihuBot()

    ring_id = args.ring_id
    page_num = args.page_num or 1
    page_size = args.page_size or 20

    print(f"=== 获取圈子详情 ===")
    print(f"圈子 ID: {ring_id}")
    print(f"页码: {page_num}")
    print(f"每页数量: {page_size}")
    print()

    params = {
        "ring_id": ring_id,
        "page_num": page_num,
        "page_size": page_size
    }

    result = bot._make_request("GET", "/openapi/ring/detail", params=params)

    if result.get("status") == 0 or result.get("code") == 0:
        data = result.get("data", {})
        ring_info = data.get("ring_info", {})

        print(f"✓ 圈子名称: {ring_info.get('ring_name', 'N/A')}")
        print(f"✓ 圈子描述: {ring_info.get('ring_desc', 'N/A')}")
        print(f"✓ 成员数: {ring_info.get('membership_num', 0)}")
        print(f"✓ 讨论数: {ring_info.get('discussion_num', 0)}")
        print()

        contents = data.get("contents", [])
        print(f"✓ 获取到 {len(contents)} 条内容:")
        for i, content in enumerate(contents, 1):
            print(f"\n  [{i}] {content.get('author_name', 'N/A')}")
            print(f"      {content.get('content', '')[:100]}...")
            print(f"      点赞: {content.get('like_num', 0)} | 评论: {content.get('comment_num', 0)}")

    return result


def pin_publish(args):
    """发布想法"""
    bot = ZhihuBot()

    print(f"=== 发布想法 ===")
    print(f"圈子 ID: {args.ring_id}")
    print(f"标题: {args.title}")
    print(f"内容: {args.content}")
    if args.images:
        print(f"图片: {len(args.images.split(','))} 张")
    print()

    data = {
        "ring_id": args.ring_id,
        "title": args.title,
        "content": args.content
    }

    if args.images:
        image_urls = [url.strip() for url in args.images.split(',') if url.strip()]
        data["image_urls"] = image_urls

    result = bot._make_request("POST", "/openapi/publish/pin", data=data)

    if result.get("status") == 0:
        data = result.get("data", {})
        content_token = data.get("content_token")
        print(f"✓ 发布成功！")
        print(f"  想法 ID: {content_token}")
        print(f"  链接: https://www.zhihu.com/pin/{content_token}")
    else:
        print(f"✗ 发布失败: {result.get('msg')}")

    return result


def reaction(args):
    """点赞/取消点赞"""
    bot = ZhihuBot()

    content_type = args.content_type  # pin 或 comment
    content_token = args.content_token
    action_value = 1 if args.action == "like" else 0

    action_desc = "点赞" if args.action == "like" else "取消点赞"

    print(f"=== {action_desc} ===")
    print(f"内容类型: {content_type}")
    print(f"内容 ID: {content_token}")
    print()

    data = {
        "content_token": content_token,
        "content_type": content_type,
        "action_type": "like",
        "action_value": action_value
    }

    result = bot._make_request("POST", "/openapi/reaction", data=data)

    if result.get("status") == 0:
        data = result.get("data", {})
        if data.get("success"):
            print(f"✓ {action_desc}成功！")
        else:
            print(f"✗ {action_desc}失败")
    else:
        print(f"✗ 操作失败: {result.get('msg')}")

    return result


def comment_create(args):
    """创建评论"""
    bot = ZhihuBot()

    content_type = args.content_type  # pin 或 comment
    content_token = args.content_token
    content = args.content

    print(f"=== 创建评论 ===")
    print(f"类型: {'对想法发评论' if content_type == 'pin' else '回复评论'}")
    print(f"目标 ID: {content_token}")
    print(f"内容: {content}")
    print()

    data = {
        "content_token": content_token,
        "content_type": content_type,
        "content": content
    }

    result = bot._make_request("POST", "/openapi/comment/create", data=data)

    if result.get("status") == 0 or result.get("code") == 0:
        data = result.get("data", {})
        comment_id = data.get("comment_id")
        print(f"✓ 评论创建成功！")
        print(f"  评论 ID: {comment_id}")
    else:
        print(f"✗ 评论创建失败: {result.get('msg')}")

    return result


def comment_delete(args):
    """删除评论"""
    bot = ZhihuBot()

    comment_id = args.comment_id

    print(f"=== 删除评论 ===")
    print(f"评论 ID: {comment_id}")
    print()

    data = {
        "comment_id": comment_id
    }

    result = bot._make_request("POST", "/openapi/comment/delete", data=data)

    if result.get("status") == 0:
        data = result.get("data", {})
        if data.get("success"):
            print(f"✓ 评论删除成功！")
        else:
            print(f"✗ 评论删除失败")
    else:
        print(f"✗ 删除失败: {result.get('msg')}")

    return result


def comment_list(args):
    """获取评论列表"""
    bot = ZhihuBot()

    content_type = args.content_type  # pin 或 comment
    content_token = args.content_token
    page_num = args.page_num or 1
    page_size = args.page_size or 10

    print(f"=== 获取评论列表 ===")
    print(f"类型: {'想法的一级评论' if content_type == 'pin' else '评论的二级评论'}")
    print(f"目标 ID: {content_token}")
    print(f"页码: {page_num}")
    print(f"每页数量: {page_size}")
    print()

    params = {
        "content_token": content_token,
        "content_type": content_type,
        "page_num": page_num,
        "page_size": page_size
    }

    result = bot._make_request("GET", "/openapi/comment/list", params=params)

    if result.get("status") == 0 or result.get("code") == 0:
        data = result.get("data", {})
        comments = data.get("comments", [])
        has_more = data.get("has_more", False)

        print(f"✓ 获取到 {len(comments)} 条评论")
        if has_more:
            print(f"  (还有更多评论)")

        for i, comment in enumerate(comments, 1):
            print(f"\n  [{i}] {comment.get('author_name', 'N/A')}")
            print(f"      {comment.get('content', '')}")
            print(f"      点赞: {comment.get('like_count', 0)} | 回复: {comment.get('reply_count', 0)}")

    return result


def main():
    """主函数"""
    parser = argparse.ArgumentParser(description="知乎 AI Bot API 工具")

    subparsers = parser.add_subparsers(dest="command", help="可用命令")

    # ring 命令
    ring_parser = subparsers.add_parser("ring", help="圈子相关操作")
    ring_subparsers = ring_parser.add_subparsers(dest="ring_command", help="圈子子命令")

    ring_detail_parser = ring_subparsers.add_parser("detail", help="获取圈子详情")
    ring_detail_parser.add_argument("ring_id", help="圈子 ID")
    ring_detail_parser.add_argument("--page-num", type=int, help="页码，默认 1")
    ring_detail_parser.add_argument("--page-size", type=int, help="每页数量，默认 20")
    ring_detail_parser.set_defaults(func=ring_detail)

    # pin 命令
    pin_parser = subparsers.add_parser("pin", help="想法相关操作")
    pin_subparsers = pin_parser.add_subparsers(dest="pin_command", help="想法子命令")

    pin_publish_parser = pin_subparsers.add_parser("publish", help="发布想法")
    pin_publish_parser.add_argument("--ring-id", required=True, help="圈子 ID")
    pin_publish_parser.add_argument("--title", required=True, help="标题")
    pin_publish_parser.add_argument("--content", required=True, help="内容")
    pin_publish_parser.add_argument("--images", help="图片 URL，用逗号分隔")
    pin_publish_parser.set_defaults(func=pin_publish)

    # reaction 命令
    reaction_parser = subparsers.add_parser("reaction", help="点赞/取消点赞")
    reaction_parser.add_argument("content_type", choices=["pin", "comment"], help="内容类型")
    reaction_parser.add_argument("content_token", help="内容 ID")
    reaction_parser.add_argument("action", choices=["like", "unlike"], help="操作类型")
    reaction_parser.set_defaults(func=reaction)

    # comment 命令
    comment_parser = subparsers.add_parser("comment", help="评论相关操作")
    comment_subparsers = comment_parser.add_subparsers(dest="comment_command", help="评论子命令")

    comment_create_parser = comment_subparsers.add_parser("create", help="创建评论")
    comment_create_parser.add_argument("content_type", choices=["pin", "comment"], help="内容类型")
    comment_create_parser.add_argument("content_token", help="内容 ID")
    comment_create_parser.add_argument("content", help="评论内容")
    comment_create_parser.set_defaults(func=comment_create)

    comment_delete_parser = comment_subparsers.add_parser("delete", help="删除评论")
    comment_delete_parser.add_argument("comment_id", help="评论 ID")
    comment_delete_parser.set_defaults(func=comment_delete)

    comment_list_parser = comment_subparsers.add_parser("list", help="获取评论列表")
    comment_list_parser.add_argument("content_type", choices=["pin", "comment"], help="内容类型")
    comment_list_parser.add_argument("content_token", help="内容 ID")
    comment_list_parser.add_argument("--page-num", type=int, help="页码，默认 1")
    comment_list_parser.add_argument("--page-size", type=int, help="每页数量，默认 10")
    comment_list_parser.set_defaults(func=comment_list)

    args = parser.parse_args()

    if not args.command:
        parser.print_help()
        sys.exit(1)

    # 执行对应的命令
    if args.command == "ring" and args.ring_command == "detail":
        ring_detail(args)
    elif args.command == "pin" and args.pin_command == "publish":
        pin_publish(args)
    elif args.command == "reaction":
        reaction(args)
    elif args.command == "comment":
        if args.comment_command == "create":
            comment_create(args)
        elif args.comment_command == "delete":
            comment_delete(args)
        elif args.comment_command == "list":
            comment_list(args)
    else:
        parser.print_help()


if __name__ == "__main__":
    main()
