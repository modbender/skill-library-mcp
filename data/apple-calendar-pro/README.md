# apple-calendar-pro

Manage Apple Calendar from macOS and Linux (and Windows with env/keyring auth).

Connects to iCloud Calendar over CalDAV (RFC 4791) with iPhone-compatible attachment support (RFC 8607).

---

## Requirements

- An iCloud account with Calendar enabled
- Python 3.9+
- The `requests` library
- Optional: `keyring` for secure credential lookup on Linux/Windows/macOS

---

## Setup

### 1. Install the dependency
```bash
pip3 install requests
# optional (recommended off-macOS):
pip3 install keyring
```

### 2. Generate an app-specific password
Sign in at [appleid.apple.com](https://appleid.apple.com) → **Sign-In and Security** → **App-Specific Passwords** → Generate one for this skill.

### 3. Configure authentication

**Option A — Environment variable** *(macOS, Linux, CI)*
```bash
export APPLECAL_PASSWORD="your-app-specific-password"
```
Add to your shell profile (`.zshrc`, `.bashrc`, etc.) to persist across sessions.

**Option B — Python keyring** *(Linux/Windows/macOS)*
```bash
python3 - <<'PY'
import keyring
keyring.set_password('caldav.icloud.com', 'your@icloud.com', 'your-app-specific-password')
print('saved')
PY
```
Used automatically when `APPLECAL_PASSWORD` is not set and keyring is available.

**Option C — macOS Keychain** *(macOS only)*
```bash
security add-internet-password \
  -s "caldav.icloud.com" \
  -a "your@icloud.com" \
  -w "your-app-specific-password"
```
Used automatically on macOS when `APPLECAL_PASSWORD` is not set.

### 4. Verify your connection
```bash
python3 scripts/applecal.py --apple-id your@icloud.com doctor
```
If it fails, double-check your Apple ID and app-specific password.

---

## Usage

> Replace `your@icloud.com` with your iCloud account email in all commands.

### List calendars
```bash
python3 scripts/applecal.py --apple-id your@icloud.com calendars list
```

### List events
```bash
python3 scripts/applecal.py --apple-id your@icloud.com events list \
  --calendar Family \
  --from "2026-03-01T00:00:00Z" \
  --to "2026-03-07T23:59:59Z"
```

Query multiple calendars at once:
```bash
python3 scripts/applecal.py --apple-id your@icloud.com events list \
  --calendar Family \
  --calendar Work \
  --from "2026-03-01T00:00:00Z" \
  --to "2026-03-07T23:59:59Z"
```

### Create an event
```bash
python3 scripts/applecal.py --apple-id your@icloud.com events create \
  --calendar Family \
  --summary "Team Meeting" \
  --start "2026-03-05T09:00:00" \
  --end "2026-03-05T10:00:00" \
  --location "Conference Room A" \
  --description "Quarterly review"
```

### Create an all-day event
```bash
python3 scripts/applecal.py --apple-id your@icloud.com events create \
  --calendar Family \
  --summary "Public Holiday" \
  --start "2026-03-05" \
  --end "2026-03-05" \
  --all-day
```

### Update an event
```bash
python3 scripts/applecal.py --apple-id your@icloud.com events update \
  --calendar Family \
  --uid "YOUR-EVENT-UID" \
  --summary "Updated Title" \
  --location "New Location"
```

Clear optional fields explicitly:
```bash
python3 scripts/applecal.py --apple-id your@icloud.com events update \
  --calendar Family \
  --uid "YOUR-EVENT-UID" \
  --clear-location \
  --clear-description
```

### Delete an event
```bash
python3 scripts/applecal.py --apple-id your@icloud.com events delete \
  --calendar Family \
  --uid "YOUR-EVENT-UID"
```

### Attach a file
Files are uploaded via RFC 8607 managed attachments and visible natively on iPhone and iPad.
```bash
python3 scripts/applecal.py --apple-id your@icloud.com attach add \
  --calendar Family \
  --uid "YOUR-EVENT-UID" \
  --file /path/to/document.pdf
```

### Remove an attachment
```bash
python3 scripts/applecal.py --apple-id your@icloud.com attach remove \
  --calendar Family \
  --uid "YOUR-EVENT-UID" \
  --managed-id "MANAGED-ATTACHMENT-ID"
```

### Check availability
```bash
python3 scripts/applecal.py --apple-id your@icloud.com freebusy \
  --calendar Family \
  --from "2026-03-05T00:00:00Z" \
  --to "2026-03-05T23:59:59Z"
```

---

## Output

All commands return JSON. Use `--json-indent 2` for pretty-printing:
```bash
python3 scripts/applecal.py --apple-id your@icloud.com --json-indent 2 events list \
  --calendar Family \
  --from "2026-03-01T00:00:00Z" \
  --to "2026-03-07T23:59:59Z"
```

---

## Notes

- **Birthdays calendar:** Not accessible via CalDAV. Add birthdays as recurring events in a regular calendar for agent visibility.
- **Free/busy:** Uses CalDAV freebusy where supported; falls back to event-derived calculation if the server returns 400/403.
- **Event updates:** `events update` now patches only mutable VEVENT fields (`DTSTART/DTEND/DTSTAMP/SUMMARY/LOCATION/DESCRIPTION`) and preserves recurrence, alarms, attachments, and other existing properties.
- **Clear semantics:** Use `--clear-location` / `--clear-description` to remove those fields; these flags are mutually exclusive with `--location` / `--description`.
- **Apple ID:** Your iCloud login email — could be `yourname@icloud.com` or another address linked to your Apple account.
- **Attachment security:** `attach add` enforces extension allowlisting, sensitive-path blocking, and optional directory scoping via `APPLECAL_ATTACH_DIR`.

---

## License

MIT
