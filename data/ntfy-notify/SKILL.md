---
name: ntfy-notify
description: Send ntfy.sh notifications with curl, including advanced headers like title, priority, tags, click links, action buttons, and image attachments. Use when a user asks to send basic or rich ntfy notifications to a topic.
---

# ntfy-notify

Send notifications to ntfy topics.

## Author

- Name: 沉舟
- Website: https://chenzhou.dev

## Default topic

- `CaptainDragonflyBot-TopicTest001`

## Script

Use:

```bash
skills/ntfy-notify/scripts/send_ntfy.sh
```

### Parameters

- `--topic` topic name
- `--message` body text
- `--title` notification title
- `--priority` 1-5
- `--tags` comma-separated tags
- `--click` URL opened on tap
- `--actions` ntfy actions header string (supports buttons)
- `--attach` URL to an image/file shown as attachment
- `--filename` optional attachment filename hint

## Button format

Pass buttons via `--actions` as a variable string.

Example format:

```text
view, Open docs, https://docs.openclaw.ai; http, Trigger API, https://example.com/hook
```

## Examples

Basic (explicit message):

```bash
skills/ntfy-notify/scripts/send_ntfy.sh --message "你好，老爷"
```

Default message (omit --message, script auto-generates timestamp text):

```bash
skills/ntfy-notify/scripts/send_ntfy.sh
```

Rich notification with buttons and image:

```bash
skills/ntfy-notify/scripts/send_ntfy.sh \
  --title "Deploy finished" \
  --message "Build #42 is ready" \
  --priority 4 \
  --tags "rocket,white_check_mark" \
  --click "https://example.com/build/42" \
  --actions "view, Open build, https://example.com/build/42; view, Open docs, https://docs.openclaw.ai" \
  --attach "https://picsum.photos/1200/630"
```
