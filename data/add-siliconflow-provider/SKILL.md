---
name: add-siliconflow-provider
description: 为 OpenClaw 配置硅基流动 (SiliconFlow) 作为模型源。SiliconFlow 是国内领先的 AI 模型推理平台，提供 98+ 个 chat 模型，包含多个免费模型（Qwen3-8B、DeepSeek-R1-8B 等）。使用标准 OpenAI 协议（openai-completions）。包含 provider 注册、模型定义、别名配置、fallback 链接入和验证的完整流程。当管理员说想"加硅基流动"、"配 SiliconFlow"、"接入 SF 模型"、"加 Kimi"、"加 Qwen3"、"加免费模型"、"接入 DeepSeek V3.2"时使用此 skill。
---

# 配置 SiliconFlow Provider（硅基流动模型推理平台）

SiliconFlow（硅基流动）是国内领先的 AI 模型推理平台，提供 98+ 个 chat 模型，涵盖 Qwen、DeepSeek、Kimi、GLM、MiniMax 等主流系列。

**核心优势**：
- 🆓 **多个免费模型**：Qwen3-8B、DeepSeek-R1-8B 等完全免费
- 💰 **价格极低**：旗舰模型价格仅为官方的 30-50%
- 🔌 **OpenAI 兼容**：标准 `openai-completions` 协议，即插即用
- 📦 **模型丰富**：一个 API Key 访问所有模型

如果还没有 SiliconFlow 账号，请通过邀请链接注册（双方均获赠额度）：
👉 **https://cloud.siliconflow.cn/i/ihj5inat**

| 项目 | 值 |
|------|------|
| Provider 名称 | `siliconflow` |
| API 协议 | `openai-completions` |
| Base URL | `https://api.siliconflow.cn/v1` |
| 认证方式 | Bearer Token (API Key) |

---

## 前置条件

