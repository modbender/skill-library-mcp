#!/usr/bin/env python3
"""
Cloud-Local Bridge Server
在本地机器上运行，接收云端的命令并执行
"""

import http.server
import socketserver
import json
import os
import subprocess
import base64
import argparse
import logging
from urllib.parse import urlparse, parse_qs
import threading

# 配置日志
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

class BridgeHandler(http.server.BaseHTTPRequestHandler):
    
    def log_message(self, format, *args):
        """自定义日志格式"""
        logger.info(f"{self.client_address[0]}:{self.client_address[1]} - {format % args}")
    
    def verify_token(self):
        """验证 Authorization header"""
        auth_header = self.headers.get('Authorization', '')
        if not auth_header.startswith('Bearer '):
            return False
        token = auth_header[7:]  # 移除 "Bearer " 前缀
        return token == self.server.token
    
    def send_json_response(self, status_code, data):
        """发送 JSON 响应"""
        self.send_response(status_code)
        self.send_header('Content-Type', 'application/json')
        self.end_headers()
        self.wfile.write(json.dumps(data, ensure_ascii=False).encode('utf-8'))
    
    def do_POST(self):
        """处理 POST 请求"""
        if not self.verify_token():
            self.send_json_response(401, {"error": "Unauthorized: Invalid token"})
            return
        
        # 获取路径
        path = urlparse(self.path).path
        
        try:
            # 读取请求体
            content_length = int(self.headers.get('Content-Length', 0))
            body = self.rfile.read(content_length).decode('utf-8') if content_length > 0 else "{}"
            data = json.loads(body) if body else {}
            
            # 路由处理
            if path == '/execute':
                self.handle_execute(data)
            elif path == '/message':
                self.handle_message(data)
            elif path == '/file':
                self.handle_file(data)
            elif path == '/status':
                self.handle_status()
            else:
                self.send_json_response(404, {"error": "Not found"})
                
        except json.JSONDecodeError as e:
            self.send_json_response(400, {"error": f"Invalid JSON: {str(e)}"})
        except Exception as e:
            logger.exception("处理请求时出错")
            self.send_json_response(500, {"error": str(e)})
    
    def do_GET(self):
        """处理 GET 请求"""
        if not self.verify_token():
            self.send_json_response(401, {"error": "Unauthorized: Invalid token"})
            return
        
        path = urlparse(self.path).path
        
        if path == '/health':
            self.send_json_response(200, {"status": "healthy", "service": "cloud-local-bridge"})
        elif path == '/status':
            self.handle_status()
        else:
            self.send_json_response(404, {"error": "Not found"})
    
    def handle_execute(self, data):
        """执行命令"""
        command = data.get('command', '')
        timeout = data.get('timeout', 30)
        capture = data.get('capture_output', True)
        
        if not command:
            self.send_json_response(400, {"error": "Missing 'command' field"})
            return
        
        logger.info(f"执行命令: {command}")
        
        try:
            # 执行命令
            result = subprocess.run(
                command,
                shell=True,
                capture_output=capture,
                text=True,
                timeout=timeout
            )
            
            response = {
                "success": True,
                "returncode": result.returncode,
                "stdout": result.stdout if capture else None,
                "stderr": result.stderr if capture else None
            }
            
            # 如果有 reply_to，回调通知
            if data.get('reply_to'):
                self.send_callback(data['reply_to'], response)
            
            self.send_json_response(200, response)
            
        except subprocess.TimeoutExpired:
            self.send_json_response(408, {"error": "Command timeout"})
        except Exception as e:
            self.send_json_response(500, {"error": str(e)})
    
    def handle_message(self, data):
        """处理消息"""
        message = data.get('content', '')
        logger.info(f"收到消息: {message}")
        
        # 可以在这里添加自定义消息处理逻辑
        response = {
            "status": "received",
            "message": message,
            "timestamp": str(__import__('datetime').datetime.now())
        }
        
        self.send_json_response(200, response)
    
    def handle_file(self, data):
        """处理文件传输"""
        action = data.get('action', '')
        file_path = data.get('path', '')
        
        if not action or not file_path:
            self.send_json_response(400, {"error": "Missing 'action' or 'path' field"})
            return
        
        try:
            if action == 'upload':
                # 上传文件到本地
                content = data.get('base64_content', '')
                if not content:
                    self.send_json_response(400, {"error": "Missing 'base64_content' for upload"})
                    return
                
                # 解码并写入文件
                file_content = base64.b64decode(content)
                os.makedirs(os.path.dirname(file_path), exist_ok=True)
                
                with open(file_path, 'wb') as f:
                    f.write(file_content)
                
                response = {"status": "uploaded", "path": file_path}
                
            elif action == 'download':
                # 从本地下载文件
                if not os.path.exists(file_path):
                    self.send_json_response(404, {"error": "File not found"})
                    return
                
                with open(file_path, 'rb') as f:
                    content = base64.b64encode(f.read()).decode('utf-8')
                
                response = {"status": "downloaded", "path": file_path, "base64_content": content}
            
            elif action == 'read':
                # 读取文件内容
                if not os.path.exists(file_path):
                    self.send_json_response(404, {"error": "File not found"})
                    return
                
                with open(file_path, 'r', encoding='utf-8') as f:
                    content = f.read()
                
                response = {"status": "read", "path": file_path, "content": content}
            
            else:
                self.send_json_response(400, {"error": f"Unknown action: {action}"})
                return
            
            self.send_json_response(200, response)
            
        except Exception as e:
            self.send_json_response(500, {"error": str(e)})
    
    def handle_status(self):
        """返回服务状态"""
        response = {"status": "running"}
        
        # 可选依赖：系统信息
        try:
            import platform
            response["platform"] = platform.system()
            response["hostname"] = platform.node()
        except:
            pass
        
        # 可选依赖：资源使用率
        try:
            import psutil
            response["cpu_percent"] = psutil.cpu_percent()
            response["memory_percent"] = psutil.virtual_memory().percent
            response["disk_usage"] = psutil.disk_usage('/').percent
        except:
            pass
        
        self.send_json_response(200, response)
    
    def send_callback(self, url, data):
        """发送回调通知"""
        try:
            import requests
            requests.post(url, json=data, timeout=10)
        except Exception as e:
            logger.warning(f"回调失败: {e}")


