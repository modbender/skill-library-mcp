#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""B站热门视频日报邮件发送脚本 - 支持多收件人"""

import argparse
import os
import re
import smtplib
import sys
from email.message import EmailMessage
from email.headerregistry import Address
from pathlib import Path


def send_email(
    to_emails: list[str],
    subject: str,
    body: str,
    smtp_email: str | None = None,
    smtp_password: str | None = None,
    smtp_host: str | None = None,
    smtp_port: int | None = None,
    html: bool = False,
) -> bool:
    """发送邮件 - 支持多个收件人"""
    smtp_email = smtp_email or os.environ.get("SMTP_EMAIL")
    smtp_password = smtp_password or os.environ.get("SMTP_PASSWORD")
    smtp_host = smtp_host or os.environ.get("SMTP_HOST", "smtp.gmail.com")
    smtp_port = smtp_port or int(os.environ.get("SMTP_PORT", "587"))

    if not smtp_email or not smtp_password:
        print("Error: SMTP credentials not set.")
        return False

    try:
        msg = EmailMessage()
        msg["Subject"] = subject
        msg["From"] = smtp_email
        msg["To"] = ", ".join(to_emails)

        if html:
            msg.set_content(body, subtype="html", charset="utf-8")
        else:
            msg.set_content(body, charset="utf-8")

        print(f"Connecting to {smtp_host}:{smtp_port}...")
        with smtplib.SMTP(smtp_host, smtp_port) as server:
            server.starttls()
            print("Logging in...")
            server.login(smtp_email, smtp_password)
            for email in to_emails:
                print(f"Sending to {email}...")
            server.send_message(msg)

        print(f"[SUCCESS] Email sent to {len(to_emails)} recipient(s)")
        return True

    except Exception as e:
        print(f"[ERROR] Send failed: {e}")
        return False


