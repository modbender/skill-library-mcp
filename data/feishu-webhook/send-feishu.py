#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Feishu Webhook - Heredoc Edition

Usage:
    python3 send-feishu.py << 'EOF'
    内容
    EOF
"""

import base64
import hashlib
import hmac
import time
import json
import sys
import http.client
import os
from urllib.parse import urlparse

# 直接从环境变量读取（OpenClaw自动注入）
WEBHOOK = os.environ.get('FEISHU_WEBHOOK_URL', '')
SECRET = os.environ.get('FEISHU_WEBHOOK_SECRET', '')

def sign(timestamp):
    if not SECRET: return None
    s = f"{timestamp}\n{SECRET}"
    return base64.b64encode(hmac.new(s.encode(), digestmod=hashlib.sha256).digest()).decode()

def send(content):
    # 飞书卡片格式 - 支持所有样式
    payload = {
        "msg_type": "interactive",
        "card": {
            "schema": "2.0",
            "config": {"update_multi": True},
            "body": {
                "elements": [{
                    "tag": "markdown",
                    "content": content
                }]
            }
        }
    }
    ts = int(time.time())
    if SECRET: 
        payload["sign"] = sign(ts)
        payload["timestamp"] = ts
    
    u = urlparse(WEBHOOK)
    conn = http.client.HTTPSConnection(u.netloc)
    conn.request(
        "POST", u.path,
        json.dumps(payload, ensure_ascii=False).encode(),
        {"Content-Type": "application/json"}
    )
    resp = conn.getresponse()
    return json.loads(resp.read().decode())

if __name__ == '__main__':
    # 检查是否有stdin输入
    if sys.stdin.isatty():
        print("Usage: python3 send-feishu.py << 'EOF'\n# 标题\n内容\nEOF")
        sys.exit(1)
    
    # 读取所有内容
    content = sys.stdin.read().strip()
    
    if not content:
        print("❌ 内容为空")
        sys.exit(1)
    
    # 直接发送整个内容
    r = send(content)
    print('✅ 发送成功！' if r.get('code') == 0 else f"❌ {r.get('msg')}")
