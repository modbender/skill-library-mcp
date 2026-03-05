# identity-resolver

**Canonical user identity resolution across messaging channels**

## Description

Resolves multi-channel user identities (Telegram, WhatsApp, Discord, web, etc.) to canonical user IDs, preventing state fragmentation when users interact via multiple channels.

**Problem it solves:** Without identity resolution, a user messaging via Telegram and WhatsApp appears as two different users, causing fragmented memory, access control, and per-user state across skills.

**Solution:** Maps all channel identities to one canonical user ID automatically.

## Installation

**Prerequisites:** Install `uv` if not already installed:
```bash
curl -LsSf https://astral.sh/uv/install.sh | sh
```

**Install the skill:**
```bash
cd /path/to/openclaw/workspace

# Via ClawHub (recommended)
clawhub install identity-resolver

# Or via Git
git clone https://github.com/clawinfra/identity-resolver skills/identity-resolver
```

## Quick Start

### For End Users

```bash
# Initialize identity map (auto-detects owner from USER.md)
cd /path/to/workspace
uv run python skills/identity-resolver/scripts/identity_cli.py init

# Verify your identity
uv run python skills/identity-resolver/scripts/identity_cli.py resolve \
  --channel telegram --user-id YOUR_TELEGRAM_ID
# Output: your-canonical-id

# List all registered identities
uv run python skills/identity-resolver/scripts/identity_cli.py list
```

### For Skill Developers

Add to your skill's Python code:

```python
import sys
from pathlib import Path

# Import identity resolver
sys.path.insert(0, str(Path.cwd() / "skills" / "identity-resolver" / "scripts"))
from identity import resolve_canonical_id

# Get canonical user ID from session context
import os
channel = os.getenv("OPENCLAW_CHANNEL")  # e.g., "telegram"
user_id = os.getenv("OPENCLAW_USER_ID")   # e.g., "123456789"

canonical_id = resolve_canonical_id(channel, user_id)
# Use canonical_id for all user-specific operations

# Example: User-specific memory file
memory_file = f"data/users/{canonical_id}/memory.json"
```

## Features

✅ **Auto-registers owner** from workspace USER.md  
✅ **Thread-safe** identity map storage with fcntl locking  
✅ **CLI + Python API** for both users and developers  
✅ **Path traversal protection** — sanitizes all canonical IDs  
✅ **Zero dependencies** — pure Python stdlib  
✅ **Multi-channel support** — Telegram, WhatsApp, Discord, web, and future channels

## Use Cases

### Multi-User Memory Systems
```python
# tiered-memory skill integration
canonical_id = resolve_canonical_id(channel, user_id)
memory_tree = f"memory/users/{canonical_id}/tree.json"
```

### Access Control
```python
# agent-access-control skill integration
canonical_id = resolve_canonical_id(channel, user_id)
if is_owner(canonical_id):
    # Full access
else:
    # Limited access
```

### Cross-Platform User Tracking
```python
# Same user across Discord + Telegram
discord_id = resolve_canonical_id("discord", "user#1234")
telegram_id = resolve_canonical_id("telegram", "987654321")
# Both resolve to same canonical ID if registered
```

## API Reference

### Core Functions

**`resolve_canonical_id(channel, provider_user_id, workspace=None, owner_numbers=None) -> str`**

Resolve channel identity to canonical user ID.

- Auto-registers owner numbers from USER.md
- Returns canonical ID (e.g., "alice") or "stranger:{channel}:{user_id}" for unmapped users

**`add_channel(canonical_id, channel, provider_user_id, workspace=None, display_name=None)`**

Add channel mapping to a canonical user (creates user if doesn't exist).

**`remove_channel(canonical_id, channel, provider_user_id, workspace=None)`**

Remove channel mapping from canonical user.

**`list_identities(workspace=None) -> dict`**

Return all identity mappings.

**`get_channels(canonical_id, workspace=None) -> list`**

Get all channels for a canonical user.

**`is_owner(canonical_id, workspace=None) -> bool`**

Check if canonical ID is the owner.

### CLI Commands

```bash
# Initialize
identity init [--force]

# Resolve (auto-detect from env or explicit params)
identity resolve [--channel CH] [--user-id ID]

# Add mapping
identity add --canonical ID --channel CH --user-id ID [--display-name NAME]

# Remove mapping
identity remove --canonical ID --channel CH --user-id ID

# List all
identity list [--json]

# Get channels
identity channels --canonical ID [--json]

# Check owner
identity is-owner --canonical ID [--json]
```

## Identity Map Format

Location: `data/identity-map.json` or `memory/identity-map.json`

```json
{
  "version": "1.0",
  "identities": {
{
  "version": "1.0",
  "identities": {
    "alice": {
      "canonical_id": "alice",
      "is_owner": true,
      "display_name": "Alice Johnson",
      "channels": [
        "telegram:123456789",
        "whatsapp:+1234567890",
        "whatsapp:+9876543210",
        "whatsapp:+5555555555"
      ],
      "created_at": "2026-01-15T10:00:00Z",
      "updated_at": "2026-01-15T10:05:00Z"
    },
    "bob": {
      "canonical_id": "bob",
      "is_owner": false,
      "display_name": "Bob Smith",
      "channels": [
        "discord:bob#1234",
        "telegram:987654321"
      ],
      "created_at": "2026-01-15T10:10:00Z",
      "updated_at": "2026-01-15T10:10:00Z"
    }
  }
}
    }
  }
}
```

## Security

- **Path traversal protection**: Canonical IDs sanitized to `[a-z0-9-_]` only
- **Thread-safe operations**: fcntl file locking on all reads/writes
- **Input validation**: All user inputs validated and sanitized
- **Owner auto-registration**: Only numbers from USER.md auto-register as owner

## Integration Examples

See `docs/TIERED_MEMORY_INTEGRATION_EXAMPLE.md` for complete working example.

## License

MIT - See LICENSE file

## Author

OpenClaw Agent <agent@openclaw.local>

## Links

- GitHub: https://github.com/clawinfra/identity-resolver
- Issues: https://github.com/clawinfra/identity-resolver/issues
- ClawHub: https://clawhub.com/skills/identity-resolver
