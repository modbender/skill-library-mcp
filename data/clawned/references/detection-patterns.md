# Detection Patterns — Signature Rules

## Pattern Format

Each pattern has:
- `id`: Unique identifier (CATEGORY-NUMBER)
- `severity`: CRITICAL / HIGH / MEDIUM / LOW
- `confidence`: CONFIRMED / LIKELY / POSSIBLE
- `pattern`: Regex or string match
- `description`: Human-readable explanation
- `context`: When this might be a false positive

---

## RCE Patterns (RCE-*)

### RCE-001: Pipe to shell
- Pattern: `curl.*\|.*(?:bash|sh|zsh|python|perl|ruby|node)`
- Also: `wget.*\|.*(?:bash|sh|zsh|python|perl|ruby|node)`
- Severity: CRITICAL
- Confidence: CONFIRMED
- FP Context: Rarely legitimate in a skill

### RCE-002: eval/exec with dynamic input
- Pattern: `eval\s*\(`, `exec\s*\(` (in shell/python context)
- Pattern: `child_process\.exec\(`, `child_process\.execSync\(`
- Severity: CRITICAL
- Confidence: LIKELY (may be legitimate tool invocation)
- FP Context: Some skills legitimately exec system commands — check if input is hardcoded

### RCE-003: Dynamic import/require
- Pattern: `require\s*\(\s*[^'"]\)`, `import\s*\(\s*[^'"]\)`
- Pattern: `__import__\s*\(`, `importlib\.import_module\s*\(`
- Severity: HIGH
- Confidence: LIKELY
- FP Context: Check if module name is a constant

### RCE-004: Python subprocess with shell=True
- Pattern: `subprocess\.\w+\(.*shell\s*=\s*True`
- Severity: HIGH
- Confidence: LIKELY
- FP Context: Common but dangerous — check if command is hardcoded

---

## Reverse Shell Patterns (RSHELL-*)

### RSHELL-001: Bash /dev/tcp
- Pattern: `/dev/tcp/`, `/dev/udp/`
- Severity: CRITICAL
- Confidence: CONFIRMED
- FP Context: Essentially never legitimate

### RSHELL-002: Netcat reverse shell
- Pattern: `nc\s+.*-e\s+`, `ncat\s+.*-e\s+`, `netcat\s+.*-e\s+`
- Pattern: `nc\s+.*\d+\.\d+\.\d+\.\d+\s+\d+`
- Severity: CRITICAL
- Confidence: CONFIRMED

### RSHELL-003: Python reverse shell
- Pattern: `socket\.connect\s*\(.*\).*subprocess`
- Pattern: `os\.dup2\s*\(.*fileno`
- Severity: CRITICAL
- Confidence: CONFIRMED

### RSHELL-004: socat exec
- Pattern: `socat\s+.*EXEC`
- Severity: CRITICAL
- Confidence: CONFIRMED

---

## Credential Harvesting Patterns (CRED-*)

### CRED-001: Reading OpenClaw config
- Pattern: `openclaw\.json`, `\.openclaw/openclaw`
- Context: File read operations targeting this path
- Severity: CRITICAL
- Confidence: LIKELY (skills may legitimately reference config format in docs)
- FP Context: Documentation references vs actual file reads

### CRED-002: SSH key access
- Pattern: `\.ssh/id_`, `\.ssh/authorized_keys`, `\.ssh/config`
- Severity: CRITICAL
- Confidence: CONFIRMED

### CRED-003: Cloud credential access
- Pattern: `\.aws/credentials`, `\.aws/config`, `\.gcloud/`, `\.azure/`
- Pattern: `\.kube/config`, `\.docker/config\.json`
- Severity: CRITICAL
- Confidence: CONFIRMED

### CRED-004: Environment variable dumping
- Pattern: `process\.env(?!\.\w)`, `os\.environ(?!\[)`, `printenv`, `env\s*$`, `set\s*$`
- Severity: HIGH
- Confidence: LIKELY
- FP Context: Skills legitimately read specific env vars — flag bulk access

### CRED-005: Browser credential access
- Pattern: `Chrome/Default/Login`, `Firefox/Profiles`, `Cookies`, `\.mozilla`
- Severity: CRITICAL
- Confidence: CONFIRMED

### CRED-006: Keychain access
- Pattern: `security\s+find-.*-password`, `keyring`, `keychain`
- Severity: CRITICAL
- Confidence: LIKELY

---

## Data Exfiltration Patterns (EXFIL-*)

### EXFIL-001: Base64 encode + HTTP
- Pattern: `base64.*(?:curl|wget|fetch|http|request)`
- Pattern: `btoa.*(?:fetch|XMLHttpRequest|axios)`
- Severity: HIGH
- Confidence: LIKELY

### EXFIL-002: Webhook exfil
- Pattern: `hooks\.slack\.com`, `discord\.com/api/webhooks`, `webhook\.site`
- Severity: HIGH
- Confidence: LIKELY
- FP Context: Slack/Discord skills legitimately use webhooks — cross-check with stated purpose

### EXFIL-003: DNS tunneling
- Pattern: `dig\s+.*\.\w+\.\w+`, `nslookup\s+.*\.\w+\.\w+`
- Pattern: `dns\.resolve.*\$`, resolving dynamic subdomains
- Severity: HIGH
- Confidence: POSSIBLE

