#!/usr/bin/env python3
"""SSH Batch Manager - Web UI Server"""

import http.server
import socketserver
import os
import webbrowser
import threading

PORT = 8765
DIRECTORY = os.path.dirname(os.path.abspath(__file__))

class Handler(http.server.SimpleHTTPRequestHandler):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, directory=DIRECTORY, **kwargs)
    
    def log_message(self, format, *args):
        print(f"[{self.log_date_time_string()}] {format % args}")

def open_browser():
    """延迟打开浏览器"""
    import time
    time.sleep(1)
    webbrowser.open(f'http://localhost:{PORT}')

def main():
    print(f"🚀 SSH Batch Manager - Web UI Server")
    print(f"")
    print(f"📂 目录：{DIRECTORY}")
    print(f"🌐 地址：http://localhost:{PORT}")
    print(f"📄 页面：ssh-manager.html")
    print(f"")
    print(f"按 Ctrl+C 停止服务")
    print(f"")
    
    # 在后台线程中打开浏览器
    threading.Thread(target=open_browser, daemon=True).start()
    
    with socketserver.TCPServer(("", PORT), Handler) as httpd:
        try:
            httpd.serve_forever()
        except KeyboardInterrupt:
            print("\n👋 服务已停止")

if __name__ == "__main__":
    main()
