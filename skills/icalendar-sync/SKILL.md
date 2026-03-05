# iCloud Calendar Sync Skill

Synchronizes calendar events between local system and iCloud.

## ⚠️ Security Requirements

**CRITICAL - Read before installation:**

### 1. Use App-Specific Password ONLY

- Generate at https://appleid.apple.com/account/security
- **NEVER use your main Apple ID password**
- Can be revoked anytime if compromised

### 2. Use OS Keyring for Credential Storage

The skill stores credentials securely in your operating system's keyring:
- **macOS**: Keychain
- **Windows**: Credential Manager
- **Linux**: Secret Service API

### 3. For Headless/Automated Environments

For Docker, CI/CD, or headless servers where interactive input is not possible:

**Option A: Environment Variables** (standard, secure method)
```bash
# Set credentials as environment variables
export ICLOUD_USERNAME="user@icloud.com"
export ICLOUD_APP_PASSWORD="xxxx-xxxx-xxxx-xxxx"

# Run setup
python -m icalendar_sync setup --non-interactive
```

**Option B: Docker/Kubernetes Secrets** (most secure for containers)
```bash
# Docker secrets
docker run --secret icloud_username --secret icloud_password ...

# Kubernetes secrets
kubectl create secret generic icloud-credentials \
  --from-literal=username=user@icloud.com \
  --from-literal=password=xxxx-xxxx-xxxx-xxxx
```

Credentials are read in this order:
1. OS keyring (if available and configured)
2. Environment variables (if keyring unavailable)
3. Interactive prompt (if neither available)

## Installation

```bash
./install.sh
```

## Usage

### Setup Credentials (Interactive)

```bash
# Interactive mode - password prompted securely
python -m icalendar_sync setup --username user@icloud.com
```

The password will be prompted interactively and stored in OS keyring.

### List Calendars

```bash
python -m icalendar_sync list
```

### Get Calendar Events

```bash
python -m icalendar_sync get --calendar "Personal" --days 7
```

### Create Event

```bash
python -m icalendar_sync create \
  --calendar "Personal" \
  --json '{
    "summary": "Meeting",
    "dtstart": "2026-02-15T14:00:00+03:00",
    "dtend": "2026-02-15T15:00:00+03:00"
  }'
```

### Update Event

**Update simple event:**
```bash
python -m icalendar_sync update \
  --calendar "Personal" \
  --uid "event-uid-here" \
  --json '{"summary": "Updated Meeting Title"}'
```

**Update single instance of recurring event:**
```bash
python -m icalendar_sync update \
  --calendar "Work" \
  --uid "recurring-event-uid" \
  --recurrence-id "2026-02-20T09:00:00+03:00" \
  --mode single \
  --json '{"dtstart": "2026-02-21T09:00:00+03:00"}'
```

**Update all instances:**
```bash
python -m icalendar_sync update \
  --calendar "Work" \
  --uid "recurring-event-uid" \
  --mode all \
  --json '{"summary": "New Title for All Instances"}'
```

**Update this and future instances:**
```bash
python -m icalendar_sync update \
  --calendar "Work" \
  --uid "recurring-event-uid" \
  --recurrence-id "2026-03-01T09:00:00+03:00" \
  --mode future \
  --json '{"dtstart": "2026-03-01T14:00:00+03:00"}'
```

### Delete Event

```bash
python -m icalendar_sync delete --calendar "Personal" --uid "event-uid-here"
```

## Requirements

- Python 3.9+
- iCloud app-specific password
- Access to iCloud CalDAV server (caldav.icloud.com:443)

## Security Features

- ✅ OS keyring integration for credential storage
- ✅ App-specific password requirement (not main password)
- ✅ SSL/TLS verification enforced
- ✅ Rate limiting (10 calls per 60 seconds)
- ✅ Automatic credential redaction in logs
- ✅ Input validation on all user inputs

## License

MIT
