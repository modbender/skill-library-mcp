# Installation & Setup Guide

## Quick Install

```bash
cd ~/.openclaw/workspace/skills
git clone <repo-url> arc-shield
cd arc-shield
chmod +x scripts/*.sh scripts/*.py tests/*.sh examples/*.sh
./tests/quick-test.sh
```

## Manual Install

If not using git:

```bash
# Create directory
mkdir -p ~/.openclaw/workspace/skills/arc-shield/{scripts,config,tests,examples}

# Download files (or copy manually)
# - scripts/arc-shield.sh
# - scripts/output-guard.py
# - config/patterns.conf
# - tests/quick-test.sh
# - examples/*

# Make executable
chmod +x ~/.openclaw/workspace/skills/arc-shield/scripts/*.sh
chmod +x ~/.openclaw/workspace/skills/arc-shield/scripts/*.py
chmod +x ~/.openclaw/workspace/skills/arc-shield/tests/*.sh
chmod +x ~/.openclaw/workspace/skills/arc-shield/examples/*.sh

# Test
cd ~/.openclaw/workspace/skills/arc-shield/tests
./quick-test.sh
```

## Requirements

- **Bash** 4.0+ (ships with macOS/Linux)
- **Python** 3.6+ (for entropy detection)
- **grep** with `-E` flag (extended regex)
- **sed** with `-E` flag (extended regex)

No external dependencies. Pure stdlib.

## Integration with OpenClaw

### Method 1: Pre-send Hook (Recommended)

Create a hook that runs before all external messages:

```bash
# ~/.openclaw/workspace/hooks/pre-send.sh
#!/bin/bash
ARC_SHIELD="${HOME}/.openclaw/workspace/skills/arc-shield/scripts/arc-shield.sh"

message="$1"
channel="$2"

# Skip internal channels
if [[ "$channel" =~ ^(internal|agent) ]]; then
    exit 0
fi

# Scan
if ! echo "$message" | "$ARC_SHIELD" --strict 2>/dev/null; then
    echo "❌ Message blocked by arc-shield" >&2
    exit 1
fi

exit 0
```

Then in your agent's message sending code:

```bash
send_message() {
    if ~/.openclaw/workspace/hooks/pre-send.sh "$message" "$channel"; then
        openclaw message send --channel "$channel" "$message"
    fi
}
```

### Method 2: Wrapper Script

Create a `send-safe` command:

```bash
# ~/.openclaw/bin/send-safe
#!/bin/bash
ARC_SHIELD="${HOME}/.openclaw/workspace/skills/arc-shield/scripts/arc-shield.sh"

channel="$1"
shift
message="$*"

if echo "$message" | "$ARC_SHIELD" --strict 2>/dev/null; then
    openclaw message send --channel "$channel" "$message"
else
    echo "❌ Message blocked: contains secrets" >&2
    exit 1
fi
```

Usage:
```bash
send-safe discord "Hello world"  # Safe
send-safe discord "Token: ghp_abc123..."  # BLOCKED
```

### Method 3: Pipe Through

Manual scanning before each send:

```bash
RESPONSE=$(generate_agent_response)

# Sanitize
CLEAN=$(echo "$RESPONSE" | arc-shield.sh --redact)

# Send
openclaw message send --channel discord "$CLEAN"
```

## Configuration

### Custom Patterns

Edit `config/patterns.conf`:

```conf
# Add your own patterns
CRITICAL|MyService Token|mytoken_[a-zA-Z0-9]{32,}
HIGH|Internal Secret|SECRET_[A-Z0-9]{16,}
WARN|Dev Path|/internal/secrets/[^\s]*
```

Format: `SEVERITY|Category Name|regex_pattern`

### Adjust Sensitivity

For the Python version (entropy detection):

```bash
# More sensitive (more false positives)
output-guard.py --entropy-threshold 4.0

# Less sensitive (might miss some secrets)
output-guard.py --entropy-threshold 5.0

# Default: 4.5 (good balance)
output-guard.py
```

## Testing Your Setup

```bash
cd ~/.openclaw/workspace/skills/arc-shield

# Quick smoke test
./tests/quick-test.sh

# Visual demo
./examples/demo.sh

# Test with your own samples
echo "Your test message" | scripts/arc-shield.sh --report

# Strict mode test (should block)
echo "Token: ghp_abc123def456ghi789jkl012mno345pqr" | scripts/arc-shield.sh --strict
# Exit code: 1

# Strict mode test (should pass)
echo "Normal message" | scripts/arc-shield.sh --strict
# Exit code: 0
```

## Troubleshooting

### "Permission denied" errors

```bash
chmod +x scripts/*.sh scripts/*.py tests/*.sh examples/*.sh
```

### "grep: unrecognized option" errors

macOS/BSD grep issue. Install GNU grep:

```bash
brew install grep
# Use as ggrep instead of grep
```

Or the scripts should work with `grep -E --` (already fixed in v1.0.0).

### False positives

1. Check `config/patterns.conf` — you may need to refine patterns
2. Adjust entropy threshold: `output-guard.py --entropy-threshold 5.0`
3. Add exceptions to patterns (negative lookbehind/lookahead)

### Secrets not detected

1. Check pattern coverage: `arc-shield.sh --report`
2. Test pattern manually: `echo "test" | grep -oE 'your_pattern'`
3. Add custom pattern to `config/patterns.conf`
4. Lower entropy threshold (Python): `--entropy-threshold 4.0`

## Performance Tuning

For high-volume usage:

```bash
# Use bash version only (skip entropy detection)
arc-shield.sh  # ~10ms

# Skip Python
# output-guard.py  # ~50ms

# Limit input size
head -c 10000 | arc-shield.sh

# Run in background for async checking
arc-shield.sh --report &
```

## Uninstall

```bash
rm -rf ~/.openclaw/workspace/skills/arc-shield
```

That's it. No system changes, no dependencies to clean up.

## Next Steps

1. ✅ **Run tests**: `./tests/quick-test.sh`
2. ✅ **Try demo**: `./examples/demo.sh`
3. ✅ **Add patterns**: Edit `config/patterns.conf`
4. ✅ **Integrate**: Set up pre-send hook
5. ✅ **Read docs**: See `SKILL.md` for full details

## Support

- Documentation: [SKILL.md](SKILL.md)
- Examples: [examples/](examples/)
- Tests: [tests/](tests/)
- Issues: File on GitHub

---

**Remember**: Arc-shield is your safety net. Train your agent to avoid secrets, use arc-shield to catch mistakes.
