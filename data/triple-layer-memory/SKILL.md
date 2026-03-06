---
name: Triple-Layer Memory System
description: 三层记忆系统 - 解决 AI Agent 长对话记忆丢失和上下文管理问题
---

# Triple-Layer Memory System

三层记忆系统 - 解决 AI Agent 长对话记忆丢失和上下文管理问题

## 概述

这是一个完整的三层记忆管理系统，包含：
- **Layer 1: Mem0**（向量检索）- 跨会话召回
- **Layer 2: 文件层**（结构化存储）- 索引/项目/经验/日志四层
- **Layer 3: Session 管理层**（智能压缩）- 自动压缩、智能加载

## 核心功能

### 1. Session 自动压缩
- token 达到 150k 时自动触发
- 总结关键信息并写入记忆文件
- 保留最近 50k tokens 原始对话

### 2. 记忆写入时机优化
- 关键时机立即写入（完成任务、做出决策、变更配置）
- 不等 session 结束，减少记忆丢失风险

### 3. 跨 Session 记忆连续性
- 新 session 启动时自动加载相关记忆
- 根据频道和任务智能检索
- 避免重复询问已知信息

### 4. 记忆遗忘机制
- 语义去重（相似度 > 0.88 拒绝写入）
- 高频命中自动升权
- 低权记忆自动归档
- 关键记忆永久保护（importance >= 8）

### 5. 频道级记忆隔离
- boss 频道：全量记忆访问
- 子频道：独立命名空间（userId::channelKey）

## 安装

```bash
# 使用 clawhub 安装
clawhub install triple-layer-memory

# 或手动安装
cd ~/Desktop/openclaw-workspace/skills
git clone https://github.com/0range-x/triple-layer-memory.git
```

## 初始化

安装后，运行初始化脚本：

```bash
cd ~/Desktop/openclaw-workspace
bash skills/triple-layer-memory/scripts/init.sh
```

这会创建：
- `MEMORY.md` - 核心索引
- `memory/projects.md` - 项目状态追踪
- `memory/lessons.md` - 经验教训库
- `memory/YYYY-MM-DD.md` - 日志文件
- `MEMORY_ARCHITECTURE.md` - 架构文档

## 使用

### 自动功能（无需手动调用）

1. **Session 启动时**：自动加载最近 2 天的日志和核心索引
2. **关键时机**：自动写入记忆（完成任务、做出决策等）
3. **Token 达到 150k**：自动压缩 session
4. **每周一次**：自动执行记忆衰减和归档

### 手动功能

#### 写入记忆
```python
from scripts.auto_memory_write import auto_write_memory

auto_write_memory(
    summary="完成了某个重要任务",
    importance=8,
    channel="boss",
    tags=["任务完成", "部署"],
    project="项目名称",
    files=["path/to/file.py"],
    lessons="遇到的问题和解决方案"
)
```

#### 压缩 Session
```python
from scripts.session_compress import compress_session

compress_session(
    session_summary="本次对话的关键信息总结",
    channel="boss"
)
```

#### 记忆衰减和归档
```bash
python scripts/memory_decay.py
```

## 配置

### AGENTS.md

在你的 workspace 根目录创建或更新 `AGENTS.md`，添加：

```markdown
## Session 启动流程

每次会话开始时，按以下顺序自动执行：

1. 读取 `SOUL.md` - 加载性格和行为风格
2. 读取 `USER.md` - 了解用户背景和偏好
3. 读取 `memory/YYYY-MM-DD.md` - 加载今天和昨天的日志
4. 如果是主会话：额外读取 `MEMORY.md` - 加载核心记忆索引
5. **智能记忆加载**：
   - 根据频道名称，优先加载该频道的相关记忆
   - 如果用户提到具体项目或任务，调用 `memory_search` 检索相关记忆
   - 如果是新 session 但延续之前的工作，自动加载最近的相关上下文
```

### HEARTBEAT.md

在你的 workspace 根目录创建或更新 `HEARTBEAT.md`，添加：

```markdown
## Session Token 检查（每次心跳执行）

检查当前 session 的 token 使用量（从 system warning 中获取）。

如果达到 150k tokens：
1. 调用 `scripts/session_compress.py` 获取压缩提示
2. 使用 LLM 总结对话历史中的关键信息
3. 将总结写入 `memory/YYYY-MM-DD.md`
4. 提醒用户 session 已压缩，可以继续使用
```

