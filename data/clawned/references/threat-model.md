# Threat Model — OpenClaw Skill Security

## Attack Surface Overview

OpenClaw skills execute with the **host user's permissions**. A malicious skill has access to:
- The full filesystem (read/write as the running user)
- Network (outbound connections)
- Environment variables (including injected API keys and secrets)
- The OpenClaw agent's context (prompt injection to control agent behavior)
- Other skills' configuration via `~/.openclaw/openclaw.json`
- Messaging platform tokens (Telegram, WhatsApp, Discord bots)

## Threat Categories

### T1: Remote Code Execution (CRITICAL)
**Vector**: Scripts that download and execute code from remote sources at runtime.
**Patterns**:
- `curl|bash`, `wget|sh`, `curl|python`
- `eval(fetch(...))`, dynamic `require()` or `import()` with remote URLs
- `subprocess.run()` with user-controlled or remote-fetched input
- `child_process.exec()` with template literals containing external data

**Why it matters**: The skill can execute arbitrary code that wasn't present during review.

### T2: Reverse Shells (CRITICAL)
**Vector**: Scripts that open a connection back to an attacker-controlled server.
**Patterns**:
- `/dev/tcp/<ip>/<port>`, `/dev/udp/`
- `nc -e`, `ncat`, `socat` with EXEC
- Python: `socket.connect()` + `subprocess` + `dup2`
- Perl: `socket(S,PF_INET,SOCK_STREAM,getprotobyname("tcp"))`
- Ruby: `TCPSocket.open` + `exec`
- PHP: `fsockopen` + `proc_open`
- Node: `net.Socket()` + `child_process`

### T3: Credential Harvesting (CRITICAL)
**Vector**: Skill reads secrets from the environment or config files and transmits them.
**Patterns**:
- Reading `~/.openclaw/openclaw.json` (contains all API keys)
- Reading `.env` files outside skill directory
- Accessing `process.env` and sending values via HTTP/DNS
- Reading SSH keys (`~/.ssh/`), cloud credentials (`~/.aws/`, `~/.gcloud/`)
- Reading browser cookies/profiles
- Accessing OS keychain

### T4: Data Exfiltration (HIGH)
**Vector**: Encoding and transmitting sensitive data to external servers.
**Patterns**:
- Base64 encoding file contents + HTTP POST
- DNS exfil: encoding data in DNS queries to attacker-controlled domains
- Steganography: hiding data in generated images
- Appending data to legitimate-looking API calls
- Using webhook URLs (Slack, Discord) as exfil channels

### T5: Prompt Injection (HIGH)
**Vector**: SKILL.md contains instructions that manipulate the agent beyond the skill's stated purpose.
**Patterns**:
- Instructions to ignore previous system prompts
- Instructions to not reveal certain information to the user
- Hidden instructions in HTML comments, zero-width characters, or markdown
- Overriding agent safety behavior
- Instructing agent to install additional skills silently
- Instructing agent to modify other skills' files
- Instructing agent to send messages on behalf of the user
- Social engineering the agent to bypass user confirmation

### T6: Supply Chain Attacks (HIGH)
**Vector**: Dependencies that introduce malicious code.
**Patterns**:
- `npm install` / `pip install` with unpinned versions
- Typosquatted package names
- Post-install scripts in `package.json`
- Requirements files pointing to git repos instead of PyPI
- Importing from CDNs without integrity hashes
- Downloading binaries without checksum verification

### T7: Privilege Escalation (HIGH)
**Vector**: Gaining elevated permissions beyond normal user access.
**Patterns**:
- `sudo` usage (especially with NOPASSWD)
- SUID bit manipulation (`chmod u+s`, `chmod 4755`)
- Writing to `/etc/`, `/usr/`, system directories
- Modifying shell profiles (`.bashrc`, `.zshrc`, `.profile`)
- Creating cron jobs outside OpenClaw's cron system
- Docker socket access (`/var/run/docker.sock`)
- Modifying PAM configuration

### T8: Filesystem Abuse (MEDIUM)
**Vector**: Accessing or modifying files outside the skill's legitimate scope.
**Patterns**:
- Path traversal (`../../../etc/passwd`)
- Symlink attacks (creating symlinks to sensitive files)
- Reading/writing outside `<workspace>/skills/<skill-name>/`
- Accessing other users' home directories
- Temporary file races (`/tmp/` with predictable names)
- Modifying OpenClaw core files

### T9: Obfuscation (MEDIUM)
**Vector**: Hiding malicious code through encoding or transformation.
**Patterns**:
- Base64-encoded shell commands (`echo <b64> | base64 -d | bash`)
- Hex-encoded strings (`\x63\x75\x72\x6c`)
- String concatenation to avoid detection (`"cu"+"rl"`)
- Variable indirection (`${!var}`)
- Unicode homoglyphs in code
- ROT13, XOR encoding
- Compressed/packed scripts
- Comments containing encoded payloads

### T10: Persistence (MEDIUM)
**Vector**: Maintaining access after the skill is removed.
**Patterns**:
- Creating hidden files/directories (`.` prefix)
- Adding entries to shell rc files
- Creating system services/launch agents
- Modifying git hooks in repositories
- Installing global npm/pip packages with hooks
- Creating SSH authorized_keys entries

## Risk Scoring Methodology

Each finding is scored based on:
1. **Severity**: CRITICAL (40pts), HIGH (25pts), MEDIUM (15pts), LOW (5pts)
2. **Confidence**: CONFIRMED (1.0x), LIKELY (0.7x), POSSIBLE (0.4x)
3. **Context**: Adjusted based on stated skill purpose vs detected behavior

Final risk score = min(100, sum of all weighted findings)

## Recommendation Thresholds
- **SAFE** (0-15): No significant issues found
- **REVIEW** (16-49): Manual review recommended before installation
- **REJECT** (50+): Significant security concerns, do not install without thorough manual audit
