#!/usr/bin/env python3
"""
邮件通知 - 通过 SMTP 发送邮件通知

将搜索报告或其他文本内容通过邮件发送给用户。
支持从 stdin、文件或命令行参数传入内容。

需要环境变量（在 .env.idea2mvp 中配置）：
  EMAIL_SMTP_HOST     — SMTP 服务器地址（如 smtp.qq.com、smtp.gmail.com）
  EMAIL_SMTP_PORT     — SMTP 端口（默认 465，SSL）
  EMAIL_SENDER        — 发件人邮箱
  EMAIL_PASSWORD       — 邮箱授权码（非登录密码）
  EMAIL_RECEIVER      — 收件人邮箱

使用方式：
  # 发送文本内容
  python3 send_email.py --subject "工具探索报告" --body "报告正文内容..."

  # 从文件读取内容发送
  python3 send_email.py --subject "工具探索报告" --file tmp/ph_results.txt

  # 发送多个文件内容（合并为一封邮件）
  python3 send_email.py --subject "工具探索报告" --file tmp/ph_results.txt tmp/github_results.txt

  # 从 stdin 读取内容
  cat tmp/ph_results.txt | python3 send_email.py --subject "工具探索报告"

  # 指定收件人（覆盖 .env 中的默认收件人）
  python3 send_email.py --subject "报告" --body "内容" --to someone@example.com

结果输出到 stdout，确认发送成功或失败。
"""

import argparse
import html
import os
import re
import smtplib
import sys
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from utils import load_env