| 项目 | 说明 |
|------|------|
| API Key | 在 [控制台](https://cloud.siliconflow.cn/account/ak) 创建，格式 `sk-xxx` |
| 余额 | 免费模型无需余额；付费模型需充值（新用户注册送 ¥14） |

### 获取 API Key

1. 注册：https://cloud.siliconflow.cn/i/ihj5inat
2. 进入控制台 → API 密钥 → 创建
3. 复制 `sk-xxx` 格式的密钥

### 验证 API Key

```bash
curl -s 'https://api.siliconflow.cn/v1/user/info' \
  -H 'Authorization: Bearer <YOUR_API_KEY>' | python3 -m json.tool
```

期望返回 `"status": "normal"` 和余额信息。

---

## 推荐模型

### 🆓 免费模型（无限使用）

| 模型 ID | 说明 | 推荐别名 |
|---------|------|----------|
| `Qwen/Qwen3-8B` | 通义千问 3 代 8B，综合能力强 | `sf-qwen3-8b` |
| `deepseek-ai/DeepSeek-R1-0528-Qwen3-8B` | DeepSeek R1 推理蒸馏版 | `sf-r1-8b` |
| `THUDM/glm-4-9b-chat` | 智谱 GLM-4 9B | `sf-glm4` |
| `Qwen/Qwen2.5-7B-Instruct` | Qwen 2.5 7B | `sf-qwen25-7b` |
| `Qwen/Qwen2.5-Coder-7B-Instruct` | Qwen 2.5 编码专用 | `sf-qwen-coder-7b` |

### 💰 性价比模型（便宜好用）

| 模型 ID | 输入/输出 (¥/M tokens) | 说明 | 推荐别名 |
|---------|----------------------|------|----------|
| `Qwen/Qwen3-30B-A3B` | 0.7 / 2.8 | MoE 架构，性价比极高 | `sf-qwen3-30b` |
| `Qwen/Qwen3-Coder-30B-A3B-Instruct` | 0.7 / 2.8 | 编码专用 30B | `sf-coder-30b` |
| `deepseek-ai/DeepSeek-V3.2` | 2.0 / 3.0 | DeepSeek 最新版 | `sf-dsv3` |
| `Pro/deepseek-ai/DeepSeek-V3.2` | 2.0 / 3.0 | Pro 加速版 | `sf-dsv3-pro` |

### 🚀 旗舰模型（重要任务）

| 模型 ID | 输入/输出 (¥/M tokens) | 说明 | 推荐别名 |
|---------|----------------------|------|----------|
| `deepseek-ai/DeepSeek-R1` | 4.0 / 16.0 | 推理模型 | `sf-r1` |
| `Pro/moonshotai/Kimi-K2.5` | 4.0 / 21.0 | 月之暗面最强模型 | `sf-kimi` |
| `Qwen/Qwen3-Coder-480B-A35B-Instruct` | 8.0 / 16.0 | 编码旗舰 480B MoE | `sf-coder-480b` |

---

## 配置步骤

### Step 1: 备份配置

```bash
cp ~/.openclaw/openclaw.json ~/.openclaw/openclaw.json.backup.$(date +%Y%m%d_%H%M%S)
```

### Step 2: 添加 Provider

通过 `gateway config.patch` 添加 SiliconFlow provider。以下为推荐配置（8 个精选模型）：

```json
{
  "models": {
    "providers": {
      "siliconflow": {
        "baseUrl": "https://api.siliconflow.cn/v1",
        "apiKey": "<YOUR_API_KEY>",
        "api": "openai-completions",
        "models": [
          {
            "id": "Qwen/Qwen3-8B",
            "name": "Qwen3 8B (Free)",
            "reasoning": false,
            "input": ["text"],
            "cost": {"input": 0, "output": 0, "cacheRead": 0, "cacheWrite": 0},
            "contextWindow": 32768,
            "maxTokens": 8192
          },
          {
            "id": "deepseek-ai/DeepSeek-R1-0528-Qwen3-8B",
            "name": "DeepSeek R1 Qwen3 8B (Free)",
            "reasoning": true,
            "input": ["text"],
            "cost": {"input": 0, "output": 0, "cacheRead": 0, "cacheWrite": 0},
            "contextWindow": 32768,
            "maxTokens": 8192
          },
          {
            "id": "Qwen/Qwen3-30B-A3B",
            "name": "Qwen3 30B MoE",
            "reasoning": false,
            "input": ["text"],
            "cost": {"input": 0.7, "output": 2.8, "cacheRead": 0, "cacheWrite": 0},
            "contextWindow": 32768,
            "maxTokens": 8192
          },
          {
            "id": "Qwen/Qwen3-Coder-30B-A3B-Instruct",
            "name": "Qwen3 Coder 30B",
            "reasoning": false,
            "input": ["text"],
            "cost": {"input": 0.7, "output": 2.8, "cacheRead": 0, "cacheWrite": 0},
            "contextWindow": 32768,
            "maxTokens": 8192
          },
          {
            "id": "deepseek-ai/DeepSeek-V3.2",
            "name": "DeepSeek V3.2",
            "reasoning": false,
            "input": ["text"],
            "cost": {"input": 2.0, "output": 3.0, "cacheRead": 0, "cacheWrite": 0},
            "contextWindow": 128000,
            "maxTokens": 8192
          },
          {
            "id": "deepseek-ai/DeepSeek-R1",
            "name": "DeepSeek R1",
            "reasoning": true,
            "input": ["text"],
            "cost": {"input": 4.0, "output": 16.0, "cacheRead": 0, "cacheWrite": 0},
            "contextWindow": 128000,
            "maxTokens": 8192
          },
          {
            "id": "Pro/moonshotai/Kimi-K2.5",
            "name": "Kimi K2.5",
            "reasoning": false,
            "input": ["text"],
            "cost": {"input": 4.0, "output": 21.0, "cacheRead": 0, "cacheWrite": 0},
            "contextWindow": 128000,
            "maxTokens": 8192
          },
          {
            "id": "Qwen/Qwen3-Coder-480B-A35B-Instruct",
            "name": "Qwen3 Coder 480B",
            "reasoning": false,
            "input": ["text"],
            "cost": {"input": 8.0, "output": 16.0, "cacheRead": 0, "cacheWrite": 0},
            "contextWindow": 32768,
            "maxTokens": 8192
          }
        ]
      }
    }
  }
}
```

### Step 3: 添加别名

在同一个 patch 中添加别名映射：

```json
{
  "agents": {
    "defaults": {
      "models": {
        "siliconflow/Qwen/Qwen3-8B": {"alias": "sf-qwen3-8b"},
        "siliconflow/deepseek-ai/DeepSeek-R1-0528-Qwen3-8B": {"alias": "sf-r1-8b"},
        "siliconflow/Qwen/Qwen3-30B-A3B": {"alias": "sf-qwen3-30b"},
        "siliconflow/Qwen/Qwen3-Coder-30B-A3B-Instruct": {"alias": "sf-coder-30b"},
        "siliconflow/deepseek-ai/DeepSeek-V3.2": {"alias": "sf-dsv3"},
        "siliconflow/deepseek-ai/DeepSeek-R1": {"alias": "sf-r1"},
        "siliconflow/Pro/moonshotai/Kimi-K2.5": {"alias": "sf-kimi"},
        "siliconflow/Qwen/Qwen3-Coder-480B-A35B-Instruct": {"alias": "sf-coder-480b"}
      }
    }
  }
}
```

⚠️ **`agents.defaults.models.<id>` 只允许 `alias` 字段！** 其他字段会导致 Gateway 崩溃。

### Step 4: 接入 Fallback 链

将免费模型加入 fallback 链作为兜底：

```json
{
  "agents": {
    "defaults": {
      "model": {
        "fallbacks": [
          "...(现有 fallbacks)...",
          "siliconflow/Qwen/Qwen3-8B",
          "siliconflow/Qwen/Qwen3-30B-A3B"
        ]
      }
    }
  }
}
```

推荐 fallback 策略：优先放免费模型 (Qwen3-8B)，然后放便宜模型 (Qwen3-30B)。

### Step 5: 验证

```bash
# 1. 配置校验
openclaw doctor

# 2. 重启生效
openclaw gateway restart

# 3. 确认状态
openclaw gateway status

# 4. 测试模型切换
# 在聊天中输入: /model sf-kimi
```

---

## 实用 API

### 查询余额

```bash
curl -s 'https://api.siliconflow.cn/v1/user/info' \
  -H 'Authorization: Bearer <API_KEY>' | python3 -c "
import json,sys; d=json.load(sys.stdin)['data']
print(f'充值余额: ¥{d[\"chargeBalance\"]}')
print(f'赠送余额: ¥{d[\"balance\"]}')
print(f'总余额: ¥{d[\"totalBalance\"]}')
"
```

### 查看可用模型

```bash
# 所有 chat 模型
curl -s 'https://api.siliconflow.cn/v1/models?sub_type=chat' \
  -H 'Authorization: Bearer <API_KEY>' | python3 -c "
import json,sys
models = json.load(sys.stdin)['data']
print(f'共 {len(models)} 个 chat 模型')
for m in sorted(models, key=lambda x: x['id']):
    print(f'  {m[\"id\"]}')
"
```

### 测试模型

```bash
curl -s 'https://api.siliconflow.cn/v1/chat/completions' \
  -H 'Authorization: Bearer <API_KEY>' \
  -H 'Content-Type: application/json' \
  -d '{
    "model": "Qwen/Qwen3-8B",
    "messages": [{"role":"user","content":"说OK"}],
    "max_tokens": 5
  }'
```

---

## 添加更多模型

SiliconFlow 有 98+ 个 chat 模型。如需添加更多，先用模型列表 API 查询可用模型，然后按 Step 2 的格式添加到 provider 的 `models` 数组中。

### 热门模型速查

| 模型 | 输入/输出 (¥/M tokens) | 特点 |
|------|----------------------|------|
| `zai-org/GLM-4.6` | 3.5 / 14.0 | 智谱最新旗舰 |
| `Pro/deepseek-ai/DeepSeek-R1` | 4.0 / 16.0 | Pro 加速推理 |
| `moonshotai/Kimi-K2-Thinking` | 4.0 / 16.0 | Kimi 思考模型 |
| `Qwen/Qwen3-235B-A22B-Instruct-2507` | 2.5 / 10.0 | Qwen3 指令模型 |
| `baidu/ERNIE-4.5-300B-A47B` | 2.0 / 8.0 | 百度文心 |
| `stepfun-ai/step3` | 4.0 / 10.0 | 阶跃星辰 Step3 |

---

## 注意事项

1. **免费模型有 QPS 限制**：免费模型的并发数可能受限，适合 fallback 和低频任务
2. **Pro 版本 vs 普通版本**：`Pro/` 前缀的模型使用专用推理集群，速度更快但价格略高
3. **模型 ID 区分大小写**：必须严格匹配，如 `Qwen/Qwen3-8B` 不能写成 `qwen/qwen3-8b`
4. **cost 字段单位**：¥/百万 tokens (1M tokens)

---

**注册链接**：https://cloud.siliconflow.cn/i/ihj5inat （邀请注册双方均获赠额度）
