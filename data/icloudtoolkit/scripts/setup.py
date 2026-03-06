"""setup.py — Setup commands for iCloud Toolkit."""

import base64
import getpass
import json
import os
import shutil
import stat
import subprocess
import sys
import xml.etree.ElementTree as ET
from datetime import datetime, timezone
from pathlib import Path
from urllib.request import Request, urlopen
from urllib.error import HTTPError, URLError


REQUIRED_BINS = ["vdirsyncer", "khal", "himalaya", "khard"]

KHAL_COLORS = ["dark green", "dark blue", "dark red", "dark magenta", "dark cyan",
               "light green", "light blue", "light red", "brown", "white"]


# --- Helpers ---

def validate_dir_id(dir_id, label="directory ID"):
    """Reject dir_ids that could cause path traversal.

    dir_ids come from CalDAV PROPFIND (trusted) or from --calendars /
    --addressbooks JSON (agent-provided).  They should be bare directory
    names (UUIDs, slugs) — never paths.  Reject anything with path
    separators or parent-directory references.
    """
    if not dir_id or ".." in dir_id or "/" in dir_id or "\\" in dir_id:
        raise ValueError(
            f"Invalid {label}: {dir_id!r} — must be a plain directory name, "
            f"not a path (no '..', '/', or '\\\\')")
    return dir_id


def _print_step(number, title):
    print(f"\n{'='*60}")
    print(f"  Step {number}: {title}")
    print(f"{'='*60}\n")


def _backup_if_exists(path):
    """Back up a file with .bak suffix before overwriting."""
    if path.exists():
        backup = path.with_suffix(path.suffix + ".bak")
        shutil.copy2(path, backup)
        print(f"  Backed up existing file to {backup}")
        return True
    return False


def detect_binary_paths():
    """Find vdirsyncer, khal, and himalaya on $PATH. Exits if any missing."""
    bins = {}
    missing = []

    for name in REQUIRED_BINS:
        path = shutil.which(name)
        if path:
            bins[name] = path
        else:
            missing.append(name)

    if missing:
        print(f"Error: Required binaries not found: {', '.join(missing)}", file=sys.stderr)
        print("Install them with: brew install " + " ".join(missing), file=sys.stderr)
        sys.exit(1)

    return bins


def detect_timezone():
    """Try to auto-detect the system's IANA timezone name."""
    # /etc/timezone (Debian/Ubuntu)
    tz_file = Path("/etc/timezone")
    if tz_file.exists():
        tz = tz_file.read_text().strip()
        if "/" in tz:
            return tz

    # /etc/localtime symlink
    localtime = Path("/etc/localtime")
    if localtime.is_symlink():
        target = str(localtime.resolve())
        if "zoneinfo/" in target:
            return target.split("zoneinfo/", 1)[1]

    # Python fallback
    try:
        local_tz = datetime.now().astimezone().tzinfo
        tz_name = str(local_tz)
        if "/" in tz_name:
            return tz_name
    except Exception:
        pass

    return None


def write_auth_file(auth_path, password):
    """Write password to config/auth with 600 permissions."""
    auth_path.parent.mkdir(parents=True, exist_ok=True)
    _backup_if_exists(auth_path)
    auth_path.write_text(password + "\n")
    os.chmod(auth_path, stat.S_IRUSR | stat.S_IWUSR)
    print(f"  Wrote {auth_path} (permissions: 600)")


# --- Config Generators ---

