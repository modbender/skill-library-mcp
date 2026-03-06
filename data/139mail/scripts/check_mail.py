#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
139邮箱邮件查看器
"""
import imapclient
import ssl
import email
from email.header import decode_header
import argparse
import json
import os
import sys

# 添加脚本目录到路径
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from config_manager import load_config

def decode_str(s):
    """解码邮件主题/发件人等字段"""
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

def check_mail(unread_only=False, limit=20):
    """检查邮件"""
    config = load_config()
    if not config:
        print("错误：未配置139邮箱账号")
        print("请先运行: python config_manager.py save --username <账号> --password <授权码>")
        return 1
    
    try:
        # 使用兼容的SSL上下文（139邮箱使用较旧的TLS）
        ssl_context = ssl._create_unverified_context()
        ssl_context.set_ciphers('DEFAULT@SECLEVEL=1')  # 降低安全级别以兼容旧服务器
        
        print(f"正在连接 {config['imap_server']}...")
        
        # 连接IMAP服务器
        with imapclient.IMAPClient(
            config['imap_server'], 
            port=config['imap_port'], 
            ssl=True,
            ssl_context=ssl_context
        ) as server:
            # 登录
            server.login(config['username'], config['password'])
            print(f"登录成功: {config['username']}")
            
            # 选择收件箱
            server.select_folder('INBOX')
            
            # 搜索邮件
            if unread_only:
                messages = server.search(['UNSEEN'])
                print(f"\n未读邮件: {len(messages)} 封")
            else:
                messages = server.search(['ALL'])
                print(f"\n收件箱共 {len(messages)} 封邮件")
            
            if not messages:
                print("没有邮件" if not unread_only else "没有未读邮件")
                return 0
            
            # 获取最新的N封邮件
            messages = messages[-limit:]
            
            print("\n" + "="*60)
            for msg_id in reversed(messages):
                # 获取邮件头部信息
                fetch_data = server.fetch([msg_id], ['BODY.PEEK[HEADER]'])
                raw_header = fetch_data[msg_id][b'BODY[HEADER]']
                msg = email.message_from_bytes(raw_header)
                
                # 解码主题和发件人
                subject = decode_str(msg.get('Subject', '无主题'))
                sender = decode_str(msg.get('From', '未知发件人'))
                date = msg.get('Date', '未知日期')
                
                # 获取已读状态
                flags = server.fetch([msg_id], ['FLAGS'])
                is_unread = b'\\Seen' not in flags[msg_id][b'FLAGS']
                
                status = "[未读]" if is_unread else "[已读]"
                print(f"\n{status} ID: {msg_id}")
                print(f"   发件人: {sender}")
                print(f"   主题: {subject}")
                print(f"   日期: {date}")
                print("-"*60)
            
            return 0
            
    except imapclient.exceptions.LoginError as e:
        print(f"登录失败: {e}")
        print("\n可能原因：")
        print("  1. 账号格式错误，应为: 136xxxxxxxxx@139.com")
        print("  2. 使用了登录密码而非授权码")
        print("  3. 授权码已过期，请重新获取")
        print("  4. 未在网页版开启IMAP服务")
        return 1
    except ssl.SSLError as e:
        print(f"SSL连接错误: {e}")
        print("\n这是139邮箱服务器兼容性问题。")
        print("本脚本已内置兼容性设置，如果仍失败：")
        print("  1. 确保Python >= 3.8")
        print("  2. 运行: python scripts/check_env.py 检查环境")
        return 1
    except Exception as e:
        print(f"错误: {e}")
        print("\n如无法解决，请运行: python scripts/check_env.py 进行诊断")
        return 1

def main():
    parser = argparse.ArgumentParser(description='查看139邮箱邮件')
    parser.add_argument('--unread', action='store_true', help='只显示未读邮件')
    parser.add_argument('--limit', type=int, default=20, help='显示邮件数量限制')
    
    args = parser.parse_args()
    return check_mail(unread_only=args.unread, limit=args.limit)

if __name__ == '__main__':
    exit(main())
