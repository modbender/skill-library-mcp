#!/usr/bin/env python3
"""
飞书图片操作脚本
支持：上传图片、发送图片消息、获取图片、查看图片

Usage:
    feishu_image.py upload --file <path>
    feishu_image.py send --chat-id <id> --file <path> | --image-key <key>
    feishu_image.py get --image-key <key> --output <path>
    feishu_image.py view --image-key <key>
"""

import argparse
import base64
import json
import os
import ssl
import sys
import mimetypes
from pathlib import Path
from typing import Optional

import urllib.request
import urllib.parse
import urllib.error

# OpenClaw 配置路径
OPENCLAW_CONFIG = Path.home() / ".openclaw" / "openclaw.json"

# 飞书 API 基础 URL
FEISHU_API_BASE = "https://open.feishu.cn/open-apis"

# 创建不验证 SSL 的上下文（解决 macOS 证书验证问题）
SSL_CONTEXT = ssl.create_default_context()
SSL_CONTEXT.check_hostname = False
SSL_CONTEXT.verify_mode = ssl.CERT_NONE


def load_feishu_config(account: str = "main") -> dict:
    """从 OpenClaw 配置加载飞书凭证"""
    try:
        with open(OPENCLAW_CONFIG, "r") as f:
            config = json.load(f)
        
        feishu_channels = config.get("channels", {}).get("feishu", {})
        accounts = feishu_channels.get("accounts", {})
        
        if account not in accounts:
            raise ValueError(f"飞书账户 '{account}' 未配置")
        
        acc = accounts[account]
        return {
            "app_id": acc.get("appId"),
            "app_secret": acc.get("appSecret"),
            "botname": acc.get("botname", "Bot"),
        }
    except FileNotFoundError:
        raise ValueError(f"OpenClaw 配置文件不存在: {OPENCLAW_CONFIG}")
    except json.JSONDecodeError as e:
        raise ValueError(f"配置文件解析失败: {e}")


def get_tenant_access_token(app_id: str, app_secret: str) -> str:
    """获取 tenant_access_token"""
    url = f"{FEISHU_API_BASE}/auth/v3/tenant_access_token/internal"
    
    data = json.dumps({
        "app_id": app_id,
        "app_secret": app_secret
    }).encode("utf-8")
    
    headers = {
        "Content-Type": "application/json"
    }
    
    req = urllib.request.Request(url, data=data, headers=headers, method="POST")
    
    try:
        with urllib.request.urlopen(req, timeout=30, context=SSL_CONTEXT) as resp:
            result = json.loads(resp.read().decode("utf-8"))
            
        if result.get("code") != 0:
            raise ValueError(f"获取 token 失败: {result.get('msg', '未知错误')}")
        
        return result.get("tenant_access_token")
    except urllib.error.URLError as e:
        raise ValueError(f"网络请求失败: {e}")


def upload_image(token: str, file_path: str) -> str:
    """上传图片到飞书，返回 image_key"""
    file_path = Path(file_path).expanduser().resolve()
    
    if not file_path.exists():
        raise ValueError(f"文件不存在: {file_path}")
    
    # 获取文件信息
    filename = file_path.name
    file_size = file_path.stat().st_size
    mime_type, _ = mimetypes.guess_type(str(file_path))
    if not mime_type or not mime_type.startswith("image/"):
        mime_type = "application/octet-stream"
    
    # 构建 multipart/form-data
    boundary = "----WebKitFormBoundary" + "".join(map(str, range(16)))
    
    # 读取文件内容
    with open(file_path, "rb") as f:
        file_content = f.read()
    
    # 构建 multipart body
    body_parts = []
    body_parts.append(f'--{boundary}\r\n'.encode())
    body_parts.append(f'Content-Disposition: form-data; name="image_type"\r\n\r\n'.encode())
    body_parts.append(b'message\r\n')
    body_parts.append(f'--{boundary}\r\n'.encode())
    body_parts.append(f'Content-Disposition: form-data; name="image"; filename="{filename}"\r\n'.encode())
    body_parts.append(f'Content-Type: {mime_type}\r\n\r\n'.encode())
    body_parts.append(file_content)
    body_parts.append(f'\r\n--{boundary}--\r\n'.encode())
    
    body = b"".join(body_parts)
    
    # 发送请求
    url = f"{FEISHU_API_BASE}/im/v1/images"
    headers = {
        "Authorization": f"Bearer {token}",
        "Content-Type": f"multipart/form-data; boundary={boundary}",
    }
    
    req = urllib.request.Request(url, data=body, headers=headers, method="POST")
    
    try:
        with urllib.request.urlopen(req, timeout=60, context=SSL_CONTEXT) as resp:
            result = json.loads(resp.read().decode("utf-8"))
        
        if result.get("code") != 0:
            raise ValueError(f"上传失败: {result.get('msg', '未知错误')} (code: {result.get('code')})")
        
        image_key = result.get("data", {}).get("image_key")
        if not image_key:
            raise ValueError("上传成功但未返回 image_key")
        
        return image_key
    except urllib.error.URLError as e:
        raise ValueError(f"网络请求失败: {e}")


