# Chinese Providers Guide

## 适用场景

- 需要更好的中文理解和生成能力
- 想要使用国产 AI 模型（通义千问、智谱 GLM、文心一言等）
- 合规要求需要使用境内服务
- 降低海外 API 调用延迟

## 配置变更

本指南将修改以下文件：

1. `openclaw.json` - 添加中国 AI 提供商配置
2. `workspace/AGENTS.md` - 添加提供商选择规则

## 支持的提供商

### 通义千问 (Qwen)

**优势**:
- 强大的中文理解能力
- 支持长上下文（32K-128K tokens）
- 代码能力出色
- 价格合理

**推荐模型**:
- `qwen-max` - 最强能力
- `qwen-plus` - 平衡性价比
- `qwen-turbo` - 快速响应

### 智谱 GLM

**优势**:
- 中文对话流畅
- 多模态支持
- 工具调用能力强
- 开源版本可用

**推荐模型**:
- `glm-4` - 最新版本
- `glm-4-flash` - 快速版本

### 文心一言 (ERNIE)

**优势**:
- 百度生态集成
- 知识图谱增强
- 企业级支持

**推荐模型**:
- `ernie-4.0` - 最强版本
- `ernie-3.5-turbo` - 快速版本

### DeepSeek

**优势**:
- 极低价格
- 代码能力强
- 支持长上下文

**推荐模型**:
- `deepseek-chat` - 通用对话
- `deepseek-coder` - 代码专用

## 安装命令

### 1. 更新 openclaw.json

添加中国提供商配置：

```json
{
  "api": {
    "anthropic": {
      "apiKey": "${ANTHROPIC_API_KEY}"
    },
    "qwen": {
      "apiKey": "${QWEN_API_KEY}",
      "baseUrl": "https://dashscope.aliyuncs.com/api/v1"
    },
    "zhipu": {
      "apiKey": "${ZHIPU_API_KEY}",
      "baseUrl": "https://open.bigmodel.cn/api/paas/v4"
    },
    "ernie": {
      "apiKey": "${ERNIE_API_KEY}",
      "secretKey": "${ERNIE_SECRET_KEY}",
      "baseUrl": "https://aip.baidubce.com/rpc/2.0/ai_custom/v1"
    },
    "deepseek": {
      "apiKey": "${DEEPSEEK_API_KEY}",
      "baseUrl": "https://api.deepseek.com/v1"
    }
  },
  "model": {
    "default": "qwen-max",
    "fallback": "qwen-plus",
    "providers": {
      "chinese": ["qwen-max", "glm-4", "ernie-4.0", "deepseek-chat"],
      "code": ["deepseek-coder", "qwen-plus"],
      "fast": ["qwen-turbo", "glm-4-flash", "deepseek-chat"]
    }
  }
}
```

### 2. 设置环境变量

创建 `~/.openclaw/.env`:

```bash
# Anthropic (Optional - for fallback)
ANTHROPIC_API_KEY=your_anthropic_key

# 通义千问
QWEN_API_KEY=sk-your-qwen-key

# 智谱 GLM
ZHIPU_API_KEY=your_zhipu_key

# 文心一言
ERNIE_API_KEY=your_ernie_key
ERNIE_SECRET_KEY=your_ernie_secret

# DeepSeek
DEEPSEEK_API_KEY=sk-your-deepseek-key
```

### 3. 更新 AGENTS.md

添加提供商选择规则：

```markdown
## Chinese Provider Selection

### 模型选择策略

根据任务类型选择最合适的模型：

| Task Type | Model | Reason |
|-----------|-------|--------|
| 中文对话 | qwen-max | 最佳中文理解 |
| 代码生成 | deepseek-coder | 专注代码，性价比高 |
| 快速响应 | qwen-turbo | 低延迟 |
| 复杂推理 | glm-4 | 强推理能力 |
| 成本敏感 | deepseek-chat | 极低价格 |

### 语言偏好

- 用户使用中文 → 使用中文模型
- 代码相关 → 优先 DeepSeek
- 长文档 → 使用支持长上下文的模型

### Fallback 策略

当首选模型不可用时：
1. 尝试同提供商的其他模型
2. 切换到其他中国提供商
3. 最后使用 Anthropic（如果配置）
```

## 验证步骤

### 1. 验证配置

```bash
cat ~/.openclaw/openclaw.json | grep -A 20 "api"
```

### 2. 测试通义千问

```
使用 qwen-max 模型解释一下什么是微服务架构
```

Expected:
- AI 使用 qwen-max 模型
- 返回流畅的中文回答

### 3. 测试 DeepSeek 代码能力

```
使用 deepseek-coder 创建一个用户注册的 API 端点
```

Expected:
- AI 使用 deepseek-coder
- 生成高质量代码

### 4. 测试模型切换

```
用最快的模型告诉我现在几点了
```

Expected:
- AI 选择 qwen-turbo 或 glm-4-flash
- 快速返回结果

## 使用示例

### 指定模型

```
使用 qwen-max 分析这段代码的问题
```

### 语言自适应

```
帮我写一份项目文档（AI 会自动选择中文模型）
```

### 成本优化

```
用最便宜的模型完成这个简单的翻译任务
```

### 长文档处理

```
用支持长上下文的模型总结这份 100 页的报告
```

## 价格对比

| Provider | Model | Input (¥/1M tokens) | Output (¥/1M tokens) |
|----------|-------|---------------------|----------------------|
| 通义千问 | qwen-max | 40 | 40 |
| 通义千问 | qwen-turbo | 2 | 6 |
| 智谱 | glm-4 | 100 | 100 |
| 智谱 | glm-4-flash | 1 | 1 |
| 文心 | ernie-4.0 | 120 | 120 |
| DeepSeek | deepseek-chat | 1 | 2 |
| DeepSeek | deepseek-coder | 1 | 2 |

*价格仅供参考，以官方最新价格为准*

## 进阶配置

### 混合使用中外模型

```json
{
  "model": {
    "default": "qwen-max",
    "fallback": "claude-sonnet-4",
    "routing": {
      "chinese_tasks": "qwen-max",
      "english_tasks": "claude-sonnet-4",
      "code_tasks": "deepseek-coder"
    }
  }
}
```

### 自定义提供商

添加其他中国提供商：

```json
{
  "api": {
    "minimax": {
      "apiKey": "${MINIMAX_API_KEY}",
      "baseUrl": "https://api.minimax.chat/v1"
    }
  }
}
```

### 地理位置路由

根据用户位置自动选择：

```json
{
  "routing": {
    "geoBased": true,
    "china": "qwen-max",
    "international": "claude-sonnet-4"
  }
}
```

## 故障排除

### API Key 无效

1. 检查环境变量设置
2. 验证 API Key 格式
3. 确认账户余额充足

### 模型响应慢

1. 检查网络连接
2. 尝试其他提供商
3. 使用快速模型（turbo/flash）

### 中文理解不准确

1. 尝试不同模型
2. 提供更多上下文
3. 使用专业领域模型

## 相关指南

- [agent-swarm.md](agent-swarm.md) - 不同提供商作为不同 Worker
- [cost-optimization.md](cost-optimization.md) - 优化中国提供商成本
- [memory-optimized.md](memory-optimized.md) - 中文记忆优化

## 官方文档

- 通义千问: https://help.aliyun.com/zh/dashscope/
- 智谱 GLM: https://open.bigmodel.cn/dev/api
- 文心一言: https://cloud.baidu.com/doc/WENXINWORKSHOP/
- DeepSeek: https://platform.deepseek.com/api-docs/