def markdown_to_html(markdown_text: str) -> str:
    """将 Markdown 转换为精美的 HTML"""
    
    lines = markdown_text.split('\n')
    html_parts = []
    in_video_block = False
    
    for line in lines:
        stripped = line.strip()
        
        if not stripped:
            html_parts.append('')
            continue
        
        # 一级标题
        if stripped.startswith('# ') and not stripped.startswith('## '):
            title = stripped[2:]
            html_parts.append(f'<h1>{title}</h1>')
            continue
        
        # 二级标题 ## 1. 视频标题
        match = re.match(r'^## (\d+)\. (.+)$', stripped)
        if match:
            if in_video_block:
                html_parts.append('</div>')
            num, title = match.groups()
            html_parts.append(f'<div class="video-card">')
            html_parts.append(f'<div class="video-title"><span class="num">{num}</span>{title}</div>')
            in_video_block = True
            continue
        
        # 二级标题 ## 📊 统计
        if stripped.startswith('## '):
            if in_video_block:
                html_parts.append('</div>')
                in_video_block = False
            title = stripped[3:]
            html_parts.append(f'<h2>{title}</h2>')
            continue
        
        # 分隔线
        if stripped == '---':
            if in_video_block:
                html_parts.append('</div>')
                in_video_block = False
            html_parts.append('<hr>')
            continue
        
        # 列表项 - **标签**：内容
        match = re.match(r'^- \*\*(.+?)\*\*：(.+)$', stripped)
        if match:
            label, content = match.groups()
            # 处理 content 中的粗体和链接
            content = re.sub(r'\*\*(.+?)\*\*', r'<strong>\1</strong>', content)
            content = re.sub(r'\[([^\]]+)\]\(([^)]+)\)', r'<a href="\2">\1</a>', content)
            html_parts.append(f'<div class="info-row"><span class="label">{label}：</span><span class="value">{content}</span></div>')
            continue
        
        # 内容大纲列表项
        match = re.match(r'^- \*\*(.+?)\*\*$', stripped)
        if match:
            title = match.group(1)
            html_parts.append(f'<div class="outline-title">{title}</div>')
            continue
        
        # 子列表项
        match = re.match(r'^  - (.+)$', stripped)
        if match:
            content = match.group(1)
            html_parts.append(f'<div class="outline-item">• {content}</div>')
            continue
        
        # 引用块（支持多行，处理内部格式）
        if stripped.startswith('>'):
            content = stripped[1:].strip() if len(stripped) > 1 else ''
            # 处理引用内的粗体和链接
            content = re.sub(r'\*\*(.+?)\*\*', r'<strong>\1</strong>', content)
            content = re.sub(r'\[([^\]]+)\]\(([^)]+)\)', r'<a href="\2">\1</a>', content)
            # 检查是否是连续引用块
            if html_parts and html_parts[-1].startswith('<div class="quote">') and not html_parts[-1].endswith('</div>'):
                html_parts[-1] += f'<br>{content}'
            elif html_parts and html_parts[-1].endswith('</div>') and '<div class="quote">' in html_parts[-1]:
                # 上一行也是引用，合并
                html_parts[-1] = html_parts[-1][:-6] + f'<br>{content}</div>'
            else:
                html_parts.append(f'<div class="quote">{content}</div>')
            continue
        
        # 粗体标签行
        match = re.match(r'^\*\*(.+?)\*\*：$', stripped)
        if match:
            label = match.group(1)
            html_parts.append(f'<div class="section-label">{label}：</div>')
            continue
        
        # 粗体标签带内容
        match = re.match(r'^\*\*(.+?)\*\*：(.+)$', stripped)
        if match:
            label, content = match.groups()
            html_parts.append(f'<div class="section-label">{label}：</div>')
            html_parts.append(f'<div class="section-content">{content}</div>')
            continue
        
        # 视频链接（支持两种格式）
        if stripped.startswith('🔗'):
            # 格式1: 🔗 [点击观看视频](url)
            match = re.search(r'\[([^\]]+)\]\((https://www\.bilibili\.com/video/\S+)\)', stripped)
            if match:
                text, url = match.groups()
                html_parts.append(f'<div class="video-link">🔗 <a href="{url}">{text}</a></div>')
                continue
            # 格式2: 🔗 **视频链接**：url
            match = re.search(r'https://www\.bilibili\.com/video/\S+', stripped)
            if match:
                url = match.group()
                html_parts.append(f'<div class="video-link">🔗 <a href="{url}">点击观看视频</a></div>')
            continue
        
        # 表格行
        if stripped.startswith('|') and stripped.endswith('|'):
            cells = [c.strip() for c in stripped[1:-1].split('|')]
            # 跳过表格分隔行（只包含 - : 空格的行）
            if all(c.replace('-', '').replace(':', '').strip() == '' for c in cells):
                continue
            # 处理单元格中的链接和粗体
            processed_cells = []
            for c in cells:
                c = re.sub(r'\[([^\]]+)\]\(([^)]+)\)', r'<a href="\2">\1</a>', c)
                c = re.sub(r'\*\*(.+?)\*\*', r'<strong>\1</strong>', c)
                processed_cells.append(c)
            # 检查是否是表头行（前一行不是表格行，或者这是第一个表格行）
            is_header = len(html_parts) == 0 or not html_parts[-1].startswith('<tr>')
            if is_header:
                row_html = ''.join(f'<th>{c}</th>' for c in processed_cells)
            else:
                row_html = ''.join(f'<td>{c}</td>' for c in processed_cells)
            html_parts.append(f'<tr>{row_html}</tr>')
            continue
        
        # 普通文本
        text = re.sub(r'\*\*(.+?)\*\*', r'<strong>\1</strong>', stripped)
        html_parts.append(f'<p>{text}</p>')
    
    if in_video_block:
        html_parts.append('</div>')
    
    content = '\n'.join(html_parts)
    content = re.sub(r'(<tr>.*?</tr>(?:\s*<tr>.*?</tr>)*)', r'<table>\1</table>', content, flags=re.DOTALL)
    
    html = f'''<!DOCTYPE html>
<html>
<head>
<meta charset="utf-8">
<style>
body {{ font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", "PingFang SC", "Microsoft YaHei", sans-serif; line-height: 1.6; color: #333; background: #f5f5f5; margin: 0; padding: 20px; }}
.container {{ max-width: 700px; margin: 0 auto; background: #fff; padding: 25px; border-radius: 10px; box-shadow: 0 2px 10px rgba(0,0,0,0.1); }}
h1 {{ color: #00a1d6; font-size: 24px; border-bottom: 2px solid #00a1d6; padding-bottom: 10px; margin-bottom: 20px; }}
h2 {{ color: #333; font-size: 18px; margin: 25px 0 15px 0; }}
.video-card {{ background: #fafafa; border-radius: 8px; padding: 15px 20px; margin: 15px 0; border-left: 4px solid #00a1d6; }}
.video-title {{ font-size: 16px; font-weight: bold; color: #222; margin-bottom: 12px; }}
.num {{ background: #00a1d6; color: #fff; padding: 2px 8px; border-radius: 4px; margin-right: 10px; font-size: 14px; }}
.info-row {{ font-size: 14px; color: #555; margin: 6px 0; }}
.label {{ color: #00a1d6; font-weight: 500; }}
.value {{ color: #333; }}
.section-label {{ font-size: 14px; font-weight: bold; color: #333; margin: 12px 0 6px 0; }}
.section-content {{ font-size: 14px; color: #555; margin-bottom: 10px; }}
.quote {{ background: #e8f4fd; border-left: 3px solid #00a1d6; padding: 10px 15px; margin: 10px 0; font-size: 14px; color: #444; border-radius: 0 6px 6px 0; }}
.outline-title {{ font-size: 14px; font-weight: bold; color: #333; margin: 8px 0 4px 0; }}
.outline-item {{ font-size: 13px; color: #666; margin: 3px 0 3px 15px; }}
.video-link {{ margin-top: 12px; font-size: 14px; }}
.video-link a {{ color: #00a1d6; word-break: break-all; }}
hr {{ border: none; border-top: 1px solid #e0e0e0; margin: 20px 0; }}
table {{ width: 100%; border-collapse: collapse; margin: 15px 0; font-size: 14px; }}
th {{ padding: 10px 12px; border: 1px solid #ddd; background: #00a1d6; color: #fff; font-weight: bold; text-align: left; }}
td {{ padding: 8px 12px; border: 1px solid #ddd; }}
p {{ margin: 8px 0; font-size: 14px; }}
strong {{ color: #333; }}
</style>
</head>
<body>
<div class="container">
{content}
</div>
</body>
</html>'''
    
    return html