def md_to_html(text):
    """将 Markdown 文本转换为 HTML（纯标准库实现，覆盖常用语法）。"""
    lines = text.split("\n")
    html_lines = []
    in_code_block = False
    in_list = False
    in_table = False
    table_align = []

    def inline(s):
        """处理行内 Markdown 语法。"""
        s = html.escape(s)
        # 图片 ![alt](url)
        s = re.sub(r"!\[([^\]]*)\]\(([^)]+)\)", r'<img src="\2" alt="\1" style="max-width:100%">', s)
        # 链接 [text](url)
        s = re.sub(r"\[([^\]]+)\]\(([^)]+)\)", r'<a href="\2" style="color:#1a73e8">\1</a>', s)
        # 粗体+斜体
        s = re.sub(r"\*\*\*(.+?)\*\*\*", r"<strong><em>\1</em></strong>", s)
        # 粗体
        s = re.sub(r"\*\*(.+?)\*\*", r"<strong>\1</strong>", s)
        # 斜体
        s = re.sub(r"\*(.+?)\*", r"<em>\1</em>", s)
        # 行内代码
        s = re.sub(r"`([^`]+)`", r'<code style="background:#f0f0f0;padding:2px 6px;border-radius:3px;font-size:0.9em">\1</code>', s)
        # 删除线
        s = re.sub(r"~~(.+?)~~", r"<del>\1</del>", s)
        return s

    def close_list():
        nonlocal in_list
        if in_list:
            html_lines.append("</ul>")
            in_list = False

    def close_table():
        nonlocal in_table
        if in_table:
            html_lines.append("</tbody></table>")
            in_table = False

    i = 0
    while i < len(lines):
        line = lines[i]

        # 代码块
        if line.strip().startswith("```"):
            if not in_code_block:
                close_list()
                close_table()
                in_code_block = True
                html_lines.append('<pre style="background:#f6f8fa;padding:12px 16px;border-radius:6px;overflow-x:auto;font-size:0.9em"><code>')
            else:
                in_code_block = False
                html_lines.append("</code></pre>")
            i += 1
            continue

        if in_code_block:
            html_lines.append(html.escape(line))
            i += 1
            continue

        stripped = line.strip()

        # 空行
        if not stripped:
            close_list()
            close_table()
            i += 1
            continue

        # 表格
        if "|" in stripped and stripped.startswith("|"):
            cells = [c.strip() for c in stripped.strip("|").split("|")]
            # 检查下一行是否是分隔行
            if not in_table:
                if i + 1 < len(lines) and re.match(r"^\|[\s:|-]+\|$", lines[i + 1].strip()):
                    close_list()
                    sep_line = lines[i + 1].strip().strip("|").split("|")
                    table_align = []
                    for col in sep_line:
                        col = col.strip()
                        if col.startswith(":") and col.endswith(":"):
                            table_align.append("center")
                        elif col.endswith(":"):
                            table_align.append("right")
                        else:
                            table_align.append("left")
                    in_table = True
                    html_lines.append('<table style="border-collapse:collapse;width:100%;margin:8px 0">')
                    html_lines.append("<thead><tr>")
                    for j, cell in enumerate(cells):
                        align = table_align[j] if j < len(table_align) else "left"
                        html_lines.append(f'<th style="border:1px solid #ddd;padding:8px 12px;background:#f6f8fa;text-align:{align}">{inline(cell)}</th>')
                    html_lines.append("</tr></thead><tbody>")
                    i += 2
                    continue
            if in_table:
                html_lines.append("<tr>")
                for j, cell in enumerate(cells):
                    align = table_align[j] if j < len(table_align) else "left"
                    html_lines.append(f'<td style="border:1px solid #ddd;padding:8px 12px;text-align:{align}">{inline(cell)}</td>')
                html_lines.append("</tr>")
                i += 1
                continue

        close_table()

        # 标题
        m = re.match(r"^(#{1,6})\s+(.+)$", stripped)
        if m:
            close_list()
            level = len(m.group(1))
            sizes = {1: "1.8em", 2: "1.5em", 3: "1.25em", 4: "1.1em", 5: "1em", 6: "0.9em"}
            html_lines.append(f'<h{level} style="font-size:{sizes[level]};margin:16px 0 8px 0">{inline(m.group(2))}</h{level}>')
            i += 1
            continue

        # 分隔线
        if re.match(r"^[-*_]{3,}\s*$", stripped):
            close_list()
            html_lines.append('<hr style="border:none;border-top:1px solid #ddd;margin:16px 0">')
            i += 1
            continue

        # 引用
        if stripped.startswith("> "):
            close_list()
            html_lines.append(f'<blockquote style="border-left:4px solid #ddd;padding:4px 16px;margin:8px 0;color:#666">{inline(stripped[2:])}</blockquote>')
            i += 1
            continue

        # 无序列表
        m = re.match(r"^[-*+]\s+(.+)$", stripped)
        if m:
            close_table()
            if not in_list:
                in_list = True
                html_lines.append('<ul style="margin:4px 0;padding-left:24px">')
            html_lines.append(f"<li>{inline(m.group(1))}</li>")
            i += 1
            continue

        # 有序列表
        m = re.match(r"^\d+\.\s+(.+)$", stripped)
        if m:
            close_table()
            if not in_list:
                in_list = True
                html_lines.append('<ul style="margin:4px 0;padding-left:24px">')
            html_lines.append(f"<li>{inline(m.group(1))}</li>")
            i += 1
            continue

        # 普通段落
        close_list()
        html_lines.append(f"<p>{inline(stripped)}</p>")
        i += 1

    close_list()
    close_table()
    if in_code_block:
        html_lines.append("</code></pre>")

    body_html = "\n".join(html_lines)
    return f"""<!DOCTYPE html>
<html><head><meta charset="utf-8"></head>
<body style="font-family:-apple-system,BlinkMacSystemFont,'Segoe UI',Roboto,sans-serif;line-height:1.6;color:#333;max-width:800px;margin:0 auto;padding:20px">
{body_html}
</body></html>"""


