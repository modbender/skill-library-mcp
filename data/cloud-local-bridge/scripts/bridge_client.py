#!/usr/bin/env python3
"""
Cloud-Local Bridge Client
从云端发送请求到本地 Bridge 服务
"""

import requests
import json
import argparse
import sys


class BridgeClient:
    def __init__(self, server_url, token):
        self.server_url = server_url.rstrip('/')
        self.token = token
        self.session = requests.Session()
        self.session.headers.update({
            'Authorization': f'Bearer {token}',
            'Content-Type': 'application/json'
        })
    
    def health_check(self):
        """健康检查"""
        try:
            response = self.session.get(f'{self.server_url}/health')
            return response.json()
        except requests.exceptions.RequestException as e:
            return {"status": "error", "message": str(e)}
    
    def get_status(self):
        """获取服务器状态"""
        try:
            response = self.session.get(f'{self.server_url}/status')
            return response.json()
        except requests.exceptions.RequestException as e:
            return {"status": "error", "message": str(e)}
    
    def execute(self, command, timeout=30, capture_output=True, reply_to=None):
        """
        执行远程命令
        
        Args:
            command: 要执行的命令
            timeout: 超时时间（秒）
            capture_output: 是否捕获输出
            reply_to: 回调 URL
        """
        data = {
            "command": command,
            "timeout": timeout,
            "capture_output": capture_output
        }
        if reply_to:
            data["reply_to"] = reply_to
        
        try:
            response = self.session.post(f'{self.server_url}/execute', json=data)
            return response.json()
        except requests.exceptions.RequestException as e:
            return {"success": False, "error": str(e)}
    
    def send_message(self, content):
        """发送消息"""
        try:
            response = self.session.post(
                f'{self.server_url}/message',
                json={"content": content}
            )
            return response.json()
        except requests.exceptions.RequestException as e:
            return {"status": "error", "message": str(e)}
    
    def upload_file(self, local_path, remote_path=None):
        """
        上传文件到远程服务器
        
        Args:
            local_path: 本地文件路径
            remote_path: 远程保存路径（默认同本地路径）
        """
        import os
        import base64
        
        if not os.path.exists(local_path):
            print(f"❌ 文件不存在: {local_path}")
            return None
        
        with open(local_path, 'rb') as f:
            content = base64.b64encode(f.read()).decode('utf-8')
        
        data = {
            "action": "upload",
            "path": remote_path or local_path,
            "base64_content": content
        }
        
        try:
            response = self.session.post(f'{self.server_url}/file', json=data)
            return response.json()
        except requests.exceptions.RequestException as e:
            return {"status": "error", "message": str(e)}
    
    def download_file(self, remote_path, local_path=None):
        """
        从远程服务器下载文件
        
        Args:
            remote_path: 远程文件路径
            local_path: 本地保存路径（默认同远程路径）
        """
        import os
        import base64
        
        data = {
            "action": "download",
            "path": remote_path
        }
        
        try:
            response = self.session.post(f'{self.server_url}/file', json=data)
            result = response.json()
            
            if result.get('status') == 'downloaded' and local_path:
                os.makedirs(os.path.dirname(local_path), exist_ok=True)
                content = base64.b64decode(result['base64_content'])
                with open(local_path, 'wb') as f:
                    f.write(content)
                return {"status": "downloaded", "local_path": local_path}
            
            return result
        except requests.exceptions.RequestException as e:
            return {"status": "error", "message": str(e)}
    
    def read_file(self, remote_path):
        """读取远程文件内容"""
        data = {
            "action": "read",
            "path": remote_path
        }
        
        try:
            response = self.session.post(f'{self.server_url}/file', json=data)
            return response.json()
        except requests.exceptions.RequestException as e:
            return {"status": "error", "message": str(e)}


def main():
    parser = argparse.ArgumentParser(description='Cloud-Local Bridge Client')
    parser.add_argument('--server', required=True, help='Bridge 服务器地址 (例如: http://192.168.1.100:8080)')
    parser.add_argument('--token', required=True, help='认证 token')
    
    subparsers = parser.add_subparsers(dest='command', help='可用命令')
    
    # 健康检查
    subparsers.add_parser('health', help='健康检查')
    
    # 状态查询
    subparsers.add_parser('status', help='获取服务器状态')
    
    # 执行命令
    exec_parser = subparsers.add_parser('execute', help='执行远程命令')
    exec_parser.add_argument('command', help='要执行的命令')
    exec_parser.add_argument('--timeout', type=int, default=30, help='超时时间（秒）')
    
    # 发送消息
    msg_parser = subparsers.add_parser('message', help='发送消息')
    msg_parser.add_argument('content', help='消息内容')
    
    # 上传文件
    upload_parser = subparsers.add_parser('upload', help='上传文件')
    upload_parser.add_argument('local_path', help='本地文件路径')
    upload_parser.add_argument('--remote', help='远程保存路径')
    
    # 下载文件
    download_parser = subparsers.add_parser('download', help='下载文件')
    download_parser.add_argument('remote_path', help='远程文件路径')
    download_parser.add_argument('--local', help='本地保存路径')
    
    # 读取文件
    read_parser = subparsers.add_parser('read', help='读取远程文件')
    read_parser.add_argument('remote_path', help='远程文件路径')
    
    args = parser.parse_args()
    
    if not args.command:
        parser.print_help()
        sys.exit(1)
    
    # 创建客户端
    client = BridgeClient(args.server, args.token)
    
    # 执行命令
    if args.command == 'health':
        result = client.health_check()
        print(json.dumps(result, indent=2, ensure_ascii=False))
    
    elif args.command == 'status':
        result = client.get_status()
        print(json.dumps(result, indent=2, ensure_ascii=False))
    
    elif args.command == 'execute':
        result = client.execute(args.command, timeout=args.timeout)
        print(json.dumps(result, indent=2, ensure_ascii=False))
    
    elif args.command == 'message':
        result = client.send_message(args.content)
        print(json.dumps(result, indent=2, ensure_ascii=False))
    
    elif args.command == 'upload':
        result = client.upload_file(args.local_path, args.remote)
        print(json.dumps(result, indent=2, ensure_ascii=False))
    
    elif args.command == 'download':
        result = client.download_file(args.remote_path, args.local)
        print(json.dumps(result, indent=2, ensure_ascii=False))
    
    elif args.command == 'read':
        result = client.read_file(args.remote_path)
        print(json.dumps(result, indent=2, ensure_ascii=False))


if __name__ == '__main__':
    main()
