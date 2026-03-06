---
name: post-at
description: Manage Austrian Post (post.at) deliveries - list packages, check delivery status, set delivery place preferences.
homepage: https://github.com/krausefx/post-at-cli
metadata: {"clawdbot":{"emoji":"📦","requires":{"bins":["node"]}}}
---

# post-at CLI

Unofficial CLI for viewing and managing deliveries on post.at (Österreichische Post). Uses the same web flows as the site and requires your own account credentials.

Credentials: `POST_AT_USERNAME` and `POST_AT_PASSWORD` environment variables (or `--username` / `--password` options).

## Quick Reference

### Login
Cache a short-lived session (auto-expires):
```bash
post-at login
# Output: Logged in as you@example.com
```

### List Deliveries
Upcoming deliveries (default):
```bash
post-at deliveries
# Shows: tracking number, ETA, sender, status
```

All deliveries (including delivered):
```bash
post-at deliveries --all
```

JSON output:
```bash
post-at deliveries --json
```

Limit results:
```bash
post-at deliveries --limit 10
```

### Delivery Details
Get details for a specific tracking number:
```bash
post-at delivery 1042348411302810212306
# Output: tracking, expected delivery, sender, status, picture URL
```

JSON output:
```bash
post-at delivery <tracking-number> --json
```

### Delivery Place Options (Wunschplatz)

List available place options:
```bash
post-at routing place-options
```

Common options:
- `Vor_Haustüre` — Vor der Haustüre
- `Vor_Wohnungstüre` — Vor der Wohnungstüre
- `AufOderUnter_Briefkasten` — Unter / Auf dem Briefkasten
- `Hinter_Zaun` — Hinter dem Zaun
- `In_Garage` — In der Garage
- `Auf_Terrasse` — Auf der Terrasse
- `Im_Carport` — Im Carport
- `In_Flexbox` — In der Flexbox
- `sonstige` — Anderer Wunsch‑Platz

### Set Delivery Place
Using preset shortcut:
```bash
post-at routing place <tracking-number> \
  --preset vor-der-wohnungstuer \
  --description "Please leave at the door"
```

Using key directly:
```bash
post-at routing place <tracking-number> \
  --key Vor_Wohnungstüre \
  --description "Bitte vor die Wohnungstür"
```

Using label:
```bash
post-at routing place <tracking-number> \
  --place "Vor der Wohnungstüre" \
  --description "Custom instructions"
```

## Example Workflows

Check what's arriving today/tomorrow:
```bash
post-at deliveries
```

Get full details including package photo:
```bash
post-at delivery <tracking-number>
```

Set all upcoming deliveries to door:
```bash
# First list deliveries
post-at deliveries --json > /tmp/deliveries.json

# Then set place for each (requires scripting)
# Example for a specific one:
post-at routing place 1042348411302810212306 \
  --preset vor-der-wohnungstuer \
  --description "Leave at apartment door"
```

## Notes

- Session tokens expire after a short time (auto-relogin when needed)
- Not all deliveries support Wunschplatz redirection
- Picture URLs may not be available for all packages
- Use `--json` output for programmatic processing
