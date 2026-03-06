---
name: zotero
description: Zotero integration for both personal and Group libraries. search items (title/author/tags/year/fulltext/combined queries), create/update/delete items and metadata, add/edit item-level notes, perform bulk operations, and sync attachments (upload PDF or link URL). Trigger when user asks to search their Zotero, add or modify an item/note, upload attachments, or manage group libraries.
metadata:
  clawdbot:
    primaryEnv: ZOTERO_API_KEY
    requires:
      env:
        - ZOTERO_API_KEY
        - ZOTERO_USER_ID
        - ZOTERO_GROUP_ID
    config:
      requiredEnv:
        - ZOTERO_API_KEY
      example: "config = { env = { ZOTERO_API_KEY = \"/run/agenix/zotero-api-key\"; ZOTERO_USER_ID = \"12345\"; }; };"
---

# Zotero (overview)

This skill enables safe, repeatable programmatic access to a user's Zotero account (personal and group libraries) using Zotero API keys. It provides example scripts, a small Python client wrapper around pyzotero, a CLI example, and guidance for secure configuration and packaging as an AgentSkill.

## Triggers (must be present in description)

Activate this skill when the user asks things like: "search my Zotero for X", "add a note to item <id>", "upload PDF to Zotero", "create item in Group library <id>", or any request explicitly referencing Zotero library management.

## Preconditions

- The user provides a Zotero API key (developer key) and the target userID and/or groupID(s).
- **Credentials are resolved with the following priority** (first match is used):
  1. Command-line argument flags (e.g., `--user 12345` or `--group 99999`)
  2. Environment variables: `ZOTERO_API_KEY`, `ZOTERO_USER_ID`, `ZOTERO_GROUP_ID`
  
- `ZOTERO_API_KEY` is **required** (must be set as an environment variable or passed explicitly). Do NOT store raw keys in the repository.
- Implementation uses the pyzotero Python library by default. A Node.js variant can be added later if desired.
- If environment variables are set, no user input is needed—the skill executes automatically with the configured credentials.

## Supported features

- Search items by title, creator/author, tags, year, fulltext, or arbitrary field combinations; supports sorting and pagination.
- Create new items (journalArticle, book, conferencePaper, thesis, etc.) with standard Zotero metadata fields (title, creators, date, abstractNote, tags, publicationTitle, DOI, ISBN, extra, etc.).
- Update item metadata by sending a field-level patch/diff.
- Add / edit / delete item-level notes (Zotero item notes). PDF internal annotations/highlights are out-of-scope (advanced extension).
- Upload attachments (local PDF) and link attachments (external URLs) to items; include attachment metadata (title, contentType).
- Delete single items or perform batch operations (with explicit confirmation and dry-run options).
- List available groups and collections for the authenticated key.
- Logging of key operations to local logs (no API keys or full PDF contents in logs by default).

## Bundled resources (recommended)

- scripts/
  - pyzotero_client.py — lightweight wrapper around pyzotero with functions: auth, search_items, create_item, update_item, add_note, upload_attachment, delete_items, list_groups, list_collections.
  - cli.py — example CLI: zotero search|create|update|note|upload|delete — accepts JSON input or flags.
  - install.sh - installs pyzotero and dependencies in a virtual environment; includes instructions for setting ZOTERO_API_KEY.

- references/
  - zotero-api.md — concise Zotero Web API reference (endpoints used, rate limits, common error codes).
  - usage-examples.md — mapping from natural-language triggers to API actions and sample payloads.
  - security.md — recommendation to store API key in environment variables or a local secrets manager; do not commit keys.

- assets/
  - config.example.json — example configuration (no keys): { api_key_env: "ZOTERO_API_KEY", user_id: null, group_ids: [] }

## Design & implementation notes

- Default language: Python (pyzotero). All write operations require an explicit confirmation flag (e.g., --yes) to avoid accidental destructive changes.
- Batch delete defaults to a dry-run; a second confirmation is required to execute.
- Attachment upload flow: POST to /users/<userID or groupID>/items/<itemKey>/children with file data, then update parent-child relationships as required (see zotero-api.md).
- Error handling: API errors are translated into readable messages including suggested recovery actions (retry, check permissions, check rate limits).
- Logging: by default logs to ~/.config/zotero-skill/logs/operations.log. Logs omit ZOTERO_API_KEY and do not store full PDF contents.

## Example natural-language triggers

When environment variables (`ZOTERO_API_KEY`, `ZOTERO_USER_ID`, `ZOTERO_GROUP_ID`) are configured, the skill executes automatically without additional user prompts:

- "Search my Zotero for 'deep learning' and sort by year"
- "Add a note to item 12345: 'Expand methods section with ablation study'"
- "Upload /home/user/papers/foo.pdf as an attachment to item 67890"
- "Create a new journalArticle in Group library 99999 with title X, authors Y, DOI Z"

When using the CLI without `ZOTERO_USER_ID` or `ZOTERO_GROUP_ID` set, you can override via arguments:
- `python cli.py search --q "term" --user 12345` (overrides ZOTERO_USER_ID env var)

## Security

- Required environment variables (in the execution environment):

  ```bash
  export ZOTERO_API_KEY="<your_api_key_here>"
  export ZOTERO_USER_ID="<your_user_id>"         # For personal library (optional if using groups)
  export ZOTERO_GROUP_ID="<your_group_id>"       # For group library (optional if using personal)
  ```

- Do not commit real keys to source control. Prefer OS keyrings or secret managers for long-term storage.
- Once these environment variables are set, the skill will use them automatically without requiring user input.

## Notes for integrators

- If a JavaScript/Node implementation is required, add a node/ subfolder and provide equivalent wrappers and examples.
- Advanced feature: support parsing and syncing PDF annotations or highlights — requires downloading PDFs and using annotation parsers and is out-of-scope for initial release.