class BridgeServer(socketserver.ThreadingMixIn, http.server.HTTPServer):
    """多线程 Bridge 服务器"""
    daemon_threads = True
    allow_reuse_address = True
    
    def __init__(self, *args, token=None, **kwargs):
        self.token = token
        super().__init__(*args, **kwargs)


def main():
    parser = argparse.ArgumentParser(description='Cloud-Local Bridge Server')
    parser.add_argument('--port', type=int, default=8080, help='监听端口')
    parser.add_argument('--host', type=str, default='0.0.0.0', help='绑定地址')
    parser.add_argument('--token', type=str, required=True, help='认证 token')
    parser.add_argument('--verbose', action='store_true', help='详细日志')
    
    args = parser.parse_args()
    
    if args.verbose:
        logging.getLogger().setLevel(logging.DEBUG)
    
    server = BridgeServer((args.host, args.port), BridgeHandler, token=args.token)
    
    logger.info(f"🚀 Cloud-Local Bridge Server 启动成功!")
    logger.info(f"   监听地址: http://{args.host}:{args.port}")
    logger.info(f"   Token: {args.token}")
    logger.info(f"   端点:")
    logger.info(f"   - POST /execute  - 执行命令")
    logger.info(f"   - POST /message  - 发送消息")
    logger.info(f"   - POST /file     - 文件传输")
    logger.info(f"   - GET  /health   - 健康检查")
    logger.info(f"   - GET  /status   - 服务状态")
    
    try:
        server.serve_forever()
    except KeyboardInterrupt:
        logger.info("\n🛑 服务器已停止")
        server.shutdown()


if __name__ == '__main__':
    main()
