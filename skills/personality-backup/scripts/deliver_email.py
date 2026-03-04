#!/usr/bin/env python3
"""Send backup archive via email."""
import json, sys, os, smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.base import MIMEBase
from email.mime.text import MIMEText
from email import encoders
from datetime import datetime

config_file = sys.argv[1]
with open(config_file) as f:
    c = json.load(f)

email_cfg = c.get("email", {})
agent_name = c.get("agent_name", "Agent")
agent_emoji = c.get("agent_emoji", "")

archive_path = os.environ["CFG_ARCHIVE_PATH"]
archive_name = os.environ["CFG_ARCHIVE_NAME"]
size = os.environ["CFG_SIZE"]

smtp_pass = email_cfg.get("smtp_pass", "")
if not smtp_pass:
    env_var = email_cfg.get("smtp_pass_env", "")
    if env_var:
        smtp_pass = os.environ.get(env_var, "")

msg = MIMEMultipart()
msg["From"] = email_cfg["from"]
msg["To"] = email_cfg["to"]
msg["Subject"] = f"{agent_name} Daily Backup — {datetime.now().strftime('%Y-%m-%d')}"

body = f"Daily personality backup ({size}).\n\nEncrypted with AES-256 via 7-zip.\n\n— {agent_name} {agent_emoji}\n"
msg.attach(MIMEText(body, "plain"))

with open(archive_path, "rb") as f:
    part = MIMEBase("application", "x-7z-compressed")
    part.set_payload(f.read())
    encoders.encode_base64(part)
    part.add_header("Content-Disposition", "attachment", filename=archive_name)
    msg.attach(part)

smtp = smtplib.SMTP_SSL(email_cfg["smtp_host"], email_cfg.get("smtp_port", 465))
smtp.login(email_cfg.get("smtp_user", email_cfg["from"]), smtp_pass)
smtp.send_message(msg)
smtp.quit()
print("Email sent successfully!")
