---
name: privatebin-upload
description: Upload content to a PrivateBin instance and return a shareable link. Use when the user wants to share text, code, reports, or files via paste URL with options like expiry, password protection, or burn-after-reading.
---

# PrivateBin Upload Skill

## When to Use

**Use this skill when:**
- User wants to upload/share text, code, reports, or files via a paste link
- User mentions "paste", "privatebin", "shareable link", "burn after reading", or "password-protect"
- User needs expiry-controlled or one-time viewing sharing

**Do NOT use this skill when:**
- User only wants to *read* an existing paste (use `privatebin show <url>` directly)
- No content or file has been identified to upload
- User is asking about PrivateBin in general without intent to upload

## Input / Output

```yaml
Input:
  content:    string | file_path   # text/code to upload, or file path
  formatter?: plaintext | markdown | syntaxhighlighting  # default: plaintext
  expire?:    5min | 10min | 1hour | 1day | 1week | 1month | 1year | never
  burn_after_reading?: boolean     # default: false
  password?:  string               # ask user if requested
  attachment?: boolean             # true for binary/image/archive files
  bin?:       string               # named instance from config

Output:
  paste_url:  string   # shareable link to present
  expire:     string   # expiry setting used
  password?:  string   # echoed back if set
```

## Steps

1. **Check CLI** — Run `privatebin --version`. If not found, install `privatebin-cli` and stop until user resolves it.

2. **Check config** — Verify `~/.config/privatebin/config.json` exists. If missing, run:
   ```bash
   privatebin init                                 # default: privatebin.net
   privatebin init --host https://bin.example.com  # custom host
   ```

3. **Determine parameters** — Infer formatter, expiry, attachment from context. Use defaults (`plaintext`, `1day`) if unspecified. Ask for password only if user requested it.

4. **Run upload** — Use `--output=json` as global flag (before `create`):
   ```bash
   # Text/code via stdin
   printf '%s' "<content>" | privatebin --output=json create [flags]

   # From file
   privatebin --output=json create --filename=/path/to/file [flags]

   # File attachment
   privatebin --output=json create --attachment --filename=/path/to/file [flags]
   ```

5. **Parse response** — Extract `paste_url` from JSON:
   ```json
   { "paste_id": "...", "paste_url": "https://bin.example.com?id#key", "delete_token": "..." }
   ```

6. **Confirm** — Present `paste_url`, expiry, and password (if set) to user.

## Common Flags

| Flag | Example | Use Case |
|------|---------|----------|
| Formatter | `--formatter=markdown` | Markdown reports |
| Expiry | `--expire=10min` | Quick share |
| Burn | `--burn-after-reading` | One-time secret |
| Password | `--password=secret` | Access control |
| Attachment | `--attachment` | Binary/image files |

## On Failure

| Error | Action |
|-------|--------|
| CLI not found | Guide user to install (see README.md) |
| `no privatebin instance configured` | Run `privatebin init --host <url> --force` |
| Rate limit | Wait 10s, retry once. If fails again, report to user |
| Upload error | Show error message. Check host URL, network, config |
