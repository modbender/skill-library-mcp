---
name: GoList Shared-List Manager (OpenClaw Skill)
description: Enable OpenClaw to manage GoList through a simple,
  beginner-friendly CLI wrapper around the backend API.
---

# GoList Shared-List Manager (OpenClaw Skill)

## Purpose
Enable OpenClaw to manage GoList through a simple, beginner-friendly CLI wrapper around the backend API.

GoList is a simplistic app for creating and sharing grocery / shopping lists. This skill is designed to make first-time usage feel fast and approachable: create a list, add items, share with others, and switch between saved lists with minimal setup.

This skill supports:
- creating new lists,
- joining shared lists via share token,
- saving known lists (name + id) and switching between them,
- generating share tokens for users,
- reading lists,
- upserting items,
- soft-deleting items.

## Hard constraints
1. API base URL is fixed to `https://go-list.app/api` and must never be overridden.
2. OpenClaw must generate its own random device UUID and persist it for reuse.
3. Every request must include the `X-Device-Id` header.
4. For item writes, OpenClaw must only set:
   - `name` (required),
   - `deleted` (optional, defaults to `false`),
   - `quantityOrUnit` (optional).
5. OpenClaw must generate all item UUIDs and timestamps in the Python CLI (never require the agent to provide them).
6. Immediately after creating a new list, OpenClaw must always generate a share token and send the share URL to the user without being asked.
7. When talking to the user, OpenClaw must never refer to lists by ID; always use list names (use the stored name↔id mapping internally).
8. For item upserts, if the user does not explicitly provide a quantity/unit, OpenClaw must omit `quantityOrUnit`.

## Python CLI tool
Use `apps/openclaw/golist_cli.py` as the operational API wrapper for this skill.

### CLI guarantees
- Fixed API base URL: `https://go-list.app/api`.
- Generates and persists device id when missing.
- Generates list IDs and item IDs when creating entities.
- Generates item `updatedAt` timestamps on write operations.
- Automatically sends `X-Device-Id` on every request.
- Persists known lists with friendly names and IDs, and tracks an active list.

### CLI state and environment
Optional environment:
- `GOLIST_DEVICE_ID` (override persisted device id)
- `OPENCLAW_STATE_FILE` (custom path for persisted JSON state)
- `GOLIST_SHARE_TOKEN` (optional token source for `bootstrap --share-token`)

Persisted state file (default):
- `~/.openclaw_golist_state.json` with:
  - `device_id`
  - `active_list_id`
  - `known_lists[]` containing `id` + `name`

## Core flows
### 1) Create a new list
```bash
python3 apps/openclaw/golist_cli.py create-list "Weekend groceries"
python3 apps/openclaw/golist_cli.py share
```
Creates a list with a generated UUID, stores it in known lists, sets it as active, then immediately creates a share token and returns the share URL to the user.

### 2) Share a list with a user
```bash
python3 apps/openclaw/golist_cli.py share
```
Creates a share token for the active list and returns both token + share URL.

### 3) Join an existing list via share token
```bash
python3 apps/openclaw/golist_cli.py join <share-token-uuid>
```
Redeems the token, fetches the real list name from the API, stores that name+id mapping, and sets it active.

### 4) Switch/access saved lists
```bash
python3 apps/openclaw/golist_cli.py lists
python3 apps/openclaw/golist_cli.py use-list "Weekend groceries"
python3 apps/openclaw/golist_cli.py show
```

### 5) Item writes (restricted fields)
```bash
python3 apps/openclaw/golist_cli.py upsert "milk" [--quantity "2 L"] [--deleted]
python3 apps/openclaw/golist_cli.py delete "milk"
```

## Intent mapping for OpenClaw
- “create a new list called X” → `create-list "X"`
- After `create-list`, always run `share` and send the URL/token to the user.
- “share this list with me” → `share`
- “join this token” → `join <token>`
- “show my lists” → `lists`
- “switch to list X” → `use-list "X"`
- “show current list” → `show`
- “add X (qty)” → `upsert "X" [--quantity "..."]`
- “remove X” → `delete "X"`

## Safety behavior
- If device id is missing, generate and persist it before any API call.
- If no active list is set, require `create-list` or `join` first.
- If token redemption fails, return a clear auth/share error.
- In user-facing responses, refer to lists by name only (never by raw ID).
- Do not invent item quantities; only send `--quantity` when the user asked for one.
- Never send item metadata fields outside `name`, `deleted`, and optional `quantityOrUnit`.
