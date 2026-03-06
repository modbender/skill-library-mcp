# Browser Relay for Xiaohongshu

[![GitHub](https://img.shields.io/badge/GitHub-browser--relay--xiaohongshu-blue)](https://github.com/esojourn/browser-relay-xiaohongshu)

Lightweight HTTP relay that lets AI assistants control a local Chromium browser via Chrome DevTools Protocol (CDP), bypassing data center IP blocks from Chinese platforms like Xiaohongshu (小红书).

## Why This Exists

AI assistants typically run on cloud servers. Chinese platforms aggressively block data center IPs. This relay bridges the gap — the AI sends HTTP commands to a local relay server, which forwards them to your Chromium via CDP. All web requests originate from your local IP.

## Architecture

```
AI Agent → HTTP (port 18792) → relay.py → CDP WebSocket (port 9222) → Local Chromium
```

## Features

- **Full browser control**: navigate, click, type, scroll, screenshot, JS execution
- **Tab management**: create, switch, close tabs
- **DOM queries**: find elements by CSS selector, get coordinates
- **Screenshot to Telegram**: capture screenshots and send directly to Telegram via Bot API
- **Auth token**: auto-generated per session for security
- **Chromium auto-launch**: supports launching Chromium with correct flags

## Quick Start

### 1. Launch Chromium with remote debugging

```bash
chromium --remote-debugging-port=9222 --remote-allow-origins=*
```

> **Important**: `--remote-allow-origins=*` is required, otherwise WebSocket connections will be rejected.

### 2. Install dependencies and start relay

```bash
cd browser-relay
python3 -m venv venv && source venv/bin/activate
pip install -r requirements.txt
python3 relay.py
```

Or use the launcher script:

```bash
bash start.sh          # start
bash start.sh restart  # restart
bash start.sh stop     # stop
```

### 3. Use the API

All endpoints require `Authorization: Bearer <token>` header. The token is auto-generated at startup and saved to `/tmp/browser-relay-token`.

```bash
TOKEN=$(cat /tmp/browser-relay-token)

# Health check
curl -s -H "Authorization: Bearer $TOKEN" http://localhost:18792/health

# List browser tabs
curl -s -H "Authorization: Bearer $TOKEN" http://localhost:18792/tabs

# Navigate
curl -s -H "Authorization: Bearer $TOKEN" -H "Content-Type: application/json" \
  -d '{"url":"https://www.xiaohongshu.com"}' http://localhost:18792/navigate

# Screenshot
curl -s -H "Authorization: Bearer $TOKEN" -H "Content-Type: application/json" \
  -d '{"quality":80}' http://localhost:18792/screenshot

# Click at coordinates
curl -s -H "Authorization: Bearer $TOKEN" -H "Content-Type: application/json" \
  -d '{"x":400,"y":300}' http://localhost:18792/click

# Click by CSS selector
curl -s -H "Authorization: Bearer $TOKEN" -H "Content-Type: application/json" \
  -d '{"selector":"button.submit"}' http://localhost:18792/click

# Type text
curl -s -H "Authorization: Bearer $TOKEN" -H "Content-Type: application/json" \
  -d '{"text":"hello"}' http://localhost:18792/type

# Send key
curl -s -H "Authorization: Bearer $TOKEN" -H "Content-Type: application/json" \
  -d '{"key":"Enter"}' http://localhost:18792/keypress

# Execute JavaScript
curl -s -H "Authorization: Bearer $TOKEN" -H "Content-Type: application/json" \
  -d '{"expression":"document.title"}' http://localhost:18792/evaluate

# Scroll
curl -s -H "Authorization: Bearer $TOKEN" -H "Content-Type: application/json" \
  -d '{"y":300}' http://localhost:18792/scroll

# Wait for element
curl -s -H "Authorization: Bearer $TOKEN" -H "Content-Type: application/json" \
  -d '{"selector":".target","timeout":5000}' http://localhost:18792/wait
```

### Screenshot to Telegram

When interacting via Telegram, screenshots can be sent directly to the chat:

```bash
TOKEN=$(cat /tmp/browser-relay-token)

# 1. Capture screenshot
curl -s -H "Authorization: Bearer $TOKEN" -H "Content-Type: application/json" \
  -d '{"quality":80}' http://localhost:18792/screenshot \
  | python3 -c "
import sys, json, base64
data = json.load(sys.stdin)
if data.get('ok'):
    with open('/tmp/relay_screenshot.png', 'wb') as f:
        f.write(base64.b64decode(data['data']))
    print('ok')
"

# 2. Send to Telegram
TG_BOT_TOKEN="your-bot-token"
TG_CHAT_ID="your-chat-id"
curl -s -X POST "https://api.telegram.org/bot${TG_BOT_TOKEN}/sendPhoto" \
  -F "chat_id=${TG_CHAT_ID}" \
  -F "photo=@/tmp/relay_screenshot.png"
```

### Tab Management

```bash
# New tab
curl -s -H "Authorization: Bearer $TOKEN" -H "Content-Type: application/json" \
  -d '{"url":"https://example.com"}' http://localhost:18792/tab/new

# Switch tab
curl -s -H "Authorization: Bearer $TOKEN" -H "Content-Type: application/json" \
  -d '{"tab_id":"xxx"}' http://localhost:18792/tab/activate

# Close tab
curl -s -H "Authorization: Bearer $TOKEN" -H "Content-Type: application/json" \
  -d '{"tab_id":"xxx"}' http://localhost:18792/tab/close
```

## API Endpoints

| Endpoint | Method | Description |
|----------|--------|-------------|
| `/health` | GET | Health check |
| `/tabs` | GET | List all browser tabs |
| `/navigate` | POST | Navigate to URL (`{"url":"..."}`) |
| `/screenshot` | POST | Capture screenshot (jpeg/png, optional `quality`, `fullPage`) |
| `/click` | POST | Click at coordinates (`{"x":N,"y":N}`) or selector (`{"selector":"..."}`) |
| `/type` | POST | Type text (`{"text":"..."}`) |
| `/keypress` | POST | Send key event (`{"key":"Enter"}`) |
| `/scroll` | POST | Scroll page (`{"y":N}`) |
| `/evaluate` | POST | Execute JavaScript (`{"expression":"..."}`) |
| `/wait` | POST | Wait for element (`{"selector":"...","timeout":5000}`) |
| `/tab/new` | POST | Open new tab (`{"url":"..."}`) |
| `/tab/activate` | POST | Switch to tab (`{"tab_id":"..."}`) |
| `/tab/close` | POST | Close tab (`{"tab_id":"..."}`) |

## Requirements

- Python 3.8+
- `aiohttp`, `websockets` — install via `pip install -r requirements.txt`
- Chromium / Chrome with `--remote-debugging-port=9222 --remote-allow-origins=*`

## Security

- The relay listens only on `127.0.0.1` (localhost) and is never exposed to the network.
- A random auth token is generated on each startup and saved to `/tmp/browser-relay-token`. All API requests require `Authorization: Bearer <token>`.
- The `/evaluate` endpoint executes arbitrary JavaScript in the browser context. This is by design for automation, but should only be called by trusted local clients.
- It is recommended to run the relay in an isolated environment (VM, container) when automating untrusted websites.

## File Structure

```
browser-relay/
├── relay.py           # Main relay server (asyncio + aiohttp + CDP WebSocket)
├── start.sh           # Launcher script (start/stop/restart, CDP check)
├── requirements.txt   # Python dependencies
├── SKILL.md           # AI assistant skill definition
└── screenshots/       # Auto-saved screenshots (gitignored)
```

## Disclaimer

This tool is for personal automation and educational purposes. Respect platform terms of service. The authors are not responsible for any misuse.

---

# Browser Relay 小红书自动化中继（中文说明）

轻量级 HTTP 中继服务，让 AI 助手通过本地 Chromium 浏览器操作小红书等中国平台，绕过数据中心 IP 封锁。

## 为什么需要这个？

AI 助手通常运行在云服务器上，其 IP 会被小红书等平台的风控系统拦截（"网络环境异常"）。本中继让 AI 通过 HTTP 发送指令到本地 relay 服务，再通过 CDP 协议控制你的 Chromium 浏览器。所有网络请求都从你的本机 IP 发出，绕过封锁。

## 架构

```
AI 助手 → HTTP (端口 18792) → relay.py → CDP WebSocket (端口 9222) → 本地 Chromium
```

## 功能特性

- **完整浏览器控制**：导航、点击、输入、滚动、截图、JS 执行
- **标签页管理**：新建、切换、关闭标签页
- **DOM 查询**：通过 CSS 选择器查找元素坐标
- **截图发送到 Telegram**：截图后直接通过 Bot API 发送到 Telegram 聊天
- **认证 Token**：每次启动自动生成，保障安全
- **Chromium 自动启动**：支持正确参数启动 Chromium

## 快速开始

### 1. 启动 Chromium（带远程调试端口）

```bash
chromium --remote-debugging-port=9222 --remote-allow-origins=*
```

> **重要**：必须加 `--remote-allow-origins=*`，否则 WebSocket 连接会被拒绝。

### 2. 安装依赖并启动

```bash
cd browser-relay
python3 -m venv venv && source venv/bin/activate
pip install -r requirements.txt
python3 relay.py
```

或使用启动脚本：

```bash
bash start.sh          # 启动
bash start.sh restart  # 重启
bash start.sh stop     # 停止
```

## API 端点

| 端点 | 说明 |
|------|------|
| `/health` | 健康检查 |
| `/tabs` | 获取所有标签页 |
| `/navigate` | 导航到 URL |
| `/screenshot` | 截图（支持质量参数和全页截图） |
| `/click` | 点击坐标或 CSS 选择器 |
| `/type` | 输入文本 |
| `/keypress` | 发送按键 |
| `/scroll` | 滚动页面 |
| `/evaluate` | 执行 JavaScript |
| `/wait` | 等待元素出现 |
| `/tab/new` | 新建标签页 |
| `/tab/activate` | 切换标签页 |
| `/tab/close` | 关闭标签页 |

## 依赖

- Python 3.8+
- `aiohttp`, `websockets` — 通过 `pip install -r requirements.txt` 安装
- Chromium（需启用 `--remote-debugging-port=9222 --remote-allow-origins=*`）

## 安全说明

- relay 仅监听 `127.0.0.1`（localhost），不会暴露到外部网络
- 每次启动自动生成随机 auth token，保存到 `/tmp/browser-relay-token`，所有 API 请求必须携带 `Authorization: Bearer <token>`
- `/evaluate` 端点允许在浏览器中执行任意 JavaScript，这是自动化所需的设计，但仅应由本地可信调用方使用
- 建议在隔离环境（虚拟机、容器）中运行

## 免责声明

本工具仅用于个人自动化和学习目的。请遵守平台使用条款。作者不对任何滥用行为负责。
