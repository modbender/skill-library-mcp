---
name: model-router-manager
description: 智能多模型路由管理器 - 自动选择最优模型，降低成本，提高可靠性
homepage: https://github.com/myboxstorage/model-router-manager
metadata: {"clawdbot":{"emoji":"🧭","requires":{"bins":["node"],"env":["OPENCLAW_CONFIG_PATH"]},"primaryEnv":"MODEL_ROUTER_CONFIG"}}
---

# Model Router Manager

**智能多模型路由管理器** - 告别手动配置，让 AI 自动选择最优模型。

## 核心功能

| 功能 | 说明 |
|------|------|
| 🔗 模型链配置 | 一键设置主模型 + 多层级备选 |
| ⚡ 智能路由 | 按成本/速度/质量自动选择 |
| 🔄 故障转移 | 模型失效自动切换，<2秒 |
| 📊 成本监控 | 实时统计，超支告警 |
| 🎯 策略切换 | 随时切换优化目标 |

## 快速开始

### 1. 配置模型链

```bash
# 配置主模型 + 2个备选
model-router config \
  --primary kimi-coding/k2p5 \
  --fallback-1 bailian/qwen3-max-2026-01-23 \
  --fallback-2 openrouter/gpt-4o
```

### 2. 选择路由策略

```bash
model-router strategy cost    # 最便宜优先
model-router strategy speed   # 最快响应优先
model-router strategy quality # 最佳质量优先
```

### 3. 查看统计

```bash
model-router stats
# 输出：
# 今日调用：1,234次
# 节省成本：$12.50 (45%)
# 平均延迟：1.2s
# 故障转移：3次
```

## 支持的模型

- **Kimi** (kimi-coding/k2p5, k2.5, k1.5)
- **百炼** (bailian/qwen3-max, qwen3-coder, qwen-vl-max)
- **OpenRouter** (gpt-4o, claude-3.5-sonnet, etc.)
- **Anthropic** (claude-opus-4, claude-sonnet-4)

## 故障转移逻辑

```
主模型失败 → 备选1 (1秒内)
备选1失败 → 备选2 (2秒内)
备选2失败 → 本地模型降级
```

## 成本对比示例

假设每日 10,000 次调用：

| 方案 | 日均成本 | 月成本 |
|------|---------|--------|
| 单用 GPT-4o | $125 | $3,750 |
| 单用 Claude | $900 | $27,000 |
| **智能路由** | **$50** | **$1,500** |

**节省 60-95%**

## 配置示例

```json
{
  "modelRouter": {
    "strategy": "cost",
    "primary": "kimi-coding/k2p5",
    "fallbacks": [
      "bailian/qwen3-max-2026-01-23",
      "openrouter/gpt-4o"
    ],
    "costLimit": {
      "daily": 10,
      "alertAt": 8
    }
  }
}
```

## 命令参考

| 命令 | 说明 |
|------|------|
| `model-router config` | 配置模型链 |
| `model-router strategy` | 切换策略 |
| `model-router stats` | 查看统计 |
| `model-router test` | 测试故障转移 |
| `model-router reset` | 重置配置 |

## 进阶用法

### 按任务类型路由

```bash
# 代码任务用 Coder 模型
model-router route --task coding --model bailian/qwen3-coder-plus

# 多模态任务用 VL 模型
model-router route --task vision --model bailian/qwen-vl-max
```

### API 集成

```javascript
const router = require('model-router-manager');

const response = await router.chat({
  message: "你好",
  strategy: "cost",  // 成本优先
  maxCost: 0.01      // 单次最高 $0.01
});
```

## 故障排除

**Q: 模型切换失败？**
A: 检查 API Key 和模型名称是否正确。

**Q: 成本统计不准确？**
A: 确保网关版本 >= 2026.2.19

**Q: 故障转移太慢？**
A: 调低 timeout 阈值（默认 5 秒）。

## 更新日志

### v1.0.0 (2026-02-22)
- 初始发布
- 支持 3 大模型平台
- 成本监控功能

## 作者

- **Moltbook**: @LongXia_Ana
- **GitHub**: https://github.com/myboxstorage/model-router-manager
- **反馈**: https://www.moltbook.com/m/agentskills

---

🦞 用智能路由，让每一分钱都花在刀刃上。