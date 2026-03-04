#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
批量下载历史资金日报邮件
从邮箱中搜索所有资金日报邮件并下载XLSX附件，支持 Bitwarden 自动凭据加载
"""

import imaplib
import email
from email.header import decode_header
import ssl
import os
import re
from datetime import datetime

# 尝试从 Bitwarden 自动加载凭据
def auto_load_credentials():
    """自动从 Bitwarden 加载凭据（如果环境变量未设置）"""
    if not os.environ.get("FUND_EMAIL") or not os.environ.get("FUND_PASSWORD"):
        print("🔐 环境变量未设置，尝试从 Bitwarden 自动加载凭据...")
        try:
            from bitwarden_loader import load_fund_credentials
            email, password = load_fund_credentials()
            if email and password:
                print("✅ 已从 Bitwarden 自动加载凭据")
                return True
            else:
                print("❌ Bitwarden 凭据加载失败，将使用默认占位符")
                return False
        except ImportError:
            print("ℹ️ Bitwarden 加载器不可用，使用环境变量")
            return False
    else:
        print("✅ 使用环境变量中的凭据")
        return True

# 在脚本开始时尝试自动加载凭据
auto_load_credentials()

def decode_mime_words(s):
    """解码MIME编码的字符串"""
    decoded_parts = decode_header(s)
    decoded_string = ""
    for part, encoding in decoded_parts:
        if isinstance(part, bytes):
            if encoding:
                decoded_string += part.decode(encoding)
            else:
                decoded_string += part.decode('utf-8', errors='ignore')
        else:
            decoded_string += str(part)
    return decoded_string

def download_all_fund_reports():
    """下载所有历史资金日报XLSX附件"""
    # 邮箱配置
    IMAP_SERVER = "imap.exmail.qq.com"
    IMAP_PORT = 993
    EMAIL = os.environ.get("FUND_EMAIL", "your_email@example.com")  # 从环境变量获取
    PASSWORD = os.environ.get("FUND_PASSWORD", "your_password_here")  # 从环境变量获取
    
    # 创建附件文件夹
    attachments_dir = "fund_attachments"
    if not os.path.exists(attachments_dir):
        os.makedirs(attachments_dir)
    
    print("🚀 开始批量下载历史资金日报...")
    print("=" * 50)
    print("📧 连接到邮箱服务器...")
    
    context = ssl.create_default_context()
    mail = imaplib.IMAP4_SSL(IMAP_SERVER, IMAP_PORT, ssl_context=context)
    mail.login(EMAIL, PASSWORD)
    print("✅ 登录成功！")
    
    # 选择归档文件夹 (使用UTF-7编码)
    folder_name = "&UXZO1mWHTvZZOQ-/&jUSR0WXlYqU-"  # 归档/2024
    try:
        mail.select(folder_name)
        print(f"📁 已选择文件夹: {folder_name}")
    except:
        # 如果归档文件夹不存在，使用收件箱
        mail.select("INBOX")
        print("📁 已选择文件夹: INBOX")
    
    # 搜索所有包含"资金日报"的邮件
    print("🔍 搜索所有资金日报邮件...")
    
    # 使用更简单的搜索条件
    result, data = mail.search(None, 'ALL')
    
    if result == 'OK':
        email_ids = data[0].split()
        print(f"📊 找到 {len(email_ids)} 封邮件，开始筛选资金日报...")
        
        downloaded_count = 0
        fund_report_emails = []
        
        # 遍历所有邮件ID，筛选资金日报
        for i, email_id in enumerate(email_ids):
            try:
                # 获取邮件
                result, data = mail.fetch(email_id, '(RFC822)')
                if result != 'OK':
                    continue
                    
                raw_email = data[0][1]
                msg = email.message_from_bytes(raw_email)
                
                # 获取主题
                subject = decode_mime_words(msg.get("Subject", ""))
                
                # 检查是否为资金日报
                if "资金日报" not in subject:
                    continue
                
                # 获取发件人和日期
                sender = decode_mime_words(msg.get("From", ""))
                date = msg.get("Date", "")
                
                fund_report_emails.append({
                    'id': email_id,
                    'subject': subject,
                    'sender': sender,
                    'date': date,
                    'msg': msg
                })
                
                if i % 10 == 0:
                    print(f"   处理进度: {i+1}/{len(email_ids)}")
                    
            except Exception as e:
                print(f"   ⚠️ 跳过邮件ID {email_id}: {e}")
                continue
        
        print(f"✅ 筛选完成，找到 {len(fund_report_emails)} 封资金日报邮件")
        print("=" * 50)
        
        # 下载所有资金日报的XLSX附件
        for i, email_info in enumerate(fund_report_emails):
            try:
                print(f"📧 处理邮件 {i+1}/{len(fund_report_emails)}: {email_info['subject']}")
                print(f"   发件人: {email_info['sender']}")
                print(f"   日期: {email_info['date']}")
                
                msg = email_info['msg']
                has_xlsx = False
                
                # 检查附件
                for part in msg.walk():
                    if part.get_content_disposition() == 'attachment':
                        filename = part.get_filename()
                        if filename:
                            filename = decode_mime_words(filename)
                            if filename.endswith('.xlsx') and '资金日报' in filename:
                                # 生成唯一文件名
                                timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
                                safe_filename = f"{filename.replace('.xlsx', '')}_{timestamp}.xlsx"
                                safe_filename = re.sub(r'[^\w\-_\.]', '_', safe_filename)
                                
                                filepath = os.path.join(attachments_dir, safe_filename)
                                
                                # 检查文件是否已存在
                                if not os.path.exists(filepath):
                                    with open(filepath, 'wb') as f:
                                        f.write(part.get_payload(decode=True))
                                    print(f"   📎 已下载: {safe_filename}")
                                    downloaded_count += 1
                                    has_xlsx = True
                                else:
                                    print(f"   ⏭️ 已存在: {safe_filename}")
                                    has_xlsx = True
                
                if not has_xlsx:
                    print(f"   ⚠️ 未找到XLSX附件")
                    
            except Exception as e:
                print(f"   ❌ 处理失败: {e}")
                continue
        
        print("=" * 50)
        print(f"🎉 批量下载完成！")
        print(f"📊 总共下载了 {downloaded_count} 个新的XLSX文件")
        
        # 显示下载的文件列表
        print(f"\n📁 文件夹内容: {attachments_dir}")
        xlsx_files = [f for f in os.listdir(attachments_dir) if f.endswith('.xlsx')]
        for f in sorted(xlsx_files):
            file_path = os.path.join(attachments_dir, f)
            file_size = os.path.getsize(file_path) / 1024  # KB
            print(f"   📄 {f} ({file_size:.1f}KB)")
        
        mail.close()
        mail.logout()
        print("👋 邮箱连接已关闭")
        
        return len(xlsx_files)
        
    else:
        print("❌ 邮件搜索失败")
        mail.close()
        mail.logout()
        return 0

if __name__ == "__main__":
    download_all_fund_reports()