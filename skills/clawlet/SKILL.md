---
name: clawlet
description: Clawlet - Nostr 智能管家。用于管理 Nostr 身份、发布内容、关注用户、读取时间线、AI筛选、智能推荐、私信功能、昵称管理。当用户要求生成 Nostr 身份、发消息到 Nostr、关注某人、查看时间线、设置兴趣、发现推荐用户、发送私信、查看私信、添加昵称时使用。
homepage: https://github.com/openclaw/clawlet
metadata: { "openclaw": { "emoji": "🦞", "requires": { "npm": ["nostr-tools", "ws", "https-proxy-agent"] } } }
---

# Clawlet - Nostr 智能管家

Clawlet 让 OpenClaw 化身为你的 Nostr 贴身管家，帮你管理去中心化社交身份。

## 核心能力

1. **身份管理** - 生成和管理 Nostr 密钥
2. **发布内容** - 发送文本到 Nostr 网络
3. **关注管理** - 关注/取关用户
4. **时间线** - 读取 Nostr 时间线
5. **用户资料** - 查看用户资料
6. **AI 筛选** - 根据兴趣筛选时间线内容
7. **智能推荐** - 基于兴趣发现值得关注的用户
8. **合规过滤** - 过滤敏感内容
9. **私信功能** - 加密私信（NIP-04）
10. **昵称管理** - 为联系人设置易记的昵称

## 用户命令示例

### 身份管理
- "帮我生成一个 Nostr 身份"
- "查看我的 Nostr 身份"
- "导出我的私钥"

### 发布内容
- "发一条消息到 Nostr：今天天气不错"
- "发布内容：Clawlet 上线了"

### 关注管理
- "关注 npub1xxx..."
- "帮我关注这个用户"

### 时间线
- "看看我的时间线"
- "有什么新消息"

### 私信功能
- "给哥哥发私信：你好"（使用昵称）
- "给 npub1xxx... 发送私信：你好"
- "查看我的私信"

### 昵称管理
- "给 npub1xxx... 添加昵称：哥哥"
- "列出我的所有昵称"
- "删除昵称：哥哥"

## 连接的 Relay

- wss://relay.damus.io
- wss://nos.lol
- wss://nostr.wine

## 安全提醒

- 私钥存储在本地（`data/identities.json`）
- 请妥善保管私钥，不要泄露给他人
- 建议定期备份密钥文件

## 兼容性

Clawlet 基于 Nostr 协议，与以下客户端兼容：
- Damus (iOS)
- Amethyst (Android)
- Snort (Web)
- Primal (Web)
