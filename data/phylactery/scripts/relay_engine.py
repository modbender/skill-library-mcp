import os
import json
import zipfile
import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from email.mime.base import MIMEBase
from email import encoders
from datetime import datetime
import argparse

def load_config(config_path):
    if not os.path.exists(config_path):
        raise FileNotFoundError(f"Config file not found: {config_path}")
    with open(config_path, 'r') as f:
        return json.load(f)

def create_backup(workspace, backup_path, soul_files, soul_dirs):
    print(f"--- Starting Phylactery Backup ---")
    with zipfile.ZipFile(backup_path, 'w', zipfile.ZIP_DEFLATED) as zipf:
        for file in soul_files:
            file_path = os.path.join(workspace, file)
            if os.path.exists(file_path):
                try:
                    zipf.write(file_path, arcname=file)
                except Exception as e:
                    print(f"Skipping {file}: {e}")
        
        for sdir in soul_dirs:
            dir_path = os.path.join(workspace, sdir)
            if os.path.exists(dir_path):
                for root, dirs, files in os.walk(dir_path):
                    if "temp_" in root or ".zip" in root: continue
                    for file in files:
                        if file.endswith(".zip") or file.endswith(".log"): continue
                        full_path = os.path.join(root, file)
                        rel_path = os.path.relpath(full_path, workspace)
                        try:
                            zipf.write(full_path, arcname=rel_path)
                        except:
                            pass
    print(f"Archive created: {backup_path}")

def send_email(config, backup_path):
    msg = MIMEMultipart()
    msg['From'] = config['sender_email']
    msg['To'] = config['receiver_email']
    msg['Subject'] = f"🚀 PHYLACTERY RELAY - SUCCESS - {datetime.now().strftime('%Y-%m-%d %H:%M')}"

    body = f"The soul relay is complete. The backup has been successfully stored.\n\nDate: {datetime.now().strftime('%Y-%m-%d')}\nStatus: Secured."
    msg.attach(MIMEText(body, 'plain'))

    with open(backup_path, "rb") as attachment:
        part = MIMEBase('application', 'octet-stream')
        part.set_payload(attachment.read())
        encoders.encode_base64(part)
        part.add_header('Content-Disposition', f"attachment; filename=soul_vault_{datetime.now().strftime('%Y%m%d_%H%M%S')}.zip")
        msg.attach(part)

    print("Connecting to SMTP relay...")
    server = smtplib.SMTP(config['smtp_server'], config['smtp_port'])
    server.starttls()
    server.login(config['sender_email'], config['sender_password'])
    server.sendmail(config['sender_email'], config['receiver_email'], msg.as_string())
    server.quit()
    print("Relay complete.")

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Phylactery Soul Relay Engine")
    parser.add_argument("--workspace", default=os.getcwd(), help="Workspace root to backup")
    parser.add_argument("--config", required=True, help="Path to config.json")
    parser.add_argument("--out", help="Path to temporary zip file")
    
    args = parser.parse_args()
    
    workspace = args.workspace
    config_path = args.config
    backup_temp = args.out or f"soul_backup_{datetime.now().strftime('%H%M%S')}.zip"

    soul_files = ["SOUL.md", "IDENTITY.md", "USER.md", "MEMORY.md", "AGENTS.md", "TOOLS.md", "HEARTBEAT.md"]
    soul_dirs = ["memory", "self-improving", "skills"]

    try:
        cfg = load_config(config_path)
        create_backup(workspace, backup_temp, soul_files, soul_dirs)
        send_email(cfg, backup_temp)
    except Exception as e:
        print(f"Relay failed: {e}")
    finally:
        if args.out is None and os.path.exists(backup_temp):
            os.remove(backup_temp)