def generate_vdirsyncer_config(apple_id, auth_path, subscribed_sources=None):
    """Generate ~/.config/vdirsyncer/config for iCloud CalDAV.

    When subscribed_sources is provided ({dir_id: source_url}), appends
    singlefile storage pairs for each subscribed calendar. These read from
    pre-sanitized local cache files (fetched by fetch_and_sanitize_feeds())
    rather than fetching HTTP directly — this avoids vdirsyncer ident
    collisions caused by non-standard VCALENDAR-level UIDs in some feeds.
    """
    config_path = Path.home() / ".config" / "vdirsyncer" / "config"
    config_path.parent.mkdir(parents=True, exist_ok=True)
    _backup_if_exists(config_path)

    abs_auth = str(auth_path.resolve())

    content = f"""[general]
status_path = "~/.local/share/vdirsyncer/status/"

[pair icloud_calendar]
a = "icloud_remote"
b = "icloud_local"
collections = ["from a", "from b"]
conflict_resolution = "a wins"

[storage icloud_remote]
type = "caldav"
url = "https://caldav.icloud.com/"
username = "{apple_id}"
password.fetch = ["command", "cat", "{abs_auth}"]

[storage icloud_local]
type = "filesystem"
path = "~/.local/share/vdirsyncer/calendars/"
fileext = ".ics"

[pair icloud_contacts]
a = "icloud_contacts_remote"
b = "icloud_contacts_local"
collections = ["from a", "from b"]
conflict_resolution = "a wins"

[storage icloud_contacts_remote]
type = "carddav"
url = "https://contacts.icloud.com/"
username = "{apple_id}"
password.fetch = ["command", "cat", "{abs_auth}"]

[storage icloud_contacts_local]
type = "filesystem"
path = "~/.local/share/vdirsyncer/contacts/"
fileext = ".vcf"
"""

    # Append singlefile pairs for subscribed calendars (sanitized ICS feeds).
    # fetch_and_sanitize_feeds() downloads the raw HTTP feed, strips any
    # VCALENDAR-level UID that would cause ident collisions, and writes
    # the result to _feed_cache/{dir_id}.ics.  vdirsyncer reads from
    # that cache via singlefile storage (read_only so it won't write back).
    if subscribed_sources:
        for dir_id, source_url in subscribed_sources.items():
            # Sanitize dir_id for TOML bare key names (hyphens → underscores)
            safe_id = dir_id.replace("-", "_")
            content += f"""
[pair sub_{safe_id}]
a = "sub_{safe_id}_remote"
b = "sub_{safe_id}_local"
collections = null
conflict_resolution = "a wins"

[storage sub_{safe_id}_remote]
type = "singlefile"
path = "~/.local/share/vdirsyncer/subscriptions/_feed_cache/{dir_id}.ics"
read_only = true

[storage sub_{safe_id}_local]
type = "filesystem"
path = "~/.local/share/vdirsyncer/subscriptions/{dir_id}/"
fileext = ".ics"
"""

    config_path.write_text(content)
    print(f"  Wrote {config_path}")
    return config_path


def run_vdirsyncer_discover(vdirsyncer_bin):
    """Run vdirsyncer discover + sync to pull calendars from iCloud."""
    print("  Running vdirsyncer discover (this may take a moment)...")

    result = subprocess.run(
        [vdirsyncer_bin, "discover"],
        input="y\n" * 20,  # Auto-answer yes for new collections
        capture_output=True, text=True
    )
    if result.returncode != 0:
        print(f"  Warning: vdirsyncer discover had issues:", file=sys.stderr)
        print(f"  {result.stderr.strip()}", file=sys.stderr)
    else:
        print("  Discovery complete.")

    print("  Running vdirsyncer sync...")
    result = subprocess.run(
        [vdirsyncer_bin, "sync"],
        capture_output=True, text=True
    )
    if result.returncode != 0:
        print(f"  Warning: vdirsyncer sync had issues:", file=sys.stderr)
        print(f"  {result.stderr.strip()}", file=sys.stderr)
    else:
        print("  Sync complete.")


def discover_calendars(cal_base):
    """List calendar directories with .ics counts, sorted by count descending."""
    cal_path = Path(cal_base)
    if not cal_path.is_dir():
        print(f"  Calendar base not found: {cal_base}")
        return []

    discovered = []
    for entry in sorted(cal_path.iterdir()):
        if not entry.is_dir():
            continue
        ics_count = sum(1 for f in entry.iterdir() if f.suffix == ".ics")
        discovered.append((entry.name, ics_count))

    discovered.sort(key=lambda x: x[1], reverse=True)
    return discovered


def discover_addressbooks(contacts_base):
    """List address book directories with .vcf counts, sorted by count descending."""
    contacts_path = Path(contacts_base)
    if not contacts_path.is_dir():
        print(f"  Contacts base not found: {contacts_base}")
        return []

    discovered = []
    for entry in sorted(contacts_path.iterdir()):
        if not entry.is_dir():
            continue
        vcf_count = sum(1 for f in entry.iterdir() if f.suffix == ".vcf")
        discovered.append((entry.name, vcf_count))

    discovered.sort(key=lambda x: x[1], reverse=True)
    return discovered


