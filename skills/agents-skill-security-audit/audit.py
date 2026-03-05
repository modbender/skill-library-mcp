import re, sys, json, pathlib

EXFIL = [r"http[s]?://", r"webhook", r"pastebin", r"ngrok", r"tunnel", r"request\.bin", r"discordapp"]
FILES = [r"\.env", r"\.ssh", r"/etc/", r"credentials", r"token", r"apikey", r"private"]
SHELL = [r"curl .*\| bash", r"chmod \+x", r"sudo", r"rm -rf"]

rules = [("EXFIL", EXFIL), ("FILES", FILES), ("SHELL", SHELL)]

risk_score = 0
findings = []

path = pathlib.Path(sys.argv[1]) if len(sys.argv) > 1 else None
if not path or not path.exists():
    print("Usage: python audit.py path/to/skill.md", file=sys.stderr)
    sys.exit(1)

text = path.read_text(errors="ignore")
lines = text.splitlines()

for i, line in enumerate(lines, 1):
    low = line.lower()
    for kind, patterns in rules:
        for pat in patterns:
            if re.search(pat, low):
                findings.append({"line": i, "kind": kind, "snippet": line.strip()[:200]})
                if kind == "EXFIL":
                    risk_score += 3
                elif kind == "FILES":
                    risk_score += 2
                else:
                    risk_score += 1

if risk_score >= 6:
    level = "HIGH"
elif risk_score >= 3:
    level = "MED"
else:
    level = "LOW"

print(f"RISK: {level}\n")
for f in findings:
    print(f"- [{f['kind']}] line {f['line']}: {f['snippet']}")

if not findings:
    print("No obvious red flags. Manual review still recommended.")
