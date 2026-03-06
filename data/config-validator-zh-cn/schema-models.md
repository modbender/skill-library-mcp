# Models Schema（模型配置）

## 基础配置

```json5
{
  agents: {
    defaults: {
      models: {
        "anthropic/claude-opus-4-6": { alias: "opus" },
        "openai/gpt-5.2": { alias: "gpt" },
        "minimax/MiniMax-M2.1": { alias: "minimax" },
      },
      model: {
        primary: "anthropic/claude-opus-4-6",
        fallbacks: ["minimax/MiniMax-M2.1"],
      },
      imageModel: {
        primary: "openrouter/qwen/qwen-2.5-vl-72b-instruct:free",
        fallbacks: ["openrouter/google/gemini-2.0-flash-vision:free"],
      },
    }
  }
}
```

### 核心字段

| 字段 | 类型 | 有效值 | 默认值 | 说明 |
|---|---|---|---|---|
| `models` | object | 模型配置对象 | - | 模型目录 |
| `model.primary` | string | `provider/model` | - | 主模型 |
| `model.fallbacks` | array | 模型列表 | `[]` | 故障转移模型 |
| `imageModel.primary` | string | `provider/model` | - | 图像模型 |
| `imageModel.fallbacks` | array | 模型列表 | `[]` | 图像故障转移 |

---

## 内置模型别名

| 别名 | 模型 |
|---|---|
| `opus` | `anthropic/claude-opus-4-6` |
| `sonnet` | `anthropic/claude-sonnet-4-5` |
| `gpt` | `openai/gpt-5.2` |
| `gpt-mini` | `openai/gpt-5-mini` |
| `gemini` | `google/gemini-3-pro-preview` |
| `gemini-flash` | `google/gemini-3-flash-preview` |

---

## 模型配置详解

```json5
{
  agents: {
    defaults: {
      models: {
        "anthropic/claude-opus-4-6": {
          alias: "opus",
          params: {
            temperature: 0.7,
            maxTokens: 4096,
            cacheRetention: "none",
          },
        },
        "openai/gpt-5.2": {
          alias: "gpt",
          reasoning: true,
          input: ["text", "image"],
        },
      }
    }
  }
}
```

### 模型字段

| 字段 | 类型 | 有效值 | 默认值 | 说明 |
|---|---|---|---|---|
| `alias` | string | 任意字符串 | - | 模型别名 |
| `reasoning` | boolean | `true` \| `false` | - | 支持推理 |
| `input` | array | `text` \| `image` | `["text"]` | 输入类型 |
| `params.temperature` | number | `0.0` - `2.0` | - | 温度 |
| `params.maxTokens` | number | Token 数 | - | 最大 Token |
| `params.cacheRetention` | string | `none` \| `session` \| `permanent` | - | 缓存保留 |

---

## Thinking 模式（推理模型）

```json5
{
  agents: {
    defaults: {
      models: {
        "anthropic/claude-opus-4-6": {
          reasoning: true,
        },
        "openai/gpt-5.2": {
          reasoning: true,
        },
      },
      thinkingDefault: "low",
    }
  }
}
```

### Thinking 级别

| 级别 | 指令 | 说明 |
|---|---|---|
| `off` | `/think:off` | 关闭思考 |
| `minimal` | `/think:minimal` | 最小思考 |
| `low` | `/think:low` | 低思考（默认） |
| `medium` | `/think:medium` | 中等思考 |
| `high` | `/think:high` | 高思考 |

---

## 故障转移配置

```json5
{
  agents: {
    defaults: {
      model: {
        primary: "anthropic/claude-opus-4-6",
        fallbacks: [
          "openai/gpt-5.2",
          "minimax/MiniMax-M2.1",
        ],
      }
    }
  }
}
```

### 故障转移规则

1. 主模型失败时自动尝试 fallbacks
2. 按顺序尝试，直到成功
3. 所有模型失败时报错

---

## 图像模型配置

```json5
{
  agents: {
    defaults: {
      imageModel: {
        primary: "openrouter/qwen/qwen-2.5-vl-72b-instruct:free",
        fallbacks: ["openrouter/google/gemini-2.0-flash-vision:free"],
      },
      imageMaxDimensionPx: 1200,
    }
  }
}
```

### 字段详解

| 字段 | 类型 | 有效值 | 默认值 | 说明 |
|---|---|---|---|---|
| `imageModel.primary` | string | `provider/model` | - | 主图像模型 |
| `imageModel.fallbacks` | array | 模型列表 | `[]` | 故障转移 |
| `imageMaxDimensionPx` | number | 像素数 | `1200` | 图像最大尺寸 |

---

## 常见错误

| 错误 | 原因 | 修复 |
|---|---|---|
| `"model": "gpt-5.2"` | 缺少提供商前缀 | 改为 `"openai/gpt-5.2"` |
| `fallbacks: "gpt-5.2"` | 应该是数组 | 改为 `["openai/gpt-5.2"]` |
| `"thinkingDefault": "hard"` | 不是有效枚举值 | 改为 `low` \| `medium` \| `high` |
| 别名冲突 | 两个模型用同一别名 | 使用唯一别名 |

---

## 官方文档

- https://docs.openclaw.ai/gateway/configuration-reference#agent-defaults
- https://docs.openclaw.ai/zh-CN/concepts/model-failover
