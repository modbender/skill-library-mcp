---
name: ews-calendar
description: Extract calendar events from Microsoft Exchange via EWS API
user-invocable: true
metadata:
  {
    "openclaw":
      {
        "emoji": "📅",
        "requires":
          {
            "bins": ["curl", "xmllint"],
            "env": ["EWS_URL", "EWS_USER"],
            "anyBins": ["security", "secret-tool"]
          }
      }
  }
---

## Purpose

Fetch calendar events from Microsoft Exchange Web Services (EWS) and return them as structured JSON.

## When to Use

- User asks about their calendar events ("What's on my calendar today?")
- Need to retrieve meetings for today, tomorrow, or a specific date
- Extracting meeting details: subject, time, location, organizer, body text, links

## Security Model

**Credentials are stored in OS keyring, NOT in config files:**

- **macOS**: Keychain Access (encrypted, OS-managed)
- **Linux**: libsecret / gnome-keyring (encrypted, OS-managed)

Only `EWS_URL` and `EWS_USER` are stored in OpenClaw config (non-secret). The password is retrieved securely at runtime.

## Setup

### 1. Install keyring tools (Linux only)

```bash
# Debian/Ubuntu
sudo apt install libsecret-tools gnome-keyring

# Fedora
sudo dnf install libsecret gnome-keyring

# Arch
sudo pacman -S libsecret gnome-keyring
```

macOS has Keychain built-in.

### 2. Store credentials in keyring

```bash
{baseDir}/ews-calendar-setup.sh --user "DOMAIN\\username"
```

You will be prompted for your password. This stores it securely in the OS keyring.

### 3. Configure OpenClaw

Add to `~/.openclaw/openclaw.json`:

```json5
{
  skills: {
    entries: {
      "ews-calendar": {
        enabled: true,
        env: {
          EWS_URL: "https://outlook.company.com/EWS/Exchange.asmx",
          EWS_USER: "DOMAIN\\username"
        }
      }
    }
  }
}
```

Replace with your actual Exchange URL and username.

## Usage

The skill runs `{baseDir}/ews-calendar-secure.sh` which:

1. Retrieves `EWS_PASS` from OS keyring
2. Calls the main script with all credentials in environment
3. Returns JSON output

### Command Syntax

```bash
{baseDir}/ews-calendar-secure.sh --date <DATE> [--output <FILE>] [--verbose]
```

### Parameters

- `--date` (required): Date filter
  - `YYYY-MM-DD` — specific date (e.g., `2026-03-03`)
  - `today` — today's date
  - `tomorrow` — tomorrow's date
- `--output <FILE>`: Write JSON to file instead of stdout
- `--verbose`: Enable debug logging
- `--debug-xml <FILE>`: Save raw XML response for debugging

### Output Format

Returns JSON array of calendar events:

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

## Example Invocations

**Get today's events:**
```bash
{baseDir}/ews-calendar-secure.sh --date today
```

**Get tomorrow's events to file:**
```bash
{baseDir}/ews-calendar-secure.sh --date tomorrow --output /tmp/tomorrow.json
```

**Get specific date with debug:**
```bash
{baseDir}/ews-calendar-secure.sh --date 2026-03-03 --verbose --debug-xml /tmp/debug.xml
```

## Troubleshooting

### Password not found in keyring

```
[ERROR] Password not found in keyring for user: DOMAIN\username
[HINT] Run: ./ews-calendar-setup.sh to store credentials
```

**Solution:** Run the setup script to store your password:
```bash
{baseDir}/ews-calendar-setup.sh --user "DOMAIN\\username"
```

### Linux: secret-tool not found

```
[ERROR] 'secret-tool' not found. Install: apt install libsecret-tools
```

**Solution:** Install libsecret tools:
```bash
sudo apt install libsecret-tools gnome-keyring
```

### Linux: Keyring locked

On Linux, the keyring may be locked after login.

**Solution:** Unlock your keyring (usually happens automatically on desktop login). For headless servers, you may need to set up a keyring daemon.

### HTTP request failed

```
[ERROR] HTTP request failed with status: 401
```

**Possible causes:**
- Incorrect username or password
- Password changed — re-run setup script
- Account locked or expired

### SOAP Fault

```
[ERROR] SOAP Fault detected
Fault code: a:ErrorInvalidRequest
Fault string: The request is invalid.
```

**Possible causes:**
- Invalid EWS URL (check `EWS_URL` in config)
- Date format issue (use `YYYY-MM-DD`)
- Exchange server configuration issue

## Credential Management

### Update password (after password change)

```bash
{baseDir}/ews-calendar-setup.sh --user "DOMAIN\\username"
```

The script will overwrite the existing entry.

### Remove credentials

```bash
{baseDir}/ews-calendar-setup.sh --user "DOMAIN\\username" --delete
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

## Files in This Skill

```
{baseDir}/
├── SKILL.md                 # This file
├── ews-calendar.sh          # Main script (reads from env or .env)
├── ews-calendar-secure.sh   # Wrapper that gets password from keyring
├── ews-calendar-setup.sh    # Store credentials in keyring
├── templates/
│   ├── find-items.xml       # SOAP template for finding calendar items
│   └── get-item.xml         # SOAP template for getting item details
└── .env.example             # Example config for standalone usage
```

## Alternative: Standalone Usage (without keyring)

For development or testing, you can run `ews-calendar.sh` directly with a `.env` file:

1. Copy `.env.example` to `.env`
2. Fill in your credentials
3. Run: `./ews-calendar.sh --date today`

**Warning:** This stores password in plaintext. Use keyring for production.
