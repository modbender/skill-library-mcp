# Namecheap DNS Skill

Safe DNS record management for Namecheap domains. Prevents accidental DNS wipeout by the Namecheap API's destructive `setHosts` method.

## ⚠️ Why This Exists

The Namecheap API's `setHosts` method **replaces ALL DNS records** at once. One wrong call = your entire DNS is gone. This skill wraps the API with safety features:

- ✅ Always fetches existing records first
- ✅ Merges new records with existing (no accidental wipeout)
- ✅ Shows diff preview before applying
- ✅ Auto-backups before every change
- ✅ Dry-run mode for safe testing
- ✅ One-command rollback

## Quick Start

```bash
# List current DNS
./namecheap-dns.js list menuhq.ai

# Add a TXT record (dry-run first)
./namecheap-dns.js add menuhq.ai \
  --txt "mail=v=spf1 include:mailgun.org ~all" \
  --dry-run

# Apply it
./namecheap-dns.js add menuhq.ai \
  --txt "mail=v=spf1 include:mailgun.org ~all"

# Rollback if needed
./namecheap-dns.js restore menuhq.ai
```

## Installation

See `SKILL.md` for full setup instructions.

## Examples

### Mailgun Email Setup

```bash
# Add all Mailgun DNS records at once
./namecheap-dns.js add menuhq.ai \
  --txt "mail.menuhq.ai=v=spf1 include:mailgun.org ~all" \
  --txt "smtp._domainkey.mail.menuhq.ai=k=rsa; p=MIGfMA0GCS..." \
  --txt "_dmarc.mail.menuhq.ai=v=DMARC1; p=quarantine;" \
  --cname "email.mail.menuhq.ai=mailgun.org" \
  --mx "mail.menuhq.ai=10 mxa.mailgun.org" \
  --mx "mail.menuhq.ai=20 mxb.mailgun.org" \
  --dry-run
```

Review the preview, then run without `--dry-run`.

### Add Custom Domain

```bash
# Point subdomain to server
./namecheap-dns.js add example.com \
  --a "app=192.168.1.100" \
  --cname "www=app.example.com"
```

### Remove Old Records

```bash
# Remove by host + type
./namecheap-dns.js remove example.com \
  --host "old-service" \
  --type "A" \
  --dry-run
```

## Safety Features

1. **Auto-backup** — every change creates `~/.openclaw/workspace/data/namecheap-backups/{domain}-{timestamp}.json`
2. **Dry-run** — `--dry-run` shows what will change without applying
3. **Diff preview** — always shows exactly what's added/removed
4. **Merge logic** — adds to existing records, doesn't replace
5. **Rollback** — `restore` command brings back the last state

## Commands

| Command | Description |
|---------|-------------|
| `list <domain>` | Show current DNS records |
| `add <domain> [options]` | Add records (merges with existing) |
| `remove <domain> [options]` | Remove specific records |
| `backup <domain>` | Create manual backup |
| `backups <domain>` | List available backups |
| `restore <domain> [options]` | Restore from backup |

## Record Types Supported

- **TXT** — `--txt "host=value"`
- **CNAME** — `--cname "host=target.com"`
- **MX** — `--mx "host=10 mx.example.com"`
- **A** — `--a "host=192.168.1.1"`

Use `@` for root domain: `--a "@=192.168.1.1"`

## Limitations

- Only works with domains using **Namecheap nameservers** (`registrar-servers.com`)
- Domains using custom nameservers (Cloudflare, Route53, etc.) must be managed via those platforms
- Check nameservers: `dig example.com NS +short`

## Troubleshooting

### "IP not whitelisted"
Add your IP at https://ap.www.namecheap.com/settings/tools/apiaccess/
Check current IP: `curl ifconfig.me`

### "Invalid API key"
Verify `NAMECHEAP_API_KEY` in `~/.zshrc`

### Records not showing
Domain might use custom nameservers. Check: `dig example.com NS +short`

## Publishing to ClawHub

This skill is designed to be shared on ClawHub so others don't make DNS mistakes.

```bash
cd ~/.openclaw/workspace/skills/namecheap-dns
clawhub publish .
```

## License

MIT — Use freely, share improvements
