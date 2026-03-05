# Keys Setup

## Requirements

- **macOS** or **Linux with desktop** (GNOME/KDE with keyring)
- curl, jq, bash 4.0+
- NOT supported: Docker, WSL, headless servers

## Install

```bash
# Copy to PATH
cp keys-broker.sh ~/.local/bin/keys-broker
chmod +x ~/.local/bin/keys-broker

# Ensure ~/.local/bin is in PATH
echo 'export PATH="$HOME/.local/bin:$PATH"' >> ~/.bashrc
source ~/.bashrc
```

## Verify

```bash
# Check dependencies
keys-broker ping
# {"ok":true,"status":"running"}

# List configured services
keys-broker services
# {"ok":true,"services":["openai","anthropic","stripe","github"]}
```

## How It Works

```
Agent                        Keys Broker
  │                              │
  │ {"call": "openai", ...}      │
  ├─────────────────────────────►│
  │                              │ ← validates URL against allowlist
  │                              │ ← reads key from OS keychain
  │                              │ ← makes HTTPS request
  │      {response data}         │
  │◄─────────────────────────────┤
  │                              │
  (agent never sees the key)
```

## Security Features

- **URL allowlisting**: Keys can ONLY be sent to their designated APIs
- **Keys hidden from process list**: Uses temp files for auth headers
- **Input validation**: Service names, methods, URLs all validated
- **No key exposure**: Agent never sees decrypted keys
