---
name: namecheap-dns
description: Safe DNS record management for Namecheap domains. Fetch, add, remove, backup, and restore DNS records with automatic safety checks and dry-run mode. Prevents accidental DNS record wipeout via the Namecheap API's destructive setHosts method.
homepage: https://www.namecheap.com/support/api/
metadata:
  {
    "openclaw":
      {
        "emoji": "🌐",
        "requires": { "bins": ["node", "npm"] },
      },
  }
---

# Namecheap DNS Management

Safe wrapper around the Namecheap API for DNS operations. **Prevents accidental record wipeout** by always fetching existing records first and merging changes.

## ⚠️ Why This Skill Exists

The Namecheap API's `setHosts` method **replaces ALL DNS records** for a domain. One wrong API call = your entire DNS config is gone. This skill:

- ✅ Always fetches existing records first
- ✅ Merges new records with existing ones (unless explicitly replacing)
- ✅ Shows a diff preview before applying changes
- ✅ Auto-backups before every change
- ✅ Supports dry-run mode for safe testing
- ✅ One-command rollback from backups

## Setup

### 1. Install dependencies

```bash
cd ~/.openclaw/workspace/skills/namecheap-dns
npm install
```

### 2. Enable Namecheap API access

1. Go to https://ap.www.namecheap.com/settings/tools/apiaccess/
2. Toggle "API Access" ON
3. Whitelist your IP address
4. Copy your API key

### 3. Set environment variables

Add to `~/.zshrc` or `~/.bashrc`:

```bash
export NAMECHEAP_API_KEY="your-api-key-here"
export NAMECHEAP_USERNAME="your-username"
export NAMECHEAP_API_USER="your-username"  # Usually same as username
```

## Usage

### Verify DNS and detect ghost records

**⚠️ IMPORTANT: Run this first!**

```bash
./namecheap-dns.js verify example.com
```

This command compares DNS records visible to the Namecheap API with actual live DNS records (via `dig`). It will warn you about "ghost records" that exist in DNS but are invisible to the API (email forwarding, URL redirects, etc.).

### List current DNS records

```bash
./namecheap-dns.js list example.com
```

**Note:** This only shows records visible to the API. Use `verify` to see ALL records including those managed by Namecheap subsystems.

### Add records (safe merge)

```bash
# Add a single TXT record
./namecheap-dns.js add example.com \
  --txt "mail.example.com=v=spf1 include:mailgun.org ~all"

# Add multiple records at once
./namecheap-dns.js add example.com \
  --txt "mail=v=spf1 include:mailgun.org ~all" \
  --cname "email.mail=mailgun.org" \
  --mx "mail=10 mxa.mailgun.org"

# Dry-run (preview changes without applying)
./namecheap-dns.js add example.com \
  --txt "test=hello" \
  --dry-run

# Force override safety check (if you know ghost records can be deleted)
./namecheap-dns.js add example.com \
  --txt "test=hello" \
  --force
```

**Safety:** The skill automatically checks for "ghost records" before making changes. If detected, it will refuse to proceed unless you use `--force`.

### Remove records

```bash
# Remove by host + type
./namecheap-dns.js remove example.com \
  --host "old-record" \
  --type "TXT"

# Dry-run first
./namecheap-dns.js remove example.com \
  --host "old-record" \
  --type "TXT" \
  --dry-run
```

### Backup & Restore

```bash
# Create manual backup
./namecheap-dns.js backup example.com

# List available backups
./namecheap-dns.js backups example.com

# Restore from latest backup
./namecheap-dns.js restore example.com

# Restore from specific backup
./namecheap-dns.js restore example.com \
  --backup "example.com-20260213-114500.json"
```

## Record Format

### TXT Records
```
--txt "subdomain=value"
--txt "@=value"  # Root domain
```

### CNAME Records
```
--cname "subdomain=target.com"
```

### MX Records
```
--mx "subdomain=10 mx.target.com"
--mx "@=10 mx.target.com"  # Root domain
```

### A Records
```
--a "subdomain=192.168.1.1"
--a "@=192.168.1.1"  # Root domain
```

## Backup Location

**Default:** `./backups/` (relative to skill directory)

