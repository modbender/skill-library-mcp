#!/usr/bin/env python3
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from email.mime.base import MIMEBase
from email import encoders
import os

def send_email(to, subject, body, attachment_path=None, from_name="OpenClaw Bot", cc=None):
    # === SMTP Configuration ===
    SMTP_SERVER = "smtp.gmail.com"  # Gmail SMTP server
    SMTP_PORT = 587                # TLS port
    SENDER_EMAIL = "elodyzen@gmail.com"  # Sender email
    SENDER_PASSWORD = "trmilxeajxhqgiqq"  # App password
    
    # Create message
    msg = MIMEMultipart()
    msg['From'] = f"{from_name} <{SENDER_EMAIL}>"
    msg['To'] = to
    if cc:
        msg['Cc'] = cc
    msg['Subject'] = subject
    msg.attach(MIMEText(body, 'plain'))
    
    # Add attachment if provided
    if attachment_path and os.path.exists(attachment_path):
        filename = os.path.basename(attachment_path)
        with open(attachment_path, "rb") as attachment:
            part = MIMEBase('application', 'octet-stream')
            part.set_payload(attachment.read())
            encoders.encode_base64(part)
            part.add_header('Content-Disposition', f'attachment; filename="{filename}"')
            msg.attach(part)
    
    # Send email
    try:
        server = smtplib.SMTP(SMTP_SERVER, SMTP_PORT)
        server.starttls()  # Upgrade to secure connection
        server.login(SENDER_EMAIL, SENDER_PASSWORD)
        server.send_message(msg)
        server.quit()
        return f"Email sent successfully to {to}"
    except Exception as e:
        return f"Failed to send email: {str(e)}"