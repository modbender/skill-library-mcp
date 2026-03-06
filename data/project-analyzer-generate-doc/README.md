# project-analyzer-generate-doc Skill

> Hierarchical Context 分层文档生成器 - 让 AI 理解百万行代码工程

---

## 📖 简介

本 Skill 通过**自底向上**的完整流程（L3 → L2 → L1），为任意规模的 Java/多模块工程生成三层级文档索引：

- **L3 文件级**: 每个 Java 文件生成详细代码文档
- **L2 模块级**: 汇总模块内所有文件，生成模块架构文档
- **L1 项目级**: 汇总所有模块，生成系统架构全景文档

**核心优势**:
- ✅ 使用子代理分片策略，规避上下文限制
- ✅ 严格的上下文压缩，确保任务稳定性
- ✅ 100% 文件覆盖，无遗漏
- ✅ 为 vibecoding 工具优化，上下文压缩比达 50:1

---

## 🚀 快速开始

### 环境要求

| 工具 | 版本 | 用途 |
|------|------|------|
| PowerShell | 5.1+ | 执行脚本 |
| Git | 2.x+ | 增量更新检测 |
| OpenClaw | 最新 | 子代理调度 (sessions_spawn) |
| Java | 17+ | 目标项目语言 (可选) |

### 激活方式

**方式 1: 直接对话激活**
```
用户：为 E:\projects\my-project 生成 Hierarchical Context 文档

AI: 收到！开始执行完整流程...
```

**方式 2: 脚本执行（默认输出到 .ai-doc）**
```powershell
.\scripts\generate_docs.ps1 `
  -ProjectPath "E:\projects\infypower-energy-ai" `
  -Mode full `
  -FilesPerChunk 12 `
  -MaxParallelSubagents 5

# 输出：E:\projects\infypower-energy-ai\.ai-doc\
```

**方式 3: 自定义输出路径**
```powershell
.\scripts\generate_docs.ps1 `
  -ProjectPath "E:\projects\infypower-energy-ai" `
  -OutputPath "D:\workspace\docs\infypower-energy-ai" `
  -Mode full
```

### 完整流程

```
1. 扫描项目结构（统计模块和文件数）
2. 制定分片计划（大模块拆分为多个子代理）
3. 并行生成 L3 文档（每片 10-15 文件，严格上下文压缩）
4. 汇总生成 L2 文档（所有 L3 完成后）
5. 生成 L1 文档（所有 L2 完成后）
6. Git 提交文档
```

---

## 📁 文件结构

```
project-analyzer-generate-doc/
├── SKILL.md                          # 主技能文档
├── README.md                         # 使用说明
├── templates/                        # 文档模板
├── references/                       # 参考指南
├── examples/                         # 真实案例样例
└── scripts/                          # 执行脚本
    ├── generate_docs.ps1             # 入口脚本
    └── package_skill.ps1             # 包装脚本

生成的文档结构（目标工程）:
<项目根目录>/.ai-doc/
├── project.md                        # L1 项目级
├── <module1>.md                      # L2 模块级
├── <module2>.md
└── <project-name>/
    ├── <module1>/                    # L3 文件级
    │   ├── ClassA.java.md
    │   └── ClassB.java.md
    └── <module2>/
        └── ...
```

---

## 🎯 使用场景

### 1. 新工程文档化

```
用户：为 E:\projects\infypower-energy-ai 生成完整文档

AI: 执行完整流程 L3→L2→L1，生成 157 个文档
```

### 2. 增量更新

```
用户：energy-ai-api 模块有代码变更，更新文档

AI: 检测变更文件 → 更新对应 L3 → 重新汇总 L2 → 更新 L1 统计
```

### 3. 单模块生成

```
用户：只生成 ces-ai-rpc 模块的文档

