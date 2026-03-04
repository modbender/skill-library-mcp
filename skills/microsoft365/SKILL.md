---
name: microsoft365
description: Microsoft 365 integration for Outlook, Calendar, Contacts, and OneDrive via Microsoft Graph API. Supports reading/sending emails, managing calendar events, and accessing files.
metadata:
  {
    "openclaw": {
      "emoji": "🟦",
      "requires": { 
        "bins": ["node"],
        "env": ["MICROSOFT_CLIENT_ID", "MICROSOFT_TENANT_ID"]
      }
    }
  }
---

# Microsoft 365 (Custom)

This skill provides a direct integration with Microsoft 365 services using the Device Code Flow.

## Usage

The skill is executed via `node index.js`. Use the `--account <name>` flag to specify which account to use (e.g., `--account personal`).

### Calendar
- **Fetch events**: `node index.js --account personal --calendar`
- **Create event**: Use interactive mode or automated scripts.

### Email
- **Read emails**: Interactive mode (option 1).
- **Send email**: Interactive mode (option 5).

### Contacts & OneDrive
- **Contacts**: Interactive mode (option 3).
- **OneDrive files**: Interactive mode (option 4).

## Configuration & Security

This skill uses centralized credential management to keep the skill directory clean and safe for sharing.

### File Locations
- **Tokens**: Saved in `~/.openclaw/credentials/ms365.tokens.<account>.json`.
- **Environment**: Automatically loads secrets from `~/.openclaw/credentials/ms365.env` if present.
- **Config**: Expects `config.<account>.json` in the skill directory (or environment variables).

### Setup
1. Register an application in Azure (Public Client Flow, Device Code enabled).
2. Set `MICROSOFT_CLIENT_ID` and `MICROSOFT_TENANT_ID` in your environment or `~/.openclaw/credentials/ms365.env`.
3. Run `node index.js --account <name>` and follow the device login instructions.
