---
name: telegram-chat-to-image
description: "Convert Telegram chat exports into a long screenshot-style image. Supports Telegram Desktop JSON exports with bubble-style message rendering, avatars, timestamps, and proper text wrapping. Use when user wants to generate a visual image of Telegram conversations, create chat screenshots, or share conversation history as a single long image."
---

# Telegram Chat to Image

Converts Telegram chat exports into a long screenshot-style image with iOS-style bubble interface.

## Changelog

### v1.1.0 (2026-03-01)
- **修复**: 中文长文本换行问题 — 现在逐字符检查宽度，正确换行
- **修复**: 发件人显示问题 — 正确区分"我"(蓝色气泡)和其他人(灰色气泡+头像)
- **新增**: 显示每条消息的发件人名称

### v1.0.0
- 初始版本

## Prerequisites

\`\`\`bash
pip install Pillow
\`\`\`

## Usage

### CLI

\`\`\`bash
# Basic usage
python3 scripts/chat_to_image.py --input result.json --output chat.png

# Limit messages
python3 scripts/chat_to_image.py --input result.json --limit 50 --output chat.png

# Custom font (for Chinese support)
python3 scripts/chat_to_image.py --input result.json --font /System/Library/Fonts/PingFang.ttc
\`\`\`

### Getting Telegram Export

1. Open Telegram Desktop
2. Go to the chat you want to export
3. Click menu and Export chat history
4. Select JSON format
5. Choose messages and export

### Input Format

Expects Telegram Desktop JSON export format with messages array containing id, type, date, from, from_id, and text fields.

## Output

Generates a PNG image with:
- 800px width
- iOS-style bubble chat interface
- Gray bubbles for others, blue for user messages
- Circular avatars with initials
- Timestamps (HH:MM format)
- Proper text wrapping for long messages

## Limitations

- Images, stickers, and media are not rendered
- Reply threads are not visually indicated
- Only plain text messages are fully supported
- Large exports may create very tall images

## Customization

Edit scripts/chat_to_image.py to adjust:
- WIDTH: Image width (default 800)
- MY_BUBBLE_COLOR: Your message color
- OTHER_BUBBLE_COLOR: Others message color
- FONT_SIZE, BUBBLE_PADDING: Layout spacing
