# Claw Brain 🧠

**Personal AI Memory System for AI Agents**

A sophisticated memory and learning system that enables truly personalized AI-human communication.

## Features

- 🎭 **Soul/Personality** - 6 evolving traits (humor, empathy, curiosity, creativity, helpfulness, honesty)
- 👤 **User Profile** - Learns user preferences, interests, communication style
- 💭 **Conversation State** - Real-time mood detection and context tracking
- 📚 **Learning Insights** - Continuously learns from interactions and corrections
- 🧠 **get_full_context()** - Everything for personalized responses
- 🔐 **Encrypted Secrets** - Securely store API keys and credentials

## Installation

### From PyPI (Recommended)

```bash
# Basic installation
pip install clawbrain

# With encryption support (recommended)
pip install clawbrain[encryption]

# With all optional features
pip install clawbrain[all]
```

### Post-Installation Setup

After installation, run the setup command:

```bash
# Interactive setup (generates encryption key, installs hooks)
clawbrain setup

# Backup your encryption key (important!)
clawbrain backup-key --all
```

### For ClawdBot / OpenClaw

```bash
# Install with all features
pip install clawbrain[all]

# Run setup to install hooks
clawbrain setup

# Restart your service
sudo systemctl restart clawdbot  # or openclaw
```

The setup command will:
- Generate a secure encryption key
- Detect your platform (ClawdBot or OpenClaw)
- Install the startup hook automatically
- Test the installation

**Configure your agent ID** (optional, add to systemd service):
```bash
sudo mkdir -p /etc/systemd/system/clawdbot.service.d  # or openclaw.service.d
sudo tee /etc/systemd/system/clawdbot.service.d/brain.conf << EOF
[Service]
Environment="BRAIN_AGENT_ID=your-agent-name"
EOF
sudo systemctl daemon-reload
sudo systemctl restart clawdbot  # or openclaw
```

### For Python Projects

```bash
pip install clawbrain[encryption]
```

## Quick Start

```bash
pip install clawbrain[encryption]
```

```python
from clawbrain import Brain

brain = Brain()
context = brain.get_full_context(
    session_key="chat_123",
    user_id="user",
    agent_id="assistant",
    message="Hey, how's it going?"
)
```

## Storage Options

### Option 1: SQLite (Zero Setup) ✅ Recommended for development

```python
from clawbrain import Brain

# Automatically uses SQLite
brain = Brain({"storage_backend": "sqlite"})
```

**Requirements:** Python 3.10+, no external dependencies

**Best for:**
- Development and testing
- Single-user deployments
- Quick prototyping

---

### Option 2: PostgreSQL + Redis (Production) 🚀

```python
from clawbrain import Brain

# Auto-detects PostgreSQL and Redis
brain = Brain()
```

**Requirements:**
- PostgreSQL 14+ (port 5432)
- Redis 6+ (port 6379)
- Python packages: `psycopg2-binary`, `redis`

**Install dependencies:**
```bash
pip install psycopg2-binary redis
```

**Environment variables (optional):**
```bash
export POSTGRES_HOST=localhost
export POSTGRES_PORT=5432
export POSTGRES_DB=brain_db
export POSTGRES_USER=brain_user
export POSTGRES_PASSWORD=your_password

export REDIS_HOST=localhost
export REDIS_PORT=6379
```

**Best for:**
- Production deployments
- High-concurrency environments
- Distributed AI agents
- Multi-user platforms

---

### Auto-Detection Order

1. PostgreSQL (if available)
2. Redis (if available, used as cache)
3. SQLite (fallback)

You can also force a specific backend:
```python
brain = Brain({"storage_backend": "postgresql"})  # Force PostgreSQL
brain = Brain({"storage_backend": "sqlite"})      # Force SQLite
```
---

## Encrypted Secrets 🔐

ClawBrain supports encrypting sensitive data like API keys and credentials.

**Installation:**
```bash
pip install clawbrain[encryption]
```

**Setup:**
```bash
# Generate encryption key (done automatically during setup)
clawbrain setup

# Backup your key (IMPORTANT!)
clawbrain backup-key --all
```

