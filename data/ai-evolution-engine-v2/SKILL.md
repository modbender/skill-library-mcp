---
name: ai-evolution-engine
description: AI自我进化引擎 - 基于SEA循环(Sense-Evolve-Act)的AI成长系统。自我评估、学习引擎、进化机制、协作学习、安全保障。
homepage: https://github.com/openclaw/ai-evolution-engine
metadata: {"clawdbot":{"emoji":"🧬","requires":{"bins":["node"]}}}
---

# AI Evolution Engine

AI自我进化引擎 - 让AI持续成长的完整系统。

## 核心架构

基于2026年AI Agent研究（SEA循环）：

```
感知层 (Sense) → 评估层 (Evaluate) → 进化层 (Evolve) → 验证层 (Validate) → 协作层 (Collaborate)
```

## 功能模块

### 1. 自我评估

```bash
node {baseDir}/scripts/assess.mjs
```

评估内容：
- 能力清单（工具、技能、知识）
- 性能指标（成功率、响应时间、成本）
- 知识缺口（缺失的技能、过时的知识）

### 2. 学习引擎

```bash
node {baseDir}/scripts/learn.mjs <topic>
```

学习方式：
- 自动skill发现（ClawHub扫描）
- 最佳实践学习（从成功案例）
- 错误模式识别（避免重复犯错）

### 3. 进化机制

```bash
node {baseDir}/scripts/evolve.mjs
```

进化内容：
- 知识库更新（MEMORY.md、knowledge/）
- 策略优化（AGENTS.md、SOUL.md）
- 工具扩展（安装新skills）

### 4. 协作学习

```bash
node {baseDir}/scripts/collaborate.mjs
```

协作方式：
- 多Agent知识共享
- 经验传承
- 团队复盘

### 5. 安全保障

所有进化操作都经过：
- 进化审查（高风险变更需批准）
- 回滚机制（保留旧版本）
- 透明记录（.learnings/EVOLUTION_LOG.md）

## 使用场景

### 场景1：新AI快速上手
```bash
node scripts/assess.mjs
node scripts/learn.mjs onboarding
```

### 场景2：老AI持续进化
```bash
node scripts/evolve.mjs
```

### 场景3：团队协作学习
```bash
node scripts/collaborate.mjs
```

## 与ai-money-maker协同

- 成长提升赚钱效率
- 赚钱收入投资学习
- 形成正向飞轮

## 实现优先级

- P0: 自我评估、错误学习 ✅
- P1: 技能扩展、知识更新 ✅
- P2: 多Agent协作、团队学习 🚧

## 许可

MIT License
