#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
搜索邮件
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

def search_mail(keyword):
    """搜索邮件"""
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
            print(f"登录成功: {config['username']}")
            
            server.select_folder('INBOX')
            
            # 搜索主题或发件人包含关键词的邮件
            # 139邮箱支持的基本搜索
            messages = server.search(['OR', 'SUBJECT', keyword, 'FROM', keyword])
            
            print(f"\n搜索关键词: '{keyword}'")
            print(f"找到 {len(messages)} 封匹配邮件\n")
            
            if not messages:
                print("没有找到匹配的邮件")
                return 0
            
            print("="*60)
            for msg_id in reversed(messages[-20:]):  # 最多显示20封
                fetch_data = server.fetch([msg_id], ['BODY.PEEK[HEADER]'])
                raw_header = fetch_data[msg_id][b'BODY[HEADER]']
                msg = email.message_from_bytes(raw_header)
                
                subject = decode_str(msg.get('Subject', '无主题'))
                sender = decode_str(msg.get('From', '未知发件人'))
                date = msg.get('Date', '未知日期')
                
                flags = server.fetch([msg_id], ['FLAGS'])
                is_unread = b'\\Seen' not in flags[msg_id][b'FLAGS']
                
                status = "[未读]" if is_unread else "[已读]"
                print(f"\n{status} ID: {msg_id}")
                print(f"   发件人: {sender}")
                print(f"   主题: {subject}")
                print(f"   日期: {date}")
                print("-"*60)
            
            return 0
            
    except Exception as e:
        print(f"错误: {e}")
        return 1

def main():
    parser = argparse.ArgumentParser(description='搜索139邮箱邮件')
    parser.add_argument('keyword', help='搜索关键词')
    
    args = parser.parse_args()
    return search_mail(args.keyword)

if __name__ == '__main__':
    exit(main())