def send_image_message(token: str, chat_id: str, image_key: str, chat_type: str = "group") -> dict:
    """发送图片消息"""
    url = f"{FEISHU_API_BASE}/im/v1/messages"
    
    # 设置 receive_id_type
    receive_id_type = "chat_id" if chat_type == "group" else "open_id"
    
    params = {"receive_id_type": receive_id_type}
    url_with_params = f"{url}?{urllib.parse.urlencode(params)}"
    
    data = json.dumps({
        "receive_id": chat_id,
        "msg_type": "image",
        "content": json.dumps({"image_key": image_key})
    }).encode("utf-8")
    
    headers = {
        "Authorization": f"Bearer {token}",
        "Content-Type": "application/json",
    }
    
    req = urllib.request.Request(url_with_params, data=data, headers=headers, method="POST")
    
    try:
        with urllib.request.urlopen(req, timeout=30, context=SSL_CONTEXT) as resp:
            result = json.loads(resp.read().decode("utf-8"))
        
        if result.get("code") != 0:
            raise ValueError(f"发送失败: {result.get('msg', '未知错误')} (code: {result.get('code')})")
        
        return result
    except urllib.error.URLError as e:
        raise ValueError(f"网络请求失败: {e}")


def get_image(token: str, image_key: str, output_path: str) -> str:
    """下载飞书图片"""
    url = f"{FEISHU_API_BASE}/im/v1/images/{image_key}"
    
    headers = {
        "Authorization": f"Bearer {token}",
    }
    
    req = urllib.request.Request(url, headers=headers, method="GET")
    
    try:
        with urllib.request.urlopen(req, timeout=60, context=SSL_CONTEXT) as resp:
            content_type = resp.headers.get("Content-Type", "")
            
            # 检查是否是错误响应（JSON）
            if "application/json" in content_type:
                result = json.loads(resp.read().decode("utf-8"))
                if result.get("code") != 0:
                    raise ValueError(f"获取图片失败: {result.get('msg', '未知错误')}")
                raise ValueError("服务器返回了意外的 JSON 响应")
            
            # 读取图片二进制数据
            image_data = resp.read()
            
            # 保存到文件
            output_path = Path(output_path).expanduser().resolve()
            output_path.parent.mkdir(parents=True, exist_ok=True)
            
            with open(output_path, "wb") as f:
                f.write(image_data)
            
            return str(output_path)
    except urllib.error.URLError as e:
        raise ValueError(f"网络请求失败: {e}")


def view_image(token: str, image_key: str) -> str:
    """获取图片的 base64 编码（供 AI 查看）"""
    url = f"{FEISHU_API_BASE}/im/v1/images/{image_key}"
    
    headers = {
        "Authorization": f"Bearer {token}",
    }
    
    req = urllib.request.Request(url, headers=headers, method="GET")
    
    try:
        with urllib.request.urlopen(req, timeout=60, context=SSL_CONTEXT) as resp:
            content_type = resp.headers.get("Content-Type", "")
            
            if "application/json" in content_type:
                result = json.loads(resp.read().decode("utf-8"))
                if result.get("code") != 0:
                    raise ValueError(f"获取图片失败: {result.get('msg', '未知错误')}")
                raise ValueError("服务器返回了意外的 JSON 响应")
            
            image_data = resp.read()
            
            # 转换为 base64
            b64_data = base64.b64encode(image_data).decode("utf-8")
            
            # 推断 MIME 类型
            mime_type = content_type or "image/jpeg"
            
            return f"data:{mime_type};base64,{b64_data}"
    except urllib.error.URLError as e:
        raise ValueError(f"网络请求失败: {e}")


def cmd_upload(args):
    """上传图片命令"""
    config = load_feishu_config(args.account)
    token = get_tenant_access_token(config["app_id"], config["app_secret"])
    
    print(f"上传图片: {args.file}")
    image_key = upload_image(token, args.file)
    
    result = {
        "success": True,
        "image_key": image_key,
        "file": str(Path(args.file).expanduser().resolve())
    }
    print(json.dumps(result, ensure_ascii=False, indent=2))
    return result


