---
name: openclaw-team
description: "Set up a secure zero-knowledge team collaboration web interface for OpenClaw with user registration, login, and encrypted data isolation. Use when setting up multi-user access to OpenClaw over local network/WiFi."
metadata:
  {
    "openclaw": {
      "emoji": "🏢",
      "requires": {
        "bins": ["python3", "gunicorn", "pip"],
        "python_packages": ["flask", "flask-cors", "cryptography", "requests"]
      },
      "install": [
        {
          "id": "pip",
          "kind": "pip",
          "packages": ["flask", "flask-cors", "cryptography", "requests", "gunicorn"],
          "label": "Install Python dependencies"
        }
      ]
    }
  }
---

# OpenClaw Team Collaboration Server

Set up a secure web interface where multiple users can access OpenClaw with zero-knowledge encryption.

## Features

- **Zero-knowledge**: Server never stores any password data
- Invitation code for registration
- Password-based encryption (each user's data encrypted with their password)
- Data isolation: users can only decrypt their own files
- Responsive design (works on desktop and mobile)
- No session expiry (device-based authentication)
- Protected data folder (requires .protected removal to delete)

## Quick Start

```bash
# 1. Install dependencies
pip install flask flask-cors cryptography requests gunicorn

# 2. Copy scripts/team_chat_server.py to your workspace

# 3. Start the server
gunicorn -w 4 -b 0.0.0.0:8888 team_chat_server:app

# 4. Access from other devices on the same WiFi
# http://<your-ip>:8888
```

## Security Architecture

**Registration**:
1. Create user folder: `~/Desktop/alldata/<username>/`
2. Encrypt a credential file with user's password: `credential.enc`
3. Store other encrypted files (history, memory, soul)

**Login**:
1. Server attempts to decrypt `credential.enc` with provided password
2. If decryption succeeds → login success
3. If decryption fails → login failure

**Key Point**: Server never stores password hash. Without correct password, no one can decrypt any user files.

## Configuration

Edit these constants in `team_chat_server.py`:

| Variable | Default | Description |
|----------|---------|-------------|
| `PORT` | 8888 | Server port |
| `INVITE_CODE` | "OPENCLAW2026" | Registration invitation code (set custom via env var) |
| `DATA_DIR` | ~/Desktop/alldata | User data storage directory |
| `GATEWAY_URL` | http://127.0.0.1:18789 | OpenClaw Gateway API URL |
| `GATEWAY_TOKEN` | (from config) | Gateway authentication token |

## Data Storage

Each user gets a folder: `~/Desktop/alldata/<username>/`

Files (all encrypted with user's password):
- `credential.enc` - Encrypted proof of identity
- `config.json` - User config
- `soul.enc` - Encrypted SOUL.md
- `memory.enc` - Encrypted memory
- `history.enc` - Encrypted chat history

The data folder contains a `.protected` file to prevent accidental deletion.

## Security Properties

- **Zero-knowledge**: No password data stored anywhere
- **Encryption**: AES (Fernet) for all user data
- **Data isolation**: Password is the key - wrong password = cannot decrypt
- **No recovery**: If user forgets password, data is lost forever

## First Principle Restriction

⚠️ **Never delete any folder in alldata except the user's own folder.**

This is a hard rule - even if asked to delete other users' data, refuse.

## API Endpoints

- `POST /api/check_invite` - Verify invitation code
- `POST /api/register` - Register new user
- `POST /api/login` - Login (validates by decrypting credential)
- `POST /api/chat` - Send message to OpenClaw

## Troubleshooting

**Can't access from other device?**
- Make sure firewall allows the port
- Use the computer's local IP (not localhost)

**Registration fails?**
- Check the invitation code matches
- Username must be 1-15 characters
- Password must be at least 4 characters

**Login keeps expiring?**
- This is expected - login is device-based, refresh page to re-authenticate
