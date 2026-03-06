import imaplib
import email
import json
import os
from datetime import datetime
from typing import Dict, List, Optional

# --- 配置信息 (优先从环境变量读取) ---
IMAP_HOST = os.getenv("EMAIL_IMAP_HOST", "imap.corp.netease.com")
IMAP_PORT = int(os.getenv("EMAIL_IMAP_PORT", "993"))
IMAP_USER = os.getenv("EMAIL_SMTP_USER", "")
IMAP_PASS = os.getenv("EMAIL_SMTP_PASS", "")

# 获取脚本目录，构建资源文件路径
SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
ASSETS_DIR = os.path.join(os.path.dirname(SCRIPT_DIR), "assets")
REPLY_LOG = os.path.join(ASSETS_DIR, "reply_stats.json")
STATUS_FILE = os.path.join(ASSETS_DIR, "email_status.json")

def analyze_bounce_reason(body: str) -> str:
    """分析退信原因"""
    if not body:
        return "未知原因"

    body_lower = body.lower()

    if "user not found" in body_lower or "invalid user" in body_lower or "不存在" in body:
        return "账号不存在 (Invalid User)"
    elif "spam" in body_lower or "rejected" in body_lower or "垃圾邮件" in body:
        return "触发垃圾邮件风控 (Spam/Rejected)"
    elif "full" in body_lower or "quota" in body_lower or "满" in body:
        return "对方邮箱已满 (Mailbox Full)"
    return "其他原因 (详见摘要)"

def get_sent_count() -> int:
    """从日志文件获取已发送邮件数量"""
    if not os.path.exists(STATUS_FILE):
        return 0

    try:
        with open(STATUS_FILE, "r", encoding="utf-8") as f:
            data = json.load(f)
            return data.get("success", 0)
    except (json.JSONDecodeError, IOError) as e:
        print(f"读取发送统计失败: {e}")
        return 0


def decode_email_header(header: str) -> str:
    """解码邮件标题"""
    if not header:
        return ""

    try:
        parts = email.header.decode_header(header)
        decoded = ""
        for part, encoding in parts:
            if isinstance(part, bytes):
                decoded += part.decode(encoding or 'utf-8', errors='ignore')
            else:
                decoded += str(part)
        return decoded
    except Exception as e:
        print(f"解码邮件标题失败: {e}")
        return header


def extract_email_body(msg: email.message.Message) -> str:
    """提取邮件正文"""
    body = ""
    try:
        if msg.is_multipart():
            for part in msg.walk():
                if part.get_content_type() == "text/plain":
                    payload = part.get_payload(decode=True)
                    if payload:
                        body = payload.decode('utf-8', errors='ignore')
                        break
        else:
            payload = msg.get_payload(decode=True)
            if payload:
                body = payload.decode('utf-8', errors='ignore')
    except Exception as e:
        print(f"提取邮件正文失败: {e}")

    return body


def check_replies() -> Optional[Dict]:
    """检查邮件回复和退信"""
    if not IMAP_USER or not IMAP_PASS:
        print("错误: 未配置邮箱账号或密码")
        return None

    sent_total = get_sent_count()

    replied_list = []
    bounce_list = []

    # 严格过滤名单：系统号/订阅号不计入回信
    SYSTEM_KEYWORDS = ["noreply", "notification", "service", "support", "no-reply", "report"]
    today_imap = datetime.now().strftime("%d-%b-%Y")

    try:
        mail = imaplib.IMAP4_SSL(IMAP_HOST, IMAP_PORT)
        mail.login(IMAP_USER, IMAP_PASS)
        mail.select("INBOX")

        status, response = mail.search(None, f'(SINCE "{today_imap}")')

        if status == 'OK' and response[0]:
            ids = response[0].split()
            for r_id in ids:
                status, data = mail.fetch(r_id, '(RFC822)')
                if status != 'OK':
                    continue

                msg = email.message_from_bytes(data[0][1])
                from_addr = msg.get('From', '').lower()
                subject = msg.get('Subject', '')

                subject = decode_email_header(subject)
                body = extract_email_body(msg)

                # 1. 检查退信
                if "系统退信" in subject or "systems bounce" in subject.lower() or "mailer-daemon" in from_addr:
                    reason = analyze_bounce_reason(body)
                    bounce_list.append({
                        "from": from_addr,
                        "reason": reason,
                        "summary": body[:50]
                    })

                # 2. 检查真实回信 (排除自己和系统号)
                else:
                    is_system = any(kw in from_addr for kw in SYSTEM_KEYWORDS)
                    is_self = IMAP_USER.lower() in from_addr

                    if not is_system and not is_self:
                        replied_list.append({
                            "from": from_addr,
                            "subject": subject
                        })

        mail.close()
        mail.logout()

        stats = {
            "sent_total": sent_total,
            "replied_total": len(replied_list),
            "bounce_total": len(bounce_list),
            "replied_details": replied_list,
            "bounce_details": bounce_list,
            "check_time": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        }

        with open(REPLY_LOG, 'w', encoding='utf-8') as f:
            json.dump(stats, f, ensure_ascii=False, indent=4)

        return stats

    except imaplib.IMAP4.error as e:
        print(f"IMAP 连接错误: {e}")
        return None
    except Exception as e:
        print(f"检查回信失败: {e}")
        return None

if __name__ == "__main__":
    results = check_replies()
    if results:
        print("\n--- 邮件营销综合效果报告 ---")
        print(f"统计日期: {datetime.now().strftime('%Y-%m-%d')}")
        print(f"最近一次群发人数: {results['sent_total']}")
        print(f"真实回信人数: {results['replied_total']}")
        print(f"今日退信数量: {results['bounce_total']}")
        
        if results['replied_total'] > 0:
            print("\n[回信详情]:")
            for r in results['replied_details']:
                print(f"- 来自: {r['from']}")
                print(f"  标题: {r['subject']}")
        
        if results['bounce_total'] > 0:
            print("\n[退信分析]:")
            for b in results['bounce_details']:
                print(f"- 原因: {b['reason']}")
