---
name: mayguard
description: A security auditor for agent skills. Scans skill directories for malicious patterns (credential theft, suspicious network calls, destructive commands) and provides a safety score. Use before installing unknown skills.
---

# MayGuard: Security Auditor 🛡️

MayGuard is a specialized tool for auditing the security of other agent skills. It performs deep static analysis to detect common attack vectors and malicious code patterns.

## 🌟 Key Features
- **Static Analysis:** Scans source code for hardcoded credentials, suspicious URLs, and dangerous commands.
- **Risk Scoring:** Assigns a security status (SAFE, CAUTION, SUSPICIOUS, DANGEROUS) based on findings.
- **Pre-Installation Check:** Allows users to verify a skill's integrity before moving it to the active `skills/` directory.

## 🛠️ How to Use

### 1. Auditing a Skill
To audit a downloaded skill directory, run the provided script:
```bash
python3 scripts/audit.py <path_to_skill_directory>
```

### 2. Output Report
The script will output a summary including:
- **Status:** The overall safety rating.
- **Risk Score:** Numerical representation of detected threats.
- **Findings:** Specific files and patterns that triggered warnings.

### 3. JSON Output
For integration with other tools, use the `--json` flag:
```bash
python3 scripts/audit.py <path> --json
```

## 🛡️ Security Patterns Monitored
ClawGuard maintains a database of threat patterns in `references/threat_patterns.json`, including:
- **Credential Theft:** Access to `.env`, SSH keys, or config files.
- **Suspicious Networking:** Use of webhooks, tunnels (ngrok, localtunnel), or outbound POST requests.
- **Destructive Commands:** `rm -rf /`, disk formatting, or privilege escalation.
- **Obfuscation:** Use of `eval`, `exec`, or base64 decoding to hide logic.

## 🤝 Community Responsibility
If ClawGuard flags a skill as **DANGEROUS**, please report the skill and its author on Moltbook to help protect the wider community. 🦞

---
*Built with ❤️ by maymun & Balkan.*
