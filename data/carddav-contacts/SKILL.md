---
name: carddav-contacts
description: Sync and manage CardDAV contacts (Google, iCloud, Nextcloud, etc.) using vdirsyncer + khard.
metadata: {"clawdbot":{"emoji":"📇","os":["linux"],"requires":{"bins":["vdirsyncer","khard"]},"install":[{"id":"apt","kind":"apt","packages":["vdirsyncer","khard"],"bins":["vdirsyncer","khard"],"label":"Install vdirsyncer + khard via apt"}]}}
---

# CardDAV Contacts (vdirsyncer + khard)

**vdirsyncer** syncs CardDAV contacts to local `.vcf` files. **khard** reads and manages them via CLI.

## Sync First

Always sync before querying to ensure you have the latest contacts:
```bash
vdirsyncer sync
```

## Quick Search (Smart)

If configured with `default_action = list` (standard), you can search directly without subcommands:

```bash
khard "john"                     # Search for "john" in all fields
khard "pilar"                    # Search for "pilar"
```

## List & Search (Explicit)

Use `list` if you need specific flags or if the implicit search doesn't match your config.

```bash
khard list                       # List all contacts
khard list "john"                # Search explicitly
khard list -a work               # List only from 'work' address book
khard list -p                    # Parsable output (tab-separated)
```

## View Contact Details

```bash
khard show "john doe"            # Show details (pretty print)
khard show --format yaml "john"  # Show as YAML (good for editing)
```

## Quick Field Lookup

Extract specific info (great for piping):

```bash
khard email "john"               # List emails only
khard phone "john"               # List phone numbers only
khard postaddress "john"         # List postal addresses
```

## Management

```bash
khard new                        # Create new contact (interactive editor)
khard edit "john"                # Edit contact (interactive editor)
khard remove "john"              # Delete contact
khard move "john" -a work        # Move to another address book
```

## Configuration Setup

### 1. Configure vdirsyncer (`~/.config/vdirsyncer/config`)

```ini
[pair google_contacts]
a = "google_contacts_remote"
b = "google_contacts_local"
collections = ["from a", "from b"]
conflict_resolution = "a wins"

[storage google_contacts_remote]
type = "carddav"
url = "https://www.googleapis.com/.well-known/carddav"
username = "your@email.com"
password.fetch = ["command", "cat", "~/.config/vdirsyncer/google_app_password"]

[storage google_contacts_local]
type = "filesystem"
path = "~/.local/share/vdirsyncer/contacts/"
fileext = ".vcf"
```

### 2. Configure khard (`~/.config/khard/khard.conf`)

Critically, set `default_action = list` to enable quick search.

```ini
[addressbooks]
[[google]]
path = ~/.local/share/vdirsyncer/contacts/default/

[general]
default_action = list
editor = vim
merge_editor = vimdiff

[contact table]
display = formatted_name
sort = last_name
```

### 3. Initialize

```bash
mkdir -p ~/.local/share/vdirsyncer/contacts
vdirsyncer discover google_contacts
vdirsyncer sync
```
