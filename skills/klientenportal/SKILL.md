---
name: klientenportal
description: "Automate RZL Klientenportal.at — a web-based portal by RZL Software for exchanging receipts, invoices, and reports with your tax accountant. Login/logout, upload documents (Belegübergabe), list released files, and download Kanzleidokumente via Playwright."
summary: "RZL Klientenportal automation: upload receipts, download reports."
version: 1.5.1
homepage: https://github.com/odrobnik/klientenportal-skill
metadata:
  openclaw:
    emoji: "📋"
    requires:
      bins: ["python3", "playwright"]
      python: ["playwright"]
      env: ["KLIENTENPORTAL_PORTAL_ID", "KLIENTENPORTAL_USER_ID", "KLIENTENPORTAL_PASSWORD"]
---

# RZL Klientenportal

Automate [klientenportal.at](https://klientenportal.at) — a web portal by [RZL Software](https://www.rzl.at) for securely exchanging accounting documents between clients and their tax accountant.

**Entry point:** `{baseDir}/scripts/klientenportal.py`

## Setup

See [SETUP.md](SETUP.md) for prerequisites and setup instructions.

## Commands

### Login / Logout

```bash
python3 {baseDir}/scripts/klientenportal.py login          # Test login (validates credentials)
python3 {baseDir}/scripts/klientenportal.py logout         # Clear stored browser session
```

### Upload Documents (Belegübergabe)

Upload receipts/invoices to a specific Belegkreis category:

```bash
python3 {baseDir}/scripts/klientenportal.py upload -f invoice.pdf --belegkreis KA
python3 {baseDir}/scripts/klientenportal.py upload -f *.xml --belegkreis SP
```

| Code | Name | Use for |
|------|------|---------|
| ER | Eingangsrechnungen | Incoming invoices (default) |
| AR | Ausgangsrechnungen | Outgoing invoices |
| KA | Kassa | Credit card payments |
| SP | Sparkasse | Bank account receipts |

### List Released Files

Show files your accountant has released (freigegebene Dokumente):

```bash
python3 {baseDir}/scripts/klientenportal.py released
```

### Received Files (from Accountant)

List files received from your accountant (Kanzleidokumente / Auswertungen):

```bash
python3 {baseDir}/scripts/klientenportal.py received              # List all
python3 {baseDir}/scripts/klientenportal.py received -n 5          # Latest 5
python3 {baseDir}/scripts/klientenportal.py received --json         # JSON output
```

Output columns: Datei, Von, Dokumentbereich, Empfangen

### Download Received Files

Download specific files from the received files list:

```bash
python3 {baseDir}/scripts/klientenportal.py received-download --latest                  # Latest file
python3 {baseDir}/scripts/klientenportal.py received-download 1 2 3                     # By index (1=latest)
python3 {baseDir}/scripts/klientenportal.py received-download "10-12_2025"              # By name pattern
python3 {baseDir}/scripts/klientenportal.py received-download "10-12_2025" -o ~/Downloads  # Custom output
```

Single-file downloads are auto-extracted from ZIP wrapper.

### Download Kanzleidokumente (Legacy)

Download all available Kanzleidokumente at once:

```bash
python3 {baseDir}/scripts/klientenportal.py download                    # To default dir
python3 {baseDir}/scripts/klientenportal.py download -o /path/to/dir    # Custom output dir
```

Default output: `/tmp/openclaw/klientenportal/`

### Options

- `--visible` — Show the browser window (useful for debugging or first login)

## Recommended Flow

```
login → upload / released / download → logout
```

Always call `logout` after completing all operations to clear the stored browser session.
