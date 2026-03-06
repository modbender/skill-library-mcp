# Elite Longterm Memory (Local Edition) 🧠

本地向量嵌入版的长期记忆系统。基于 LanceDB + Ollama，无需 OpenAI API。

## 架构

```
┌─────────────────────────────────────────────────────────────────┐
│                    ELITE LONGTERM MEMORY                        │
├─────────────────────────────────────────────────────────────────┤
│  HOT RAM          WARM STORE        COLD STORE                 │
│  SESSION-STATE.md → LanceDB      → Git-Notes                   │
│  (survives         (semantic       (permanent                  │
│   compaction)       search)         decisions)                 │
│         │              │                │                      │
│         └──────────────┼────────────────┘                      │
│                        ▼                                       │
│                   MEMORY.md                                    │
│               (curated archive)                                │
└─────────────────────────────────────────────────────────────────┘
```

## 快速开始

```bash
# 1. 初始化记忆系统
node skills/elite-longterm-memory/bin/init.js

# 2. 确保 Ollama 运行并拉取向量模型
ollama pull nomic-embed-text

# 3. 测试
node skills/elite-longterm-memory/bin/memory.js store "用户喜欢深色模式"
node skills/elite-longterm-memory/bin/memory.js search "用户偏好"
```

## 配置

在 `~/.openclaw/openclaw.json` 中添加：

```json
{
  "plugins": {
    "entries": {
      "elite-longterm-memory": {
        "enabled": true,
        "config": {
          "ollamaUrl": "http://localhost:11434",
          "embeddingModel": "nomic-embed-text",
          "dbPath": "./memory/vectors"
        }
      }
    }
  }
}
```

## 依赖

- Node.js 18+
- Ollama (本地运行)
- LanceDB (自动安装)

## License

MIT
