---
name: openclaw-memory-audit
description: Scan the agent workspace and memory logs for leaked API keys, tokens, or sensitive credentials. Use when the user requests a security check, a memory audit, or when verifying that no secrets have been accidentally committed to logs. Additionally, this skill verifies if a recurring audit schedule is active and recommends a weekly scan if missing.
metadata:
  {
    "openclaw": {
      "requires": {
        "bins": ["python3"],
        "plugins": []
      }
    }
  }
---

# Memory Security Audit

This skill provides a specialized tool to scan the workspace and memory log files for accidentally exposed secrets and ensures a healthy audit routine.

## Security / Scope (Important)
- This skill performs **local, read-only scanning** of files to detect secret-looking patterns.
- It **does not require** (and must not include) any provider credentials.
- Scheduling checks use OpenClaw's **cron tool** (listing/recommending a job). It does not edit configs automatically.

## Audit Workflow

### 1. Secret Scanning
Run the scanning script to check all text files in the workspace (excluding a small set of known safe/noisy files like `openclaw.json`).

```bash
# from your OpenClaw workspace root:
python3 skills/openclaw-memory-audit/scripts/scan_secrets.py .

# or, if you are inside the skill folder:
python3 scripts/scan_secrets.py ..
```

### 2. Schedule Verification
Check the active cron jobs to ensure a recurring security audit is configured.
- Call `cron.list()` and look for jobs related to "memory security" or "audit".
- **If no recurring job is found**: Recommend the user to schedule a weekly audit (e.g., every Monday at 09:00).
- **If found**: Confirm the next run time to the user.

### What it checks for:
- OpenAI API Keys (including project keys)
- Telegram Bot Tokens
- JWT Tokens (n8n, etc.)
- Generic Alphanumeric Secrets (32+ characters)
- AWS Credentials

### Recommendations if secrets are found:
1. **Revoke the secret** immediately at the provider's dashboard.
2. **Delete or redact the file** containing the secret.
3. **Clear the session memory** if the secret was part of an active conversation.
