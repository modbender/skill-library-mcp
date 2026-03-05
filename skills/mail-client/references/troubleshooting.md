# Troubleshooting - mail-client

---

## Connection refused

**Symptom:** `OSError: [Errno 111] Connection refused` or `TimeoutError`

**Causes and fixes:**

1. Wrong host or port in `~/.openclaw/secrets/mail_creds`
   - IMAP SSL default port: 993
   - SMTP STARTTLS default port: 587
   - Re-run `python3 scripts/setup.py` to correct values

2. Firewall blocking outbound connections
   - Test with: `nc -zv mail.example.com 993`
   - Contact your network administrator or hosting provider

3. Server not reachable from this host
   - Verify DNS: `nslookup mail.example.com`
   - Try pinging the mail server IP

---

## Authentication failed

**Symptom:** `IMAP4.error: [AUTH] Authentication failed` or `SMTPAuthenticationError`

**Causes and fixes:**

1. Wrong username or app key
   - Re-run `python3 scripts/setup.py`
   - MAIL_USER should be the full email address (e.g. `user@example.com`)
   - MAIL_APP_KEY should be an application-specific password, not your main account password

2. Two-factor authentication (2FA) is enabled
   - Most providers (Gmail, Fastmail, Protonmail Bridge) require an app-specific password
   - Generate one in your account security settings
   - Gmail: My Account > Security > App passwords
   - Fastmail: Settings > Privacy & Security > Connected Apps

3. IMAP or SMTP is disabled for your account
   - Gmail: Settings > See all settings > Forwarding and POP/IMAP > Enable IMAP
   - Outlook: Account settings > Sync email > Enable IMAP

4. Credentials file permissions issue (unrelated user reading the file)
   - Run: `chmod 600 ~/.openclaw/secrets/mail_creds`

---

## IMAP folder not found

**Symptom:** `imaplib.IMAP4.error: SELECT failed` or folder returns no results

**Causes and fixes:**

1. Wrong folder name in `config.json`
   - List available folders: `python3 scripts/mail.py folders`
   - Common names: `INBOX`, `Sent`, `Drafts`, `Trash`, `Archive`, `Spam`
   - Some servers use namespaces: `INBOX.Sent`, `INBOX/Sent`
   - Update `default_folder` in `config.json` accordingly

2. Folder name is case-sensitive on some servers
   - Try uppercase `INBOX` vs lowercase `inbox`

3. Special characters in folder names
   - Folder names with spaces or special characters may need quoting
   - Use the exact name returned by the `folders` subcommand

---

## SMTP relay rejected

**Symptom:** `SMTPRecipientsRefused` or `550 relay not permitted`

**Causes and fixes:**

1. Sending to an external address from a server that requires authentication
   - Verify you are authenticated (STARTTLS + login should handle this)
   - Some servers block relay even after auth: contact your mail provider

2. MAIL_FROM address does not match authenticated user
   - Set `MAIL_FROM` to the same address as `MAIL_USER` in the creds file

3. Rate limiting or greylisting by the receiving server
   - Wait a few minutes and retry
   - Check if your IP is on a blocklist: https://mxtoolbox.com/blacklists.aspx

4. STARTTLS not supported on port 587
   - Some servers use port 465 with direct SSL (SMTP_SSL), not STARTTLS
   - This skill uses STARTTLS on port 587 by design
   - For port 465: the `send()` method must be adapted manually (replace `smtplib.SMTP` with `smtplib.SMTP_SSL`)

---

## Local server without valid TLS certificate

**Default behavior:** SSL/TLS verification is enabled (secure). The skill uses
`ssl.create_default_context()` which verifies the server certificate against the
system's CA bundle. This is the correct and safe behavior for production mail servers.

**Workaround for self-signed certificates (local/trusted servers only):**

This is a **manual code change only** - it is intentionally not a config option,
because disabling TLS verification is a security risk and must be an explicit choice
made by a developer. Only use this for trusted local servers where you control the
certificate.

**For IMAP (in `scripts/mail.py`, method `_imap_connect`):**

```python
import ssl

def _imap_connect(self) -> imaplib.IMAP4_SSL:
    ctx = ssl.create_default_context()
    ctx.check_hostname = False          # manual change only
    ctx.verify_mode = ssl.CERT_NONE     # manual change only - WARNING: insecure
    imap = imaplib.IMAP4_SSL(self._imap_host, self._imap_port, ssl_context=ctx)
    imap.login(self._user, self._app_key)
    return imap
```

**For SMTP (in `scripts/mail.py`, method `send`):**

```python
import ssl

ctx = ssl.create_default_context()
ctx.check_hostname = False          # manual change only
ctx.verify_mode = ssl.CERT_NONE     # manual change only - WARNING: insecure
with smtplib.SMTP(self._smtp_host, self._smtp_port) as srv:
    srv.ehlo()
    srv.starttls(context=ctx)       # passes the permissive context
    srv.ehlo()
    srv.login(self._user, self._app_key)
    srv.sendmail(...)
```

**Important:** This disables certificate validation entirely. Only apply this to
servers on your own trusted local network. Never use it for connections to external
or public mail servers.

---

## Quota not supported

**Symptom:** `get_quota()` returns `{"supported": false, ...}`

Some IMAP servers do not implement the QUOTA extension (RFC 2087).
This is normal. The skill handles this gracefully with a fallback.
If you need quota information, check your mail provider's web interface.

---

## Checking the effective config

```bash
python3 scripts/mail.py config
```

This prints the current `config.json` values (no secrets).
All capabilities must be explicitly set to `true` to be active.

---

## Running diagnostics

```bash
python3 scripts/init.py
```

Runs all connection and permission checks. Expected: all OK or SKIP, no FAIL.
