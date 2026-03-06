# EWS Calendar Skill

Extract calendar events from Microsoft Exchange via EWS API and return them as structured JSON.

## Features

- Fetch calendar events for today, tomorrow, or specific dates
- Returns structured JSON with subject, time, location, organizer, body text, and links
- Secure credential storage using OS keyring (macOS Keychain / Linux libsecret)
- NTLM authentication support
- URL extraction from event bodies and locations

## Prerequisites

- **curl** - HTTP requests
- **xmllint** - XML parsing (part of libxml2)
- **macOS**: Keychain Access (built-in)
- **Linux**: libsecret-tools + gnome-keyring

### Linux Setup

```bash
# Debian/Ubuntu
sudo apt install libsecret-tools gnome-keyring

# Fedora
sudo dnf install libsecret gnome-keyring

# Arch
sudo pacman -S libsecret gnome-keyring
```

## Installation

### 1. Clone the repository

```bash
git clone <repo-url>
cd ews-skill
```

### 2. Store credentials in OS keyring

```bash
./ews-calendar-setup.sh --user "DOMAIN\\username"
```

You will be prompted for your password. This stores it securely in the OS keyring.

### 3. Configure environment

Set environment variables or create a `.env` file:

```bash
EWS_URL=https://outlook.company.com/EWS/Exchange.asmx
EWS_USER=DOMAIN\\username
EWS_EMAIL=user@company.com  # optional, defaults to EWS_USER
```

## Usage

### Basic Commands

```bash
# Get today's events
./ews-calendar-secure.sh --date today

# Get tomorrow's events
./ews-calendar-secure.sh --date tomorrow

# Get events for a specific date
./ews-calendar-secure.sh --date 2026-03-03

# Write output to file
./ews-calendar-secure.sh --date today --output events.json

# Enable verbose logging
./ews-calendar-secure.sh --date today --verbose

# Debug raw XML response
./ews-calendar-secure.sh --date today --debug-xml response.xml
```

### Command Options

| Option | Description |
|--------|-------------|
| `-d, --date DATE` | Filter events by date (YYYY-MM-DD, `today`, or `tomorrow`) |
| `-o, --output FILE` | Write JSON to file instead of stdout |
| `-v, --verbose` | Enable debug logging |
| `--debug-xml FILE` | Save raw XML response for debugging |
| `-h, --help` | Show help message |

## Output Format

Returns a JSON array of calendar events:

```json
[
  {
    "subject": "Team Standup",
    "start": "2026-03-03T10:00:00Z",
    "end": "2026-03-03T10:30:00Z",
    "location": "Conference Room A",
    "organizer": "manager@company.com",
    "body": "Weekly sync meeting to discuss sprint progress...",
    "links": ["https://zoom.us/j/12345", "https://confluence.example.com/doc"]
  }
]
```

Returns empty array `[]` if no events found.

## Security Model

Credentials are stored in OS keyring, **not** in config files:

- **macOS**: Keychain Access (encrypted, OS-managed)
- **Linux**: libsecret / gnome-keyring (encrypted, OS-managed)

Only `EWS_URL` and `EWS_USER` are stored in environment/config (non-secret). The password is retrieved securely at runtime.

## Credential Management

### Update password (after password change)

```bash
./ews-calendar-setup.sh --user "DOMAIN\\username"
```

### Remove credentials

```bash
./ews-calendar-setup.sh --user "DOMAIN\\username" --delete
```

Or manually:

**macOS:**
```bash
security delete-generic-password -a "DOMAIN\\username" -s "ews-calendar"
```

**Linux:**
```bash
secret-tool clear service "ews-calendar" user "DOMAIN\\username"
```

### View stored credentials (macOS only)

```bash
security find-generic-password -a "DOMAIN\\username" -s "ews-calendar" -w
```

## Troubleshooting

### Password not found in keyring

```
[ERROR] Password not found in keyring for user: DOMAIN\username
[HINT] Run: ./ews-calendar-setup.sh to store credentials
```

**Solution:** Run the setup script:
```bash
./ews-calendar-setup.sh --user "DOMAIN\\username"
```

### Linux: secret-tool not found

```
[ERROR] 'secret-tool' not found. Install: apt install libsecret-tools
```

**Solution:**
```bash
sudo apt install libsecret-tools gnome-keyring
```

### Linux: Keyring locked

On Linux, the keyring may be locked after login. Unlock your keyring (usually happens automatically on desktop login). For headless servers, you may need to set up a keyring daemon.

### HTTP request failed (401)

**Possible causes:**
- Incorrect username or password
- Password changed — re-run setup script
- Account locked or expired

### SOAP Fault

**Possible causes:**
- Invalid EWS URL (check `EWS_URL`)
- Date format issue (use `YYYY-MM-DD`)
- Exchange server configuration issue

## Project Structure

```
ews-skill/
├── SKILL.md                 # OpenClaw skill definition
├── ews-calendar.sh          # Main script
├── ews-calendar-secure.sh   # Wrapper that gets password from keyring
├── ews-calendar-setup.sh    # Store credentials in keyring
├── templates/
│   ├── find-items.xml       # SOAP template for finding calendar items
│   └── get-item.xml         # SOAP template for getting item details
└── README.md                # This file
```

## Alternative: Standalone Usage (without keyring)

For development or testing, you can run `ews-calendar.sh` directly with environment variables:

```bash
export EWS_URL="https://outlook.company.com/EWS/Exchange.asmx"
export EWS_USER="DOMAIN\\username"
export EWS_PASS="your_password"
./ews-calendar.sh --date today
```

Or create a `.env` file and source it:

```bash
source .env
./ews-calendar.sh --date today
```

> **Warning:** This stores password in plaintext. Use keyring for production.

## License

MIT
