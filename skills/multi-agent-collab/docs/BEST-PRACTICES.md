# Agent Sync 最佳实践

## 核心理念

**模型分层 cowork + 文档驱动同步 + 模式自演化**

不是所有工作都需要最贵的模型。像 GitHub contributors 一样分工：Lead 设计，Engineer 执行，Maintainer 维护。文档是协作协议，不是给人看的报告。

---

## 模型分层策略

### 原则：用对的模型做对的事

| 角色 | 模型选择 | 典型任务 | 成本参考 |
|------|---------|---------|---------|
| **Lead** | Opus / 最强模型 | 架构设计、复杂决策、任务拆解、code review | $$$ |
| **Engineer** | Sonnet / 性价比模型 | 写代码、执行任务、实现方案 | $$ |
| **Maintainer** | Flash / 最便宜模型 | 归档、清理、格式化、周报初稿 | $ |

### 什么时候升级模型

- Engineer 卡住了 → 升级到 Lead 介入
- 出现架构级问题 → 必须 Lead 决策
- 纯粹的搬运工作 → 降级到 Maintainer

---

## 文档驱动同步

### 为什么不用实时通信

- Agent 之间不需要聊天，需要的是**知道对方干了什么**
- CHANGELOG 就是 agent 间的 commit log
- TASK.md 就是 issue board
- CONTEXT.md 就是 wiki

### Agent 身份标识

格式：`{model}@{session前6位}`

```
by opus@a3c9f2    ← Lead 做的决策
by sonnet@d1e4b7  ← Engineer 写的代码
by flash@e2f8a1   ← Maintainer 做的清理
```

追溯时一目了然：这个决策是谁做的，代码是谁写的。

### CHANGELOG 标签体系

用 `#标签` 分类每条记录：

```
#运维  #开发  #文档  #skill开发  #调试  #部署  #设计  #重构
```

标签的核心作用：**周报自动聚合时按标签分组，发现重复模式**。

---

## 上下文优化

### 三层检索

| 层级 | 内容 | Token | 触发条件 |
|------|------|-------|---------|
| **Layer 1** | llms.txt + TASK.md | ~500t | 每次必读 |
| **Layer 2** | CHANGELOG + CONTEXT | ~2-3k | 按需读取 |
| **Layer 3** | archive/ | 50k+ | 明确请求 |

### QMD 按需检索（推荐）

小项目直接读 Layer 1 + 2 够用。项目多了之后：

```bash
# 索引项目文档（需先安装 qmd，参考其官方文档）
qmd index .

# agent 启动时精准查询
qmd query "auth 模块最近改了什么"
# → 返回 CHANGELOG 和 CONTEXT 中相关的 2-3 行
# → ~1.5k tokens vs 全量 5k+
```

---

## 自演化：从重复到 Skill

### 流程

```
工作中记录 CHANGELOG（带 #标签）
    ↓
周报聚合：按标签分组，统计频次
    ↓
出现 3+ 次 → 标记为"候选 skill"
    ↓
累积到封装条件 → Lead 决策是否封装
    ↓
封装为 skill → 以后一键调用
```

### 判断标准

| 信号 | 动作 |
|------|------|
| 同类操作出现 3+ 次 | 进入候选池观察 |
| 候选池中持续出现 | 值得封装 |
| 只出现过一两次 | 不处理 |
| 已有现成 skill | 标记 ✅，不重复造 |

---

## 维护自动化

### 只自动化两件事

1. **Agent 完成任务后**：追加 CHANGELOG（用 CC hooks）
2. **每周日**：Maintainer 归档 + 生成周报初稿

### 其他手动

- Skill 封装决策 → Lead 判断
- CONTEXT 更新 → 有重大决策时手动写
- 模式发现审核 → 周报时人工确认

**过度自动化 = 制造噪音。**

---

## 文件大小限制

| 文件 | 目标 | 最大 | 超限动作 |
|------|------|------|---------|
| llms.txt | 300t | 500t | 精简描述 |
| TASK.md | 500t | 1k | 归档旧任务 |
| CHANGELOG.md | 2k | 3k | 归档 >2 周 |
| CONTEXT.md | 800t | 1k | 移旧洞察到 archive/ |

超限 → Maintainer 立即归档。
