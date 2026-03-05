# OpenClaw 配置路径速查表

常用配置项的正确路径，避免猜测和错误。

---

## 🔌 Providers（模型提供商）

### 添加/修改 Provider
```json
{
  "models": {
    "providers": {
      "<provider-name>": {
        "baseUrl": "https://api.example.com/v1",
        "apiKey": "sk-...",
        "api": "openai-completions",
        "models": [
          {
            "id": "model-id",
            "name": "Display Name",
            "contextWindow": 200000,
            "maxTokens": 8192
          }
        ]
      }
    }
  }
}
```

### 常见 Provider 名称
| Provider | 名称 |
|----------|------|
| Moonshot (Kimi) | `moonshot` |
| OpenAI | `openai` |
| Anthropic (Claude) | `anthropic` |
| Google (Gemini) | `google` |

---

## 📢 Channels（消息通道）

### Discord
```json
{
  "channels": {
    "discord": {
      "enabled": true,
      "token": "YOUR_BOT_TOKEN",
      "groupPolicy": "open"
    }
  }
}
```

### WhatsApp
```json
{
  "plugins": {
    "entries": {
      "whatsapp": {
        "enabled": true
      }
    }
  }
}
```

### Telegram
```json
{
  "channels": {
    "telegram": {
      "enabled": true,
      "token": "YOUR_BOT_TOKEN"
    }
  }
}
```

### Slack
```json
{
  "channels": {
    "slack": {
      "enabled": true,
      "token": "xoxb-..."
    }
  }
}
```

---

## 🤖 Agent 配置

### 默认模型
```json
{
  "agents": {
    "defaults": {
      "model": {
        "primary": "moonshot/kimi-k2.5"
      }
    }
  }
}
```

### 并发设置
```json
{
  "agents": {
    "defaults": {
      "maxConcurrent": 4,
      "subagents": {
        "maxConcurrent": 8
      }
    }
  }
}
```

---

## ⚙️ Gateway 配置

### 认证模式
```json
{
  "gateway": {
    "mode": "local",
    "auth": {
      "mode": "token",
      "token": "YOUR_GATEWAY_TOKEN"
    }
  }
}
```

---

## 📝 消息设置

### 反应范围
```json
{
  "messages": {
    "ackReactionScope": "group-mentions"
  }
}
```

选项值：
- `"all"` - 所有消息
- `"group-mentions"` - 仅群聊中提到
- `"none"` - 从不

---

## ⚠️ 常见错误路径对照表

| 配置项 | ❌ 错误路径 | ✅ 正确路径 |
|--------|------------|------------|
| Discord Token | `plugins.entries.discord.botToken` | `channels.discord.token` |
| 默认模型 | `model.default` | `agents.defaults.model.primary` |
| Provider Key | `apiKeys.moonshot` | `models.providers.moonshot.apiKey` |

---

## 🔍 快速查询

### 如何查看完整配置？
```
gateway config.get
```

### 如何修改配置？
```
gateway config.patch
{ "要修改的部分": "值" }
```

### 配置修改后没生效？
1. 检查 JSON 语法
2. 使用 `config.get` 验证
3. 重启 OpenClaw: `openclaw gateway restart`

---

*最后更新: 2026-02-10*
