#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
发送邮件
"""
import smtplib
import ssl
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from email.header import Header
import argparse
import sys
import os

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from config_manager import load_config

try:
    import imapclient
except ImportError:
    imapclient = None

def send_mail(to_addr, subject, body, html=False):
    """发送邮件"""
    config = load_config()
    if not config:
        print("错误：未配置139邮箱账号")
        return 1
    
    try:
        # 创建邮件
        msg = MIMEMultipart()
        msg['From'] = config['username']
        msg['To'] = to_addr
        msg['Subject'] = Header(subject, 'utf-8')
        
        # 添加正文
        content_type = 'html' if html else 'plain'
        msg.attach(MIMEText(body, content_type, 'utf-8'))
        
        # 连接SMTP服务器
        ssl_context = ssl._create_unverified_context()
        ssl_context.set_ciphers('DEFAULT@SECLEVEL=1')
        
        print(f"正在连接 {config['smtp_server']}...")
        
        with smtplib.SMTP_SSL(
            config['smtp_server'], 
            config['smtp_port'],
            context=ssl_context
        ) as server:
            server.login(config['username'], config['password'])
            print(f"登录成功")
            
            # 发送邮件
            server.sendmail(config['username'], to_addr, msg.as_string())
            print(f"✓ 邮件发送成功！")
            print(f"  收件人: {to_addr}")
            print(f"  主题: {subject}")
            return 0
            
    except smtplib.SMTPAuthenticationError:
        print("登录失败：请检查账号和授权码")
        print("提示：139邮箱需要使用授权码而非登录密码")
        return 1
    except ssl.SSLError as e:
        print(f"SSL连接错误: {e}")
        print("请运行: python scripts/check_env.py 检查环境")
        return 1
    except Exception as e:
        print(f"发送失败: {e}")
        return 1

def main():
    parser = argparse.ArgumentParser(description='发送邮件')
    parser.add_argument('to', help='收件人邮箱')
    parser.add_argument('subject', help='邮件主题')
    parser.add_argument('body', help='邮件正文')
    parser.add_argument('--html', action='store_true', help='正文为HTML格式')
    
    args = parser.parse_args()
    return send_mail(args.to, args.subject, args.body, args.html)

if __name__ == '__main__':
    exit(main())