**Configurable via environment variable:**
```bash
export NAMECHEAP_BACKUP_DIR="/custom/path/to/backups"
```

Format: `{domain}-{timestamp}.json`

Each backup includes:
- `apiHosts`: Records visible to Namecheap API
- `liveDNS`: Actual DNS records captured via `dig`
- Timestamp and domain metadata

This allows you to see what was ACTUALLY live in DNS, not just what the API knew about.

## Safety Features

1. **Ghost record detection** — automatic check for records invisible to API
2. **Auto-backup before changes** — every `add` or `remove` creates a timestamped backup (includes DNS snapshot)
3. **Dry-run mode** — `--dry-run` shows what will change without applying
4. **Diff preview** — see exactly what records will be added/removed
5. **Fetch-first** — always gets current DNS state before changes
6. **Merge logic** — adds to existing records instead of replacing
7. **Rollback** — one command to restore from backup
8. **Safety override** — `--force` flag for when you need to bypass ghost record warnings

## Examples

### Mailgun Setup

```bash
./namecheap-dns.js add menuhq.ai \
  --txt "mail.menuhq.ai=v=spf1 include:mailgun.org ~all" \
  --txt "smtp._domainkey.mail.menuhq.ai=k=rsa; p=MIGfMA0..." \
  --txt "_dmarc.mail.menuhq.ai=v=DMARC1; p=quarantine;" \
  --cname "email.mail.menuhq.ai=mailgun.org" \
  --mx "mail.menuhq.ai=10 mxa.mailgun.org" \
  --mx "mail.menuhq.ai=20 mxb.mailgun.org" \
  --dry-run
```

Review the diff, then run without `--dry-run` to apply.

## Known Limitations

### ⚠️ The Namecheap API is Destructive

The Namecheap `domains.dns.setHosts` API method **replaces ALL DNS records** for a domain. There is no "add one record" or "update one record" endpoint. Every change requires:

1. Fetch all existing records (`getHosts`)
2. Modify the list
3. Upload the entire list (`setHosts`)

**This skill handles this for you** by always fetching first and merging changes.

### 🔍 Ghost Records: The Hidden Danger

**Problem:** `domains.dns.getHosts` does NOT return all DNS records. Records managed by Namecheap subsystems are invisible to the API:

- **Email Forwarding** — MX, SPF, and DKIM records
- **URL Redirect** — A/CNAME records for domain parking/redirects
- **Third-party integrations** — Records added through Namecheap's dashboard for services

Since `setHosts` **replaces all records**, using the API can silently delete these hidden records.

### 🛡️ How This Skill Protects You

1. **`verify` command** — Compares API records with actual live DNS (via `dig`) and warns about ghost records
2. **Automatic safety check** — Before any `add`, `remove`, or `restore`, the skill checks for ghost records
3. **Refuses to proceed** — If ghost records are detected, the operation is blocked (unless `--force` is used)
4. **Clear warnings** — Shows exactly which records will be lost if you proceed
5. **DNS snapshots in backups** — Captures actual DNS state via `dig`, not just API state

### When to Use `--force`

Only use the `--force` flag when:

- You've manually verified the ghost records are no longer needed
- You're intentionally removing email forwarding or URL redirects
- You understand and accept that those records will be deleted

**Never use `--force` blindly.** Always run `verify` first to see what will be lost.

### Example: The Production Incident

This skill was created after adding Mailgun DNS records via the API wiped out Namecheap's email forwarding records. The email forwarding MX/SPF/TXT records were invisible to `getHosts`, so the fetch-merge-write pattern deleted them.

Now, the skill would have:
1. Detected the ghost records during `verify`
2. Refused to proceed without `--force`
3. Shown exactly which email forwarding records would be deleted
4. Created a backup including the DNS snapshot

## Troubleshooting

### "API request failed: IP not whitelisted"
- Add your current IP to https://ap.www.namecheap.com/settings/tools/apiaccess/
- Check with: `curl ifconfig.me`

### "Invalid API key"
- Verify `NAMECHEAP_API_KEY` is set correctly
- Re-enable API access if needed

### "Domain not found"
- Ensure domain is in your Namecheap account
- Check spelling (case-sensitive)

## API Reference

Namecheap API docs: https://www.namecheap.com/support/api/methods/domains-dns/
