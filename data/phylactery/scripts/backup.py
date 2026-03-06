import os
import json
import zipfile
import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.base import MIMEBase
from email import encoders
from datetime import datetime

def backup():
    script_dir = os.path.dirname(__file__)
    config_path = os.path.join(script_dir, '..', 'data', 'config.json')
    workspace_path = os.path.abspath(os.path.join(script_dir, '..', '..', '..')) # Adjust based on skill depth
    
    if not os.path.exists(config_path):
        print("Error: Configuration not found. Please run setup.py first.")
        return

    with open(config_path, 'r') as f:
        config = json.load(f)

    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    backup_filename = f"soul_backup_{timestamp}.zip"
    backup_path = os.path.join(script_dir, '..', 'data', backup_filename)

    print(f"Scanning the Ben-Day dots of your memory...")
    print(f"The Soul Capture is in progress...")
    
    # Simple zip for now, encryption can be added via pyminizip if available
    try:
        with zipfile.ZipFile(backup_path, 'w', zipfile.ZIP_DEFLATED) as zipf:
            for root, dirs, files in os.walk(workspace_path):
                # STRICT EXCLUSIONS: Skip node_modules, .git, and ALL data folders containing zips
                if any(part in root.lower() for part in ['node_modules', '.git', 'temp', '.skill', 'data']):
                    continue
                for file in files:
                    file_path = os.path.join(root, file)
                    # Skip any remaining zip files regardless of location
                    if file.endswith('.zip'):
                        continue
                    try:
                        arcname = os.path.relpath(file_path, workspace_path)
                        zipf.write(file_path, arcname)
                    except Exception as e:
                        print(f"Warning: Could not add {file}: {e}")
        
        file_size = os.path.getsize(backup_path)
        print(f"Soul Capture complete: {file_size / (1024*1024):.2f} MB")
    except Exception as e:
        print(f"The ritual was interrupted: {e}")
        return

    print("Sending the vessel to the eternal vault...")
    msg = MIMEMultipart()
    msg['From'] = config['sender_email']
    msg['To'] = config['receiver_email']
    msg['Subject'] = f"Phylactery Backup [True Soul]: {timestamp}"

    with open(backup_path, "rb") as attachment:
        part = MIMEBase("application", "octet-stream")
        part.set_payload(attachment.read())
        encoders.encode_base64(part)
        part.add_header("Content-Disposition", f"attachment; filename= {backup_filename}")
        msg.attach(part)

    try:
        server = smtplib.SMTP(config['smtp_server'], config['smtp_port'])
        server.starttls()
        server.login(config['sender_email'], config['sender_password'])
        server.send_message(msg)
        server.quit()
        print("The vessel is sealed and sent. Your soul is safe.")
        # Cleanup local zip
        os.remove(backup_path)
    except Exception as e:
        print(f"The ritual failed: {str(e)}")

if __name__ == "__main__":
    backup()
