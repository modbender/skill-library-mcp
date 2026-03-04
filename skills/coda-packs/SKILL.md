---
name: coda-packs
description: Manage Coda Packs via REST API v1. Supports listing, creating, updating, and deleting private Packs. Requires CODA_API_TOKEN. Delete requires confirmation. Note: Builds, Gallery submission, Analytics, and Collaborators require Coda's Pack SDK CLI, not available via REST API.
---

# Coda Packs Skill

Manage Coda Packs through the REST API v1. Create, list, update, and delete private Packs.

## ⚠️ API Limitations

The Coda REST API v1 has limited Pack management capabilities:

| Feature | REST API | Pack SDK CLI |
|---------|----------|--------------|
| **List Packs** | ✅ Available | ✅ |
| **Create Pack** | ✅ Available | ✅ |
| **Update Pack** | ✅ Available | ✅ |
| **Delete Pack** | ✅ Available | ✅ |
| **Build Versions** | ❌ Not available | ✅ Required |
| **Gallery Submit** | ❌ Not available | ✅ Required |
| **Analytics** | ❌ Not available | ✅ Required |
| **Collaborators** | ❌ Not available | ✅ Required |

**For builds, gallery submission, and advanced features, use:**
```bash
npx @codahq/packs-sdk register    # Create account
npx @codahq/packs-sdk build       # Build Pack
npx @codahq/packs-sdk release     # Submit to Gallery
```

## When to Use

Use this skill when the user wants to:
- List existing Coda Packs
- Create new private Pack shells
- Update Pack metadata (name, description)
- Delete unused Packs

## When NOT to Use

- **Do NOT use** for Doc management (tables, rows, pages) → use `coda` skill
- **Do NOT use** for building Pack versions → use Pack SDK CLI
- **Do NOT use** for Gallery submission → use Pack SDK CLI
- **Do NOT use** for viewing analytics → use Pack SDK CLI or Coda web UI

## Prerequisites

1. **API Token**: Set environment variable `CODA_API_TOKEN`
   - Get token at: https://coda.io/account -> API Settings
   - Must have Pack management permissions

2. **Python 3.7+** with `requests` library

## Quick Start

```bash
# Setup
export CODA_API_TOKEN="your_token_here"

# List your Packs
python scripts/coda_packs_cli.py packs list

# Create new Pack shell
python scripts/coda_packs_cli.py packs create \
  --name "My Integration" \
  --description "Does cool things"

# Update Pack
python scripts/coda_packs_cli.py packs update my-pack-id \
  --description "Updated description"

# Delete Pack (requires confirmation)
python scripts/coda_packs_cli.py packs delete my-pack-id
```

## Full Pack Development Workflow

Since the REST API only supports basic Pack management, here's the complete workflow:

### Step 1: Create Pack Shell (via REST API)
```bash
python scripts/coda_packs_cli.py packs create \
  --name "Karakeep Bookmarks" \
  --description "Save and search bookmarks"
```

### Step 2-4: Use Pack SDK CLI (Required)
```bash
# Install Pack SDK
npm install -g @codahq/packs-sdk

# Initialize Pack project
npx @codahq/packs-sdk init karakeep-pack

# Develop your Pack (edit pack.ts)
# See: https://coda.io/packs/build/latest/guides/quickstart/

# Build and upload
npx @codahq/packs-sdk build
npx @codahq/packs-sdk upload

# Submit to Gallery (when ready)
npx @codahq/packs-sdk release
```

## CLI Tool Usage

### Pack Management

```bash
# List all your Packs
python scripts/coda_packs_cli.py packs list

# Get Pack details
python scripts/coda_packs_cli.py packs get 48093
python scripts/coda_packs_cli.py packs get "Karakeep"

# Create new Pack
python scripts/coda_packs_cli.py packs create \
  --name "My Pack" \
  --description "Description" \
  --readme "# My Pack\n\nDetails here"

# Update Pack metadata
python scripts/coda_packs_cli.py packs update my-pack-id \
  --name "New Name" \
  --description "New description"

# Delete Pack (requires confirmation)
python scripts/coda_packs_cli.py packs delete my-pack-id
# Or skip confirmation: --force
```

### Pack ID Resolution

The CLI accepts both **numeric Pack IDs** and **Pack Names**:

```bash
# These are equivalent:
python scripts/coda_packs_cli.py packs get 48093
python scripts/coda_packs_cli.py packs get "Karakeep"
```

If the name is ambiguous, the CLI lists matches and exits.

## Safety Guardrails

### Operations Requiring Confirmation

| Operation | Risk | Confirmation |
|-----------|------|--------------|
| **Delete Pack** | Irreversible | "Delete Pack 'X'? This cannot be undone." |

### No Confirmation Required

- **Create Pack**: Safe, reversible
- **List/Get Packs**: Read-only
- **Update Pack**: Reversible

## Error Handling

Common API errors:

| Code | Meaning | Resolution |
|------|---------|------------|
| `401` | Invalid token | Refresh CODA_API_TOKEN |
| `403` | Insufficient permissions | Ensure token has Pack management rights |
| `404` | Pack not found | Check Pack ID or name |
| `429` | Rate limited | Wait and retry (handled automatically) |

## References

- **Pack SDK Guides**: https://coda.io/packs/build/latest/guides/overview/
- **Pack SDK Quickstart**: https://coda.io/packs/build/latest/guides/quickstart/
- **Coda API Docs**: https://coda.io/developers/apis/v1
- **Pack SDK NPM**: https://www.npmjs.com/package/@codahq/packs-sdk

## Example: Karakeep Pack Shell

Created for testing:
- **Name**: Karakeep
- **ID**: 48093
- **Description**: Karakeep bookmark manager - save URLs, search, and organize with tags

**Next steps for full Pack development:**
1. Use Pack SDK CLI: `npx @codahq/packs-sdk init karakeep-pack`
2. Implement Karakeep API integration (see https://docs.karakeep.app/api/)
3. Build and upload: `npx @codahq/packs-sdk build && npx @codahq/packs-sdk upload`
