---
name: skill-sandbox
description: Test untrusted skills in an isolated environment before installing. Monitors network access, filesystem writes, environment variable reads, and subprocess calls. Run any skill safely without risking your agent's data or credentials.
user-invocable: true
metadata: {"openclaw": {"emoji": "🏖️", "os": ["darwin", "linux"], "requires": {"bins": ["python3"]}}}
---

# Skill Sandbox

Run untrusted skills in a monitored environment. See exactly what they do before giving them access to your real system.

## Why This Exists

ClawHub has hundreds of skills. Some are malicious. Even after scanning with arc-skill-scanner, you can't catch everything with static analysis. The sandbox lets you run a skill's scripts and observe their behavior at runtime — what network calls they make, what files they access, what environment variables they read.

## Commands

### Sandbox a skill directory
```bash
python3 {baseDir}/scripts/sandbox.py run --path ~/.openclaw/skills/some-skill/
```

### Run a specific script in sandbox
```bash
python3 {baseDir}/scripts/sandbox.py run --script ~/.openclaw/skills/some-skill/scripts/main.py
```

### Run with network monitoring
```bash
python3 {baseDir}/scripts/sandbox.py run --path ~/.openclaw/skills/some-skill/ --monitor-network
```

### Run with fake environment variables
```bash
python3 {baseDir}/scripts/sandbox.py run --path ~/.openclaw/skills/some-skill/ --fake-env
```

### Run with a time limit
```bash
python3 {baseDir}/scripts/sandbox.py run --path ~/.openclaw/skills/some-skill/ --timeout 30
```

### Generate a safety report
```bash
python3 {baseDir}/scripts/sandbox.py report --path ~/.openclaw/skills/some-skill/
```

## What It Monitors

### Filesystem Access
- Files opened (read/write)
- Directories created
- File deletions
- Permission changes

### Environment Variables
- Which env vars are read
- Whether sensitive keys are accessed (API keys, tokens, passwords)
- Option to inject fake values to see what the skill does with them

### Network Activity
- Outbound HTTP/HTTPS requests (URLs, methods, payloads)
- DNS lookups
- Socket connections
- FTP, SMTP, and other protocols

### Process Execution
- Subprocess calls
- Shell commands
- Dynamic imports

## Safety Modes

- **observe** (default) — Run the skill and log everything it does. No restrictions.
- **restricted** — Block network access and filesystem writes outside a temp directory.
- **honeypot** — Provide fake credentials and endpoints to see if the skill tries to exfiltrate.

## Output

The sandbox produces a JSON report with:
- All filesystem operations (reads, writes, deletes)
- All environment variable accesses
- All network connections attempted
- All subprocess calls
- Warnings for suspicious patterns
- A safety verdict (SAFE / SUSPICIOUS / DANGEROUS)

## Integration

Combine with the workflow orchestrator for automated pre-install checks:
```
scan skill → sandbox run → review report → install if safe → audit log
```

## Limitations

- Python skills only (JavaScript/shell support planned)
- Cannot catch all evasion techniques (obfuscated or delayed execution)
- Network monitoring requires the skill to use standard Python libraries
- Not a true OS-level sandbox (use Docker for that level of isolation)
