# Notion IDs (DIY_PC) - LOCAL ONLY

⚠️ Do not publish this file with real IDs.

Copy `references/config.example.json` to `~/.config/diy-pc-ingest/config.json` and put IDs there.

How to find IDs:
- Create your Notion tables first (PCConfig/PCInput/ストレージ/エンクロージャー)
- Use Notion API `POST /v1/search` with your integration token to locate each table
- Then read the table's `data_source_id` (query/schema) and `database_id` (create page parent)

Recommended:
- Keep IDs in a local-only config file outside your repo.
- Keep your Notion token in `NOTION_API_KEY` env or a secret manager.
