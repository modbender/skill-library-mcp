#!/usr/bin/env python3
"""
简单的 HTTP API Server for SaaS Affiliate
让其他 Agent 可以通过 HTTP 调用
"""

from http.server import HTTPServer, BaseHTTPRequestHandler
import json
from tools import search_saas_tools, get_affiliate_link, get_all_products, get_product_details
import cgi

class Handler(BaseHTTPRequestHandler):
    def do_GET(self):
        if self.path == '/health':
            self.send_response(200)
            self.send_header('Content-type', 'application/json')
            self.end_headers()
            self.wfile.write(json.dumps({'status': 'ok'}).encode())
        elif self.path == '/products':
            self.send_response(200)
            self.send_header('Content-type', 'application/json')
            self.end_headers()
            result = get_all_products()
            self.wfile.write(json.dumps(result, ensure_ascii=False).encode())
        else:
            self.send_response(404)
            self.end_headers()
    
    def do_POST(self):
        content_length = int(self.headers.get('Content-Length', 0))
        body = self.rfile.read(content_length)
        
        try:
            data = json.loads(body)
            method = data.get('method')
            params = data.get('params', {})
            
            if method == 'search':
                result = search_saas_tools(params.get('query', ''))
            elif method == 'link':
                result = get_affiliate_link(params.get('product_name', ''))
            elif method == 'detail':
                result = get_product_details(params.get('product_name', ''))
            else:
                result = {'error': f'Unknown method: {method}'}
            
            self.send_response(200)
            self.send_header('Content-type', 'application/json')
            self.end_headers()
            self.wfile.write(json.dumps(result, ensure_ascii=False).encode())
            
        except Exception as e:
            self.send_response(500)
            self.send_header('Content-type', 'application/json')
            self.end_headers()
            self.wfile.write(json.dumps({'error': str(e)}).encode())
    
    def log_message(self, format, *args):
        pass  # 静默日志

def run(port=8080):
    server = HTTPServer(('0.0.0.0', port), Handler)
    print(f"🚀 SaaS Affiliate API running on http://0.0.0.0:{port}")
    server.serve_forever()

if __name__ == '__main__':
    run()
