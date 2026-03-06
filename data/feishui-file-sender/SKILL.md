---
name: feishu-file-sender
description: Send files via Feishu channel using message tool with filePath parameter.
---

# Feishu File Sender

Send binary files (ZIP, PDF, images, etc.) to Feishu groups or users.

## Prerequisites

- OpenClaw configured with Feishu channel
- Target chat ID (group or user)

## Step 1: Package the Skill/File

```bash
cd /root/.openclaw/workspace/skills
zip -r /tmp/skill_name.zip skill_folder/
```

**Key:** Use relative path inside the zip, not absolute path.

## Step 2: Send via Feishu

```python
message(
    action="send",
    channel="feishu",
    filePath="/tmp/skill_name.zip",
    message="📦 Skill Name",
    target="oc_xxxxxxxxxxxx"  # chat ID
)
```

## Parameters

| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| action | string | Yes | "send" |
| channel | string | Yes | "feishu" |
| filePath | string | Yes | Absolute path to file |
| message | string | Yes | Caption text |
| target | string | Yes | Chat ID (oc_xxx for groups, user ID for DM) |

## Common Issues

1. **File too large**: Feishu limits apply (~20MB for most)
2. **Wrong path**: Use absolute path `/tmp/xxx.zip`
3. **Relative path in zip**: Package from parent dir, e.g., `zip -r /tmp/out.zip folder/`

## Example: Send a Skill

```bash
# Package
cd /root/.openclaw/workspace/skills
zip -r /tmp/weather.zip weather/

# Send
message(action="send", channel="feishu", filePath="/tmp/weather.zip", message="📦 weather skill", target="oc_group_id")
```
