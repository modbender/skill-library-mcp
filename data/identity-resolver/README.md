# identity-resolver

**Solve multi-channel identity fragmentation in OpenClaw**

[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![Tests](https://img.shields.io/badge/tests-24%20passing-success)](tests/)

## The Problem

Users interact via multiple channels — Telegram, WhatsApp, Discord, web. Without identity resolution, each channel creates a separate user identity, fragmenting state across your skills:

```
telegram:123456789      → memory tree A
whatsapp:+1234567890    → memory tree B
discord:user#1234        → memory tree C
web:session_abc          → memory tree D
```

**Result:** User has 4+ fragmented states instead of one unified identity.

## The Solution

**identity-resolver** maps all channel identities to one canonical user ID:

```
telegram:123456789  ─┐
whatsapp:+1234567890─┼─→ "alice" (canonical ID)
discord:user#1234    ─┤
web:session_abc      ─┘
```

Now all channels share one memory tree, one access level, one user state.

## Features

✅ **Auto-registers owner** from workspace USER.md  
✅ **Thread-safe** file operations (fcntl locking)  
✅ **CLI + Python API** — works for users and skill developers  
✅ **Path traversal protection** — secure by design  
✅ **Zero dependencies** — pure Python stdlib  
✅ **Test coverage** — 24 tests, 100% passing

## Installation

### Prerequisites

Install `uv` (modern Python package manager):
```bash
curl -LsSf https://astral.sh/uv/install.sh | sh
```

### Install the Skill

**Option 1: Via ClawHub** (recommended)
```bash
cd /path/to/openclaw/workspace
clawhub install identity-resolver
```

**Option 2: Via Git**
```bash
cd /path/to/openclaw/workspace
git clone https://github.com/clawinfra/identity-resolver skills/identity-resolver
cd skills/identity-resolver
uv sync  # Optional: creates .venv for development
```

## Quick Start

### Initialize

```bash
uv run python skills/identity-resolver/scripts/identity_cli.py init
```

Auto-detects owner from `USER.md` and creates identity map.

### Resolve Identity

```bash
# From environment variables
OPENCLAW_CHANNEL=telegram OPENCLAW_USER_ID=123456789 \
  uv run python skills/identity-resolver/scripts/identity_cli.py resolve

# Or explicit params
uv run python skills/identity-resolver/scripts/identity_cli.py resolve \
  --channel telegram --user-id 123456789
```

Output: `alice` (canonical ID)

### Add User

```bash
uv run python skills/identity-resolver/scripts/identity_cli.py add \
  --canonical alice \
  --channel discord \
  --user-id alice#1234 \
  --display-name "Alice"
```

### List All

```bash
uv run python skills/identity-resolver/scripts/identity_cli.py list
```

## For Skill Developers

Integrate identity resolution into your skill in 3 lines:

```python
from identity import resolve_canonical_id
import os

# Get canonical user ID
canonical_id = resolve_canonical_id(
    os.getenv("OPENCLAW_CHANNEL"),
    os.getenv("OPENCLAW_USER_ID")
)

# Use for user-specific storage
user_data_path = f"data/users/{canonical_id}/state.json"
```

## Use Cases

**Skills that need this:**

- 🧠 **tiered-memory** — unified memory across channels
- 🔐 **agent-access-control** — recognize users across platforms
- 💬 **conversation-history** — cross-channel chat logs
- ⚙️ **user-preferences** — settings follow the user
- 📊 **analytics** — accurate per-user metrics
- ✅ **task-manager** — tasks linked to canonical user

**Any skill storing per-user data should use identity-resolver.**

## How It Works

1. **Auto-registration**: Reads owner numbers from `USER.md`, auto-registers on first use
2. **Lookup**: Given `(channel, provider_user_id)`, returns canonical ID
3. **Fallback**: Unmapped users get `stranger:{channel}:{id}` format
4. **Thread-safe**: fcntl locks prevent concurrent write corruption

## Testing

```bash
cd skills/identity-resolver
uv run python tests/test_identity_resolver.py
```

**Output:**
```
Ran 24 tests in 0.078s
OK
✅ ALL TESTS PASSED!
```

## Security

- **Path traversal protected** — canonical IDs sanitized to `[a-z0-9-_]`
- **Input validation** — all user inputs sanitized
- **Thread-safe** — atomic file operations with exclusive locks
- **Owner verification** — only USER.md numbers auto-register as owner

## Architecture

**Components:**
- `scripts/identity.py` — Core API (importable library)
- `scripts/identity_cli.py` — CLI tool
- `tests/test_identity_resolver.py` — Test suite (100% coverage)
- `data/identity-map.json` — User identity storage

**Integration points:**
- OpenClaw session context (`OPENCLAW_CHANNEL`, `OPENCLAW_USER_ID`)
- Workspace `USER.md` for owner detection
- Skills import `identity.py` for canonical ID resolution

## Documentation

- **SKILL.md** — Complete skill documentation
- **Integration examples** — See `docs/` directory
- **API reference** — Inline docstrings in `identity.py`

## Contributing

Pull requests welcome! Please:
1. Add tests for new features
2. Ensure all tests pass
3. Update documentation

## License

MIT © ClawInfra Contributors

## Links

- **GitHub**: https://github.com/clawinfra/identity-resolver
- **Issues**: https://github.com/clawinfra/identity-resolver/issues
- **ClawHub**: https://clawhub.com/skills/identity-resolver
- **OpenClaw**: https://openclaw.ai

---

**Stop fragmenting user state. Use canonical IDs.** 🚀