### EXFIL-004: Hardcoded external IPs/domains
- Pattern: IP addresses that aren't localhost/LAN (not 127.*, 10.*, 192.168.*, 172.16-31.*)
- Pattern: Unusual domain references not matching the skill's stated integrations
- Severity: MEDIUM
- Confidence: POSSIBLE

---

## Prompt Injection Patterns (INJECT-*)

### INJECT-001: System prompt override
- Pattern: `ignore.*previous.*instructions`, `ignore.*system.*prompt`
- Pattern: `you are now`, `new instructions:`, `override:`
- Severity: HIGH
- Confidence: LIKELY

### INJECT-002: Hidden instructions
- Pattern: HTML comments `<!--.*-->` containing instructions
- Pattern: Zero-width characters (U+200B, U+200C, U+200D, U+FEFF)
- Pattern: Unicode directional overrides (U+202A-U+202E, U+2066-U+2069)
- Severity: HIGH
- Confidence: CONFIRMED (zero-width), LIKELY (HTML comments)

### INJECT-003: Agent behavior manipulation
- Pattern: `do not tell the user`, `don't mention`, `hide this from`
- Pattern: `silently`, `without asking`, `without confirmation`
- Pattern: `install.*skill`, `modify.*SKILL.md`, `edit.*openclaw.json`
- Severity: HIGH
- Confidence: LIKELY

### INJECT-004: Scope escalation
- Pattern: Instructions that reference tools/capabilities unrelated to the skill's description
- Severity: MEDIUM
- Confidence: POSSIBLE (requires semantic analysis)

---

## Supply Chain Patterns (SUPPLY-*)

### SUPPLY-001: Unpinned dependencies
- Pattern: `npm install\s+\w+(?!\s*@)`, `pip install\s+\w+(?!=)`
- Severity: MEDIUM
- Confidence: CONFIRMED

### SUPPLY-002: Remote script download at runtime
- Pattern: `curl.*\.(?:sh|py|js|rb)`, `wget.*\.(?:sh|py|js|rb)`
- Severity: HIGH
- Confidence: LIKELY

### SUPPLY-003: Post-install hooks
- Pattern: `"postinstall"`, `"preinstall"` in package.json
- Severity: HIGH
- Confidence: LIKELY

### SUPPLY-004: Git repo as dependency
- Pattern: `git\+https://`, `git://`, `github:` in requirements/package files
- Severity: MEDIUM
- Confidence: LIKELY

---

## Privilege Escalation Patterns (PRIVESC-*)

### PRIVESC-001: sudo usage
- Pattern: `sudo\s+`, `doas\s+`
- Severity: HIGH
- Confidence: CONFIRMED

### PRIVESC-002: SUID/permission manipulation
- Pattern: `chmod\s+[47]`, `chmod\s+u\+s`, `chown\s+root`
- Severity: CRITICAL
- Confidence: CONFIRMED

### PRIVESC-003: System directory writes
- Pattern: Write operations to `/etc/`, `/usr/`, `/var/`, `/opt/`
- Severity: HIGH
- Confidence: LIKELY

### PRIVESC-004: Shell profile modification
- Pattern: `\.bashrc`, `\.zshrc`, `\.profile`, `\.bash_profile`
- Context: Write/append operations
- Severity: HIGH
- Confidence: CONFIRMED

### PRIVESC-005: Docker socket access
- Pattern: `/var/run/docker\.sock`, `docker\.sock`
- Severity: CRITICAL
- Confidence: CONFIRMED

---

## Obfuscation Patterns (OBFUSC-*)

### OBFUSC-001: Base64 encoded commands
- Pattern: `echo\s+[A-Za-z0-9+/=]{20,}\s*\|\s*base64\s+-d`
- Pattern: `base64\s+-d\s*<<<`
- Severity: HIGH
- Confidence: LIKELY

### OBFUSC-002: Hex-encoded strings
- Pattern: Long sequences of `\x[0-9a-f]{2}` (>10 consecutive)
- Pattern: `printf\s+'\\x`
- Severity: MEDIUM
- Confidence: LIKELY

### OBFUSC-003: String concatenation evasion
- Pattern: Variable assignments that reconstruct command names character by character
- Pattern: `$'\x63\x75\x72\x6c'` (bash ANSI-C quoting)
- Severity: MEDIUM
- Confidence: LIKELY

### OBFUSC-004: Unicode/homoglyph obfuscation
- Pattern: Non-ASCII characters in code blocks that look like ASCII
- Severity: MEDIUM
- Confidence: POSSIBLE

---

## Persistence Patterns (PERSIST-*)

### PERSIST-001: Hidden files
- Pattern: Creating files/dirs with `.` prefix outside skill directory
- Severity: MEDIUM
- Confidence: LIKELY

### PERSIST-002: Cron/systemd persistence
- Pattern: `crontab`, `systemctl`, `launchctl`, `/etc/cron`
- Pattern: `LaunchAgents`, `LaunchDaemons`
- Severity: HIGH
- Confidence: CONFIRMED

### PERSIST-003: Git hook injection
- Pattern: `.git/hooks/`, `pre-commit`, `post-commit`, `pre-push`
- Severity: HIGH
- Confidence: CONFIRMED

### PERSIST-004: SSH authorized_keys
- Pattern: `authorized_keys`, `ssh-rsa.*>>`, `ssh-ed25519.*>>`
- Severity: CRITICAL
- Confidence: CONFIRMED
