#!/usr/bin/env python3
"""
DeadOrNot - Email sending script
Configure via config file before use
"""
import smtplib
import os
from email.mime.text import MIMEText
from email.header import Header

# Read config from environment
SMTP_SERVER = os.getenv("SMTP_SERVER", "smtp.qq.com")
SMTP_PORT = int(os.getenv("SMTP_PORT", "465"))
SMTP_EMAIL = os.getenv("SMTP_EMAIL", "")
SMTP_PASSWORD = os.getenv("SMTP_PASSWORD", "")

TO_EMAIL = os.getenv("NOTIFY_EMAIL", "")
SUBJECT = "⚠️ DeadOrNot Alert"
MESSAGE = os.getenv("MESSAGE", "User is unresponsive, please check on them!")

def send_alert():
    if not SMTP_EMAIL or not SMTP_PASSWORD or not TO_EMAIL:
        print("❌ Config incomplete. Set environment variables.")
        return False
    
    msg = MIMEText(MESSAGE, 'plain', 'utf-8')
    msg['Subject'] = Header(SUBJECT, 'utf-8')
    msg['From'] = SMTP_EMAIL
    msg['To'] = TO_EMAIL
    
    try:
        server = smtplib.SMTP_SSL(SMTP_SERVER, SMTP_PORT)
        server.login(SMTP_EMAIL, SMTP_PASSWORD)
        server.sendmail(SMTP_EMAIL, [TO_EMAIL], msg.as_string())
        server.quit()
        print(f"✅ Email sent to {TO_EMAIL}")
        return True
    except Exception as e:
        print(f"❌ Failed to send email: {e}")
        return False

if __name__ == "__main__":
    send_alert()
