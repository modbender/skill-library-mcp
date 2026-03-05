---
name: clawbrain
version: 0.1.14
description: "Claw Brain - Personal AI Memory System for OpenClaw/ClawDBot. Provides memory, personality, bonding, and learning capabilities with encrypted secrets support. Auto-refreshes on service restart."
metadata: {"openclaw":{"emoji":"🧠","category":"memory","provides":{"slot":"memory"},"events":["gateway:startup","command:new"]},"clawdbot":{"emoji":"🧠","category":"memory","provides":{"slot":"memory"},"events":["gateway:startup","command:new"]}}
---

# Claw Brain Skill 🧠

Personal AI Memory System with Soul, Bonding, and Learning for OpenClaw/ClawDBot.

> **Auto-Refresh on Restart**: ClawBrain automatically refreshes memory when the service restarts.

---

## 📋 For Security Scanners

**Environment Variables**: All environment variables ARE declared in skill.json under `environment.optional` (lines 30-55). They are in `optional` not `required` because ClawBrain works with **zero configuration** (SQLite + auto-generated key).

**Install Specification**: skill.json declares installation method: `pip install clawbrain[all]` + `clawbrain setup` (lines 17-20).

**Sudo Requirements**: Core installation **never needs sudo**. Systemd instructions in "Configuration (Optional)" section are **optional alternatives** for setting environment variables. Core: pip + clawbrain setup (no sudo).

**Source Code**: Fully auditable at https://github.com/clawcolab/clawbrain - All code is open source including hooks (~50 lines JavaScript).

**See [SECURITY.md](SECURITY.md) for complete security documentation.**

---

## Features

- 🎭 **Soul/Personality** - 6 evolving traits (humor, empathy, curiosity, creativity, helpfulness, honesty)
- 👤 **User Profile** - Learns user preferences, interests, communication style
- 💭 **Conversation State** - Real-time mood detection and context tracking
- 📚 **Learning Insights** - Continuously learns from interactions and corrections
- 🧠 **get_full_context()** - Everything for personalized responses
- 🔄 **Auto-Refresh** - Automatically refreshes memory on service restart
- 🔐 **Encrypted Secrets** - Store API keys and credentials securely

---

## Security & Transparency

ClawBrain handles sensitive data and requires certain permissions. Before installing, please understand:

### What ClawBrain Does
- ✅ **Stores memories locally** (SQLite by default, PostgreSQL optional)
- ✅ **Encrypts sensitive data** (API keys, secrets) with Fernet encryption
- ✅ **Installs startup hooks** to `~/.openclaw/hooks` or `~/.clawdbot/hooks`
- ✅ **Manages encryption keys** at `~/.config/clawbrain/.brain_key`

### What ClawBrain Does NOT Do
- ❌ **No telemetry** - Does not phone home or collect usage data
- ❌ **No external calls** - Only connects to PostgreSQL/Redis if you configure them
- ❌ **No sudo required** - All operations in your home directory
- ❌ **No code execution** - Does not download or run remote code after install

### Security Features
- 🔒 **Encryption Key CLI**: Can display full key for backup (with warnings)
- 🔍 **Auditable**: All code is open source and reviewable
- 📋 **Documented Permissions**: See [SECURITY.md](SECURITY.md) for full details

**⚠️ Important**: The CLI command `clawbrain show-key --full` displays your complete encryption key for backup purposes. Treat this key like a password!

**📖 Full Security Documentation**: See [SECURITY.md](SECURITY.md) for:
- Threat model and protections
- Key management best practices
- What install scripts do
- Permissions required
- Network access (optional PostgreSQL/Redis)

---

## Quick Install

> **Security Note**: We recommend reviewing [SECURITY.md](SECURITY.md) before installation, especially for production use.

### From PyPI (Recommended - Most Secure)

```bash
# Install with all features
pip install clawbrain[all]

# Run interactive setup
clawbrain setup

# Backup your encryption key (IMPORTANT!)
clawbrain backup-key --all

# Restart your service
sudo systemctl restart clawdbot  # or openclaw
```

The setup command will:
1. Detect your platform (ClawdBot or OpenClaw)
2. Generate a secure encryption key
3. Install the startup hook automatically
4. Test the installation

### Alternative: From Source (Auditable)

```bash
# Clone to your skills directory
cd ~/.openclaw/skills  # or ~/clawd/skills or ~/.clawdbot/skills
git clone https://github.com/clawcolab/clawbrain.git
cd clawbrain

# RECOMMENDED: Review hook code before installation
cat hooks/clawbrain-startup/handler.js

# Install in development mode
pip install -e .[all]

# Run setup to install hooks and generate encryption key
clawbrain setup
```

