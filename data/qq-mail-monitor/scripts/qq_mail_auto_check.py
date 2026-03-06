#!/usr/bin/env python3
"""
QQ 邮箱自动监控 - 定时任务专用
发现新邮件时输出通知内容（供 cron 任务处理）
"""

import imaplib
import email
from email.header import decode_header
import json
import os
import time
from datetime import datetime

# 配置
# ⚠️ 使用前请修改为你的邮箱和授权码
# 获取授权码：登录 QQ 邮箱 → 设置 → 账户 → 开启 IMAP/SMTP 服务 → 生成授权码
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
        
        latest_id = email_ids[-1]
        status, data = mail.fetch(latest_id, '(RFC822)')
        
        for response_part in data:
            if isinstance(response_part, tuple):
                raw_email = response_part[1]
                msg = email.message_from_bytes(raw_email)
                
                # 解析日期
                date_str = msg.get('Date', '')
                try:
                    parsed_date = email.utils.parsedate_to_datetime(date_str)
                    date_display = parsed_date.strftime("%m-%d %H:%M")
                except:
                    date_display = date_str[:25]
                
                result = {
                    "subject": decode_field(msg.get('Subject', '')),
                    "from": decode_field(msg.get('From', '')),
                    "date": date_display,
                    "id": latest_id.decode() if isinstance(latest_id, bytes) else str(latest_id)
                }
                
                mail.close()
                mail.logout()
                return result
        
        mail.close()
        mail.logout()
        return None
        
    except Exception as e:
        return {"error": str(e)}

def load_state():
    if os.path.exists(STATE_FILE):
        with open(STATE_FILE, 'r') as f:
            return json.load(f)
    return {"latest_id": None, "checked_at": None}

def save_state(state):
    with open(STATE_FILE, 'w') as f:
        json.dump(state, f, ensure_ascii=False, indent=2)

def main():
    now = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    print(f"[{now}] 🔍 检查 QQ 邮箱新邮件...")
    
    # 获取最新邮件
    latest = get_latest_email()
    
    if not latest:
        print("[✓] 收件箱为空")
        return
    
    if "error" in latest:
        print(f"[✗] 检查失败：{latest['error']}")
        return
    
    # 加载上次状态
    state = load_state()
    last_id = state.get("latest_id")
    current_id = latest["id"]
    
    # 判断是否有新邮件
    if last_id != current_id:
        print(f"[!] 📬 发现新邮件！")
        print(f"    主题：{latest['subject']}")
        print(f"    发件人：{latest['from']}")
        print(f"    时间：{latest['date']}")
        
        # 保存新状态
        save_state({
            "latest_id": current_id,
            "checked_at": time.time()
        })
        
        # 输出播报文本
        subject_short = latest['subject'][:30] + "..." if len(latest['subject']) > 30 else latest['subject']
        tts_text = f"新邮件提醒。主题：{subject_short}，来自：{latest['from']}"
        
        print(f"\n🔊 TTS: {tts_text}")
        print(f"\n[RESULT] NEW_EMAIL|{latest['subject']}|{latest['from']}|{latest['date']}")
    else:
        print("[✓] 没有新邮件")
        print(f"[RESULT] NO_NEW")

if __name__ == "__main__":
    main()
