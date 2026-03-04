---
name: openclaw-wecom-channel
description: "企业微信 (WeCom) Channel 插件 — 让 OpenClaw AI Agent 通过企业微信收发消息。支持消息加解密、Token 自动管理、访问控制策略。"
homepage: https://github.com/darrryZ/openclaw-wecom-channel
metadata: { "openclaw": { "emoji": "💬", "requires": { "bins": ["node"], "network": true } } }
---

# OpenClaw 企业微信 Channel 插件

企业微信 (WeCom/WxWork) 消息通道插件，让 OpenClaw AI Agent 通过企业微信收发消息，与 Telegram、Discord、Signal 等并列为原生 Channel。

## 功能

- **📩 接收消息** — 企业微信用户发送文本，Agent 自动回复
- **📤 主动推送** — Agent 通过企业微信 API 主动发送消息
- **🔐 消息加解密** — 完整实现企业微信 AES-256-CBC 消息加解密（WXBizMsgCrypt 标准）
- **🔑 Token 管理** — access_token 自动缓存 + 提前 5 分钟刷新
- **🛡️ 访问控制** — open / pairing / allowlist 三种策略
- **⚡ 智能回复** — 5 秒内被动回复，超时自动降级为主动推送

## 前置条件

- OpenClaw 已安装并运行
- 企业微信管理员权限（创建自建应用）
- 公网可达的回调 URL（推荐 Cloudflare Tunnel）

## 快速开始

### 1. 安装插件

```bash
# 克隆到 OpenClaw extensions 目录
git clone https://github.com/darrryZ/openclaw-wecom-channel.git ~/.openclaw/extensions/wecom
```

### 2. 配置 OpenClaw

编辑 `~/.openclaw/openclaw.json`：

```json
{
  "channels": {
    "wecom": {
      "enabled": true,
      "corpId": "你的企业ID",
      "agentId": 1000003,
      "secret": "应用Secret",
      "token": "回调Token",
      "encodingAESKey": "回调EncodingAESKey",
      "port": 18800,
      "dmPolicy": "open"
    }
  },
  "plugins": {
    "entries": {
      "wecom": { "enabled": true }
    }
  }
}
```

### 3. 配置公网回调（Cloudflare Tunnel）

```bash
cloudflared tunnel create wecom-tunnel
cloudflared tunnel route dns wecom-tunnel wecom.yourdomain.com
cloudflared tunnel run --edge-ip-version 4 --url http://localhost:18800 wecom-tunnel
```

企业微信后台回调 URL 设置为：`https://wecom.yourdomain.com/wecom/callback`

### 4. 重启 Gateway

```bash
openclaw gateway restart
```

## 详细文档

完整的配置指南、企业微信后台设置步骤、故障排查请参考 README.md。

## 链接

- **GitHub**: https://github.com/darrryZ/openclaw-wecom-channel
- **OpenClaw**: https://github.com/openclaw/openclaw
- **企业微信开发文档**: https://developer.work.weixin.qq.com/document/
