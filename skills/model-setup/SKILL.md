---
name: model-setup
description: 安全地管理 OpenClaw 模型配置。用于添加、测试和配置新模型到 models.json，包括 API key 验证、模型可访问性测试、工具调用功能检测、设置默认模型和配置到特定 agent。所有操作都会自动备份配置文件以确保安全。
---

# Model Manager

安全地管理 OpenClaw 模型配置。

## 工作流程

### 1. 收集模型配置参数

询问用户以下信息：

**必需参数：**
- **Provider ID**: 提供商标识符（如 `openai`, `anthropic`, 或自定义 ID）
- **Base URL**: API 基础 URL（如 `https://api.openai.com/v1`）
- **API Key**: API 密钥（格式通常为 `key_id:secret`）
- **Model ID**: 模型 ID（如 `gpt-4`, `claude-3-opus`）
- **Model Name**: 显示名称（如 `GPT-4 (OpenAI)`）
- **Context Window**: 上下文窗口大小（token 数）
- **Max Tokens**: 最大输出 token 数

**可选参数：**
- **API Type**: API 类型（默认 `openai-completions`）
- **Reasoning**: 是否支持推理（默认 `false`）
- **Input Types**: 输入类型（默认 `["text"]`）
- **Cost**: 成本配置（输入/输出/缓存读写）
- **Streaming**: 是否支持流式输出（默认 `false`）

### 2. 验证 API Key 和模型可访问性

使用 `scripts/test_model.py` 测试模型配置：

```bash
python3 scripts/test_model.py '<provider_config_json>' '<model_id>' [--test-tool-calling] [--test-streaming]
```

测试内容包括：
- API key 格式验证
- 模型可访问性测试
- 基本响应验证
- 工具调用功能测试（可选，使用 `--test-tool-calling`）
- 流式输出功能测试（可选，使用 `--test-streaming`）

如果测试失败，告知用户错误原因并允许修正配置。

### 3. 测试工具调用功能（可选）

询问用户是否需要测试工具调用功能。如果需要，发送一个包含工具调用的测试请求，验证模型是否正确处理工具调用。

### 4. 确认配置

向用户展示完整的配置摘要，包括：
- Provider ID 和 Base URL
- Model ID 和 Name
- Context Window 和 Max Tokens
- 其他配置项

询问用户是否确认添加。

### 5. 确认是否设为默认模型

询问用户是否将此模型设为默认模型。

### 6. 确认是否配置给特定 agent

询问用户是否需要将此模型配置给特定 agent。如果需要，询问 agent 路径（如 `/home/yupeng/.openclaw/agents/main`）。

### 7. 添加模型配置

使用 `scripts/add_model.py` 添加模型配置：

```bash
python3 scripts/add_model.py '<config_path>' '<provider_id>' '<provider_config_json>' '<model_config_json>' [--default] [--agent <agent_path>]
```

脚本会自动：
- 备份原始配置文件（`.json.backup.YYYYMMDD_HHMMSS`）
- 验证模型配置
- 添加或更新模型
- 设置默认模型（如果指定）
- 配置到指定 agent（如果指定）
- 如果失败，自动从备份恢复

### 8. 验证结果

检查操作结果：
- 如果成功，显示成功消息和备份文件路径
- 如果失败，显示错误信息并告知用户已从备份恢复

## 配置文件位置

- **models.json**: `/home/yupeng/.openclaw/agents/main/agent/models.json`
- **config.json** (默认模型): `/home/yupeng/.openclaw/agents/main/agent/config.json`
- **Agent config.json**: `/home/yupeng/.openclaw/agents/<agent_name>/agent/config.json`

## 列出已配置的模型

使用 `scripts/list_models.py` 列出所有已配置的模型：

```bash
# JSON 格式输出
python3 scripts/list_models.py

# 格式化文本输出
python3 scripts/list_models.py --format

# 指定配置文件路径
python3 scripts/list_models.py /path/to/models.json --format
```

输出内容包括：
- 提供商信息（ID、Base URL、API 类型）
- 模型列表（ID、名称、上下文窗口、最大 token、推理支持）

## 安全注意事项

1. **始终备份**: 所有操作都会自动备份配置文件
2. **原子性写入**: 使用临时文件 + 原子替换，避免写入过程中断导致文件损坏
3. **验证优先**: 添加前先验证 API key 和模型可访问性
4. **错误恢复**: 如果操作失败，自动从备份恢复
5. **不覆盖**: 询问用户确认后再执行修改操作

## 示例配置

### OpenAI GPT-4

```json
{
  "provider_id": "openai",
  "provider_config": {
    "baseUrl": "https://api.openai.com/v1",
    "apiKey": "sk-xxx:yyy",
    "api": "openai-completions"
  },
  "model_config": {
    "id": "gpt-4",
    "name": "GPT-4 (OpenAI)",
    "reasoning": false,
    "input": ["text"],
    "cost": {
      "input": 0.03,
      "output": 0.06,
      "cacheRead": 0.001,
      "cacheWrite": 0.004
    },
    "contextWindow": 128000,
    "maxTokens": 4096,
    "api": "openai-completions"
  }
}
```

### Anthropic Claude 3

```json
{
  "provider_id": "anthropic",
  "provider_config": {
    "baseUrl": "https://api.anthropic.com/v1",
    "apiKey": "sk-ant-xxx",
    "api": "anthropic-completions"
  },
  "model_config": {
    "id": "claude-3-opus-20240229",
    "name": "Claude 3 Opus (Anthropic)",
    "reasoning": false,
    "input": ["text"],
    "cost": {
      "input": 0.015,
      "output": 0.075
    },
    "contextWindow": 200000,
    "maxTokens": 4096,
    "api": "anthropic-completions"
  }
}
```

## 错误处理

常见错误及解决方案：

1. **API key 格式错误**: 检查 API key 是否包含正确的分隔符
2. **模型不可访问**: 检查 Base URL、API key 和 Model ID 是否正确
3. **配置文件损坏**: 使用备份文件恢复
4. **权限不足**: 检查文件权限和用户权限