def cmd_send(args):
    """发送图片命令"""
    config = load_feishu_config(args.account)
    token = get_tenant_access_token(config["app_id"], config["app_secret"])
    
    # 如果提供了文件，先上传
    if args.file:
        print(f"上传图片: {args.file}")
        image_key = upload_image(token, args.file)
        print(f"image_key: {image_key}")
    elif args.image_key:
        image_key = args.image_key
    else:
        raise ValueError("必须提供 --file 或 --image-key")
    
    # 发送消息
    print(f"发送图片到 {args.chat_type}: {args.chat_id}")
    result = send_image_message(token, args.chat_id, image_key, args.chat_type)
    
    response = {
        "success": True,
        "message_id": result.get("data", {}).get("message_id"),
        "image_key": image_key
    }
    print(json.dumps(response, ensure_ascii=False, indent=2))
    return response


def cmd_get(args):
    """下载图片命令"""
    config = load_feishu_config(args.account)
    token = get_tenant_access_token(config["app_id"], config["app_secret"])
    
    print(f"下载图片: {args.image_key}")
    saved_path = get_image(token, args.image_key, args.output)
    
    result = {
        "success": True,
        "image_key": args.image_key,
        "saved_to": saved_path
    }
    print(json.dumps(result, ensure_ascii=False, indent=2))
    return result


def cmd_view(args):
    """查看图片命令"""
    config = load_feishu_config(args.account)
    token = get_tenant_access_token(config["app_id"], config["app_secret"])
    
    print(f"获取图片内容: {args.image_key}", file=sys.stderr)
    b64_data = view_image(token, args.image_key)
    
    # 输出 base64 数据（可供 image 工具使用）
    print(b64_data)
    return {"success": True, "data": b64_data}


def main():
    parser = argparse.ArgumentParser(
        description="飞书图片操作工具",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
示例:
  # 上传图片
  %(prog)s upload --file /path/to/image.jpg
  
  # 发送本地图片到群聊
  %(prog)s send --chat-id oc_xxxxx --file /path/to/image.jpg
  
  # 发送本地图片给用户
  %(prog)s send --chat-id ou_xxxxx --chat-type user --file /path/to/image.jpg
  
  # 用 image_key 发送图片
  %(prog)s send --chat-id oc_xxxxx --image-key img_xxxxx
  
  # 下载图片
  %(prog)s get --image-key img_xxxxx --output /path/to/save.jpg
  
  # 查看图片（返回 base64）
  %(prog)s view --image-key img_xxxxx
        """
    )
    
    subparsers = parser.add_subparsers(dest="command", help="命令")
    
    # upload 命令
    upload_parser = subparsers.add_parser("upload", help="上传图片")
    upload_parser.add_argument("--file", required=True, help="图片文件路径")
    upload_parser.add_argument("--account", default="main", help="飞书账户名")
    
    # send 命令
    send_parser = subparsers.add_parser("send", help="发送图片消息")
    send_parser.add_argument("--chat-id", required=True, help="接收者 ID（群聊 oc_ 或用户 ou_）")
    send_parser.add_argument("--file", help="本地图片文件路径")
    send_parser.add_argument("--image-key", help="已上传的 image_key")
    send_parser.add_argument("--chat-type", default="group", choices=["group", "user"], help="会话类型")
    send_parser.add_argument("--account", default="main", help="飞书账户名")
    
    # get 命令
    get_parser = subparsers.add_parser("get", help="下载图片")
    get_parser.add_argument("--image-key", required=True, help="图片的 image_key")
    get_parser.add_argument("--output", required=True, help="保存路径")
    get_parser.add_argument("--account", default="main", help="飞书账户名")
    
    # view 命令
    view_parser = subparsers.add_parser("view", help="查看图片（返回 base64）")
    view_parser.add_argument("--image-key", required=True, help="图片的 image_key")
    view_parser.add_argument("--account", default="main", help="飞书账户名")
    
    args = parser.parse_args()
    
    if not args.command:
        parser.print_help()
        sys.exit(1)
    
    try:
        if args.command == "upload":
            cmd_upload(args)
        elif args.command == "send":
            cmd_send(args)
        elif args.command == "get":
            cmd_get(args)
        elif args.command == "view":
            cmd_view(args)
    except ValueError as e:
        print(json.dumps({"success": False, "error": str(e)}, ensure_ascii=False), file=sys.stderr)
        sys.exit(1)
    except Exception as e:
        print(json.dumps({"success": False, "error": f"未知错误: {e}"}, ensure_ascii=False), file=sys.stderr)
        sys.exit(1)


if __name__ == "__main__":
    main()
