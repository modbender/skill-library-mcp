---
name: capture-website
version: 1.0.0
description: Capture website screenshots from the command line. Use when user wants to take screenshots of any URL (Twitter, news sites, webpages) and send them via Discord/Feishu. Requires capture-website-cli to be installed (npm install -g capture-website-cli).
---

# Capture Website Screenshot

Take screenshots of any website and send to user.

## Quick Start

```bash
capture-website <URL> --output=/home/aaronz/.openclaw/workspace/screenshot.png
```

## Common Options

| Option | 说明 | 示例 |
|--------|------|------|
| `--output` | 输出文件路径 | `--output=/tmp/screenshot.png` |
| `--full-page` | 截取完整页面 | `--full-page` |
| `--width` | 页面宽度 | `--width=1280` |
| `--height` | 页面高度 | `--height=800` |
| `--type` | 图片格式 | `--type=png` 或 `--type=jpeg` |
| `--delay` | 加载后等待秒数 | `--delay=2` |
| `--wait-for-element` | 等待元素出现 | `--wait-for-element=.content` |
| `--dark-mode` | 暗色模式 | `--dark-mode` |
| `--emulate-device` | 模拟设备 | `--emulate-device="iPhone X"` |

## Workflow

1. Run capture-website command with URL
2. Save to workspace folder: `/home/aaronz/.openclaw/workspace/`
3. Send via message tool with filePath

## Example

```bash
capture-website https://x.com/elonmusk/status/2026052687423562228 \
  --output=/home/aaronz/.openclaw/workspace/tweet.png \
  --width=1280 \
  --height=800
```

Then send the file to user via Discord.

## Notes

- Requires: `npm install -g capture-website-cli`
- Default timeout: 60 seconds
- If screenshot fails, try adding `--delay=2` for slow-loading pages
