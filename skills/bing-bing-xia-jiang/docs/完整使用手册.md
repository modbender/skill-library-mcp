# AI协作操作系统 - 完整使用手册

## 1. 系统概述

AI协作操作系统包含四个核心系统：
- **统一记忆系统**：五层记忆架构（L0→L1→L2→L3→L4）
- **信息信号识别系统**：信号识别、模式发现、世界观构建
- **工作流资产沉淀系统**：隐性知识显性化、方法论构建
- **个人目标追踪系统**：动机解析、AI镜像、未来预测

## 2. 快速开始

```typescript
import { AICollaborationSystem } from './dist/index';

const ai = new AICollaborationSystem('my_system');
```

## 3. 统一记忆系统

```typescript
// L0 闪存
ai.memory.setVariable('key', 'value');
ai.memory.getVariable('key');

// L1 工作记忆
ai.memory.addToL1('任务', '完成文档', 'task', 3);

// L2 经验记忆
ai.memory.addToL2('经验', '数据', 'insight', 4, ['tag'], 'signal');

// L3 知识记忆
ai.memory.addToL3({ category: 'methodology', key: '方法论', value: {...}, importance: 5 });

// L4 智慧记忆
ai.memory.addToL4({ category: 'insight', key: '洞察', value: {...}, importance: 5 });

// 查询
ai.memory.queryAll('关键词');
```

## 4. 信息信号识别

```typescript
const signals = [
  { title: '信号标题', source: '来源', timeSensitivity: 'immediate', impactDepth: 'worldview', actionability: 8, compoundValue: 9 }
];

const report = ai.dailyScan(signals);
console.log(report.signals);
```

## 5. 工作流资产沉淀

```typescript
const tasks = ['任务1', '任务2'];
const responses = [
  { operation: '步骤', experience: '经验', decision: '决策', thinking: '思维', value: '价值' }
];

const report = ai.dailyWorkflow(tasks, responses);
console.log(report.methodologies);
```

## 6. 个人目标追踪

```typescript
const goals = [{ name: '目标', priority: 8, progress: 30 }];
const timeLog = { career: 50, family: 20, health: 5 };
const ideal = { career: 35, family: 25, health: 15 };

const energy = ai.dailyGoalTracking(goals, timeLog, ideal);
console.log(energy);
```

## 7. AI镜像洞察

```typescript
const insight = ai.generateInsight();
console.log(insight.observation);
console.log(insight.suggestion);
```

## 8. 健康检查

```typescript
const health = ai.healthCheck();
console.log(health);
```
