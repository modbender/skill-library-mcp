# iCloud Toolkit — First-Time Setup

## Prerequisites

Install via brew (not apt):
```bash
brew install vdirsyncer khal himalaya
```

Verify binaries:
```bash
/home/linuxbrew/.linuxbrew/bin/vdirsyncer --version
/home/linuxbrew/.linuxbrew/bin/khal --version
/home/linuxbrew/.linuxbrew/bin/himalaya --version
```

## 1. Create Auth File

Generate an app-specific password at https://appleid.apple.com (Sign-In and Security → App-Specific Passwords).

```bash
echo "your-app-specific-password" > config/auth
chmod 600 config/auth
```

## 2. Configure vdirsyncer

Edit `~/.config/vdirsyncer/config`. The `username` must be your **Apple ID** (iCloud login), which is used for CalDAV authentication:
```ini
[general]
status_path = "~/.local/share/vdirsyncer/status/"

[pair icloud_calendar]
a = "icloud_remote"
b = "icloud_local"
collections = ["from a", "from b"]
conflict_resolution = "a wins"

[storage icloud_remote]
type = "caldav"
url = "https://caldav.icloud.com/"
username = "you@icloud.com"
password.fetch = ["command", "cat", "/full/path/to/config/auth"]

[storage icloud_local]
type = "filesystem"
path = "~/.local/share/vdirsyncer/calendars/"
fileext = ".ics"
```

## 3. Discover Calendars

```bash
/home/linuxbrew/.linuxbrew/bin/vdirsyncer discover
/home/linuxbrew/.linuxbrew/bin/vdirsyncer sync
```

This creates subdirectories in `~/.local/share/vdirsyncer/calendars/` — one per calendar. The directory names are UUIDs or slugs assigned by iCloud.

## 4. Identify Calendar UUIDs

```bash
ls ~/.local/share/vdirsyncer/calendars/
```

To figure out which UUID is which calendar, check iCloud.com or count events:
```bash
python3 scripts/icloud.py setup discover-calendars
```

## 5. Populate config.json

Edit `config/config.json` with your details:
```json
{
  "timezone": "America/New_York",
  "account_email": "you@yourdomain.com",
  "display_name": "Your Name",
  "calendars": {
    "Personal": "uuid-or-slug-from-step-4",
    "Work": "another-uuid-or-slug"
  },
  "default_calendar": "Personal",
  "bins": {
    "himalaya": "/home/linuxbrew/.linuxbrew/bin/himalaya",
    "khal": "/home/linuxbrew/.linuxbrew/bin/khal",
    "vdirsyncer": "/home/linuxbrew/.linuxbrew/bin/vdirsyncer"
  },
  "calendar_base": "~/.local/share/vdirsyncer/calendars",
  "email_addresses": [
    "you@yourdomain.com",
    "you@icloud.com"
  ]
}
```

**account_email:** Your preferred sending address (appears in the From header). This may differ from your Apple ID if you use a custom domain with iCloud.

**email_addresses:** All email addresses associated with your account. Used for reply-matching — when replying, the script checks which of your addresses received the original email and replies from that one.

**timezone:** Your IANA timezone name (e.g. `America/Regina`, `America/New_York`, `Europe/London`). The script uses this to calculate the correct UTC offset automatically, including DST transitions. Find yours at https://en.wikipedia.org/wiki/List_of_tz_database_time_zones

## 6. Configure khal

Edit `~/.config/khal/config`. Add explicit entries for each calendar (do NOT use `type = discover` — it gives UUID-based names):

```ini
[calendars]
[[Personal]]
path = ~/.local/share/vdirsyncer/calendars/your-uuid/
color = dark green

[[Work]]
path = ~/.local/share/vdirsyncer/calendars/work-uuid/
color = dark blue

[default]
default_calendar = Personal
highlight_event_days = True

[locale]
timeformat = %H:%M
dateformat = %Y-%m-%d
longdateformat = %Y-%m-%d
datetimeformat = %Y-%m-%d %H:%M
longdatetimeformat = %Y-%m-%d %H:%M
local_timezone = America/New_York
default_timezone = America/New_York

[view]
theme = dark
```

**local_timezone / default_timezone:** Set these to your IANA timezone so khal displays event times correctly regardless of system timezone.

## 7. Configure himalaya

Edit `~/.config/himalaya/config.toml`.

**Important:** The `email` field is your **sending address** (From header). The `backend.login` fields are your **Apple ID** (iCloud login for authentication). These may be different if you use a custom domain:

```toml
[accounts.icloud]
default = true
email = "you@yourdomain.com"
display-name = "Your Name"

backend.type = "imap"
backend.host = "imap.mail.me.com"
backend.port = 993
backend.encryption.type = "tls"
backend.login = "you@icloud.com"
backend.auth.type = "password"
backend.auth.command = "cat /full/path/to/config/auth"

message.send.backend.type = "smtp"
message.send.backend.host = "smtp.mail.me.com"
message.send.backend.port = 587
message.send.backend.encryption.type = "start-tls"
message.send.backend.login = "you@icloud.com"
message.send.backend.auth.type = "password"
message.send.backend.auth.command = "cat /full/path/to/config/auth"
message.send.save-copy = true
folder.aliases.sent = "Sent Messages"
```

**message.send.save-copy:** Must be `true` (a boolean). Do NOT use `save-copy.folder = "..."` — that crashes himalaya's TOML parser.

**folder.aliases.sent:** iCloud's Sent folder is named "Sent Messages" (with a space), not "Sent".

## 8. Verify

```bash
python3 scripts/icloud.py --test                    # Self-test
python3 scripts/icloud.py calendar list --days 3    # Calendar
python3 scripts/icloud.py email list --count 5      # Email
python3 scripts/icloud.py setup discover-calendars  # Config check
```

## Troubleshooting

**"config not found":** The script looks for `../config/config.json` relative to `scripts/`. Make sure the directory structure is correct.

**vdirsyncer sync fails:** Check the auth file path in `~/.config/vdirsyncer/config` is absolute (no ~).

**khal shows wrong calendar names:** Use explicit `[[CalendarName]]` entries in khal config, not `type = discover`.

**Events show as all-day on iPhone:** You used `khal new` instead of `icloud.py calendar create`. The whole point of this skill is to avoid `khal new` for writes.

**himalaya auth error:** The auth command in `config.toml` must use an absolute path to `config/auth`.

**Stale khal data:** Clear the cache: `rm ~/.local/share/khal/khal.db`
