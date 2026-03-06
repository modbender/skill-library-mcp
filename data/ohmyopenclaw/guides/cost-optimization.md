# Cost Optimization Guide

## 适用场景

- 需要控制 API 调用成本
- 大量使用 AI 服务，预算有限
- 想要最大化 token 使用效率
- 生产环境需要成本可预测性

## 配置变更

本指南将修改以下文件：

1. `openclaw.json` - 配置成本控制策略
2. `workspace/AGENTS.md` - 添加成本意识规则

## 成本优化策略

### 1. 模型 Fallback 策略

使用成本分级：

```
┌─────────────────────────────────────┐
│       Cost Optimization Flow        │
│                                     │
│  1. Analyze task complexity         │
│     ├─ Simple: haiku/turbo          │
│     ├─ Medium: sonnet/plus          │
│     └─ Complex: opus/max            │
│                                     │
│  2. Check context size              │
│     ├─ Small (<10K): any model      │
│     ├─ Medium (10-50K): mid-tier    │
│     └─ Large (>50K): specialized    │
│                                     │
│  3. Apply fallback chain            │
│     └─ Try cheaper models first     │
└─────────────────────────────────────┘
```

### 2. 缓存策略

启用智能缓存：

```json
{
  "cache": {
    "enabled": true,
    "ttl": 3600,
    "strategies": {
      "exact": true,
      "semantic": true,
      "threshold": 0.95
    }
  }
}
```

### 3. Token 优化

- 压缩上下文
- 移除重复信息
- 使用简洁提示词

## 成本分级表

### Anthropic Models

| Model | Input ($/1M) | Output ($/1M) | Best For |
|-------|--------------|---------------|----------|
| claude-opus-4 | $15 | $75 | 复杂推理、关键任务 |
| claude-sonnet-4 | $3 | $15 | 日常开发、平衡选择 |
| claude-haiku-4 | $0.25 | $1.25 | 简单任务、高频调用 |

### Chinese Models

| Model | Input (¥/1M) | Output (¥/1M) | Best For |
|-------|--------------|---------------|----------|
| qwen-max | ¥40 | ¥40 | 中文复杂任务 |
| qwen-plus | ¥4 | ¥12 | 中文日常任务 |
| qwen-turbo | ¥2 | ¥6 | 中文快速任务 |
| deepseek-chat | ¥1 | ¥2 | 超低成本通用 |
| deepseek-coder | ¥1 | ¥2 | 代码专用 |

### OpenAI Models

| Model | Input ($/1M) | Output ($/1M) | Best For |
|-------|--------------|---------------|----------|
| gpt-4o | $5 | $15 | 多模态任务 |
| gpt-4o-mini | $0.15 | $0.6 | 快速轻量任务 |

## 安装命令

### 1. 更新 openclaw.json

```json
{
  "model": {
    "default": "claude-sonnet-4",
    "fallback": "claude-haiku-4",
    "costOptimization": {
      "enabled": true,
      "strategies": {
        "simple_tasks": "claude-haiku-4",
        "medium_tasks": "claude-sonnet-4",
        "complex_tasks": "claude-opus-4"
      },
      "maxBudgetPerDay": 10.00,
      "alertThreshold": 0.8
    }
  },
  "cache": {
    "enabled": true,
    "ttl": 3600,
    "maxSize": "100MB"
  },
  "logging": {
    "costTracking": true
  }
}
```

### 2. 更新 AGENTS.md

添加成本意识规则：

```markdown
## Cost Optimization

### 模型选择原则

1. **简单任务** → 使用 haiku/turbo
   - 简单问答
   - 格式转换
   - 小修改

2. **中等任务** → 使用 sonnet/plus
   - 代码生成
   - 重构
   - 文档编写

3. **复杂任务** → 使用 opus/max
   - 架构设计
   - 复杂推理
   - 关键决策

### Token 优化

- 使用简洁提示词
- 避免重复上下文
- 压缩历史对话
- 利用缓存

### 成本监控

每日检查成本日志：
```bash
cat ~/.openclaw/logs/costs.log
```
```

### 3. 创建成本监控脚本

创建 `~/.openclaw/scripts/check-costs.sh`:

