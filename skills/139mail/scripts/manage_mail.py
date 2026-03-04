#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
邮件管理：标记已读/未读、删除、恢复等
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

def list_messages(server, folder='INBOX', limit=20):
    """列出邮件"""
    server.select_folder(folder)
    messages = server.search(['ALL'])
    
    if not messages:
        print(f"文件夹 '{folder}' 中没有邮件")
        return
    
    messages = messages[-limit:]
    
    from email.header import decode_header
    import email
    
    print(f"\n文件夹: {folder} (显示最新 {len(messages)} 封)")
    print("="*60)
    
    for msg_id in reversed(messages):
        fetch_data = server.fetch([msg_id], ['BODY.PEEK[HEADER]'])
        raw_header = fetch_data[msg_id][b'BODY[HEADER]']
        msg = email.message_from_bytes(raw_header)
        
        # 解码
        def decode_str(s):
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
        
        subject = decode_str(msg.get('Subject', '无主题'))
        sender = decode_str(msg.get('From', '未知'))
        
        flags = server.fetch([msg_id], ['FLAGS'])
        is_unread = b'\\Seen' not in flags[msg_id][b'FLAGS']
        status = "📧" if is_unread else "✓"
        
        # 截断显示
        subject = (subject[:40] + '...') if len(subject) > 40 else subject
        sender = (sender[:30] + '...') if len(sender) > 30 else sender
        
        print(f"{status} ID:{msg_id:4d} | {sender:33s} | {subject}")

def main():
    parser = argparse.ArgumentParser(description='邮件管理')
    parser.add_argument('--list', action='store_true', help='列出收件箱邮件')
    parser.add_argument('--list-trash', action='store_true', help='列出已删除邮件')
    parser.add_argument('--mark-read', type=int, help='标记指定ID为已读')
    parser.add_argument('--mark-unread', type=int, help='标记指定ID为未读')
    parser.add_argument('--delete', type=int, help='删除指定ID邮件（移到已删除）')
    parser.add_argument('--restore', type=int, help='从已删除恢复指定ID邮件')
    parser.add_argument('--permanent-delete', type=int, help='永久删除指定ID邮件')
    parser.add_argument('--limit', type=int, default=20, help='显示数量限制')
    
    args = parser.parse_args()
    
    config = load_config()
    if not config:
        print("错误：未配置139邮箱账号")
        return 1
    
    try:
        with connect_server(config) as server:
            if args.list:
                list_messages(server, 'INBOX', args.limit)
            
            elif args.list_trash:
                # 139邮箱的已删除文件夹可能是 'Deleted Messages' 或 'Trash'
                try:
                    list_messages(server, 'Deleted Messages', args.limit)
                except:
                    try:
                        list_messages(server, 'Trash', args.limit)
                    except:
                        print("无法访问已删除文件夹")
            
            elif args.mark_read:
                server.select_folder('INBOX')
                server.add_flags([args.mark_read], ['\\Seen'])
                print(f"✓ 邮件 {args.mark_read} 已标记为已读")
            
            elif args.mark_unread:
                server.select_folder('INBOX')
                server.remove_flags([args.mark_unread], ['\\Seen'])
                print(f"✓ 邮件 {args.mark_unread} 已标记为未读")
            
            elif args.delete:
                server.select_folder('INBOX')
                # 复制到已删除文件夹，然后从收件箱删除
                try:
                    server.copy([args.delete], 'Deleted Messages')
                except:
                    try:
                        server.copy([args.delete], 'Trash')
                    except:
                        pass
                server.delete_messages([args.delete])
                server.expunge()
                print(f"✓ 邮件 {args.delete} 已删除")
            
            elif args.restore:
                # 从已删除恢复到收件箱
                try:
                    server.select_folder('Deleted Messages')
                except:
                    server.select_folder('Trash')
                server.copy([args.restore], 'INBOX')
                server.delete_messages([args.restore])
                server.expunge()
                print(f"✓ 邮件 {args.restore} 已恢复到收件箱")
            
            elif args.permanent_delete:
                # 在当前选中的文件夹中永久删除
                server.delete_messages([args.permanent_delete])
                server.expunge()
                print(f"✓ 邮件 {args.permanent_delete} 已永久删除")
            
            else:
                parser.print_help()
        
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

if __name__ == '__main__':
    exit(main())