def load_config(config_path: str) -> dict:
    """加载 JSON 配置文件"""
    import json
    with open(config_path, 'r', encoding='utf-8') as f:
        return json.load(f)


def main():
    parser = argparse.ArgumentParser(description="B站热门视频日报邮件发送")
    parser.add_argument("--config", "-c", help="配置文件路径（推荐）")
    parser.add_argument("--to", nargs="+", help="收件人邮箱（支持多个）")
    parser.add_argument("--subject", help="邮件主题")
    parser.add_argument("--subject-file", help="从文件读取邮件主题（支持中文）")
    parser.add_argument("--body", help="邮件内容")
    parser.add_argument("--body-file", help="从文件读取邮件内容")
    parser.add_argument("--html", action="store_true", help="转换为 HTML 格式")
    parser.add_argument("--smtp-email", help="发件人邮箱")
    parser.add_argument("--smtp-password", help="邮箱密码")
    parser.add_argument("--smtp-host", default="smtp.gmail.com", help="SMTP 服务器")
    parser.add_argument("--smtp-port", type=int, default=587, help="SMTP 端口")

    args = parser.parse_args()

    # 从配置文件读取
    config = {}
    if args.config:
        config = load_config(args.config)
    
    email_config = config.get('email', {})
    
    # 处理收件人列表（优先命令行参数）
    to_emails = []
    recipients = args.to or email_config.get('recipients', [])
    if isinstance(recipients, str):
        recipients = [recipients]
    for email in recipients:
        to_emails.extend([e.strip() for e in email.split(",") if e.strip()])
    
    print(f"Recipients: {', '.join(to_emails)}")

    # 获取邮件主题
    if args.subject_file:
        subject = Path(args.subject_file).read_text(encoding="utf-8").strip()
    elif args.subject:
        subject = args.subject
    else:
        from datetime import datetime
        subject = f"B站热门视频日报 - {datetime.now().strftime('%Y-%m-%d')}"

    # 获取邮件内容
    if args.body_file:
        body = Path(args.body_file).read_text(encoding="utf-8")
    elif args.body:
        body = args.body
    else:
        print("Error: Please provide --body or --body-file")
        sys.exit(1)

    if args.html:
        body = markdown_to_html(body)

    # SMTP 配置（优先级：命令行参数 > 环境变量 > 配置文件）
    smtp_email = args.smtp_email or os.environ.get('SMTP_EMAIL') or email_config.get('smtp_email')
    smtp_password = args.smtp_password or os.environ.get('SMTP_PASSWORD') or email_config.get('smtp_password')
    
    success = send_email(
        to_emails=to_emails,
        subject=subject,
        body=body,
        smtp_email=smtp_email,
        smtp_password=smtp_password,
        smtp_host=args.smtp_host,
        smtp_port=args.smtp_port,
        html=args.html,
    )

    sys.exit(0 if success else 1)


if __name__ == "__main__":
    main()
