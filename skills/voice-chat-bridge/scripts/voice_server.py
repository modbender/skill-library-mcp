#!/usr/bin/env python3
"""
Voice Chat Bridge - HTTP Server
为生成的语音文件提供本地HTTP服务
"""

import http.server
import socketserver
import os
import sys

# 配置
VOICE_DIR = os.path.expanduser("~/.openclaw/workspace/voice_output")
PORT = 8765

class QuietHTTPRequestHandler(http.server.SimpleHTTPRequestHandler):
    """静音版 HTTP Handler"""
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, directory=VOICE_DIR, **kwargs)
    
    def log_message(self, format, *args):
        # 不输出访问日志
        pass

def main():
    # 确保目录存在
    os.makedirs(VOICE_DIR, exist_ok=True)
    
    handler = QuietHTTPRequestHandler
    
    with socketserver.TCPServer(("", PORT), handler) as httpd:
        print(f"🌐 Voice Chat Bridge Server started")
        print(f"📂 Serving: {VOICE_DIR}")
        print(f"🔗 Local: http://localhost:{PORT}/")
        print(f"⏹️  Press Ctrl+C to stop\n")
        
        try:
            httpd.serve_forever()
        except KeyboardInterrupt:
            print("\n⏹️  Server stopped")

if __name__ == "__main__":
    main()
