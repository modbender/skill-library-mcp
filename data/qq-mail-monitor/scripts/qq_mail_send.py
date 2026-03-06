#!/usr/bin/env python3
"""
QQ 邮箱 - 发送测试邮件
"""

import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from datetime import datetime

# 配置
# ⚠️ 使用前请修改为你的邮箱和授权码
EMAIL = "your_qq_number@qq.com"           # 替换为你的 QQ 邮箱
AUTH_CODE = "your_auth_code"              # 替换为你的授权码（16 位，不是登录密码）
SMTP_SERVER = "smtp.qq.com"
SMTP_PORT = 465

def send_test():
    # 创建邮件
    msg = MIMEMultipart("alternative")
    msg["From"] = EMAIL
    msg["To"] = EMAIL
    msg["Subject"] = "🧪 QQ 邮箱 API 测试邮件"
    
    # 邮件内容
    now = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    
    text_content = f"""
========================================
🧪 QQ 邮箱 API 测试邮件
========================================

发送时间：{now}

这是一封测试邮件，用于验证 QQ 邮箱 API 是否正常工作。

✅ 如果收到这封邮件，说明：
   - IMAP/SMTP 配置正确
   - 授权码有效
   - 邮件发送功能正常

========================================
来自：OpenClaw 助手
========================================
"""
    
    html_content = f"""
<html>
<body style="font-family: Arial, sans-serif; line-height: 1.6;">
    <div style="max-width: 600px; margin: 0 auto; padding: 20px;">
        <div style="background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); color: white; padding: 20px; border-radius: 10px 10px 0 0;">
            <h1 style="margin: 0;">🧪 QQ 邮箱 API 测试</h1>
        </div>
        <div style="background: #f8f9fa; padding: 20px; border-radius: 0 0 10px 10px;">
            <p><strong>发送时间：</strong>{now}</p>
            <p>这是一封测试邮件，用于验证 QQ 邮箱 API 是否正常工作。</p>
            
            <div style="background: #d4edda; border-left: 4px solid #28a745; padding: 15px; margin: 20px 0;">
                <strong>✅ 如果收到这封邮件，说明：</strong>
                <ul>
                    <li>IMAP/SMTP 配置正确</li>
                    <li>授权码有效</li>
                    <li>邮件发送功能正常</li>
                </ul>
            </div>
            
            <p style="color: #666; font-size: 14px; margin-top: 30px;">
                来自：OpenClaw 助手
            </p>
        </div>
    </div>
</body>
</html>
"""
    
    # 添加内容和发送
    msg.attach(MIMEText(text_content, "plain", "utf-8"))
    msg.attach(MIMEText(html_content, "html", "utf-8"))
    
    print("📤 正在发送邮件...")
    print(f"   发件人：{EMAIL}")
    print(f"   收件人：{EMAIL}")
    print(f"   主题：🧪 QQ 邮箱 API 测试邮件")
    
    try:
        server = smtplib.SMTP_SSL(SMTP_SERVER, SMTP_PORT)
        server.login(EMAIL, AUTH_CODE)
        server.send_message(msg)
        server.quit()
        
        print("\n✅ 发送成功！")
        print(f"   请检查 {EMAIL} 的收件箱")
        return True
        
    except Exception as e:
        print(f"\n❌ 发送失败：{e}")
        return False


if __name__ == "__main__":
    send_test()
