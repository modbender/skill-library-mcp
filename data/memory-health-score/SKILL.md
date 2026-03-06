---
name: Memory Health Score — 记忆健康度评分
description: 一个总分让用户快速判断 Agent 记忆系统健康状况。
---

# Memory Health Score — 记忆健康度评分

## 概述
一个总分让用户快速判断 Agent 记忆系统健康状况。

## 评分维度 (总分 100)

### 1. 完整性 (30分)
- **MEMORY.md 存在且有内容** (10分)
- **memory/INDEX.md 存在** (5分)
- **近 7 天有日志文件** (10分)
- **P0 标记使用率** (5分) — 至少 3 个 P0 项

### 2. 新鲜度 (25分)
- **今日日志已创建** (10分)
- **MEMORY.md 最近 7 天内更新** (10分)
- **INDEX.md 最近 3 天内更新** (5分)

### 3. 结构化 (20分)
- **任务系统 (.issues/) 存在** (10分)
- **至少 3 个 open issue** (5分)
- **心跳配置正确** (5分)

### 4. 密度 (15分)
- **MEMORY.md 行数 50-500** (10分) — 太少=信息不足，太多=需压缩
- **日志文件平均长度 20-200 行** (5分)

### 5. 一致性 (10分)
- **INDEX.md 与 MEMORY.md 项目一致** (5分)
- **issue 文件与 INDEX.md 一致** (5分)

## 健康等级

| 分数 | 等级 | 状态 | 建议 |
|------|------|------|------|
| 90-100 | 🟢 优秀 | 记忆系统运转良好 | 保持当前节奏 |
| 70-89 | 🟡 良好 | 基本健康，有改进空间 | 检查低分项 |
| 50-69 | 🟠 警告 | 存在明显问题 | 立即优化 |
| 0-49 | 🔴 危险 | 记忆系统失效 | 紧急修复 |

## 使用方法

```bash
# 运行评分
openclaw cron add --name "memory-health-check" \
  --cron "0 9 * * *" --tz "Asia/Shanghai" \
  --session isolated --agent main \
  --message "运行记忆健康度评分，生成报告并更新 memory/health-score.json"
```

## 输出格式

```json
{
  "timestamp": "2026-03-01T09:00:00Z",
  "totalScore": 85,
  "grade": "良好",
  "dimensions": {
    "completeness": { "score": 28, "max": 30, "issues": ["缺少 P0 标记"] },
    "freshness": { "score": 25, "max": 25, "issues": [] },
    "structure": { "score": 15, "max": 20, "issues": ["open issue 不足"] },
    "density": { "score": 12, "max": 15, "issues": ["MEMORY.md 过长"] },
    "consistency": { "score": 5, "max": 10, "issues": ["INDEX 与 MEMORY 不一致"] }
  },
  "recommendations": [
    "添加更多 P0 标记到 MEMORY.md",
    "创建至少 3 个 open issue",
    "压缩 MEMORY.md，移除过时信息"
  ]
}
```

## 自动修复建议

评分 <70 时，自动触发：
1. **记忆压缩** — 合并重复内容
2. **索引重建** — 同步 INDEX.md
3. **任务清理** — 关闭过期 issue

## 集成到 AgentAwaken

在 Dashboard 显示：
- 大号分数 (85/100)
- 彩色进度条
- 各维度雷达图
- 一键修复按钮
