# Human-Like Memory Skill for OpenClaw

Skill providing long-term memory capabilities for OpenClaw, allowing AI assistants to remember past conversations.

[中文文档](README.md)

## Features

- **Memory Recall** - Automatically retrieve relevant historical memories based on current conversation
- **Memory Storage** - Save important conversation content to long-term memory
- **Memory Search** - Explicitly search for memories on specific topics

## Installation

### From ClawHub (Recommended)

```bash
openclaw skill install human-like-memory
```

### Manual Installation

```bash
# Clone repository
git clone https://gitlab.ttyuyin.com/personalization_group/human-like-mem-openclaw-skill.git

# Copy to OpenClaw skills directory
cp -r human-like-mem-openclaw-skill ~/.openclaw/skills/human-like-memory
```

## Configuration

### Option 1: Auto-configuration on Install

When installing via ClawHub, OpenClaw will detect the secrets declared in `skill.json` and display a configuration form.
If you skip the form by mistake, open the skill settings page later and fill in `HUMAN_LIKE_MEM_API_KEY`.

### Option 2: Run Setup Script

```bash
cd ~/.openclaw/skills/human-like-memory
bash scripts/setup.sh
```

### Quick Check After Install

Run the command below to verify whether API Key is configured:

```bash
node ~/.openclaw/skills/human-like-memory/scripts/memory.mjs config
```

If `apiKeyConfigured` is `false`, run:

```bash
bash ~/.openclaw/skills/human-like-memory/scripts/setup.sh
```

### Option 3: Manual Configuration

Edit `~/.openclaw/secrets.json`:

```json
{
  "human-like-memory": {
    "HUMAN_LIKE_MEM_API_KEY": "mp_your_api_key_here",
    "HUMAN_LIKE_MEM_BASE_URL": "https://multiego.me",
    "HUMAN_LIKE_MEM_USER_ID": "your-user-id"
  }
}
```

### Option 4: Environment Variables

```bash
export HUMAN_LIKE_MEM_API_KEY="mp_your_api_key_here"
export HUMAN_LIKE_MEM_BASE_URL="https://multiego.me"
export HUMAN_LIKE_MEM_USER_ID="your-user-id"
```

## Get API Key

1. Visit [https://multiego.me](https://multiego.me)
2. Register and login
3. Create an API Key in the console
4. Copy the key starting with `mp_`

## Configuration Reference

| Config | Required | Default | Description |
|--------|----------|---------|-------------|
| `HUMAN_LIKE_MEM_API_KEY` | Yes | - | API Key |
| `HUMAN_LIKE_MEM_BASE_URL` | No | `https://multiego.me` | API endpoint |
| `HUMAN_LIKE_MEM_USER_ID` | No | `openclaw-user` | User identifier |

## Usage

After installation and configuration, the skill triggers automatically when:

1. You ask "Do you remember what we discussed..."
2. You say "Remember this..."
3. You need to review past conversations

### CLI Testing

```bash
# Check configuration
node ~/.openclaw/skills/human-like-memory/scripts/memory.mjs config

# Recall memories
node ~/.openclaw/skills/human-like-memory/scripts/memory.mjs recall "what projects am I working on"

# Save memory
node ~/.openclaw/skills/human-like-memory/scripts/memory.mjs save "I'm developing a memory plugin" "Got it, I'll remember that"

# Search memories
node ~/.openclaw/skills/human-like-memory/scripts/memory.mjs search "meeting notes"
```

## License

Apache-2.0