def propfind_calendars(apple_id, auth_path):
    """Query iCloud CalDAV for all calendars via PROPFIND.

    Uses a 3-step flow:
      1. PROPFIND caldav.icloud.com/ → current-user-principal href
      2. PROPFIND <principal> → calendar-home-set href
      3. PROPFIND <calendar-home> Depth:1 → all calendars

    Returns a list of dicts:
      [{"name": "Social", "dir_id": "294D4503-...", "subscribed": False,
        "source_url": None}, ...]

    Subscribed calendars include source_url (the original ICS feed URL).

    Raises Exception on auth or network errors so callers can handle gracefully.
    """
    password = Path(auth_path).read_text().strip()
    creds = base64.b64encode(f"{apple_id}:{password}".encode()).decode()
    auth_header = f"Basic {creds}"

    # Namespaces used in CalDAV/WebDAV responses
    DAV = "{DAV:}"
    CALDAV = "{urn:ietf:params:xml:ns:caldav}"
    CS = "{http://calendarserver.org/ns/}"

    def _propfind(url, body, depth="0"):
        """Send a PROPFIND request and return parsed XML root."""
        req = Request(url, data=body.encode("utf-8"), method="PROPFIND")
        req.add_header("Authorization", auth_header)
        req.add_header("Content-Type", "application/xml; charset=utf-8")
        req.add_header("Depth", depth)
        resp = urlopen(req, timeout=30)
        return ET.fromstring(resp.read()), resp.url

    def _mkurl(base_url, href):
        """Build full URL from a base URL and an href.

        iCloud may return absolute URLs pointing to a shard
        (e.g. https://p110-caldav.icloud.com:443/...) — use those as-is.
        For relative paths, prepend the scheme+host from the response URL.
        """
        if href.startswith("http://") or href.startswith("https://"):
            return href
        from urllib.parse import urlparse
        parsed = urlparse(base_url)
        return f"{parsed.scheme}://{parsed.netloc}{href}"

    # Step 1: Get principal URL
    body1 = """<?xml version="1.0" encoding="utf-8"?>
<d:propfind xmlns:d="DAV:">
  <d:prop><d:current-user-principal/></d:prop>
</d:propfind>"""

    root1, base1 = _propfind("https://caldav.icloud.com/", body1)
    principal_el = root1.find(f".//{DAV}current-user-principal/{DAV}href")
    if principal_el is None or not principal_el.text:
        raise Exception("PROPFIND: could not find current-user-principal")
    principal_url = _mkurl(base1, principal_el.text)

    # Step 2: Get calendar-home-set URL
    body2 = """<?xml version="1.0" encoding="utf-8"?>
<d:propfind xmlns:d="DAV:" xmlns:c="urn:ietf:params:xml:ns:caldav">
  <d:prop><c:calendar-home-set/></d:prop>
</d:propfind>"""

    root2, base2 = _propfind(principal_url, body2)
    home_el = root2.find(f".//{CALDAV}calendar-home-set/{DAV}href")
    if home_el is None or not home_el.text:
        raise Exception("PROPFIND: could not find calendar-home-set")
    home_url = _mkurl(base2, home_el.text)

    # Step 3: List all calendars with Depth:1
    # Include cs:source to get the original ICS feed URL for subscribed calendars
    body3 = """<?xml version="1.0" encoding="utf-8"?>
<d:propfind xmlns:d="DAV:" xmlns:cs="http://calendarserver.org/ns/">
  <d:prop>
    <d:displayname/>
    <d:resourcetype/>
    <cs:source/>
  </d:prop>
</d:propfind>"""

    root3, base3 = _propfind(home_url, body3, depth="1")

    calendars = []
    for response in root3.findall(f"{DAV}response"):
        href_el = response.find(f"{DAV}href")
        if href_el is None or not href_el.text:
            continue

        # Extract dir_id from href: /12345/calendars/<dir_id>/
        href = href_el.text.rstrip("/")
        parts = href.split("/")
        if len(parts) < 2:
            continue
        dir_id = parts[-1]

        # Skip the calendar-home itself (its dir_id would be "calendars")
        if dir_id == "calendars" or dir_id == "":
            continue

        # Check resourcetype for calendar or subscribed
        propstat = response.find(f"{DAV}propstat")
        if propstat is None:
            continue
        restype = propstat.find(f"{DAV}prop/{DAV}resourcetype")
        if restype is None:
            continue

        is_calendar = restype.find(f"{CALDAV}calendar") is not None
        is_subscribed = restype.find(f"{CS}subscribed") is not None

        # Must be a calendar (owned or subscribed) — skip notification
        # collections and other non-calendar resources
        if not is_calendar and not is_subscribed:
            continue

        displayname_el = propstat.find(f"{DAV}prop/{DAV}displayname")
        name = displayname_el.text if displayname_el is not None and displayname_el.text else dir_id

        # Extract source URL for subscribed calendars (original ICS feed)
        source_url = None
        source_el = propstat.find(f"{DAV}prop/{CS}source")
        if source_el is not None:
            source_href = source_el.find(f"{DAV}href")
            if source_href is not None and source_href.text:
                source_url = source_href.text

        calendars.append({
            "name": name,
            "dir_id": dir_id,
            "subscribed": is_subscribed,
            "source_url": source_url,
        })

    return calendars