```bash
#!/bin/bash

# 今日成本统计
echo "=== 今日成本统计 ==="
echo ""

# 读取配置
DAILY_BUDGET=$(cat ~/.openclaw/openclaw.json | grep -o '"maxBudgetPerDay": [0-9.]*' | grep -o '[0-9.]*')

# 模拟成本数据（实际应从日志读取）
SPENT_TODAY=5.23

echo "预算: \$$DAILY_BUDGET"
echo "已用: \$$SPENT_TODAY"
echo "剩余: \$$(echo "$DAILY_BUDGET - $SPENT_TODAY" | bc)"
echo ""

# 使用百分比
PERCENTAGE=$(echo "scale=1; $SPENT_TODAY / $DAILY_BUDGET * 100" | bc)
echo "使用率: ${PERCENTAGE}%"

if (( $(echo "$PERCENTAGE > 80" | bc -l) )); then
  echo "⚠️  接近预算上限！"
fi
```

## 验证步骤

### 1. 验证配置

```bash
cat ~/.openclaw/openclaw.json | grep -A 10 "costOptimization"
```

### 2. 测试成本优化

```
用最便宜的模型告诉我 2+2 等于几
```

Expected:
- AI 使用 claude-haiku-4 或 deepseek-chat
- 成本日志记录低消耗

### 3. 测试缓存

重复相同问题：

```
什么是 REST API？
```

第二次应该更快，且成本更低（如果命中缓存）。

### 4. 检查成本日志

```bash
cat ~/.openclaw/logs/costs.log | tail -10
```

## 使用示例

### 明确指定成本优先

```
用最便宜的模型翻译这句话：Hello World
```

### 复杂任务不省钱

```
用最好的模型设计一个分布式系统的架构
```

### 查看成本统计

```
显示今天的 API 调用成本
```

### 设置预算提醒

```
当今日成本超过 $8 时提醒我
```

## 成本估算示例

### 简单对话 (1000 tokens)

- **Opus**: $0.015 + $0.075 = $0.09
- **Sonnet**: $0.003 + $0.015 = $0.018
- **Haiku**: $0.00025 + $0.00125 = $0.0015
- **DeepSeek**: ¥0.001 + ¥0.002 ≈ $0.0004

**节省**: 使用 Haiku 比 Opus 省 98%

### 代码生成 (5000 tokens)

- **Opus**: $0.075 + $0.375 = $0.45
- **Sonnet**: $0.015 + $0.075 = $0.09
- **Haiku**: $0.00125 + $0.00625 = $0.0075
- **DeepSeek Coder**: ¥0.005 + ¥0.01 ≈ $0.002

**节省**: 使用 DeepSeek Coder 比 Opus 省 99.5%

### 长文档分析 (50000 tokens)

- **Opus**: $0.75 + $3.75 = $4.50
- **Sonnet**: $0.15 + $0.75 = $0.90
- **Haiku**: $0.0125 + $0.0625 = $0.075
- **Qwen-Max**: ¥2 + ¥2 ≈ $0.28

**节省**: 使用 Qwen-Max 比 Opus 省 94%

## 进阶配置

### 分时策略

不同时段使用不同模型：

```json
{
  "costOptimization": {
    "schedule": {
      "peak_hours": {
        "time": "09:00-18:00",
        "model": "claude-sonnet-4"
      },
      "off_peak": {
        "time": "18:00-09:00",
        "model": "claude-haiku-4"
      }
    }
  }
}
```

### 用户级预算

```json
{
  "costOptimization": {
    "perUserBudget": {
      "user1": 20.00,
      "user2": 5.00
    }
  }
}
```

### 自动降级

当接近预算上限时自动降级：

```json
{
  "costOptimization": {
    "autoDowngrade": true,
    "downgradeThreshold": 0.9,
    "downgradeModel": "claude-haiku-4"
  }
}
```

## 故障排除

### 成本超支

1. 检查 maxBudgetPerDay 设置
2. 查看成本日志找出高消耗任务
3. 启用更激进的 fallback

### 缓存未命中

1. 检查缓存配置
2. 验证 TTL 设置
3. 查看缓存命中率

### 质量下降

如果简单模型质量不够：
1. 调整任务分类规则
2. 提高复杂任务的判断标准
3. 为关键任务强制使用高级模型

## 相关指南

- [chinese-providers.md](chinese-providers.md) - 中国模型通常更便宜
- [memory-optimized.md](memory-optimized.md) - 减少重复请求
- [agent-swarm.md](agent-swarm.md) - 为不同 Worker 选择不同模型

## 成本监控工具

### 日志格式

```
[2026-02-27 10:30:45] model=claude-sonnet-4 input=1500 output=800 cost=$0.0165
[2026-02-27 10:31:12] model=claude-haiku-4 input=500 output=300 cost=$0.0010 (cached)
```

### 可视化面板

集成 Grafana 或类似工具：
- 实时成本曲线
- 模型使用分布
- 预算消耗进度
- 异常告警
