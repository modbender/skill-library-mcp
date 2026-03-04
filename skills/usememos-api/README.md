# UseMemos

An [OpenClaw](https://openclaw.ai) skill for interacting with [UseMemos](https://usememos.com) — a lightweight, self-hosted memo hub.

Create, search, list memos and upload attachments through your AI agent.

## Installation

### From ClawHub

```bash
clawhub install usememos
```

### Manual

Clone this repo into your OpenClaw skills directory:

```bash
git clone https://github.com/minstn/usememos.git ~/.openclaw/skills/usememos
```

## Setup

1. Copy the example environment file and fill in your values:

```bash
cp .env.example .env
```

2. Edit `.env` with your UseMemos instance URL and access token:

```
USEMEMOS_URL=http://localhost:5230
USEMEMOS_TOKEN=your_access_token_here
```

To get an access token, go to **Settings > My Account** in your UseMemos instance.

## Usage

### Create a memo

```bash
python3 scripts/create_memo.py "Buy milk and eggs #shopping"
# Created memo [3UZ7uBbHsLEAwdYE5HKhjd]
```

Visibility options: `PRIVATE` (default), `PROTECTED`, `PUBLIC`

```bash
python3 scripts/create_memo.py "Public announcement" PUBLIC
```

### List recent memos

```bash
python3 scripts/list_memos.py 5
# [abc123] Buy milk and eggs #shopping...
# [def456] Meeting notes from standup #work...
```

### Search memos

```bash
python3 scripts/search_memos.py "project idea" 10
# [xyz789] New project idea: build a CLI for...
```

### Attachments

**Upload a standalone attachment:**

```bash
python3 scripts/upload_attachment.py photo.jpg "sale_photo.jpg" "image/jpeg"
# Uploaded [abc123] sale_photo.jpg (45678 bytes)
```

**Create a memo with an attachment (two-step):**

```bash
# 1. Create the memo
python3 scripts/create_memo.py "Sale: Charger for 240 CHF #income"
# Created memo [memo123]

# 2. Upload and link in one shot
python3 scripts/upload_and_link_attachment.py memo123 charger.jpg
# Uploaded [attachments/att456] (45678 bytes)
# Linked to memo [memo123]
```

**Attach multiple files to the same memo:**

```bash
python3 scripts/create_memo.py "Bike parts lot — 3 photos #inventory"
# Created memo [memo789]

python3 scripts/upload_and_link_attachment.py memo789 front.jpg
python3 scripts/upload_and_link_attachment.py memo789 side.jpg
python3 scripts/upload_and_link_attachment.py memo789 detail.jpg
```

**Upload a non-image file (PDF, text, etc.):**

```bash
python3 scripts/upload_attachment.py invoice.pdf "invoice_feb.pdf" "application/pdf"
python3 scripts/upload_and_link_attachment.py memo123 notes.txt "meeting_notes.txt" "text/plain"
```

**Upload first, link later:**

```bash
# Upload without linking to any memo
python3 scripts/upload_attachment.py receipt.jpg
# Uploaded [att999] receipt.jpg (12345 bytes)

# Link it to a memo later using curl
curl -X PATCH "${USEMEMOS_URL}/api/v1/memos/<memo_id>" \
  -H "Authorization: Bearer ${USEMEMOS_TOKEN}" \
  -H "Content-Type: application/json" \
  -d '{"attachments": [{"name": "attachments/att999", "filename": "receipt.jpg", "type": "image/jpeg"}]}'
```

## Scripts

| Script | Arguments | Description |
|--------|-----------|-------------|
| `create_memo.py` | `<content> [visibility]` | Create a memo |
| `list_memos.py` | `[limit] [tag]` | List recent memos |
| `search_memos.py` | `<query> [limit]` | Search memos by content |
| `upload_attachment.py` | `<filepath> [filename] [type]` | Upload a file attachment |
| `upload_and_link_attachment.py` | `<memo_id> <filepath> [filename] [type]` | Upload and link to a memo |

## Requirements

- Python 3.6+ (no external dependencies — stdlib only)
- A running [UseMemos](https://usememos.com) instance

## API Reference

See [references/api.md](references/api.md) for the UseMemos v1 API endpoints used by this skill.

## License

MIT