def write_config_json(config_path, email, apple_id, display_name, tz,
                      calendars, default_calendar, bins,
                      addressbooks=None, default_addressbook=None, contacts_base=None,
                      subscribed_calendars=None, subscribed_sources=None):
    """Write the main config.json."""
    config_path.parent.mkdir(parents=True, exist_ok=True)

    if config_path.exists():
        _backup_if_exists(config_path)

    email_addresses = [email]
    if apple_id != email:
        email_addresses.append(apple_id)

    himalaya_toml = str(config_path.parent / "himalaya.toml")

    config = {
        "timezone": tz,
        "account_email": email,
        "apple_id": apple_id,
        "display_name": display_name,
        "calendars": calendars,
        "default_calendar": default_calendar,
        "bins": bins,
        "calendar_base": "~/.local/share/vdirsyncer/calendars",
        "email_addresses": email_addresses,
        "himalaya_config": himalaya_toml,
    }

    if addressbooks:
        config["addressbooks"] = addressbooks
        config["default_addressbook"] = default_addressbook
        config["contacts_base"] = contacts_base or "~/.local/share/vdirsyncer/contacts"

    if subscribed_calendars:
        config["subscribed_calendars"] = subscribed_calendars

    if subscribed_sources:
        config["subscribed_sources"] = subscribed_sources
        config["subscribed_calendar_base"] = "~/.local/share/vdirsyncer/subscriptions"

    with open(config_path, "w") as f:
        json.dump(config, f, indent=2)
        f.write("\n")

    print(f"  Wrote {config_path}")
    return config


def generate_khal_config(calendars, cal_base, default_calendar, tz=None,
                         subscribed_calendars=None, disabled_calendars=None,
                         subscribed_cal_base=None):
    """Generate ~/.config/khal/config with explicit calendar entries.

    Skips any calendar whose name appears in disabled_calendars.
    Adds subscribed_calendars with readonly = True so khal can display
    but not write to externally-owned calendars.

    When subscribed_cal_base is provided, subscribed calendar paths use
    that base directory instead of cal_base (for HTTP-synced feeds stored
    in a separate directory).
    """
    config_path = Path.home() / ".config" / "khal" / "config"
    config_path.parent.mkdir(parents=True, exist_ok=True)
    _backup_if_exists(config_path)

    disabled = set(disabled_calendars or [])

    lines = ["[calendars]"]
    color_idx = 0
    for name, dir_id in calendars.items():
        if name in disabled:
            continue
        color = KHAL_COLORS[color_idx % len(KHAL_COLORS)]
        color_idx += 1
        lines.extend([
            f"[[{name}]]",
            f"path = {cal_base}/{dir_id}/",
            f"color = {color}",
            "",
        ])
    sub_base = subscribed_cal_base or cal_base
    for name, dir_id in (subscribed_calendars or {}).items():
        if name in disabled:
            continue
        color = KHAL_COLORS[color_idx % len(KHAL_COLORS)]
        color_idx += 1
        lines.extend([
            f"[[{name}]]",
            f"path = {sub_base}/{dir_id}/",
            f"color = {color}",
            f"readonly = True",
            "",
        ])

    default = default_calendar or next(iter(calendars), "")
    locale_lines = [
        "[locale]",
        "timeformat = %H:%M",
        "dateformat = %Y-%m-%d",
        "longdateformat = %Y-%m-%d",
        "datetimeformat = %Y-%m-%d %H:%M",
        "longdatetimeformat = %Y-%m-%d %H:%M",
    ]
    if tz:
        locale_lines.append(f"local_timezone = {tz}")
        locale_lines.append(f"default_timezone = {tz}")

    lines.extend([
        "[default]",
        f"default_calendar = {default}",
        "highlight_event_days = True",
        "",
        *locale_lines,
        "",
        "[view]",
        "theme = dark",
        "",
    ])

    config_path.write_text("\n".join(lines))
    print(f"  Wrote {config_path}")


