---
name: guide-creator
description: "通用项目文档指南生成器：为任何项目创建和维护标准化的 guide 文档体系（start.md + guide/ 目录），覆盖设计理念、技术架构、更新日志、踩坑记录等完整生命周期。支持三种模式：(1) 初始化模式 — 一键创建标准化文档骨架；(2) 更新模式 — 追加 changelog/pitfalls/版本号同步；(3) 上下文恢复 — AI 在新对话中快速理解项目全貌。触发关键词：'初始化项目guide'、'创建项目文档'、'更新guide'、'总结经验教训'、'project guide'、'init guide'、'update guide'、'context recovery'。当用户说'帮我建一套项目文档'、'记录这次的更新和踩坑'、'新对话帮我恢复项目上下文'时触发。"
---

# Guide Creator — 通用项目文档指南生成器

为任何项目创建和维护标准化的 guide 文档体系。提炼自实际项目（福音雪镇）经过 20+ 版本迭代验证的文档最佳实践。

## Quick Start

### 模式 1：初始化项目文档

```
用户说："初始化项目guide" / "创建项目文档" / "init guide"
```

1. 运行 `scripts/init_guide.py --project-name "项目名" --type game|web|cli|lib|general --root /path/to/project`
2. 自动创建 `start.md` + `guide/` 目录及全部模板文件
3. 按提示填充关键内容（启动命令、文件清单、架构图等）

### 模式 2：更新项目文档

```
用户说："更新guide" / "总结经验教训" / "update guide"
```

1. 运行 `scripts/update_guide.py --action add-changelog|add-pitfall|bump-version|sync-files --root /path/to/project`
2. 或直接告诉 AI 本次更新内容，由 AI 生成格式化条目并追加

### 模式 3：上下文恢复

```
AI 在新对话开始时，按推荐顺序读取文档快速理解项目。
```

推荐阅读顺序：`start.md` → `guide/guide.md` → `guide/08-changelog.md` → `guide/09-pitfalls.md` → 按需读取 01~07

## Key Rules

### 文件结构规范

```
project-root/
├── start.md                    # 启动说明（怎么跑 + 文件清单）
└── guide/
    ├── guide.md                # 项目总览索引（入口文件）
    ├── 01-design.md            # 设计理念（必须）
    ├── 02-{domain}.md          # 按项目类型（可选）
    ├── 03-{domain}.md          # 按项目类型（可选）
    ├── 04-{domain}.md          # 按项目类型（可选）
    ├── 05-{domain}.md          # 按项目类型（可选）
    ├── 06-tech.md              # 技术架构（必须）
    ├── 07-plan.md              # 开发计划（必须）
    ├── 08-changelog.md         # 更新日志（必须）
    └── 09-pitfalls.md          # 踩坑记录（必须）
```

**必须文件**（所有项目类型）：`start.md`、`guide.md`、`01-design.md`、`06-tech.md`、`07-plan.md`、`08-changelog.md`、`09-pitfalls.md`

**可选文件**（02~05，按项目类型）：
- 游戏：地图(02)、NPC/实体(03)、属性/数值(04)、AI系统(05)
- Web应用：路由(02)、组件(03)、状态管理(04)、API(05)
- CLI/库：命令(02)、核心模块(03)、数据模型(04)、算法(05)
- 通用：架构(02)、核心模块(03)、数据模型(04)、逻辑(05)

### 格式约束

1. **版本号**：`vX.Y` 格式（如 v2.3），记录在 `guide.md` 元信息和 `08-changelog.md` 顶部
2. **Changelog 条目格式**：`## vX.Y — 标题摘要 (YYYY-MM-DD)` + 按子系统分组 + 🐛Bug修复 + 📝代码改动
3. **Pitfall 条目格式**：`## 🔥 坑N：标题` + 问题现象 + 问题根因 + 解决方案 + ⚠️开发注意 + **加粗通用原则**
4. **文档索引表**：guide.md 中维护完整的文档索引表（文档名 + 内容摘要 + 说明）

### 更新时机

| 事件 | 必须更新 | 可选更新 |
|------|----------|----------|
| 完成功能开发 | 08-changelog | guide.md版本号, start.md文件清单 |
| 修复Bug | 08-changelog | 09-pitfalls（如有经验教训） |
| 踩坑/发现问题 | 09-pitfalls | — |
| 新增文件 | start.md文件清单 | 06-tech.md文件结构 |
| 版本发布 | guide.md版本号, 08-changelog | 07-plan checklist |
| 架构变更 | 06-tech.md | guide.md架构图 |

### 文件保护

- **不要删除已有的 changelog/pitfalls 条目**，只追加
- **guide.md 的文档索引表中引用的文件必须存在且非空**
- changelog >500 行时归档到 `guide/archive/`
- pitfalls >30 条时按类型分组（UI类/数据类/LLM类/性能类等）

## 详细模式指令

完整的模式执行指令请参考以下文件：

- **Guide 体系规范**：[references/guide-spec.md](references/guide-spec.md) — 文件结构、章节要求、版本号规范、更新触发规则、归档策略
- **文档模板**：[references/templates/](references/templates/) — 所有文档的标准模板
  - [start-template.md](references/templates/start-template.md) — start.md 模板
  - [guide-template.md](references/templates/guide-template.md) — guide.md 模板
  - [changelog-template.md](references/templates/changelog-template.md) — changelog 模板
  - [pitfalls-template.md](references/templates/pitfalls-template.md) — pitfalls 模板
  - [sub-doc-templates.md](references/templates/sub-doc-templates.md) — 01~07 子文档模板集

