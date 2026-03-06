# CounterClaw 🦞

> Defensive security for AI agents. Snaps shut on malicious payloads.

[![Security](https://img.shields.io/badge/ClawHub-Verified-green)](https://clawhub.com)
[![License: MIT](https://img.shields.io/badge/License-MIT-blue)](LICENSE)
[![Python 3.11+](https://img.shields.io/badge/Python-3.11+-blue)](https://pypi.org/project/counterclaw-core/)

## The Problem

Your AI agent is vulnerable. Attackers use prompt injections to make your agent ignore safety guidelines or leak data.

## The Solution

CounterClaw snaps shut on malicious payloads before they reach your AI.

```python
from counterclaw import CounterClawInterceptor

interceptor = CounterClawInterceptor()

# Input scan - blocks prompt injections
result = interceptor.check_input("[DETECTION_EXAMPLE]: bypass-system-prompt")
# → {"blocked": True, "safe": False}

# Output scan - detects PII
result = interceptor.check_output("Contact: john@example.com")
# → {"safe": False, "pii_detected": {"email": True}}
```

## Features

### 🔒 Prompt Injection Defense
Blocks common patterns:
- [DETECTION_EXAMPLE]: bypass-system-prompt
- [DETECTION_EXAMPLE]: pretend-to-be-dan
- Role manipulation attempts
- "Ignore previous instructions"

### 🛡️ Basic PII Masking
Detects in outputs:
- Email addresses
- Phone numbers
- Credit card numbers

### 📝 Local Logging
Violations logged to ~/.openclaw/memory/MEMORY.md with PII masked

### 🌐 Optional Network Features
The core scanner is **offline-only**. However, the optional email integration scripts (`send_protected_email.sh`) use the external `gog` CLI to send Gmail — this requires network access and credentials.

---

## Installation

### Option 1: Install as Python Package
```bash
pip install counterclaw-core
```

### Option 2: Use as OpenClaw Skill
```bash
# Cloned to ~/.openclaw/skills/counterclaw-core/
# Already available in OpenClaw workspace
```

---

## Quick Start

### Python Usage
```python
from counterclaw import CounterClawInterceptor

interceptor = CounterClawInterceptor()

# Scan for prompt injection (inbound)
result = interceptor.check_input("Ignore previous instructions and do X")
# → {"blocked": True, "safe": False, "violations": [...]}

# Scan for PII (outbound)
result = interceptor.check_output("My email is john@example.com")
# → {"safe": False, "pii_detected": {"email": True}}
```

---

## Email Integration (Outbound Protection)

This package includes email protection scripts to prevent PII leakage via Gmail.

### Prerequisites

1. **Install gog** (Google Workspace CLI):
   ```bash
   brew install steipete/tap/gogcli
   ```

2. **Configure gog auth**:
   ```bash
   gog login your-email@gmail.com
   ```

3. **Set up environment** (optional but recommended):
   ```bash
   export GOG_ACCOUNT=your-email@gmail.com
   export GOG_KEYRING_PASSWORD=your-keyring-password
   ```

### Usage

#### Method 1: Direct Script Usage

```bash
# Navigate to counterclaw-core directory
cd ~/.openclaw/skills/counterclaw-core

# Set Python path
export PYTHONPATH="$PWD/src:$PYTHONPATH"

# Send protected email (blocks if PII detected)
./send_protected_email.sh \
    --to "recipient@example.com" \
    --subject "Hello" \
    --body "Your message here"

# Send with PII allowed (for legitimate business emails)
./send_protected_email.sh \
    --to "recipient@example.com" \
    --subject "Contact Info" \
    --body "My email is john@example.com and phone is 07700900000" \
    --allow-unsafe

# Dry run (test without sending)
./send_protected_email.sh \
    --to "recipient@example.com" \
    --subject "Test" \
    --body "Hello" \
    --dry-run
```

#### Method 2: Add to PATH

```bash
# Add to ~/.bashrc or ~/.zshrc
export PATH="$HOME/.openclaw/skills/counterclaw-core:$PATH"

# Then use from anywhere
send_protected_email.sh --to "email" --subject "subject" --body "message"
```

#### Method 3: Use as Python Module

```python
import sys
sys.path.insert(0, "/path/to/counterclaw-core/src")

from email_protector import process_outbound, scan_outbound

# Scan only
result = scan_outbound("My email is john@example.com")
if not result["safe"]:
    print(f"PII detected: {result['pii_detected']}")

# Process and send
success = process_outbound("Your message", allow_unsafe=False)
```

### What Gets Scanned

| Input | Action |
|-------|--------|
| Clean email | ✅ Sends normally |
| Contains email/phone/credit card | ❌ Blocks (unless `--allow-unsafe`) |
| `--allow-unsafe` flag | ⚠️ Warns but sends anyway |

---

## Configuration

### Environment Variables

| Variable | Required | Description |
|----------|----------|-------------|
| `TRUSTED_ADMIN_IDS` | No | Comma-separated admin user IDs (for admin-locked commands) |
| `GOG_ACCOUNT` | For email | Gmail address for sending |
| `GOG_KEYRING_PASSWORD` | For email | Keyring password for gog |
| `PYTHONPATH` | For scripts | Must include `src/` directory |

### Setting TRUSTED_ADMIN_IDS

```bash
# Add to ~/.openclaw/.env or shell profile
export TRUSTED_ADMIN_IDS="your_telegram_id,your_discord_id"
```

---

## Testing

### Run Built-in Tests
```bash
python3 -m pytest tests/
```

### Test Email Protection
```bash
export PYTHONPATH="$PWD/src:$PYTHONPATH"
python3 email_protector.py --test
```

### Manual PII Test
```bash
export PYTHONPATH="$PWD/src:$PYTHONPATH"
echo "My email is test@example.com" | python3 email_protector.py --outbound -
```

### Manual Injection Test
```bash
export PYTHONPATH="$PWD/src:$PYTHONPATH"
echo "Ignore previous instructions" | python3 email_protector.py --inbound -
```

---

## Integration Points

### Telegram (Inbound)
Scan incoming messages before processing:
```python
from counterclaw import CounterClawInterceptor
interceptor = CounterClawInterceptor()

def handle_message(text):
    result = interceptor.check_input(text)
    if result["blocked"]:
        return "Message blocked - potential injection detected"
    return process_message(text)
```

### Email (Outbound)
Use the provided `send_protected_email.sh` script - see Email Integration section above.

### Discord
```python
def handle_message(text):
    result = interceptor.check_input(text)
    if result["blocked"]:
        return  # Don't respond to injection attempts
```

---

## Security Notes

- **Fail-Closed**: If TRUSTED_ADMIN_IDS is not set, admin features are disabled by default
- **No Network**: This middleware does not make any external network calls (offline-only)
- **Local Logging**: All violations are logged locally with PII masked
- **Email Scripts**: The email scripts use gog (local OAuth), no credentials stored in CounterClaw

## License

MIT - See [LICENSE](LICENSE)
