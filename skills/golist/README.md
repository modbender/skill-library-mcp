# OpenClaw integration assets

This folder contains an OpenClaw skill that makes GoList easy to try with OpenClaw.

GoList is a fast, simplistic app for creating and sharing grocery / shopping lists with other people. This skill gives new users a friendly, low-friction CLI flow to create a list, add items, and share it in seconds.

- `SKILL.md`: operational instructions and constraints for OpenClaw.
- `golist_cli.py`: Python CLI wrapper that executes list creation/join/share/read/item operations.

The skill uses the fixed API base URL `https://go-list.app/api`, generates/persists its own device UUID, generates UUIDs + timestamps for writes, and saves known lists by name/id so users can quickly jump back into the right shopping list.

## Quick usage
```bash
python3 apps/openclaw/golist_cli.py create-list "Weekend groceries"
python3 apps/openclaw/golist_cli.py upsert "milk" --quantity "2 L"
python3 apps/openclaw/golist_cli.py share
python3 apps/openclaw/golist_cli.py join <share-token-uuid>
python3 apps/openclaw/golist_cli.py lists
```