**Usage:**
```python
from clawbrain import Brain

brain = Brain()

# Store encrypted secret
brain.remember(
    agent_id="assistant",
    memory_type="secret",  # Memory type 'secret' triggers encryption
    content="sk-1234567890abcdef",
    key="openai_api_key"
)

# Retrieve and automatically decrypt
secrets = brain.recall(agent_id="assistant", memory_type="secret")
api_key = secrets[0].content  # Automatically decrypted
```

**Encryption Key Management:**

The encryption key is automatically generated during `clawbrain setup`. Manage it with CLI:

```bash
# View key info (masked)
clawbrain show-key

# View full key
clawbrain show-key --full

# Backup key to file
clawbrain backup-key --output ~/my_backup.txt

# Backup with QR code (requires: pip install clawbrain[qr])
clawbrain backup-key --qr

# Copy to clipboard (requires: pip install clawbrain[clipboard])
clawbrain backup-key --clipboard

# All backup methods
clawbrain backup-key --all
```

**Key Storage Locations:**
- `~/.config/clawbrain/.brain_key` (default)
- Or set via environment: `BRAIN_ENCRYPTION_KEY`

⚠️ **Important**: Backup your encryption key! Lost keys = lost encrypted data.

---

## CLI Commands

ClawBrain includes a command-line interface for setup and management:

```bash
# Setup ClawBrain (generate key, install hooks)
clawbrain setup

# Generate new encryption key
clawbrain generate-key

# Show current encryption key
clawbrain show-key --full

# Backup encryption key
clawbrain backup-key --all

# Check health status
clawbrain health

# Show installation info
clawbrain info
```

---

## Optional Dependencies

Install with specific features:

```bash
# Encryption only
pip install clawbrain[encryption]

# PostgreSQL support
pip install clawbrain[postgres]

# Redis caching
pip install clawbrain[redis]

# Semantic search
pip install clawbrain[embeddings]

# QR code key backup
pip install clawbrain[qr]

# All features
pip install clawbrain[all]
```

---

## Development Installation

### From GitHub

```bash
pip install git+https://github.com/clawcolab/clawbrain.git
```

### From Local Development

```bash
cd /path/to/clawbrain
pip install -e .
```

### For ClawDBot

```bash
# Install as skill
git clone https://github.com/clawcolab/clawbrain.git ClawBrain
```

Then in your bot:
```python
import sys
sys.path.insert(0, "ClawBrain")
from clawbrain import Brain

brain = Brain()
```

## API Reference

### Core Class

```python
from clawbrain import Brain

brain = Brain()
```

**Methods:**

| Method | Description |
|--------|-------------|
| `get_full_context()` | Get all context for personalized responses |
| `remember()` | Store a memory |
| `recall()` | Retrieve memories |
| `learn_user_preference()` | Learn user preferences |
| `get_user_profile()` | Get user profile |
| `detect_user_mood()` | Detect current mood |
| `detect_user_intent()` | Detect message intent |
| `generate_personality_prompt()` | Generate personality guidance |
| `health_check()` | Check backend connections |
| `close()` | Close connections |

### Data Classes

```python
from clawbrain import Memory, UserProfile

# Memory
memory = Memory(
    id="...",
    agent_id="assistant",
    memory_type="fact",
    key="job",
    content="User works at Walmart",
    importance=0.8
)

# User Profile
profile = UserProfile(
    user_id="user",
    name="Alex",
    interests=["AI", "crypto"],
    communication_preferences={"style": "casual"}
)
```

## Repository Structure

```
clawbrain/
├── clawbrain.py      ← Main module
├── __init__.py       ← Exports
├── SKILL.md          ← ClawDBot skill docs
├── skill.json        ← ClawdHub metadata
└── README.md         ← This file
```

## For ClawDBot

Install as a skill via ClawdHub or manually:

```bash
git clone https://github.com/clawcolab/clawbrain.git ClawBrain
```

Usage in your bot:
```python
import sys
sys.path.insert(0, "ClawBrain")
from clawbrain import Brain

brain = Brain()

# Get context for responses
context = brain.get_full_context(
    session_key=session_id,
    user_id=user_id,
    agent_id=agent_id,
    message=user_message
)
```

## License

MIT
