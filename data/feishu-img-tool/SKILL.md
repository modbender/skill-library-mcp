---
name: feishu-img-tool
description: |
  Feishu image upload and send tool. Send images to Feishu chats by uploading first then sending with image_key.
  Usage: `node feishu-image-tool.js send --target <open_id> --file <path>`
---

# Feishu Image Tool

Tool `feishu_image` for uploading and sending images to Feishu chats.

## How It Works

Feishu requires a two-step process to send images:

1. **Upload Image** - Call `/open-apis/im/v1/images` to upload the image and get `image_key`
2. **Send Message** - Call `/open-apis/im/v1/messages` with `msg_type: "image"` and the `image_key`

## Actions

### Upload and Send Image

```json
{
  "action": "send",
  "target": "ou_xxx",  // User open_id or chat_id
  "file_path": "/path/to/image.png",
  "message": "Optional caption"
}
```

**Parameters:**
- `action`: `"send"`
- `target`: Feishu user open_id or chat_id (omit for current conversation)
- `file_path`: Path to the image file on the server
- `message`: Optional text message to send with the image

**Returns:**
- `success`: boolean
- `image_key`: The uploaded image key
- `message_id`: The sent message ID

### Upload Image Only

```json
{
  "action": "upload",
  "file_path": "/path/to/image.png"
}
```

Returns `image_key` for later use.

### Send Image with Key

```json
{
  "action": "send_with_key",
  "target": "ou_xxx",
  "image_key": "img_v3_xxx"
}
```

## Image Limits

- **Max size**: 10 MB
- **Supported formats**: JPG, JPEG, PNG, WEBP, GIF, BMP, ICO
- **Resolution**: 
  - GIF: max 2000 x 2000 pixels
  - Other formats: max 12000 x 12000 pixels

## Configuration

### Feishu App Credentials

Required credentials (in order of priority):
1. Environment variables: `FEISHU_APP_ID`, `FEISHU_APP_SECRET`
2. Config file: `~/.feishu-image/config.json`

```bash
# Method 1: Environment variables
export FEISHU_APP_ID="cli_xxx"
export FEISHU_APP_SECRET="xxx"

# Method 2: Config file (~/.feishu-image/config.json)
{
  "appId": "cli_xxx",
  "appSecret": "xxx"
}
```

### Required Permissions

- `im:message` - Send messages as bot
- `im:image` - Upload images

## Permissions

- `im:message` - Send messages as bot
- `im:image` - Upload images

## Example Usage

### Send stock chart to user

```json
{
  "action": "send",
  "target": "ou_xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx",
  "file_path": "/tmp/stock-report.png",
  "message": "📊 今日股票报告"
}
```

### Send to current conversation (omit target)

```json
{
  "action": "send",
  "file_path": "/tmp/chart.png"
}
```

## Implementation Notes

- Uses Feishu SDK `@larksuiteoapi/node-sdk`
- `client.im.image.create()` for upload
- `client.im.message.create()` for sending
- `image_key` is permanent and can be reused by the same app
