# Causal Graph Auto-Builder — 因果图谱自动构建

> 降低 Knowledge Graph 维护成本，自动发现事件因果关系

## 概述

从日志和记忆文件中自动提取**事件、实体、因果关系**，构建知识图谱。

## 核心功能

### 1. 实体识别
- **人物**: 瓜农, 龙虾, Jason Zuo
- **项目**: AgentAwaken, NeuroBoost, ClawWork
- **工具**: GitHub, Vercel, ClawHub
- **概念**: 永续记忆, 三层架构, P0 标记

### 2. 事件提取
```
[2026-02-22] 实施永续记忆增强
[2026-02-26] NeuroBoost v5.0 发布
[2026-03-01] 创建 agentawaken repo
```

### 3. 因果关系推断
```
ClawHub 超时 → 检查版本 → 发现已发布
永续记忆增强 → 记忆健康度提升 → 任务完成率提升
```

## 图谱结构

### 节点类型
- **Entity** (实体): 人、项目、工具
- **Event** (事件): 带时间戳的动作
- **Concept** (概念): 抽象想法

### 边类型
- **causes** (导致): A → B
- **enables** (使能): A 让 B 成为可能
- **requires** (需要): A 依赖 B
- **relates** (相关): A 与 B 有关

## 自动构建流程

### 输入
- `memory/YYYY-MM-DD.md` (日志)
- `MEMORY.md` (长期记忆)
- `.issues/open-*.md` (任务)

### 处理
1. **NER (命名实体识别)** — 提取人名、项目名
2. **事件抽取** — 识别动作和时间
3. **因果推断** — 分析前后关系
4. **去重合并** — 同一实体不同表述合并

### 输出
```json
{
  "nodes": [
    { "id": "agent-awaken", "type": "project", "label": "AgentAwaken" },
    { "id": "vercel", "type": "tool", "label": "Vercel" },
    { "id": "deploy-event", "type": "event", "label": "部署到 Vercel", "timestamp": "2026-03-01" }
  ],
  "edges": [
    { "from": "agent-awaken", "to": "vercel", "type": "requires" },
    { "from": "deploy-event", "to": "agent-awaken", "type": "affects" }
  ]
}
```

## 实现方案

### 方案 A: 规则匹配（快速）
```javascript
// 简单正则匹配
const patterns = {
  cause: /因为|由于|导致|所以/,
  enable: /使得|让|允许/,
  require: /需要|依赖|基于/
};
```

### 方案 B: LLM 提取（准确）
```javascript
// 用 LLM 分析文本
const prompt = `
从以下文本提取因果关系，输出 JSON:
{ "cause": "...", "effect": "...", "confidence": 0.9 }

文本: ${text}
`;
```

### 方案 C: 混合（推荐）
- 规则匹配快速筛选候选
- LLM 验证和补充细节
- 人工审核低置信度关系

## 使用示例

```bash
# 构建图谱
node skills/causal-graph/build.mjs

# 查询
node skills/causal-graph/query.mjs "AgentAwaken 的依赖"
# 输出: Vercel, GitHub, Next.js, pnpm

# 可视化
node skills/causal-graph/visualize.mjs > graph.html
```

## 集成到 AgentAwaken

在 Dashboard 显示：
- 交互式知识图谱
- 点击节点查看详情
- 高亮因果链路
- 时间轴动画

## 维护成本对比

| 方式 | 初始成本 | 维护成本 | 准确度 |
|------|----------|----------|--------|
| 手动维护 | 高 | 极高 | 高 |
| 规则匹配 | 低 | 中 | 中 |
| LLM 提取 | 中 | 低 | 高 |
| 混合方案 | 中 | 低 | 极高 |

**结论**: 混合方案最优，初期投入中等，长期维护成本低。

## 下一步

1. 实现基础规则匹配版本
2. 集成 LLM 提取
3. 添加可视化界面
4. 接入 AgentAwaken Dashboard
