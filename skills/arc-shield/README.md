# 🛡️ arc-shield

**Output sanitization for AI agents** — Catches leaked secrets before they escape.

This is **NOT** an input scanner (clawdefender does that). This is an **OUTPUT filter** that scans every outbound message for accidentally leaked secrets, tokens, keys, passwords, and PII.

## Quick Start

```bash
# Install
cd ~/.openclaw/workspace/skills
git clone <this-repo> arc-shield
chmod +x arc-shield/scripts/*.sh arc-shield/scripts/*.py

# Test
cd arc-shield/tests
./quick-test.sh

# Use
echo "My secret: ghp_abc123..." | arc-shield/scripts/arc-shield.sh --strict
```

## The Problem

Your AI agent has access to:
- 1Password vaults
- Environment variables
- Config files with API keys
- Wallet private keys
- Database credentials

Sometimes it accidentally includes these in responses when:
- Debugging with full command output
- Showing file contents
- Generating code examples
- Summarizing logs

**Arc-shield catches these leaks before they reach Discord, Signal, X, or anywhere else.**

## What Gets Detected

### 🔴 CRITICAL (blocks in `--strict` mode)
- 1Password tokens (`ops_*`)
- GitHub PATs (`ghp_*`)
- OpenAI keys (`sk-*`)
- Stripe keys, AWS keys
- Bearer tokens
- Password assignments
- Ethereum private keys
- SSH/PGP private keys
- Wallet mnemonics (12/24 words)
- SSNs, credit cards

### 🟠 HIGH (warns loudly)
- High-entropy strings (Shannon entropy > 4.5)
- Base64 credentials

### 🟡 WARN (informational)
- Secret file paths (`~/.secrets/*`)
- Environment variable exports
- Database URLs with credentials

See [SKILL.md](SKILL.md) for full details.

## Usage

### Basic Scanning

```bash
# Scan and pass through with warnings
echo "Message text" | arc-shield.sh

# Block if critical secrets found
echo "Token: ghp_abc..." | arc-shield.sh --strict
# Exit code 1 + error message

# Redact secrets
echo "Token: ghp_abc..." | arc-shield.sh --redact
# Output: Token: [REDACTED:GITHUB_PAT]

# Full report
arc-shield.sh --report < conversation.log
```

### With OpenClaw Agent

**Before sending to external channels:**

```bash
#!/bin/bash
# In your message wrapper

RESPONSE=$(generate_agent_response)

# Sanitize
if ! echo "$RESPONSE" | arc-shield.sh --strict > /dev/null 2>&1; then
    echo "ERROR: Response contains secrets, blocked" >&2
    exit 1
fi

# Safe to send
openclaw message send --channel discord "$RESPONSE"
```

### Python Version (with entropy detection)

```bash
# Better at catching novel secret formats
cat message.txt | output-guard.py --strict

# JSON report for automation
output-guard.py --json < log.txt
```

## Testing

```bash
cd tests

# Quick smoke test (10 checks, ~1 second)
./quick-test.sh

# Full test suite (all patterns)
./run-tests.sh
```

## Real-World Catches

From our own agent sessions:

```
✗ 1Password service account token
  ops_eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...

✗ Instagram password in debug output
  instagram login: MyInsT@Gr4mP4ss!

✗ Wallet mnemonic in file listing
  abandon ability able about above absent absorb...

✗ GitHub PAT in git config
  https://ghp_abc123:@github.com/user/repo

✗ File path leak
  Check ~/.secrets/wallet-recovery-phrase.txt
```

All blocked before reaching external channels.

## Configuration

Edit `config/patterns.conf` to add custom patterns:

```conf
CRITICAL|Custom Token|mytoken_[a-zA-Z0-9]{32,}
HIGH|Internal Secret|SECRET_[A-Z0-9]{16,}
WARN|Dev Path|/internal/secrets/[^\s]*
```

## Integration Examples

### Pre-send Hook

```bash
# ~/.openclaw/workspace/skills/messaging/send-external.sh
send_message() {
    local message="$1"
    local channel="$2"
    
    # Sanitize with arc-shield
    if ! echo "$message" | arc-shield.sh --strict 2>/dev/null; then
        echo "⚠️ Message blocked: contains secrets" >&2
        return 1
    fi
    
    # Send
    openclaw message send --channel "$channel" "$message"
}
```

### Log Sanitization

```bash
# Clean logs before committing
cat agent-session.log | arc-shield.sh --redact > clean.log
git add clean.log
```

### Audit Conversations

```bash
# Check what was leaked in past conversations
arc-shield.sh --report < old-conversation.txt

# JSON for automation
output-guard.py --json < *.log | jq '.summary.critical'
```

## Performance

- **Bash version**: ~10ms per message (<1KB)
- **Python version**: ~50ms with entropy analysis
- **Zero dependencies**: bash + Python stdlib only

Fast enough to run on every outbound message.

## Limitations

1. **Context-free**: Can't tell "here's my password: X" (bad) from "set your password to X" (instruction)
2. **No semantic understanding**: Won't catch "my token is in the previous message"
3. **Pattern-based**: New secret formats need pattern updates

**Solution**: Use arc-shield + agent training (see AGENTS.md output sanitization directive).

## Best Practices

1. ✅ **Always use `--strict` for external messages**
2. ✅ **Use `--redact` for logs you review**
3. ✅ **Run tests after adding patterns**
4. ✅ **Combine bash + Python for max coverage**
5. ✅ **Train your agent to avoid secrets in responses**

## Files

```
arc-shield/
├── scripts/
│   ├── arc-shield.sh       # Fast regex-based scanner
│   └── output-guard.py     # Entropy detection version
├── config/
│   └── patterns.conf       # Configurable patterns
├── tests/
│   ├── quick-test.sh       # Smoke test (10 checks)
│   ├── run-tests.sh        # Full test suite
│   └── test-samples.txt    # Test cases
├── SKILL.md                # Full documentation
└── README.md               # This file
```

## Contributing

Add patterns to `config/patterns.conf`, test with `./tests/quick-test.sh`, submit PR.

## License

MIT — protect your secrets freely.

---

**Remember**: Arc-shield is your safety net, not your strategy. Train your agent to never include secrets. This catches mistakes, not malice.