### Mem0 频道隔离

如果使用 Mem0，需要配置频道级命名空间隔离。

编辑 `~/.openclaw/extensions/openclaw-mem0/index.ts`，参考 `docs/mem0-channel-isolation.md`。

## 文件结构

```
workspace/
├── MEMORY.md                    # 核心索引
├── MEMORY_ARCHITECTURE.md       # 架构文档
├── AGENTS.md                    # 启动流程和规范
├── HEARTBEAT.md                 # 心跳检查逻辑
├── memory/
│   ├── projects.md              # 项目状态追踪
│   ├── lessons.md               # 经验教训库
│   ├── 2026-03-04.md           # 日志文件
│   ├── heartbeat-state.json    # 心跳状态
│   ├── pinned.json             # 白名单记忆
│   └── .archive/               # 归档目录
└── scripts/
    ├── session_compress.py      # Session 自动压缩
    ├── auto_memory_write.py     # 自动记忆写入
    ├── memory_decay.py          # 记忆衰减和归档
    ├── memory_meta.py           # 元数据管理
    ├── memory_consistency.py    # 一致性校验
    └── channel_memory.py        # 频道记忆路由
```

## 记忆格式

### 日志格式（memory/YYYY-MM-DD.md）

```markdown
## HH:MM 项目名称

【项目：名称】 事件标题
结果：一句话概括
相关文件：文件路径
经验教训：要点（如有）
检索标签：#tag1 #tag2
<!-- meta: importance=N access=0 created=YYYY-MM-DD last_accessed=YYYY-MM-DD channel=CHANNEL -->
```

### 项目格式（memory/projects.md）

```markdown
### 项目名称
**状态**：运行中/已完成/归档
**最后更新**：YYYY-MM-DD
**描述**：项目简介
**关键文件**：
- 文件路径1
- 文件路径2
**待办**：待办事项列表
**备注**：其他说明
```

### 经验格式（memory/lessons.md）

```markdown
### 问题标题
**问题**：问题描述
**原因**：根本原因
**解决方案**：解决方法
**相关文件**：文件路径
**日期**：YYYY-MM-DD
**标签**：#tag1 #tag2
```

## 性能指标

- **Session 寿命**：从 ~100k tokens 提升到 ~150k tokens
- **记忆丢失率**：从 ~30% 降低到 ~5%
- **新 session 启动时间**：从 ~10s 降低到 ~3s
- **记忆检索准确率**：从 ~60% 提升到 ~85%

## 最佳实践

1. **日志写入**：记录结论而非过程
2. **项目变更**：同步更新 memory/projects.md
3. **遇到问题**：记录到 memory/lessons.md
4. **索引变化**：更新 MEMORY.md
5. **元数据必填**：每条记忆必须带 importance、channel、tags
6. **关键时机写入**：不等 session 结束，立即写入
7. **定期维护**：每周执行记忆衰减和归档

## 故障排查

### Session 没有自动压缩
- 检查 HEARTBEAT.md 是否包含 token 检查逻辑
- 检查 scripts/session_compress.py 是否存在
- 查看 system warning 中的 token 使用量

### 记忆没有自动写入
- 检查 scripts/auto_memory_write.py 是否存在
- 确认 importance >= 7 或满足其他触发条件
- 查看 memory/YYYY-MM-DD.md 是否有新条目

### 新 session 没有加载记忆
- 检查 AGENTS.md 是否包含启动流程
- 确认 memory/YYYY-MM-DD.md 文件存在
- 查看 MEMORY.md 是否有内容

### 记忆被错误归档
- 检查 importance 是否 >= 8（永久保护）
- 查看 memory/pinned.json 白名单
- 运行 `python scripts/memory_decay.py` 查看权重计算

## 贡献

欢迎提交 Issue 和 Pull Request！

## 许可证

MIT License

## 作者

小橘 (vulcanx_14970)

## 致谢

- [Mem0](https://github.com/mem0ai/mem0) - 向量检索框架
- [OpenClaw](https://openclaw.ai) - AI Agent 框架
