# OpenClaw Template Generator Agent

当用户需要创建新项目时，使用这个 Agent。

## Agent 配置

```json
{
  "id": "template-generator",
  "model": {
    "provider": "minimax-portal",
    "model": "MiniMax-M2.1"
  },
  "systemPrompt": "你是一个 OpenClaw 项目规划专家。当用户提供需求时，生成完整的 OpenClaw 项目配置。",
  "instructions": "openclaw-gen/SKILL.md",
  "tools": {
    "allow": ["llm-task", "shell"]
  }
}
```

## 使用方式

### 通过 llm-task 工具

```json
{
  "tool": "llm-task",
  "parameters": {
    "prompt": "用户需求：每天早上 7 点发送天气到 Telegram",
    "model": "MiniMax-M2.1",
    "schema": {
      "type": "object",
      "properties": {
        "AGENTS.md": { "type": "string" },
        "workflows": { "type": "array" },
        "MEMORY.md": { "type": "string" }
      }
    }
  }
}
```

## 文件输出

```
~/.openclaw/workspace/generated/[项目名]/
├── AGENTS.md
├── workflows/*.yaml
├── MEMORY.md
└── README.md
```
