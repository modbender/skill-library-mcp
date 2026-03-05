import smtplib
import sys
import os
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from email.mime.base import MIMEBase
from email import encoders

# Config - Load from environment variables for security
SMTP_EMAIL = os.environ.get("SMTP_EMAIL")
SMTP_PASSWORD = os.environ.get("SMTP_PASSWORD")
SMTP_SERVER = os.environ.get("SMTP_SERVER", "smtp.gmail.com")
SMTP_PORT = int(os.environ.get("SMTP_PORT", 587))
# Kindle email can be passed as arg or env var, default to env
DEFAULT_KINDLE_EMAIL = os.environ.get("KINDLE_EMAIL")

if not SMTP_EMAIL or not SMTP_PASSWORD:
    print("ERROR: Missing credentials. Please set SMTP_EMAIL and SMTP_PASSWORD environment variables.")
    sys.exit(1)

if len(sys.argv) < 2:
    print("Usage: python3 send_to_kindle.py <file_path> [optional_filename]")
    sys.exit(1)

file_path = sys.argv[1]

# Use optional filename if provided, otherwise use basename
if len(sys.argv) >= 3:
    filename = sys.argv[2]
else:
    filename = os.path.basename(file_path)

# Determine recipient
to_email = DEFAULT_KINDLE_EMAIL
if not to_email:
    print("ERROR: No Kindle email configured. Set KINDLE_EMAIL env var.")
    sys.exit(1)

msg = MIMEMultipart()
msg['From'] = SMTP_EMAIL
msg['To'] = to_email
msg['Subject'] = f"Doc: {filename}"

msg.attach(MIMEText("Document attached.", 'plain'))

try:
    with open(file_path, "rb") as f:
        attachment = MIMEBase('application', 'octet-stream')
        attachment.set_payload(f.read())
        encoders.encode_base64(attachment)
        attachment.add_header('Content-Disposition', 'attachment', filename=filename)
        msg.attach(attachment)

    server = smtplib.SMTP(SMTP_SERVER, SMTP_PORT)
    server.starttls()
    server.login(SMTP_EMAIL, SMTP_PASSWORD)
    text = msg.as_string()
    server.sendmail(SMTP_EMAIL, to_email, text)
    server.quit()
    print(f"SUCCESS: Sent {filename} to {to_email}")

except Exception as e:
    print(f"ERROR: {e}")
    sys.exit(1)
