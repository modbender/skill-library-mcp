---
name: openclaw-sentinel
user-invocable: true
metadata: {"openclaw":{"emoji":"🏰","requires":{"bins":["python3"]},"os":["darwin","linux","win32"]}}
---

# OpenClaw Sentinel

Supply chain security scanner for agent skills. Detects obfuscated code, known-bad signatures, suspicious install behaviors, dependency confusion, and metadata inconsistencies — before and after installation.

## The Problem

You install skills from the community. Any skill can contain obfuscated payloads, post-install hooks that execute arbitrary code, or supply chain attacks that modify other skills in your workspace. Existing tools verify file integrity after the fact — nothing inspects skills for supply chain risks before they run.


## Commands

### Scan Installed Skills

Deep scan of all installed skills for supply chain risks. Checks file hashes against a local threat database, detects obfuscated code patterns, suspicious install behaviors, dependency confusion, and metadata inconsistencies. Generates a risk score (0-100) per skill.

```bash
python3 {baseDir}/scripts/sentinel.py scan --workspace /path/to/workspace
```

### Scan a Single Skill

```bash
python3 {baseDir}/scripts/sentinel.py scan openclaw-warden --workspace /path/to/workspace
```

### Pre-Install Inspection

Scan a skill directory BEFORE copying it to your workspace. Outputs a SAFE/REVIEW/REJECT recommendation and shows exactly what binaries, network calls, and file operations the skill will perform.

```bash
python3 {baseDir}/scripts/sentinel.py inspect /path/to/skill-directory
```

### Manage Threat Database

View current threat database statistics.

```bash
python3 {baseDir}/scripts/sentinel.py threats --workspace /path/to/workspace
```

Import a community-shared threat list.

```bash
python3 {baseDir}/scripts/sentinel.py threats --update-from threats.json --workspace /path/to/workspace
```

### Quick Status

Summary of installed skills, scan history, and risk score overview.

```bash
python3 {baseDir}/scripts/sentinel.py status --workspace /path/to/workspace
```

## Workspace Auto-Detection

If `--workspace` is omitted, the script tries:
1. `OPENCLAW_WORKSPACE` environment variable
2. Current directory (if AGENTS.md exists)
3. `~/.openclaw/workspace` (default)

## What It Detects

| Category | Patterns |
|----------|----------|
| **Encoded Execution** | eval(base64.b64decode(...)), exec(compile(...)), eval/exec with encoded strings |
| **Dynamic Imports** | \_\_import\_\_('os').system(...), dynamic subprocess/ctypes imports |
| **Shell Injection** | subprocess.Popen with shell=True + string concatenation, os.system() |
| **Remote Code Exec** | urllib/requests combined with exec/eval — download-and-run patterns |
| **Obfuscation** | Lines >1000 chars, high-entropy strings, minified code blocks |
| **Install Behaviors** | Post-install hooks, auto-exec in \_\_init\_\_.py, cross-skill file writes |
| **Hidden Files** | Non-standard dotfiles and hidden directories |
| **Dependency Confusion** | Skills shadowing popular package names, typosquatting near-matches |
| **Metadata Mismatch** | Undeclared binaries, undeclared env vars, invocable flag inconsistencies |
| **Serialization** | pickle.loads, marshal.loads — arbitrary code execution via deserialization |
| **Known-Bad Hashes** | File SHA-256 matches against local threat database |

## Risk Scoring

Each skill receives a score from 0-100:

| Score | Label | Meaning |
|-------|-------|---------|
| 0 | CLEAN | No issues detected |
| 1-19 | LOW | Minor findings, likely benign |
| 20-49 | MODERATE | Review recommended |
| 50-74 | HIGH | Significant risk, review required |
| 75-100 | CRITICAL | Serious supply chain risk |

## Threat Database Format

Community-shared threat lists use this JSON format:

```json
{
  "hashes": {
    "<sha256hex>": {"name": "...", "severity": "...", "description": "..."}
  },
  "patterns": [
    {"name": "...", "regex": "...", "severity": "..."}
  ]
}
```

## Exit Codes

- `0` — Clean, no issues
- `1` — Review needed
- `2` — Threats detected

## No External Dependencies

Python standard library only. No pip install. No network calls. Everything runs locally.

## Cross-Platform

Works with OpenClaw, Claude Code, Cursor, and any tool using the Agent Skills specification.
