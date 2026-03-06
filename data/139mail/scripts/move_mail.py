#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
邮件分拣 - 移动邮件到不同文件夹
"""
import imapclient
import ssl
import argparse
import sys
import os

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from config_manager import load_config

def connect_server(config):
    """连接服务器"""
    ssl_context = ssl._create_unverified_context()
    ssl_context.set_ciphers('DEFAULT@SECLEVEL=1')
    
    server = imapclient.IMAPClient(
        config['imap_server'], 
        port=config['imap_port'], 
        ssl=True,
        ssl_context=ssl_context
    )
    server.login(config['username'], config['password'])
    return server

def list_folders(server):
    """列出所有文件夹"""
    folders = server.list_folders()
    print("\n邮箱文件夹列表：")
    print("="*40)
    for flags, delimiter, name in folders:
        print(f"  - {name}")
    print()

def move_mail(msg_id, target_folder):
    """移动邮件"""
    config = load_config()
    if not config:
        print("错误：未配置139邮箱账号")
        return 1
    
    try:
        with connect_server(config) as server:
            server.select_folder('INBOX')
            
            # 检查邮件是否存在
            messages = server.search(['ALL'])
            if int(msg_id) not in messages:
                print(f"错误：收件箱中没有 ID 为 {msg_id} 的邮件")
                return 1
            
            # 复制到目标文件夹
            server.copy([int(msg_id)], target_folder)
            
            # 从收件箱删除
            server.delete_messages([int(msg_id)])
            server.expunge()
            
            print(f"✓ 邮件 {msg_id} 已移动到 '{target_folder}'")
            return 0
            
    except imapclient.exceptions.IMAPClientError as e:
        print(f"移动失败: {e}")
        print(f"请确认目标文件夹 '{target_folder}' 存在")
        return 1
    except Exception as e:
        print(f"错误: {e}")
        return 1

def main():
    parser = argparse.ArgumentParser(description='邮件分拣')
    parser.add_argument('--list-folders', action='store_true', help='列出所有文件夹')
    parser.add_argument('--move', type=int, help='要移动的邮件ID')
    parser.add_argument('--to', help='目标文件夹')
    
    args = parser.parse_args()
    
    config = load_config()
    if not config:
        print("错误：未配置139邮箱账号")
        return 1
    
    try:
        with connect_server(config) as server:
            if args.list_folders:
                list_folders(server)
            elif args.move and args.to:
                return move_mail(args.move, args.to)
            else:
                parser.print_help()
        
        return 0
        
    except Exception as e:
        print(f"错误: {e}")
        return 1

if __name__ == '__main__':
    exit(main())
