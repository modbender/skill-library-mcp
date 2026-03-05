---
name: openclaw-onebot
description: "OneBot 11 channel plugin for QQ messaging (NapCat/go-cqhttp). Enables QQ private & group chat as a first-class OpenClaw channel. WebSocket inbound + HTTP API outbound, auto-reconnect, access token auth, allowFrom filtering. 58 tests. 适用于 QQ 消息收发、NapCat 集成、go-cqhttp 对接。"
metadata:
  openclaw:
    emoji: "🐧"
    type: "channel-plugin"
    requires:
      config: ["channels.onebot.wsUrl", "channels.onebot.httpUrl"]
      bins: ["node", "npm"]
---

# OpenClaw OneBot 11 Channel Plugin

[中文](#中文) | [English](#english)

---

## 中文

> ⚠️ **ClawHub 安全扫描说明**：本 skill 在 ClawHub 上可能被标记为 "Suspicious"，这是因为 `.ts` (TypeScript) 文件的扩展名被自动识别为 `video/mp2t` (MPEG-2 视频流) MIME 类型触发了误报。所有源码均为标准 TypeScript，可在 [GitHub](https://github.com/xucheng/openclaw-onebot) 审查。


OpenClaw 的 OneBot 11 协议通道插件，让 QQ 成为 OpenClaw 一等消息通道。支持 [NapCat](https://github.com/NapNeko/NapCatQQ)、[go-cqhttp](https://github.com/Mrs4s/go-cqhttp) 等所有兼容 OneBot 11 协议的 QQ 机器人框架。

### 功能

- 🔌 OneBot 11 协议全支持，QQ 消息作为 OpenClaw 一等通道
- 📨 私聊和群聊收发消息
- 🖼️ 图片、语音、文件附件发送
- 🔄 WebSocket 自动重连（指数退避）
- 🔒 可选 access token 鉴权
- 🎯 `allowFrom` 消息来源过滤（私聊/群聊/用户级别）
- ✅ 58 个测试用例全部通过


### 语音支持（可选）

本插件支持 QQ 语音消息的**自动链路**：
- 入站：OneBot `record` (SILK/AMR) → 下载 → 转 MP3 → 交给 OpenClaw 统一音频管线（STT/TTS）
- 出站：当上层生成 `mediaUrl/mediaUrls` 为音频文件（`.mp3/.ogg/.wav/.amr/.silk` 等）时，会自动走 `sendRecord` 发送 QQ 语音

**依赖（需要你本机安装）：**
- `ffmpeg`
- `uv`（用于按需运行 `pilk` 解码 SILK；AMR 仅需 ffmpeg）

如果只用文字/图片，不装这些也没问题。


### 与其他方案对比

| | **openclaw-onebot** (本项目) | 方案 A | 方案 B |
|---|---|---|---|
| **协议** | OneBot 11 (NapCat/go-cqhttp) | QQ 官方 Bot API | OneBot 11 |
| **集成方式** | ✅ **ChannelPlugin 原生集成** | ❌ 独立 Python 脚本 + 文件队列 | ❌ 独立 Python 脚本 |
| **消息路由** | OpenClaw 自动路由，`message` tool 直接用 | 文件队列读写，需手动桥接 | 手动调 Python API |
| **语音支持** | ✅ SILK/AMR → MP3 → STT/TTS 全自动 | ❌ 无 | ❌ 无 |
| **消息聚合** | ✅ 1.5s 智能合并 | ❌ 无 | ❌ 无 |
| **自动重连** | ✅ WebSocket 指数退避 | daemon 脚本重启 | ❌ 无 |
| **测试覆盖** | ✅ 58 tests | ❌ 无 | ❌ 无 |
| **需要额外进程** | ❌ 随 gateway 启动 | ✅ 需独立运行 daemon | ✅ 需独立运行 listener |

**核心区别**：本项目是 OpenClaw **原生通道插件**，安装后 QQ 就和 Discord / Telegram 一样使用，不需要额外的桥接脚本或消息队列。

### 架构

```
QQ 机器人框架 (NapCat / go-cqhttp)
  ├── WebSocket → 接收消息
  └── HTTP API  → 发送消息
      ↕
OpenClaw OneBot Plugin (ChannelPlugin)
      ↕
OpenClaw 主会话
```

### 安装

```bash
# 方式一：自动安装
bash scripts/install.sh

# 方式二：手动安装
cp -r src index.ts package.json tsconfig.json ~/.openclaw/plugins/onebot/
cd ~/.openclaw/plugins/onebot && npm install && npm run build
```

重启 gateway 生效。

### 配置

在 `openclaw.json` 中添加：

```json
{
  "channels": {
    "onebot": {
      "enabled": true,
      "wsUrl": "ws://your-host:port",
      "httpUrl": "http://your-host:port"
    }
  }
}
```

也可以通过环境变量配置：

```bash
ONEBOT_WS_URL=ws://your-host:port
ONEBOT_HTTP_URL=http://your-host:port
ONEBOT_ACCESS_TOKEN=your_token  # 可选
```

#### 高级配置

```json
{
  "channels": {
    "onebot": {
      "enabled": true,
      "wsUrl": "ws://your-host:port",
      "httpUrl": "http://your-host:port",
      "accessToken": "your_token",
      "allowFrom": ["private:12345", "group:67890"],
      "users": ["12345"]
    }
  }
}
```

| 参数 | 说明 |
|------|------|
| `allowFrom` | 消息来源过滤 — `private:<QQ号>`、`group:<群号>`、或 `<QQ号>`（同时匹配私聊和群聊） |
| `users` | 允许触发机器人的 QQ 用户白名单 |
| `accessToken` | HTTP API 使用 `Authorization: Bearer <token>`，WebSocket 使用 query 参数 |

### 消息目标格式

- `private:<QQ号>` — 私聊消息
- `group:<群号>` — 群聊消息
- `<QQ号>` — 自动识别为私聊

### 状态检查

```bash
bash scripts/status.sh
```

### NapCat 部署

1. 部署 [NapCat](https://github.com/NapNeko/NapCatQQ)（推荐 Docker）
2. 启用 WebSocket 和 HTTP API（同一端口）
3. 在插件中配置对应地址

---

## English

> ⚠️ **ClawHub Security Note**: This skill may be flagged as "Suspicious" on ClawHub because `.ts` (TypeScript) files are auto-detected as `video/mp2t` (MPEG-2 Transport Stream) MIME type, triggering a false positive. All source code is standard TypeScript — review it on [GitHub](https://github.com/xucheng/openclaw-onebot).


An [OpenClaw](https://github.com/openclaw/openclaw) channel plugin that connects to [NapCat](https://github.com/NapNeko/NapCatQQ), [go-cqhttp](https://github.com/Mrs4s/go-cqhttp), or any OneBot 11 compatible QQ bot framework.

### Features

- 🔌 Full OneBot 11 protocol — QQ as a first-class OpenClaw channel
- 📨 Private & group chat (inbound + outbound)
- 🖼️ Image, audio, and file attachments
- 🔄 WebSocket auto-reconnect with exponential backoff
- 🔒 Optional access token authentication
- 🎯 `allowFrom` filtering (private/group/user-level)
- ✅ 58 tests passing


### Voice Support (Optional)

This plugin supports an **end-to-end voice flow**:
- Inbound: OneBot `record` (SILK/AMR) → download → convert to MP3 → pass to OpenClaw unified audio pipeline (STT/TTS)
- Outbound: if the upstream reply contains audio `mediaUrl/mediaUrls` (e.g. `.mp3/.ogg/.wav/.amr/.silk`), it will automatically use `sendRecord` to send QQ voice

**Dependencies (install on your machine):**
- `ffmpeg`
- `uv` (used to run `pilk` for SILK decoding on-demand; AMR only needs ffmpeg)

If you only need text/images, you can skip these.


### Comparison with Alternatives

| | **openclaw-onebot** (this) | Solution A | Solution B |
|---|---|---|---|
| **Protocol** | OneBot 11 (NapCat/go-cqhttp) | QQ Official Bot API | OneBot 11 |
| **Integration** | ✅ **Native ChannelPlugin** | ❌ Standalone Python + file queue | ❌ Standalone Python scripts |
| **Message routing** | Auto via OpenClaw `message` tool | Manual file I/O bridge | Manual Python API calls |
| **Voice** | ✅ SILK/AMR → MP3 → STT/TTS auto | ❌ None | ❌ None |
| **Batching** | ✅ 1.5s smart merge | ❌ None | ❌ None |
| **Auto-reconnect** | ✅ Exponential backoff | Daemon restart | ❌ None |
| **Tests** | ✅ 58 tests | ❌ None | ❌ None |
| **Extra process** | ❌ Runs with gateway | ✅ Separate daemon | ✅ Separate listener |

**Key difference**: This is a **native OpenClaw channel plugin** — once installed, QQ works just like Discord or Telegram. No bridge scripts, no message queues, no extra processes.

### Installation

```bash
# Auto install
bash scripts/install.sh

# Manual
cp -r src index.ts package.json tsconfig.json ~/.openclaw/plugins/onebot/
cd ~/.openclaw/plugins/onebot && npm install && npm run build
```

Restart gateway to activate.

### Configuration

Add to `openclaw.json`:

```json
{
  "channels": {
    "onebot": {
      "enabled": true,
      "wsUrl": "ws://your-host:port",
      "httpUrl": "http://your-host:port"
    }
  }
}
```

Or via environment variables:

```bash
ONEBOT_WS_URL=ws://your-host:port
ONEBOT_HTTP_URL=http://your-host:port
ONEBOT_ACCESS_TOKEN=your_token  # optional
```

| Option | Description |
|--------|-------------|
| `allowFrom` | Filter inbound — `private:<qq>`, `group:<id>`, or `<qq>` (matches both) |
| `users` | Whitelist of QQ user IDs |
| `accessToken` | Bearer token for HTTP API, query param for WebSocket |

### Target Format

- `private:<qq_number>` — Private message
- `group:<group_id>` — Group message
- `<qq_number>` — Auto-detected as private

### Development

```bash
npm install
npm test          # Run 58 tests
npm run build     # Compile TypeScript
npm run coverage  # Coverage report
```

## License

MIT
