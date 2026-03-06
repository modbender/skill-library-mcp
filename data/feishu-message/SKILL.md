---
name: Feishu Message Skill
description: A unified toolkit for Feishu messaging operations, providing a
  single CLI entry point for common tasks.
---

# Feishu Message Skill

A unified toolkit for Feishu messaging operations, providing a single CLI entry point for common tasks.

## Usage

Use the unified CLI via `index.js`:
```bash
node skills/feishu-message/index.js <command> [options]
```

## Commands

### 1. Get Message (`get`)
Fetch message content by ID. Supports recursive fetching for merged messages.
```bash
node skills/feishu-message/index.js get <message_id> [--raw] [--recursive]
```
Example:
```bash
node skills/feishu-message/index.js get om_12345 --recursive
```

### 2. Send Audio (`send-audio`)
Send an audio file as a voice bubble.
```bash
node skills/feishu-message/index.js send-audio --target <id> --file <path> [--duration <ms>]
```
- `--target`: User OpenID (`ou_`) or ChatID (`oc_`).
- `--file`: Path to audio file (mp3/wav/etc).
- `--duration`: (Optional) Duration in ms.

### 3. Create Group Chat (`create-chat`)
Create a new group chat with specified users.
```bash
node skills/feishu-message/index.js create-chat --name "Project Alpha" --users "ou_1" "ou_2" --desc "Description"
```

### 4. List Pins (`list-pins`)
List pinned messages in a chat.
```bash
node skills/feishu-message/index.js list-pins <chat_id>
```

## Legacy Scripts
Standalone scripts are still available for backward compatibility:
- `get.js`
- `send-audio.js`
- `create_chat.js`
- `list_pins_v2.js`

## Dependencies
- axios
- form-data
- music-metadata
- commander
