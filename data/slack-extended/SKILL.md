---
name: slack-extended
description: Upload files, manage canvases, and manage bookmarks in Slack. Use when you need to share files, create/edit canvases, or add/organize link bookmarks in Slack channels. Complements the core slack skill which handles messages, reactions, and pins.
metadata: { "openclaw": { "emoji": "📎", "requires": { "config": ["channels.slack"] }, "credentials": { "source": "~/.openclaw/openclaw.json", "keys": ["channels.slack.botToken"], "scopes": ["files:write", "canvases:write", "bookmarks:write", "bookmarks:read"] } } }
---

# Slack Extended

Extends the core `slack` skill with file uploads and canvas management. Uses Python scripts that call the Slack API directly with the bot token from `~/.openclaw/openclaw.json`.

**Requires OAuth scopes:** `files:write`, `canvases:write` (add at api.slack.com if missing).

## File Upload

Upload a local file to a Slack channel:

```bash
python3 /mnt/openclaw/skills/slack-extended/scripts/slack_file_upload.py \
  --channel C123ABC \
  --file /path/to/file.png \
  --title "Q4 Report" \
  --message "Here's the latest report"
```

**Arguments:**
- `--channel` (required): Channel ID to share the file in
- `--file` (required): Path to the local file
- `--title`: Display title (defaults to filename)
- `--message`: Comment posted with the file

Returns JSON with `file_id`, `permalink`, and `channel`.

**Common patterns:**
- Share a generated chart: `--file /tmp/chart.png --title "Performance Chart"`
- Share a text file: `--file ./notes.txt --title "Meeting Notes"`
- Share with context: `--message "Backtest results for GEM v2" --file results.csv`

## Canvas Operations

Manage Slack canvases (collaborative documents):

### Create a canvas

```bash
python3 /mnt/openclaw/skills/slack-extended/scripts/slack_canvas.py create \
  --title "Sprint Notes" \
  --markdown "## Goals\n- Ship feature X\n- Fix bug Y"
```

### Edit a canvas

Append content:
```bash
python3 /mnt/openclaw/skills/slack-extended/scripts/slack_canvas.py edit \
  --canvas-id F07ABCD1234 \
  --operation insert_at_end \
  --markdown "## Update\nNew section added"
```

Replace a section:
```bash
python3 /mnt/openclaw/skills/slack-extended/scripts/slack_canvas.py edit \
  --canvas-id F07ABCD1234 \
  --section-id temp:C:abc123 \
  --operation replace \
  --markdown "## Revised Section\nUpdated content"
```

**Operations:** `insert_at_start`, `insert_at_end`, `insert_after`, `replace`, `delete`

### Look up sections

```bash
python3 /mnt/openclaw/skills/slack-extended/scripts/slack_canvas.py sections \
  --canvas-id F07ABCD1234
```

### Delete a canvas

```bash
python3 /mnt/openclaw/skills/slack-extended/scripts/slack_canvas.py delete \
  --canvas-id F07ABCD1234
```

### Set access

```bash
python3 /mnt/openclaw/skills/slack-extended/scripts/slack_canvas.py access \
  --canvas-id F07ABCD1234 \
  --channel C123ABC \
  --level edit
```

## Canvas Markdown

Canvases support: bold, italic, strikethrough, headings (h1-h3), bulleted/ordered lists, checklists, code blocks, code spans, links, tables (max 300 cells), blockquotes, dividers, emojis.

**Mentions:** `![](@USER_ID)` for users, `![](#CHANNEL_ID)` for channels.

## Bookmarks

Manage link bookmarks in the bookmark bar at the top of Slack channels.

**Limitation:** Slack API only supports **link** bookmarks. Folders are a UI-only feature and cannot be created via the API.

**Requires OAuth scopes:** `bookmarks:write`, `bookmarks:read`

### List bookmarks

```bash
python3 /mnt/openclaw/skills/slack-extended/scripts/slack_bookmark.py list \
  --channel C123ABC
```

### Add a link bookmark

```bash
python3 /mnt/openclaw/skills/slack-extended/scripts/slack_bookmark.py add \
  --channel C123ABC \
  --title "Design Docs" \
  --link "https://example.com" \
  --emoji ":link:"
```

### Edit a bookmark

```bash
python3 /mnt/openclaw/skills/slack-extended/scripts/slack_bookmark.py edit \
  --channel C123ABC \
  --bookmark-id Bk123 \
  --title "New Title"
```

### Remove a bookmark

```bash
python3 /mnt/openclaw/skills/slack-extended/scripts/slack_bookmark.py remove \
  --channel C123ABC \
  --bookmark-id Bk123
```

## Troubleshooting

- **`missing_scope` error**: Add the required scope (`files:write` or `canvases:write`) at api.slack.com, then reinstall the app to the workspace.
- **`channel_not_found`**: Use the channel ID (e.g. `C07ABC123`), not the channel name.
- **`not_authed`**: Bot token may have changed. Check `~/.openclaw/openclaw.json`.
- **Canvas edit fails**: Look up sections first to get valid `section_id` values.
- **`missing_scope` for bookmarks**: Add `bookmarks:write` and `bookmarks:read` at api.slack.com, then reinstall.
- **Folders not supported**: Slack API does not support creating folders — only link bookmarks. Folders can only be created manually in the Slack UI.