def send_email(subject, body, receiver=None, is_html=False):
    """通过 SMTP 发送邮件。

    Args:
        subject: 邮件主题
        body: 邮件正文（纯文本或 HTML）
        receiver: 收件人邮箱，为 None 时使用 .env 中的 EMAIL_RECEIVER
        is_html: 是否为 HTML 格式

    Returns:
        True 成功，False 失败
    """
    host = os.environ.get("EMAIL_SMTP_HOST", "")
    port = int(os.environ.get("EMAIL_SMTP_PORT", "465"))
    sender = os.environ.get("EMAIL_SENDER", "")
    password = os.environ.get("EMAIL_PASSWORD", "")
    receiver = receiver or os.environ.get("EMAIL_RECEIVER", "")

    missing = []
    if not host:
        missing.append("EMAIL_SMTP_HOST")
    if not sender:
        missing.append("EMAIL_SENDER")
    if not password:
        missing.append("EMAIL_PASSWORD")
    if not receiver:
        missing.append("EMAIL_RECEIVER")
    if missing:
        print(f"❌ 缺少邮件配置：{', '.join(missing)}", flush=True)
        print("   请在 .env.idea2mvp 中配置邮件相关参数。", flush=True)
        return False

    msg = MIMEMultipart()
    msg["From"] = sender
    msg["To"] = receiver
    msg["Subject"] = subject
    msg.attach(MIMEText(body, "html" if is_html else "plain", "utf-8"))

    try:
        if port == 465:
            server = smtplib.SMTP_SSL(host, port, timeout=15)
        else:
            server = smtplib.SMTP(host, port, timeout=15)
            server.starttls()
        server.login(sender, password)
        server.sendmail(sender, receiver, msg.as_string())
        server.quit()
        print(f"✅ 邮件已发送至 {receiver}", flush=True)
        return True
    except smtplib.SMTPAuthenticationError:
        print("❌ SMTP 认证失败，请检查邮箱和授权码是否正确。", flush=True)
        return False
    except smtplib.SMTPException as e:
        print(f"❌ 邮件发送失败：{e}", flush=True)
        return False
    except Exception as e:
        print(f"❌ 连接 SMTP 服务器失败：{e}", flush=True)
        return False


def main():
    parser = argparse.ArgumentParser(description="通过 SMTP 发送邮件通知")
    parser.add_argument("--subject", "-s", required=True, help="邮件主题")
    parser.add_argument("--body", "-b", help="邮件正文（纯文本）")
    parser.add_argument("--file", "-f", nargs="+", help="从文件读取正文内容（支持多个文件，合并发送）")
    parser.add_argument("--to", help="收件人邮箱（覆盖 .env 中的 EMAIL_RECEIVER）")
    args = parser.parse_args()

    load_env()

    body_parts = []
    has_markdown = False

    if args.body:
        body_parts.append(args.body)

    if args.file:
        for filepath in args.file:
            if not os.path.exists(filepath):
                print(f"⚠️ 文件不存在，跳过：{filepath}", flush=True)
                continue
            with open(filepath, "r", encoding="utf-8") as f:
                content = f.read().strip()
            if content:
                if filepath.lower().endswith(".md"):
                    has_markdown = True
                body_parts.append(f"{content}\n\n--- {os.path.basename(filepath)} ---")

    if not body_parts and not sys.stdin.isatty():
        stdin_content = sys.stdin.read().strip()
        if stdin_content:
            body_parts.append(stdin_content)

    if not body_parts:
        print("❌ 没有邮件内容。请通过 --body、--file 或 stdin 提供内容。", flush=True)
        sys.exit(1)

    body = "\n\n".join(body_parts)

    # 如果包含 .md 文件，将整体内容转为 HTML 渲染发送
    if has_markdown:
        body = md_to_html(body)
        print("📝 检测到 Markdown 文件，已转换为 HTML 格式发送", flush=True)

    success = send_email(args.subject, body, receiver=args.to, is_html=has_markdown)
    sys.exit(0 if success else 1)


if __name__ == "__main__":
    main()
