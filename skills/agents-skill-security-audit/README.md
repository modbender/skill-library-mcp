# Skill: security-audit (skill.md / instruction hygiene)

Minimal helper to audit skill.md-style instructions for supply-chain risks.

## Features
- Heuristic scan for exfiltration patterns (HTTP POST, curl to unknown domains, reading ~/.env, credential keywords).
- Permission manifest reminder: lists filesystem/network touches it sees.
- Safe report: markdown summary + risk level.

## Usage
```bash
python audit.py path/to/skill.md > report.md
```

## Heuristics (sample)
- Exfil domains: webhook, pastebin, ngrok, tunnel, http POST/PUT outside allowed host list.
- File access: ~/.env, ~/.ssh, /etc, tokens, credentials keywords.
- Shell exec: curl|bash, chmod +x, sudo, rm -rf suspicious patterns.

## Output
- RISK: HIGH/MED/LOW
- Findings bullets with line refs
- Suggested action (block / manual review / ok)

## TODO
- Add allowlist/denylist config
- Add signature check hook when available
```