def generate_khard_config(addressbooks, contacts_base, default_addressbook):
    """Generate ~/.config/khard/khard.conf with address book entries."""
    config_path = Path.home() / ".config" / "khard" / "khard.conf"
    config_path.parent.mkdir(parents=True, exist_ok=True)
    _backup_if_exists(config_path)

    lines = ["[addressbooks]"]
    for name, dir_id in addressbooks.items():
        lines.extend([
            f"[[{name}]]",
            f"path = {contacts_base}/{dir_id}/",
            "",
        ])

    default = default_addressbook or next(iter(addressbooks), "")
    lines.extend([
        "[general]",
        f"default_action = list",
        "",
        "[contact table]",
        "display = first_name",
        "group_by_addressbook = no",
        "reverse = no",
        "show_nicknames = no",
        "show_uids = yes",
        "sort = first_name",
        "",
    ])

    config_path.write_text("\n".join(lines))
    print(f"  Wrote {config_path}")


def generate_himalaya_config(email, apple_id, display_name, auth_path, config_dir=None):
    """Generate himalaya config.toml for IMAP/SMTP.

    When config_dir is provided, writes to config_dir/himalaya.toml (skill-local).
    Otherwise falls back to ~/.config/himalaya/config.toml (interactive wizard).
    """
    if config_dir:
        config_path = Path(config_dir) / "himalaya.toml"
    else:
        config_path = Path.home() / ".config" / "himalaya" / "config.toml"
    config_path.parent.mkdir(parents=True, exist_ok=True)
    _backup_if_exists(config_path)

    abs_auth = str(auth_path.resolve())

    content = f"""[accounts.icloud]
default = true
email = "{email}"
display-name = "{display_name}"

backend.type = "imap"
backend.host = "imap.mail.me.com"
backend.port = 993
backend.encryption.type = "tls"
backend.login = "{apple_id}"
backend.auth.type = "password"
backend.auth.command = "cat {abs_auth}"

message.send.backend.type = "smtp"
message.send.backend.host = "smtp.mail.me.com"
message.send.backend.port = 587
message.send.backend.encryption.type = "start-tls"
message.send.backend.login = "{apple_id}"
message.send.backend.auth.type = "password"
message.send.backend.auth.command = "cat {abs_auth}"
message.send.save-copy = true
folder.aliases.sent = "Sent Messages"
"""
    config_path.write_text(content)
    print(f"  Wrote {config_path}")


# --- Verification ---

def run_verification(script_dir, config):
    """Run self-tests + smoke tests for calendar and email."""
    script = script_dir / "icloud.py"
    passed = True

    print("  Running self-tests...")
    result = subprocess.run(
        [sys.executable, str(script), "--test"],
        capture_output=True, text=True
    )
    if result.returncode == 0:
        print("  ✓ Self-tests passed")
    else:
        print(f"  ✗ Self-tests failed: {result.stderr.strip()}")
        passed = False

    print("  Testing calendar list...")
    result = subprocess.run(
        [sys.executable, str(script), "calendar", "list"],
        capture_output=True, text=True
    )
    if result.returncode == 0:
        print("  ✓ Calendar access works")
    else:
        print(f"  ✗ Calendar test failed: {result.stderr.strip()}")
        passed = False

    print("  Testing email list...")
    result = subprocess.run(
        [sys.executable, str(script), "email", "list", "--count", "1"],
        capture_output=True, text=True
    )
    if result.returncode == 0:
        print("  ✓ Email access works")
    else:
        print(f"  ✗ Email test failed: {result.stderr.strip()}")
        passed = False

    return passed


# --- Agent Commands (non-interactive) ---

def cmd_setup_configure(args, script_dir):
    """Phase 1: credentials + vdirsyncer discover → outputs calendar JSON."""
    password = os.environ.get("ICLOUD_APP_PASSWORD")
    if not password:
        print("Error: $ICLOUD_APP_PASSWORD environment variable is not set.", file=sys.stderr)
        print("The agent must set this before calling setup configure.", file=sys.stderr)
        sys.exit(1)

    auth_path = script_dir.parent / "config" / "auth"
    write_auth_file(auth_path, password)

    bins = detect_binary_paths()
    apple_id = args.apple_id or args.email

    generate_vdirsyncer_config(apple_id, auth_path)
    run_vdirsyncer_discover(bins["vdirsyncer"])

    cal_base = os.path.expanduser("~/.local/share/vdirsyncer/calendars")
    discovered = discover_calendars(cal_base)

    contacts_base = os.path.expanduser("~/.local/share/vdirsyncer/contacts")
    discovered_ab = discover_addressbooks(contacts_base)

    tz = args.timezone or detect_timezone()

    output = {
        "status": "ok",
        "timezone_detected": tz,
        "calendars": [
            {"directory": dir_name, "event_count": count}
            for dir_name, count in discovered
        ],
        "addressbooks": [
            {"directory": dir_name, "contact_count": count}
            for dir_name, count in discovered_ab
        ],
    }
    print(json.dumps(output, indent=2))


