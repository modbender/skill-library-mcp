#!/usr/bin/env python3
"""
QQ 邮箱快速检查工具 - v3
"""

import imaplib
import email
from email.header import decode_header

# 配置
# ⚠️ 使用前请修改为你的邮箱和授权码
EMAIL = "your_qq_number@qq.com"           # 替换为你的 QQ 邮箱
AUTH_CODE = "your_auth_code"              # 替换为你的授权码（16 位，不是登录密码）
IMAP_SERVER = "imap.qq.com"
IMAP_PORT = 993

def main():
    print("=" * 60)
    print(f"QQ 邮箱检查：{EMAIL}")
    print("=" * 60)
    
    try:
        mail = imaplib.IMAP4_SSL(IMAP_SERVER, IMAP_PORT)
        mail.login(EMAIL, AUTH_CODE)
        print("\n✅ 登录成功")
        
        mail.select("INBOX")
        
        status, messages = mail.search(None, "ALL")
        email_ids = messages[0].split()
        total = len(email_ids)
        print(f"📊 收件箱共有 {total} 封邮件\n")
        
        if total == 0:
            mail.logout()
            return
        
        limit = min(10, total)
        print(f"最近 {limit} 封邮件:\n")
        
        for i, eid in enumerate(reversed(email_ids[-limit:])):
            eid_str = eid.decode() if isinstance(eid, bytes) else str(eid)
            
            # 获取完整邮件
            status, data = mail.fetch(eid, '(RFC822)')
            
            for response_part in data:
                if isinstance(response_part, tuple):
                    raw_email = response_part[1]
                    msg = email.message_from_bytes(raw_email)
                    
                    subject = decode_field(msg.get('Subject', ''))
                    from_addr = decode_field(msg.get('From', ''))
                    date = msg.get('Date', '')[:30]
                    
                    print(f"{i+1}. {date}")
                    print(f"   从：{from_addr}")
                    print(f"   主题：{subject}")
                    print()
        
        mail.close()
        mail.logout()
        
    except Exception as e:
        print(f"❌ 错误：{type(e).__name__}: {e}")


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


if __name__ == "__main__":
    main()
