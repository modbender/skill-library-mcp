# Arc-Shield Quick Reference Card

## One-Liner Usage

```bash
# Check before sending (production use)
echo "$MESSAGE" | arc-shield.sh --strict || echo "BLOCKED"

# Sanitize logs
cat log.txt | arc-shield.sh --redact > clean.log

# Audit what was leaked
arc-shield.sh --report < old-conversation.txt
```

## Common Patterns Detected

| Type | Example | Severity |
|------|---------|----------|
| 1Password | `ops_eyJhbGc...` | CRITICAL |
| GitHub | `ghp_abc123...` | CRITICAL |
| OpenAI | `sk-proj-...` | CRITICAL |
| AWS | `AKIAIOSFOD...` | CRITICAL |
| Password | `password: secret123` | CRITICAL |
| Eth Key | `0x1234...` (64 hex) | CRITICAL |
| Mnemonic | `abandon ability able...` | CRITICAL |
| SSN | `123-45-6789` | CRITICAL |
| CC | `4532-1234-5678-9010` | HIGH |
| Secret Path | `~/.secrets/key.txt` | WARN |

## Exit Codes

- `0` = Clean (safe to send)
- `1` = Critical secrets found (blocked)

## Modes

| Mode | Use Case | Output |
|------|----------|--------|
| (default) | Development | Pass through + warnings |
| `--strict` | Production sends | Block on critical |
| `--redact` | Logging | Replace with `[REDACTED:TYPE]` |
| `--report` | Audit | Analysis only |

## Integration Template

```bash
send_safe() {
    local msg="$1"
    local channel="$2"
    
    if echo "$msg" | arc-shield.sh --strict 2>/dev/null; then
        openclaw message send --channel "$channel" "$msg"
    else
        echo "❌ Blocked: contains secrets" >&2
        return 1
    fi
}
```

## Test It

```bash
# Good - should pass
echo "Hello world" | arc-shield.sh --strict
echo $?  # 0

# Bad - should block
echo "Token: ghp_abc123def456ghi789jkl012mno345pqr" | arc-shield.sh --strict
echo $?  # 1
```

## Performance

- **Bash**: ~10ms per message
- **Python**: ~50ms with entropy detection
- Fast enough for every outbound message

## Files You Need

```
arc-shield/
├── scripts/arc-shield.sh      ← Main tool
├── scripts/output-guard.py    ← Entropy detection
└── config/patterns.conf       ← Patterns (edit to customize)
```

## Help

```bash
arc-shield.sh --help
output-guard.py --help
```

## Remember

⚠️ This is an **OUTPUT** filter (not input).  
⚠️ Use `--strict` before external messages.  
⚠️ Train your agent to avoid secrets.  
✅ Arc-shield catches mistakes.
