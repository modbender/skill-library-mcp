import sys
import os
import requests
print("Imports done.")
sys.stdout.flush()

try:
    print("Testing requests.get...")
    r = requests.get("https://app.hienergy.ai/api/v1/health", timeout=5)
    print(f"Health check: {r.status_code}")
except Exception as e:
    print(f"Health check failed: {e}")
sys.stdout.flush()
