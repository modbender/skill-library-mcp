---
name: google-tag-manager
description: >
  Manage Google Tag Manager containers, tags, triggers, variables, and versions via the GTM API v2.
  Use when the user wants to list, create, update, delete, or inspect GTM tags, triggers, variables,
  built-in variables, workspaces, or versions. Also use for publishing container versions, auditing
  GTM setups, creating conversion tags, setting up cross-domain tracking, or managing dataLayer events.
  Covers: "GTM", "Tag Manager", "container tag", "conversion tag", "trigger", "GTM variable",
  "publish GTM", "GTM workspace", "dataLayer", "Google Ads tag", "GA4 tag", "cross-domain tracking".
metadata:
  env:
    - GTM_ACCOUNT_ID: GTM account ID (numeric). Find at tagmanager.google.com.
    - GTM_CONTAINER_ID: GTM container ID (numeric).
    - GOOGLE_APPLICATION_CREDENTIALS: Path to service account JSON key file with Tag Manager API access.
---

# Google Tag Manager Skill

Interact with the GTM API v2 to manage containers, workspaces, tags, triggers, variables, and versions.

## Authentication

The GTM API uses OAuth2 via a Google Cloud service account.

### Setup
1. Enable **Tag Manager API** in Google Cloud Console
2. Create a service account with key (JSON)
3. Grant the service account access in GTM (Admin → User Management → add service account email)
4. Set env vars:
   - `GOOGLE_APPLICATION_CREDENTIALS=/path/to/service-account.json`
   - `GTM_ACCOUNT_ID=123456`
   - `GTM_CONTAINER_ID=789012`

## Script

All operations use `scripts/gtm.sh`. Run without args to see usage:

```bash
scripts/gtm.sh <command> [args...]
```

### Commands

| Command | Description |
|---------|-------------|
| `accounts` | List all GTM accounts |
| `containers [accountId]` | List containers in account |
| `workspaces` | List workspaces in container |
| `tags [workspaceId]` | List tags in workspace (default: latest) |
| `tag <tagId> [workspaceId]` | Get a specific tag |
| `create-tag <jsonFile> [workspaceId]` | Create a tag from JSON |
| `update-tag <tagId> <jsonFile> [workspaceId]` | Update a tag |
| `delete-tag <tagId> [workspaceId]` | Delete a tag |
| `triggers [workspaceId]` | List triggers |
| `trigger <triggerId> [workspaceId]` | Get a specific trigger |
| `create-trigger <jsonFile> [workspaceId]` | Create a trigger from JSON |
| `update-trigger <triggerId> <jsonFile> [workspaceId]` | Update a trigger |
| `delete-trigger <triggerId> [workspaceId]` | Delete a trigger |
| `variables [workspaceId]` | List variables |
| `variable <variableId> [workspaceId]` | Get a specific variable |
| `create-variable <jsonFile> [workspaceId]` | Create a variable from JSON |
| `update-variable <variableId> <jsonFile> [workspaceId]` | Update a variable |
| `delete-variable <variableId> [workspaceId]` | Delete a variable |
| `built-in-vars [workspaceId]` | List enabled built-in variables |
| `enable-built-in <type,...> [workspaceId]` | Enable built-in variable(s) |
| `versions` | List container version headers |
| `version <versionId>` | Get a specific version |
| `version-live` | Get the live (published) version |
| `create-version [workspaceId] [name] [notes]` | Create version from workspace |
| `publish <versionId>` | Publish a container version |

### Workspace Resolution

Most commands accept an optional `workspaceId`. If omitted, the script auto-resolves to the **Default Workspace** (the first workspace returned by the API — typically "Default Workspace").

## Common Recipes

### Create a Google Ads Conversion Tag

See `references/recipes.md` for JSON templates for:
- Google Ads Conversion Tracking tag
- GA4 Event tag
- Custom Event trigger (dataLayer)
- Cross-domain tracking linker

### Workflow: Add Tag → Create Version → Publish

```bash
# 1. Create trigger
scripts/gtm.sh create-trigger trigger.json

# 2. Create tag referencing the trigger
scripts/gtm.sh create-tag tag.json

# 3. Create version from workspace
scripts/gtm.sh create-version "" "v1.2 - Added conversion tag"

# 4. Publish
scripts/gtm.sh publish <versionId>
```

## API Reference

For full resource schemas and trigger types, see `references/api-reference.md`.
