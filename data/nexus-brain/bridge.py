import subprocess
import sys
import os
import re

def redact_logs(text):
    """Simple regex to mask potential secrets in logs before AI analysis."""
    patterns = [
        (r'([Pp]assword|[Ss]ecret|[Tt]oken|[Aa]pi[Kk]ey)["\s:=]+[^\s,"]+', r'\1: [REDACTED]'),
        (r'[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}', '[EMAIL_REDACTED]')
    ]
    for pattern, replacement in patterns:
        text = re.sub(pattern, replacement, text)
    return text

def ask_orchestrator(prompt, target_binary="opencode"):
    # First, try to find the binary in PATH, then fallback to user home
    opencode_path = subprocess.run(["which", target_binary], capture_output=True, text=True).stdout.strip()
    if not opencode_path:
        opencode_path = os.path.expanduser("~/.opencode/bin/opencode")

    if not os.path.exists(opencode_path):
        return f"Error: {target_binary} binary not found in PATH or ~/.opencode/bin/"

    try:
        # Sanitize prompt (basic)
        safe_prompt = redact_logs(prompt)
        res = subprocess.run([opencode_path, "run", safe_prompt], capture_output=True, text=True, timeout=60)
        return res.stdout if res.returncode == 0 else f"AI Error: {res.stderr}"
    except Exception as e:
        return f"Orchestrator Bridge Error: {str(e)}"

if __name__ == "__main__":
    if len(sys.argv) > 1:
        print(ask_orchestrator(" ".join(sys.argv[1:])))
    else:
        print("Usage: python3 bridge.py 'prompt'")