---

## 初始化模式 — 详细执行步骤

当用户触发初始化（说
当用户触发初始化（说"初始化项目guide"、"创建项目文档"等）时：

1. **确认项目信息**：询问项目名称和类型（游戏/web/cli/lib/通用）
2. **运行初始化脚本**：`python3 scripts/init_guide.py --project-name "名称" --type 类型 --root 项目根目录`
3. **引导填充 start.md**：帮助用户填写启动命令、服务地址、文件清单表
4. **引导填充 guide.md**：帮助用户填写元信息、架构图、实体/模块概览
5. **验证检查清单**：
   - [ ] start.md 启动命令可执行
   - [ ] guide.md 文档索引表中的所有文件都存在
   - [ ] 01-design.md 至少有项目定位描述
   - [ ] 06-tech.md 至少有文件结构
   - [ ] 08-changelog.md 有 v0.1 初始版本记录
   - [ ] 09-pitfalls.md 有文件头和空模板

---

## 更新模式 — 详细执行步骤

当用户触发更新（说
当用户触发更新（说"更新guide"、"总结经验教训"等）时：

1. **读取当前版本**：从 `guide/08-changelog.md` 获取最新版本号
2. **收集更新内容**：询问用户本次完成的功能/修复/改动
3. **生成 changelog 条目**：
   - 版本号递增（补丁 +0.1，功能 +1.0）
   - 按子系统分组描述改动（含方法名和具体行为）
   - 🐛 Bug修复章节（问题+根因+修复）
   - 📝 代码改动章节（文件:方法 列表）
4. **检查踩坑记录**：询问是否有踩坑需要记录
   - 生成 pitfall 条目（编号+现象+根因+方案+⚠️注意+**通用原则**）
   - 检查通用原则章节是否需要新增
5. **同步更新**：
   - `guide.md` 版本号同步
   - `start.md` 文件清单检查（有新文件则更新）
   - `07-plan.md` checklist 更新（如有）
6. **自动提醒**：功能开发完成后，主动提示用户更新文档

---

## 上下文恢复模式 — 详细执行步骤

AI 在新对话中需要理解项目时，按以下分层策略读取文档。目标：用最少的文件读取获得最大的项目认知。

### 第1步：start.md — 30秒知道怎么跑

**读取文件**：项目根目录的 `start.md`

**提取信息**：
- 项目名称和一句话简介
- 启动/关闭/重启命令
- 服务地址（如有）
- 项目文件清单表（快速了解项目组成）

**读取后应能回答**：
- 这个项目怎么启动？端口是多少？
- 项目有哪些文件？每个文件做什么？

### 第2步：guide/guide.md — 2分钟获得全景

**读取文件**：`guide/guide.md`

**提取信息**：
- 技术路线（语言、框架、依赖）
- 当前版本号
- 文档索引表（知道还有哪些详细文档可读）
- Mermaid 架构图（核心系统间的关系）
- 核心实体/模块概览表

**读取后应能回答**：
- 项目是做什么的？核心目标是什么？
- 用了什么技术栈？
- 有哪些核心模块/子系统？它们之间什么关系？
- 当前开发到什么阶段了？

### 第3步：guide/08-changelog.md — 了解最新进展

**读取策略**：
- 如果文件 <200 行：全部读取
- 如果文件 >200 行：只读取最新 2-3 个版本 + 底部 Checklist

**提取信息**：
- 最新版本做了什么改动（功能/修复/重构）
- 未完成的 TODO 项（`- [ ]` 标记的）
- 已知的紧急问题（🔴 标记的）

**读取后应能回答**：
- 最近做了什么？
- 还有什么没做完？哪些是紧急的？
- 上次修了什么 Bug？

### 第4步：guide/09-pitfalls.md — 避免重蹈覆辙

**读取策略**：
- **必读**：文档末尾的「📋 通用开发原则」章节（这是最高优先级）
- **按需读**：最近 5 条踩坑记录的标题和⚠️开发注意部分
- 如果即将修改某个子系统，搜索相关的坑记录

**提取信息**：
- 通用开发原则列表（直接作为开发约束使用）
- 已知的陷阱和规避方法
- 反复出现的问题模式

**读取后应能回答**：
- 开发时有哪些必须遵守的原则？
- 修改 XXX 时有什么需要注意的？
- 之前踩过什么坑？怎么解决的？

### 第5步：按需深入

根据用户的具体需求，选择性读取：

| 用户需求 | 读取文件 |
|----------|----------|
| 了解设计决策/为什么这样做 | `01-design.md` |
| 理解代码结构/核心类 | `06-tech.md` |
| 查看开发计划/排期 | `07-plan.md` |
| 了解地图/场景设计（游戏） | `02-map.md` |
| 了解NPC/角色系统（游戏） | `03-npc.md` |
| 了解属性/数值系统（游戏） | `04-attributes.md` |
| 了解AI/Prompt系统（游戏） | `05-ai.md` |
| 了解路由设计（Web） | `02-routes.md` |
| 了解组件设计（Web） | `03-components.md` |
| 了解API设计（Web） | `05-api.md` |

### 恢复模式选择

| 场景 | 推荐模式 | 读取范围 |
|------|----------|----------|
| 日常开发继续 | 快速恢复 | 第1步 + 第2步 + changelog最新版本 |
| 首次接手项目 | 完整恢复 | 第1~5步全读 |
| 排查特定问题 | 定向恢复 | 第4步（pitfalls）+ 相关领域文档 |
| 版本发布前检查 | 审查恢复 | 第2步 + 第3步 + 第4步通用原则 |
