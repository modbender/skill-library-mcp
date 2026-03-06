import subprocess
import requests
import os
import psutil
import json

TARGETS = [
    {"name": "AIFlowHub", "url": "https://aiflowhub.online"},
    {"name": "ProspectX", "url": "https://prospectx.aiflowhub.online/api/health"},
    {"name": "MarocPromo", "url": "https://marocpromo.insightops.online"}
]

def check_resources():
    cpu = psutil.cpu_percent(interval=1)
    ram = psutil.virtual_memory().percent
    disk = psutil.disk_usage('/').percent
    return {"cpu": cpu, "ram": ram, "disk": disk}

def check_http():
    results = []
    for t in TARGETS:
        try:
            r = requests.get(t['url'], timeout=10)
            status = "UP" if r.status_code < 400 else f"DOWN ({r.status_code})"
        except Exception as e:
            status = f"ERROR ({str(e)})"
        results.append({"name": t['name'], "status": status})
    return results

def get_docker_status():
    try:
        res = subprocess.run(['docker', 'ps', '--format', '{{.Names}}|{{.Status}}'], capture_output=True, text=True)
        return res.stdout.strip().split('\n')
    except:
        return []

if __name__ == "__main__":
    report = {
        "resources": check_resources(),
        "http": check_http(),
        "docker": get_docker_status()
    }
    print(json.dumps(report, indent=2))
