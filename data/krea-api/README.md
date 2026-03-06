# Krea.ai API Skill

See [SKILL.md](./SKILL.md) for full documentation.

## Quick Start

```bash
# Generate an image (uses credentials from ~/.openclaw/credentials/krea.json)
python3 krea_api.py --prompt "A cute crab at a desk" --model flux

# List available models
python3 krea_api.py --list-models
```

## Configure Credentials

Create the credentials file:
```bash
mkdir -p ~/.openclaw/credentials
echo '{"apiKey": "YOUR_KEY_ID:YOUR_SECRET"}' > ~/.openclaw/credentials/krea.json
chmod 600 ~/.openclaw/credentials/krea.json
```

Or pass directly via CLI:
```bash
python3 krea_api.py --prompt "..." --key-id YOUR_KEY_ID --secret YOUR_SECRET
```

## Publish to ClawHub

```bash
# Login once
clawdhub login

# Publish this skill folder
clawdhub publish . --slug krea-api --name "Krea.ai API"
```

## Requirements

- Python 3.7+
- No external dependencies (uses stdlib)
