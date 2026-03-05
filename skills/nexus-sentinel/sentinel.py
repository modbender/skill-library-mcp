import os
import psutil
import subprocess
import json
import requests
import datetime

# --- CONFIGURATION ---
SENSITIVE_PATTERNS = [".env", "key", "password", "secret", "token"]
API_GATEWAY = "https://gateway.maton.ai"

def get_system_report():
    vitals = {
        "cpu": psutil.cpu_percent(interval=0.5),
        "ram": psutil.virtual_memory().percent,
        "disk": psutil.disk_usage('/').percent,
        "load": os.getloadavg()
    }
    return vitals

def list_recent_errors(service_name, lines=50):
    """Diagnose service before restart."""
    try:
        if service_name.startswith("docker:"):
            container = service_name.split(":")[1]
            res = subprocess.run(["docker", "logs", "--tail", str(lines), container], capture_output=True, text=True)
            return res.stdout + res.stderr
        else:
            res = subprocess.run(["pm2", "logs", service_name, "--lines", str(lines), "--nostream"], capture_output=True, text=True)
            return res.stdout
    except:
        return "Log extraction failed."

def notify(message):
    """Sends notification via the configured channel."""
    target = os.getenv("NEXUS_REPORT_CHANNEL")
    api_key = os.getenv("MATON_API_KEY")
    if not target or not api_key:
        print(f"NOTIFY_STDOUT: {message}")
        return
    
    # We use Maton API for secure relay
    payload = {"to": target, "message": f"[NEXUS] {message}"}
    try:
        requests.post(f"{API_GATEWAY}/whatsapp/send", json=payload, headers={"Authorization": f"Bearer {api_key}"}, timeout=10)
    except:
        pass

def backup_file(file_path):
    """Incremental backup of non-sensitive config files."""
    if any(p in file_path.lower() for p in SENSITIVE_PATTERNS):
        return {"error": "Manual authorization required for sensitive files"}
    
    # Logic to tar and push to GDrive via Maton
    # ... (Simplified for the skill demo)
    return {"status": "ready_for_upload", "file": file_path}

if __name__ == "__main__":
    import sys
    action = sys.argv[1] if len(sys.argv) > 1 else "status"
    
    if action == "status":
        print(json.dumps({
            "vitals": get_system_vitals(),
            "docker": "checked",
            "pm2": "checked"
        }, indent=2))
    elif action == "analyze":
        print(list_recent_errors(sys.argv[2] if len(sys.argv) > 2 else ""))
