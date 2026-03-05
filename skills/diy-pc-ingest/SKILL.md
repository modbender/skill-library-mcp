---
name: diy-pc-ingest
description: Ingest pasted PC parts purchase/config text (Discord message receipts, bullet lists) into Notion DIY_PC tables (PCConfig, ストレージ, エンクロージャー, PCInput). Use when the user pastes raw purchase logs/spec notes and wants the AI to classify, enrich via web search, ask follow-up questions for unknowns, and then upsert rows into the correct Notion data sources using the 2025-09-03 data_sources API.
metadata: {"openclaw":{"requires":{"bins":["node"],"env":["NOTION_API_KEY"]},"optionalEnv":["NOTION_TOKEN","NOTION_API_KEY_FILE","NOTION_VERSION","DIY_PC_INGEST_CONFIG","DIY_PC_INGEST_BOOTSTRAP"],"primaryEnv":"NOTION_API_KEY","dependsOnSkills":["notion-api-automation"],"localReads":["~/.config/diy-pc-ingest/config.json","~/.config/notion/api_key"],"localWrites":["~/.config/diy-pc-ingest/config.json (only when bootstrap enabled)"],"network":["notion-api","optional:web_search/web_fetch"]}}
---

# diy-pc-ingest

## Setup (required)

This skill is intended to be shared. Do **not** hardcode your Notion IDs or token in the skill.

1) Copy the example config:
- `skills/diy-pc-ingest/references/config.example.json` → `~/.config/diy-pc-ingest/config.json`
- Auto-bootstrap is disabled by default. Enable only when explicitly needed with `DIY_PC_INGEST_BOOTSTRAP=1`.

2) Fill in your Notion targets (IDs):
- `notion.targets.*.data_source_id` (for schema/query)
- `notion.targets.*.database_id` (for creating pages)

3) Provide Notion auth for `notion-api-automation` (`notionctl`):
- env: `NOTION_API_KEY` (recommended)
- or `~/.config/notion/api_key`

Notes:
- This skill uses Notion-Version `2025-09-03` by default.
- Targets are read at runtime from config; see `references/config.example.json`.

## Data flow disclosure

- Local input: pasted receipts/spec notes are parsed locally.
- External enrichment (optional): `web_search`/`web_fetch` may send partial product text to external web providers.
- Notion write path: records are queried/upserted via `notion-api-automation/scripts/notionctl.mjs`.
- Local config: `~/.config/diy-pc-ingest/config.json` is read; write occurs only when bootstrap is explicitly enabled.

Security rules:
- If user does not want external enrichment, skip `web_search`/`web_fetch` and proceed with local extraction only.
- Use minimal-scope Notion integration permissions (only target DIY_PC data sources).

## Canonical Notion targets

Use **data_sources** endpoints for schema/query, and **pages** endpoint for row creation.

(IDs are intentionally not included in this public skill. They live in your local config.)

## Workflow (A: user pastes raw text)

1) **Read the pasted text** and decide target table per item:
   - **エンクロージャー**: USB/RAID/HDDケース/ドック、ベイ数、JAN/型番、"安全な取り外し"表示名。
   - **ストレージ**: HDD/SSD/NVMe/SATA/容量/シリアル/健康状態。
   - **PCConfig**: CPU/GPU/RAM/PSU/MB/ケース/冷却/NIC/キャプチャ等。

2) **Extract fields** (best-effort). Prefer Japanese column names as they exist in each table.

3) **Enrich specs using web_search/web_fetch** when it reduces user work (e.g., bay count, interface, capacity, form factor). Keep it minimal; don't overfill.

4) **Ask follow-up questions** only for fields needed to avoid ambiguity or bad joins.
   - **ストレージ**: Serial missing → ask for serial (or confirm creating as "暫定/シリアル不明").
   - **エンクロージャー**: ベイ数 or USB/Thunderbolt/LAN unclear → ask.
   - **PCConfig**: Identifier/型番 missing but needed to match existing row → ask.
- If a key collides with multiple rows, do not write; ask user.

5) **Search existing records in Notion** using `scripts/notion_apply_records.js` (auto-discovery mode):
   - Provide JSONL records (one per item) on stdin.
   - Script will:
     - find an existing row by key (see below)
     - report what would be created/updated/skipped without making changes
     - **Do not write anything** (no create/update operations)
   - Use this to preview results before actual upsert.

6) **Review search results** and confirm with user:
   - Show what would be created/updated/skipped
   - Ask for confirmation before proceeding to actual upsert

7) **Upsert into Notion** using `scripts/notion_apply_records.js`:
   - Provide JSONL records (one per item) on stdin.
   - Script will:
     - find an existing row by key (see below)
     - patch only missing fields unless `overwrite=true`
     - otherwise create a new row

8) Report results (created/updated/skipped) and link any created rows.
3
## Upsert keys (rules)

- **ストレージ**: `シリアル` (exact) is the primary key. If the existing row was created without serial, allow a safe fallback match by title + (optional) `購入日`/`価格(円)` to support post-fill of serial/health/scan-date.
- **エンクロージャー**: `取り外し表示名` (exact) else title/name.
- **PCConfig**: `(Name + Purchase Date)` を複合キーとして扱う（exact）。重複ヒット時は書き込まず質問。
- If a key collides with multiple rows, do not write; ask user.

## JSONL input format for the apply script

Each line is a JSON object:

```json
{"target":"enclosure","title":"RATOC RS-EC32-R5G","properties":{"種別":"USBケース","接続":"USB","ベイ数":2,"普段つないでるPC":"RECRYZEN","購入日":"2026-01-18","購入店":"PCワンズ","価格(円)":8977,"取り外し表示名":"RS-EC32-R5G","メモ":"JAN: 4949090752191"}}
```

Optional control fields (for cleanup / manual fixes):
- `page_id` (or `id`): update this Notion page directly (bypasses upsert matching)
- `archive: true`: archive the page (useful for de-dup)
- `overwrite: true`: allow overwriting existing values (including clearing with null)

Optional behavior flags:
- `mirror_to_pcconfig: true` (only for `target=storage`): also create/update a `pcconfig` row for the installed component.
  - requires: `現在の接続先PC`, `購入日`, `Name`

Targets: `enclosure | storage | pcconfig | pcinput`

Property value encoding:
- select/status: string name
- rich_text: string
- number: number
- date: `YYYY-MM-DD`
- checkbox: boolean
- relation: array of page_ids (advanced; avoid unless needed)

## Notes

- Always use Notion-Version `2025-09-03`.
- Prefer `POST /v1/data_sources/{id}/query` over `/databases/{id}/query`.
- Relation schema updates require `relation.data_source_id` (not database_id).


## Note (implementation)
- JS implementation is the default: `scripts/notion_apply_records.js`
- Legacy Python implementation is kept for reference: `scripts/_deprecated/notion_apply_records.py`


## Notion tooling (recommended)
- Install `notion-api-automation` via ClawHub for Notion API debugging: `clawhub install notion-api-automation`
- This skill does not depend on `skills/notionkit/*`.
- Primary ingestion path is `scripts/notion_apply_records.js`; use `skills/notion-api-automation/scripts/notionctl.mjs` for diagnostics/manual API operations.