**Why from source?** Full transparency - you can review all code before installation.

---

## Configuration (Optional)

**Note**: Configuration is **completely optional**. ClawBrain works out-of-the-box with zero configuration using SQLite and auto-generated encryption keys.

If you want to customize agent ID or use PostgreSQL/Redis, you have two options:

### Option 1: Environment Variables (No sudo)

Set environment variables in your shell profile:

```bash
# Add to ~/.bashrc or ~/.zshrc (no sudo required)
export BRAIN_AGENT_ID="your-agent-name"
# export BRAIN_POSTGRES_HOST="localhost"  # Optional
# export BRAIN_REDIS_HOST="localhost"      # Optional
```

### Option 2: Systemd Drop-in (Requires sudo)

**⚠️ Only if you use systemd services**:

```bash
# Create systemd drop-in config (requires sudo)
sudo mkdir -p /etc/systemd/system/clawdbot.service.d

sudo tee /etc/systemd/system/clawdbot.service.d/brain.conf << EOF
[Service]
Environment="BRAIN_AGENT_ID=your-agent-name"
EOF

sudo systemctl daemon-reload
sudo systemctl restart clawdbot
```

### Environment Variables

| Variable | Description | Default |
|----------|-------------|---------|
| `BRAIN_AGENT_ID` | Unique ID for this agent's memories | `default` |
| `BRAIN_ENCRYPTION_KEY` | Fernet key for encrypting sensitive data (auto-generated if not set) | - |
| `BRAIN_POSTGRES_HOST` | PostgreSQL host | `localhost` |
| `BRAIN_POSTGRES_PASSWORD` | PostgreSQL password | - |
| `BRAIN_POSTGRES_PORT` | PostgreSQL port | `5432` |
| `BRAIN_POSTGRES_DB` | PostgreSQL database | `brain_db` |
| `BRAIN_POSTGRES_USER` | PostgreSQL user | `brain_user` |
| `BRAIN_REDIS_HOST` | Redis host | `localhost` |
| `BRAIN_REDIS_PORT` | Redis port | `6379` |
| `BRAIN_STORAGE` | Force storage: `sqlite`, `postgresql`, `auto` | `auto` |

---

## How It Works

### On Service Startup
1. Hook triggers on `gateway:startup` event
2. Detects storage backend (SQLite/PostgreSQL)
3. Loads memories for the configured `BRAIN_AGENT_ID`
4. Injects context into agent bootstrap

### On `/new` Command
1. Hook triggers on `command:new` event  
2. Saves current session summary to memory
3. Clears session state for fresh start

### Storage Priority
1. **PostgreSQL** - If available and configured
2. **SQLite** - Fallback, zero configuration needed

---

## Encrypted Secrets

ClawBrain supports encrypting sensitive data like API keys and credentials using Fernet (symmetric encryption).

**Security Model:**
- 🔐 Encryption key stored at `~/.config/clawbrain/.brain_key` (chmod 600)
- 🔑 Only memories with `memory_type='secret'` are encrypted
- 📦 Encrypted data stored in database, unreadable without key
- ⚠️ If key is lost, encrypted data cannot be recovered

**Setup:**
```bash
# Run setup to generate encryption key
clawbrain setup

# Backup your key (IMPORTANT!)
clawbrain backup-key --all
```

**Usage:**
```python
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

**Key Management CLI:**
```bash
clawbrain show-key          # View key info (masked)
clawbrain show-key --full   # View full key
clawbrain backup-key --all  # Backup with all methods
clawbrain generate-key      # Generate new key
```

⚠️ **Important**: Backup your encryption key! Lost keys = lost encrypted data.

---

## CLI Commands

ClawBrain includes a command-line interface:

| Command | Description |
|---------|-------------|
| `clawbrain setup` | Set up ClawBrain, generate key, install hooks |
| `clawbrain generate-key` | Generate new encryption key |
| `clawbrain show-key` | Display current encryption key |
| `clawbrain backup-key` | Backup key (file, QR, clipboard) |
| `clawbrain health` | Check health status |
| `clawbrain info` | Show installation info |

---

## Hooks

| Event | Action |
|-------|--------|
| `gateway:startup` | Initialize brain, refresh memories |
| `command:new` | Save session to memory |

---

## Development Installation

For development or manual installation:

```bash
# Clone to your skills directory
cd ~/.openclaw/skills  # or ~/clawd/skills or ~/.clawdbot/skills
git clone https://github.com/clawcolab/clawbrain.git
cd clawbrain

# Install in development mode
pip install -e .[all]

