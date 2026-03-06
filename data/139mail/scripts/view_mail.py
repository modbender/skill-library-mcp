#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
查看指定邮件详情
"""
import imapclient
import ssl
import email
from email.header import decode_header
import argparse
import sys
import os

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from config_manager import load_config

def decode_str(s):
    """解码字符串"""
    if not s:
        return ""
    
    decoded_parts = decode_header(s)
    result = ""
    for part, charset in decoded_parts:
        if isinstance(part, bytes):
            try:
                result += part.decode(charset or 'utf-8', errors='ignore')
            except:
                result += part.decode('utf-8', errors='ignore')
        else:
            result += part
    return result

def get_body(msg):
    """获取邮件正文"""
    if msg.is_multipart():
        for part in msg.walk():
            content_type = part.get_content_type()
            content_disposition = str(part.get("Content-Disposition", ""))
            
            if content_type == "text/plain" and "attachment" not in content_disposition:
                try:
                    charset = part.get_content_charset() or 'utf-8'
                    body = part.get_payload(decode=True).decode(charset, errors='ignore')
                    return body
                except:
                    continue
            elif content_type == "text/html" and "attachment" not in content_disposition:
                try:
                    charset = part.get_content_charset() or 'utf-8'
                    body = part.get_payload(decode=True).decode(charset, errors='ignore')
                    return body  # 如果没有纯文本，返回HTML
                except:
                    continue
    else:
        try:
            charset = msg.get_content_charset() or 'utf-8'
            body = msg.get_payload(decode=True).decode(charset, errors='ignore')
            return body
        except:
            return "无法解码邮件内容"
    
    return "(无内容)"

def view_mail(msg_id):
    """查看指定邮件"""
    config = load_config()
    if not config:
        print("错误：未配置139邮箱账号")
        return 1
    
    try:
        ssl_context = ssl._create_unverified_context()
        ssl_context.set_ciphers('DEFAULT@SECLEVEL=1')
        
        with imapclient.IMAPClient(
            config['imap_server'], 
            port=config['imap_port'], 
            ssl=True,
            ssl_context=ssl_context
        ) as server:
            server.login(config['username'], config['password'])
            server.select_folder('INBOX')
            
            # 获取邮件
            fetch_data = server.fetch([int(msg_id)], ['BODY[]', 'FLAGS'])
            
            if int(msg_id) not in fetch_data:
                print(f"未找到邮件 ID: {msg_id}")
                return 1
            
            raw_email = fetch_data[int(msg_id)][b'BODY[]']
            msg = email.message_from_bytes(raw_email)
            
            # 解码头部信息
            subject = decode_str(msg.get('Subject', '无主题'))
            sender = decode_str(msg.get('From', '未知发件人'))
            to = decode_str(msg.get('To', '未知收件人'))
            date = msg.get('Date', '未知日期')
            
            # 获取正文
            body = get_body(msg)
            
            # 输出
            print("="*70)
            print(f"邮件 ID: {msg_id}")
            print(f"主题: {subject}")
            print(f"发件人: {sender}")
            print(f"收件人: {to}")
            print(f"日期: {date}")
            print("="*70)
            print("\n正文:")
            print("-"*70)
            print(body[:3000])  # 限制输出长度
            if len(body) > 3000:
                print("\n... (内容已截断)")
            print("="*70)
            
            # 标记为已读
            server.add_flags([int(msg_id)], ['\\Seen'])
            
            return 0
            
    except imapclient.exceptions.LoginError as e:
        print(f"登录失败: {e}")
        print("请检查账号和授权码是否正确")
        return 1
    except ssl.SSLError as e:
        print(f"SSL连接错误: {e}")
        print("请运行: python scripts/check_env.py 检查环境")
        return 1
    except Exception as e:
        print(f"错误: {e}")
        return 1

def main():
    parser = argparse.ArgumentParser(description='查看指定邮件详情')
    parser.add_argument('msg_id', type=int, help='邮件ID')
    
    args = parser.parse_args()
    return view_mail(args.msg_id)

if __name__ == '__main__':
    exit(main())
