---
name: notion-cli-agent
description: notion-cli Interact with your Notion workspace via the notion-cli.
---

notion-cli
Interact with your Notion workspace via the notion-cli.

A production-grade CLI for the Notion API that supports searching, creating and managing pages, databases, blocks, users, and comments with multiple output formats (JSON, table, CSV).

Install
Clone and install the CLI:
```
git clone https://github.com/FroeMic/notion-cli
cd notion-cli
npm install
npm run build
npm link
```
Set `NOTION_API_KEY` environment variable:
1. Create an integration at https://www.notion.so/profile/integrations
2. Copy the Internal Integration Secret (starts with `ntn_` or `secret_`)
3. Share any pages/databases you want to access with the integration
- Recommended: Add to `~/.claude/.env` for Claude Code
- Alternative: Add to `~/.bashrc` or `~/.zshrc`: `export NOTION_API_KEY="your-api-key"`

Optional: Set `NOTION_DEBUG=true` for verbose request/response logging.

Repository: https://github.com/FroeMic/notion-cli

Commands
Search across your workspace:
```
notion search [query]                                  # Search pages, databases, and data sources
notion search [query] --filter page                    # Search only pages
notion search [query] --filter database                # Search only databases
notion search [query] --sort ascending                 # Sort by last edited time
```

Work with pages:
```
notion pages get <page-id>                             # Get page details
notion pages create --parent <id> --title <text>       # Create a new page
notion pages update <page-id> --properties <json>      # Update page properties
notion pages archive <page-id>                         # Archive a page
notion pages restore <page-id>                         # Restore an archived page
notion pages property <page-id> <property-id>          # Get a specific property value
```

Work with databases:
```
notion databases get <database-id>                     # Get database schema
notion databases create --parent <id> --title <text>   # Create a database
notion databases update <database-id> --title <text>   # Update database metadata
notion databases query <data-source-id>                # Query records in a data source
notion databases query <id> --filter <json>            # Query with filters
notion databases query <id> --sort <json>              # Query with sorting
```

Work with blocks (page content):
```
notion blocks get <block-id>                           # Get a block
notion blocks children <block-id>                      # List child blocks
notion blocks append <block-id> --content <json>       # Append new blocks
notion blocks update <block-id> --content <json>       # Update a block
notion blocks delete <block-id>                        # Delete a block
```

Work with users:
```
notion users list                                      # List workspace members
notion users get <user-id>                             # Get user details
notion users me                                        # Get the authenticated bot user
```

Work with comments:
```
notion comments list --block <block-id>                # List comments on a block
notion comments create --page <page-id> --content <text>  # Add a comment to a page
```

Global options (available on all commands):
```
--api-key <key>                                        # Override NOTION_API_KEY env var
-f, --format <fmt>                                     # Output format: json (default), table, csv
--limit <n>                                            # Max results to return
--cursor <cursor>                                      # Pagination cursor
```

Key Concepts
| Concept     | Purpose                              | Example                                  |
|-------------|--------------------------------------|------------------------------------------|
| Pages       | Individual Notion pages              | A meeting note, a project brief           |
| Databases   | Structured collections of pages      | A task tracker, a CRM table               |
| Data Sources| Individual tables within a database  | A specific view/table in a database       |
| Blocks      | Content elements within a page       | Paragraphs, headings, lists, code blocks  |
| Properties  | Typed fields on database pages       | Title, status, date, select, relation     |
| Users       | Workspace members and integrations   | Team members, bot integrations            |
| Comments    | Discussion threads on pages/blocks   | Feedback, review notes                    |

API Reference
- Base URL: `https://api.notion.com/v1`
- API Version: `2022-06-28`
- Auth: `Authorization: Bearer $NOTION_API_KEY`
- Rate Limits: Automatic retry with exponential backoff (up to 3 retries)

Common API Operations
Search for a page:
```
curl -X POST https://api.notion.com/v1/search \
  -H "Authorization: Bearer $NOTION_API_KEY" \
  -H "Notion-Version: 2022-06-28" \
  -H "Content-Type: application/json" \
  -d '{"query": "Meeting Notes", "filter": {"value": "page", "property": "object"}}'
```

Query a database with filters:
```
curl -X POST https://api.notion.com/v1/databases/<database-id>/query \
  -H "Authorization: Bearer $NOTION_API_KEY" \
  -H "Notion-Version: 2022-06-28" \
  -H "Content-Type: application/json" \
  -d '{"filter": {"property": "Status", "status": {"equals": "In Progress"}}}'
```

Create a page in a database:
```
curl -X POST https://api.notion.com/v1/pages \
  -H "Authorization: Bearer $NOTION_API_KEY" \
  -H "Notion-Version: 2022-06-28" \
  -H "Content-Type: application/json" \
  -d '{"parent": {"database_id": "<database-id>"}, "properties": {"Name": {"title": [{"text": {"content": "New Task"}}]}}}'
```

Append content to a page:
```
curl -X PATCH https://api.notion.com/v1/blocks/<block-id>/children \
  -H "Authorization: Bearer $NOTION_API_KEY" \
  -H "Notion-Version: 2022-06-28" \
  -H "Content-Type: application/json" \
  -d '{"children": [{"object": "block", "type": "paragraph", "paragraph": {"rich_text": [{"type": "text", "text": {"content": "Hello world"}}]}}]}'
```

Notes
- The integration must be explicitly shared with each page or database you want to access (via Notion UI: ... menu > Connections > Add your integration).
- Pages can accept IDs as UUIDs or Notion URLs — the CLI will parse both formats.
- All list endpoints support cursor-based pagination via `--limit` and `--cursor`.
- Output format can be set to `json` (default), `table`, or `csv` with the `-f` flag.
- Property types include: title, rich_text, number, select, multi_select, status, date, people, files, checkbox, url, email, phone_number, relation, rollup, formula, and timestamp fields.

Files
1 total
- SKILL.md (this file)