def cmd_setup_finalize(args, script_dir):
    """Phase 2: write all config files after user picks calendar names.

    When --calendars is provided, uses the explicit JSON mapping (backward compat).
    When --calendars is omitted, auto-discovers via CalDAV PROPFIND and cross-
    references against local filesystem directories from vdirsyncer.
    """
    bins = detect_binary_paths()
    apple_id = args.apple_id or args.email
    auth_path = script_dir.parent / "config" / "auth"
    cal_base = os.path.expanduser("~/.local/share/vdirsyncer/calendars")

    if args.calendars:
        # Explicit mapping provided — use as-is (backward compat)
        try:
            calendars = json.loads(args.calendars)
        except json.JSONDecodeError as e:
            print(f"Error: Invalid JSON for --calendars: {e}", file=sys.stderr)
            sys.exit(1)

        if not calendars:
            print("Error: --calendars must contain at least one mapping.", file=sys.stderr)
            sys.exit(1)

        # Validate dir_ids to prevent path traversal
        try:
            for name, dir_id in calendars.items():
                validate_dir_id(dir_id, f"calendar dir_id for '{name}'")
        except ValueError as e:
            print(f"Error: {e}", file=sys.stderr)
            sys.exit(1)

        subscribed_calendars = None
        subscribed_sources = None
        if getattr(args, "subscribed_calendars", None):
            try:
                subscribed_calendars = json.loads(args.subscribed_calendars)
            except json.JSONDecodeError as e:
                print(f"Error: Invalid JSON for --subscribed-calendars: {e}", file=sys.stderr)
                sys.exit(1)
            try:
                for name, dir_id in subscribed_calendars.items():
                    validate_dir_id(dir_id, f"subscribed calendar dir_id for '{name}'")
            except ValueError as e:
                print(f"Error: {e}", file=sys.stderr)
                sys.exit(1)
    else:
        # Auto-discover via PROPFIND
        print("  No --calendars provided, auto-discovering via CalDAV PROPFIND...")
        try:
            discovered = propfind_calendars(apple_id, auth_path)
        except Exception as e:
            print(f"Error: CalDAV PROPFIND failed: {e}", file=sys.stderr)
            print("\nTo proceed manually, re-run with explicit --calendars:", file=sys.stderr)
            print(f"  setup finalize ... --calendars '{{\"Name\":\"dir_id\"}}' "
                  f"--subscribed-calendars '{{\"Name\":\"dir_id\"}}'", file=sys.stderr)
            sys.exit(1)

        if not discovered:
            print("Error: PROPFIND returned no calendars.", file=sys.stderr)
            sys.exit(1)

        # Build subscribed_sources from PROPFIND results that have source_url
        subscribed_sources = {}
        for cal in discovered:
            if cal.get("source_url"):
                subscribed_sources[cal["dir_id"]] = cal["source_url"]

        # If we have subscribed sources, regenerate vdirsyncer config with
        # HTTP pairs and re-discover to create local dirs for them
        sub_cal_base = os.path.expanduser("~/.local/share/vdirsyncer/subscriptions")
        if subscribed_sources:
            print(f"  Found {len(subscribed_sources)} subscribed calendar(s) with ICS feed URLs")
            generate_vdirsyncer_config(apple_id, auth_path,
                                       subscribed_sources=subscribed_sources)
            run_vdirsyncer_discover(bins["vdirsyncer"])

        # Cross-reference against local filesystem — scan both owned and
        # subscribed base paths for directory matches
        local_dirs = set()
        if os.path.isdir(cal_base):
            local_dirs = {e for e in os.listdir(cal_base)
                          if os.path.isdir(os.path.join(cal_base, e))}
        if os.path.isdir(sub_cal_base):
            local_dirs |= {e for e in os.listdir(sub_cal_base)
                           if os.path.isdir(os.path.join(sub_cal_base, e))}

        calendars = {}
        subscribed_calendars = {}
        skipped = []
        for cal in discovered:
            if cal["dir_id"] not in local_dirs:
                skipped.append(cal)
                continue
            if cal["subscribed"]:
                subscribed_calendars[cal["name"]] = cal["dir_id"]
            else:
                calendars[cal["name"]] = cal["dir_id"]

        if not calendars and not subscribed_calendars:
            print("Error: No discovered calendars match local directories.", file=sys.stderr)
            print("Run 'setup configure' first to sync calendars from iCloud.", file=sys.stderr)
            sys.exit(1)

        if skipped:
            print(f"  Skipped {len(skipped)} calendar(s) not found on disk: "
                  f"{', '.join(c['name'] for c in skipped)}")
        print(f"  Discovered {len(calendars)} owned + "
              f"{len(subscribed_calendars)} subscribed calendar(s)")

        # Don't pass empty dict — use None so write_config_json skips the key
        if not subscribed_sources:
            subscribed_sources = None
        if not subscribed_calendars:
            subscribed_calendars = None

    if args.default not in (calendars | (subscribed_calendars or {})):
        print(f"Error: --default '{args.default}' not found in calendars.", file=sys.stderr)
        all_names = sorted(list(calendars.keys()) + list((subscribed_calendars or {}).keys()))
        print(f"Available: {', '.join(all_names)}", file=sys.stderr)
        sys.exit(1)

    addressbooks = None
    default_addressbook = None
    contacts_base = None
    if args.addressbooks:
        try:
            addressbooks = json.loads(args.addressbooks)
        except json.JSONDecodeError as e:
            print(f"Error: Invalid JSON for --addressbooks: {e}", file=sys.stderr)
            sys.exit(1)
        try:
            for name, dir_id in addressbooks.items():
                validate_dir_id(dir_id, f"addressbook dir_id for '{name}'")
        except ValueError as e:
            print(f"Error: {e}", file=sys.stderr)
            sys.exit(1)
        default_addressbook = args.default_addressbook or next(iter(addressbooks), "")
        contacts_base = os.path.expanduser("~/.local/share/vdirsyncer/contacts")

    config_path = script_dir.parent / "config" / "config.json"
    config = write_config_json(
        config_path, args.email, apple_id, args.name, args.timezone,
        calendars, args.default, bins,
        addressbooks=addressbooks, default_addressbook=default_addressbook,
        contacts_base=contacts_base,
        subscribed_calendars=subscribed_calendars,
        subscribed_sources=subscribed_sources,
    )

    # Use subscribed_cal_base if we have subscribed sources, otherwise
    # subscribed calendars use cal_base (backward compat for explicit mapping)
    sub_cal_base = None
    if subscribed_sources:
        sub_cal_base = os.path.expanduser("~/.local/share/vdirsyncer/subscriptions")
    generate_khal_config(calendars, cal_base, args.default, args.timezone,
                         subscribed_calendars=subscribed_calendars,
                         subscribed_cal_base=sub_cal_base)

    config_dir = script_dir.parent / "config"
    generate_himalaya_config(args.email, apple_id, args.name, auth_path, config_dir=config_dir)

    if addressbooks:
        generate_khard_config(addressbooks, contacts_base, default_addressbook)

    print("\nRunning verification...")
    all_passed = run_verification(script_dir, config)

    output = {
        "status": "ok" if all_passed else "partial",
        "config_written": str(config_path),
        "calendars": calendars,
        "subscribed_calendars": subscribed_calendars or {},
        "default_calendar": args.default,
        "verification_passed": all_passed,
    }
    print(json.dumps(output, indent=2))


