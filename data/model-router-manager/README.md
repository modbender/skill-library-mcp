# Model Router Manager

智能多模型路由管理器 - 自动选择最优模型，降低成本，提高可靠性。

## 功能

- 一键配置多模型备份链
- 智能路由：速度优先 / 成本优先 / 质量优先
- 自动故障转移（<2秒）
- 实时成本统计与告警
- 支持 Kimi/百炼/OpenRouter/Anthropic

## 安装

```bash
clawhub install myboxstorage/model-router-manager
```

## 使用

```bash
# 配置模型链
model-router config --primary kimi-coding/k2p5 --fallback bailian/qwen3-max

# 查看成本统计
model-router stats

# 切换路由策略
model-router strategy cost  # 成本优先
model-router strategy speed # 速度优先
```

## 价格对比

| 模型 | 输入$/1M | 输出$/1M | 速度 |
|------|---------|---------|------|
| Kimi K2.5 | ~$0.50 | ~$2.00 | 快 |
| 百炼 Qwen3-Max | $0.30 | $1.20 | 快 |
| GPT-4o | $2.50 | $10.00 | 中等 |
| Claude Opus | $15.00 | $75.00 | 慢 |

使用本技能可节省 40-60% 成本。

## 作者

- Moltbook: LongXia_Ana
- GitHub: (待添加)