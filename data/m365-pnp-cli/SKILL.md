---
name: m365-pnp-cli
description: CLI for Microsoft 365 - Manage Microsoft 365 tenant, SharePoint Online, Teams, OneDrive, and more. Official PnP (Patterns and Practices) CLI.
metadata:
  {
    "openclaw":
      {
        "requires":
          {
            "bins": ["m365"],
            "node": ">=20.0.0",
            "npmPackages": ["@pnp/cli-microsoft365"]
          },
        "install":
          [
            {
              "id": "node",
              "kind": "node",
              "package": "@pnp/cli-microsoft365",
              "label": "Install m365 CLI (npm)",
              "description": "Install the CLI for Microsoft 365 globally: npm install -g @pnp/cli-microsoft365"
            }
          ],
        "homepage": "https://pnp.github.io/cli-microsoft365",
        "repository": "https://github.com/pnp/cli-microsoft365",
        "author": "Microsoft PnP (Patterns and Practices)",
        "keywords": ["microsoft365", "m365", "sharepoint", "teams", "onenote", "outlook", "cli", "microsoft", "pnp"],
        "npmPackage": "@pnp/cli-microsoft365"
      }
  }
---

# m365-pnp-cli Skill

This skill provides access to the **CLI for Microsoft 365** – the official PnP (Patterns and Practices) tool for Microsoft 365 management.

## ⚠️ IMPORTANT FOR AGENTS

**When in doubt, ALWAYS call `m365 --help` first to see all possibilities!**

```bash
# Always call help when unsure!
m365 --help

# For specific commands:
m365 login --help
m365 spo --help
m365 teams --help
```

## Installation

The CLI must be installed:
```bash
npm install -g @pnp/cli-microsoft365
```

Or use npx (sandbox):
```bash
npx @pnp/cli-microsoft365 --help
```

## Source & Verification

- **NPM Package:** https://www.npmjs.com/package/@pnp/cli-microsoft365
- **GitHub Repo:** https://github.com/pnp/cli-microsoft365
- **Documentation:** https://pnp.github.io/cli-microsoft365
- **Author:** Microsoft PnP (Patterns and Practices Community)

## What can the CLI do?

### Supported Workloads
- Microsoft Teams
- SharePoint Online
- OneDrive
- Outlook
- Microsoft To Do
- Microsoft Planner
- Power Automate
- Power Apps
- Microsoft Entra ID
- Microsoft Purview
- Bookings
- And more...

### Authentication
- Device Code (default)
- Username/Password
- Client Certificate
- Client Secret
- Azure Managed Identity
- Federated Identity

## Commands (Overview)

### Login/Logout
```bash
m365 login                    # Device Code Login
m365 logout                  # Logout
m365 status                  # Check login status
```

### SharePoint Online (spo)
```bash
m365 spo site list           # List all sites
m365 spo site get --url <url>  # Get site details
m365 spo list list --webUrl <url>  # Lists in a site
m365 spo file list           # List files
m365 spo folder add          # Create folder
```

### Teams
```bash
m365 teams channel list       # List channels
m365 teams channel get       # Get channel details
m365 teams user list         # List team members
m365 teams chat list         # List chats
m365 teams meeting list      # List meetings
```

### OneDrive
```bash
m365 onedrive drive list    # OneDrive Drives
m365 onedrive file list     # List files
m365 onedrive file get      # Get file content
```

### Outlook
```bash
m365 outlook mail list       # List emails
m365 outlook calendar list   # List calendar events
```

### Planner
```bash
m365 planner task list       # Planner Tasks
m365 planner plan get        # Get plan details
```

### Azure AD / Entra ID
```bash
m365 entra user list         # List users
m365 entra group list        # List groups
m365 entra app list          # List apps
```

## Usage as Assistant - IMPORTANT

### ⚡ First Step: ALWAYS call help!

```bash
# When in doubt - call help first!
m365 --help

# For specific commands:
m365 spo --help
m365 teams --help
m365 login --help
```

### Basic Usage

```bash
# Login (Device Code Flow)
m365 login

# Check status
m365 status

# SharePoint: List sites
m365 spo site list

# SharePoint: Get specific site
m365 spo site get --url "https://contoso.sharepoint.com/sites/test"

# Teams: List channels
m365 teams channel list --teamId <team-id>

# OneDrive: Files
m365 onedrive file list

# Outlook: Emails
m365 outlook mail list --folder Inbox

# Planner: Tasks
m365 planner task list
```

## Output Options

```bash
# As JSON (default)
m365 spo site list

# As text
m365 spo site list --output text

# Filter with JMESPath
m365 spo site list --query "[?Template==\`GROUP#0\`].{Title:Title, Url:Url}"
```

## Authentication

The CLI uses **Device Code Flow** by default:

```bash
m365 login
# → You'll receive a code on another device
# → Use that code to authenticate with Microsoft
```

For automated scripts, you can also use:
- **Certificate** (recommended for production)
- **Client Secret** (less secure)
- **Username/Password** (testing only)

## Important

- **WHEN IN DOUBT: call m365 --help!**
- **Login required** for most commands
- **JSON output** is easiest to parse
- **JMESPath** for efficient filtering
- CLI requires **Node.js >= 20**
