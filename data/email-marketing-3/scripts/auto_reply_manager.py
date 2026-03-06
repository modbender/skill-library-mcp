"""自动回复管理器 - 邮件监控和回复功能"""

import imaplib
import email
from email.header import decode_header
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
import os
import ssl
import json
import time
from typing import List, Dict, Optional

# --- 配置信息 (从环境变量读取) ---
IMAP_HOST = os.getenv("EMAIL_IMAP_HOST", "imap.corp.netease.com")
IMAP_PORT = int(os.getenv("EMAIL_IMAP_PORT", "993"))
SMTP_HOST = os.getenv("EMAIL_SMTP_HOST", "smtp.corp.netease.com")
SMTP_PORT = int(os.getenv("EMAIL_SMTP_PORT", "465"))
EMAIL_USER = os.getenv("EMAIL_SMTP_USER", "")
EMAIL_PASS = os.getenv("EMAIL_SMTP_PASS", "")

FAQ_PATH = "/home/node/.openclaw/media/inbound/c3b043ac-df37-4fb0-9e21-89c4282030ef"

# 获取脚本目录，构建资源文件路径
SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
ASSETS_DIR = os.path.join(os.path.dirname(SCRIPT_DIR), "assets")
PENDING_REPLIES_FILE = os.path.join(ASSETS_DIR, "pending_replies.json")

def decode_email_content(content, encoding: Optional[str] = None) -> str:
    """解码邮件内容"""
    if isinstance(content, bytes):
        try:
            return content.decode(encoding or 'utf-8', errors='ignore')
        except Exception:
            return content.decode('utf-8', errors='replace')
    return str(content)


def get_unread_emails() -> List[Dict]:
    """连接 IMAP 获取未读邮件"""
    if not EMAIL_USER or not EMAIL_PASS:
        print("错误: 未配置邮箱账号或密码")
        return []

    try:
        mail = imaplib.IMAP4_SSL(IMAP_HOST, IMAP_PORT)
        mail.login(EMAIL_USER, EMAIL_PASS)

        mail.select("INBOX")
        # 搜索所有未读且未回复标志的邮件
        status, response = mail.search(None, '(UNSEEN)')

        if status != 'OK':
            print("搜索未读邮件失败")
            mail.logout()
            return []

        unread_msg_nums = response[0].split()

        emails = []
        for num in unread_msg_nums:
            status, msg_data = mail.fetch(num, '(RFC822)')
            if status != 'OK':
                continue

            raw_email = msg_data[0][1]
            msg = email.message_from_bytes(raw_email)

            # 解析发件人
            from_ = decode_header(msg.get("From", ""))[0][0]
            from_ = decode_email_content(from_)

            # 解析主题
            subject = decode_header(msg.get("Subject", ""))[0][0]
            subject = decode_email_content(subject)

            # 解析正文
            body = extract_email_body(msg)

            emails.append({
                "id": num.decode(),
                "from": from_,
                "subject": subject,
                "body": body.strip(),
                "msg_id": msg.get("Message-ID")
            })

        mail.close()
        mail.logout()
        return emails
    except imaplib.IMAP4.error as e:
        print(f"IMAP 连接错误: {e}")
        return []
    except Exception as e:
        print(f"IMAP 读取失败: {e}")
        return []


def extract_email_body(msg: email.message.Message) -> str:
    """提取邮件正文"""
    body = ""
    try:
        if msg.is_multipart():
            for part in msg.walk():
                content_type = part.get_content_type()
                if content_type == "text/plain" and not body:
                    payload = part.get_payload(decode=True)
                    if payload:
                        body = decode_email_content(payload)
                elif content_type == "text/html":
                    payload = part.get_payload(decode=True)
                    if payload:
                        html_body = decode_email_content(payload)
                        # 如果没有纯文本，或者纯文本太短，则使用 HTML（后续可以加清洗）
                        if not body or len(body) < 10:
                            body = "[HTML Content] " + html_body
        else:
            payload = msg.get_payload(decode=True)
            if payload:
                body = decode_email_content(payload)
    except Exception as e:
        print(f"提取邮件正文失败: {e}")

    return body

def save_pending_reply(email_data: Dict, draft_reply: str) -> bool:
    """保存待确认的回信"""
    try:
        data = []
        if os.path.exists(PENDING_REPLIES_FILE):
            with open(PENDING_REPLIES_FILE, 'r', encoding='utf-8') as f:
                data = json.load(f)

        data.append({
            "email_id": email_data["id"],
            "to": email_data["from"],
            "original_subject": email_data["subject"],
            "original_body": email_data["body"],
            "draft_reply": draft_reply,
            "status": "pending",
            "timestamp": time.time()
        })

        with open(PENDING_REPLIES_FILE, 'w', encoding='utf-8') as f:
            json.dump(data, f, ensure_ascii=False, indent=4)
        return True
    except Exception as e:
        print(f"保存待回信失败: {e}")
        return False

def send_reply(to_email: str, subject: str, body: str, original_msg_id: Optional[str] = None) -> bool:
    """发送回信"""
    if not EMAIL_USER or not EMAIL_PASS:
        print("错误: 未配置邮箱账号或密码")
        return False

    if not to_email or '@' not in to_email:
        print(f"错误: 无效的收件人邮箱 {to_email}")
        return False

    try:
        # 跳过证书验证
        context = ssl.create_default_context()
        context.check_hostname = False
        context.verify_mode = ssl.CERT_NONE

        msg = MIMEMultipart()
        msg['From'] = f"Youdao Ads <{EMAIL_USER}>"
        msg['To'] = to_email
        # 如果是回复，标题加上 Re:
        if not subject.lower().startswith("re:"):
            msg['Subject'] = "Re: " + subject
        else:
            msg['Subject'] = subject

        if original_msg_id:
            msg['In-Reply-To'] = original_msg_id
            msg['References'] = original_msg_id

        msg.attach(MIMEText(body, 'plain', 'utf-8'))

        with smtplib.SMTP_SSL(SMTP_HOST, SMTP_PORT, context=context) as server:
            server.login(EMAIL_USER, EMAIL_PASS)
            server.send_message(msg)
        return True
    except smtplib.SMTPException as e:
        print(f"SMTP 发送失败: {e}")
        return False
    except Exception as e:
        print(f"发送回信失败: {e}")
        return False

if __name__ == "__main__":
    import sys
    # 如果通过命令行参数调用发送
    if len(sys.argv) > 4 and sys.argv[1] == "send":
        to = sys.argv[2]
        subj = sys.argv[3]
        content = sys.argv[4]
        if send_reply(to, subj, content):
            print("SUCCESS")
        else:
            print("FAILED")
        sys.exit(0)
    
    # 默认扫描逻辑
    unread = get_unread_emails()
    if unread:
        print(f"发现 {len(unread)} 封新回信。")
        for e in unread:
            print(f"--- 邮件来自: {e['from']} ---")
            print(f"标题: {e['subject']}")
            print(f"内容摘要: {e['body'][:100]}...")
            # 后续逻辑将交由 Agent 使用 FAQ 进行拟稿并通知用户
    else:
        print("没有发现新回信。")
