---
name: session-cleanup
description: 定期清理过期会话，评估并保存有价值信息，自动清理无价值会话。
---

# Session Cleanup

定期检查和清理过期会话，评估会话价值并保存重要信息。

## 能力轮廓

- **输入**：会话目录路径
- **输出**：清理报告 + 保存的有价值会话
- **核心**：过期检测 → 价值评估 → 选择性清理

## 工作流

```
1. 扫描会话目录
2. 检查过期会话（7天无活动）
3. 评估会话价值（关键词匹配）
4. 保存有价值会话到记忆
5. 清理无价值会话
6. 生成报告
```

## 目标目录

| 目录 | 说明 |
|------|------|
| ~/.openclaw/cron/runs/ | 定时任务运行记录 |
| ~/.openclaw/delivery-queue/ | 消息投递队列 |
| ~/.openclaw/telegram/ | Telegram 会话数据 |
| ~/.openclaw/subagents/ | 子智能体会话 |

## 过期规则

- **cron runs**: 超过 3 天
- **delivery-queue**: 超过 1 天（已完成/失败的）
- **telegram**: 超过 7 天
- **subagents**: 超过 7 天

## 价值评估关键词

| 类别 | 关键词 |
|------|--------|
| 重要决策 | decision, important, remember, 重要, 决策 |
| 学习 | learn, study, understand, 学习, 理解 |
| 问题解决 | fix, bug, error, 修复, 问题, 错误 |
| 创建 | create, build, new, 创建, 新建 |

## 主动性

- 每周执行一次
- 自动评估并保存有价值内容
- 汇报清理结果

## 使用方式

```bash
# 手动执行
~/.openclaw/workspace/skills/session-cleanup/cleanup.sh

# 配置定时任务（每周日凌晨3点）
cron job add session-cleanup "0 3 * * 0" ~/.openclaw/workspace/skills/session-cleanup/run.sh
```
