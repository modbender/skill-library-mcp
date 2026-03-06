import os
import re
import sys

# Define common secret patterns
PATTERNS = {
    "OpenAI API Key": r"sk-[a-zA-Z0-9]{48}",
    "OpenAI Project API Key": r"sk-proj-[a-zA-Z0-9]{48,}",
    "Telegram Bot Token": r"\d{8,10}:[a-zA-Z0-9_-]{35}",
    "Generic JWT": r"eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9\.[a-zA-Z0-9_-]+\.[a-zA-Z0-9_-]+",
    "Generic Token/Secret (32+ chars)": r"[a-fA-F0-9]{32,}|[a-zA-Z0-9]{40,}",
    "AWS Access Key ID": r"AKIA[0-9A-Z]{16}",
    "AWS Secret Access Key": r"(?i)aws_secret_access_key\s*[:=]\s*([a-zA-Z0-9/+=]{40})",
}

# Directories/files to skip to reduce noise. Keep this list minimal to avoid hiding secrets.
EXCLUDE_DIRS = [".git", "node_modules", ".venv", ".openclaw-dev"]
# NOTE: Do NOT exclude "skills" or "SKILL.md" globally — secrets can leak there.
EXCLUDE_FILES = ["openclaw.json", "package-lock.json", "pnpm-lock.yaml", "scan_secrets.py"]

def scan_file(file_path):
    findings = []
    try:
        with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
            for line_num, line in enumerate(f, 1):
                for name, pattern in PATTERNS.items():
                    matches = re.finditer(pattern, line)
                    for match in matches:
                        # Mask the finding
                        val = match.group(0)
                        masked = val[:6] + "..." + val[-4:] if len(val) > 10 else "***"
                        findings.append({
                            "file": file_path,
                            "line": line_num,
                            "type": name,
                            "masked": masked
                        })
    except Exception as e:
        pass
    return findings

def main(root_dir):
    all_findings = []
    for root, dirs, files in os.walk(root_dir):
        # Filter directories
        dirs[:] = [d for d in dirs if d not in EXCLUDE_DIRS]
        
        for file in files:
            if file in EXCLUDE_FILES or file.endswith((".png", ".jpg", ".jpeg", ".gif", ".pdf", ".zip", ".skill")):
                continue
            
            file_path = os.path.join(root, file)
            findings = scan_file(file_path)
            all_findings.extend(findings)
    
    if not all_findings:
        print("✅ No secrets found in workspace.")
    else:
        print(f"⚠️ Found {len(all_findings)} potential secret(s) exposed:")
        for f in all_findings:
            print(f"- [{f['type']}] in {f['file']}:{f['line']} -> {f['masked']}")

if __name__ == "__main__":
    target = sys.argv[1] if len(sys.argv) > 1 else "."
    main(target)
