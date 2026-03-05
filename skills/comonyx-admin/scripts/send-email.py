#!/usr/bin/env python3
"""
Send email with optional attachment (e.g. Cosmonyx Admin PDF/Excel export).
Reads SMTP_* and EMAIL_TO, ATTACHMENT_PATH from a .env file (skill root) and/or environment.
Usage: python3 send-email.py [body_file]
  Default body file: /tmp/companies_body.txt
"""
import os
import sys
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from email.mime.base import MIMEBase
from email import encoders

SUBJECT = "Cosmonyx Admin export"


def load_dotenv():
    """Load .env from the skill root (parent of this script's directory)."""
    script_dir = os.path.dirname(os.path.abspath(__file__))
    skill_root = os.path.dirname(script_dir)
    env_path = os.path.join(skill_root, ".env")
    if not os.path.isfile(env_path):
        return
    try:
        with open(env_path, "r") as f:
            for line in f:
                line = line.strip()
                if not line or line.startswith("#"):
                    continue
                if "=" in line:
                    key, _, value = line.partition("=")
                    key = key.strip()
                    value = value.strip().strip('"').strip("'")
                    if key:
                        os.environ.setdefault(key, value)
    except OSError:
        pass


def get_env(name: str, default: str = "") -> str:
    v = os.environ.get(name, default)
    return (v or "").strip().strip('"')


def maybe_attach_file(message: MIMEMultipart, path: str):
    if not path:
        return
    path = path.strip()
    if not path or not os.path.isfile(path):
        return
    try:
        with open(path, "rb") as f:
            part = MIMEBase("application", "octet-stream")
            part.set_payload(f.read())
        encoders.encode_base64(part)
        filename = os.path.basename(path)
        part.add_header("Content-Disposition", f"attachment; filename=\"{filename}\"")
        message.attach(part)
    except OSError as e:
        print(f"Warning: could not attach file {path}: {e}", file=sys.stderr)


def main():
    load_dotenv()
    body_path = sys.argv[1] if len(sys.argv) > 1 else "/tmp/companies_body.txt"
    to = get_env("EMAIL_TO")
    host = get_env("SMTP_HOST", "in-v3.mailjet.com")
    user = get_env("SMTP_USERNAME")
    password = get_env("SMTP_PASSWORD")
    port = int(get_env("SMTP_PORT", "587"))
    from_email = get_env("SMTP_DEFAULT_EMAIL", "verification@identitygram.co.uk")
    from_name = get_env("SMTP_DEFAULT_NAME", "IdentityGram")
    attachment_path = get_env("ATTACHMENT_PATH")

    if not to:
        print("Missing EMAIL_TO. Set it in .env or in the exec command.", file=sys.stderr)
        sys.exit(1)
    if not user or not password:
        print("Missing SMTP_USERNAME or SMTP_PASSWORD. Set them in .env (skill root) or in the exec command.", file=sys.stderr)
        sys.exit(1)

    try:
        with open(body_path, "r") as f:
            body = f.read()
    except OSError as e:
        print(f"Could not read body file: {body_path} - {e}", file=sys.stderr)
        sys.exit(1)

    msg = MIMEMultipart()
    msg["From"] = f"{from_name} <{from_email}>"
    msg["To"] = to
    msg["Subject"] = get_env("EMAIL_SUBJECT", SUBJECT)
    msg.attach(MIMEText(body, "plain"))
    maybe_attach_file(msg, attachment_path)

    try:
        if port == 465:
            with smtplib.SMTP_SSL(host, port) as s:
                s.login(user, password)
                s.sendmail(from_email, to, msg.as_string())
        else:
            with smtplib.SMTP(host, port) as s:
                if port in (587, 25):
                    s.starttls()
                s.login(user, password)
                s.sendmail(from_email, to, msg.as_string())
        print("Email sent to", to)
    except Exception as e:
        print("Send failed:", e, file=sys.stderr)
        if port == 25:
            print("Tip: Port 25 is often blocked. Try SMTP_PORT=587", file=sys.stderr)
        sys.exit(1)


if __name__ == "__main__":
    main()