def cmd_setup_verify(args, script_dir):
    """Run verification against current config."""
    config_path = script_dir.parent / "config" / "config.json"
    if not config_path.exists():
        print(f"Error: config not found at {config_path}", file=sys.stderr)
        sys.exit(1)

    with open(config_path) as f:
        config = json.load(f)
    config["calendar_base"] = os.path.expanduser(config["calendar_base"])

    all_passed = run_verification(script_dir, config)

    output = {
        "status": "ok" if all_passed else "partial",
        "verification_passed": all_passed,
    }
    print(json.dumps(output, indent=2))


# --- Interactive Wizard (dev-only) ---

def setup_wizard(script_dir):
    """Full interactive setup wizard for local development."""
    print("\n" + "="*60)
    print("  iCloud Toolkit — Setup Wizard")
    print("="*60)
    print("\nThis wizard will configure your iCloud Calendar and Email access.")
    print("It will ask a few questions and generate all needed config files.\n")

    _print_step(1, "Check Dependencies")
    bins = detect_binary_paths()
    for name, path in bins.items():
        print(f"  {name}: {path}")

    _print_step(2, "Account Information")
    print("We need a few details to configure your iCloud connection.\n")

    apple_id = input("Apple ID (iCloud login email): ").strip()
    if not apple_id or "@" not in apple_id:
        print("Error: A valid Apple ID email is required.", file=sys.stderr)
        sys.exit(1)

    email_input = input(f"Sending address — leave blank to use Apple ID [{apple_id}]: ").strip()
    email = email_input if email_input else apple_id

    name_guess = email.split("@")[0].replace(".", " ").title()
    name_input = input(f"Display name (for sent emails) [{name_guess}]: ").strip()
    display_name = name_input if name_input else name_guess

    detected_tz = detect_timezone()
    if detected_tz:
        print(f"\n  Detected system timezone: {detected_tz}")
    tz_input = input(f"IANA timezone (e.g. America/New_York) [{detected_tz}]: ").strip()
    tz = tz_input if tz_input else detected_tz
    if not tz:
        print("Error: A timezone is required.", file=sys.stderr)
        sys.exit(1)

    try:
        from zoneinfo import ZoneInfo
        ZoneInfo(tz)
    except (KeyError, Exception):
        print(f"Warning: '{tz}' may not be a valid IANA timezone.", file=sys.stderr)

    _print_step(3, "iCloud App-Specific Password")
    print("You need an app-specific password from Apple.")
    print("  1. Go to https://appleid.apple.com")
    print("  2. Sign-In and Security → App-Specific Passwords")
    print("  3. Generate a new password for 'iCloud Toolkit'")
    print()
    password = getpass.getpass("Paste your app-specific password: ")
    if not password:
        print("Error: A password is required.", file=sys.stderr)
        sys.exit(1)

    auth_path = script_dir.parent / "config" / "auth"
    write_auth_file(auth_path, password)

    _print_step(4, "Configure vdirsyncer (CalDAV Sync)")
    generate_vdirsyncer_config(apple_id, auth_path)

    _print_step(5, "Discover Calendars from iCloud")
    run_vdirsyncer_discover(bins["vdirsyncer"])

    _print_step(6, "Map Your Calendars")
    cal_base = os.path.expanduser("~/.local/share/vdirsyncer/calendars")
    discovered = discover_calendars(cal_base)

    if not discovered:
        print("  No calendar directories found.")
        calendars = {}
        default_calendar = None
    else:
        print("Give each calendar a friendly name, or press Enter to skip.\n")
        print(f"  {'Directory':<45} {'Events'}")
        print(f"  {'-'*45} {'-'*6}")
        for dir_name, count in discovered:
            print(f"  {dir_name:<45} {count}")
        print()

        calendars = {}
        for dir_name, count in discovered:
            name = input(f"  Name for {dir_name} ({count} events): ").strip()
            if name:
                calendars[name] = dir_name

        if not calendars:
            print("  Warning: No calendars mapped. You can edit config.json later.")
            default_calendar = None
        else:
            cal_names = list(calendars.keys())
            print(f"\n  Mapped calendars: {', '.join(cal_names)}")
            if len(cal_names) == 1:
                default_calendar = cal_names[0]
                print(f"  Default calendar: {default_calendar}")
            else:
                default_input = input(f"  Which should be the default? [{cal_names[0]}]: ").strip()
                default_calendar = default_input if default_input else cal_names[0]
                if default_calendar not in cal_names:
                    print(f"  '{default_calendar}' not in mapped names, using '{cal_names[0]}'")
                    default_calendar = cal_names[0]

    _print_step(7, "Write Configuration")
    config_path = script_dir.parent / "config" / "config.json"
    config = write_config_json(
        config_path, email, apple_id, display_name, tz,
        calendars, default_calendar, bins,
    )

    _print_step(8, "Configure khal (Calendar Display)")
    generate_khal_config(calendars, cal_base, default_calendar, tz)

    _print_step(9, "Configure himalaya (Email Client)")
    generate_himalaya_config(email, apple_id, display_name, auth_path)

    _print_step(10, "Verification")
    all_passed = run_verification(script_dir, config)

    print("\n" + "="*60)
    if all_passed:
        print("  Setup complete! Everything is working.")
    else:
        print("  Setup complete with some warnings.")
        print("  Check the output above for details.")
    print("="*60)
    print("\nTry these commands:")
    print("  python3 scripts/icloud.py calendar list --days 7")
    print("  python3 scripts/icloud.py email list")
    print()