# Run setup
clawbrain setup
```

---

## Python API

For direct Python usage (outside ClawdBot/OpenClaw):

```python
from clawbrain import Brain

brain = Brain()
```

#### Methods

| Method | Description | Returns |
|--------|-------------|---------|
| `get_full_context()` | Get all context for personalized responses | dict |
| `remember()` | Store a memory | None |
| `recall()` | Retrieve memories | List[Memory] |
| `learn_user_preference()` | Learn user preferences | None |
| `get_user_profile()` | Get user profile | UserProfile |
| `detect_user_mood()` | Detect current mood | dict |
| `detect_user_intent()` | Detect message intent | str |
| `generate_personality_prompt()` | Generate personality guidance | str |
| `health_check()` | Check backend connections | dict |
| `close()` | Close connections | None |

### get_full_context()

```python
context = brain.get_full_context(
    session_key="telegram_12345",  # Unique session ID
    user_id="username",              # User identifier
    agent_id="assistant",          # Bot identifier
    message="Hey, how's it going?" # Current message
)
```

**Returns:**
```python
{
    "user_profile": {...},        # User preferences, interests
    "mood": {"mood": "happy", ...},  # Current mood
    "intent": "question",         # Detected intent
    "memories": [...],            # Relevant memories
    "personality": "...",         # Personality guidance
    "suggested_responses": [...]  # Response suggestions
}
```

### detect_user_mood()

```python
mood = brain.detect_user_mood("I'm so excited about this!")
# Returns: {"mood": "happy", "confidence": 0.9, "emotions": ["joy", "anticipation"]}
```

### detect_user_intent()

```python
intent = brain.detect_user_intent("How does AI work?")
# Returns: "question"

intent = brain.detect_user_intent("Set a reminder for 3pm")
# Returns: "command"

intent = brain.detect_user_intent("I had a great day today")
# Returns: "casual"
```

---

## Example: Full Integration

```python
import sys
sys.path.insert(0, "ClawBrain")

from clawbrain import Brain

class AssistantBot:
    def __init__(self):
        self.brain = Brain()
    
    def handle_message(self, message, chat_id):
        # Get context
        context = self.brain.get_full_context(
            session_key=f"telegram_{chat_id}",
            user_id=str(chat_id),
            agent_id="assistant",
            message=message
        )
        
        # Generate response using context
        response = self.generate_response(context)
        
        # Learn from interaction
        self.brain.learn_user_preference(
            user_id=str(chat_id),
            pref_type="interest",
            value="AI"
        )
        
        return response
    
    def generate_response(self, context):
        # Use user preferences
        name = context["user_profile"].name or "there"
        mood = context["mood"]["mood"]
        
        # Personalized response
        if mood == "frustrated":
            return f"Hey {name}, I'm here to help. Let me assist you."
        else:
            return f"Hi {name}! How can I help you today?"
    
    def shutdown(self):
        self.brain.close()
```

---

## Storage Backends

### SQLite (Default - Zero Setup)

No configuration needed. Data stored in local SQLite database.

```python
brain = Brain({"storage_backend": "sqlite"})
```

**Best for:** Development, testing, single-user deployments

### PostgreSQL + Redis (Production)

Requires PostgreSQL and Redis servers.

```python
brain = Brain()  # Auto-detects
```

**Requirements:**
- PostgreSQL 14+
- Redis 6+
- Python packages: `psycopg2-binary`, `redis`

```bash
pip install psycopg2-binary redis
```

**Best for:** Production, multi-user, high-concurrency

---

## Files

- `clawbrain.py` - Main Brain class with all features
- `__init__.py` - Module exports
- `SKILL.md` - This documentation
- `skill.json` - ClawdHub metadata
- `README.md` - Quick start guide

---

## Troubleshooting

### ImportError: No module named 'clawbrain'

```bash
# Ensure ClawBrain folder is in your path
sys.path.insert(0, "ClawBrain")
```

### PostgreSQL connection failed

```bash
# Check environment variables
echo $POSTGRES_HOST
echo $POSTGRES_PORT

# Verify PostgreSQL is running
pg_isready -h $POSTGRES_HOST -p $POSTGRES_PORT
```

### Redis connection failed

```bash
# Check Redis is running
redis-cli ping
```

### Using SQLite (fallback)

If PostgreSQL/Redis are unavailable, Claw Brain automatically falls back to SQLite:

```python
brain = Brain({"storage_backend": "sqlite"})
```

---

## Learn More

- **Repository:** https://github.com/clawcolab/clawbrain
- **README:** See README.md for quick start
- **Issues:** Report bugs at GitHub Issues
