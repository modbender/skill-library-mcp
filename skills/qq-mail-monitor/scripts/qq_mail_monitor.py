#!/usr/bin/env python3
"""
QQ 邮箱监控 - 检查新邮件并记录
输出结果供外部处理（通知/播报）
"""

import imaplib
import email
from email.header import decode_header
import json
import os
import time

# 配置
# ⚠️ 使用前请修改为你的邮箱和授权码
EMAIL = "your_qq_number@qq.com"           # 替换为你的 QQ 邮箱
AUTH_CODE = "your_auth_code"              # 替换为你的授权码（16 位，不是登录密码）
IMAP_SERVER = "imap.qq.com"
IMAP_PORT = 993
STATE_FILE = "/Users/qin/.openclaw/workspace/.mail_state.json"

def decode_field(value):
    if not value:
        return ""
    parts = decode_header(value)
    result = ""
    for part, enc in parts:
        if isinstance(part, bytes):
            result += part.decode(enc or 'utf-8', errors='ignore')
        else:
            result += str(part)
    return result[:100]

def get_latest_email():
    """获取最新一封邮件的信息"""
    try:
        mail = imaplib.IMAP4_SSL(IMAP_SERVER, IMAP_PORT)
        mail.login(EMAIL, AUTH_CODE)
        mail.select("INBOX")
        
        status, messages = mail.search(None, "ALL")
        email_ids = messages[0].split()
        
        if not email_ids:
            mail.logout()
            return None
        
        # 获取最新一封
        latest_id = email_ids[-1]
        status, data = mail.fetch(latest_id, '(RFC822)')
        
        for response_part in data:
            if isinstance(response_part, tuple):
                raw_email = response_part[1]
                msg = email.message_from_bytes(raw_email)
                
                result = {
                    "subject": decode_field(msg.get('Subject', '')),
                    "from": decode_field(msg.get('From', '')),
                    "date": msg.get('Date', '')[:30],
                    "id": latest_id.decode() if isinstance(latest_id, bytes) else str(latest_id)
                }
                
                mail.close()
                mail.logout()
                return result
        
        mail.close()
        mail.logout()
        return None
        
    except Exception as e:
        print(f"❌ 错误：{e}")
        return None

def load_state():
    """加载上次的邮件 ID"""
    if os.path.exists(STATE_FILE):
        with open(STATE_FILE, 'r') as f:
            return json.load(f)
    return {"latest_id": None, "checked_at": None}

def save_state(state):
    """保存当前邮件 ID"""
    with open(STATE_FILE, 'w') as f:
        json.dump(state, f, ensure_ascii=False, indent=2)

def main():
    print("🔍 检查新邮件...")
    
    # 获取最新邮件
    latest = get_latest_email()
    
    if not latest:
        print("📭 收件箱为空")
        print(json.dumps({"has_new": False, "reason": "empty"}))
        return
    
    # 加载上次状态
    state = load_state()
    last_id = state.get("latest_id")
    current_id = latest["id"]
    
    # 判断是否有新邮件
    if last_id != current_id:
        print("📬 发现新邮件！")
        print(f"   主题：{latest['subject']}")
        print(f"   发件人：{latest['from']}")
        print(f"   时间：{latest['date']}")
        
        # 保存新状态
        save_state({
            "latest_id": current_id,
            "checked_at": time.time()
        })
        
        # 输出 JSON 供外部处理
        result = {
            "has_new": True,
            "email": latest,
            "message": f"新邮件：{latest['subject']}，来自 {latest['from']}"
        }
        print("\n" + json.dumps(result, ensure_ascii=False))
    else:
        print("✅ 没有新邮件")
        print(json.dumps({"has_new": False, "reason": "no_new"}))

if __name__ == "__main__":
    main()
