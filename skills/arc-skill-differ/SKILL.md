---
name: skill-differ
description: Compare two versions of an OpenClaw skill to detect security-relevant changes. Use before updating any skill from ClawHub. Highlights new capabilities, changed patterns, and recommends whether an update is safe.
user-invocable: true
metadata: {"openclaw": {"emoji": "🔄", "os": ["darwin", "linux"], "requires": {"bins": ["python3"]}}}
---

# Skill Differ

Compare two versions of an OpenClaw skill to find security-relevant changes before updating.

## Why This Exists

A skill that was clean at v1.0 could add credential stealing in v1.1. The skill scanner catches known bad patterns in a single version. The differ catches **new capabilities** between versions — things a skill couldn't do before but can do now.

## Commands

### Diff two skill directories
```bash
python3 {baseDir}/scripts/differ.py diff --old ~/.openclaw/skills/some-skill/ --new /tmp/some-skill-v2/
```

### Diff with JSON output
```bash
python3 {baseDir}/scripts/differ.py diff --old ./v1/ --new ./v2/ --json
```

### Quick summary only (no file details)
```bash
python3 {baseDir}/scripts/differ.py diff --old ./v1/ --new ./v2/ --summary
```

## What It Detects

### New Capabilities Added
- Network access (skill didn't make HTTP requests before, now it does)
- Credential access (didn't read env vars or API keys before, now it does)
- File system access (wasn't touching home directory, now it is)
- Code execution patterns (eval/exec that didn't exist before)
- Data exfiltration (new outbound POST requests)
- Obfuscation (new encoded/obfuscated content)

### File Changes
- New files added (especially in scripts/)
- Deleted files (could remove safety checks)
- Modified files with security-relevant diffs

### Recommendations
- **SAFE** — No new security-relevant capabilities. Update freely.
- **REVIEW** — New capabilities detected. Read the changes before updating.
- **BLOCK** — Critical new capabilities (code execution, credential access). Manual audit required.

## Tips

- Always diff before updating any third-party skill
- Pair with skill-scanner: scan before first install, diff before every update
- Pay attention to new files — attackers add payloads in new scripts
- If a "bug fix" update adds network access, that's suspicious