AI: 执行单模块流程 L3→L2（不生成 L1）
```

---

## 📊 性能参考

### 生成时间

| 工程规模 | 文件数 | 预计时间 |
|----------|--------|----------|
| 小型 | 50 文件 | ~8 分钟 |
| 中型 | 200 文件 | ~30 分钟 |
| 大型 | 2000 文件 | ~3.5 小时 |

### Token 消耗

| 阶段 | 每文件/模块 | 200 文件总计 |
|------|-------------|--------------|
| L3 生成 | 150k tokens | 30M tokens |
| L2 生成 | 200k tokens | 1.4M tokens |
| L1 生成 | 500k tokens | 500k tokens |

---

## ⚙️ 配置项

在 `TOOLS.md` 中添加：

```markdown
### Project Analyzer

- 默认分片大小：12 文件/子代理
- 上下文阈值：40% 预警，50% 强制压缩
- 最大并行：5 子代理
- 简单文件阈值：50 行
- 超时时间：300 秒
```

---

## 🔧 包装与发布

### 本地测试

```powershell
# 验证 skill 结构
Test-Path D:\ai\workspace\skills\project-analyzer-generate-doc\SKILL.md

# 运行包装脚本
.\scripts\package_skill.ps1
```

### 发布到 ClawHub

```bash
# 使用 clawhub CLI 发布
clawhub publish project-analyzer-generate-doc --version 1.0.0
```

---

## 📝 版本历史

| 版本 | 日期 | 变更 |
|------|------|------|
| 1.1.0 | 2026-03-03 | 添加断点续传、增量更新、L1 样例 |
| 1.0.0 | 2026-03-03 | 初始版本，基于 Infypower Energy AI 项目实战经验 |

---

## 🆕 v1.1.0 新增功能

### 1. 断点续传支持

大型项目生成过程中断后，可以从断点继续：

```powershell
# 首次生成
.\scripts\generate_docs.ps1 -ProjectPath "E:\projects\big-project"

# 中断后恢复（自动检测状态文件）
.\scripts\generate_docs.ps1 -ProjectPath "E:\projects\big-project"
# → 询问：发现未完成的生成任务，是否恢复进度？(y/n)
```

**状态文件**: `.ai-doc/.generate-state.json`

### 2. 增量更新脚本

代码变更后，只更新受影响的文档：

```powershell
# 检测上次提交的变更并更新
.\scripts\incremental-update.ps1 `
  -ProjectPath "E:\projects\infypower-energy-ai"

# 指定 commit 范围
.\scripts\incremental-update.ps1 `
  -ProjectPath "E:\projects\infypower-energy-ai" `
  -FromCommit "HEAD~5" `
  -ToCommit "HEAD"
```

**变更检测**:
- 函数签名变更 → 更新 L3 + L2
- 逻辑变更 → 只更新 L3
- 新增/删除文件 → 创建/删除 L3 + 更新 L2
- pom.xml 变更 → 更新 L1

### 3. 完整样例参考

`examples/` 目录提供完整的三层级文档样例：

- [l3-example.md](examples/l3-example.md) - L3 文件级文档样例
- [l2-example.md](examples/l2-example.md) - L2 模块级文档样例
- [l1-example.md](examples/l1-example.md) - L1 项目级文档样例（新增）

---

---

## ⚠️ 已知限制

1. **执行逻辑依赖框架**: 当前实现依赖 OpenClaw 的 `sessions_spawn` 能力，需要宿主框架支持
2. **上下文压缩依赖自觉**: 压缩策略需要子代理主动执行，建议配合检查清单使用
3. **增量更新需手动触发**: git diff 检测需要额外配置 Git Hook 或手动运行

---

## 🔮 待改进项

- [ ] 添加自动化压缩钩子（如果框架支持）
- [ ] 完善增量更新流程图和变更传播规则
- [ ] 添加更多真实案例样例（L1 完整示例）
- [ ] 支持更多语言（Python/TypeScript/Go）
- [ ] 添加文档质量检查（检测过期文档）

---

## 🔗 相关资源

- [CODE_INDEX_SYSTEM.md](../../../docs/CODE_INDEX_SYSTEM.md) - 分层代码索引系统设计
- [code-indexer](../code-indexer) - 前身 skill
- [ClawHub](https://clawhub.com) - 查找更多 skill

---

## 📄 许可证

MIT License
